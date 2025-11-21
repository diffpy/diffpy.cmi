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
"""Example of fitting the Debye recipe to experimental Debye-Waller
factors.

This is an extension of example in debyemodel.py. The recipe we create will
simultaneously fit the low and high temperature parts of the experimental data
with the same Debye temperature, but different offsets. This example also
introduces constraints.

Instructions

Run the example and then read through the 'make_recipeII' code to learn about
multi-profile recipes.  You will learn how to constrain related information
between the fit contributions.

Extensions

- Play with the fit ranges and see if you can improve the fit.
- The Debye temperature parameters from the two contributions can be
  constrained without creating a new variable. Try to figure out how that is
  done.
"""

from debyemodel import make_recipe

from diffpy.cmi.fit_tools import optimize_recipe
from diffpy.srfit.fitbase import FitRecipe, FitResults

######
#  Example Code


def make_recipeII():
    """Make a recipe for fitting low and high temperature regions.

    We will fit the low and high temperature parts of Debye curve
    simultaneously with the same Debye temperature, but different
    offsets.

    We will make two FitRecipes using the make_recipe function from
    debyemodel.py and extract the configured FitContribution from each.
    We will use different fitting ranges for each FitContribution and
    constrain the Debye temperature in each FitContribution to be the
    same.
    """

    # We'll throw these away. We just want the FitContributions that are
    # configured within the recipes.
    m1 = make_recipe()
    m2 = make_recipe()
    # These are the FitContributions (we named them "pb" in the debyemodel
    # example).
    lowT = m1.pb
    highT = m2.pb
    # Let's rename the FitContributions to something more meaningful for this
    # example.
    lowT.name = "lowT"
    highT.name = "highT"

    # Now create a fresh FitRecipe to work with and add to it the two
    # FitContributions.
    recipe = FitRecipe()
    recipe.addContribution(lowT)
    recipe.addContribution(highT)

    # Change the fit ranges of the Profiles embedded within the
    # FitContributions. We want to fit one of the contributions at low
    # temperature, and one at high.
    lowT.profile.setCalculationRange(0, 150)
    highT.profile.setCalculationRange(400, 500)

    # Vary the offset from each FitContribution separately, while keeping the
    # Debye temperatures the same. We give each offset variable a different
    # name in the recipe so it retains its identity.
    recipe.addVar(recipe.lowT.offset, name="lowToffset")
    recipe.addVar(recipe.highT.offset, name="highToffset")
    # We create a new Variable and use the recipe's "constrain" method to
    # associate the Debye temperature parameters with that variable.
    recipe.newVar("thetaD", 100)
    recipe.constrain(recipe.lowT.thetaD, "thetaD")
    recipe.constrain(recipe.highT.thetaD, "thetaD")
    return recipe


def plot_results(recipe):
    """Display the results contained within a refined FitRecipe."""

    # The variable values are returned in the order in which the variables were
    # added to the FitRecipe.
    lowToffset, highToffset, thetaD = recipe.getValues()

    # We want to extend the fitting range to its full extent so we can get a
    # nice full plot.
    recipe.lowT.profile.setCalculationRange(xmin="obs", xmax="obs")
    recipe.highT.profile.setCalculationRange(xmin="obs", xmax="obs")
    T = recipe.lowT.profile.x
    U = recipe.lowT.profile.y
    # We can use a FitContribution's 'evaluateEquation' method to evaluate
    # expressions involving the Parameters and other aspects of the
    # FitContribution. Here we evaluate the fitting equation, which is always
    # accessed using the name "eq". We access it this way (rather than through
    # the Profile's ycalc attribute) because we changed the calculation range
    # above, and we therefore need to recalculate the profile.
    lowU = recipe.lowT.evaluateEquation("eq")
    highU = recipe.highT.evaluateEquation("eq")

    # Now we can plot this.
    import pylab

    pylab.plot(T, U, "o", label="Pb $U_{iso}$ Data")
    lbl1 = r"$T_d$=%3.1f K, lowToff=%1.5f $\AA^2$" % (abs(thetaD), lowToffset)
    lbl2 = r"$T_d$=%3.1f K, highToff=%1.5f $\AA^2$" % (
        abs(thetaD),
        highToffset,
    )
    pylab.plot(T, lowU, label=lbl1)
    pylab.plot(T, highU, label=lbl2)
    pylab.xlabel("T (K)")
    pylab.ylabel(r"$U_{iso} (\AA^2)$")
    pylab.legend()

    pylab.show()
    return


def main():

    # Create the recipe
    recipe = make_recipeII()

    # Refine using the optimizer of your choice
    optimize_recipe(recipe)

    # Get the results in a FitResults object.
    res = FitResults(recipe)

    # Print the results
    res.printResults()

    # Plot the results
    plot_results(recipe)

    return


if __name__ == "__main__":

    main()

# End of file
