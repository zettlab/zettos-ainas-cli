#!/usr/bin/env python3
"""Produce a minimal local report without reading NAS data or credentials."""
import argparse
import json
import platform
import shutil
import subprocess


def version(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        return result.stdout.strip().splitlines()[0] if result.returncode == 0 and result.stdout.strip() else "unavailable"
    except (OSError, subprocess.SubprocessError):
        return "unavailable"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", default="znas")
    args = parser.parse_args()
    print(json.dumps({"os": platform.system(), "architecture": platform.machine(),
                      "python": platform.python_version(), "openssl": version(["openssl", "version"]),
                      "cli": version([args.binary, "--version"]) if shutil.which(args.binary) else "not found"}, indent=2))
