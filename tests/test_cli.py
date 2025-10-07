import os
from pathlib import Path

import pytest

from diffpy.cmi import cli
from diffpy.cmi.packsmanager import PacksManager


def test_print_info(temp_path, capsys):
    pkmg = PacksManager()
    actual = pkmg.available_examples(temp_path)
    # pretty print the actual dict
    pkmg.print_info(actual)
    captured = capsys.readouterr()
    output = captured.out.strip()
    # check that output contains expected headers
    assert "Available packs" in output or "Installed packs" in output


@pytest.mark.parametrize()
def test_copy_examples(dict, tmp_path):
    cli.copy_examples(examples=dict, target_dir=tmp_path)
    assert False


def test_map_pack_to_examples_structure():
    """Test that map_pack_to_examples returns the right shape of
    data."""
    actual = cli.map_pack_to_examples()
    assert isinstance(actual, dict)
    for pack, exdirs in actual.items():
        assert isinstance(pack, str)
        assert isinstance(exdirs, list)
        for ex in exdirs:
            assert isinstance(ex, str)
    # Check for known packs
    assert "core" in actual.keys()
    assert "pdf" in actual.keys()
    # Check for known examples
    assert ["linefit"] in actual.values()


@pytest.mark.parametrize(
    "input_valid_str",
    [
        "core/linefit",
        "pdf/ch03NiModelling",
    ],
)
def test_copy_example_success(tmp_path, input_valid_str):
    """Given a valid example format (<pack>/<ex>), test that its copied
    to the temp dir."""
    os.chdir(tmp_path)
    actual = cli.copy_example(input_valid_str)
    expected = tmp_path / Path(input_valid_str).name
    assert expected.exists() and expected.is_dir()
    assert actual == expected


def test_copy_example_fnferror():
    """Test that FileNotFoundError is raised when the example does not
    exist."""
    with pytest.raises(FileNotFoundError):
        cli.copy_example("pack/example1")


@pytest.mark.parametrize(
    "input_bad_str",
    [
        "",  # empty string
        "/",  # missing pack and example
        "corelinefit",  # missing slash
        "linefit",  # missing pack and slash
        "core/",  # missing example
        "/linefit",  # missing pack
        "core/linefit/extra",  # too many slashes
    ],
)
def test_copy_example_valueerror(input_bad_str):
    """Test that ValueError is raised when the format is invalid."""
    with pytest.raises(ValueError):
        cli.copy_example(input_bad_str)
