from diffpy.cmi import cli


def test_map_pack_to_examples_structure():
    """Test that map_pack_to_examples returns the right shape of
    data."""
    result = cli.map_pack_to_examples()
    assert isinstance(result, dict)
    for pack, exdirs in result.items():
        assert isinstance(pack, str)
        assert isinstance(exdirs, list)
        for ex in exdirs:
            assert isinstance(ex, str)
    # Check for known packs
    assert "core" in result.keys()
    assert "pdf" in result.keys()
    # Check for known examples
    assert ["linefit"] in result.values()
