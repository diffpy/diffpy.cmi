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
