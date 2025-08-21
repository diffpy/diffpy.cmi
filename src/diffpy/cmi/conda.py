#!/usr/bin/env python
##############################################################################
#
# (c) 2025 The Trustees of Columbia University in the City of New York.
# All rights reserved.
#
# File coded by: Tieqiong Zhang and members of the Billinge Group.
#
# See GitHub contributions for a more detailed list of contributors.
# https://github.com/diffpy/diffpy.cmi/graphs/contributors
#
# See LICENSE.rst for license information.
#
##############################################################################

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from diffpy.cmi.log import is_debug, plog

__all__ = [
    "CondaEnvInfo",
    "env_info",
    "available",
    "mamba_available",
    "list_installed_names",
    "install_specs",
    "reset_cache",
    "run",
]

# Environment info


@dataclass
class CondaEnvInfo:
    """Snapshot of conda/mamba availability and the active environment.

    Parameters
    ----------
    available : bool
        Whether ``conda`` is available on ``PATH``.
    mamba : bool
        Whether ``mamba`` is available on ``PATH``.
    env_name : str or None
        Name of the active environment, if known.
    prefix : str or None
        Filesystem prefix of the active environment, if known.
    """

    available: bool
    mamba: bool
    env_name: Optional[str]
    prefix: Optional[str]


def run(
    cmd: Sequence[str],
    cwd: Optional[Path] = None,
    *,
    capture: Optional[bool] = None,
) -> Tuple[int, str]:
    """Run a subprocess with sensible, mode-dependent defaults.

    The function does **not** decide logging policy. It simply runs the
    command and returns the exit code and combined output. Visibility of
    the child output follows CMI's current log mode:

    - In **debug** mode: stream output live by default.
    - In **user** mode: capture output quietly by default.

    Parameters
    ----------
    cmd : sequence of str
        Command and arguments.
    cwd : path-like, optional
        Working directory for the child process.
    capture : bool or None, optional
        Override the default visibility. ``True`` forces capture; ``False``
        forces streaming; ``None`` selects the mode-dependent default.

    Returns
    -------
    tuple of (int, str)
        Exit code and captured output (empty string when streaming).

    Notes
    -----
    When capturing in debug mode, the output is also echoed so developers
    still see live progress.
    """
    dbg = is_debug()
    do_capture = (not dbg) if capture is None else bool(capture)
    qcmd = " ".join(str(x) for x in cmd)

    win = os.name == "nt"
    prog = str(cmd[0]).lower() if cmd else ""
    needs_cmd = win and (
        prog.endswith("\\conda.bat")
        or prog.endswith("\\mamba.bat")
        or prog in ("conda", "conda.bat", "mamba", "mamba.bat")
    )
    argv = (["cmd", "/c"] + list(cmd)) if needs_cmd else list(cmd)

    try:
        if do_capture:
            cp = subprocess.run(
                argv,
                cwd=str(cwd) if cwd else None,
                capture_output=True,
                text=True,
                check=False,
            )
            rc = cp.returncode
            out = (cp.stdout or "") + (cp.stderr or "")
            # In debug, also echo captured output so devs see it live
            if dbg:
                if cp.stdout:
                    sys.stdout.write(cp.stdout)
                if cp.stderr:
                    sys.stderr.write(cp.stderr)
                if cp.stdout or cp.stderr:
                    sys.stdout.flush()
                    sys.stderr.flush()
        else:
            cp = subprocess.run(
                argv,
                cwd=str(cwd) if cwd else None,
                text=True,
                check=False,
            )
            rc = cp.returncode
            out = ""
        if rc != 0:
            plog.debug("Command failed (%d): %s", rc, qcmd)
        return rc, out
    except FileNotFoundError as e:
        plog.debug("Command not found: %s (%s)", cmd[0], e)
        return 127, str(e)


def available() -> bool:
    """Return whether ``conda`` is available on PATH.

    Returns
    -------
    bool
        ``True`` if the ``conda`` executable can be invoked.
    """
    rc, _ = run(["conda", "--version"])
    return rc == 0


def mamba_available() -> bool:
    """Return whether ``mamba`` is available on PATH.

    Returns
    -------
    bool
        ``True`` if the ``mamba`` executable can be invoked.
    """
    rc, _ = run(["mamba", "--version"])
    return rc == 0


