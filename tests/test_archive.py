import archive


def test_file_url_is_cached(tmp_path, monkeypatch):
    source = tmp_path / "manual.pdf"
    source.write_bytes(b"%PDF-1.1\n")
    dest = tmp_path / "cache" / "manual.pdf"
    item = {
        "id": "sample-doc",
        "url": source.as_uri(),
        "path": str(dest),
        "sha256": "",
        "manual": False,
    }
    monkeypatch.setattr(archive, "ROOT", tmp_path)
    # fetch_item joins ROOT / item["path"]. Use a relative path.
    item["path"] = "cache/manual.pdf"
    status = {"items": {}}
    assert archive.fetch_item(item, status)
    assert (tmp_path / "cache" / "manual.pdf").read_bytes().startswith(b"%PDF")
    assert status["items"]["sample-doc"]["bytes"] > 0
