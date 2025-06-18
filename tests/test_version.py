"""Unit tests for __version__.py."""

import diffpy.cmi  # noqa


def test_package_version():
    """Ensure the package version is defined and not set to the initial
    placeholder."""
    assert hasattr(diffpy.cmi, "__version__")
    assert diffpy.cmi.__version__ != "0.0.0"
