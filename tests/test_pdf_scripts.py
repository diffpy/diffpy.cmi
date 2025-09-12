import glob
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import pytest


def no_op(*args, **kwargs):
    """A no-operation function to replace plt.show during tests."""
    pass


example_scripts = glob.glob("docs/examples/ch*/solutions/diffpy-cmi/*.py")


@pytest.mark.parametrize("script_path", example_scripts)
def test_script_execution(monkeypatch, script_path):
    """Test execution of each example script while suppressing plot
    display."""
    monkeypatch.setattr(plt, "show", no_op)
    # Special handling for fitNPPt.py which depends on fitBulkNi.py
    if script_path.endswith("fitNPPt.py"):
        ni_script = script_path.replace("fitNPPt.py", "fitBulkNi.py")
        ni_script_path = Path(ni_script)
        if not ni_script_path.exists():
            pytest.fail(
                f"Required script {ni_script} not found for {script_path}"
            )
        # Run Ni calibration first
        result_ni = subprocess.run(
            ["python", str(ni_script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result_ni.returncode != 0:
            pytest.fail(
                f"Calibration script {ni_script}",
                " failed with error:\n{result_ni.stderr}",
            )
    # Run rest of the scripts
    result = subprocess.run(
        ["python", script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert (
        result.returncode == 0
    ), f"Script {script_path} failed with error:\n{result.stderr}"
