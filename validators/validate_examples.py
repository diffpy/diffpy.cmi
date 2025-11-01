import runpy
import shutil
from pathlib import Path

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


def test_all_examples(tmp_examples):
    """Run all example scripts to ensure they execute without error."""
    scripts = list(tmp_examples.rglob("**/solutions/diffpy-cmi/*.py"))
    # sort list so that fitBulkNi.py runs first
    scripts.sort(key=lambda s: 0 if s.name == "fitBulkNi.py" else 1)
    for script in scripts:
        script_relative_path = script.relative_to(tmp_examples)
        print(f"Testing {script_relative_path}")
        runpy.run_path(str(script), run_name="__main__")
