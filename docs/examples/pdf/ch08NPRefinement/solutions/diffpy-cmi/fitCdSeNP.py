"""Please see notes in Chapter 9 of the 'PDF to the People' book for
additional explanation of the code.

This Diffpy-CMI script will carry out a structural refinement of various
measured PDFs from CdSe nanoparticles.  It is the same refinements as
are done using PDFgui in this chapter of the book, only this time using
Diffpy-CMI.
"""

# 1: Import relevant system packages that we will need...
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares

# ... and the relevant CMI packages
from diffpy.srfit.fitbase import (
    FitContribution,
    FitRecipe,
    FitResults,
    Profile,
)
from diffpy.srfit.pdf import PDFGenerator, PDFParser
from diffpy.srfit.pdf.characteristicfunctions import spherical_particle
from diffpy.srfit.structure import constrain_as_space_group
from diffpy.structure.parsers import getParser

# Config ##############################
# 2: Give a file path to where your pdf (.gr) and (.cif) files are located.
PWD = Path(__file__).parent.absolute()
DPATH = PWD.parent.parent / "data"

# 3: Give an identifying name for the refinement.
FIT_ID_BASE = "Fit_CdSe"

# 4: Specify the names of the input PDF file.
GR_NAME_SEARCH_STRING = "CdSe"

# 5: Specify the filename for the structure we'd like to use.
STRU_FILE_SEARCH_STRING = GR_NAME_SEARCH_STRING


# Experimental PDF Config ######################
# 6: Specify the min, max, and step r-values of
# the PDF (that we want to fit over)
# also, specify the Q_max and Q_min values used to reduce the PDF.
PDF_RMIN = 0.5
PDF_RMAX = 40
PDF_RSTEP = 0.01
QMAX = 19
QMIN = 1.0

# PDF initialize refinable variables #############
# 7: In this case, initial values for the lattice parameters
# and ADPs, for both phases, will be taken directly from
# the .cif structures.
SCALE_I = 0.1
DELTA2_I = 5
PSIZE_I = 40
UISO_I = 0.01
SCALE_PHASE_I = 0.50
DATA_SCALE_I = SCALE_I


# 8: Instrumental will be fixed based on values obtained from a
# separate calibration step. These are hard-coded here.
QDAMP = 0.058
QBROAD = 0.0

RUN_PARALLEL = False
OPTI_OPTS = {"ftol": 1e-3, "gtol": 1e-5, "xtol": 1e-4}
SHOW_PLOT = False


