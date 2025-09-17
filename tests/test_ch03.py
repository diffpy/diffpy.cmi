from pathlib import Path

import pytest
from conftest import __examples_dir__, run_cmi_script

chapter = "ch03NiModelling"
chapter_dir = Path(__examples_dir__) / chapter
example_scripts = list(chapter_dir.rglob("*.py"))


# Runs all example scripts in chapter 3, skips files in main() is not defined.
# Passes if script runs without error.
@pytest.mark.parametrize("script_path", example_scripts, ids=lambda p: p.name)
def test_ch03_examples(script_path):
    run_cmi_script(script_path)
