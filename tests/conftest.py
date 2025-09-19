import json
import shutil
import warnings
from pathlib import Path

import matplotlib
import pytest

# Suppress specific UserWarnings when running mpl headless
warnings.filterwarnings(
    "ignore", category=UserWarning, message=".*FigureCanvasAgg.*"
)

EXAMPLES_DIR = Path(__file__).parent.parent / "docs" / "examples"
TESTS_DIR = Path(__file__).parent


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


@pytest.fixture(scope="session", autouse=True)
def use_headless_matplotlib():
    """Force matplotlib to use a headless backend during tests."""
    matplotlib.use("Agg")


@pytest.fixture(scope="session")
def examples_tmpdir(tmp_path_factory):
    """Make a temp copy of all examples for safe testing.

    Removes the temp copy after tests are done.
    """
    temp_dir = tmp_path_factory.mktemp("examples_copy")
    temp_examples = temp_dir / "examples"
    shutil.copytree(EXAMPLES_DIR, temp_examples, dirs_exist_ok=True)
    yield temp_examples
    shutil.rmtree(temp_dir, ignore_errors=True)