# Functions that will carry out the refinement ##################
# 9: Make the recipe that the fit will follow.
# Here we create a function to make a recipe designed to fit our
# data using one phase.
def make_recipe_one_phase(cif_path, dat_path, adp_iso=True):
    """Creates and returns a Fit Recipe object using just one phase.

    Parameters
    ----------
    cif_path :  string, The location and filename of the structure
                XYZ file to load
    dat_path :  string, The full path to the PDF data to be fit.
    adp_iso :   bool, specifying if ADPs are isotropic (True) or
                anisotropic (False).

    Returns
    ----------
    recipe :    The initialized Fit Recipe object using the datname
                and structure path provided.
    """
    # 10: Create a CIF file parsing object, parse and load the structure, and
    # grab the space group name.
    p_cif = getParser("cif")
    stru1 = p_cif.parse_file(cif_path)
    sg = p_cif.spacegroup.short_name

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

    # If you have a multi-core computer (you probably do), run
    # your refinement in parallel!
    if RUN_PARALLEL:
        try:
            import multiprocessing
            from multiprocessing import Pool

            import psutil

            syst_cores = multiprocessing.cpu_count()
            cpu_percent = psutil.cpu_percent()
            avail_cores = np.floor((100 - cpu_percent) / (100.0 / syst_cores))
            ncpu = int(np.max([1, avail_cores]))
            pool = Pool(processes=ncpu)
            generator_crystal1.parallel(ncpu=ncpu, mapfunc=pool.map)
        except ImportError:
            print(
                "\nYou don't appear to have the necessary packages "
                "for parallelization"
            )

    # 14: Set the Fit Contribution profile to the Profile object.
    contribution.set_profile(profile, xname="r")

    # 15: Set an equation, based on your PDF generators.
    # Here we add an extra layer of complexity, incorporating
    # "f" int our equation. This new term
    # incorporates damping to our PDF to model the effect of
    # finite crystallite size.
    # In this case we use a function which models a spherical NP.
    contribution.register_function(spherical_particle, name="f")
    contribution.set_equation("s1*G1*f")

    # 16: Create the Fit Recipe object that holds all the details of the fit.
    recipe = FitRecipe()
    recipe.add_contribution(contribution)

    # 17: Initialize the instrument parameters, Q_damp and Q_broad, and
    # assign Q_max and Q_min.
    generator_crystal1.qdamp.value = QDAMP
    generator_crystal1.qbroad.value = QBROAD
    generator_crystal1.setQmax(QMAX)
    generator_crystal1.setQmin(QMIN)

    # 18: Add, initialize, and tag variables in the Fit Recipe object.
    # In this case we also add psize, which is the NP size.
    recipe.add_variable(contribution.s1, SCALE_I, tag="scale")
    recipe.add_variable(
        contribution.particle_diameter, PSIZE_I, name="psize", tag="psize"
    )
    recipe.add_variable(
        generator_crystal1.delta2, name="Delta2", value=DELTA2_I, tag="d2"
    )

    # 19: Now, we want to have one behavior if we desire isotropic ADPs
    # and another behavior if we desire anistropic ADPs. To achieve this we
    # use our 'adp_iso' argument and an 'if..else' statement.
    if adp_iso:
        # 20: We explicitly want to tell our structure to not allow anisotropy.
        # We pass in the boolean 'False' to the anisotropy attribute
        # of the structure.
        stru1.anisotropy = False
        # 21: Use the srfit function constrain_as_space_group to constrain
        # the lattice and atomic positions according to the space group.
        # Note we do not include ADPs in the following.
        spacegroupparams = constrain_as_space_group(
            generator_crystal1.phase, sg, constrainadps=False
        )

        for par in spacegroupparams.latpars:
            recipe.add_variable(par, fixed=False, tag="lat")
        for par in spacegroupparams.xyzpars:
            recipe.add_variable(par, fixed=False, tag="xyz")

        # 22: We create the variables of isotropic ADP and assign the initial
        # value to them,
        # specified above. In this portion of the 'if' statement, we use
        # isotropic ADP for all atoms
        cd_uiso = recipe.create_new_variable(
            "Cd_Uiso", value=UISO_I, tag="adp"
        )
        se_uiso = recipe.create_new_variable(
            "Se_Uiso", value=UISO_I, tag="adp"
        )

        # 23: For all atoms in the structure model, we constrain their
        # Uiso according to their species.
        atoms = generator_crystal1.phase.getScatterers()
        for atom in atoms:
            if atom.element == "Cd":
                recipe.add_constraint(atom.Uiso, cd_uiso)
            elif atom.element == "Se":
                recipe.add_constraint(atom.Uiso, se_uiso)

    # 24: Now, we want to have one behavior if we desire isotropic ADPs
    # and another behavior if we desire anistropic ADPs. To achieve this we
    # use our 'adp_iso' argument and an 'if..else' statement.
    else:
        # 25: We explicitly want to tell our structure to allow anisotropy.
        # We pass in the boolean 'True' to the anisotropy attribute of
        # the structure.
        stru1.anisotropy = True

        # 26: Use the srfit function constrain_as_space_group to constrain
        # the lattice and atomic positions according to the space group.
        # Note we do include ADPs in the following.
        spacegroupparams = constrain_as_space_group(
            generator_crystal1.phase, sg
        )

        for par in spacegroupparams.latpars:
            recipe.add_variable(par, fixed=False, tag="lat")
        for par in spacegroupparams.adppars:
            recipe.add_variable(par, fixed=False, tag="adp")
        for par in spacegroupparams.xyzpars:
            recipe.add_variable(par, fixed=False, tag="xyz")

    # 27: Return the Fit Recipe object to be optimized
    return recipe

    # End of function


