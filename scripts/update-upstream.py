#!/usr/bin/env python3
"""Pin the manifest to the newest commit of deltaq471/musicdl.

Used by the daily GitHub Actions run, but works locally too:

    ./scripts/update-upstream.py           # rewrite the pin and commit
    ./scripts/update-upstream.py --check   # report only, never writes

The script only touches the archive url/sha256 pair of the app source. It
deliberately leaves <releases> in the metainfo alone, because upstream tags
are not semver ("release" is their only tag).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request

OWNER = "deltaq471"
REPO = "musicdl"
API = "https://api.github.com"
MANIFEST = "io.github.deltaq471.musicdl.json"

ARCHIVE = f"https://github.com/{OWNER}/{REPO}/archive"
URL_RE = re.compile(re.escape(ARCHIVE) + r"/([0-9a-f]{40})\.tar\.gz")
SHA_RE = re.compile(
    r"(" + re.escape(ARCHIVE) + r"/[0-9a-f]{40}\.tar\.gz\",\s*\n\s*\"sha256\": \")"
    r"[0-9a-f]{64}"
)


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def http_json(path: str):
    req = urllib.request.Request(
        API + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "musicdl-flatpak-updater",
        },
    )
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def latest_commit() -> str:
    """Newest commit on the repository's default branch."""
    data = http_json(f"/repos/{OWNER}/{REPO}/commits?per_page=1")
    if not isinstance(data, list) or not data:
        raise SystemExit(f"unexpected API response for {OWNER}/{REPO} commits")
    return data[0]["sha"]


def sha256_of(url: str) -> str:
    digest = hashlib.sha256()
    req = urllib.request.Request(url, headers={"User-Agent": "musicdl-flatpak-updater"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        for chunk in iter(lambda: resp.read(256 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def set_output(changed: bool, sha: str) -> None:
    out = os.environ.get("GITHUB_OUTPUT")
    if not out:
        return
    with open(out, "a", encoding="utf-8") as fh:
        fh.write(f"changed={'true' if changed else 'false'}\n")
        fh.write(f"sha={sha}\n")


def run(*cmd: str) -> None:
    subprocess.run(cmd, check=True)


def main() -> int:
    check_only = "--check" in sys.argv[1:]

    with open(MANIFEST, encoding="utf-8") as fh:
        text = fh.read()

    match = URL_RE.search(text)
    if not match:
        raise SystemExit(f"could not find a {OWNER}/{REPO} archive source in {MANIFEST}")
    pinned = match.group(1)

    upstream = latest_commit()
    log(f"pinned:   {pinned}")
    log(f"upstream: {upstream}")

    if pinned == upstream:
        log("up to date, nothing to do")
        set_output(False, pinned)
        return 0

    tarball = f"{ARCHIVE}/{upstream}.tar.gz"
    log(f"hashing {tarball}")
    digest = sha256_of(tarball)

    text = text.replace(match.group(0), f"{ARCHIVE}/{upstream}.tar.gz")
    text, count = SHA_RE.subn(lambda m: m.group(1) + digest, text)
    if count != 1:
        raise SystemExit(f"expected exactly one sha256 to update, patched {count}")

    log(f"new sha256: {digest}")

    if check_only:
        log("--check given, not writing")
        return 0

    with open(MANIFEST, "w", encoding="utf-8") as fh:
        fh.write(text)

    # Only commit when this is a git checkout (CI is, a tarball is not).
    if subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True).returncode == 0:
        run("git", "add", MANIFEST)
        run("git", "commit", "-m", f"Update musicdl source to {upstream[:7]}")
        run("git", "push")
    else:
        log("not a git checkout, left the change in the working tree")

    set_output(True, upstream)
    return 0


if __name__ == "__main__":
    sys.exit(main())
