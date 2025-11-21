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

This is like gaussianrecipe.py, but it uses a shorthand interface
defined in the diffpy.srfit.interface.interface.py module.
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

    p = Profile()
    data = str(Path(__file__).parent / "gaussian.dat")
    p.loadtxt(data)

    # FitContribution operations
    # "<<"  -   Inject a parameter value
    c = FitContribution("g1")
    c.setProfile(p)
    c.setEquation("A * exp(-0.5*(x-x0)**2/sigma**2)")
    c.A << 0.5
    c.x0 << 5
    c.sigma << 1

    # FitRecipe operations
    # "|="  -   Union of necessary components.
    # "+="  -   Add Parameter or create a new one. Each tuple is a set of
    #           arguments for either setVar or addVar.
    # "*="  -   Constrain a parameter. Think of "*" as a push-pin holding one
    #           parameter's value to that of another.
    # "%="  -   Restrain a parameter or equation. Think of "%" as a rope
    #           loosely tying parameters to a value.
    r = FitRecipe()
    r |= c
    r += (c.A, 0.5), (c.x0, 5), ("sig", 1)
    r *= c.sigma, "sig"
    r %= c.A, 0.5, 0.5

    from diffpy.cmi.fit_tools import optimize_recipe

    optimize_recipe(r)

    res = FitResults(r)
    # Print the results.
    res.printResults()
    # Plot the results.
    from diffpy.cmi.fit_tools import plot_results

    x = r.g1.profile.x
    y = r.g1.profile.y
    ycalc = r.g1.profile.ycalc

    plot_results(x, y, ycalc)

    return


if __name__ == "__main__":
    main()

# End of file