# 28: Make the recipe that the fit will follow.
# Here we create a second function to make a recipe designed to fit our
# data using two phases.
def make_recipe_two_phase(cif_path1, cif_path2, dat_path):
    """Creates and returns a Fit Recipe object using two phases.

    Parameters
    ----------
    cif_path1 :  string, The location and filename of the first structure
                 cif file to load
    cif_path2 :  string, The location and filename of the second structure
                 cif file to load
    dat_path :   string, The full path to the PDF data to be fit.

    Returns
    ----------
    recipe :    The initialized Fit Recipe object using the dat_path
                and structure paths provided.
    """
    # 29: Create a CIF file parsing object, parse and load the structure, and
    # grab the space group name for the first structure.
    p_cif1 = getParser("cif")
    stru1 = p_cif1.parse_file(cif_path1)
    sg1 = p_cif1.spacegroup.short_name

    # 30: Create a CIF file parsing object, parse and load the structure, and
    # grab the space group name for the second structure.
    p_cif2 = getParser("cif")
    stru2 = p_cif2.parse_file(cif_path2)
    sg2 = p_cif2.spacegroup.short_name

    # 31: Create a Profile object for the experimental dataset and
    # tell this profile the range and mesh of points in r-space.
    profile = Profile()
    parser = PDFParser()
    parser.parse_file(dat_path)
    profile.load_parsed_data(parser)
    profile.set_calculation_range(xmin=PDF_RMIN, xmax=PDF_RMAX, dx=PDF_RSTEP)

    # 32: Create a PDF Generator object for a periodic structure model
    # of phase 1.
    generator_crystal1 = PDFGenerator("G1")
    generator_crystal1.setStructure(stru1, periodic=True)

    # 33: Create a PDF Generator object for a periodic structure model
    # of phase 2.
    generator_crystal2 = PDFGenerator("G2")
    generator_crystal2.setStructure(stru2, periodic=True)

    # 33: Make convenient lists of the generators and space group names
    generators = [generator_crystal1, generator_crystal2]
    sgs = [sg1, sg2]

    # 34: Create a Fit Contribution objects, one for each phase. This is new,
    # as we need to tell the Fit Contribution about BOTH the phase
    # represented by "generator_crystal1" AND the phase represented
    # by "generator_crystal2".
    contribution = FitContribution("crystal")
    contribution.add_profile_generator(generator_crystal1)
    contribution.add_profile_generator(generator_crystal2)

    # If you have a multi-core computer (you probably do), run your refinement
    # in parallel!
    if RUN_PARALLEL:
        try:
            import multiprocessing
            from multiprocessing import Pool

            import psutil

            syst_cores = multiprocessing.cpu_count()
            cpu_percent = psutil.cpu_percent()
            avail_cores = np.floor((100 - cpu_percent) / (100.0 / syst_cores))
            ncpu = int(np.max([1, avail_cores]))
            pool = Pool(processes=ncpu)
            generator_crystal1.parallel(ncpu=ncpu, mapfunc=pool.map)
        except ImportError:
            print(
                "\nYou don't appear to have the necessary packages "
                "for parallelization"
            )

    # 35: Set the Fit Contribution profile to the Profile object.
    contribution.set_profile(profile, xname="r")

    # 36: Set an equation, based on your PDF generators. Here we add an
    # extra layer of complexity, incorporating "f" int our equation.
    # This new term incorporates damping to our PDF to model the
    # effect of finite crystallite size.
    # In this case we use a function which models a spherical NP.
    # We use the same function for each phase.
    contribution.register_function(spherical_particle, name="f")
    contribution.set_equation("data_scale*(s1*G1*f + (1.0-s1)*G2*f)")

    # 37: Create the Fit Recipe object that holds all the details of the fit.
    recipe = FitRecipe()
    recipe.add_contribution(contribution)

    # 38: Add, initialize, and tag both scale parameters, the crystal size
    # parameter,
    # and a correlated motion parameter. We will use one correlated motion
    # parameter across both phases.
    recipe.add_variable(contribution.s1, SCALE_PHASE_I, tag="phase_scale")
    recipe.add_variable(contribution.data_scale, DATA_SCALE_I, tag="scale")
    recipe.add_variable(
        contribution.particle_diameter, PSIZE_I, name="psize", tag="psize"
    )
    delta2 = recipe.create_new_variable("Delta2", value=DELTA2_I, tag="d2")

    # 39: restrain our new parameters.
    recipe.add_soft_bounds(
        "data_scale", lower_bound=0.0, scaled=True, sig=0.00001
    )

    recipe.add_soft_bounds(
        "s1", lower_bound=0.0, upper_bound=1.0, scaled=True, sig=0.00001
    )

    recipe.add_soft_bounds("psize", lower_bound=0.0, scaled=True, sig=0.00001)

    # 40: Initialize the instrument parameters, Q_damp and Q_broad, and
    # assign Q_max and Q_min.
    generator_crystal1.qdamp.value = QDAMP
    generator_crystal1.qbroad.value = QBROAD
    generator_crystal1.setQmax(QMAX)
    generator_crystal1.setQmin(QMIN)

    # 41: We create the variables of ADP and assign the initial value to them,
    # specified above. In this example, we use isotropic ADP for all atoms.
    # We will use these across both phases
    cd_uiso = recipe.create_new_variable("Cd_Uiso", value=UISO_I, tag="adp")
    se_uiso = recipe.create_new_variable("Se_Uiso", value=UISO_I, tag="adp")

    # 42: Now, we loop over our list of generators and space groups
    for generator, sg in zip(generators, sgs):
        # 43: The minus sign '-' will cause problems in parameter naming, so
        # we should remove it.
        sg_clean = sg.replace("-", "")

        # 44: constrain the delta2 parameter of each generator according to
        # our parameter
        recipe.add_constraint(generator.delta2, delta2)

        # 45: turn off anisotropy
        generator.phase.stru.anisotropy = False

        # 46: Use the srfit function constrain_as_space_group to constrain
        # the lattice, ADP parameters, and atomic positions according to the
        # space group.
        spacegroupparams = constrain_as_space_group(
            generator.phase, sg, constrainadps=False
        )

        for par in spacegroupparams.latpars:
            recipe.add_variable(
                par,
                name=f"{par.name}_phase_{sg_clean}",
                fixed=False,
                tag="lat",
            )
        for par in spacegroupparams.xyzpars:
            recipe.add_variable(
                par,
                name=f"{par.name}_phase_{sg_clean}",
                fixed=False,
                tag="xyz",
            )

        # 47: We do not use the ADP portion of spacegroupparams, instead we
        # add isotropic ADPs. We use one set across both phases.
        atoms = generator.phase.getScatterers()
        for atom in atoms:
            if atom.element == "Cd":
                recipe.add_constraint(atom.Uiso, cd_uiso)
            elif atom.element == "Se":
                recipe.add_constraint(atom.Uiso, se_uiso)

    # 48: Return the Fit Recipe object to be optimized
    return recipe

    # End of function


