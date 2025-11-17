#!/usr/bin/env python
########################################################################
#
# diffpy.srfit      by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2009 The Trustees of Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Chris Farrow
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE_DANSE.txt for license information.
#
########################################################################
"""Example of fitting a three double peaks to simulated data."""

from __future__ import print_function

import numpy

from diffpy.srfit.fitbase import (
    FitContribution,
    FitRecipe,
    FitResults,
    Profile,
)

######
#  Example Code


def makeRecipe():
    """Make a FitRecipe for fitting three double-gaussian curves to
    data.

    The separation and amplitude ratio of the double peaks follows a
    specific relationship.  The peaks are broadend according to their
    position and they sit on top of a background. We are seeking the
    absolute locations of the peaks as well as their amplitudes.

    The independent variable is t. The relationship between the double
    peaks is sin(t2) / l2 = sin(t1) / l1 amplitude(peak2) = r *
    amplitude(peak1) The values of l1, l2 and r come from experiment.
    For this example, we use l1 = 1.012, l2 = 1.0 and r = 0.23.
    """

    # The Profile
    # Create a Profile to hold the experimental and calculated signal.
    profile = Profile()
    x, y, dy = profile.loadtxt("data/threedoublepeaks.dat")

    # Create the contribution
    contribution = FitContribution("peaks")
    contribution.setProfile(profile, xname="t")
    pi = numpy.pi
    exp = numpy.exp

    # This is a building-block of our profile function
    def gaussian(t, mu, sig):
        return 1 / (2 * pi * sig**2) ** 0.5 * exp(-0.5 * ((t - mu) / sig) ** 2)

    contribution.registerFunction(gaussian, name="peakshape")

    def delta(t, mu):
        """Calculate a delta-function.

        We don't have perfect precision, so we must make this a very
        thin Gaussian.
        """
        sig = t[1] - t[0]
        return gaussian(t, mu, sig)

    contribution.registerFunction(delta)

    # Here is another one
    bkgdstr = "b0 + b1*t + b2*t**2 + b3*t**3 + b4*t**4 + b5*t**5 + b6*t**6"

    contribution.registerStringFunction(bkgdstr, "bkgd")

    # Now define our fitting equation. We will hardcode the peak ratios.
    contribution.setEquation(
        "A1 * ( convolve( delta(t, mu11), peakshape(t, c, sig11) ) \
         + 0.23*convolve( delta(t, mu12), peakshape(t, c, sig12) ) ) + \
         A2 * ( convolve( delta(t, mu21), peakshape(t, c, sig21) ) \
         + 0.23*convolve( delta(t, mu22), peakshape(t, c, sig22) ) ) + \
         A3 * ( convolve( delta(t, mu31), peakshape(t, c, sig31) ) \
         + 0.23*convolve( delta(t, mu32), peakshape(t, c, sig32) ) ) + \
         bkgd"
    )

    # c is the center of the gaussian.
    contribution.c.value = x[len(x) // 2]

    # The FitRecipe
    # The FitRecipe lets us define what we want to fit. It is where we can
    # create variables, constraints and restraints.
    recipe = FitRecipe()

    # Here we tell the FitRecipe to use our FitContribution. When the FitRecipe
    # calculates its residual function, it will call on the FitContribution to
    # do part of the work.
    recipe.addContribution(contribution)

    # Vary the amplitudes for each double peak
    recipe.addVar(contribution.A1, 100)
    recipe.addVar(contribution.A2, 100)
    recipe.addVar(contribution.A3, 100)

    # Vary the position of the first of the double peaks
    recipe.addVar(contribution.mu11, 13.0)
    recipe.addVar(contribution.mu21, 24.0)
    recipe.addVar(contribution.mu31, 33.0)

    # Constrain the position of the second double peak
    from numpy import arcsin, sin

    def peakloc(mu):
        """Calculate the location of the second peak given the first."""
        l1 = 1.012
        l2 = 1.0
        return 180 / pi * arcsin(pi / 180 * l2 * sin(mu) / l1)

    recipe.registerFunction(peakloc)
    recipe.constrain(contribution.mu12, "peakloc(mu11)")
    recipe.constrain(contribution.mu22, "peakloc(mu21)")
    recipe.constrain(contribution.mu32, "peakloc(mu31)")

    # Vary the width of the peaks. We know the functional form of the peak
    # broadening.
    recipe.newVar("sig0", 0.001)
    recipe.newVar("dsig", 4)

    def sig(sig0, dsig, mu):
        """Calculate the peak broadening with respect to position."""
        return sig0 * (1 - dsig * mu**2)

    recipe.registerFunction(sig)
    recipe.fix("mu")
    # Now constrain the peak widths to this
    recipe.sig0.value = 0.001
    recipe.dsig.value = 4.0
    recipe.constrain(contribution.sig11, "sig(sig0, dsig, mu11)")
    recipe.constrain(
        contribution.sig12,
        "sig(sig0, dsig, mu12)",
        ns={"mu12": contribution.mu12},
    )
    recipe.constrain(contribution.sig21, "sig(sig0, dsig, mu21)")
    recipe.constrain(
        contribution.sig22,
        "sig(sig0, dsig, mu22)",
        ns={"mu22": contribution.mu22},
    )
    recipe.constrain(contribution.sig31, "sig(sig0, dsig, mu31)")
    recipe.constrain(
        contribution.sig32,
        "sig(sig0, dsig, mu32)",
        ns={"mu32": contribution.mu32},
    )

    # Also the background
    recipe.addVar(contribution.b0, 0, tag="bkgd")
    recipe.addVar(contribution.b1, 0, tag="bkgd")
    recipe.addVar(contribution.b2, 0, tag="bkgd")
    recipe.addVar(contribution.b3, 0, tag="bkgd")
    recipe.addVar(contribution.b4, 0, tag="bkgd")
    recipe.addVar(contribution.b5, 0, tag="bkgd")
    recipe.addVar(contribution.b6, 0, tag="bkgd")
    return recipe


def scipyOptimize(recipe):
    """Optimize the recipe created above using scipy.

    The FitRecipe we created in makeRecipe has a 'residual' method that
    we can be minimized using a scipy optimizer. The details are
    described in the source.
    """

    # We're going to use the least-squares (Levenberg-Marquardt) optimizer from
    # scipy. We simply have to give it the function to minimize
    # (recipe.residual) and the starting values of the Variables
    # (recipe.getValues()).
    from scipy.optimize.minpack import leastsq

    print("Fit using scipy's LM optimizer")
    leastsq(recipe.residual, recipe.getValues())

    return


def plotResults(recipe):
    """Plot the results contained within a refined FitRecipe."""

    # We can access the data and fit profile through the Profile we created
    # above. We get to it through our FitContribution, which we named "g1".
    #
    # The independent variable. This is always under the "x" attribute.
    x = recipe.peaks.profile.x
    # The observed profile that we loaded earlier, the "y" attribute.
    y = recipe.peaks.profile.y
    # The calculated profile, the "ycalc" attribute.
    ycalc = recipe.peaks.profile.ycalc

    # This stuff is specific to pylab from the matplotlib distribution.
    import pylab

    pylab.plot(x, y, "b.", label="observed profile")
    pylab.plot(x, ycalc, "r-", label="calculated profile")
    pylab.plot(x, y - ycalc - 0.1 * max(y), "g-", label="difference")
    pylab.legend(loc=(0.0, 0.8))
    pylab.xlabel("x")
    pylab.ylabel("y")

    pylab.show()
    return


def steerFit(recipe):
    """Steer the fit for this problem.

    This is a complex fit, it requires some steering.
    """
    recipe.fix("all")

    recipe.free("bkgd")
    scipyOptimize(recipe)

    recipe.free("all")
    recipe.fix("mu11", "mu21", "mu31")
    scipyOptimize(recipe)

    recipe.free("all")
    scipyOptimize(recipe)

    return


if __name__ == "__main__":

    # Create the recipe
    recipe = makeRecipe()

    # Refine
    steerFit(recipe)

    # Get the results in a FitResults object. The FitResults object stores the
    # current state of the recipe, and uses it to calculate useful statistics
    # about the fit.  If you later modify the recipe, the FitResults object
    # will hold the recipe values from when it was created. You can tell it to
    # update its values by calling its 'update' method.
    res = FitResults(recipe)

    # Print the results
    res.printResults()

    # Plot the results
    plotResults(recipe)


# End of file
