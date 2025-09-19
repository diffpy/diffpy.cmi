import importlib.util
import os
from pathlib import Path


def load_module_from_path(path: Path):
    """Load a module given an absolute Path."""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_cmi_script(script_path: Path):
    """Run a script with a main() function."""
    old_cwd = os.getcwd()
    os.chdir(script_path.parent)
    try:
        module = load_module_from_path(script_path)
        module.main()
    finally:
        os.chdir(old_cwd)


def run_all_scripts_for_given_example(examples_tmpdir, test_file_path):
    """Run all Python scripts in the chapter corresponding to this test
    file.

    Only scripts that define a main() function will be executed.
    """
    chapter_dir_name = Path(test_file_path).stem.replace("test_", "")
    chapter_dir = examples_tmpdir / chapter_dir_name
    assert chapter_dir.exists(), f"Chapter dir does not exist: {chapter_dir}"

    # Recursively find all .py scripts
    scripts = list(chapter_dir.rglob("*.py"))
    for script_path in scripts:
        module = load_module_from_path(script_path)
        if hasattr(module, "main"):
            run_cmi_script(script_path)
        else:
            # automatically skip helper or non-example scripts
            print(f"Skipping file without main(): {script_path.name}")
