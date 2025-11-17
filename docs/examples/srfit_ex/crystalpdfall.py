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

This example uses PDFGenerator to refine a the two phase nickel-silicon
structure to all the available data.
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


def makeProfile(datafile):
    """Make an place data within a Profile."""
    profile = Profile()
    parser = PDFParser()
    parser.parseFile(datafile)
    profile.loadParsedData(parser)
    profile.setCalculationRange(xmax=20)
    return profile


def makeContribution(name, generator, profile):
    """Make a FitContribution and add a generator and profile."""
    contribution = FitContribution(name)
    contribution.addProfileGenerator(generator)
    contribution.setProfile(profile, xname="r")
    return contribution


def makeRecipe(
    ciffile_ni, ciffile_si, xdata_ni, ndata_ni, xdata_si, xdata_sini
):
    """Create a fitting recipe for crystalline PDF data."""

    # The Profiles
    # We need a profile for each data set.
    xprofile_ni = makeProfile(xdata_ni)
    xprofile_si = makeProfile(xdata_si)
    nprofile_ni = makeProfile(ndata_ni)
    xprofile_sini = makeProfile(xdata_sini)

    # The ProfileGenerators
    # We create one for each phase and share the phases.
    xgenerator_ni = PDFGenerator("xG_ni")
    stru = loadCrystal(ciffile_ni)
    xgenerator_ni.setStructure(stru)
    phase_ni = xgenerator_ni.phase

    xgenerator_si = PDFGenerator("xG_si")
    stru = loadCrystal(ciffile_si)
    xgenerator_si.setStructure(stru)
    phase_si = xgenerator_si.phase

    ngenerator_ni = PDFGenerator("nG_ni")
    ngenerator_ni.setPhase(phase_ni)

    xgenerator_sini_ni = PDFGenerator("xG_sini_ni")
    xgenerator_sini_ni.setPhase(phase_ni)

    xgenerator_sini_si = PDFGenerator("xG_sini_si")
    xgenerator_sini_si.setPhase(phase_si)

    # The FitContributions
    # We one of these for each data set.
    xcontribution_ni = makeContribution("xnickel", xgenerator_ni, xprofile_ni)
    xcontribution_si = makeContribution("xsilicon", xgenerator_si, xprofile_si)
    ncontribution_ni = makeContribution("nnickel", ngenerator_ni, nprofile_ni)
    xcontribution_sini = makeContribution(
        "xsini", xgenerator_sini_ni, xprofile_sini
    )
    xcontribution_sini.addProfileGenerator(xgenerator_sini_si)
    xcontribution_sini.setEquation("scale * (xG_sini_ni +  xG_sini_si)")

    # As explained in another example, we want to minimize using Rw^2.
    xcontribution_ni.setResidualEquation("resv")
    xcontribution_si.setResidualEquation("resv")
    ncontribution_ni.setResidualEquation("resv")
    xcontribution_sini.setResidualEquation("resv")

    # Make the FitRecipe and add the FitContributions.
    recipe = FitRecipe()
    recipe.addContribution(xcontribution_ni)
    recipe.addContribution(xcontribution_si)
    recipe.addContribution(ncontribution_ni)
    recipe.addContribution(xcontribution_sini)

    # Now we vary and constrain Parameters as before.
    for par in phase_ni.sgpars:
        recipe.addVar(par, name=par.name + "_ni")
    delta2_ni = recipe.newVar("delta2_ni", 2.5)
    recipe.constrain(xgenerator_ni.delta2, delta2_ni)
    recipe.constrain(ngenerator_ni.delta2, delta2_ni)
    recipe.constrain(xgenerator_sini_ni.delta2, delta2_ni)

    for par in phase_si.sgpars:
        recipe.addVar(par, name=par.name + "_si")
    delta2_si = recipe.newVar("delta2_si", 2.5)
    recipe.constrain(xgenerator_si.delta2, delta2_si)
    recipe.constrain(xgenerator_sini_si.delta2, delta2_si)

    # Now the experimental parameters
    recipe.addVar(xgenerator_ni.scale, name="xscale_ni")
    recipe.addVar(xgenerator_si.scale, name="xscale_si")
    recipe.addVar(ngenerator_ni.scale, name="nscale_ni")
    recipe.addVar(xcontribution_sini.scale, 1.0, "xscale_sini")
    recipe.newVar("pscale_sini_ni", 0.8)
    recipe.constrain(xgenerator_sini_ni.scale, "pscale_sini_ni")
    recipe.constrain(xgenerator_sini_si.scale, "1 - pscale_sini_ni")

    # The qdamp parameters are too correlated to vary so we fix them based on
    # previous measurements.
    xgenerator_ni.qdamp.value = 0.055
    xgenerator_si.qdamp.value = 0.051
    ngenerator_ni.qdamp.value = 0.030
    xgenerator_sini_ni.qdamp.value = 0.052
    xgenerator_sini_si.qdamp.value = 0.052

    # Give the recipe away so it can be used!
    return recipe


