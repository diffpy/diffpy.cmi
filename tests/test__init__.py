# from diffpy.cmi import get_package_dir
from pathlib import Path

import pytest


@pytest.mark.parametrize("root_path", [None, str(Path(__file__).parent)])
def test_get_package_dir(root_path):
    """Test that get_package_dir returns a valid path context
    manager."""
    assert False
