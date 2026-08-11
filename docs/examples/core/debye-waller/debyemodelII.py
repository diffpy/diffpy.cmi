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
    recipe.add_contribution(lowT)
    recipe.add_contribution(highT)

    # Change the fit ranges of the Profiles embedded within the
    # FitContributions. We want to fit one of the contributions at low
    # temperature, and one at high.
    lowT.profile.set_calculation_range(0, 150)
    highT.profile.set_calculation_range(400, 500)

    # Vary the offset from each FitContribution separately, while keeping the
    # Debye temperatures the same. We give each offset variable a different
    # name in the recipe so it retains its identity.
    recipe.add_variable(recipe.lowT.offset, name="lowToffset")
    recipe.add_variable(recipe.highT.offset, name="highToffset")
    # We create a new Variable and use the recipe's "constrain" method to
    # associate the Debye temperature parameters with that variable.
    recipe.create_new_variable("thetaD", 100)
    recipe.add_constraint(recipe.lowT.thetaD, "thetaD")
    recipe.add_constraint(recipe.highT.thetaD, "thetaD")
    return recipe


def plot_results(recipe):
    """Display the results contained within a refined FitRecipe."""

    # The variable values are returned in the order in which the variables were
    # added to the FitRecipe.
    lowToffset, highToffset, thetaD = recipe.get_values()
    print(
        r"lowT:  $T_d$=%3.1f K, offset=%1.5f $\AA^2$"
        % (abs(thetaD), lowToffset)
    )
    print(
        r"highT: $T_d$=%3.1f K, offset=%1.5f $\AA^2$"
        % (abs(thetaD), highToffset)
    )

    # We want to extend the fitting range to its full extent so we can get a
    # nice full plot. Since the calculated profile is only valid for the
    # calculation range that was used during the fit, we need to trigger a
    # recalculation over the widened range before plotting.
    recipe.lowT.profile.set_calculation_range(xmin="obs", xmax="obs")
    recipe.highT.profile.set_calculation_range(xmin="obs", xmax="obs")
    recipe.residual()

    recipe.plot_recipe(
        show_diff=False,
        data_label=r"Pb $U_{iso}$ Data",
        fit_label="Calculated",
        xlabel="T (K)",
        ylabel=r"$U_{iso} (\AA^2)$",
        legend_loc=(0.0, 0.8),
    )
    return


def main():

    # Create the recipe
    recipe = make_recipeII()

    # Refine using the optimizer of your choice
    optimize_recipe(recipe)

    # Get the results in a FitResults object.
    res = FitResults(recipe)

    # Print the results
    res.print_results()

    # Plot the results
    plot_results(recipe)

    return


if __name__ == "__main__":

    main()

# End of file
