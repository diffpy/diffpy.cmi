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
    case3a = examples_dir / "case3" / "packA" / "my_ex1"  # packA, ex1
    case3a.mkdir(parents=True, exist_ok=True)
    (case3a / "script1.py").touch()
    case3b = (
        examples_dir / "case3" / "packA" / "my_ex2" / "solutions"
    )  # packA, ex2
    case3b.mkdir(parents=True, exist_ok=True)
    (case3b / "script2.py").touch()
    case3c = (
        examples_dir / "case3" / "packB" / "ex1" / "more" / "random" / "path"
    )  # packB, ex1
    case3c.mkdir(parents=True, exist_ok=True)
    (case3c / "script3.py").touch()
    (case3c / "script4.py").touch()

    # # Case 4: no pack found (empty directory)
    case4 = examples_dir / "case4"
    case4.mkdir(parents=True, exist_ok=True)

    # Case 5: multiple packs with the same example names
    case5a = examples_dir / "case5" / "packA" / "example" / "path1"
    case5a.mkdir(parents=True, exist_ok=True)
    (case5a / "script1.py").touch()
    case5b = examples_dir / "case5" / "packB" / "example" / "path2"
    case5b.mkdir(parents=True, exist_ok=True)
    (case5b / "script2.py").touch()

    yield examples_dir


@pytest.fixture(scope="session")
def target_dir(tmp_path_factory):
    """Create a temporary directory to serve as the target for copying
    examples."""
    target_directory = tmp_path_factory.mktemp("copy_target")
    yield target_directory


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
