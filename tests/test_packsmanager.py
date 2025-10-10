import pytest

from diffpy.cmi.packsmanager import PacksManager


def paths_and_names_match(expected, actual, root):
    """Compare two (example_name, path) lists ignoring temp dir
    differences."""
    if len(expected) != len(actual):
        return False
    for (exp_name, exp_path), (act_name, act_path) in zip(expected, actual):
        if exp_name != act_name:
            return False
        actual_rel_path = str(act_path.relative_to(root))
        if actual_rel_path != exp_path:
            return False
    return True


example_params = [
    # 1) pack with no examples.  Expect {'empty_pack': []}
    # 2) pack with multiple examples.
    #  Expect {'full_pack': [('example1`, path_to_1'), 'example2', path_to_2)]
    # 3) multiple packs.  Expect dict with multiple pack:tuple pairs
    # 4) no pack found. Expect {}
    # case 1: pack with no examples.  Expect {'empty_pack': []}
    # 5) multiple packs with the same example names
    # Expect dict with multiple pack:tuple pairs
    (
        "case1",
        {"empty_pack": []},
    ),
    # case 2: pack with multiple examples.
    # Expect {'full_pack': [('example1', path_to_1),
    #           ('example2', path_to_2)]}
    (
        "case2",
        {
            "full_pack": [
                ("ex1", "case2/docs/examples/full_pack/ex1"),
                ("ex2", "case2/docs/examples/full_pack/ex2"),
            ]
        },
    ),
    # case 3: multiple packs.  Expect dict with multiple pack:tuple pairs
    (
        "case3",
        {
            "packA": [
                ("ex1", "case3/docs/examples/packA/ex1"),
                ("ex2", "case3/docs/examples/packA/ex2"),
            ],
            "packB": [("ex3", "case3/docs/examples/packB/ex3")],
        },
    ),
    (  # case 4: no pack found. Expect {}
        "case4",
        {},
    ),
    (  # case 5: multiple packs with duplicate example names
        # Expect dict with multiple pack:tuple pairs
        "case5",
        {
            "packA": [
                ("ex1", "case5/docs/examples/packA/ex1"),
            ],
            "packB": [
                ("ex1", "case5/docs/examples/packB/ex1"),
            ],
        },
    ),
]


@pytest.mark.parametrize("input,expected", example_params)
def test_available_examples(input, expected, example_cases):
    case_dir = example_cases / input
    pkmg = PacksManager(case_dir)
    actual = pkmg.available_examples()
    assert actual.keys() == expected.keys()
    for pack in expected:
        assert paths_and_names_match(
            expected[pack], actual[pack], example_cases
        )


@pytest.mark.parametrize("input,expected", example_params)
def test_tmp_file_structure(input, expected, example_cases):
    example_path = example_cases / input
    for path in example_path.rglob("*"):
        if path.suffix:
            assert path.is_file()
        else:
            assert path.is_dir()
