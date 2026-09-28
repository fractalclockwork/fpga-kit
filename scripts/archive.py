#!/usr/bin/env python3
"""Fetch and checksum the local documentation and SDK cache."""

import argparse
import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "archive" / "manifest.yaml"
STATUS = ROOT / "archive" / "cache" / "status.json"
SDK_IDS = ("ise-14.7-lin", "adept-runtime", "adept-utilities")


def load_manifest():
    data = yaml.safe_load(MANIFEST.read_text())
    return data.get("items") or []


def load_status():
    if STATUS.exists():
        return json.loads(STATUS.read_text())
    return {"items": {}}


def save_status(status):
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(json.dumps(status, indent=2) + "\n")


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def zip_members(path):
    if path.suffix.lower() != ".zip":
        return None
    import zipfile

    with zipfile.ZipFile(path) as archive:
        return archive.namelist()


def download(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "fpga-kit-archive"})
    with urllib.request.urlopen(request, timeout=120) as response:
        content_type = response.headers.get("Content-Type", "")
        payload = response.read()
    if "text/html" in content_type and not url.lower().endswith((".html", ".htm")):
        raise RuntimeError(f"URL returned HTML, not a file: {url}")
    dest.write_bytes(payload)


def record(status, item, path):
    members = zip_members(path)
    entry = {
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
        "retrieved": datetime.now(timezone.utc).isoformat(),
    }
    if members is not None:
        entry["zip_members"] = members
    status["items"][item["id"]] = entry
    return entry


def fetch_item(item, status):
    path = ROOT / item["path"]
    expected = (item.get("sha256") or "").strip()
    known = status["items"].get(item["id"], {}).get("sha256", "")
    check = expected or known
    if path.exists() and check and sha256_file(path) == check:
        print(f"skip {item['id']}", flush=True)
        return True
    if path.exists() and not check:
        record(status, item, path)
        print(f"hashed {item['id']}")
        return True
    if item.get("manual"):
        if path.exists():
            record(status, item, path)
            print(f"hashed {item['id']}")
            return True
        print(f"manual {item['id']}: place the file at {item['path']}", flush=True)
        return True
    try:
        download(item["url"], path)
    except Exception as exc:
        print(f"fail {item['id']}: {exc}", file=sys.stderr)
        return bool(item.get("optional"))
    entry = record(status, item, path)
    if expected and entry["sha256"] != expected:
        print(f"fail {item['id']}: sha256 mismatch", file=sys.stderr)
        return False
    print(f"fetched {item['id']}", flush=True)
    return True


def require_sdk():
    missing = []
    for item in load_manifest():
        if item["id"] in SDK_IDS and not (ROOT / item["path"]).is_file():
            missing.append(item["id"])
    if missing:
        print("missing SDK cache files: " + ", ".join(missing), file=sys.stderr)
        print("Drop them at the paths in archive/manifest.yaml and rerun.", file=sys.stderr)
        return 1
    return 0


def save_image():
    import subprocess

    item = next(row for row in load_manifest() if row["id"] == "ise-image")
    dest = ROOT / item["path"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["docker", "save", "-o", str(dest), "xilinx-ise-hil"], check=True)
    status = load_status()
    record(status, item, dest)
    save_status(status)
    print(f"saved {item['id']}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fill archive/cache from archive/manifest.yaml")
    parser.add_argument("--require-sdk", action="store_true")
    parser.add_argument("--save-image", action="store_true")
    args = parser.parse_args(argv)
    if args.require_sdk:
        return require_sdk()
    if args.save_image:
        return save_image()
    status = load_status()
    ok = True
    for item in load_manifest():
        if not fetch_item(item, status):
            ok = False
    save_status(status)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
