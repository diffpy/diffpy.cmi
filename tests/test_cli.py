import os
from pathlib import Path
from shutil import copytree

import pytest

from diffpy.cmi import cli
from diffpy.cmi.packsmanager import PacksManager


@pytest.mark.parametrize(
    "input,to_cwd,expected",
    [
        # PARAMS:
        # input: list - list of example(s) and/or pack(s) to copy
        # to_cwd: bool - whether to copy to cwd (default) or a target dir
        # expected: list - path of copied example(s) and/or pack(s)
        # 1a) user wants to copy one example to cwd
        # 1b) user wants to copy one example to a target dir
        (),
        # 2a) user wants to copy multiple examples to cwd
        # 2b) user wants to copy multiple examples to a target dir
        (),
        # 3a) user wants to copy all examples from a pack to cwd
        # 3b) user wants to copy all examples from a pack to a target dir
        (),
        # 4a) user wants to copy all examples from multiple packs to cwd
        # 4b) user wants to copy all examples from multiple packs to target dir
        (),
        # 5a) user wants to copy a combination of packs and examples to cwd
        # 5b) user wants to copy a combination of packs and examples to target
        (),
        # 6a) user wants to copy all examples from all packs to cwd
        # 6b) user wants to copy all examples from all packs to a target dir
        (),
    ],
)
def test_copy_examples(input, to_cwd, expected, example_cases, target_dir):
    tmp_ex_dir = example_cases / input
    copytree(tmp_ex_dir, target_dir)
    # pkmg = PacksManager()
    # actual = cli.copy_examples(str(target_dir))
    assert False


def test_print_info(temp_path, capsys):
    pkmg = PacksManager()
    actual = pkmg.available_examples(temp_path)
    # pretty print the actual dict
    pkmg.print_info(actual)
    captured = capsys.readouterr()
    output = captured.out.strip()
    # check that output contains expected headers
    assert "Available packs" in output or "Installed packs" in output


# NOTE: double check and remove these test after new above tests are made
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
