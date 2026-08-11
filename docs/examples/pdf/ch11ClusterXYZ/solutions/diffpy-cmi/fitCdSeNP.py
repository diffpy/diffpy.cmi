# Please see notes in Chapter 12 of the "PDF to the People" book for further
# explanation of the code.
#
# This Diffpy-CMI script will carry out a discrete structural refinement of
# a measured PDF from atomically precise CdSe quantum dots using the Debye
# PDF Generator
#
# 1: Import packages that we will need
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

from diffpy.srfit.fitbase import (
    FitContribution,
    FitRecipe,
    FitResults,
    Profile,
)
from diffpy.srfit.pdf import DebyePDFGenerator, PDFParser
from diffpy.structure import Structure

# Config ##############################
# 2: Give a file path to where your PDF (.gr) and structure (.cif) files are
# located.
PWD = Path(__file__).parent.absolute()
DPATH = PWD.parent.parent / "data"

# 3: Give an identifying name for the refinement, similar
# to what you would name a fit tree in PDFGui.
FIT_ID = "CdSe_discrete"

# 4: Specify the names of the input PDF and XYZ files.
GR_NAME = "CdSe.gr"
XYZ_NAME = "CdSe.xyz"

# Experimental PDF Config ######################
# 5: Specify the min, max, and step r-values of
# the PDF (that we want to fit over)
# also, specify the Q_max and Q_min values used to reduce the PDF.
PDF_RMIN = 1.5
PDF_RMAX = 20
PDF_RSTEP = 0.01
QMAX = 20
QMIN = 1.0

# PDF initialize refinable variables #############
# 6: We specify initial values for an isotropic expansion factor,
# scale, isotropic thermal parameters per element, and a
# correlated motion parameter
ZOOMSCALE_I = 1.0
SCALE_I = 1.0
UISO_Cd_I = 0.01
UISO_Se_I = 0.01
DELTA2_I = 5

# 7: We will give initial values for the instrumental parameters and
# keet them fixed during the refinement.
QDAMP_I = 0.06
QBROAD_I = 0.00

RUN_PARALLEL = False


# Functions that will carry out the refinement ##################
# 8: Make the Fit Recipe object
def make_recipe(stru_path, dat_path):
    """Creates and returns a Fit Recipe object.

    Parameters
    ----------
    stru_path : string, The full path to the structure XYZ file to load.
    dat_path :  string, The full path to the PDF data to be fit.

    Returns
    ----------
    fitrecipe : The initialized Fit Recipe object using the datname and
                structure provided.
    """

    stru1 = Structure(filename=str(stru_path))

    # 9: Create a Profile object for the experimental dataset and
    # tell this profile the range and mesh of points in r-space.
    profile = Profile()
    parser = PDFParser()
    parser.parse_file(dat_path)
    profile.load_parsed_data(parser)
    profile.set_calculation_range(xmin=PDF_RMIN, xmax=PDF_RMAX, dx=PDF_RSTEP)

    # 10: Create a Debye PDF Generator object for the discrete structure model.
    generator_cluster1 = DebyePDFGenerator("G1")
    generator_cluster1.setStructure(stru1, periodic=False)

    # 11: Create a Fit Contribution object.
    contribution = FitContribution("cluster")
    contribution.add_profile_generator(generator_cluster1)

    # If you have a multi-core computer (you probably do),
    # run your refinement in parallel!
    # Here we just make sure not to overload your CPUs.
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
        generator_cluster1.parallel(ncpu=ncpu, mapfunc=pool.map)
    # 12: Set the Fit Contribution profile to the Profile object.
    contribution.set_profile(profile, xname="r")

    # 13: Set an equation, based on your PDF generators.
    contribution.set_equation("s1*G1")

    # 14: Create the Fit Recipe object that holds all the details of the fit.
    recipe = FitRecipe()
    recipe.add_contribution(contribution)

    # 15: Initialize the instrument parameters, Q_damp and Q_broad, and
    # assign Q_max and Q_min.
    generator_cluster1.qdamp.value = QDAMP_I
    generator_cluster1.qbroad.value = QBROAD_I
    generator_cluster1.setQmax(QMAX)
    generator_cluster1.setQmin(QMIN)

    # 16: Add, initialize, and tag variables in the Fit Recipe object.
    # In this case we also add psize, which is the NP size.
    recipe.add_variable(contribution.s1, SCALE_I, tag="scale")

    # 17: Define a phase and lattice from the Debye PDF Generator
    # object and assign an isotropic lattice expansion factor tagged
    # "zoomscale" to the structure.

    phase_cluster1 = generator_cluster1.phase

    lattice1 = phase_cluster1.getLattice()

    recipe.create_new_variable("zoomscale", ZOOMSCALE_I, tag="lat")

    recipe.add_constraint(lattice1.a, "zoomscale")
    recipe.add_constraint(lattice1.b, "zoomscale")
    recipe.add_constraint(lattice1.c, "zoomscale")

    # 18: Initialize an atoms object and constrain the isotropic
    # Atomic Displacement Parameters (ADPs) per element.

    atoms1 = phase_cluster1.getScatterers()

    recipe.create_new_variable("Cd_Uiso", UISO_Cd_I, tag="adp")
    recipe.create_new_variable("Se_Uiso", UISO_Se_I, tag="adp")

    for atom in atoms1:
        if atom.element.title() == "Cd":
            recipe.add_constraint(atom.Uiso, "Cd_Uiso")
        elif atom.element.title() == "Se":
            recipe.add_constraint(atom.Uiso, "Se_Uiso")

    # 19: Add and tag a variable for correlated motion effects
    recipe.add_variable(
        generator_cluster1.delta2, name="CdSe_Delta2", value=DELTA2_I, tag="d2"
    )

    return recipe

    # End of function


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
    stru_path = DPATH / XYZ_NAME

    # 23: Call 'make_recipe' to create our fit recipe.
    recipe = make_recipe(str(stru_path), str(gr_path))

    # Tell the Fit Recipe we want to write the maximum amount of
    # information to the terminal during fitting.
    recipe.fithooks[0].verbose = 3

    recipe.fix("all")

    tags = ["lat", "scale", "adp", "d2", "all"]
    for tag in tags:
        recipe.free(tag)
        least_squares(recipe.residual, recipe.values, x_scale="jac")

    # Write the fitted data to a file.
    profile = recipe.cluster.profile
    profile.savetxt(fitdir / f"{basename}.fit")

    # Print the fit results to the terminal.
    res = FitResults(recipe)
    res.print_results()

    # Write the fit results to a file.
    header = "crystal_HF.\n"
    res.save_results(resdir / f"{basename}.res", header=header)

    # Write a plot of the fit to a (pdf) file.
    fig, ax1 = recipe.plot_recipe(
        return_fig=True,
        xlabel=r"r($\mathrm{\AA}$)",
        ylabel=r"G($\mathrm{\AA}$$^{-2}$)",
    )
    fig.savefig(figdir / f"{basename}.pdf", format="pdf")

    # End of function


if __name__ == "__main__":
    main()

# End of file
