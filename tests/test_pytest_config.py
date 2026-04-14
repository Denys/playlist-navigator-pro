from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_pytest_ini_disables_cacheprovider_without_pinning_basetemp():
    config_path = REPO_ROOT / "pytest.ini"
    assert config_path.exists()

    source = config_path.read_text(encoding="utf-8")
    assert "testpaths = tests" in source
    assert "-p no:cacheprovider" in source
    assert "--basetemp=" not in source
