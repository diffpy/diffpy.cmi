import os
import re
from pathlib import Path

import pytest

from diffpy.cmi import installer
from diffpy.cmi.packsmanager import PacksManager, Styles


def paths_and_names_match(expected, actual, root):
    """Compare two tuples (example_name, path), ignoring temp dir
    differences."""
    if len(expected) != len(actual):
        return False
    for (exp_name, exp_path), (act_name, act_path) in zip(expected, actual):
        if exp_name != act_name:
            return False
        actual_rel_path = act_path.relative_to(root).as_posix()
        expected_path_norm = Path(exp_path).as_posix()
        if actual_rel_path != expected_path_norm:
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
    # 3) copy one example (unambiguous)
    # 4) copy list of examples from same pack (unambiguous)
    # 5) copy list of examples from different packs (unambiguous)
    # 6) copy all examples from a pack
    # 7) copy all examples from list of packs
    # 8) copy all examples from all packs
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
    (  # 3) copy one example (unambiguous)
        ["ex2"],
        [
            Path("packA/ex2/script3.py"),
        ],
    ),
    (  # 4) copy list of examples from same pack (unambiguous)
        ["ex3", "ex4"],
        [
            Path("packB/ex3/script4.py"),
            Path("packB/ex4/script5.py"),
        ],
    ),
    (  # 5) copy list of examples from different packs (unambiguous)
        ["ex2", "ex3"],
        [
            Path("packA/ex2/script3.py"),
            Path("packB/ex3/script4.py"),
        ],
    ),
    (  # 6) copy all examples from a pack
        ["packA"],
        [
            Path("packA/ex1/path1/script1.py"),
            Path("packA/ex2/script3.py"),
        ],
    ),
    (  # 7) copy all examples from list of packs
        ["packA", "packB"],
        [
            Path("packA/ex1/path1/script1.py"),
            Path("packA/ex2/script3.py"),
            Path("packB/ex1/path2/script2.py"),
            Path("packB/ex3/script4.py"),
            Path("packB/ex4/script5.py"),
        ],
    ),
    (  # 8) copy all examples from all packs
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
    pm.copy_examples(input, target_dir=target_dir)
    actual = sorted(target_dir.rglob("*.py"))
    expected = sorted([target_dir / path for path in expected_paths])
    assert actual == expected
    for path in expected_paths:
        copied_path = target_dir / path
        original_path = examples_dir / path
        if copied_path.is_file() and original_path.is_file():
            assert copied_path.read_text() == original_path.read_text()


# Test default and targeted copy_example location on case5
# input: str or None - path arg to copy_examples
# expected: Path - expected relative path to copied example
@pytest.mark.parametrize(
    "input,expected_paths",
    [
        (
            None,
            [
                Path("cwd/packA/ex1/path1/script1.py"),
                Path("cwd/packA/ex2/script3.py"),
            ],
        ),
        # input is a target dir that doesn't exist yet
        # expected target dir to be created and examples copied there
        (
            Path("user_target"),
            [
                Path("cwd/user_target/packA/ex1/path1/script1.py"),
                Path("cwd/user_target/packA/ex2/script3.py"),
            ],
        ),
        # input is a target dir that already exists
        # expected examples copied into existing dir
        (
            Path("existing_target"),
            [
                Path("cwd/existing_target/packA/ex1/path1/script1.py"),
                Path("cwd/existing_target/packA/ex2/script3.py"),
            ],
        ),
    ],
)
def test_copy_examples_location(input, expected_paths, example_cases):
    examples_dir = example_cases / "case5"
    os.chdir(example_cases / "cwd")
    pm = PacksManager(root_path=examples_dir)
    pm.copy_examples(["packA"], target_dir=input)
    target_directory = (
        Path.cwd() if input is None else example_cases / "cwd" / input
    )
    actual = sorted(target_directory.rglob("*.py"))
    expected = sorted([example_cases / path for path in expected_paths])
    assert actual == expected


# Test bad inputs to copy_examples on case3
# These include:
# 1) Input not found (example or pack)
# 2) Mixed good and bad inputs
# 3) Path to directory already exists
# 4) No input provided
@pytest.mark.parametrize(
    "bad_inputs,expected,path,is_warning",
    [
        (
            # 1) Input not found (example or pack).
            # Expected: Raise an error with the message.
            ["bad_example"],
            "No examples or packs found for input: 'bad_example'",
            None,
            False,
        ),
        (
            # 2) Mixed good example and bad input.
            # Expected: Raise an error with the message.
            ["ex1", "bad_example"],
            "No examples or packs found for input: 'bad_example'",
            None,
            False,
        ),
        (
            # 3) Mixed good pack and bad input.
            # Expected: Raise an error with the message.
            ["packA", "bad_example"],
            "No examples or packs found for input: 'bad_example'",
            None,
            False,
        ),
        (
            # 4) Path to directory already exists.
            # Expected: Raise a warning with the message.
            ["ex1"],
            (
                "WARNING: Example 'packA/ex1' already exists at"
                " the specified target directory. "
                "Existing files were left unchanged; new or missing "
                "files were copied. "
                "To overwrite everything, rerun with --force."
            ),
            Path("docs/examples/"),
            True,
        ),
    ],
)
def test_copy_examples_bad(
    bad_inputs, expected, path, is_warning, example_cases, capsys
):
    examples_dir = example_cases / "case3"
    pm = PacksManager(root_path=examples_dir)
    target_dir = None if path is None else examples_dir / path
    if is_warning:
        pm.copy_examples(bad_inputs, target_dir=target_dir)
        captured = capsys.readouterr()
        actual = captured.out
        assert re.search(re.escape(expected), actual)
    else:
        with pytest.raises(FileNotFoundError, match=re.escape(expected)):
            pm.copy_examples(bad_inputs, target_dir=target_dir)


@pytest.mark.parametrize(
    "expected_paths,force",
    [
        (
            [  # UC1: copy examples to target dir with overwrite
                # expected: Existing files are overwritten and new files copied
                Path("packA/ex1/script1.py"),
                Path("packA/ex2/solutions/script2.py"),
            ],
            True,
        ),
        (
            [  # UC2: copy examples to target dir without overwrite
                # expected: Existing files are left unchanged; new files copied
                Path("packA/ex1/path1/script1.py"),
                Path("packA/ex1/script1.py"),
                Path("packA/ex2/solutions/script2.py"),
                Path("packA/ex2/script3.py"),
            ],
            False,
        ),
    ],
)
def test_copy_examples_force(example_cases, expected_paths, force):
    examples_dir = example_cases / "case3"
    pm = PacksManager(root_path=examples_dir)
    case5dir = example_cases / "case5" / "docs" / "examples"
    pm.copy_examples(["packA"], target_dir=case5dir, force=force)
    actual = sorted((case5dir / "packA").rglob("*.py"))
    expected = sorted([case5dir / path for path in expected_paths])
    assert actual == expected
    for path in expected_paths:
        copied_path = case5dir / path
        original_path = examples_dir / path
        if copied_path.is_file() and original_path.is_file():
            assert copied_path.read_text() == original_path.read_text()


s = Styles()
install_params = [
    (  # input: packs to install
        # expected: output showing packA installed but not packB
        ("packA",),
        f"""{s.BOLD}{s.UNDER}{s.BLUE}Installed Packs:{s.RESET}
  packA

{s.BOLD}{s.UNDER}{s.BLUE}Available Packs:{s.RESET}
  packB

{s.BOLD}{s.UNDER}{s.CYAN}Examples:{s.RESET}
  {s.BOLD}packA:{s.RESET}
   - ex1
   - ex2
  {s.BOLD}packB:{s.RESET}
   - ex1
   - ex3
   - ex4""",
    ),
]


@pytest.mark.parametrize("packs_to_install,expected", install_params)
def test_print_packs_and_examples(
    packs_to_install, expected, example_cases, capsys, mocker
):
    case5dir = example_cases / "case5"
    req_dir = case5dir / "requirements" / "packs"

    installed_reqs = []
    for pack in packs_to_install:
        req_file = req_dir / f"{pack}.txt"
        for line in req_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                installed_reqs.append(line)

    def mock_is_installed(name: str) -> bool:
        return name in installed_reqs

    mocker.patch.object(
        installer, "_is_installed", side_effect=mock_is_installed
    )
    pm = PacksManager(root_path=case5dir)
    pm.print_packs()
    pm.print_examples()
    captured = capsys.readouterr()
    actual = captured.out
    assert actual.strip() == expected.strip()
