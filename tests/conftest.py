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


def _build_example_structure(base_dir: Path):
    """Helper to build a fake examples directory structure for
    testing."""
    packs = ["packA", "packB"]
    examples_per_pack = ["example1", "example2"]

    for pack in packs:
        for example in examples_per_pack:
            example_path = base_dir / pack / example
            example_path.mkdir(parents=True, exist_ok=True)
            (example_path / "script.py").touch()


@pytest.fixture(scope="session")
def example_cases(tmp_path_factory):
    """Copy the entire examples/ tree into a temp directory once per
    test session.

    Returns the path to that copy.
    """
    examples_dir = tmp_path_factory.mktemp("examples")
    # case 1: pack with no examples
    case1 = examples_dir / "case1" / "examples" / "empty_pack"
    case1.mkdir(parents=True, exist_ok=True)

    # Case 2: pack with multiple examples
    case2_paths_and_files = [
        ("case2/examples/full_pack/ex1/solutions/diffpy-cmi", "script1.py"),
        ("case2/examples/full_pack/ex2/random/dir/path", "script2.py"),
    ]
    for dir_path, file_name in case2_paths_and_files:
        full_path = examples_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        (full_path / file_name).touch()

    # Case 3: multiple packs with multiple examples
    case3_paths_and_files = [
        ("case3/examples/pack1/ex1/", "script1.py"),
        ("case3/examples/pack2/ex1/", "script1.py"),
    ]
    for dir_path, file_name in case3_paths_and_files:
        full_path = examples_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        (full_path / file_name).touch()

    base_case3 = examples_dir / "case3" / "examples"
    packs = ["packA", "packB"]
    examples_per_pack = ["example1", "example2"]

    for pack in packs:
        for example in examples_per_pack:
            example_path = base_case3 / pack / example
            example_path.mkdir(parents=True, exist_ok=True)
            (example_path / "script.py").touch()
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
