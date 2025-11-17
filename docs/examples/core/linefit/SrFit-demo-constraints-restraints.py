import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import plot, title
from scipy.optimize import fmin, leastsq

from diffpy.srfit.fitbase import (
    FitContribution,
    FitRecipe,
    FitResults,
    Profile,
)


def main():
    # ----------------------------------------------------------------------
    # Generate synthetic noisy data: y = 0.5 * x + 3 + noise
    # ----------------------------------------------------------------------
    xobs = np.arange(-10, 10.1)
    dyobs = 0.3 * np.ones_like(xobs)
    yobs = 0.5 * xobs + 3 + dyobs * np.random.randn(xobs.size)

    plot(xobs, yobs, "x")
    title("y = 0.5*x + 3 with Gaussian noise (σ=0.3)")
    plt.show()
    # ----------------------------------------------------------------------
    # Create a Profile object to hold the data
    # ----------------------------------------------------------------------
    linedata = Profile()
    linedata.setObservedProfile(xobs, yobs, dyobs)

    # ----------------------------------------------------------------------
    # Define a FitContribution: linear model A*x + B
    # ----------------------------------------------------------------------
    linefit = FitContribution("linefit")
    linefit.setProfile(linedata)
    linefit.setEquation("A * x + B")

    linefit.show()

    # Assign initial guesses for parameters
    linefit.A = 3
    linefit.B = 5
    print("Initial A:", linefit.A, "value:", linefit.A.value)
    print("Initial B:", linefit.B, "value:", linefit.B.value)

    # Evaluate model with initial parameters
    print("linefit.evaluate() =", linefit.evaluate())
    print("linefit.residual() =", linefit.residual())

    plot(xobs, yobs, "x", linedata.x, linefit.evaluate(), "-")
    title("Line simulated at A=3, B=5")
    plt.show()

    # ----------------------------------------------------------------------
    # Create a FitRecipe to manage fitting
    # ----------------------------------------------------------------------
    rec = FitRecipe()
    rec.clearFitHooks()
    rec.addContribution(linefit)
    rec.show()

    # Add variables to be refined
    rec.addVar(rec.linefit.A)
    rec.addVar(rec.linefit.B)

    print("rec.A =", rec.A)
    print("rec.A.value =", rec.A.value)
    print("rec.values =", rec.values)
    print("rec.names =", rec.names)
    print("rec.residual() =", rec.residual())
    print("rec.residual([2, 4]) =", rec.residual([2, 4]))

    # ----------------------------------------------------------------------
    # Fit using least squares optimizer
    # ----------------------------------------------------------------------
    leastsq(rec.residual, rec.values)
    print("After leastsq:", rec.names, "-->", rec.values)
    linefit.show()

    plot(linedata.x, linedata.y, "x", linedata.x, linedata.ycalc, "-")
    title("Line fit using leastsq optimizer")
    plt.show()

    # ----------------------------------------------------------------------
    # Fit using scalar optimizer (fmin)
    # ----------------------------------------------------------------------
    fmin(rec.scalarResidual, [1, 1])
    print("After fmin:", rec.names, "-->", rec.values)

    plot(linedata.x, linedata.y, "x", linedata.x, linedata.ycalc, "-")
    title("Line fit using fmin optimizer")
    plt.show()

    # Display fit results
    res = FitResults(rec)
    print(res)

    # ----------------------------------------------------------------------
    # Example: Fixing a parameter
    # ----------------------------------------------------------------------
    rec.fix(B=0)
    print("Free:", rec.names, "-->", rec.values)
    print("Fixed:", rec.fixednames, "-->", rec.fixedvalues)

    leastsq(rec.residual, rec.values)
    print("Fit with B fixed to 0:", FitResults(rec))

    plot(linedata.x, linedata.y, "x", linedata.x, linedata.ycalc, "-")
    title("Line fit with B fixed at 0")
    plt.show()

    rec.free("all")

    # ----------------------------------------------------------------------
    # Example: Adding a constraint (A = 2*B)
    # ----------------------------------------------------------------------
    rec.constrain(rec.A, "2 * B")
    leastsq(rec.residual, rec.values)
    print("Fit with A constrained to 2*B:", FitResults(rec))

    plot(linedata.x, linedata.y, "x", linedata.x, linedata.ycalc, "-")
    title("Line fit with constraint A=2*B")
    plt.show()

    rec.unconstrain(rec.A)

    # ----------------------------------------------------------------------
    # Example: Adding a restraint (A close to <= 0.2 with penalty)
    # ----------------------------------------------------------------------
    rec.restrain(rec.A, ub=0.2, sig=0.001)
    leastsq(rec.residual, rec.values)
    print("Fit with A restrained to ub=0.2:", FitResults(rec))

    plot(linedata.x, linedata.y, "x", linedata.x, linedata.ycalc, "-")
    title("Line fit with restraint on A (ub=0.2)")
    plt.show()


if __name__ == "__main__":
    main()
