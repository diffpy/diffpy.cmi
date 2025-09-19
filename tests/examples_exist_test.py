from conftest import TESTS_DIR


def test_example_dirs_have_tests(examples_tmpdir):
    """Verify that each example directory has a corresponding test
    file."""
    example_dirs = [d for d in examples_tmpdir.iterdir() if d.is_dir()]
    missing_tests = []
    for example_dir in example_dirs:
        # Test file expected in TESTS_DIR, named e.g. test_<example_dir>.py
        test_file = TESTS_DIR / f"test_{example_dir.name}.py"
        if not test_file.exists():
            missing_tests.append(example_dir.name)
    assert not missing_tests, (
        f"The following example dirs have no test file: {missing_tests}.",
        "Test file must be named test_<example_dir>.py.",
    )


def test_examples_tmpdir_exists(examples_tmpdir):
    """Ensure that the examples temporary directory has been created."""
    # Check the directory itself exists
    assert (
        examples_tmpdir.exists() and examples_tmpdir.is_dir()
    ), f"Temporary examples directory does not exist: {examples_tmpdir}"
