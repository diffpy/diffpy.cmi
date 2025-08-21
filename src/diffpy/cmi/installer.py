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

import importlib.metadata as md
import os
import shlex
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from packaging.requirements import InvalidRequirement
from packaging.requirements import Requirement as PkgRequirement

from diffpy.cmi import conda
from diffpy.cmi.log import plog

__all__ = [
    "ParsedReq",
    "parse_requirement_line",
    "presence_check",
    "install_requirements",
]


# Types and parsing
@dataclass
class ParsedReq:
    """Parsed representation of a single requirement line.

    A requirement line may declare a package or a script. Script lines set
    :attr:`name` to the basename (stem) of the script so presence checking can
    treat them like packages when appropriate.

    Parameters
    ----------
    raw : str
        Original, unmodified line (kept verbatim).
    kind : {"script", "pkg", "skip"}
        Classification of the line.
    name : str or None, optional
        Package name (for ``pkg``) or script basename (for ``script``).
    spec : str or None, optional
        Version specifier (e.g., ``">=1.2"``) for packages.
    channel : str or None, optional
        Optional channel (from ``channel::spec``) for packages.
    """

    raw: str
    kind: str
    name: Optional[str] = None
    spec: Optional[str] = None
    channel: Optional[str] = None


def parse_requirement_line(line: str) -> ParsedReq:
    """Parse a single requirement definition.

    Supported forms
    ---------------
    - **Scripts:** a line whose first token ends with ``.sh`` or ``.bat``.
      The script's basename becomes :attr:`ParsedReq.name`.
    - **Packages:** an optional ``channel::`` prefix followed by a valid
      PEP 508 requirement string (e.g., ``"numpy>=1.24"``).

    Parameters
    ----------
    line : str
        Raw line from a requirements file.

    Returns
    -------
    ParsedReq
        Structured representation of the requirement.
    """
    s = (line or "").strip()
    if not s or s.startswith("#"):
        return ParsedReq(raw=line, kind="skip")

    # Script?
    try:
        first = shlex.split(s, posix=(os.name != "nt"))[0]
    except Exception:
        first = s.split()[0] if s.split() else s
    if first.lower().endswith((".sh", ".bat")):
        return ParsedReq(raw=line, kind="script", name=Path(first).stem)

    # Package
    chan = None
    body = s
    if "::" in s:
        c, rest = s.split("::", 1)
        if c and all(ch not in c for ch in " <>="):
            chan, body = c, rest
    try:
        req = PkgRequirement(body)
        name = req.name
        spec = str(req.specifier) or None
        return ParsedReq(
            raw=line, kind="pkg", name=name, spec=spec, channel=chan
        )
    except InvalidRequirement:
        plog.info("Skipping invalid requirement line: %s", line.rstrip())
        return ParsedReq(raw=line, kind="skip")


def _is_installed(name: str) -> bool:
    """Return whether a package is importable or listed by conda.

    The check first tries Python package metadata and then falls back to
    the names reported by ``conda list --json``.

    Parameters
    ----------
    name : str
        Distribution/package name to check.

    Returns
    -------
    bool
        ``True`` if present, ``False`` otherwise.
    """
    try:
        md.version(name)
        return True
    except md.PackageNotFoundError:
        pass
    except Exception as e:
        plog.debug("Package %s not found in Python metadata: %s", name, e)
    return name.lower() in {n.lower() for n in conda.list_installed_names()}


def presence_check(
    reqs: List[ParsedReq], *, check_meta: Optional[bool] = True
) -> Tuple[bool, List[str]]:
    """Check whether requirements appear satisfied.

    Semantics
    ---------
    - **Packages:** mark missing when :func:`_is_installed` is ``False``.
    - **Scripts:** use the basename as a pseudo-package name.
      * If the basename starts with ``"_"`` (meta-scripts), count them as
        missing only when ``check_meta=True`` (profile checks). During
        post-install verification ``check_meta=False`` so meta-scripts
        are ignored (script exit code already enforced).
      * Otherwise, treat like a package and require the basename to be present.

    Parameters
    ----------
    reqs : list of ParsedReq
        Parsed requirements to check.
    check_meta : bool, optional
        Whether meta-scripts should be considered missing.
        Defaults to ``True``.

    Returns
    -------
    tuple of (bool, list of str)
        ``(ok, missing)`` where ``ok`` is ``True`` when all checks pass and
        ``missing`` lists raw lines deemed missing.
    """
    missing: List[str] = []
    for r in reqs:
        if r.kind == "skip" or not r.name:
            continue
        elif r.kind == "script" and r.name[0] == "_":
            if check_meta:
                missing.append(r.raw.strip())
            continue
        elif not _is_installed(r.name):
            missing.append(r.raw.strip())
    return (len(missing) == 0), missing


