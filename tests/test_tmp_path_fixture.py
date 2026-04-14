def test_tmp_path_fixture_is_writable(tmp_path):
    probe = tmp_path / "probe.txt"
    probe.write_text("ok", encoding="utf-8")
    assert probe.read_text(encoding="utf-8") == "ok"
