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
"""Example of fitting a crystal-like nanoparticle (nanocrystal) PDF.

This is an example of modeling the PDF from a nanocrystal as an
attenuated bulk PDF. This involves a crystal PDF calculation and a
spherical nanoparticle characteristic function. The equation we model is
Gnano(r) = f(r) * Gbulk(r), where f(r) is the nanoparticle
characteristic function for the nanoparticle shape. Functions for
calculating the characteristic function in the
diffpy.srfit.pdf.characteristicfunctions module.
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


def makeRecipe(ciffile, grdata):
    """Make a recipe to model a crystal-like nanoparticle PDF."""

    # Set up a PDF fit as has been done in other examples.
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

    # Register the nanoparticle shape factor.
    from diffpy.srfit.pdf.characteristicfunctions import sphericalCF

    pdfcontribution.registerFunction(sphericalCF, name="f")

    # Now we set up the fitting equation.
    pdfcontribution.setEquation("f * G")

    # Now make the recipe. Make sure we fit the characteristic function shape
    # parameters, in this case 'psize', which is the diameter of the particle.
    recipe = FitRecipe()
    recipe.addContribution(pdfcontribution)

    phase = pdfgenerator.phase
    for par in phase.sgpars:
        recipe.addVar(par)

    recipe.addVar(pdfcontribution.psize, 20)
    recipe.addVar(pdfgenerator.scale, 1)
    recipe.addVar(pdfgenerator.delta2, 0)
    recipe.B11_0 = 0.1

    return recipe


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

    recipe = makeRecipe(ciffile, grdata)
    scipyOptimize(recipe)

    res = FitResults(recipe)
    res.printResults()

    plotResults(recipe)

# End of file
