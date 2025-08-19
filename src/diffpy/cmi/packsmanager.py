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

from pathlib import Path
from typing import List, Union

from diffpy.cmi import get_package_dir
from diffpy.cmi.installer import (
    ParsedReq,
    install_requirements,
    parse_requirement_line,
    presence_check,
)
from diffpy.cmi.log import plog

__all__ = ["PacksManager"]


def _installed_packs_dir() -> Path:
    """Locate requirements/packs/ for the installed package."""
    with get_package_dir() as pkgdir:
        pkg = Path(pkgdir).resolve()
        for c in (
            pkg / "requirements" / "packs",
            pkg.parents[2] / "requirements" / "packs",
        ):
            if c.is_dir():
                return c
    raise FileNotFoundError(
        "Could not locate requirements/packs. Check your installation."
    )


class PacksManager:
    """Discovery, parsing, and installation for pack files.

    Attributes
    ----------
    packs_dir : pathlib.Path
        Absolute path to the installed packs directory.
        Defaults to `requirements/packs` under the installed package.
    """

    def __init__(self) -> None:
        self.packs_dir = _installed_packs_dir()

    def available_packs(self) -> List[str]:
        """List all available packs.

        Returns
        -------
        list of str
            Pack basenames available under :attr:`packs_dir`.
        """
        return sorted(
            p.stem for p in self.packs_dir.glob("*.txt") if p.is_file()
        )

    def _resolve_pack_file(self, identifier: Union[str, Path]) -> Path:
        """Resolve a pack identifier to an absolute .txt path.

        Rules
        -----
        1) Absolute path to a ``.txt`` file is NOT accepted.
        2) The identifier is treated as a basename that must exist
           under :attr:`packs_dir`.

        Parameters
        ----------
        identifier : str or path-like
            Basename to resolve.

        Returns
        -------
        pathlib.Path
            Absolute path to the pack file.

        Raises
        ------
        FileNotFoundError
            If the pack cannot be found per the above rules.
        """
        p = Path(identifier)
        if p.is_absolute():
            raise FileNotFoundError(
                f"Absolute pack paths are not supported: {p}.\
                Use a provided pack or \
                define extra requirements using a profile."
            )
        cand = self.packs_dir / f"{p.name}.txt"
        if cand.is_file():
            return cand.resolve()
        raise FileNotFoundError(f"Pack not found: {identifier} ({cand})")

    def pack_requirements(
        self, identifier: Union[str, Path]
    ) -> List[ParsedReq]:
        """Return parsed requirements for a pack.

        Parameters
        ----------
        identifier : str or path-like
            Installed pack name.

        Returns
        -------
        list of ParsedReq
            Parsed requirements from the pack file.
        """
        path = self._resolve_pack_file(identifier)
        lines: List[str] = []
        for ln in path.read_text(encoding="utf-8").splitlines():
            s = ln.strip()
            if s and not s.startswith("#"):
                lines.append(s)
        return [parse_requirement_line(s) for s in lines]

    def check_pack(self, identifier: Union[str, Path]) -> bool:
        """Return whether a pack is installed.

        Parameters
        ----------
        identifier : str or path-like
            Basename to the pack file.

        Returns
        -------
        bool
            ``True`` if the pack is installed, ``False`` otherwise.
        """
        reqs = self.pack_requirements(identifier)
        return presence_check(reqs)[0]

    def install_pack(self, identifier: str | Path) -> None:
        """Install a pack and verify presence.

        Parameters
        ----------
        identifier : str
            Basename to the pack file.
        """
        path = self._resolve_pack_file(identifier)
        reqs = self.pack_requirements(path.stem)
        scripts_root = self.packs_dir / "scripts"
        plog.info("Installing pack: %s", path.stem)
        if install_requirements(reqs, scripts_root=scripts_root) == 0:
            plog.info("Pack '%s' installation complete.", path.stem)
        else:
            plog.error("Pack '%s' installation failed.", path.stem)
