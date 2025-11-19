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


def plot_results(x, yobs, ycalc):
    """Plot the results contained within a refined FitRecipe.

    Parameters
    ----------
    x : array-like
        The independent variable.
    yobs : array-like
        The observed/experimental data.
    ycalc : array-like
        The calculated/fitted data.
    """
    diffzero = -0.8 * max(yobs) * np.ones_like(yobs)
    diff = yobs - ycalc + diffzero
    ls = "None"
    marker = "o"
    ms = 5
    mew = 0.5
    mfc = "None"
    plt.plot(
        x,
        yobs,
        ls=ls,
        marker=marker,
        ms=ms,
        mew=mew,
        mfc=mfc,
        label="data",
    )
    plt.plot(x, ycalc, label="calculated")
    plt.plot(x, diff, label="diff")
    plt.plot(x, diffzero, lw=1.0, c="black")
    plt.xlabel(r"$r (\AA)$")
    plt.ylabel(r"$G (\AA^{-2})$")
    plt.legend()
    plt.show()
    return