# We create a useful function 'plot_results' for writing a plot of the fit
# to disk.
def plot_results(recipe, fig_name):
    """Creates plots of the fitted PDF and residual, and writes them to
    disk as *.pdf files.

    Parameters
    ----------
    recipe :    The optimized Fit Recipe object containing the PDF data
                we wish to plot.
    fig_name :  Path object, the full path to the figure file to create..

    Returns
    ----------
    None
    """
    if not isinstance(fig_name, Path):
        fig_name = Path(fig_name)

    plt.clf()
    plt.close("all")

    r = recipe.crystal.profile.x

    # Create the standard observed/fit/diff plot using the recipe.
    fig, ax1 = recipe.plot_recipe(
        show=False,
        return_fig=True,
        data_style="o",
        data_label="G(r) Data",
        fit_label="G(r) Fit",
        diff_label="G(r) diff",
        xlabel=r"r ($\mathrm{\AA}$)",
        ylabel=r"G ($\mathrm{\AA}$$^{-2}$)",
        offset_scale=0.65,
    )

    # Tune the tick markers. We are picky!
    ax1.tick_params(axis="both", which="major", top=True, right=True)

    # Set the boundaries on the x-axis
    ax1.set_xlim(r[0], r[-1])

    # This is going to make a figure pop up on screen for you to view.
    # The script will pause until you close the figure!
    if SHOW_PLOT:
        plt.show()

    # Let's save the figure!
    fig.savefig(fig_name.parent / f"{fig_name.name}.pdf", format="pdf")

    # End of function


