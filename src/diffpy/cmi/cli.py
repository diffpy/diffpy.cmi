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

import argparse
from pathlib import Path
from typing import List, Optional, Tuple

from diffpy.cmi import __version__
from diffpy.cmi.conda import env_info
from diffpy.cmi.log import plog, set_log_mode
from diffpy.cmi.packsmanager import PacksManager
from diffpy.cmi.profilesmanager import ProfilesManager


# Manual
def open_manual_and_exit() -> None:
    """Open the manual in a web browser and exit.

    Notes
    -----
    This function terminates the process with ``SystemExit(0)``.
    """
    import webbrowser

    url = "https://diffpy.org/diffpy.cmi"
    plog.info("Opening manual at %s", url)
    webbrowser.open(url)
    raise SystemExit(0)


# Parser
def _build_parser() -> argparse.ArgumentParser:
    """Build and return the top-level argument parser for the CLI.

    Returns
    -------
    argparse.ArgumentParser
        Configured parser with all subcommands and options.
    """
    p = argparse.ArgumentParser(
        prog="cmi",
        description=(
            """\
Welcome to diffpy.cmi, a complex modeling infrastructure for
multi-modal analysis of scientific data.

Diffpy.cmi is designed as an extensible complex modeling
infrastructure. Users and developers can readily integrate
novel data types and constraints into custom workflows. While
widely used for advanced analysis of structural data, the
framework is general and can be applied to any problem where
model parameters are refined to fit calculated quantities to
data.

Diffpy.cmi is comprised of modular units called 'packs' and
'profiles' that facilitate tailored installations for specific
scientific applications. Run 'cmi info -h' for more details.
"""
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging."
    )
    p.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"diffpy.cmi {__version__}",
    )
    p.add_argument(
        "--manual",
        action="store_true",
        help="Open online documentation and exit.",
    )
    p.set_defaults()
    sub = p.add_subparsers(dest="cmd", metavar="<command>")
    # example
    p_info = sub.add_parser(
        "info",
        help=("Prints info about packs, profiles, and examples.\n "),
        description=(
            """
Definitions:
pack:       A collection of data processing routines, models, and examples.
            For example, the 'pdf' pack contains packages used for modeling
            and refinement of the Atomic Pair Distribution Function (PDF).

profile:    A set of pre-defined packs or configurations for a specific
            scientific workflow. Profiles can be installed or customized
            for different use cases.

examples:   Example scripts or folders that can be copied locally using
            'cmi copy <example_name>'.
    """
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_info.set_defaults()
    sub_info = p_info.add_subparsers(dest="info_cmd", metavar="<command>")
    sub_info.add_parser(
        "packs", help="Show available and installed packs."
    ).set_defaults()
    sub_info.add_parser(
        "profiles", help="Show available and installed profiles."
    ).set_defaults()
    sub_info.add_parser(
        "examples", help="Show available examples to copy."
    ).set_defaults()
    # install (multiple targets)
    p_install = sub.add_parser("install", help="Install packs/profiles.")
    p_install.add_argument(
        "targets",
        nargs="*",
        help="One or more targets: pack/profile base names \
              or absolute profile file/dir.",
    )
    p_install.add_argument(
        "-c",
        "--channel",
        dest="default_channel",
        default="conda-forge",
        help="Default conda channel for packages \
            without explicit per-line channel.",
    )
    p_install.set_defaults()

    p_copy = sub.add_parser(
        "copy",
        help="Copy example directories.",
        description="Copy example directories to the current "
        "or specified location.",
        usage="cmi copy [-h] [-t DIR] [-f] <commands>...",
    )
    p_copy.add_argument(
        "name",
        nargs="+",
        help="Example name(s) to copy. Use `cmi info examples` to list.",
    )
    p_copy.add_argument(
        "-t",
        "--target-dir",
        dest="target_dir",
        metavar="DIR",
        help="Target directory to copy examples into. "
        "Defaults to current working directory.",
    )
    p_copy.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force overwrite existing files and merge directories.",
    )
    p_copy.set_defaults(func=_cmd_copy)
    # env
    sub.add_parser("env", help="Show basic conda environment info")
    return p


def _resolve_target_for_install(s: str) -> Tuple[str, Path]:
    """Return ('pack'|'profile', absolute path) for a single install
    target.

    Delegates resolution to manager resolvers to keep rules centralized:
    :meth:`PacksManager._resolve_pack_file` and
    :meth:`ProfilesManager._resolve_profile_file`.
    """
    mgr = PacksManager()
    pm = ProfilesManager()
    p = Path(s)

    if p.is_absolute():
        return "profile", pm._resolve_profile_file(p)

    pack_path = None
    profile_path = None
    try:
        pack_path = mgr._resolve_pack_file(s)
    except FileNotFoundError:
        pass
    try:
        profile_path = pm._resolve_profile_file(s)
    except FileNotFoundError:
        pass

    if pack_path and profile_path:
        raise ValueError(
            f"Ambiguous install target '{s}': both a pack and a profile exist."
        )
    if pack_path:
        return "pack", pack_path
    if profile_path:
        return "profile", profile_path
    raise FileNotFoundError(f"No installed pack or profile named '{s}' found.")


def _cmd_install(ns: argparse.Namespace) -> int:
    """Handle `cmi install` subcommand for packs and profiles.

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed arguments for the install subparser.

    Returns
    -------
    int
        Exit code (``0`` on success; non-zero on failure).
    """
    if not getattr(ns, "targets", None):
        plog.error(
            "Missing install targets. "
            "Provide pack/profile names or an absolute profile path."
        )
        ns._parser.print_help()
        return 1
    rc = 0
    mgr = PacksManager()
    pm = ProfilesManager()
    for tgt in ns.targets:
        try:
            kind, path = _resolve_target_for_install(tgt)
            if kind == "pack":
                r = mgr.install_pack(path.stem)
            else:
                r = pm.install(path if path.is_absolute() else path.stem)
            if isinstance(r, bool):
                if not r:
                    rc = max(rc, 1)
            elif isinstance(r, int):
                rc = max(rc, r)
        except (ValueError, FileNotFoundError) as e:
            plog.error("%s", e)
            ns._parser.print_help()
            rc = max(rc, 1)
        except Exception as e:
            plog.error("%s", e)
            rc = max(rc, 1)
    return rc


def _cmd_env(_: argparse.Namespace) -> int:
    """Print basic conda environment information.

    Parameters
    ----------
    _ : argparse.Namespace
        Unused parsed arguments placeholder.

    Returns
    -------
    int
        Always ``0``.
    """
    info = env_info()
    print("Conda environment:")
    print(f"  available : {info.available}")
    print(f"  mamba     : {info.mamba}")
    print(f"  env_name  : {info.env_name or '(unknown)'}")
    print(f"  prefix    : {info.prefix or '(unknown)'}")
    return 0


def _cmd_info(ns: argparse.Namespace) -> int:
    """Handle `cmi info` subcommands.

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed arguments for the info subparser.

    Returns
    -------
    int
        Exit code (``0`` on success; non-zero on failure).
    """
    packsmanager = PacksManager()
    profilemanager = ProfilesManager()
    if ns.info_cmd is None:
        packsmanager.print_info()
        print("\nINFO: Run `cmi info -h` for more options.")
        return 0
    if ns.info_cmd == "packs":
        packsmanager.print_packs()
        return 0
    if ns.info_cmd == "profiles":
        profilemanager.print_profiles()
        return 0
    if ns.info_cmd == "examples":
        packsmanager.print_examples()
        return 0
    ns._parser.print_help()
    return 2


def _cmd_copy(ns: argparse.Namespace) -> int:
    """Handle `cmi copy` subcommand for copying example directories.

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed arguments for the copy subparser.

    Returns
    -------
    int
        Exit code (``0`` on success; non-zero on failure).
    """
    names = getattr(ns, "name", None)
    target_dir = getattr(ns, "target_dir", None)
    force = getattr(ns, "force", False)

    if not names:
        plog.error(
            "Missing example name(s). Use `cmi info examples` to see options."
        )
        ns._parser.print_help()
        return 1

    try:
        pkm = PacksManager()
        pkm.copy_examples(names, target_dir=target_dir, force=force)
        return 0
    except FileNotFoundError as e:
        plog.error("%s", e)
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    """Run the CMI CLI.

    Parameters
    ----------
    argv : list of str, optional
        Argument vector to parse. When ``None``, defaults to ``sys.argv[1:]``.

    Returns
    -------
    int
        Process exit code (``0`` success, ``1`` failure, ``2`` usage error).
    """
    parser = _build_parser()
    ns = parser.parse_args(argv)
    set_log_mode(ns.verbose)
    if ns.manual:
        open_manual_and_exit()
    if ns.cmd is None:
        parser.print_help()
        return 2
    if ns.cmd == "info":
        return _cmd_info(ns)
    if ns.cmd == "copy":
        return _cmd_copy(ns)
    if ns.cmd == "install":
        return _cmd_install(ns)
    if ns.cmd == "env":
        return _cmd_env(ns)
    plog.error("Unknown command: %s", ns.cmd)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