def env_info() -> CondaEnvInfo:
    """Return availability and active-environment metadata.

    Returns
    -------
    CondaEnvInfo
        Structured information assembled from ``conda info --json`` and
        availability probes.
    """
    rc, out = run(["conda", "info", "--json"], capture=True)
    if rc == 0:
        try:
            data = json.loads(out) if out else None
        except Exception as e:
            plog.debug("Failed to parse JSON: %s", e)
            data = None
    else:
        data = None
    env_name = None
    prefix = None
    if isinstance(data, dict):
        env_name = data.get("active_prefix_name")
        prefix = data.get("active_prefix") or data.get("default_prefix")
    return CondaEnvInfo(
        available=available(),
        mamba=mamba_available(),
        env_name=env_name,
        prefix=prefix,
    )


_installed_names_cache: Optional[set[str]] = None


def reset_cache() -> None:
    """Reset the internal cache of installed package names."""
    global _installed_names_cache
    _installed_names_cache = None


def list_installed_names() -> List[str]:
    """Return conda package names from ``conda list --json``.

    Results are cached for the current process to reduce repeated shell calls.

    Returns
    -------
    list of str
        Sorted unique package names.
    """
    global _installed_names_cache
    if _installed_names_cache is not None:
        return sorted(_installed_names_cache)

    rc, out = run(["conda", "list", "--json"], capture=True)
    names: set[str] = set()
    if rc == 0:
        try:
            arr = json.loads(out) or []
            for rec in arr:
                n = (rec or {}).get("name")
                if isinstance(n, str) and n:
                    names.add(n)
        except Exception as e:
            plog.debug("conda list JSON parse failed: %s", e)
    else:
        plog.debug("conda list returned rc=%d", rc)

    _installed_names_cache = names
    return sorted(names)


def _install_args(channel: Optional[str], default_channel: str) -> List[str]:
    """Return common install arguments for conda/mamba.

    Parameters
    ----------
    channel : str or None
        Target channel for the batch, or ``None`` to use ``default_channel``.
    default_channel : str
        Channel used when ``channel`` is ``None``.

    Returns
    -------
    list of str
        Flattened list of CLI arguments.
    """
    args: List[str] = ["-y"]
    ch = (channel or default_channel).strip()
    if ch:
        args += ["-c", ch]
    return args


def install_specs(
    specs: Sequence[str],
    *,
    channel: Optional[str] = None,
    default_channel: str = "conda-forge",
) -> Tuple[str, int, str]:
    """Install a batch of specs, preferring mamba then conda.

    Parameters
    ----------
    specs : sequence of str
        Conda spec strings (e.g., ``"numpy>=1.24"``).
    channel : str or None, optional
        Preferred channel for this batch.
    default_channel : str, optional
        Channel used when ``channel`` is not given.

    Returns
    -------
    tuple of (str, int, str)
        The solver used (``"mamba"`` or ``"conda"``), the exit code, and the
        captured output (empty when streaming).

    Notes
    -----
    This function logs at ``INFO`` level when each batch starts, warns when a
    mamba batch fails and a fallback is attempted, and leaves error decisions
    to higher-level callers.
    """
    specs = list(specs)
    if not specs:
        return "none", 0, ""

    # Try mamba first
    if mamba_available():
        cmd = (
            ["mamba", "install"]
            + _install_args(channel, default_channel)
            + specs
        )
        plog.info(
            "mamba batch (%s): %s", channel or default_channel, " ".join(specs)
        )
        rc, out = run(cmd)
        if rc == 0:
            reset_cache()
            return "mamba", 0, out
        plog.info(
            "mamba batch failed for channel %s", channel or default_channel
        )

    # Fallback to conda
    if available():
        cmd = (
            ["conda", "install"]
            + _install_args(channel, default_channel)
            + specs
        )
        plog.info(
            "conda batch (%s): %s", channel or default_channel, " ".join(specs)
        )
        rc, out = run(cmd)
        if rc == 0:
            reset_cache()
            return "conda", 0, out
        return "conda", rc, out

    return "unavailable", 1, "Neither mamba nor conda is available."