# 49: We again create a 'main' function to be run when we execute the script.
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

    # 50: Search our data path for all the .gr files matching a pattern
    # and parse out an identifying string from each file name.
    data_files = list(DPATH.glob(f"*{GR_NAME_SEARCH_STRING}*.gr"))
    data_ids = [ff.stem.split("-")[-1] for ff in data_files]

    # 51: Search our data path for all the .cif files matching a pattern
    # and parse out an identifying string from each file name.
    stru_files = list(DPATH.glob(f"*{STRU_FILE_SEARCH_STRING}*.cif"))
    stru_names = [ff.stem.split("-")[-1] for ff in stru_files]

    # 52: We want to handle both isotropic and anisotropic ADP constraints,
    # so we create a list of strings to keep track of which case we are
    # working on
    adp_names = ["isotropic", "anisotropic"]

    # 53: We want to loop on all the PDF data files we found, and their
    # associated identifying string.
    for data_file, data_id in zip(data_files, data_ids):

        # 54: We are going to programmatically create a name for our fit,
        # which will include the root base name we chose at the beginning
        # of the script, as well as identifying string parsed out from
        # the PDF data file.
        basename = f"{FIT_ID_BASE}_{data_id}_two_phase"
        print(basename)

        # 55: We call our two phase make recipe function to build our recipe.
        # We do this outside our loop on structure files, because we need to
        # include both our structure files here.
        recipe = make_recipe_two_phase(
            str(stru_files[0]), str(stru_files[1]), str(data_file)
        )

        # 56: As before, we fix all parameters, create a list of tags and,
        # loop over them refining sequentially.
        recipe.fix("all")
        recipe.fithooks[0].verbose = 3
        tags = ["scale", "psize", "lat", "adp", "d2", "phase_scale", "all"]
        for tag in tags:
            recipe.free(tag)
            least_squares(
                recipe.residual, recipe.values, x_scale="jac", **OPTI_OPTS
            )

        # 57: Write the fitted data to a file.
        profile = recipe.crystal.profile
        profile.savetxt(fitdir / f"{basename}.fit")

        # 58: Print the fit results to the terminal.
        res = FitResults(recipe)
        res.print_results()

        # 59: Write the fit results to a file.
        header = "crystal_HF.\n"
        res.save_results(resdir / f"{basename}.res", header=header)

        # 60: Write a plot of the fit to a (pdf) file.
        plot_results(recipe, figdir / basename)

        # 61: Now we loop on every structure file we found as well as
        # the identifying string we parsed from each file name.
        for stru_file, stru_name in zip(stru_files, stru_names):
            # 62: We loop over all type pf ADP symmetry constraints.
            for adp_symm in adp_names:

                # 63: We are going to programmatically create a name for our
                # fit, which will include the root base name we chose at the
                # beginning of the script, the identifying string parsed out
                # from the PDF data file, the structure we are using, and
                # whether we are working in with isotropic or anisotropic
                # constraints on our ADPs.
                basename = (
                    f"{FIT_ID_BASE}_{data_id}_{stru_name}_{adp_symm}_ADPs"
                )
                print(basename)

                # 64: We call our single phase make recipe function to build
                # our recipe. We do this inside our loop on structure files,
                # so we we test each structure file separately.
                # We also have a simple logic evaluation to decide what boolean
                # to pass to our new 'adp_symm' argument.
                recipe = make_recipe_one_phase(
                    str(stru_file),
                    str(data_file),
                    True if adp_symm == "isotropic" else False,
                )

                # 65: In some cases, the symmetry of the space group means that
                # isotropic and anisotropic constraints on our ADPs yield
                # essentially equivalent models. here, we check to see if all
                # the ADP parameters in our fit are isotropic,
                # and if we are attempting to use anisotropic, we skip the
                # fitting.
                recipe.fix("all")
                recipe.free("adp")
                if (
                    np.all(["iso" in par for par in recipe.get_names()])
                    and adp_symm == "anisotropic"
                ):
                    continue

                # 66: As before, we fix all parameters, create a list of
                # tags and, loop over them refining sequentially.
                recipe.fix("all")
                recipe.fithooks[0].verbose = 3
                tags = ["scale", "psize", "lat", "adp", "d2", "all"]
                for tag in tags:
                    recipe.free(tag)
                    least_squares(
                        recipe.residual,
                        recipe.values,
                        x_scale="jac",
                        **OPTI_OPTS,
                    )

                # 67: Write the fitted data to a file.
                profile = recipe.crystal.profile
                profile.savetxt(fitdir / f"{basename}.fit")

                # 68: Print the fit results to the terminal.
                res = FitResults(recipe)
                res.print_results()

                # 69: Write the fit results to a file.
                header = "crystal_HF.\n"
                res.save_results(resdir / f"{basename}.res", header=header)

                # 70: Write a plot of the fit to a (pdf) file.
                plot_results(recipe, figdir / basename)

    # End of function


# This tells python to run the 'main' function we defined above.
if __name__ == "__main__":
    main()

# End of file
