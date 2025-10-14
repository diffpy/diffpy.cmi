import os
from pathlib import Path

import pytest

from diffpy.cmi.cli import copy_examples
from diffpy.cmi.packsmanager import PacksManager

# Test copy_examples for various structural cases and copy scenarios.
# In total, 5 structural cases x 6 copy scenarios + 2 path scenarios = 32 tests
# The copy scenarios are:
# a) copy to cwd
# b) copy to target dir

# 1) copy one example
# 2) copy list of examples from same pack
# 3) copy list of examples from different packs
# 4) copy all examples from a pack
# 5) copy all examples from list of packs
# 6) copy all examples from all packs

# Case params: List of tuples
# input: str - name of the test case directory
# user_inputs: List[List[str]] - Possible user inputs for the given case
# expected: List[List[Path]] - The expected paths that should be copied for
#                              each user input
case_params = [
    (
        "case1",  # case with empty pack
        [
            ["empty_pack"],  # 4) all examples from a pack (but pack is empty)
            ["all"],  # 6) all examples from all packs (but pack is empty)
        ],
        [
            [],
            [],
        ],
    ),
    (
        "case2",  # case with one pack with multiple examples
        [
            ["ex1"],  # 1) single example
            ["ex1", "ex2"],  # 2) multiple examples from same pack
            ["full_pack"],  # 4) all examples from a pack
            ["all"],  # 6) all examples from all packs
        ],
        [
            [Path("full_pack/ex1/solution/diffpy-cmi/script1.py")],
            [
                Path("full_pack/ex1/solution/diffpy-cmi/script1.py"),
                Path("full_pack/ex2/random/path/script1.py"),
                Path("full_pack/ex2/random/path/script2.py"),
            ],
            [
                Path("full_pack/ex1/solution/diffpy-cmi/script1.py"),
                Path("full_pack/ex2/random/path/script1.py"),
                Path("full_pack/ex2/random/path/script2.py"),
            ],
            [
                Path("full_pack/ex1/solution/diffpy-cmi/script1.py"),
                Path("full_pack/ex2/random/path/script1.py"),
                Path("full_pack/ex2/random/path/script2.py"),
            ],
        ],
    ),
    (
        "case3",  # case with multiple packs with multiple examples
        [
            ["ex1"],  # 1) single example from packA
            ["ex1", "ex2"],  # 2) list of examples from same pack
            ["ex2", "ex3"],  # 3) list of examples from different packs
            ["packA"],  # 4) all examples from a pack
            ["packA", "packB"],  # 5) all examples from multiple packs
            ["all"],  # 6) all examples from all packs
        ],
        [
            [Path("packA/ex1/script1.py")],
            [
                Path("packA/ex1/script1.py"),
                Path("packA/ex2/solutions/script2.py"),
            ],
            [
                Path("packA/ex2/solutions/script2.py"),
                Path("packB/ex3/more/random/path/script3.py"),
                Path("packB/ex3/more/random/path/script4.py"),
            ],
            [
                Path("packA/ex1/script1.py"),
                Path("packA/ex2/solutions/script2.py"),
            ],
            [
                Path("packA/ex1/script1.py"),
                Path("packA/ex2/solutions/script2.py"),
                Path("packB/ex3/more/random/path/script3.py"),
                Path("packB/ex3/more/random/path/script4.py"),
            ],
            [
                Path("packA/ex1/script1.py"),
                Path("packA/ex2/solutions/script2.py"),
                Path("packB/ex3/more/random/path/script3.py"),
                Path("packB/ex3/more/random/path/script4.py"),
            ],
        ],
    ),
    (
        "case4",  # case with no packs (empty examples directory)
        [
            ["all"],  # 6) all examples from all packs (but examples exist)
        ],
        [
            [],
        ],
    ),
    (
        "case5",  # case with multiple packs with same example names
        [
            ["ex1"],  # 1) single example (ambiguous, should get both)
            [
                "ex1",
                "ex1",
            ],  # 3) list of ex from diff packs (ambiguous, should get both)
            ["packA"],  # 4) all examples from a pack
            ["packA", "packB"],  # 5) all examples from a list of packs
            ["all"],  # 6) all examples from all packs
        ],
        [
            [
                Path("packA/ex1/path1/script1.py"),
                Path("packB/ex1/path2/script2.py"),
            ],
            [
                Path("packA/ex1/path1/script1.py"),
                Path("packB/ex1/path2/script2.py"),
            ],
            [Path("packA/ex1/path1/script1.py")],
            [
                Path("packA/ex1/path1/script1.py"),
                Path("packB/ex1/path2/script2.py"),
            ],
            [
                Path("packA/ex1/path1/script1.py"),
                Path("packA/ex1/path2/script2.py"),
            ],
        ],
    ),
]


@pytest.mark.parametrize("target", [None, "user_target"])
@pytest.mark.parametrize("case,user_inputs,expected", case_params)
def test_copy_examples(case, user_inputs, expected, target, example_cases):
    cwd = example_cases / "cwd"
    os.chdir(cwd)
    case_dir = example_cases / case
    pm = PacksManager(root_path=case_dir)
    examples_dict = pm.available_examples()
    if target is None:
        target_dir = cwd
    else:
        target_dir = case_dir / "user_target"
    for command in user_inputs:
        copy_examples(
            examples_dict,
            user_input=command,
            target_dir=None if target is None else target_dir,
        )
    if expected:
        for exp_paths in expected:
            for path in exp_paths:
                dest_file = target_dir / path
                assert dest_file.exists()
    else:
        empty_dir = list(target_dir.rglob("*"))
        assert not empty_dir, f"Expected nothing, but found: {empty_dir}"


# Test bad inputs to copy_examples
# These include:
# 1) input not found (example or pack)
# 2) mixed good and bad inputs
@pytest.mark.parametrize("case", ["case1", "case2", "case3", "case4", "case5"])
@pytest.mark.parametrize(
    "bad_inputs, expected",
    [
        (["bad_example"], ValueError),  # input not found (example or pack)
        (["ex1", "bad_example"], ValueError),  # mixed good and bad inputs
    ],
)
def test_copy_examples_bad(bad_inputs, expected, case, example_cases):
    """Test copy_examples with bad inputs."""
    case_dir = example_cases / case
    pm = PacksManager(root_path=case_dir)
    examples_dict = pm.available_examples()
    with pytest.raises(expected):
        copy_examples(examples_dict, user_input=bad_inputs)
