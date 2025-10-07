import pytest

from diffpy.cmi.packsmanager import PacksManager


@pytest.mark.parametrize(
    "input,expected",
    [
        # Pack with no examples
        {"empty_pack": []},
        # Pack with multiple examples
        {
            "full_pack": [
                ("example1", "path_to_1"),
                ("example2", "path_to_2"),
            ]
        },
        # Multiple packs with examples
        {
            "pack1": [("ex1", "path1"), ("ex2", "path2")],
            "pack2": [("ex3", "path3")],
        },
        # No pack found
        {},
    ],
)
def test_available_examples(temp_path, expected):
    for pack, examples in expected.items():
        pack_dir = temp_path / pack
        pack_dir.mkdir(parents=True, exist_ok=True)
        for ex in examples:
            ex_dir = pack_dir / ex
            ex_dir.mkdir(parents=True, exist_ok=True)
    pkmg = PacksManager()
    actual = pkmg.available_examples(temp_path)
    assert actual == expected


def test_available_examples_bad(temp_path):
    pkmg = PacksManager()
    bad_path = temp_path / "nonexistent"
    with pytest.raises(FileNotFoundError):
        pkmg.available_examples(bad_path)


def test_print_info(temp_path, capsys):
    pkmg = PacksManager()
    actual = pkmg.available_examples(temp_path)
    pkmg.print_info(actual)
    captured = capsys.readouterr()
    output = captured.out.strip()
    assert "Available packs" in output or "Installed packs" in output
