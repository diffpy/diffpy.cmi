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
import shutil
from importlib.resources import as_file
from pathlib import Path
from typing import List, Union

from diffpy.cmi.installer import (
    ParsedReq,
    install_requirements,
    parse_requirement_line,
    presence_check,
)
from diffpy.cmi.log import plog

__all__ = ["PacksManager", "get_package_dir"]


class Styles:
    RESET = "\033[0m"
    # styles
    BOLD = "\033[1m"
    UNDER = "\033[4m"
    # colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"


def get_package_dir(root_path=None):
    """Get the package directory as a context manager.

    Parameters
    ----------
    root_path : str, optional
        Used for testing, overrides the files(__name__) call.

    Returns
    -------
    context manager
        A context manager that yields a pathlib.Path to the package directory.
    """
    if root_path is None:
        resource = Path(__file__).parents[0]
    else:
        resource = root_path
    return as_file(resource)


def _installed_packs_dir(root_path=None) -> Path:
    """Locate requirements/packs/ for the installed package."""
    with get_package_dir(root_path) as pkgdir:
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
    examples_dir : pathlib.Path
        Absolute path to the installed examples directory.
        Defaults to `docs/examples` under the installed package.
    """

    def __init__(self, root_path=None) -> None:
        self.packs_dir = _installed_packs_dir(root_path)
        self.examples_dir = self._get_examples_dir()

    def _get_examples_dir(self) -> Path:
        """Return the absolute path to the installed examples directory.

        Returns
        -------
        pathlib.Path
            Directory containing shipped examples.
        """
        return (self.packs_dir / ".." / ".." / "docs" / "examples").resolve()

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

    def available_examples(self) -> dict[str, List[tuple[str, Path]]]:
        """Finds all examples for each pack and builds a dict.

        Parameters
        ----------
        root_path : Path
            Root path to the examples directory.
        Returns
        -------
        dict
            A dictionary mapping pack names to lists of example names.

        Raises
        ------
        FileNotFoundError
            If the provided root_path does not exist or is not a directory.
        """
        example_dir = self.examples_dir
        examples_dict = {}
        for pack_path in sorted(example_dir.iterdir()):
            if pack_path.is_dir():
                pack_name = pack_path.stem
                examples_dict[pack_name] = []
                for example_path in sorted(pack_path.iterdir()):
                    if example_path.is_dir():
                        example_name = example_path.stem
                        examples_dict[pack_name].append(
                            (example_name, example_path)
                        )
        return examples_dict

    def copy_examples(
        self,
        examples_to_copy: List[str],
        target_dir: Union[Path | str] = None,
        force: bool = False,
    ) -> None:
        """Copy examples or packs into the target or current working
        directory.

        Parameters
        ----------
        examples_to_copy : list of str
            User-specified pack(s), example(s), or "all" to copy all.
        target_dir : pathlib.Path or str, optional
            Target directory to copy examples into. Defaults to current
            working directory.
        force : bool, optional
            Defaults to ``False``. If ``True``, existing files are
            overwritten and directories are merged
            (extra files in the target are preserved).
        """
        if isinstance(target_dir, str):
            target_dir = Path(target_dir)
        self._target_dir = target_dir.resolve() if target_dir else Path.cwd()
        self._force = force

        if "all" in examples_to_copy:
            self._copy_all()
            return

        for item in examples_to_copy:
            if item in self.available_examples():
                self._copy_pack(item)
            elif self._is_example_name(item):
                self._copy_example(item)
            else:
                raise FileNotFoundError(
                    f"No examples or packs found for input: '{item}'"
                )
        del self._target_dir
        del self._force
        return

    def _copy_all(self):
        """Copy all packs and examples."""
        for pack_name in self.available_examples():
            self._copy_pack(pack_name)

    def _copy_pack(self, pack_name):
        """Copy all examples in a single pack."""
        examples = self.available_examples().get(pack_name, [])
        for ex_name, ex_path in examples:
            self._copy_tree_to_target(pack_name, ex_name, ex_path)

    def _copy_example(self, example_name):
        """Copy a single example by its name."""
        example_found = False
        for pack_name, examples in self.available_examples().items():
            for ex_name, ex_path in examples:
                if ex_name == example_name:
                    self._copy_tree_to_target(pack_name, ex_name, ex_path)
                    example_found = True
        if not example_found:
            raise FileNotFoundError(
                f"No examples or packs found for input: '{example_name}'"
            )

    def _is_example_name(self, name):
        """Return True if the given name matches any known example."""
        for pack_name, examples in self.available_examples().items():
            for example_name, _ in examples:
                if example_name == name:
                    return True
        return False

    def _copy_tree_to_target(self, pack_name, example_name, example_origin):
        """Copy an example folder from source to the user's target
        directory."""
        target_dir = self._target_dir / pack_name / example_name
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        if target_dir.exists() and self._force:
            self._overwrite_example(
                example_origin, target_dir, pack_name, example_name
            )
            return
        if target_dir.exists():
            self._copy_missing_files(example_origin, target_dir)
            print(
                f"WARNING: Example '{pack_name}/{example_name}'"
                " already exists at the specified target directory. "
                "Existing files were left unchanged; "
                "new or missing files were copied. To overwrite everything, "
                "rerun with --force."
            )
            return
        self._copy_new_example(
            example_origin, target_dir, pack_name, example_name
        )

    def _overwrite_example(
        self, example_origin, target, pack_name, example_name
    ):
        """Delete target and copy example."""
        shutil.rmtree(target)
        shutil.copytree(example_origin, target)
        print(f"Overwriting example '{pack_name}/{example_name}'.")

    def _copy_missing_files(self, example_origin, target):
        """Copy only files and directories that are missing in the
        target."""
        for example_item in example_origin.rglob("*"):
            rel_path = example_item.relative_to(example_origin)
            target_item = target / rel_path
            if example_item.is_dir():
                target_item.mkdir(parents=True, exist_ok=True)
            elif example_item.is_file() and not target_item.exists():
                target_item.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(example_item, target_item)

    def _copy_new_example(
        self, example_origin, target, pack_name, example_name
    ):
        shutil.copytree(example_origin, target)
        print(f"Copied example '{pack_name}/{example_name}'.")

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

    def print_packs(self) -> None:
        """Print information about available packs."""
        uninstalled_packs, installed_packs = [], []
        s = Styles()
        for pack in self.available_packs():
            if self.check_pack(pack):
                installed_packs.append(pack)
            else:
                uninstalled_packs.append(pack)
        print(f"{s.BOLD}{s.UNDER}{s.BLUE}Installed Packs:{s.RESET}")
        for pack in installed_packs:
            if not installed_packs:
                print("  (none)")
            else:
                print(f"  {pack}")
        print(f"\n{s.BOLD}{s.UNDER}{s.BLUE}Available Packs:{s.RESET}")
        if not uninstalled_packs:
            print("  (all packs installed)")
        else:
            for pack in uninstalled_packs:
                print(f"  {pack}")

    def print_examples(self) -> None:
        """Print information about available examples."""
        s = Styles()
        print(f"\n{s.BOLD}{s.UNDER}{s.CYAN}Examples:{s.RESET}")
        examples_dict = self.available_examples()
        for pack, examples in examples_dict.items():
            print(f"  {s.BOLD}{pack}:{s.RESET}")
            for ex_name, _ in examples:
                print(f"   - {ex_name}")

    def print_info(self) -> None:
        """Print information about available packs, profiles, and
        examples."""
        # packs
        self.print_packs()
        # profiles
        from diffpy.cmi.profilesmanager import ProfilesManager

        prm = ProfilesManager()
        prm.print_profiles()
        # examples
        self.print_examples()
