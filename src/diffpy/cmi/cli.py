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
from shutil import copytree
from typing import List, Optional, Tuple

from diffpy.cmi import __version__, get_package_dir
from diffpy.cmi.conda import env_info
from diffpy.cmi.log import plog, set_log_mode
from diffpy.cmi.packsmanager import PacksManager
from diffpy.cmi.profilesmanager import ProfilesManager


# Examples
def _installed_examples_dir() -> Path:
    """Return the absolute path to the installed examples directory.

    Returns
    -------
    pathlib.Path
        Directory containing shipped examples.

    Raises
    ------
    FileNotFoundError
        If the examples directory cannot be located in the installation.
    """
    with get_package_dir() as pkgdir:
        pkg = Path(pkgdir).resolve()
        for c in (
            pkg / "docs" / "examples",
            pkg.parents[2] / "docs" / "examples",
        ):
            if c.is_dir():
                return c
    raise FileNotFoundError(
        "Could not locate requirements/packs. Check your installation."
    )


def list_examples() -> List[str]:
    """List installed example names.

    Returns
    -------
    list of str
        Installed example directory names.
    """
    root = _installed_examples_dir()
    if not root.exists():
        return []
    return sorted([p.name for p in root.iterdir() if p.is_dir()])


def copy_example(example: str) -> Path:
    """Copy an example into the current working directory.

    Parameters
    ----------
    example : str
        Example directory name under the installed examples root.

    Returns
    -------
    pathlib.Path
        Destination path created under the current working directory.

    Raises
    ------
    FileNotFoundError
        If the example directory does not exist.
    FileExistsError
        If the destination directory already exists.
    """
    src = _installed_examples_dir() / example
    if not src.exists() or not src.is_dir():
        raise FileNotFoundError(f"Example not found: {example}")
    dest = Path.cwd() / example
    if dest.exists():
        raise FileExistsError(f"Destination {dest} already exists")
    copytree(src, dest)
    return dest


# Manual
def open_manual_and_exit() -> None:
    """Open the installed manual or fall back to the online version,
    then exit.

    Notes
    -----
    This function terminates the process with ``SystemExit(0)``.
    """
    import webbrowser

    v = __version__.split(".post")[0]
    webdocbase = "https://www.diffpy.org/doc/cmi/" + v
    with get_package_dir() as packagedir:
        localpath = Path(packagedir) / "docs" / "build" / "html" / "index.html"
    url = (
        localpath.resolve().as_uri()
        if localpath.is_file()
        else f"{webdocbase}/index.html"
    )
    if not localpath.is_file():
        plog.info("Manual files not found, falling back to online version.")
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
            "Welcome to diffpy-CMI, a complex modeling infrastructure "
            "for multi-modal analysis of scientific data.\n\n"
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging."
    )
    p.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    p.add_argument(
        "--manual", action="store_true", help="Open manual and exit."
    )
    p.set_defaults(_parser=p)

    sub = p.add_subparsers(dest="cmd", metavar="<command>")

    # example
    p_example = sub.add_parser("example", help="List or copy an example")
    p_example.set_defaults(_parser=p_example)
    sub_ex = p_example.add_subparsers(
        dest="example_cmd", metavar="<example|list>"
    )
    sub_ex.add_parser("list", help="List examples").set_defaults(
        _parser=p_example
    )
    p_example_copy = sub_ex.add_parser("copy", help="Copy an example to CWD")
    p_example_copy.add_argument("name", metavar="EXAMPLE", help="Example name")
    p_example_copy.set_defaults(_parser=p_example)
    p_example.set_defaults(example_cmd=None)

    # pack
    p_pack = sub.add_parser("pack", help="List packs or show a pack file")
    p_pack.set_defaults(_parser=p_pack)
    sub_pack = p_pack.add_subparsers(dest="pack_cmd", metavar="<name|list>")
    sub_pack.add_parser(
        "list", help="List packs (Installed vs Available)"
    ).set_defaults(_parser=p_pack)
    p_pack_show = sub_pack.add_parser(
        "show", help="Show a pack (by base name)"
    )
    p_pack_show.add_argument("name", metavar="PACK", help="Pack base name")
    p_pack_show.set_defaults(_parser=p_pack)
    p_pack.set_defaults(pack_cmd=None)

    # profile
    p_prof = sub.add_parser(
        "profile", help="List profiles or show a profile file"
    )
    p_prof.set_defaults(_parser=p_prof)
    sub_prof = p_prof.add_subparsers(dest="profile_cmd", metavar="<name|list>")
    sub_prof.add_parser(
        "list", help="List profiles (Installed vs Available)"
    ).set_defaults(_parser=p_prof)
    p_prof_show = sub_prof.add_parser(
        "show", help="Show a profile (by base name)"
    )
    p_prof_show.add_argument(
        "name", metavar="PROFILE", help="Profile base name"
    )
    p_prof_show.set_defaults(_parser=p_prof)
    p_prof.set_defaults(profile_cmd=None)

    # install (multiple targets)
    p_install = sub.add_parser("install", help="Install packs/profiles")
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
    p_install.set_defaults(_parser=p_install)

    # env
    sub.add_parser("env", help="Show basic conda environment info")

    return p


