import pytest

from diffpy.cmi.packsmanager import PacksManager

example_params = [
    # 1) pack with no examples.  Expect {'empty_pack': []}
    # 2) pack with multiple examples.
    #  Expect {'full_pack': [('example1`, path_to_1'), 'example2', path_to_2)]
    # 3) multiple packs.  Expect dict with multiple pack:tuple pairs
    # 4) no pack found. Expect {}
    # case 1: pack with no examples.  Expect {'empty_pack': []}
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
                ("example1", "case2/full_pack/example1"),
                ("example2", "case2/full_pack/example2"),
            ]
        },
    ),
    # case 3: multiple packs.  Expect dict with multiple pack:tuple pairs
    (
        "case3",
        {
            "packA": [
                ("my_ex1", "case3/packA/my_ex1"),
                ("my_ex2", "case3/packA/my_ex2"),
            ],
            "packB": [("ex1", "case3/packB/ex1")],
        },
    ),
    (  # case 4: no pack found. Expect {}
        "case4",
        {},
    ),
    (  # case 5: multiple packs with the same example names
        # Expect dict with multiple pack:tuple pairs
        "case5",
        {
            "packA": [
                ("example", "case5/packA/example"),
            ],
            "packB": [
                ("example", "case5/packB/example"),
            ],
        },
    ),
]


@pytest.mark.parametrize("input,expected", example_params)
def test_available_examples(input, expected, example_cases):
    tmp_ex_dir = example_cases / input
    pkmg = PacksManager(tmp_ex_dir)
    # Ensure the example directory is correctly set
    assert pkmg.examples_dir == tmp_ex_dir
    actual = pkmg.available_examples()
    # Verify that the keys (pack names) are correct
    assert set(actual.keys()) == set(expected.keys())
    # Verify that each expected example exists in actual
    for expected_pack, expected_list in expected.items():
        actual_list = actual[expected_pack]
        for (expected_exname, expected_path), (
            actual_exname,
            actual_path,
        ) in zip(expected_list, actual_list):
            # Checks example name and path
            assert expected_exname == actual_exname
            assert expected_path == str(actual_path.relative_to(example_cases))


@pytest.mark.parametrize("input,expected", example_params)
def test_tmp_(input, expected, example_cases):
    example_path = example_cases / input
    for path in example_path.rglob("*"):
        if path.suffix:
            # Checks temp files are files and not dirs
            assert path.is_file()
        else:
            assert path.is_dir(), f"{path} should be a directory"
