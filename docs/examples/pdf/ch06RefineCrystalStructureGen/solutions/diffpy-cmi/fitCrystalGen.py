"""Please see notes in Chapter 7 of the 'PDF to the People' book for
additional explanation of the code.

This Diffpy-CMI script will carry out a structural refinement of a
measured PDF from Ba0.7K0.3Zn1.7Mn0.3As2.  It is the same refinement as
is done using PDFgui in this chapter of the book, only this time using
Diffpy-CMI.
"""

# 1: Import relevant system packages that we will need...
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from bg_mpl_stylesheets.styles import all_styles
from scipy.optimize import least_squares

# ... and the relevant CMI packages
from diffpy.srfit.fitbase import (
    FitContribution,
    FitRecipe,
    FitResults,
    Profile,
)
from diffpy.srfit.pdf import PDFGenerator, PDFParser
from diffpy.srfit.structure import constrain_as_space_group
from diffpy.structure.atom import Atom
from diffpy.structure.parsers import get_parser

plt.style.use(all_styles["bg-style"])

# Config ##############################
# 2: Give a file path to where your pdf (.gr) and (.cif) files are located.
PWD = Path(__file__).parent.absolute()
DPATH = PWD.parent.parent / "data"

# 3: Give an identifying name for the refinement.
FIT_ID = "Fit_Ba0.7K0.3Zn1.7Mn0.3As2"

# 4: Specify the names of the input PDF and cif files.
GR_NAME = "BaZn2As2_K-Mn-doped_300K.gr"
CIF_NAME = "BaZn2As2.cif"

# Experimental PDF Config ######################
# 5: Specify the min, max, and step r-values of
# the PDF (that we want to fit over)
# also, specify the Q_max and Q_min values used to reduce the PDF.
PDF_RMIN = 1.5
PDF_RMAX = 30
PDF_RSTEP = 0.01
QMAX = 25
QMIN = 0.1

# PDF initialize refinable variables #############
# 6: In this case, initial values for the tetragonal lattice
# parameters and ADPs will be taken directly from the .cif
# structure, so we don't need to specify them here.
SCALE_I = 0.4
DELTA1_I = 1.6
K_FRAC_I = 0.30
MN_FRAC_I = 0.15

# 7: Instrumental will be fixed based on values obtained from a
# separate calibration step. These are hard-coded here.
QDAMP_I = 0.03842
QBROAD_I = 0.01707

# If we want to run using multiprocessors, we can switch this to 'True'.
# This requires that the 'psutil' python package installed.
RUN_PARALLEL = False


