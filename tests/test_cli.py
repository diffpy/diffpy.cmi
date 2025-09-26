import pytest

from diffpy.cmi import cli


@pytest.mark.parametrize(
    "structure, expected",
    [
        # case: no packs, no examples
        ([], {}),
        # case: one pack with one example
        ([("packA", ["ex1"])], {"packA": ["ex1"]}),
        # case: one pack with multiple examples
        ([("packA", ["ex1", "ex2"])], {"packA": ["ex1", "ex2"]}),
        # case: multiple packs with one example each
        (
            [("packA", ["ex1"]), ("packB", ["ex2"])],
            {"packA": ["ex1"], "packB": ["ex2"]},
        ),
        # case: multiple packs with multiple examples
        (
            [("packA", ["ex1", "ex2"]), ("packB", ["ex3", "ex4"])],
            {"packA": ["ex1", "ex2"], "packB": ["ex3", "ex4"]},
        ),
    ],
)
def test_map_pack_to_examples(tmp_path, mocker, structure, expected):
    """Finds examples directory and returns a dictionary mapping packs
    to examples."""
    # example input: build example structure
    for pack, exdirs in structure:
        packdir = tmp_path / pack
        packdir.mkdir()
        for ex in exdirs:
            exdir = packdir / ex
            exdir.mkdir()
            # check directory was created
            assert exdir.exists() and exdir.is_dir(), f"{exdir} not created"
    # patch _get_examples_dir to point to tmp_path
    mocker.patch.object(cli, "_get_examples_dir", return_value=tmp_path)
    # expected behavior: a dictionary mapping pack to lists of examples
    result = cli.map_pack_to_examples()
    assert result == expected


def test_copy_examples():
    """"""
    return
