import runpy


def test_all_examples(tmp_examples):
    scripts = list(tmp_examples.rglob("**/solutions/diffpy-cmi/*.py"))
    for script_path in scripts:
        print(f"Testing {script_path.relative_to(tmp_examples)}")
        runpy.run_path(str(script_path), run_name="__main__")