def _script_supported_on_platform(ext: str) -> bool:
    """Return whether scripts with the given extension are runnable
    here.

    Parameters
    ----------
    ext : str
        File extension including the leading dot (e.g., ``".sh"``).

    Returns
    -------
    bool
        ``True`` if runnable on the current platform, ``False`` otherwise.
    """
    ext = (ext or "").lower()
    if os.name == "nt":
        return ext == ".bat"
    return ext == ".sh"


def _resolve_script_path(first_token: str, scripts_root: Path) -> Path:
    """Resolve a script path under the configured scripts directory.

    Rules
    -----
    1) If ``first_token`` is an **absolute file path**, accept as-is.
    2) Otherwise treat it as a relative file under ``scripts_root``.

    Parameters
    ----------
    first_token : str
        First token from the script line (ends with ``.sh`` or ``.bat``).
    scripts_root : path-like
        Root directory containing available scripts.

    Returns
    -------
    pathlib.Path
        Absolute resolved path to the script.

    Raises
    ------
    FileNotFoundError
        If the path cannot be resolved by the above rules.
    """
    p = Path(first_token)
    if p.is_absolute():
        if p.is_file():
            return p.resolve()
        raise FileNotFoundError(f"Script not found: {p}")
    cand = scripts_root / first_token
    if cand.is_file():
        return cand.resolve()
    raise FileNotFoundError(
        f"Script not found: {first_token}"
        f" (expected under {scripts_root} or absolute file path)"
    )


def _script_exec_cmd(path: Path, args: List[str]) -> List[str]:
    """Return the execution command for a script on this platform.

    Parameters
    ----------
    path : path-like
        Script path.
    args : list of str
        Arguments to pass to the script.

    Returns
    -------
    list of str
        Command vector to execute via :func:`conda.run`.
    """
    ext = path.suffix.lower()
    if os.name == "nt":
        if ext != ".bat":
            return [str(path)] + args
        return ["cmd", "/c", str(path)] + args
    if ext == ".sh":
        shell = shutil.which("bash") or shutil.which("sh") or "sh"
        return [shell, str(path)] + args
    return [str(path)] + args


# Install policy


def install_requirements(
    reqs: List[ParsedReq],
    *,
    scripts_root: Path,
    default_channel: str = "conda-forge",
) -> int:
    """Install requirements, run scripts, and verify presence.

    Policy
    ------
    1) **Packages first**: batch per channel; solver failures are treated as
       soft (final presence check decides).
    2) **Scripts next**: run native scripts only; a non-zero exit is a hard
       failure.
    3) **Presence check**: verify packages and non-meta scripts.

    Parameters
    ----------
    reqs : list of ParsedReq
        Parsed requirements (from packs and profile extras).
    scripts_root : path-like
        Directory containing relative scripts used by recipes.
    default_channel : str, optional
        Default conda channel for batches. Defaults to ``"conda-forge"``.

    Returns
    -------
    int
        ``0`` on success, ``1`` on failure.
    """
    # Batch packages by channel
    by_channel: Dict[str, List[str]] = {}
    for r in reqs:
        if r.kind != "pkg" or not r.name:
            continue
        if _is_installed(r.name):
            continue
        chan = r.channel or default_channel
        spec = f"{r.name}{r.spec or ''}"
        lst = by_channel.setdefault(chan, [])
        if spec not in lst:
            lst.append(spec)

    for chan, specs in by_channel.items():
        solver, rc, _ = conda.install_specs(
            specs, channel=chan, default_channel=default_channel
        )
        if rc != 0:
            plog.info(
                "Batch install did not complete cleanly with %s "
                "for channel '%s'. "
                "Run in debug mode (-v) to see solver output.",
                solver,
                chan,
            )
    conda.reset_cache()

    # Execute scripts
    for r in reqs:
        if r.kind != "script" or not r.name:
            continue
        if not r.name.startswith("_") and _is_installed(r.name):
            plog.info("Skipping script (already satisfied): %s", r.raw.strip())
            continue
        first_token = shlex.split(r.raw.strip(), posix=(os.name != "nt"))[0]
        ext = Path(first_token).suffix.lower()
        if not _script_supported_on_platform(ext):
            plog.info(
                "Skipping non-native script on this platform: %s", first_token
            )
            continue

        path = _resolve_script_path(first_token, scripts_root)
        args = shlex.split(r.raw, posix=(os.name != "nt"))[1:]
        cmd = _script_exec_cmd(path, args)
        plog.info("Running script: %s", " ".join(cmd))
        rc, _ = conda.run(cmd, cwd=path.parent, capture=False)
        if rc != 0:
            plog.error("Script failed (exit %d): %s", rc, r.raw.strip())
            return 1
        conda.reset_cache()

    # Final presence check
    ok, missing = presence_check(reqs, check_meta=False)
    if not ok:
        plog.error(
            "Requirements not fully satisfied after install: %s",
            ", ".join(missing),
        )
        return 1

    plog.info("Requirements installation complete.")
    return 0
