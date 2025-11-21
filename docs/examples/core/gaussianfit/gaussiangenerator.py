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
FitContribution in order to fit a Gaussian profile. The recipe creation is much
like in gaussianrecipe.py, except that it uses our custom GaussianGenerator
class.  ProfileGenerators are usually used to organize profile calculators that
require more information than can be conveniently passed into a function call,
but can be used for simple calculations as well.  The GaussianGenerator class
is an example of a ProfileGenerator that can be used by a FitContribution to
help generate a the profile.

Instructions

Run gaussianrecipe.py and this example. Note how the output is identical. Next
read through 'GaussianGenerator' class.  This provides a simple example of how
to create a custom ProfileGenerator.  Finally read the 'make_recipe' code to
see how the GaussianGenerator is used.  Contrast this to the 'make_recipe'
section in gaussianrecipe.py.

Extensions

- Remove the amplitude from GaussianGenerator and instead use the 'setEquation'
  method of the FitContribution to account for it. Note that the
  GaussianGenerator will be accessible by its name, "g".
"""

from pathlib import Path

from numpy import exp

from diffpy.srfit.fitbase import (
    FitContribution,
    FitRecipe,
    Profile,
    ProfileGenerator,
)

######
#  Example Code


class GaussianGenerator(ProfileGenerator):
    """A class for calculating a Gaussian profile.

    Generating a Gaussian is not difficult, as was shown in
    gaussianrecipe.py. Here we create a class that encapsulates this
    functionality. Placing this class in a python module would make it
    possible to import it and reuse it, thereby saving future code
    writing and debugging.

    The purpose of a ProfileGenerator is to 1) provide a function that
    generates a profile signal 2) organize the Parameters required for
    the calculation

    Thus, this class overloads the __init__ method to create the
    necessary Parameters for the calculation, and the __call__ method to
    generate the signal.
    """

    def __init__(self, name):
        """Define the generator.

        Note that a ProfileGenerator needs a name passed in the initializer.
        This makes it so the generator can be referenced by name when it is
        part of a FitContribution.

        Here we create the Parameters for the calculation.

        A       --  The amplitude
        x0      --  The center
        sigma   --  The width
        """
        # This initializes various parts of the generator
        ProfileGenerator.__init__(self, name)

        # Here we create new Parameters using the '_newParameter' method of
        # ProfileGenerator. The signature is
        # _newParameter(name, value).
        # See the API for full details.
        self._newParameter("A", 1.0)
        self._newParameter("x0", 0.0)
        self._newParameter("sigma", 1.0)
        return

    def __call__(self, x):
        """Calculate the profile.

        Here we calculate the Gaussian profile given the independent
        variable, x. We will define it as we did in gaussianrecipe.py.
        """
        # First we must get the values of the Parameters. Since we used
        # _newParameter to create them, the Parameters are accessible as
        # attributes by name.
        A = self.A.value
        x0 = self.x0.value
        sigma = self.sigma.value

        # Now we can use them. Note that we imported exp from numpy at the top
        # of the module.
        y = A * exp(-0.5 * (x - x0) ** 2 / sigma**2)

        # Now return the value.
        return y


# End class GaussianGenerator


def make_recipe():
    """Create a recipe that uses the GaussianGenerator.

    This will create a FitContribution that uses the GaussianGenerator,
    associate this with a Profile, and use this to define a FitRecipe.
    """

    # The Profile
    # Create a Profile to hold the experimental and calculated signal.
    profile = Profile()

    # Load data and add it to the profile. This uses the loadtxt function from
    # numpy.
    gaussian_data = str(Path(__file__).parent / "gaussian.dat")
    profile.loadtxt(gaussian_data)

    # The ProfileGenerator
    # Create a GaussianGenerator named "g". This will be the name we use to
    # refer to the generator from within the FitContribution equation.
    generator = GaussianGenerator("g")

    # The FitContribution
    # Create a FitContribution that will associate the Profile with the
    # GaussianGenerator.  The GaussianGenerator will be accessible as an
    # attribute of the FitContribution by its name ("g"). Note that this will
    # set the fitting equation to "g", which calls the GaussianGenerator.
    contribution = FitContribution("g1")
    contribution.addProfileGenerator(generator)
    contribution.setProfile(profile)

    # The FitRecipe
    # Now we create the FitRecipe and add the FitContribution.
    recipe = FitRecipe()
    recipe.addContribution(contribution)

    # Specify which Parameters we want to vary in the fit.  This will add
    # Variables to the FitRecipe that directly modify the Parameters of the
    # FitContribution.
    #
    # We create a variable for each Parameter of the GaussianGenerator. Note
    # that the Parameters belong to the GaussianGenerator, not the
    # FitContribution as in gaussianrecipe.py. We initialize parameters as in
    # gaussianrecipe.py so we can expect the same output.
    recipe.addVar(generator.A, 1)
    recipe.addVar(generator.x0, 5)
    recipe.addVar(generator.sigma, name="sig")
    recipe.sig.value = 1

    # Give the recipe away so it can be used!
    return recipe


if __name__ == "__main__":

    # We can use main from gaussianrecipe.py, since this doesn't care if we use
    # a ProfileGenerator or not.
    from gaussianrecipe import main

    main()

# End of file
