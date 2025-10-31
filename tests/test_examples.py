import runpy


def test_all_examples(tmp_examples):
    """Run all example scripts to ensure they execute without error."""
    scripts = list(tmp_examples.rglob("**/solutions/diffpy-cmi/*.py"))
    # sort list so that fitBulkNi.py runs first
    scripts.sort(key=lambda s: 0 if s.name == "fitBulkNi.py" else 1)
    for script in scripts:
        script_relative_path = script.relative_to(tmp_examples)
        print(f"Testing {script_relative_path}")
        runpy.run_path(str(script), run_name="__main__")
