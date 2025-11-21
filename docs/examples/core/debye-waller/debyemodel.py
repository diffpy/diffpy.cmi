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
"""Example of fitting the Debye model to experimental Debye-Waller
factors.

In this example, we build a fit recipe that uses an external function that can
simulate a atomic displacement parameters using the Debye model. This serves as
an example of how to utilize python functions in a fit and extend them with
SrFit without writing additional code.  This example also demonstrates guide a
refinement with restraints.

Instructions

Run the example and then read the 'make_recipe' code to see how to use a python
function as a profile generator.

Extensions

- Don't hardcode the mass of lead in the fitting equation. Turn it into a
  Parameter and refine it. There are two ways to do this. Try to figure out
  both.
"""

import numpy

from diffpy.cmi.fit_tools import optimize_recipe, plot_results
from diffpy.srfit.fitbase import (
    FitContribution,
    FitRecipe,
    FitResults,
    Profile,
)

# The data
data = """\
015.0 0.00334 0.00013
050.0 0.00508 0.00022
100.0 0.00830 0.00040
150.0 0.01252 0.00071
200.0 0.01792 0.00100
250.0 0.02304 0.00120
300.0 0.02737 0.00140
350.0 0.03085 0.00160
400.0 0.03484 0.00190
450.0 0.03774 0.00220
500.0 0.03946 0.00250
"""

######
#  Example Code


def make_recipe():
    """Make the recipe for the fit.

    The instructions for what we want to refine, and how to refine it
    will be defined within a FitRecipe instance. The job of a FitRecipe
    is to collect and associate all the data, the fitting equations,
    fitting variables, constraints and restrations. We will demonstrate
    each of these within the code.

    Data is held within a Profile object. The Profile is simply a
    container that holds the data, and the theoretical profile once it
    has been calculated.

    Data is associated with a fitting equation within a FitContribution.
    The FitContribution defines the equation and parameters that will be
    adjusted to fit the data. The fitting equation can be defined within
    a function or optionally within the ProfileGenerator class. We won't
    need the ProfileGenerator class in this example since the signature
    of the fitting equation (the 'debye' function defined below) is so
    simple. The FitContribution also defines the residual function to
    optimize for the data/equation pair. This can be modified, but we
    won't do that here.
    """

    # The Profile
    # Create a Profile to hold the experimental and calculated signal.
    profile = Profile()

    # Load data and add it to the profile. It is our responsibility to get our
    # data into the profile.
    xydy = numpy.array(data.split(), dtype=float).reshape(-1, 3)
    x, y, dy = xydy.T
    profile.setObservedProfile(x, y, dy)

    # The FitContribution
    # The FitContribution associates the profile with the Debye function.
    contribution = FitContribution("pb")
    # Tell the contribution about the Profile. We will need to use the
    # independent variable (the temperature) from the data to calculate the
    # theoretical signal, so give it an informative name ('T') that we can use
    # later.
    contribution.setProfile(profile, xname="T")

    # We now need to create the fitting equation.  We tell the FitContribution
    # to use the 'debye' function defined below. The 'registerFunction' method
    # will let us do this. Since we haven't told it otherwise,
    # 'registerFunction' will extract the name of the function ('debye') and
    # the names of the arguments ('T', 'm', 'thetaD'). These arguments will
    # become Parameters of the FitContribution. Since we named the x-variable
    # 'T' above, the 'T' in the 'debye' equation will refer to this x-variable
    # whenever it is used.
    contribution.registerFunction(debye)

    # Now we can create the fitting equation. We want to extend the 'debye'
    # equation by adding a vertical offset. We could wrap 'debye' in a new
    # function with an offset, and register that instead of 'debye', but what
    # we do here is easier.
    #
    # When we set the fitting equation, we do not need to specify the
    # Parameters to the 'debye' function since the FitContribution already
    # knows what they are. If we choose to specify the arguments, we can make
    # adjustments to their input values.  We wish to have the thetaD value in
    # the debye equation to be positive, so we specify the input as abs(thetaD)
    # in the equation below.  Furthermore, we know 'm', the mass of lead, so we
    # can specify that as well.
    contribution.setEquation("debye(T, 207.2, abs(thetaD)) + offset")

    # The FitRecipe
    # The FitRecipe lets us define what we want to fit. It is where we can
    # create variables, constraints and restraints. If we had multiple profiles
    # to fit simultaneously, the contribution from each could be added to the
    # recipe.
    recipe = FitRecipe()
    recipe.addContribution(contribution)

    # Specify which Parameters we want to refine.

    # Vary the offset
    recipe.addVar(contribution.offset, 0)
    # We also vary the Debye temperature.
    recipe.addVar(contribution.thetaD, 100)

    # We would like to 'suggest' that the offset should remain positive. This
    # is somethine that we know about the system that might help the refinement
    # converge to a physically reasonable result.  We will do this with a soft
    # constraint, or restraint. Here we restrain the offset variable to between
    # 0 and infinity. We tell the recipe that we want to scale the penalty for
    # breaking the restraint by the point-average chi^2 value so that the
    # restraint is roughly as significant as any other data point throughout
    # the fit.
    recipe.restrain(recipe.offset, lb=0, scaled=True)

    # We're done setting up the recipe. We can now do other things with it.
    return recipe


def main():
    """The workflow of creating, running and inspecting a fit."""

    # Create the recipe
    recipe = make_recipe()

    # Refine using the optimizer of your choice
    optimize_recipe(recipe)

    # Get the results.
    res = FitResults(recipe)

    # Print the results
    res.printResults()

    # Plot the results
    x = recipe.pb.profile.x
    yobs = recipe.pb.profile.y
    ycalc = recipe.pb.profile.ycalc

    plot_results(x, yobs, ycalc)

    return


# Functions required for calculation of Debye curve. Feel free to skip these,
# as we treat them as if existing in some external library that we cannot
# modify.


def debye(T, m, thetaD):
    """A wrapped version of 'adps' that can handle an array of
    T-values."""
    y = numpy.array([adps(m, thetaD, x) for x in T])
    return y


def adps(m, thetaD, T):
    """Calculates atomic displacement factors within the Debye model.

    <u^2> = (3h^2/4 pi^2 m kB thetaD)(phi(thetaD/T)/(ThetaD/T) + 1/4)

    arguments:
    m -- float -- mass of the ion in atomic mass units (e.g., C = 12)
    thetaD -- float -- Debye Temperature
    T -- float -- temperature.

    return:
    Uiso -- float -- the thermal factor from the Debye recipe at temp T
    """
    h = 6.6260755e-34  # Planck's constant. J.s of m^2.kg/s
    kB = 1.3806503e-23  # Boltzmann's constant. J/K
    amu = 1.66053886e-27  # Atomic mass unit. kg

    def __phi(x):
        """Evaluates the phi integral needed in Debye calculation.

        phi(x) = (1/x) int_0^x xi/(exp(xi)-1) dxi

        arguments:
        x -- float -- value of thetaD (Debye temperature)/T

        returns:
        phi -- float -- value of the phi function
        """

        def __debyeKernel(xi):
            """Function needed by debye calculators."""
            y = xi / (numpy.exp(xi) - 1)
            return y

        import scipy.integrate

        int = scipy.integrate.quad(__debyeKernel, 0, x)
        phi = (1 / x) * int[0]

        return phi

    m = m * amu
    u2 = (3 * h**2 / (4 * numpy.pi**2 * m * kB * thetaD)) * (
        __phi(thetaD / T) / (thetaD / T) + 1.0 / 4.0
    )

    return u2 * 1e20


if __name__ == "__main__":

    main()

# End of file
