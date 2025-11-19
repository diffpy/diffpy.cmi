import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize as opt

try:
    from bg_mpl_stylesheets.styles import all_styles

    plt.style.use(all_styles["bg-style"])
except ImportError:
    pass

optimizers = {
    "leastsq": opt.leastsq,
}


def optimize_recipe(recipe, optimizer: str = "leastsq", **kwargs):
    """Optimize the recipe using any selected SciPy optimizer.

    minimize the residuals (`FitRecipe().residual`) of a FitRecipe by
    using a SciPy optimization function.

    Parameters
    ----------
    recipe : FitRecipe
        The FitRecipe to be optimized.
    optimizer : str, optional
        The SciPy optimizer to use. Options are:
        'leastsq', 'least_squares', 'minimize'. Default is 'leastsq'.
    **kwargs
        Additional keyword arguments to pass to the optimizer.
    """
    if optimizer not in optimizers:
        raise ValueError(
            f"Unknown optimizer '{optimizer}'. "
            f"Choose from {list(optimizers.keys())}"
        )

    function = optimizers[optimizer]
    x0 = recipe.getValues()
    residuals = recipe.residual
    if optimizer == "leastsq":
        print("Optimizing using scipy.optimize.leastsq")
        function(residuals, x0, **kwargs)
        return


def plot_results(r, gobs, gcalc):
    """Plot the results contained within a refined FitRecipe.

    Parameters
    ----------
    r : array-like
        The independent variable.
    gobs : array-like
        The observed/experimental data.
    gcalc : array-like
        The calculated/fitted data.
    """
    diffzero = -0.8 * max(gobs) * np.ones_like(gobs)
    diff = gobs - gcalc + diffzero
    ls = "None"
    marker = "o"
    ms = 5
    mew = 0.5
    mfc = "None"
    plt.plot(
        r,
        gobs,
        ls=ls,
        marker=marker,
        ms=ms,
        mew=mew,
        mfc=mfc,
        label="G(r) Data",
    )
    plt.plot(r, gcalc, label="G(r) Fit")
    plt.plot(r, diff, label="G(r) diff")
    plt.plot(r, diffzero, lw=1.0, c="black")
    plt.xlabel(r"$r (\AA)$")
    plt.ylabel(r"$G (\AA^{-2})$")
    plt.legend(loc=1)
    return
