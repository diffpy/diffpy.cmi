import pytest

from diffpy.cmi.packsmanager import PacksManager


@pytest.mark.parametrize(
    "expected",
    [
        {
            # test with pack that has examples
            "pack1": [
                "ex1",
                "ex2",
                "ex3",
            ]
        },
        {
            # test pack with no examples
            "no_examples": []
        },
    ],
)
def test_available_examples(temp_path, expected):
    for pack, examples in expected.items():
        pack_dir = temp_path / pack
        pack_dir.mkdir(parents=True, exist_ok=True)
        for ex in examples:
            ex_dir = pack_dir / ex
            ex_dir.mkdir(parents=True, exist_ok=True)
    pkmg = PacksManager(temp_path)
    actual = pkmg.available_examples(temp_path)
    assert actual == expected


def test_available_examples_bad(temp_path):
    pkmg = PacksManager(temp_path)
    bad_path = temp_path / "nonexistent"
    with pytest.raises(FileNotFoundError):
        pkmg.available_examples(bad_path)


def test_print_info(temp_path, capsys):
    pkmg = PacksManager(temp_path)
    pkmg.print_info()
    captured = capsys.readouterr()
    output = captured.out.strip()
    assert "Available packs" in output or "Installed packs" in output
