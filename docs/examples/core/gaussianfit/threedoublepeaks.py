#!/usr/bin/env python3
"""Robust rewrite of the three-double-peaks example.

Fixes:
 - ensures profile.y/profile.dy are set
 - safe peakloc (clip arcsin argument)
 - avoid fragile sigma-from-grid-spacing
 - small stable delta() implementation
 - no accidental recipe.fix("mu")
"""

from pathlib import Path

import numpy as np

from diffpy.cmi.fit_tools import optimize_recipe, plot_results
from diffpy.srfit.fitbase import (
    FitContribution,
    FitRecipe,
    FitResults,
    Profile,
)


def make_recipe():
    """Make a FitRecipe for fitting three double-gaussian curves to
    data.

    Robust version with safe defaults for dy, safe peak location
    constraint, and stable delta/gaussian handling.
    """

    # Profile - load data and ensure y/dy are set
    profile = Profile()
    data = str(Path(__file__).parent / "threedoublepeaks.dat")

    # loadtxt returns (x, y, dy) if file contains 3 columns, else dy is None
    x, y, dy = profile.loadtxt(data)

    # simulate and set error values
    scale = np.max(np.abs(y))
    sigma = max(1e-8, 0.05 * scale)  # 5% relative default
    profile.dy = np.ones_like(y) * sigma

    # FitContribution
    contribution = FitContribution("peaks")
    contribution.setProfile(profile, xname="t")

    pi = np.pi
    exp = np.exp

    # define a gaussian function for peak shape
    def gaussian(t, mu, sig):
        sig = np.maximum(sig, 1e-12)
        return (
            1.0
            / np.sqrt(2.0 * pi * sig**2)
            * exp(-0.5 * ((t - mu) / sig) ** 2)
        )

    contribution.registerFunction(gaussian, name="peakshape")

    # define a delta function (small width gaussian) for peak position
    def delta(t, mu):
        # Use grid spacing if available but ensure non-zero
        spacing = np.mean(np.diff(t))
        eps = max(1e-6, spacing * 0.1)
        return gaussian(t, mu, eps)

    contribution.registerFunction(delta)

    # background string function: 6th degree polynomial
    bkgdstr = "b0 + b1*t + b2*t**2 + b3*t**3 + b4*t**4 + b5*t**5 + b6*t**6"
    contribution.registerStringFunction(bkgdstr, "bkgd")

    # Define equation: three double-peaks with fixed amplitude ratio 0.23
    contribution.setEquation(
        "A1 * ( convolve( delta(t, mu11), peakshape(t, c, sig11) ) "
        " + 0.23*convolve( delta(t, mu12), peakshape(t, c, sig12) ) ) + "
        "A2 * ( convolve( delta(t, mu21), peakshape(t, c, sig21) ) "
        " + 0.23*convolve( delta(t, mu22), peakshape(t, c, sig22) ) ) + "
        "A3 * ( convolve( delta(t, mu31), peakshape(t, c, sig31) ) "
        " + 0.23*convolve( delta(t, mu32), peakshape(t, c, sig32) ) ) + "
        "bkgd"
    )

    # set center c near middle of x
    contribution.c.value = x[len(x) // 2]

    # Build recipe
    recipe = FitRecipe()
    recipe.addContribution(contribution)

    # amplitudes
    recipe.addVar(contribution.A1, 100)
    recipe.addVar(contribution.A2, 100)
    recipe.addVar(contribution.A3, 100)

    # primary peak positions
    recipe.addVar(contribution.mu11, 13.0)
    recipe.addVar(contribution.mu21, 24.0)
    recipe.addVar(contribution.mu31, 33.0)

    # Safe peak location constraint using arcsin with clipping
    l1 = 1.012
    l2 = 1.0

    def peakloc(mu):
        """Compute secondary peak location from primary peak
        location."""
        # Convert to radians, compute, clip, convert back to degrees
        mu_rad = np.deg2rad(mu)
        arg = l2 * np.sin(mu_rad) / l1
        arg = np.clip(arg, -1.0, 1.0)
        out_rad = np.arcsin(arg)
        return np.rad2deg(out_rad)

    recipe.registerFunction(peakloc)
    recipe.constrain(contribution.mu12, "peakloc(mu11)")
    recipe.constrain(contribution.mu22, "peakloc(mu21)")
    recipe.constrain(contribution.mu32, "peakloc(mu31)")

    # Peak widths: use sig0 and dsig with a safer functional form (positive)
    recipe.newVar("sig0", 0.1)  # base width in same units as t
    recipe.newVar("dsig", 0.001)  # small quadratic broadening coefficient

    def sig(sig0, dsig, mu):
        """Compute sigma from base sig0, broadening dsig, and peak
        position mu."""
        # Use positive-definite formula: sig0 * (1 + dsig * mu**2)
        out = sig0 * (1.0 + dsig * mu**2)
        # enforce a minimum width
        return np.maximum(out, 1e-6)

    recipe.registerFunction(sig)
    # Constrain the component sigmas
    recipe.constrain(contribution.sig11, "sig(sig0, dsig, mu11)")
    recipe.constrain(
        contribution.sig12,
        "sig(sig0, dsig, mu12)",
        ns={"mu12": contribution.mu12},
    )
    recipe.constrain(contribution.sig21, "sig(sig0, dsig, mu21)")
    recipe.constrain(
        contribution.sig22,
        "sig(sig0, dsig, mu22)",
        ns={"mu22": contribution.mu22},
    )
    recipe.constrain(contribution.sig31, "sig(sig0, dsig, mu31)")
    recipe.constrain(
        contribution.sig32,
        "sig(sig0, dsig, mu32)",
        ns={"mu32": contribution.mu32},
    )

    # background variables
    for i in range(7):
        # addVar(param, startvalue, tag='bkgd') keeps them grouped for steering
        p = getattr(contribution, f"b{i}")
        recipe.addVar(p, 0.0, tag="bkgd")

    # Initialize sig0/dsig sensible values
    recipe.sig0.value = 0.1
    recipe.dsig.value = 0.001

    return recipe


def steerFit(recipe):
    """Simple steering sequence (similar to your original)."""
    # Start by fitting only background
    recipe.fix("all")
    recipe.free("bkgd")  # all background coeffs
    optimize_recipe(recipe)

    # then free everything except initial peak positions (if wanted)
    recipe.free("all")
    # if you prefer to hold initial peak positions for one step:
    recipe.fix("mu11", "mu21", "mu31")
    optimize_recipe(recipe)

    # finally free all and finish
    recipe.free("all")
    optimize_recipe(recipe)


if __name__ == "__main__":
    recipe = make_recipe()
    steerFit(recipe)
    res = FitResults(recipe)
    res.printResults()
    x = recipe.peaks.profile.x
    yobs = recipe.peaks.profile.y
    ycalc = recipe.peaks.profile.ycalc
    plot_results(x, yobs, ycalc, difference_offset=-700)
