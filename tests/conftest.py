import json
import shutil
from pathlib import Path

import matplotlib
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = PROJECT_ROOT / "docs" / "examples"


@pytest.fixture(scope="session")
def tmp_examples(tmp_path_factory):
    """Copy the entire examples/ tree into a temp directory once per
    test session.

    Returns the path to that copy.
    """
    tmpdir = tmp_path_factory.mktemp("examples")
    tmp_examples = tmpdir / "examples"
    shutil.copytree(EXAMPLES_ROOT, tmp_examples)
    yield tmp_examples


def _build_examples_tree_helper(
    base_dir: Path, structure: dict[str, dict[str, list[tuple[str, str]]]]
):
    """Build a nested examples directory structure based on a mapping.

    Parameters
    ----------
    base_dir : Path
        The root temporary directory (e.g., from tmp_path_factory).
    structure : dict
        Mapping of case -> {pack: [(example_name, relative_script_path), ...]}.
    """
    for case_name, packs in structure.items():
        for pack_name, examples in packs.items():
            for example_name, script_relpath in examples:
                script_path = (
                    base_dir
                    / case_name
                    / pack_name
                    / example_name
                    / Path(script_relpath)
                )
                script_path.parent.mkdir(parents=True, exist_ok=True)
                script_path.touch()
    return base_dir


@pytest.fixture(scope="session")
def example_cases(tmp_path_factory):
    """Copy the entire examples/ tree into a temp directory once per
    test session.

    Returns the path to that copy.
    """
    examples_dir = tmp_path_factory.mktemp("examples")

    # case 1: pack with no examples
    # case1_dict = {"case1": {"empty_pack": []}}
    # _build_examples_tree_helper(examples_dir, case1_dict)
    case1 = examples_dir / "case1" / "empty_pack"
    case1.mkdir(parents=True, exist_ok=True)

    # Case 2: pack with multiple examples
    case2a = (
        examples_dir
        / "case2"
        / "full_pack"
        / "example1"
        / "solution"
        / "diffpy-cmi"
    )  # full_pack, example1
    case2a.mkdir(parents=True, exist_ok=True)
    (case2a / "script1.py").touch()
    case2b = (
        examples_dir / "case2" / "full_pack" / "example2" / "random" / "path"
    )  # full_pack, example2
    case2b.mkdir(parents=True, exist_ok=True)
    (case2b / "script1.py").touch()
    (case2b / "script2.py").touch()

    # # Case 3: multiple packs with multiple examples
    # case3a = examples_dir / "case3" / "pack1" / "ex1" # pack1, ex1
    # case3a.mkdir(parents=True, exist_ok=True)
    # (case3b / "script1.py").touch()
    # case3b = examples_dir /
    # tmp_examples = tmpdir / "case3" / "examples"
    # tmp_examples = tmpdir / "case4" / "examples"
    yield examples_dir


@pytest.fixture(scope="session", autouse=True)
def use_headless_matplotlib():
    """Force matplotlib to use a headless backend during tests."""
    matplotlib.use("Agg")


@pytest.fixture
def user_filesystem(tmp_path):
    base_dir = Path(tmp_path)
    home_dir = base_dir / "home_dir"
    home_dir.mkdir(parents=True, exist_ok=True)
    cwd_dir = base_dir / "cwd_dir"
    cwd_dir.mkdir(parents=True, exist_ok=True)

    home_config_data = {"username": "home_username", "email": "home@email.com"}
    with open(home_dir / "diffpyconfig.json", "w") as f:
        json.dump(home_config_data, f)

    yield tmp_path
