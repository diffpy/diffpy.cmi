from pathlib import Path

import pytest
from conftest import __examples_dir__, run_cmi_script


@pytest.mark.parametrize(
    "relative_path",
    [
        f"{__examples_dir__}/ch07StructuralPhaseTransitions"
        + "/solutions/diffpy-cmi/fitTSeries.py",
    ],
)
def test_ch07_examples(relative_path):
    script_path = Path(__file__).parent.parent / relative_path
    run_cmi_script(script_path)
