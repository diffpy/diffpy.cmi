import pytest

from diffpy.cmi.packsmanager import PacksManager


@pytest.mark.parametrize(
    "expected_dict",
    [
        {
            "pdf": [
                "ch03NiModelling",
                "ch06RefineCrystalStructureGen",
                "ch07StructuralPhaseTransition",
                "ch08NPRefinement",
            ]
        }
    ],
)
def test_available_examples(expected_dict):
    """Test that available_examples returns a dict."""
    pkmg = PacksManager()
    returned_dict = pkmg.available_examples()
    expected_pack = list(expected_dict.keys())
    returned_pack = list(returned_dict.keys())
    for pack in expected_pack:
        assert pack in returned_pack, f"{pack} not found in returned packs."
        expected_examples = expected_dict[pack]
        returned_examples = returned_dict.get(pack, [])
        for ex in expected_examples:
            assert (
                ex in returned_examples
            ), f"{ex} not found under pack {pack}."


def test_print_info(capsys):
    """Test that print_info prints expected information to stdout."""
    pkmg = PacksManager()
    pkmg.print_info()
    captured = capsys.readouterr()
    output = captured.out.strip()
    assert "Available packs" in output or "Installed packs" in output
