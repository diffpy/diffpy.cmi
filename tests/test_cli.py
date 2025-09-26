import os

import pytest

from diffpy.cmi import cli


@pytest.mark.parametrize(
    "inputs, expected",
    [
        # case: no packs, no examples, expect empty dict
        ([], {}),
        # case: one pack with one example,
        # expect dict of {"pack-name": ["example"]}
        ([("packA", ["ex1"])], {"packA": ["ex1"]}),
        # case: one pack with multiple examples,
        # expect dict of {"pack-name": ["example1", "example2"]}
        ([("packA", ["ex1", "ex2"])], {"packA": ["ex1", "ex2"]}),
        # case: multiple packs with one example each,
        # expect dict of {"pack-name": ["example"]}
        (
            [("packA", ["ex1"]), ("packB", ["ex2"])],
            {"packA": ["ex1"], "packB": ["ex2"]},
        ),
        # case: multiple packs with multiple examples,
        # expect dict of {"pack-name": ["example1", "example2"]}
        (
            [("packA", ["ex1", "ex2"]), ("packB", ["ex3", "ex4"])],
            {"packA": ["ex1", "ex2"], "packB": ["ex3", "ex4"]},
        ),
    ],
)
def test_map_pack_to_examples(tmp_path, mocker, inputs, expected):
    """Finds examples directory and returns a dictionary mapping packs
    to examples."""
    for pack_name, example_list in inputs:
        packdir = tmp_path / pack_name
        packdir.mkdir()
        for example in example_list:
            exdir = packdir / example
            exdir.mkdir()
    # patch _get_examples_dir to point to tmp_path
    mocker.patch.object(cli, "_get_examples_dir", return_value=tmp_path)
    result = cli.map_pack_to_examples()
    assert result == expected


def test_copy_example_success(tmp_path, mocker):
    """Tests successful copy of example from pack to cwd."""
    pack, ex = "pack1", "ex1"
    example_dir = tmp_path / pack / ex
    example_dir.mkdir(parents=True)
    # Patch _get_examples_dir to use tmp_path
    mocker.patch.object(cli, "_get_examples_dir", return_value=tmp_path)
    os.chdir(tmp_path)
    dest = cli.copy_example(f"{pack}/{ex}")
    expected_dest = tmp_path / ex
    assert dest == expected_dest
    assert dest.exists()


@pytest.mark.parametrize("bad_input", ["pack1ex1", "pack1/", "/ex1"])
def test_copy_example_invalid_format(tmp_path, mocker, bad_input):
    """Tests invalid format ValueError."""
    mocker.patch.object(cli, "_get_examples_dir", return_value=tmp_path)
    os.chdir(tmp_path)
    with pytest.raises(ValueError):
        cli.copy_example(bad_input)


@pytest.mark.parametrize(
    "pack, ex",
    [
        ("pack1", "ex1"),
        ("missing_pack", "ex1"),
    ],
)
def test_copy_example_not_found(tmp_path, mocker, pack, ex):
    """
    Test copy_example raises FileNotFoundError when:
    - the pack exists but example is missing
    - the pack itself is missing
    """
    mocker.patch.object(cli, "_get_examples_dir", return_value=tmp_path)
    os.chdir(tmp_path)
    with pytest.raises(FileNotFoundError):
        cli.copy_example(f"{pack}/{ex}")


def test_copy_example_destination_exists(tmp_path, mocker):
    """Tests FileExistsError when destination directory already
    exists."""
    pack, ex = "pack1", "ex1"
    example_dir = tmp_path / pack / ex
    example_dir.mkdir(parents=True)
    mocker.patch.object(cli, "_get_examples_dir", return_value=tmp_path)
    os.chdir(tmp_path)
    (tmp_path / ex).mkdir(exist_ok=True)
    with pytest.raises(FileExistsError):
        cli.copy_example(f"{pack}/{ex}")
