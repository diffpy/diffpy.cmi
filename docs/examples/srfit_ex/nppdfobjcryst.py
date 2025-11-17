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
"""Example of a nanoparticle PDF refinement using DebyePDFGenerator.

This example is similar to crystalpdfobjcryst.py, except that it uses
the DebyePDFGenerator from SrReal to refine a pyobjcryst Molecule.
"""

import numpy

from diffpy.srfit.fitbase import (
    FitContribution,
    FitRecipe,
    FitResults,
    Profile,
)
from diffpy.srfit.pdf import DebyePDFGenerator

######
#  Example Code


def makeRecipe(molecule, datname):
    """Create a recipe that uses the DebyePDFGenerator."""

    # The Profile
    profile = Profile()

    # Load data and add it to the profile
    profile.loadtxt(datname)
    profile.setCalculationRange(xmin=1.2, xmax=8)

    # The ProfileGenerator
    # Create a DebyePDFGenerator named "G".
    generator = DebyePDFGenerator("G")
    generator.setStructure(molecule)
    # These are metadata needed by the generator
    generator.setQmin(0.68)
    generator.setQmax(22)

    # The FitContribution
    contribution = FitContribution("bucky")
    contribution.addProfileGenerator(generator)
    contribution.setProfile(profile, xname="r")

    # Make a FitRecipe.
    recipe = FitRecipe()
    recipe.addContribution(contribution)

    # Specify which parameters we want to refine. We'll be using the
    # MoleculeParSet within the generator, so let's get a handle to it. See the
    # diffpy.srfit.structure.objcryststructure module for more information
    # about the MoleculeParSet hierarchy.
    c60 = generator.phase

    # First, the isotropic thermal displacement factor.
    Biso = recipe.newVar("Biso")
    for atom in c60.getScatterers():

        # We have defined a 'center' atom that is a dummy, which means that it
        # has no scattering power. It is only used as a reference point for
        # our bond length. We don't want to constrain it.
        if not atom.isDummy():
            recipe.constrain(atom.Biso, Biso)

    # We need to let the molecule expand. If we were modeling it as a crystal,
    # we could let the unit cell expand. For instruction purposes, we use a
    # Molecule to model C60, and molecules have different modeling options than
    # crystals. To make the molecule expand from a central point, we will
    # constrain the distance from each atom to a dummy center atom that was
    # created with the molecule, and allow that distance to vary. (We could
    # also let the nearest-neighbor bond lengths vary, but that would be much
    # more difficult to set up.)
    center = c60.center
    # Create a new Parameter that represents the radius of the molecule. Note
    # that we don't give it an initial value. Since the variable is being
    # directly constrained to further below, its initial value will be inferred
    # from the constraint.
    radius = recipe.newVar("radius")
    for i, atom in enumerate(c60.getScatterers()):

        if atom.isDummy():
            continue

        # This creates a Parameter that moves the second atom according to the
        # bond length. Note that each Parameter needs a unique name.
        par = c60.addBondLengthParameter("rad%i" % i, center, atom)
        recipe.constrain(par, radius)

    # Add the correlation term, scale. The scale is too short to effectively
    # determine qdamp.
    recipe.addVar(generator.delta2, 2)
    recipe.addVar(generator.scale, 1.3e4)

    # Give the recipe away so it can be used!
    return recipe


def plotResults(recipe):
    """Plot the results contained within a refined FitRecipe."""

    # Plot this.
    r = recipe.bucky.profile.x
    g = recipe.bucky.profile.y
    gcalc = recipe.bucky.profile.ycalc
    diffzero = -0.8 * max(g) * numpy.ones_like(g)
    diff = g - gcalc + diffzero

    import pylab

    pylab.plot(r, g, "ob", label="G(r) Data")
    pylab.plot(r, gcalc, "-r", label="G(r) Fit")
    pylab.plot(r, diff, "-g", label="G(r) diff")
    pylab.plot(r, diffzero, "-k")
    pylab.xlabel(r"$r (\AA)$")
    pylab.ylabel(r"$G (\AA^{-2})$")
    pylab.legend(loc=1)

    pylab.show()
    return


