#!/usr/bin/env python3
"""Native-platform smoke verification of downloaded, signed release assets."""
import argparse
import datetime
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from unittest.mock import patch

import installer


def verify(directory, version, report):
    platform = installer.host_platform()
    asset = f"znas-{platform}.tar.gz"
    directory = directory.resolve()
    with tempfile.TemporaryDirectory(prefix="znas-native-release-") as temporary:
        root = Path(temporary)
        args = argparse.Namespace(version=version, agent="custom", skills_dir=str(root / "skills"),
                                  bin_dir=str(root / "bin"), yes=True, purge_credentials=False)

        def downloaded_asset(url, destination, limit):
            name = url.rsplit("/", 1)[-1]
            if name not in (asset, "SHA256SUMS", "SHA256SUMS.sig"):
                raise RuntimeError("Unexpected installer download")
            shutil.copyfile(directory / name, destination)

        # Only transport is replaced; signature, digest, extraction, binary execution,
        # transactions and uninstall are the production implementation.
        with patch.object(installer, "fetch", side_effect=downloaded_asset):
            with installer.installation_lock(root / "installation"):
                installer.install(args, root / "installation", {})
                binary = root / "bin/znas"
                for domain in ("file", "settings", "app-store", "docker", "photos", "theater"):
                    output = subprocess.check_output([str(binary), "schema", domain], text=True, timeout=20)
                    json.loads(output)
                blocked = subprocess.run([str(binary), "settings", "system", "restart"], capture_output=True, text=True, timeout=20)
                if blocked.returncode == 0 or "No request was sent" not in blocked.stderr:
                    raise RuntimeError("Destructive operation was not blocked before network access")
                state = json.loads((root / "installation/state.json").read_text())
                installer.install(args, root / "installation", state)
                installer.uninstall(args, root / "installation", state)
        if (root / "bin/znas").is_symlink():
            raise RuntimeError("Uninstall left a managed binary link")
    evidence = {"version": version, "platform": platform, "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "asset_sha256": installer.sha256(directory / asset), "status": "passed",
                "checks": ["release signature", "archive checksum", "payload manifest", "binary version",
                           "six domain schemas", "destructive command rejection", "install", "repeat install", "uninstall"],
                "scope": "Native binary and installer only; does not establish NAS or older-OS compatibility."}
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(evidence, indent=2) + "\n")
    print("Native signed release smoke passed: " + platform)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    verify(args.directory, args.version, args.report)
