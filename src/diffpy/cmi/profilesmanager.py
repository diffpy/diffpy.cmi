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

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

import yaml

from diffpy.cmi.installer import (
    ParsedReq,
    install_requirements,
    parse_requirement_line,
    presence_check,
)
from diffpy.cmi.log import plog
from diffpy.cmi.packsmanager import PacksManager, Styles, get_package_dir

__all__ = ["Profile", "ProfilesManager"]


def _installed_profiles_dir(root_path=None) -> Path:
    """Locate requirements/profiles/ for the installed package."""
    with get_package_dir(root_path) as pkgdir:
        pkg = Path(pkgdir).resolve()
        for c in (
            pkg / "requirements" / "profiles",
            pkg.parents[2] / "requirements" / "profiles",
        ):
            if c.is_dir():
                return c
    raise FileNotFoundError(
        "Could not locate requirements/profiles. Check your installation."
    )


@dataclass
class Profile:
    """Container for a resolved profile.

    Parameters
    ----------
    name : str
        Profile name (defaults to the YAML stem).
    packs : list of str
        Pack basenames this profile depends on.
    extras : list of str
        Extra requirement lines (scripts or packages).
    source : path-like
        Absolute path to the YAML file that defined the profile.

    Profile Format
    --------------
    All profile `.yaml` files must have the following structure::

        packs:
            - <pack_name>

        extras:
            - <additional_package_name>

    The file name is the profile identifier used for installing profiles.
    See `requirements/profiles/all.yml` for an example.
    """

    name: str
    packs: List[str]
    extras: List[str]
    source: Path


class ProfilesManager:
    """Discovery, loading, checking and installation for profiles.

    Attributes
    ----------
    packs_mgr : PacksManager, optional
        The packs manager used for discovery and installation policy.
    profiles_dir : pathlib.Path
        Absolute path to the installed profiles directory.
        Defaults to `requirements/profiles` under the installed package.
    """

    def __init__(
        self,
        packs_mgr: Optional[PacksManager] = None,
        root_path=None,
    ) -> None:

        self.packs_mgr = packs_mgr or PacksManager(root_path=root_path)
        self.profiles_dir = _installed_profiles_dir(root_path)

    # Resolution & loading
    def _resolve_profile_file(self, identifier: Union[str, Path]) -> Path:
        """Resolve a profile identifier to an absolute YAML path.

        Rules
        -----
        1) Absolute path to a ``.yml``/``.yaml`` file is accepted as-is.
        2) Otherwise treat ``identifier`` as a basename
            under :attr:`profiles_dir`.

        Parameters
        ----------
        identifier : str or path-like
            Basename or absolute file to resolve.

        Returns
        -------
        pathlib.Path
            Absolute path to the profile YAML.

        Raises
        ------
        FileNotFoundError
            If the profile cannot be found per the above rules.
        """
        p = Path(identifier)
        if p.is_absolute():
            if p.is_file() and p.suffix.lower() in {".yml", ".yaml"}:
                return p.resolve()
            raise FileNotFoundError(f"Profile file not found: {p}")

        cand_y = self.profiles_dir / f"{p}.yml"
        cand_ya = self.profiles_dir / f"{p}.yaml"
        for c in (cand_y, cand_ya):
            if c.is_file():
                return c.resolve()
        raise FileNotFoundError(
            f"No installed profile named '{identifier}' in {self.profiles_dir}"
        )

    def _profile_requirements(self, prof: Profile) -> List[ParsedReq]:
        """Return parsed requirements for a profile.

        Parameters
        ----------
        prof : Profile
            Loaded profile.

        Returns
        -------
        list of ParsedReq
            Combined pack requirements and extras
            with ``skip`` entries removed.
        """
        reqs: List[ParsedReq] = []
        for pack_name in prof.packs:
            reqs.extend(self.packs_mgr.pack_requirements(pack_name))
        reqs.extend(parse_requirement_line(x) for x in prof.extras)
        return [r for r in reqs if r.kind != "skip"]

    def load(self, identifier: Union[str, Path]) -> Profile:
        """Load a profile file into a :class:`Profile` object.

        Parameters
        ----------
        identifier : str or path-like
            Basename or absolute YAML path.

        Returns
        -------
        Profile
            Loaded profile with metadata.
        """
        path = self._resolve_profile_file(identifier)
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        packs = list(data.get("packs") or [])
        extras = list(data.get("extras") or [])
        name = data.get("name") or path.stem
        return Profile(name=name, packs=packs, extras=extras, source=path)

    def available_profiles(self) -> List[str]:
        """Return available installed profiles by basename.

        Returns
        -------
        list of str
            Profile basenames available under :attr:`profiles_dir`.
        """
        return sorted(
            p.stem for p in self.profiles_dir.glob("*.yml")
        ) + sorted(p.stem for p in self.profiles_dir.glob("*.yaml"))

    def check_profile(self, identifier: Union[str, Path]) -> bool:
        """Return whether a profile appears installed on this system.

        Parameters
        ----------
        identifier : str or path-like
            Basename or absolute YAML path.

        Returns
        -------
        bool
            ``True`` if all packages and non-meta scripts appear present.
        """
        prof = self.load(identifier)
        reqs = self._profile_requirements(prof)
        return presence_check(reqs)[0]

    def install(self, identifier: Union[str, Path]) -> None:
        """Install a profile and verify presence.

        Parameters
        ----------
        identifier : str or path-like
            Basename or absolute YAML path.
        """
        prof = self.load(identifier)
        reqs = self._profile_requirements(prof)
        scripts_root = self.packs_mgr.packs_dir / "scripts"

        plog.info("Installing profile: %s", prof.name)
        exit_code = install_requirements(reqs, scripts_root=scripts_root)
        if exit_code == 0:
            plog.info("Profile '%s' installation complete.", prof.name)
        else:
            plog.error("Profile '%s' installation failed.", prof.name)

        return exit_code

    def print_profiles(self) -> None:
        """Print available and installed profiles."""
        s = Styles()
        installed_profiles, uninstalled_profiles = [], []
        for profile_name in self.available_profiles():
            if self.check_profile(profile_name):
                installed_profiles.append(profile_name)
            else:
                uninstalled_profiles.append(profile_name)
        print(f"\n{s.BOLD}{s.UNDER}{s.MAGENTA}Installed Profiles:{s.RESET}")
        if not installed_profiles:
            print("  (none)")
        else:
            for profile in installed_profiles:
                print(f"  {profile}")
        print(f"\n{s.BOLD}{s.UNDER}{s.MAGENTA}Available Profiles:{s.RESET}")
        if not uninstalled_profiles:
            print("  (all profiles installed)")
        else:
            for profile in uninstalled_profiles:
                print(f"  {profile}")
