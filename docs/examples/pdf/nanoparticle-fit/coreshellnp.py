#!/usr/bin/env python
########################################################################
#
# diffpy.srfit      by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2011 The Trustees of Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Chris Farrow, Peng Tian
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE_DANSE.txt for license information.
#
########################################################################
"""Refine the structure of a core-shell nanoparticle.

This applies the characteristic function formalism described in
nppdfcrystal.py to the case of a spherical core-shell nanoparticle. The
modeling approach we use is to refine the core and shell as two
different phases, each with an appropriate characteristic function.
"""

from pathlib import Path

import matplotlib.pyplot as plt
from pyobjcryst import loadCrystal
from scipy.optimize import leastsq

from diffpy.cmi.fit_tools import plot_results
from diffpy.srfit.fitbase import (
    FitContribution,
    FitRecipe,
    FitResults,
    Profile,
)
from diffpy.srfit.pdf import PDFGenerator, PDFParser

# Example Code


def make_recipe(stru1, stru2, datname):
    """Create a fitting recipe for crystalline PDF data."""

    # The Profile
    profile = Profile()

    # Load data and add it to the profile
    parser = PDFParser()
    parser.parseFile(datname)
    profile.loadParsedData(parser)
    profile.setCalculationRange(xmin=1.5, xmax=45, dx=0.1)

    # The ProfileGenerator
    # In order to fit the core and shell phases simultaneously, we must use two
    # PDFGenerators.
    #
    # The generator for the CdS core. We call it "G_CdS" and will use this name
    # later when we set the fitting equation in the FitContribution.
    generator_cds = PDFGenerator("G_CdS")
    generator_cds.setStructure(stru1)
    generator_cds.setQmax(26)
    generator_cds.qdamp.value = 0.0396
    # The generator for the ZnS shell. We call it "G_ZnS".
    generator_zns = PDFGenerator("G_ZnS")
    generator_zns.setStructure(stru2)
    generator_zns.setQmax(26)
    generator_zns.qdamp.value = 0.0396

    # The FitContribution
    # Add both generators and the profile to the FitContribution.
    contribution = FitContribution("cdszns")
    contribution.addProfileGenerator(generator_cds)
    contribution.addProfileGenerator(generator_zns)
    contribution.setProfile(profile, xname="r")

    # Set up the characteristic functions. We use a spherical CF for the core
    # and a spherical shell CF for the shell. Since this is set up as two
    # phases, we implicitly assume that the core-shell correlations contribute
    # very little to the PDF.
    from diffpy.srfit.pdf.characteristicfunctions import shellCF, sphericalCF

    contribution.registerFunction(sphericalCF, name="f_CdS")
    contribution.registerFunction(shellCF, name="f_ZnS")

    # Write the fitting equation. We want to sum the PDFs from each phase and
    # multiply it by a scaling factor.
    contribution.setEquation("scale * (f_CdS * G_CdS +  f_ZnS * G_ZnS)")

    # Make the FitRecipe and add the FitContribution.
    recipe = FitRecipe()
    recipe.addContribution(contribution)

    # Vary the inner radius and thickness of the shell. Constrain the core
    # diameter to twice the shell radius.
    recipe.addVar(contribution.radius, 15)
    recipe.addVar(contribution.thickness, 11)
    recipe.constrain(contribution.psize, "2 * radius")

    # Configure the fit variables
    # Start by configuring the scale factor and resolution factors.
    # We want the sum of the phase scale factors to be 1.
    recipe.newVar("scale_CdS", 0.7)
    recipe.constrain(generator_cds.scale, "scale_CdS")
    recipe.constrain(generator_zns.scale, "1 - scale_CdS")
    # We also want the resolution factor to be the same on each.

    # Vary the global scale as well.
    recipe.addVar(contribution.scale, 0.3)

    # Now we can configure the structural parameters. We tag the different
    # structural variables so we can easily turn them on and off in the
    # subsequent refinement.
    phase_cds = generator_cds.phase
    for par in phase_cds.sgpars.latpars:
        recipe.addVar(par, name=par.name + "_cds", tag="lat")
    for par in phase_cds.sgpars.adppars:
        recipe.addVar(par, 1, name=par.name + "_cds", tag="adp")
    recipe.addVar(phase_cds.sgpars.xyzpars.z_1, name="z_1_cds", tag="xyz")
    # Since we know these have stacking disorder, constrain the B33 adps for
    # each atom type.
    recipe.constrain("B33_1_cds", "B33_0_cds")
    recipe.addVar(generator_cds.delta2, name="delta2_cds", value=5)

    phase_zns = generator_zns.phase
    for par in phase_zns.sgpars.latpars:
        recipe.addVar(par, name=par.name + "_zns", tag="lat")
    for par in phase_zns.sgpars.adppars:
        recipe.addVar(par, 1, name=par.name + "_zns", tag="adp")
    recipe.addVar(phase_zns.sgpars.xyzpars.z_1, name="z_1_zns", tag="xyz")
    recipe.constrain("B33_1_zns", "B33_0_zns")
    recipe.addVar(generator_zns.delta2, name="delta2_zns", value=2.5)

    # Give the recipe away so it can be used!
    return recipe


def main():
    """Set up and refine the recipe."""

    # Make the data and the recipe
    base_path = Path(__file__).parent
    cdsciffile = base_path / "CdS.cif"
    znsciffile = base_path / "ZnS.cif"
    data = base_path / "CdS_ZnS_nano.gr"

    # Make the recipe
    stru1 = loadCrystal(cdsciffile)
    stru2 = loadCrystal(znsciffile)
    recipe = make_recipe(stru1, stru2, data)

    recipe.fithooks[0].verbose = 3
    # Optimize - we do this in steps to help convergence
    recipe.fix("all")

    # Start with the lattice parameters. In make_recipe, these were tagged with
    # "lat". Here is how we use that.
    recipe.free("lat")
    leastsq(recipe.residual, recipe.values, maxfev=50)

    # Now the scale and phase fraction.
    recipe.free("scale", "scale_CdS")
    leastsq(recipe.residual, recipe.values, maxfev=50)

    # The ADPs.
    recipe.free("adp")
    leastsq(recipe.residual, recipe.values, maxfev=100)

    # The delta2 parameters.
    recipe.free("delta2_cds", "delta2_zns")
    leastsq(recipe.residual, recipe.values, maxfev=50)

    # The shape parameters.
    recipe.free("radius", "thickness")
    leastsq(recipe.residual, recipe.values, maxfev=50)

    # The positional parameters.
    recipe.free("xyz")
    leastsq(recipe.residual, recipe.values)

    # Generate and print the FitResults
    res = FitResults(recipe)
    res.printResults()

    # Plot!
    r = recipe.cdszns.profile.x
    g = recipe.cdszns.profile.y
    gcalc = recipe.cdszns.profile.ycalc
    plot_results(r, g, gcalc)
    plt.show()
    return


if __name__ == "__main__":
    main()

# End of file