def plotResults(recipe):
    """Plot the results contained within a refined FitRecipe."""

    # All this should be pretty familiar by now.
    xnickel = recipe.xnickel
    xr_ni = xnickel.profile.x
    xg_ni = xnickel.profile.y
    xgcalc_ni = xnickel.profile.ycalc
    xdiffzero_ni = -0.8 * max(xg_ni) * numpy.ones_like(xg_ni)
    xdiff_ni = xg_ni - xgcalc_ni + xdiffzero_ni

    xsilicon = recipe.xsilicon
    xr_si = xsilicon.profile.x
    xg_si = xsilicon.profile.y
    xgcalc_si = xsilicon.profile.ycalc
    xdiffzero_si = -0.8 * max(xg_si) * numpy.ones_like(xg_si)
    xdiff_si = xg_si - xgcalc_si + xdiffzero_si

    nnickel = recipe.nnickel
    nr_ni = nnickel.profile.x
    ng_ni = nnickel.profile.y
    ngcalc_ni = nnickel.profile.ycalc
    ndiffzero_ni = -0.8 * max(ng_ni) * numpy.ones_like(ng_ni)
    ndiff_ni = ng_ni - ngcalc_ni + ndiffzero_ni

    xsini = recipe.xsini
    xr_sini = xsini.profile.x
    xg_sini = xsini.profile.y
    xgcalc_sini = xsini.profile.ycalc
    xdiffzero_sini = -0.8 * max(xg_sini) * numpy.ones_like(xg_sini)
    xdiff_sini = xg_sini - xgcalc_sini + xdiffzero_sini

    import pylab

    pylab.subplot(2, 2, 1)
    pylab.plot(xr_ni, xg_ni, "bo", label="G(r) x-ray nickel Data")
    pylab.plot(xr_ni, xgcalc_ni, "r-", label="G(r) x-ray nickel Fit")
    pylab.plot(xr_ni, xdiff_ni, "g-", label="G(r) x-ray nickel diff")
    pylab.plot(xr_ni, xdiffzero_ni, "k-")
    pylab.xlabel(r"$r (\AA)$")
    pylab.ylabel(r"$G (\AA^{-2})$")
    pylab.legend(loc=1)

    pylab.subplot(2, 2, 2)
    pylab.plot(xr_si, xg_si, "bo", label="G(r) x-ray silicon Data")
    pylab.plot(xr_si, xgcalc_si, "r-", label="G(r) x-ray silicon Fit")
    pylab.plot(xr_si, xdiff_si, "g-", label="G(r) x-ray silicon diff")
    pylab.plot(xr_si, xdiffzero_si, "k-")
    pylab.legend(loc=1)

    pylab.subplot(2, 2, 3)
    pylab.plot(nr_ni, ng_ni, "bo", label="G(r) neutron nickel Data")
    pylab.plot(nr_ni, ngcalc_ni, "r-", label="G(r) neutron nickel Fit")
    pylab.plot(nr_ni, ndiff_ni, "g-", label="G(r) neutron nickel diff")
    pylab.plot(nr_ni, ndiffzero_ni, "k-")
    pylab.legend(loc=1)

    pylab.subplot(2, 2, 4)
    pylab.plot(xr_sini, xg_sini, "bo", label="G(r) x-ray sini Data")
    pylab.plot(xr_sini, xgcalc_sini, "r-", label="G(r) x-ray sini Fit")
    pylab.plot(xr_sini, xdiff_sini, "g-", label="G(r) x-ray sini diff")
    pylab.plot(xr_sini, xdiffzero_sini, "k-")
    pylab.legend(loc=1)

    pylab.show()
    return


if __name__ == "__main__":

    # Make the data and the recipe
    ciffile_ni = "data/ni.cif"
    ciffile_si = "data/si.cif"
    xdata_ni = "data/ni-q27r60-xray.gr"
    ndata_ni = "data/ni-q27r100-neutron.gr"
    xdata_si = "data/si-q27r60-xray.gr"
    xdata_sini = "data/si90ni10-q27r60-xray.gr"

    # Make the recipe
    recipe = makeRecipe(
        ciffile_ni, ciffile_si, xdata_ni, ndata_ni, xdata_si, xdata_sini
    )

    # Optimize
    scipyOptimize(recipe)

    # Generate and print the FitResults
    res = FitResults(recipe)
    res.printResults()

    # Plot!
    plotResults(recipe)

# End of file
