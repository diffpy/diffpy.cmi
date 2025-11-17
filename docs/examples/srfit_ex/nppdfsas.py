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
"""Example of combining PDF and SAS nanoparticles data.

This is an example of using both PDF and SAS data in the same fit. This
fits a crystal model to the PDF while fitting a shape model to both the
SAS profile and the PDF data. Using the same shape for the PDF and SAS
provides a feedback mechanism into the fit that allows the PDF and SAS
portions of the fit to guide one another, and in the end gives the shape
of the nanoparticle that agrees best with both the PDF and SAS data.
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
from diffpy.srfit.pdf.characteristicfunctions import SASCF
from diffpy.srfit.sas import SASGenerator, SASParser


def makeRecipe(ciffile, grdata, iqdata):
    """Make complex-modeling recipe where I(q) and G(r) are fit
    simultaneously.

    The fit I(q) is fed into the calculation of G(r), which provides
    feedback for the fit parameters of both.
    """

    # Create a PDF contribution as before
    pdfprofile = Profile()
    pdfparser = PDFParser()
    pdfparser.parseFile(grdata)
    pdfprofile.loadParsedData(pdfparser)
    pdfprofile.setCalculationRange(xmin=0.1, xmax=20)

    pdfcontribution = FitContribution("pdf")
    pdfcontribution.setProfile(pdfprofile, xname="r")

    pdfgenerator = PDFGenerator("G")
    pdfgenerator.setQmax(30.0)
    stru = loadCrystal(ciffile)
    pdfgenerator.setStructure(stru)
    pdfcontribution.addProfileGenerator(pdfgenerator)
    pdfcontribution.setResidualEquation("resv")

    # Create a SAS contribution as well. We assume the nanoparticle is roughly
    # elliptical.
    sasprofile = Profile()
    sasparser = SASParser()
    sasparser.parseFile(iqdata)
    sasprofile.loadParsedData(sasparser)
    if all(sasprofile.dy == 0):
        sasprofile.dy[:] = 1

    sascontribution = FitContribution("sas")
    sascontribution.setProfile(sasprofile)

    from sas.models.EllipsoidModel import EllipsoidModel

    model = EllipsoidModel()
    sasgenerator = SASGenerator("generator", model)
    sascontribution.addProfileGenerator(sasgenerator)
    sascontribution.setResidualEquation("resv")

    # Now we set up a characteristic function calculator that depends on the
    # sas model.
    cfcalculator = SASCF("f", model)

    # Register the calculator with the pdf contribution and define the fitting
    # equation.
    pdfcontribution.registerCalculator(cfcalculator)
    # The PDF for a nanoscale crystalline is approximated by
    # Gnano = f * Gcryst
    pdfcontribution.setEquation("f * G")

    # Moving on
    recipe = FitRecipe()
    recipe.addContribution(pdfcontribution)
    recipe.addContribution(sascontribution)

    # PDF
    phase = pdfgenerator.phase
    for par in phase.sgpars:
        recipe.addVar(par)

    recipe.addVar(pdfgenerator.scale, 1)
    recipe.addVar(pdfgenerator.delta2, 0)

    # SAS
    recipe.addVar(sasgenerator.scale, 1, name="iqscale")
    recipe.addVar(sasgenerator.radius_a, 10)
    recipe.addVar(sasgenerator.radius_b, 10)

    # Even though the cfcalculator and sasgenerator depend on the same sas
    # model, we must still constrain the cfcalculator Parameters so that it is
    # informed of changes in the refined parameters.
    recipe.constrain(cfcalculator.radius_a, "radius_a")
    recipe.constrain(cfcalculator.radius_b, "radius_b")

    return recipe


def fitRecipe(recipe):
    """We refine in stages to help the refinement converge."""

    # Tune SAS.
    recipe.setWeight(recipe.pdf, 0)
    recipe.fix("all")
    recipe.free("radius_a", "radius_b", iqscale=1e8)
    recipe.constrain("radius_b", "radius_a")
    scipyOptimize(recipe)
    recipe.unconstrain("radius_b")

    # Tune PDF
    recipe.setWeight(recipe.pdf, 1)
    recipe.setWeight(recipe.sas, 0)
    recipe.fix("all")
    recipe.free("a", "Biso_0", "scale", "delta2")
    scipyOptimize(recipe)

    # Tune all
    recipe.setWeight(recipe.pdf, 1)
    recipe.setWeight(recipe.sas, 1)
    recipe.free("all")
    scipyOptimize(recipe)

    return


def plotResults(recipe):
    """Plot the results contained within a refined FitRecipe."""

    # All this should be pretty familiar by now.
    r = recipe.pdf.profile.x
    g = recipe.pdf.profile.y
    gcalc = recipe.pdf.profile.ycalc
    diffzero = -0.8 * max(g) * numpy.ones_like(g)
    diff = g - gcalc + diffzero

    gcryst = recipe.pdf.evaluateEquation("G")
    gcryst /= recipe.scale.value

    fr = recipe.pdf.evaluateEquation("f")
    fr *= max(g) / fr[0]

    import pylab

    pylab.plot(r, g, "bo", label="G(r) Data")
    pylab.plot(r, gcryst, "y--", label="G(r) Crystal")
    pylab.plot(r, fr, "k--", label="f(r) calculated (scaled)")
    pylab.plot(r, gcalc, "r-", label="G(r) Fit")
    pylab.plot(r, diff, "g-", label="G(r) diff")
    pylab.plot(r, diffzero, "k-")
    pylab.xlabel(r"$r (\AA)$")
    pylab.ylabel(r"$G (\AA^{-2})$")
    pylab.legend(loc=1)

    pylab.show()
    return


if __name__ == "__main__":

    ciffile = "data/pb.cif"
    grdata = "data/pb_100_qmin1.gr"
    iqdata = "data/pb_100_qmax1.iq"

    recipe = makeRecipe(ciffile, grdata, iqdata)
    recipe.fithooks[0].verbose = 3
    fitRecipe(recipe)

    res = FitResults(recipe)
    res.printResults()

    plotResults(recipe)

# End of file
