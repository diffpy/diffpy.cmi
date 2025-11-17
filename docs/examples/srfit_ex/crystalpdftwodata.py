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
"""Example of a PDF refinement of two-phase structure.

This example uses PDFGenerator to refine a single structure two
profiles. This will require setting up two FitContribution, each with
its own PDFGenerator. However, the PDFGenerators will refer to the same
underlying ObjCrystCrystalParSet.
"""

import numpy
from gaussianrecipe import scipyOptimize
from pyobjcryst import loadCrystal

from diffpy.srfit.fitbase import (
    FitContribution,
    FitRecipe,
    FitResults,
    Profile,
)
from diffpy.srfit.pdf import PDFGenerator, PDFParser

######
#  Example Code


def makeRecipe(ciffile, xdatname, ndatname):
    """Create a fitting recipe for crystalline PDF data."""

    # The Profiles
    # We need a profile for each data set. This means that we will need two
    # FitContributions as well.
    xprofile = Profile()
    nprofile = Profile()

    # Load data and add it to the proper Profile.
    parser = PDFParser()
    parser.parseFile(xdatname)
    xprofile.loadParsedData(parser)
    xprofile.setCalculationRange(xmax=20)

    parser = PDFParser()
    parser.parseFile(ndatname)
    nprofile.loadParsedData(parser)
    nprofile.setCalculationRange(xmax=20)

    # The ProfileGenerators
    # We need one of these for the x-ray data.
    xgenerator = PDFGenerator("G")
    stru = loadCrystal(ciffile)
    xgenerator.setStructure(stru)

    # And we need one for the neutron data. We want to refine the same
    # structure object in each PDFGenerator. This would suggest that we add the
    # same Crystal to each. However, if we do that then we will have two
    # Parameters for each Crystal data member (two Parameters for the "a"
    # lattice parameter, etc.), held in different ObjCrystCrystalParSets, each
    # managed by its own PDFGenerator. Thus, changes made to the Crystal
    # through one PDFGenerator will not be known to the other PDFGenerator
    # since their ObjCrystCrystalParSets don't know about each other. The
    # solution is to share ObjCrystCrystalParSets rather than Crystals. This
    # way there is only one Parameter for each Crystal data member. (An
    # alternative to this is to constrain each structure Parameter to be varied
    # to the same variable. The present approach is easier and less error
    # prone.)
    #
    # Tell the neutron PDFGenerator to use the phase from the x-ray
    # PDFGenerator.
    ngenerator = PDFGenerator("G")
    ngenerator.setPhase(xgenerator.phase)

    # The FitContributions
    # We associate the x-ray PDFGenerator and Profile in one FitContribution...
    xcontribution = FitContribution("xnickel")
    xcontribution.addProfileGenerator(xgenerator)
    xcontribution.setProfile(xprofile, xname="r")
    # and the neutron objects in another.
    ncontribution = FitContribution("nnickel")
    ncontribution.addProfileGenerator(ngenerator)
    ncontribution.setProfile(nprofile, xname="r")

    # This example is different than the previous ones in that we are composing
    # a residual function from other residuals (one for the x-ray contribution
    # and one for the neutron contribution). The relative magnitude of these
    # residuals effectively determines the influence of each contribution over
    # the fit. This is a problem in this case because the x-ray data has
    # uncertainty values associated with it (on the order of 1e-4), and the
    # chi^2 residual is proportional to 1 / uncertainty**2. The neutron has no
    # uncertainty, so it's chi^2 is proportional to 1. Thus, my optimizing
    # chi^2 we would give the neutron data practically no weight in the fit. To
    # get around this, we will optimize a different metric.
    #
    # The contribution's residual can be either chi^2, Rw^2, or custom crafted.
    # In this case, we should minimize Rw^2 of each contribution so that each
    # one can contribute roughly equally to the fit.
    xcontribution.setResidualEquation("resv")
    ncontribution.setResidualEquation("resv")

    # Make the FitRecipe and add the FitContributions.
    recipe = FitRecipe()
    recipe.addContribution(xcontribution)
    recipe.addContribution(ncontribution)

    # Now we vary and constrain Parameters as before.
    recipe.addVar(xgenerator.scale, 1, "xscale")
    recipe.addVar(ngenerator.scale, 1, "nscale")
    recipe.addVar(xgenerator.qdamp, 0.01, "xqdamp")
    recipe.addVar(ngenerator.qdamp, 0.01, "nqdamp")
    # delta2 is a non-structual material property. Thus, we constrain together
    # delta2 Parameter from each PDFGenerator.
    delta2 = recipe.newVar("delta2", 2)
    recipe.constrain(xgenerator.delta2, delta2)
    recipe.constrain(ngenerator.delta2, delta2)

    # We only need to constrain phase properties once since there is a single
    # ObjCrystCrystalParSet for the Crystal.
    phase = xgenerator.phase
    for par in phase.sgpars:
        recipe.addVar(par)
    recipe.B11_0 = 0.1

    # Give the recipe away so it can be used!
    return recipe


def plotResults(recipe):
    """Plot the results contained within a refined FitRecipe."""

    # All this should be pretty familiar by now.
    xr = recipe.xnickel.profile.x
    xg = recipe.xnickel.profile.y
    xgcalc = recipe.xnickel.profile.ycalc
    xdiffzero = -0.8 * max(xg) * numpy.ones_like(xg)
    xdiff = xg - xgcalc + xdiffzero

    nr = recipe.nnickel.profile.x
    ng = recipe.nnickel.profile.y
    ngcalc = recipe.nnickel.profile.ycalc
    ndiffzero = -0.8 * max(ng) * numpy.ones_like(ng)
    ndiff = ng - ngcalc + ndiffzero

    import pylab

    pylab.subplot(2, 1, 1)
    pylab.plot(xr, xg, "bo", label="G(r) x-ray Data")
    pylab.plot(xr, xgcalc, "r-", label="G(r) x-ray Fit")
    pylab.plot(xr, xdiff, "g-", label="G(r) x-ray diff")
    pylab.plot(xr, xdiffzero, "k-")
    pylab.legend(loc=1)

    pylab.subplot(2, 1, 2)
    pylab.plot(nr, ng, "bo", label="G(r) neutron Data")
    pylab.plot(nr, ngcalc, "r-", label="G(r) neutron Fit")
    pylab.plot(nr, ndiff, "g-", label="G(r) neutron diff")
    pylab.plot(nr, ndiffzero, "k-")
    pylab.xlabel(r"$r (\AA)$")
    pylab.ylabel(r"$G (\AA^{-2})$")
    pylab.legend(loc=1)

    pylab.show()
    return


if __name__ == "__main__":

    # Make the data and the recipe
    ciffile = "data/ni.cif"
    xdata = "data/ni-q27r60nodg-xray.gr"
    ndata = "data/ni-q27r100-neutron.gr"

    # Make the recipe
    recipe = makeRecipe(ciffile, xdata, ndata)

    # Optimize
    scipyOptimize(recipe)

    # Generate and print the FitResults
    res = FitResults(recipe)
    res.printResults()

    # Plot!
    plotResults(recipe)

# End of file
