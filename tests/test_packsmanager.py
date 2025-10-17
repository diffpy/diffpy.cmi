import os
from pathlib import Path

import pytest

from diffpy.cmi.packsmanager import PacksManager


def paths_and_names_match(expected, actual, root):
    """Compare two tuples (example_name, path), ignoring temp dir
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
                ("ex2", "case5/docs/examples/packA/ex2"),
            ],
            "packB": [
                ("ex1", "case5/docs/examples/packB/ex1"),
                ("ex3", "case5/docs/examples/packB/ex3"),
                ("ex4", "case5/docs/examples/packB/ex4"),
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


copy_params = [
    # Test various use cases to copy_examples on case5
    # 1) copy one example (ambiguous)
    # 2) copy list of examples from same pack (ambiguous)
    # 3) copy list of examples from different pack (ambiguous)
    # 4) copy one example (unambiguous)
    # 5) copy list of examples from same pack (unambiguous)
    # 6) copy list of examples from different pack (unambiguous)
    # 7) copy all examples from a pack
    # 8) copy all examples from list of packs
    # 9) copy all examples from all packs
    (  # 1) copy one example, (ambiguous)
        ["ex1"],
        [
            Path("packA/ex1/path1/script1.py"),
            Path("packB/ex1/path2/script2.py"),
        ],
    ),
    (  # 2) copy list of examples from same pack (ambiguous)
        ["ex1", "ex2"],
        [
            Path("packA/ex1/path1/script1.py"),
            Path("packB/ex1/path2/script2.py"),
            Path("packA/ex2/script3.py"),
        ],
    ),
    (  # 3) copy list of examples from different packs (ambiguous)
        ["ex1", "ex1"],
        [
            Path("packA/ex1/path1/script1.py"),
            Path("packB/ex1/path2/script2.py"),
        ],
    ),
    (  # 4) copy one example (unambiguous)
        ["ex2"],
        [
            Path("packA/ex2/script3.py"),
        ],
    ),
    (  # 5) copy list of examples from same pack (unambiguous)
        ["ex3", "ex4"],
        [
            Path("packB/ex3/script4.py"),
            Path("packB/ex4/script5.py"),
        ],
    ),
    (  # 6) copy list of examples from different packs (unambiguous)
        ["ex2", "ex3"],
        [
            Path("packA/ex2/script3.py"),
            Path("packB/ex3/script4.py"),
        ],
    ),
    (  # 7) copy all examples from a pack
        ["packA"],
        [
            Path("packA/ex1/path1/script1.py"),
            Path("packA/ex2/script3.py"),
        ],
    ),
    (  # 8) copy all examples from list of packs
        ["packA", "packB"],
        [
            Path("packA/ex1/path1/script1.py"),
            Path("packA/ex2/script3.py"),
            Path("packB/ex1/path2/script2.py"),
            Path("packB/ex3/script4.py"),
            Path("packB/ex4/script5.py"),
        ],
    ),
    (  # 9) copy all examples from all packs
        ["all"],
        [
            Path("packA/ex1/path1/script1.py"),
            Path("packA/ex2/script3.py"),
            Path("packB/ex1/path2/script2.py"),
            Path("packB/ex3/script4.py"),
            Path("packB/ex4/script5.py"),
        ],
    ),
]


# input: list of str - cli input(s) to copy_examples
# expected_paths: list of Path - expected relative paths to copied examples
@pytest.mark.parametrize("input,expected_paths", copy_params)
def test_copy_examples(input, expected_paths, example_cases):
    examples_dir = example_cases / "case5"
    pm = PacksManager(root_path=examples_dir)
    target_dir = example_cases / "user_target"
    actual = pm.copy_examples(input, target_dir=target_dir)
    expected = []
    for path in expected_paths:
        root_path = target_dir / path
        expected.append(root_path)
    assert actual == expected


# Test default and targeted copy_example location on case5
# input: str or None - path arg to copy_examples
# expected: Path - expected relative path to copied example
@pytest.mark.parametrize(
    "input,expected_path",
    [
        (None, Path("cwd/packA/ex1/path1/script1.py")),
        ("user_target", Path("user_target/packA/ex1/path1/script1.py")),
    ],
)
def test_copy_examples_location(input, expected_path, example_cases):
    examples_dir = example_cases / "case5"
    os.chdir(example_cases / "cwd")
    pm = PacksManager(root_path=examples_dir)
    paths = pm.copy_examples(["packA"], target_dir=input)
    actual = paths[0]
    expected = example_cases / expected_path
    assert actual == expected


# Test bad inputs to copy_examples on case3
# These include:
# 1) Input not found (example or pack)
# 2) Mixed good and bad inputs
# 3) Path to directory already exists
# 4) No input provided
@pytest.mark.parametrize(
    "bad_inputs,expected,path",
    [
        (  # input not found (example or pack)
            ["bad_example"],
            ValueError,
            None,
        ),
        (  # mixed good ex and bad inputs
            ["ex1", "bad_example"],
            ValueError,
            None,
        ),
        (  # mixed good pack and bad inputs
            ["packA", "bad_example"],
            ValueError,
            None,
        ),
        (  # path to dir already exists
            ["ex1"],
            FileExistsError,
            Path("docs/examples/"),
        ),
        (  # No input provided
            [],
            ValueError,
            None,
        ),
    ],
)
def test_copy_examples_bad(bad_inputs, expected, path, example_cases):
    examples_dir = example_cases / "case3"
    pm = PacksManager(root_path=examples_dir)
    with pytest.raises(expected):
        pm.copy_examples(
            bad_inputs,
            target_dir=examples_dir / path if path is not None else None,
        )


# Test bad target_dir to copy_examples on case3
# 1) target doesn't exist
# 2) target is a file
# 3) target is nested in a file
@pytest.mark.parametrize(
    "bad_inputs,expected",
    [
        (Path("nonexistent/path/target"), FileNotFoundError),  # doesn't exist
        (
            Path("docs/examples/packA/ex1/script4.py"),
            NotADirectoryError,
        ),  # target is a file
        (
            Path("docs/examples/packA/ex1/script4.py/nested"),
            NotADirectoryError,
        ),  # nested in file
    ],
)
def test_copy_examples_bad_target(bad_inputs, expected, example_cases):
    examples_dir = example_cases / "case3"
    pm = PacksManager(root_path=examples_dir)
    with pytest.raises(expected):
        pm.copy_examples(
            ["packA"],
            target_dir=bad_inputs,
        )
