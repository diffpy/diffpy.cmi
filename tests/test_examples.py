import re
import runpy


def get_instrument_params(res_file):
    """Parse Qdamp and Qbroad from a .res file."""
    qdamp = qbroad = None
    with open(res_file, "r") as f:
        for line in f:
            if line.startswith("Calib_Qbroad"):
                qbroad = float(re.split(r"\s+", line.strip())[1])
            elif line.startswith("Calib_Qdamp"):
                qdamp = float(re.split(r"\s+", line.strip())[1])
    return qdamp, qbroad


def test_all_examples(tmp_examples):
    """Run all example scripts to ensure they execute without error."""
    # Run Ni example first to produce .res file
    ni_script = list(tmp_examples.rglob("**/FitBulkNi.py"))[0]
    runpy.run_path(str(ni_script), run_name="__main__")
    res_file = ni_script.parent / "res" / "Fit_Ni_Bulk.res"
    assert res_file.exists(), f"Ni results file not found: {res_file}"

    qdamp_i, qbroad_i = get_instrument_params(res_file)
    pt_script = list(tmp_examples.rglob("**/fitNPPt.py"))[0]
    refined_Ni_params = {"QDAMP_I": qdamp_i, "QBROAD_I": qbroad_i}
    # run the NPPt script with the refined Ni params
    runpy.run_path(
        str(pt_script), run_name="__main__", init_globals=refined_Ni_params
    )

    # Run all other example scripts, patching the instrument values
    all_scripts = list(tmp_examples.rglob("**/solutions/diffpy-cmi/*.py"))
    scripts = [
        s for s in all_scripts if s.name not in ("fitBulkNi.py", "fitNPPt.py")
    ]
    for script_path in scripts:
        print(f"Testing {script_path.relative_to(tmp_examples)}")
        mod_globals = {"QDAMP_I": qdamp_i, "QBROAD_I": qbroad_i}
        runpy.run_path(
            str(script_path), run_name="__main__", init_globals=mod_globals
        )
