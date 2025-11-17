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
"""Example of a simplified PDF refinement of two-phase structure."""

from crystalpdftwophase import plotResults
from gaussianrecipe import scipyOptimize
from pyobjcryst import loadCrystal

from diffpy.srfit.fitbase import FitRecipe, FitResults
from diffpy.srfit.pdf import PDFContribution

######
#  Example Code


def makeRecipe(niciffile, siciffile, datname):
    """Create a fitting recipe for crystalline PDF data."""

    # Load data and add it to the profile
    contribution = PDFContribution("nisi")
    contribution.loadData(datname)
    contribution.setCalculationRange(xmax=20)

    stru = loadCrystal(niciffile)
    contribution.addStructure("ni", stru)

    stru = loadCrystal(siciffile)
    contribution.addStructure("si", stru)

    # Make the FitRecipe and add the FitContribution.
    recipe = FitRecipe()
    recipe.addContribution(contribution)

    # Configure the fit variables
    # Start by configuring the scale factor and resolution factors.
    # We want the sum of the phase scale factors to be 1.
    recipe.newVar("scale_ni", 0.1)
    recipe.constrain(contribution.ni.scale, "scale_ni")
    recipe.constrain(contribution.si.scale, "1 - scale_ni")
    # We also want the resolution factor to be the same on each. This is done
    # for free by the PDFContribution. We simply need to add it to the recipe.
    recipe.addVar(contribution.qdamp, 0.03)

    # Vary the global scale as well.
    recipe.addVar(contribution.scale, 1)

    # Now we can configure the structural parameters. Since we're using
    # ObjCrystCrystalParSets, the space group constraints are automatically
    # applied to each phase. We must selectively vary the free parameters.
    #
    # First the nickel parameters.
    # Note that ni is the name of the PDFGenerator that was automatically
    # created by the PDFContribution. We selected this name in addStructure
    # above.
    phase_ni = contribution.ni.phase
    for par in phase_ni.sgpars:
        recipe.addVar(par, name=par.name + "_ni")
    recipe.addVar(contribution.ni.delta2, name="delta2_ni")
    # Next the silicon parameters
    phase_si = contribution.si.phase
    for par in phase_si.sgpars:
        recipe.addVar(par, name=par.name + "_si")
    recipe.addVar(contribution.si.delta2, name="delta2_si")

    # We have prior information from the earlier examples so we'll use it here
    # in the form of restraints.
    #
    # The nickel lattice parameter was measured to be 3.527. The uncertainty
    # values are invalid for that measurement, since the data from which it is
    # derived has no uncertainty. Thus, we will tell the recipe to scale the
    # residual, which means that it will be weighted as much as the average
    # data point during the fit.
    recipe.restrain("a_ni", lb=3.527, ub=3.527, scaled=True)
    # Now we do the same with the delta2 and Biso parameters (remember that
    # Biso = 8*pi**2*Uiso)
    recipe.restrain("delta2_ni", lb=2.22, ub=2.22, scaled=True)
    recipe.restrain("Biso_0_ni", lb=0.454, ub=0.454, scaled=True)
    #
    # We can do the same with the silicon values. We haven't done a thorough
    # job of measuring the uncertainties in the results, so we'll scale these
    # as well.
    recipe.restrain("a_si", lb=5.430, ub=5.430, scaled=True)
    recipe.restrain("delta2_si", lb=3.54, ub=3.54, scaled=True)
    recipe.restrain("Biso_0_si", lb=0.645, ub=0.645, scaled=True)

    # Give the recipe away so it can be used!
    return recipe


if __name__ == "__main__":

    # Make the data and the recipe
    niciffile = "data/ni.cif"
    siciffile = "data/si.cif"
    data = "data/si90ni10-q27r60-xray.gr"

    # Make the recipe
    recipe = makeRecipe(niciffile, siciffile, data)

    # Optimize
    scipyOptimize(recipe)

    # Generate and print the FitResults
    res = FitResults(recipe)
    res.printResults()

    # Plot!
    plotResults(recipe)

# End of file
