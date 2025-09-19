from helpers import run_all_scripts_for_given_example


def test_scripts(examples_tmpdir):
    run_all_scripts_for_given_example(examples_tmpdir, __file__)
