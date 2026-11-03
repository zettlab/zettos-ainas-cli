#!/usr/bin/env python3
"""Fail closed on accidental private implementation or credential publication."""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    rb"gh[pousr]_[A-Za-z0-9]{30,}",
    rb"github_pat_[A-Za-z0-9_]{30,}",
    rb"gitlab\.[A-Za-z0-9-]+\.com",
    rb"/ho" + rb"me/[A-Za-z0-9_-]+/",
]


def check():
    names = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    failures = []
    for name in filter(None, names):
        path = ROOT / name
        if path.suffix in (".rs", ".enc", ".zpk", ".zpk2") or path.name in ("Cargo.toml", "Cargo.lock", "accounts.json", ".encryption_key"):
            failures.append(name + ": private implementation/account file")
        if path.is_symlink():
            failures.append(name + ": symlinks are not allowed in the public repository")
            continue
        raw = path.read_bytes()
        if path.suffix in (".tar", ".gz", ".zip", ".exe") or b"\0" in raw:
            failures.append(name + ": binaries belong in reviewed Release assets")
        # The scanner contains pattern literals, not matching actual credentials.
        if any(re.search(pattern, raw) for pattern in PATTERNS):
            failures.append(name + ": private host/path or credential pattern")
    if failures:
        raise SystemExit("\n".join(failures))
    print("Public tree scan passed; review is still required before publishing.")


if __name__ == "__main__":
    check()
