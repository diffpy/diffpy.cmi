import re
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent.parent / "docs" / "examples"
TESTS_DIR = Path(__file__).parent


def get_example_chapters():
    """Return a dict {chapter_name: Path} for all dirs in examples/."""
    return {d.name: d for d in EXAMPLES_DIR.iterdir() if d.is_dir()}


def get_test_chapters():
    """Return a set of real chapter names that have test files."""
    chapters = set()
    for test_file in TESTS_DIR.glob("test_ch*.py"):
        m = re.match(r"test_(ch\d+)\.py", test_file.name)
        if m:
            prefix = m.group(1)
            match = next(
                (
                    d.name
                    for d in EXAMPLES_DIR.iterdir()
                    if d.name.startswith(prefix)
                ),
                None,
            )
            if match:
                chapters.add(match)
    return chapters


def test_chapters_have_valid_names_and_tests():
    """Check that all example chapters are named properly and have
    tests."""
    example_chapters = get_example_chapters()
    test_chapters = get_test_chapters()
    errors = []
    # 1. Fail if any dir does not follow "ch" + number convention
    bad_names = [
        name for name in example_chapters if not re.match(r"^ch\d+", name)
    ]
    if bad_names:
        errors.append(
            "Invalid example chapter names (must match '^ch[0-9]+'): "
            + str(bad_names)
        )
    # 2. Fail if any example chapter has no corresponding test
    missing_tests = set(example_chapters) - test_chapters
    if missing_tests:
        errors.append(
            "Missing test files for chapters or bad test file name "
            "(must be named 'test_ch<NN>.py'): " + str(sorted(missing_tests))
        )
    assert not errors, "\n".join(errors)