# Helpers
def _installed_pack_path(mgr: PacksManager, name: str) -> Path:
    """Return the absolute path to an installed pack file.

    Parameters
    ----------
    mgr : PacksManager
        Packs manager instance.
    name : str
        Pack basename (without ``.txt``).

    Returns
    -------
    pathlib.Path
        Absolute path to the pack file.

    Raises
    ------
    FileNotFoundError
        If the pack cannot be found.
    """
    path = mgr.packs_dir / f"{name}.txt"
    if not path.is_file():
        raise FileNotFoundError(f"Pack not found: {name} ({path})")
    return path


def _installed_profile_path(name: str) -> Path:
    """Return the absolute path to an installed profile file by
    basename.

    Parameters
    ----------
    name : str
        Profile basename (without extension).

    Returns
    -------
    pathlib.Path
        Absolute path to the profile file.

    Raises
    ------
    FileNotFoundError
        If the profile cannot be found under the installed profiles directory.
    """
    base = ProfilesManager().profiles_dir
    for cand in (base / f"{name}.yml", base / f"{name}.yaml"):
        if cand.is_file():
            return cand
    raise FileNotFoundError(f"Profile not found: {name} (under {base})")


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


def _cmd_example(ns: argparse.Namespace) -> int:
    """Handle `cmi example` subcommands.

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed arguments for the example subparser.

    Returns
    -------
    int
        Exit code (``0`` on success; non-zero on failure).
    """
    if ns.example_cmd in (None, "copy"):
        name = getattr(ns, "name", None)
        if not name:
            plog.error(
                "Missing example name. Use `cmi example list` to see options."
            )
            ns._parser.print_help()
            return 1
        out = copy_example(name)
        print(f"Example copied to: {out}")
        return 0
    if ns.example_cmd == "list":
        for g in list_examples():
            print(g)
        return 0

    plog.error("Unknown example subcommand.")
    ns._parser.print_help()
    return 2


def _cmd_pack(ns: argparse.Namespace) -> int:
    """Handle `cmi pack` subcommands.

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed arguments for the pack subparser.

    Returns
    -------
    int
        Exit code (``0`` on success; non-zero on failure).
    """
    mgr = PacksManager()
    if ns.pack_cmd == "list":
        names = mgr.available_packs()
        installed, available = [], []
        for nm in names:
            (installed if mgr.check_pack(nm) else available).append(nm)

        def dump(title: str, arr: List[str]) -> None:
            print(title + ":")
            if not arr:
                print("  (none)")
            else:
                for n in arr:
                    print(f"  - {n}")

        dump("Installed", installed)
        dump("Available to install", available)
        return 0

    name = getattr(ns, "name", None) or getattr(ns, "pack_cmd", None)
    if not name or name == "show":
        plog.error("Usage: cmi pack <name>  (or: cmi pack show <name>)")
        ns._parser.print_help()
        return 1

    path = _installed_pack_path(mgr, name)
    print(f"# pack: {name}\n# path: {path}\n")
    print(path.read_text(encoding="utf-8"))
    return 0


def _cmd_profile(ns: argparse.Namespace) -> int:
    """Handle `cmi profile` subcommands.

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed arguments for the profile subparser.

    Returns
    -------
    int
        Exit code (``0`` on success; non-zero on failure).
    """
    if ns.profile_cmd == "list":
        pm = ProfilesManager()
        names = pm.list_profiles()
        installed, available = [], []
        for nm in names:
            (installed if pm.check_profile(nm) else available).append(nm)

        def dump(title: str, arr: List[str]) -> None:
            print(title + ":")
            if not arr:
                print("  (none)")
            else:
                for n in arr:
                    print(f"  - {n}")

        dump("Installed", installed)
        dump("Available to install", available)
        return 0

    name = getattr(ns, "name", None) or getattr(ns, "profile_cmd", None)
    if not name or name == "show":
        plog.error("Usage: cmi profile <name>  (or: cmi profile show <name>)")
        ns._parser.print_help()
        return 1

    path = _installed_profile_path(name)
    print(f"# profile: {name}\n# path: {path}\n")
    print(path.read_text(encoding="utf-8"))
    return 0


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

    if ns.cmd == "example":
        return _cmd_example(ns)
    if ns.cmd == "pack":
        return _cmd_pack(ns)
    if ns.cmd == "profile":
        return _cmd_profile(ns)
    if ns.cmd == "install":
        return _cmd_install(ns)
    if ns.cmd == "env":
        return _cmd_env(ns)

    plog.error("Unknown command: %s", ns.cmd)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