# Functions that will carry out the refinement ##################
# 8: We define a function 'make_recipe' to make the recipe that the
# fit will follow.
def make_recipe(cif_path, dat_path):
    """Creates and returns a Fit Recipe object.

    Parameters
    ----------
    cif_path :  string, The full path to the structure CIF file to load.
    dat_path :  string, The full path to the PDF data to be fit.

    Returns
    ----------
    recipe :    The initialized Fit Recipe object using the datname and
                structure path provided.
    """
    # 9: Create a CIF file parsing object, parse and load the structure, and
    # grab the space group name.
    p_cif = get_parser("cif")
    stru1 = p_cif.parse_file(cif_path)
    sg = p_cif.spacegroup.short_name
    stru1.anisotropy = True

    # 10 Here we have something new. The cif file we loaded is for BaZn2As,
    # But our sample contains K on the Ba site. and Mn on the Zn site.
    # we need to add some atoms, so we loop over all atoms in the structure,
    # and if the atom element matches "Ba" or "Zn" we add a K or Zn at the same
    # coordinates, respectively.
    for atom in stru1:
        if "Ba" in atom.element:
            stru1.add_new_atom(Atom("K", xyz=atom.xyz))
        elif "Zn" in atom.element:
            stru1.add_new_atom(Atom("Mn", xyz=atom.xyz))

    # 11: Create a Profile object for the experimental dataset and
    # tell this profile the range and mesh of points in r-space.
    profile = Profile()
    parser = PDFParser()
    parser.parse_file(dat_path)
    profile.load_parsed_data(parser)
    profile.set_calculation_range(xmin=PDF_RMIN, xmax=PDF_RMAX, dx=PDF_RSTEP)

    # 12: Create a PDF Generator object for a periodic structure model.
    generator_crystal1 = PDFGenerator("G1")
    generator_crystal1.setStructure(stru1, periodic=True)

    # 13: Create a Fit Contribution object.
    contribution = FitContribution("crystal")
    contribution.add_profile_generator(generator_crystal1)

    # If you have a multi-core computer (you probably do), run your refinement
    # in parallel!
    if RUN_PARALLEL:
        try:
            import multiprocessing
            from multiprocessing import Pool

            import psutil
        except ImportError:
            print(
                "\nYou don't appear to have the necessary packages for "
                "parallelization"
            )
        syst_cores = multiprocessing.cpu_count()
        cpu_percent = psutil.cpu_percent()
        avail_cores = np.floor((100 - cpu_percent) / (100.0 / syst_cores))
        ncpu = int(np.max([1, avail_cores]))
        pool = Pool(processes=ncpu)
        generator_crystal1.parallel(ncpu=ncpu, mapfunc=pool.map)

    # 14: Set the Fit Contribution profile to the Profile object.
    contribution.set_profile(profile, xname="r")

    # 15: Set an equation, based on your PDF generators. This is
    # again a simple case, with only a scale and a single PDF generator.
    contribution.set_equation("s1*G1")

    # 16: Create the Fit Recipe object that holds all the details of the fit.
    recipe = FitRecipe()
    recipe.add_contribution(contribution)

    # 17: Initialize the instrument parameters, Q_damp and Q_broad, and
    # assign Q_max and Q_min.
    generator_crystal1.qdamp.value = QDAMP_I
    generator_crystal1.qbroad.value = QBROAD_I
    generator_crystal1.setQmax(QMAX)
    generator_crystal1.setQmin(QMIN)

    # 18: Add, initialize, and tag the scale variable.
    recipe.add_variable(contribution.s1, SCALE_I, tag="scale")

    # 19: Use the srfit function constrain_as_space_group to constrain
    # the lattice and ADP parameters according to the I4/mmm space
    # group setting.
    spacegroupparams = constrain_as_space_group(generator_crystal1.phase, sg)

    for par in spacegroupparams.latpars:
        recipe.add_variable(par, fixed=False, tag="lat")
    for par in spacegroupparams.adppars:
        recipe.add_variable(par, fixed=False, tag="adp")
    for par in spacegroupparams.xyzpars:
        recipe.add_variable(par, fixed=False, tag="xyz")

    # 20: Add delta, but not instrumental parameters to Fit Recipe.
    recipe.add_variable(
        generator_crystal1.delta1, name="Delta1", value=DELTA1_I, tag="d1"
    )

    # 21: This is also new. We would like to refine the occupancy of
    # both Mn and K, so we need to add two new parameters, here called
    # 'Mn_occ' and 'K_occ.' We give them the tag 'occs' and we initialize
    # them with reasonable values as defined above.
    recipe.create_new_variable(
        name="Mn_occ", value=MN_FRAC_I, fixed=True, tag="occs"
    )
    recipe.create_new_variable(
        name="K_occ", value=K_FRAC_I, fixed=True, tag="occs"
    )

    # 22: Now, we want to constrain the occupancy of sites appropriately.
    # To do this, we loop over all atoms in the structure, and if the
    # atom label matches a pattern, we constrain the occuapncy appropriately.
    for atom in recipe.crystal.G1.phase.atoms:
        if "Ba" in atom.atom.label:
            recipe.add_constraint(atom.occupancy, "1.0 - K_occ")
        if "K" in atom.atom.label:
            recipe.add_constraint(atom.occupancy, "K_occ")
        if "Zn" in atom.atom.label:
            recipe.add_constraint(atom.occupancy, "1.0 - Mn_occ")
        if "Mn" in atom.atom.label:
            recipe.add_constraint(atom.occupancy, "Mn_occ")

    # 23: Return the Fit Recipe object to be optimized.
    return recipe

    # End of function


# 25: We again create a 'main' function to be run when we execute the script.
def main():
    """This will run by default when the file is executed using "python
    file.py" in the command line.

    Parameters
    ----------
    None

    Returns
    ----------
    None
    """

    # Make some folders to store our output files.
    resdir = PWD / "res"
    fitdir = PWD / "fit"
    figdir = PWD / "fig"

    folders = [resdir, fitdir, figdir]

    for folder in folders:
        if not folder.exists():
            folder.mkdir()

    # Establish the location of the data and a name for our fit.
    gr_path = DPATH / GR_NAME
    basename = FIT_ID
    print(basename)

    # Establish the full path of the CIF file with the structure of interest.
    stru_path = DPATH / CIF_NAME

    # 26: Call 'make_recipe' to create our fit recipe.
    recipe = make_recipe(str(stru_path), str(gr_path))

    # Tell the Fit Recipe we want to write the maximum amount of
    # information to the terminal during fitting.
    recipe.fithooks[0].verbose = 3

    # 27: As before, we fix all parameters, create a list of tags and,
    # loop over them refining sequentially. We've added our new 'occs'
    # tag to the list.
    recipe.fix("all")
    tags = ["lat", "scale", "adp", "d1", "occs", "all"]
    for tag in tags:
        recipe.free(tag)
        least_squares(recipe.residual, recipe.values, x_scale="jac")

    # 28: Write the fitted data to a file.
    profile = recipe.crystal.profile
    profile.savetxt(fitdir / f"{basename}.fit")

    # 29: Print the fit results to the terminal.
    res = FitResults(recipe)
    res.print_results()

    # 30: Write the fit results to a file.
    header = "crystal_HF.\n"
    res.save_results(resdir / f"{basename}.res", header=header)

    # 31: Write a plot of the fit to a (pdf) file.
    fig, ax1 = recipe.plot_recipe(
        return_fig=True,
        xlabel=r"r ($\mathrm{\AA}$)",
        ylabel=r"G ($\mathrm{\AA}$$^{-2}$)",
    )
    fig.savefig(figdir / f"{basename}.pdf", format="pdf")

    # End of function


# This tells python to run the 'main' function we defined above.
if __name__ == "__main__":
    main()

# End of file
