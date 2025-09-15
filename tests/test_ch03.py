from pathlib import Path

import pytest
from conftest import __examples_dir__, run_cmi_script


@pytest.mark.parametrize(
    "relative_path",
    [
        f"{__examples_dir__}/ch03NiModelling"
        + "/solutions/diffpy-cmi/fitBulkNi.py",
        f"{__examples_dir__}/ch03NiModelling"
        + "/solutions/diffpy-cmi/fitNPPt.py",
    ],
)
def test_ch03_examples(relative_path):
    script_path = Path(__file__).parent.parent / relative_path
    run_cmi_script(script_path)
