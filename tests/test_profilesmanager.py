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
