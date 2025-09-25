import pytest

from diffpy.cmi.cli import main


def test_cli_help(capsys):
    """Test that the CLI help message is displayed correctly."""
    with pytest.raises(SystemExit) as exc:
        main(["--help", "-h"])
    assert exc.value.code == 0
    out, _ = capsys.readouterr()
    assert "Welcome to diffpy.cmi" in out


def test_example_list(capsys):
    """Test that the example listing works."""
    rc = main(["example", "list"])
    assert rc == 0
    out, _ = capsys.readouterr()
    # test specific known pack and example
    assert "ch03NiModelling" in out
    assert "pdf" in out


def test_example_copy(monkeypatch, tmp_path):
    """Test that an example can be copied to the current directory."""
    # create a fake example
    fake_examples = tmp_path / "docs" / "examples"
    src = fake_examples / "pack1" / "ex1"
    src.mkdir(parents=True)
    monkeypatch.setattr(
        "diffpy.cmi.cli._installed_examples_dir",
        lambda: fake_examples,
    )
    cwd = tmp_path
    monkeypatch.chdir(cwd)
    rc = main(["example", "copy", "pdf/ch03NiModelling"])
    assert rc == 0
    assert (cwd / "ch03NiModelling").exists()
