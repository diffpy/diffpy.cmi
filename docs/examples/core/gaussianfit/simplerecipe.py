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
"""Example of simplified fitting.

This is like gaussianrecipe.py, but it uses the SimpleRecipe, which
integrates the FitContribution and Profile objects for simple recipe
creation.
"""

from pathlib import Path

from diffpy.srfit.fitbase import SimpleRecipe

######
#  Example Code


def main():
    """Set up a simple recipe in a few lines."""

    # The SimpleRecipe class is a type of FitRecipe. It provides attribute-like
    # access to variables and a residual function that can be minimized.
    recipe = SimpleRecipe()

    # Load text from file.
    data = str(Path(__file__).parent / "gaussian.dat")
    recipe.loadtxt(data)

    # Set the equation. The variable "x" is taken from the data that was just
    # loaded. The other variables, "A", "x0" and "sigma" are turned into
    # attributes with an initial value of 0.
    recipe.setEquation("A * exp(-0.5*(x-x0)**2/sigma**2)")

    # We can give them other values here.
    recipe.A = 1
    recipe.x0 = 5
    recipe.sigma = 1

    # We explicitly optimize the residual method of the SimpleRecipe
    from scipy.optimize import leastsq

    leastsq(recipe.residual, recipe.values)

    # Print the results
    recipe.printResults()

    return


if __name__ == "__main__":

    main()

# End of file
