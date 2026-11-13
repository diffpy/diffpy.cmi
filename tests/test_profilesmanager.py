import pytest
import yaml

from diffpy.cmi.packsmanager import Styles
from diffpy.cmi.profilesmanager import ProfilesManager

s = Styles()
install_params = [
    (  # input: profiles to install
        # expected: print_profile output showing profileA
        # installed but not profileB
        ("profileA",),
        f"""{s.BOLD}{s.UNDER}{s.MAGENTA}Installed Profiles:{s.RESET}
  profileA

{s.BOLD}{s.UNDER}{s.MAGENTA}Available Profiles:{s.RESET}
  profileB
""",
    ),
]


@pytest.mark.parametrize("profiles_to_install,expected", install_params)
def test_print_profiles(
    profiles_to_install, expected, example_cases, capsys, mocker
):
    case5dir = example_cases / "case5"
    req_dir = case5dir / "requirements" / "profiles"

    installed_reqs = []
    for profile in profiles_to_install:
        req_file = req_dir / f"{profile}.yml"
        content = yaml.safe_load(req_file.read_text())
        for pack in content.get("packs", []):
            installed_reqs.append(pack)

    def fake_check_profile(identifier):
        return identifier == "profileA"

    mocker.patch.object(
        ProfilesManager, "check_profile", side_effect=fake_check_profile
    )
    pfm = ProfilesManager(root_path=case5dir)
    pfm.print_profiles()
    captured = capsys.readouterr()
    actual = captured.out
    assert actual.strip() == expected.strip()


@pytest.mark.parametrize(
    "script_exit_code, expected_install_exit_code",
    [
        # Test that installing a profile runs the scripts listed in its
        # extras with their arguments and reports whether they succeeded
        # C1: A user installs a profile whose script runs successfully.
        # Expected: The script runs with its argument and the
        # installation returns exit code 0.
        (0, 0),
        # C2: A user installs a profile whose script fails.
        # Expected: The script runs with its argument and the
        # installation returns exit code 1.
        (1, 1),
    ],
)
def test_install_with_script_extras(
    script_exit_code, expected_install_exit_code, tmp_path
):
    # Write a profile that lists the same script for Linux/macOS and Windows
    profiles_dir = tmp_path / "requirements" / "profiles"
    profiles_dir.mkdir(parents=True)
    (profiles_dir / "scripts-profile.yml").write_text(
        "packs: []\n"
        "\n"
        "extras:\n"
        "  - _write_message.sh hello\n"
        "  - _write_message.bat hello\n"
    )
    # Write scripts that save their argument to a file and exit with
    # script_exit_code
    scripts_dir = tmp_path / "requirements" / "packs" / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "_write_message.sh").write_text(
        'echo "$1" > script-output.txt\n' f"exit {script_exit_code}\n"
    )
    (scripts_dir / "_write_message.bat").write_text(
        "@echo off\n"
        "echo %1> script-output.txt\n"
        f"exit /b {script_exit_code}\n"
    )
    # Install the profile
    pfm = ProfilesManager(root_path=tmp_path)
    actual_install_exit_code = pfm.install("scripts-profile")
    actual_script_output = (
        (scripts_dir / "script-output.txt").read_text().strip()
    )
    expected_script_output = "hello"
    assert actual_install_exit_code == expected_install_exit_code
    assert actual_script_output == expected_script_output
