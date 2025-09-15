from pathlib import Path

import pytest
from conftest import __examples_dir__, run_cmi_script


@pytest.mark.parametrize(
    "relative_path",
    [
        f"{__examples_dir__}/ch11ClusterXYZ/solutions/diffpy-cmi/fitCdSeNP.py",
    ],
)
def test_ch11_examples(relative_path):
    script_path = Path(__file__).parent.parent / relative_path
    run_cmi_script(script_path)
