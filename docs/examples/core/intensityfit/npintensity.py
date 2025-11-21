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
"""Example of using ProfileGenerators in FitContributions.

This is an example of building a ProfileGenerator and using it in a
FitContribution in order to fit theoretical intensity data.  ProfileGenerators
are used to organize profile calculators that require more information than can
be conveniently passed into a function call.  The IntensityGenerator class is
an example of a ProfileGenerator that can be used by a FitContribution to help
generate a the profile.

Instructions

Run the example and note the last line of the output. It will be described in
the code. Then read through 'IntensityGenerator' class.  This will motivate the
need for the ProfileGenerator class. Next read the 'make_recipe' code.  This
will demonstrate how to use the generator, the structure container needed by
the generator and introduce new operations that can be used in a registered
equation.

Extensions

- The IntensityGenerator class uses the 'addParameterSet' method to associate
  the structure adapter (DiffpyStructureParSet) with the generator. Most SrFit
  classes have an 'addParameterSet' class and can store ParameterSet objects.
  Grab the phase object from the IntensityGenerator and try to add it to other
  objects used in the fit recipe. Create variables from the moved Parameters
  rather than from the 'phase' that lives in the IntensityGenerator and see if
  everything still refines.
"""


from pathlib import Path

import numpy

from diffpy.cmi.fit_tools import optimize_recipe
from diffpy.srfit.fitbase import (
    FitContribution,
    FitRecipe,
    FitResults,
    Profile,
    ProfileGenerator,
)
from diffpy.srfit.structure.diffpyparset import DiffpyStructureParSet

######
#  Example Code


class IntensityGenerator(ProfileGenerator):
    """A class for calculating intensity using the Debye equation.

    Calculating intensity from a structure is difficult in general. This
    class takes a diffpy.structure.Structure instance and from that
    generates a theoretical intensity signal. Unlike the example in
    gaussianrecipe.py, the intensity generator is not simple. It must
    take a structure object and some Parameters, and from that generate
    a signal. At the same time, the structure itself (the lattice, atom
    positions, thermal parameters, etc.) needs to be refinable.  Thus we
    define this ProfileGenerator to help us interface which exposes the
    Parameters required by the calculation and provides a way for a
    FitContribution to perform that calculation.

    The purpose of a ProfileGenerator is to 1) provide a function that
    generates a profile signal 2) organize the Parameters required for
    the calculation

    This generator wraps the 'iofq' function defined below. Knowledge of
    this function is not required for this example.
    """

    def __init__(self, name):
        """Define our generator.

        In this example we will keep count of how many times the
        calculation gets performed. The 'count' attribute will be used
        to store the count.
        """
        ProfileGenerator.__init__(self, name)
        # Count the calls
        self.count = 0
        return

    def setStructure(self, strufile):
        """Set the structure used in the calculation.

        strufile    --  The name of a structure file. A
                        diffpy.structure.Structure object will be created from
                        the file, and that object will be passed to the 'iofq'
                        function whenever it is called.

        This will create the refinement Parameters using the
        DiffpyStructureParSet adapter from diffpy.srfit.structure.diffpyparset.
        DiffpyStructureParSet is a ParameterSet object that organizes and gives
        attribute access to Parameters and ParameterSets adapted from a diffpy
        Structure object.  The Parameters embedded in the DiffpyStructureParSet
        are proxies for attributes of the diffpy.structure.Structure object
        that is needed by the 'iofq' function. The Parameters will be
        accessible by name under the 'phase' attribute of this generator, and
        are organized hierarchically:

        phase
          - lattice (retrieved with 'getLattice')
            - a
            - b
            - c
            - alpha
            - beta
            - gamma
          - scatterers (retrieved with 'getScatterers')
            - atom1 (the name depends on the element)
              - x
              - y
              - z
              - occ
              - U11
              - U22
              - U33
              - U12
              - U13
              - U23
              - Uiso
            - etc.

        The diffpy.structure.Structure instance is held within the
        DiffpyStructureParSet as the 'stru' attribute.
        """
        # Load the structure from file
        from diffpy.structure import Structure

        stru = Structure()
        stru.read(strufile)

        # Create a ParameterSet designed to interface with
        # diffpy.structure.Structure objects that organizes the Parameter
        # hierarchy. Note that the DiffpyStructureParSet holds a handle to the
        # loaded structure that we use in the __call__ method below.
        #
        # We pass the diffpy.structure.Structure instance, and give the
        # DiffpyStructureParSet the name "phase".
        parset = DiffpyStructureParSet("phase", stru)

        # Put this ParameterSet in the ProfileGenerator.
        self.addParameterSet(parset)

        return

    def __call__(self, q):
        """Calculate the intensity.

        This ProfileGenerator will be used in a FitContribution that
        will be optimized to fit some data.  By the time this function
        is evaluated, the diffpy.structure.Structure instance has been
        updated by the optimizer via the DiffpyStructureParSet defined
        in setStructure.  Thus, we need only call iofq with the internal
        structure object.
        """
        self.count += 1
        print("iofq called", self.count)
        return iofq(self.phase.stru, q)


