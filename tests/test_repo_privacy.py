import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_output_directory_is_not_tracked():
    result = subprocess.run(
        ["git", "ls-files", "output"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == ""


def test_source_contains_only_generic_playlist_examples():
    exporter_source = (REPO_ROOT / "execution" / "excel_exporter.py").read_text(encoding="utf-8")
    assert "daisy_synths_to_check" not in exporter_source


def test_private_and_generated_artifacts_are_not_tracked():
    result = subprocess.run(
        [
            "git",
            "ls-files",
            "_agentic_promts",
            "CHECKPOINT.md",
            "PLAYLIST_INDEXER_BUGS.md",
            "playlist_indexer_BUGS",
            "REALTIME_COMPLETION_STATE.md",
            "playlist-navigator-pro.zip",
            "playlist-navigator-pro_green.zip",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == ""
