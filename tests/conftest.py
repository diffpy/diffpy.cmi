import json
from pathlib import Path

import matplotlib
import pytest


@pytest.fixture(scope="function")
def example_cases(tmp_path_factory):
    """Copy the entire examples tree into a temp directory once per test
    session.

    Returns the path to that copy.
    """
    root_temp_dir = tmp_path_factory.mktemp("temp")
    cwd = root_temp_dir / "cwd"
    cwd.mkdir(parents=True, exist_ok=True)
    existing_dir = cwd / "existing_target"
    existing_dir.mkdir(parents=True, exist_ok=True)

    # case 1: pack with no examples
    case1ex_dir = root_temp_dir / "case1" / "docs" / "examples"
    case1 = case1ex_dir / "empty_pack"  # empty_pack
    case1.mkdir(parents=True, exist_ok=True)
    case1req_dir = root_temp_dir / "case1" / "requirements" / "packs"
    case1req_dir.mkdir(parents=True, exist_ok=True)

    # Case 2: pack with multiple examples
    case2ex_dir = root_temp_dir / "case2" / "docs" / "examples"
    case2a = (
        case2ex_dir / "full_pack" / "ex1" / "solution" / "diffpy-cmi"
    )  # full_pack, ex1
    case2a.mkdir(parents=True, exist_ok=True)
    (case2a / "script1.py").write_text(f"# {case2a.name} script1\n")

    case2b = (
        case2ex_dir / "full_pack" / "ex2" / "random" / "path"
    )  # full_pack, ex2
    case2b.mkdir(parents=True, exist_ok=True)
    (case2b / "script1.py").write_text(f"# {case2b.name} script1\n")
    (case2b / "script2.py").write_text(f"# {case2b.name} script2\n")

    case2req_dir = root_temp_dir / "case2" / "requirements" / "packs"
    case2req_dir.mkdir(parents=True, exist_ok=True)

    # Case 3: multiple packs with multiple examples
    case3ex_dir = root_temp_dir / "case3" / "docs" / "examples"
    case3a = case3ex_dir / "packA" / "ex1"  # packA, ex1
    case3a.mkdir(parents=True, exist_ok=True)
    (case3a / "script1.py").write_text(f"# {case3a.name} script1\n")

    case3b = case3ex_dir / "packA" / "ex2" / "solutions"  # packA, ex2
    case3b.mkdir(parents=True, exist_ok=True)
    (case3b / "script2.py").write_text(f"# {case3b.name} script2\n")

    case3c = (
        case3ex_dir / "packB" / "ex3" / "more" / "random" / "path"
    )  # packB, ex3
    case3c.mkdir(parents=True, exist_ok=True)
    (case3c / "script3.py").write_text(f"# {case3c.name} script3\n")
    (case3c / "script4.py").write_text(f"# {case3c.name} script4\n")

    case3req_dir = root_temp_dir / "case3" / "requirements" / "packs"
    case3req_dir.mkdir(parents=True, exist_ok=True)

    # Case 4: no pack found (empty directory)
    case4ex_dir = root_temp_dir / "case4" / "docs" / "examples"
    case4 = case4ex_dir
    case4.mkdir(parents=True, exist_ok=True)
    case4req_dir = root_temp_dir / "case4" / "requirements" / "packs"
    case4req_dir.mkdir(parents=True, exist_ok=True)

    # Case 5: multiple packs with the same example names
    case5ex_dir = root_temp_dir / "case5" / "docs" / "examples"

    case5a = case5ex_dir / "packA" / "ex1" / "path1"  # packA, ex1
    case5a.mkdir(parents=True, exist_ok=True)
    (case5a / "script1.py").write_text(f"# {case5a.name} script1\n")

    case5b = case5ex_dir / "packB" / "ex1" / "path2"  # packB, ex1
    case5b.mkdir(parents=True, exist_ok=True)
    (case5b / "script2.py").write_text(f"# {case5b.name} script2\n")

    case5c = case5ex_dir / "packA" / "ex2"  # packA, ex2
    case5c.mkdir(parents=True, exist_ok=True)
    (case5c / "script3.py").write_text(f"# {case5c.name} script3\n")

    case5d = case5ex_dir / "packB" / "ex3"
    case5d.mkdir(parents=True, exist_ok=True)
    (case5d / "script4.py").write_text(f"# {case5d.name} script4\n")

    case5e = case5ex_dir / "packB" / "ex4"
    case5e.mkdir(parents=True, exist_ok=True)
    (case5e / "script5.py").write_text(f"# {case5e.name} script5\n")

    case5reqs_dir = root_temp_dir / "case5" / "requirements"
    case5packs_dir = case5reqs_dir / "packs"
    case5packs_dir.mkdir(parents=True, exist_ok=True)
    (case5packs_dir / "packA.txt").write_text("requests")
    (case5packs_dir / "packB.txt").write_text("attrs")

    case5profiles_dir = case5reqs_dir / "profiles"
    case5profiles_dir.mkdir(parents=True, exist_ok=True)
    profileAyml = """\
packs:
- packA

extras:
- ipykernel
    """
    profileByml = """\
packs:
- packB

extras:
- notebook
    """
    (case5profiles_dir / "profileA.yml").write_text(profileAyml)
    (case5profiles_dir / "profileB.yml").write_text(profileByml)

    yield root_temp_dir


@pytest.fixture(scope="session", autouse=True)
def use_headless_matplotlib():
    """Force matplotlib to use a headless backend during tests."""
    matplotlib.use("Agg")


@pytest.fixture
def user_filesystem(tmp_path):
    base_dir = Path(tmp_path)
    home_dir = base_dir / "home_dir"
    home_dir.mkdir(parents=True, exist_ok=True)
    cwd_dir = base_dir / "cwd_dir"
    cwd_dir.mkdir(parents=True, exist_ok=True)

    home_config_data = {"username": "home_username", "email": "home@email.com"}
    with open(home_dir / "diffpyconfig.json", "w") as f:
        json.dump(home_config_data, f)

    yield tmp_path