# End class IntensityGenerator


def make_recipe(strufile, datname):
    """Create a recipe that uses the IntensityGenerator.

    This will create a FitContribution that uses the IntensityGenerator,
    associate this with a Profile, and use this to define a FitRecipe.
    """

    # The Profile
    # Create a Profile. This will hold the experimental and calculated signal.
    profile = Profile()

    # Load data and add it to the profile
    x, y, u = profile.loadtxt(datname)

    # The ProfileGenerator
    # Create an IntensityGenerator named "I". This will be the name we use to
    # refer to the generator from within the FitContribution equation.  We also
    # need to load the model structure we're using.
    generator = IntensityGenerator("I")
    generator.setStructure(strufile)

    # The FitContribution
    # Create a FitContribution, that will associate the Profile with the
    # ProfileGenerator.  The ProfileGenerator will be accessible as an
    # attribute of the FitContribution by its name ("I").  We also want to tell
    # the FitContribution to name the x-variable of the profile "q", so we can
    # use it in equations with this name.
    contribution = FitContribution("bucky")
    contribution.addProfileGenerator(generator)
    contribution.setProfile(profile, xname="q")

    # Now we're ready to define the fitting equation for the FitContribution.
    # We need to modify the intensity calculation, and we'll do that from
    # within the fitting equation for the sake of instruction. We want to
    # modify the calculation in three ways.  We want to scale it, add a
    # polynomial background, and broaden the peaks.
    #
    # There is added benefit for defining these operations outside of the
    # IntensityGenerator. By combining the different parts of the calculation
    # within the fitting equation, the time-consuming iofq calculation is only
    # performed when a structural Parameter is changed. If only non-structural
    # parameters are changed, such as the background and broadening Parameters,
    # then then previously computed iofq value will be used to compute the
    # contribution equation.  The benefit in this is very apparent when
    # refining the recipe with the LM optimizer, which only changes two
    # variables at a time most of the time. Note in the refinement output how
    # many times the residual is calculated, versus how many times iofq is
    # called when using the optimize_recipe function.

    # We will define the background as a string.

    bkgdstr = "b0 + b1*q + b2*q**2 + b3*q**3 + b4*q**4 + b5*q**5 + b6*q**6 +\
               b7*q**7 + b8*q**8 + b9*q**9"

    # This creates a callable equation named "bkgd" within the FitContribution,
    # and turns the polynomial coefficients into Parameters.
    contribution.registerStringFunction(bkgdstr, "bkgd")

    # We will create the broadening function that we need by creating a python
    # function and registering it with the FitContribution.
    pi = numpy.pi
    exp = numpy.exp

    def gaussian(q, q0, width):
        return (
            1
            / (2 * pi * width**2) ** 0.5
            * exp(-0.5 * ((q - q0) / width) ** 2)
        )

    # This registers the python function and extracts the name and creates
    # Parameters from the arguments.
    contribution.registerFunction(gaussian)

    # Center the Gaussian so it is not truncated.
    contribution.q0.value = x[len(x) // 2]

    # Now we can incorporate the scale and bkgd into our calculation. We also
    # convolve the signal with the Gaussian to broaden it. Recall that we don't
    # need to supply arguments to the registered functions unless we want to
    # make changes to their input values.
    contribution.setEquation("scale * convolve(I, gaussian) + bkgd")

    # Make the FitRecipe and add the FitContribution.
    recipe = FitRecipe()
    recipe.addContribution(contribution)

    # Specify which parameters we want to refine.
    recipe.addVar(contribution.b0, 0)
    recipe.addVar(contribution.b1, 0)
    recipe.addVar(contribution.b2, 0)
    recipe.addVar(contribution.b3, 0)
    recipe.addVar(contribution.b4, 0)
    recipe.addVar(contribution.b5, 0)
    recipe.addVar(contribution.b6, 0)
    recipe.addVar(contribution.b7, 0)
    recipe.addVar(contribution.b8, 0)
    recipe.addVar(contribution.b9, 0)

    # We also want to adjust the scale and the convolution width
    recipe.addVar(contribution.scale, 1)
    recipe.addVar(contribution.width, 0.1)

    # We can also refine structural parameters. Here we extract the
    # DiffpyStructureParSet from the intensity generator and use the parameters
    # like we would any others.
    phase = generator.phase

    # We want to allow for isotropic expansion, so we'll constrain the lattice
    # parameters to the same value (the lattice is cubic). Note that we
    # constrain to the "a" Parameter directly. In previous examples, we
    # constrained to a Variable by name. This has the same effect.
    lattice = phase.getLattice()
    a = lattice.a
    recipe.addVar(a)
    recipe.constrain(lattice.b, a)
    recipe.constrain(lattice.c, a)
    # We want to refine the thermal parameters as well. We will add a new
    # Variable that we call "Uiso" and constrain the atomic Uiso values to
    # this. Note that we don't give Uiso an initial value. The initial value
    # will be inferred from the following constraints.
    Uiso = recipe.newVar("Uiso")
    for atom in phase.getScatterers():
        recipe.constrain(atom.Uiso, Uiso)

    # Give the recipe away so it can be used!
    return recipe


def main():

    # Make the data and the recipe
    strufile = str((Path(__file__).parent / "C60.stru").resolve())
    q = numpy.arange(1, 20, 0.05)
    iq_path = str((Path(__file__).parent / "C60.iq").resolve())
    makeData(strufile, q, iq_path, 1.0, 100.68, 0.005, 0.13, 2)

    # Make the recipe
    recipe = make_recipe(strufile, iq_path)

    # Optimize
    optimize_recipe(recipe)

    # Generate and print the FitResults
    res = FitResults(recipe)
    # We want to see how much speed-up we get from bringing the scale and
    # background outside of the intensity generator.  Get the number of calls
    # to the residual function from the FitRecipe, and the number of calls to
    # 'iofq' from the IntensityGenerator.
    rescount = recipe.fithooks[0].count
    calcount = recipe.bucky.I.count
    footer = "iofq called %i%% of the time" % int(100.0 * calcount / rescount)
    res.printResults(footer=footer)

    # Plot!
    plot_results(recipe)

    return


def plot_results(recipe):
    """Plot the results contained within a refined FitRecipe."""

    # All this should be pretty familiar by now.
    q = recipe.bucky.profile.x

    Imeas = recipe.bucky.profile.y
    Icalc = recipe.bucky.profile.ycalc
    bkgd = recipe.bucky.evaluateEquation("bkgd")
    diff = Imeas - Icalc

    import pylab

    pylab.plot(q, Imeas, "ob", label="I(Q) Data")
    pylab.plot(q, Icalc, "r-", label="I(Q) Fit")
    pylab.plot(q, diff, "g-", label="I(Q) diff")
    pylab.plot(q, bkgd, "c-", label="Bkgd. Fit")
    pylab.xlabel(r"$Q (\AA^{-1})$")
    pylab.ylabel("Intensity (arb. units)")
    pylab.legend(loc=1)

    pylab.show()
    return


def iofq(S, q):
    """Calculate I(Q) (X-ray) using the Debye Equation.

    I(Q) = 2 sum(i,j) f_i(Q) f_j(Q) sinc(rij Q) exp(-0.5 ssij Q**2)
    (The exponential term is the Debye-Waller factor.)

    S   --  A diffpy.structure.Structure instance. It is assumed that the
            structure is that of an isolated scatterer. Periodic boundary
            conditions are not applied.
    q   --  The q-points to calculate over.

    This uses cctbx for the calculation of the f_i if it is available,
    otherwise f_i = 1.
    """
    # The functions we need
    sinc = numpy.sinc
    exp = numpy.exp
    pi = numpy.pi

    # The brute-force calculation is very slow. Thus we optimize a little bit.

    # The precision of distance measurements
    deltad = 1e-6
    dmult = int(1 / deltad)
    deltau = deltad**2
    umult = int(1 / deltau)

    pairdict = {}
    elcount = {}
    n = len(S)
    for i in range(n):

        # count the number of each element
        eli = S[i].element
        m = elcount.get(eli, 0)
        elcount[eli] = m + 1

        for j in range(i + 1, n):

            elj = S[j].element

            # Get the pair
            els = [eli, elj]
            els.sort()

            # Get the distance to the desired precision
            d = S.distance(i, j)
            D = int(d * dmult)

            # Get the DW factor to the same precision
            ss = S[i].Uisoequiv + S[j].Uisoequiv
            SS = int(ss * umult)

            # Record the multiplicity of this pair
            key = (els[0], els[1], D, SS)
            mult = pairdict.get(key, 0)
            pairdict[key] = mult + 1

    # Now we can calculate IofQ from the pair dictionary. Making the dictionary
    # first reduces the amount of calls to sinc and exp we have to make.

    # First we must cache the scattering factors
    fdict = {}
    for el in elcount:
        fdict[el] = getXScatteringFactor(el, q)

    # Now we can compute I(Q) for the i != j pairs
    y = 0
    x = q * deltad / pi
    for key, mult in pairdict.items():
        eli = key[0]
        elj = key[1]
        fi = fdict[eli]
        fj = fdict[elj]
        D = key[2]
        SS = key[3]

        # Note that numpy's sinc(x) = sin(x*pi)/(x*pi)
        y += fi * fj * mult * sinc(x * D) * exp(-0.5 * SS * deltau * q**2)

    # We must multiply by 2 since we only counted j > i pairs.
    y *= 2

    # Now we must add in the i == j pairs.
    for el, f in fdict.items():
        y += f**2 * elcount[el]

    # And that's it!

    return y


def getXScatteringFactor(el, q):
    """Get the x-ray scattering factor for an element over the q range.

    If cctbx is not available, f(q) = 1 is used.
    """
    try:
        import cctbx.eltbx.xray_scattering as xray

        wk1995 = xray.wk1995(el)
        g = wk1995.fetch()
        # at_stol - at sin(theta)/lambda = Q/(4*pi)
        f = numpy.asarray(map(g.at_stol, q / (4 * numpy.pi)))
        return f
    except ImportError:
        return 1


def makeData(strufile, q, datname, scale, a, Uiso, sig, bkgc, nl=1):
    """Make some fake data and save it to file.

    Make some data to fit. This uses iofq to calculate an intensity curve, and
    adds to it a background, broadens the peaks, and noise.

    strufile--  A filename holding the sample structure
    q       --  The q-range to calculate over.
    datname --  The name of the file we're saving to.
    scale   --  The scale factor
    a       --  The lattice constant to use
    Uiso    --  The thermal factor for all atoms
    sig     --  The broadening factor
    bkgc    --  A parameter that gives minor control of the background.
    nl      --  Noise level (0, inf), default 1, larger -> less noise.
    """

    from diffpy.structure import Structure

    S = Structure()
    S.read(strufile)

    # Set the lattice parameters
    S.lattice.setLatPar(a, a, a)

    # Set a DW factor
    for a in S:
        a.Uisoequiv = Uiso
    y = iofq(S, q)

    # We want to broaden the peaks as well. This simulates instrument effects.
    q0 = q[len(q) // 2]
    g = numpy.exp(-0.5 * ((q - q0) / sig) ** 2)
    y = numpy.convolve(y, g, mode="same") / sum(g)

    # Add a polynomial background.
    bkgd = (q + bkgc) ** 2 * (1.5 * max(q) - q) ** 5
    bkgd *= 0.2 * max(y) / max(bkgd)

    y += bkgd

    # Multiply by a scale factor
    y *= scale

    # Calculate the uncertainty
    u = (y / nl) ** 0.5

    # And apply the noise
    if nl > 0:
        y = numpy.random.poisson(y * nl) / nl

    # Now save it
    numpy.savetxt(datname, numpy.transpose([q, y, u]))
    return


if __name__ == "__main__":

    main()

# End of file
