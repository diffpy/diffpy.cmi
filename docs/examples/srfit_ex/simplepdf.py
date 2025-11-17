#!/usr/bin/env python
########################################################################
#
# diffpy.srfit      by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2010 The Trustees of Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Chris Farrow
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE_DANSE.txt for license information.
#
########################################################################
"""Example of a PDF using the PDFContribution helper class.

This is example of fitting the fcc nickel structure to measured PDF
data. It uses the PDFContribution class to simplify fit setup.
"""

from crystalpdf import plotResults
from gaussianrecipe import scipyOptimize

from diffpy.srfit.fitbase import FitRecipe, FitResults
from diffpy.srfit.pdf import PDFContribution
from diffpy.structure import Structure

######
#  Example Code


def makeRecipe(ciffile, datname):
    """Create a fitting recipe for crystalline PDF data."""

    # Work directly with a custom PDFContribution to load the data
    contribution = PDFContribution("nickel")
    contribution.loadData(datname)
    contribution.setCalculationRange(xmin=1, xmax=20, dx=0.1)

    # and the phase
    stru = Structure()
    stru.read(ciffile)
    contribution.addStructure("nickel", stru)

    # Make the FitRecipe and add the FitContribution.
    recipe = FitRecipe()
    recipe.addContribution(contribution)

    # Configure the fit variables
    phase = contribution.nickel.phase

    from diffpy.srfit.structure import constrainAsSpaceGroup

    sgpars = constrainAsSpaceGroup(phase, "Fm-3m")

    for par in sgpars.latpars:
        recipe.addVar(par)
    for par in sgpars.adppars:
        recipe.addVar(par, 0.005)

    recipe.addVar(contribution.scale, 1)
    recipe.addVar(contribution.qdamp, 0.03, fixed=True)
    recipe.addVar(contribution.nickel.delta2, 5)

    # Give the recipe away so it can be used!
    return recipe


if __name__ == "__main__":

    # Make the data and the recipe
    ciffile = "data/ni.cif"
    data = "data/ni-q27r100-neutron.gr"

    # Make the recipe
    recipe = makeRecipe(ciffile, data)

    # Optimize
    scipyOptimize(recipe)
    # Save the file
    recipe.nickel.savetxt("nickel_example.fit")

    # Generate, print and save the FitResults
    res = FitResults(recipe)
    res.printResults()
    res.saveResults("nickel_example.res")

    # Plot!
    plotResults(recipe)

# End of file