def main():

    molecule = makeC60()
    # Make the data and the recipe
    recipe = makeRecipe(molecule, "data/C60.gr")
    # Tell the fithook that we want very verbose output.
    recipe.fithooks[0].verbose = 3

    # Optimize
    from scipy.optimize import leastsq

    leastsq(recipe.residual, recipe.getValues())

    # Print results
    res = FitResults(recipe)
    res.printResults()

    # Plot results
    plotResults(recipe)

    return


c60xyz = """
3.451266498   0.685000000   0.000000000
3.451266498  -0.685000000   0.000000000
-3.451266498   0.685000000   0.000000000
-3.451266498  -0.685000000   0.000000000
0.685000000   0.000000000   3.451266498
-0.685000000   0.000000000   3.451266498
0.685000000   0.000000000  -3.451266498
-0.685000000   0.000000000  -3.451266498
0.000000000   3.451266498   0.685000000
0.000000000   3.451266498  -0.685000000
0.000000000  -3.451266498   0.685000000
0.000000000  -3.451266498  -0.685000000
3.003809890   1.409000000   1.171456608
3.003809890   1.409000000  -1.171456608
3.003809890  -1.409000000   1.171456608
3.003809890  -1.409000000  -1.171456608
-3.003809890   1.409000000   1.171456608
-3.003809890   1.409000000  -1.171456608
-3.003809890  -1.409000000   1.171456608
-3.003809890  -1.409000000  -1.171456608
1.409000000   1.171456608   3.003809890
1.409000000  -1.171456608   3.003809890
-1.409000000   1.171456608   3.003809890
-1.409000000  -1.171456608   3.003809890
1.409000000   1.171456608  -3.003809890
1.409000000  -1.171456608  -3.003809890
-1.409000000   1.171456608  -3.003809890
-1.409000000  -1.171456608  -3.003809890
1.171456608   3.003809890   1.409000000
-1.171456608   3.003809890   1.409000000
1.171456608   3.003809890  -1.409000000
-1.171456608   3.003809890  -1.409000000
1.171456608  -3.003809890   1.409000000
-1.171456608  -3.003809890   1.409000000
1.171456608  -3.003809890  -1.409000000
-1.171456608  -3.003809890  -1.409000000
2.580456608   0.724000000   2.279809890
2.580456608   0.724000000  -2.279809890
2.580456608  -0.724000000   2.279809890
2.580456608  -0.724000000  -2.279809890
-2.580456608   0.724000000   2.279809890
-2.580456608   0.724000000  -2.279809890
-2.580456608  -0.724000000   2.279809890
-2.580456608  -0.724000000  -2.279809890
0.724000000   2.279809890   2.580456608
0.724000000  -2.279809890   2.580456608
-0.724000000   2.279809890   2.580456608
-0.724000000  -2.279809890   2.580456608
0.724000000   2.279809890  -2.580456608
0.724000000  -2.279809890  -2.580456608
-0.724000000   2.279809890  -2.580456608
-0.724000000  -2.279809890  -2.580456608
2.279809890   2.580456608   0.724000000
-2.279809890   2.580456608   0.724000000
2.279809890   2.580456608  -0.724000000
-2.279809890   2.580456608  -0.724000000
2.279809890  -2.580456608   0.724000000
-2.279809890  -2.580456608   0.724000000
2.279809890  -2.580456608  -0.724000000
-2.279809890  -2.580456608  -0.724000000
"""


def makeC60():
    """Make the C60 molecule using pyobjcryst."""

    from pyobjcryst.crystal import Crystal
    from pyobjcryst.molecule import Molecule
    from pyobjcryst.scatteringpower import ScatteringPowerAtom

    # make a crystal box to put the molecule in
    c = Crystal(1, 1, 1, "P1")
    c.SetName("c60frame")

    # put a molecule inside the box
    m = Molecule(c, "c60")
    c.AddScatterer(m)

    # Create a dummy atom at the center.
    m.AddAtom(0, 0, 0, None, "center")

    # Create the scattering power object for the carbon atoms
    sp = ScatteringPowerAtom("C", "C")
    c.AddScatteringPower(sp)
    sp.SetBiso(0.25)

    # Add the other atoms. They will be named C1, C2, ..., C60.
    for i, l in enumerate(c60xyz.strip().splitlines()):
        x, y, z = map(float, l.split())
        m.AddAtom(x, y, z, sp, "C%i" % (i + 1))

    return m


if __name__ == "__main__":

    main()

# End of file
