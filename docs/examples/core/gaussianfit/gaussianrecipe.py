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
"""Example of fitting a Gaussian to simulated data.

This is an example of building a fit recipe that can be driven by an optimizer
to fit a Gaussian profile to simulated data.  The purpose of this example is
familiarize the developer with the objects involved in defining a SrFit
refinement recipe.

Instructions

If you have not yet run the example, run it and inspect the output. The example
script is driven by the 'main' method defined below. Take a look at that method
to get an understanding of how a fit recipe can be used once created.  After
that, read the 'make_recipe' code to see what goes into a fit recipe. After
that, read the 'optimize_recipe' code to see how the refinement is executed.
Finally, read the 'plot_results' code to see how to extracts the refined
profile and plot it.

Extensions

After reading through the code, try to perform the following tasks. The process
will leave you with a much better understanding of how SrFit works.

- Play around with setting the values of the Variables and Parameters. What
  happens to the associated Parameter when you change a variable value? What
  happens to the variable when you change the Parameter value?
- Modify the fitting equation by adding a constant. See if that improves the
  fit.
- Create a FitRecipe to fit the Lorentzian profile in the data/lorentzian.dat
  file.
"""


from pathlib import Path

from diffpy.srfit.fitbase import (
    FitContribution,
    FitRecipe,
    FitResults,
    Profile,
)

######
#  Example Code


def main():
    """The workflow of creating, running and inspecting a fit."""

    # Start by creating the recipe. The recipe describes the data to be fit,
    # the profile generator used to simulate the data and the variables that
    # will be tuned by the optimizer.
    recipe = make_recipe()

    # Refine using the optimizer of your choice.
    optimize_recipe(recipe)

    # Get the results in a FitResults object. The FitResults object stores the
    # current state of the recipe, and uses it to calculate useful statistics
    # about the fit.
    res = FitResults(recipe)

    # Print the results.
    res.printResults()

    # Plot the results.
    plot_results(recipe)

    return


def make_recipe():
    """Make a FitRecipe for fitting a Gaussian curve to data.

    The instructions for what we want to refine, and how to refine it
    will be defined within a FitRecipe instance. The job of a FitRecipe
    is to collect and associate all the data, the fitting equations,
    fitting variables, constraints and restraints. The configured recipe
    provides a 'residual' function and the initial variable values that
    an optimizer can use to refine the variables to minimize the
    disagreement between the calculated profile and the data.

    Once we define the FitRecipe, we can send it an optimizer to be
    optimized. See the 'optimize_recipe' function.
    """

    # The Profile
    # Create a Profile to hold the experimental and calculated signal.
    profile = Profile()

    # Load data and add it to the profile. This uses the loadtxt function from
    # numpy.
    gaussian_data = str(Path(__file__).parent / "gaussian.dat")
    profile.loadtxt(gaussian_data)

    # The FitContribution
    # The FitContribution associates the Profile with a fitting equation. The
    # FitContribution also stores the parameters of the fitting equation. We
    # give our FitContribution then name "g1". We will be able to access the
    # FitContribution by that name within the FitRecipe.
    contribution = FitContribution("g1")
    # Tell the FitContribution about the Profile. The FitContribution will give
    # us access to the data held within the Profile. Here, we can tell it what
    # name we want to use for the independent variable. We tell it to use the
    # name "x".
    contribution.setProfile(profile, xname="x")

    # Now we need to create a fitting equation. We do that by writing out the
    # equation as a string. The FitContribution will turn this into a callable
    # function internally. In the process, it extracts all the parameters from
    # the equation (A, x, x0, sigma) and turns them into Parameter objects
    # internally. These objects can be accessed as attributes of the
    # contribution by name.  Since we told the contribution that our
    # independent variable is named "x", this value will be substituted into
    # the fitting equation whenever it is called.
    contribution.setEquation("A * exp(-0.5*(x-x0)**2/sigma**2)")

    # To demonstrate how these parameters are used, we will give "A" an initial
    # value. Note that Parameters are not numbers, but are containers for
    # numbers. To get or modify the value of a parameter, use its 'value'
    # attribute.  Parameters also have a 'name' attribute.
    contribution.A.value = 1.0

    # The FitRecipe
    # The FitRecipe lets us define what we want to fit. It is where we can
    # create variables, constraints and restraints.
    recipe = FitRecipe()

    # Here we tell the FitRecipe to use our FitContribution. When the FitRecipe
    # calculates its residual function, it will call on the FitContribution to
    # do part of the work.
    recipe.addContribution(contribution)

    # Specify which Parameters we want to vary in the fit.  This will add
    # Variables to the FitRecipe that directly modify the Parameters of the
    # FitContribution.
    #
    # Here we create a Variable for the 'A' Parameter from our fit equation.
    # The resulting Variable will be named 'A' as well, but it will be accessed
    # via the FitRecipe.
    recipe.addVar(contribution.A)
    # Here we create the Variable for 'x0' and give it an initial value of 5.
    recipe.addVar(contribution.x0, 5)
    # Here we create a Variable named 'sig', which is tied to the 'sigma'
    # Parameter of our FitContribution. We give it an initial value through the
    # FitRecipe instance.
    recipe.addVar(contribution.sigma, name="sig")
    recipe.sig.value = 1

    return recipe


def optimize_recipe(recipe):
    """Optimize the recipe created above using scipy.

    The FitRecipe we created in make_recipe has a 'residual' method that
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


def plot_results(recipe):
    """Plot the results contained within a refined FitRecipe."""

    # We can access the data and fit profile through the Profile we created
    # above. We get to it through our FitContribution, which we named "g1".
    #
    # The independent variable. This is always under the "x" attribute.
    x = recipe.g1.profile.x
    # The observed profile that we loaded earlier, the "y" attribute.
    y = recipe.g1.profile.y
    # The calculated profile, the "ycalc" attribute.
    ycalc = recipe.g1.profile.ycalc

    # This stuff is specific to pylab from the matplotlib distribution.
    import pylab

    pylab.plot(x, y, "b.", label="observed Gaussian")
    pylab.plot(x, ycalc, "g-", label="calculated Gaussian")
    pylab.legend()
    pylab.xlabel("x")
    pylab.ylabel("y")

    pylab.show()
    return


if __name__ == "__main__":

    main()

# End of file
