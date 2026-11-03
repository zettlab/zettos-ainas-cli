import argparse
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("installer", Path(__file__).resolve().parents[1] / "scripts/installer.py")
i = importlib.util.module_from_spec(spec)
spec.loader.exec_module(i)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "installation"
        self.platform = i.host_platform()
        self.args = argparse.Namespace(version="v0.1.7-beta.1", agent="custom", skills_dir=str(self.base / "skills"),
                                       bin_dir=str(self.base / "bin"), yes=True, purge_credentials=False)

    def payload(self, version):
        directory = self.root / "releases" / version
        directory.mkdir(parents=True)
        files = {"znas": f"#!/bin/sh\necho 'znas {version[1:]}'\n", "LICENSE": "test license",
                 "THIRD-PARTY-NOTICES.txt": "test notices"}
        files.update({f"skills/{s}/SKILL.md": version for s in i.SKILLS})
        for name, data in files.items():
            p = directory / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(data)
        (directory / "znas").chmod(0o755)
        manifest = {"version": version, "platform": self.platform,
                    "files": {name: hashlib.sha256(data.encode()).hexdigest() for name, data in files.items()}}
        (directory / "manifest.json").write_text(json.dumps(manifest))
        return directory

    def state(self):
        return json.loads((self.root / "state.json").read_text())

    def install_fixture(self):
        with i.installation_lock(self.root):
            self.payload(self.args.version)
            i.install(self.args, self.root, {})

    def test_install_upgrade_rollback_uninstall(self):
        self.install_fixture()
        first = self.args.version
        self.args.version = "v0.1.7-beta.2"
        self.payload(self.args.version)
        with i.installation_lock(self.root):
            i.install(self.args, self.root, self.state())
            self.assertEqual((self.base / "skills/znas-file/SKILL.md").read_text(), self.args.version)
            i.rollback(self.root, self.state())
            self.assertEqual((self.base / "skills/znas-file/SKILL.md").read_text(), first)
            output = subprocess.check_output([self.base / "bin/znas"], text=True).strip()
            self.assertEqual(output, "znas " + first[1:])
            i.uninstall(self.args, self.root, self.state())
        self.assertFalse((self.base / "bin/znas").is_symlink())
        self.assertFalse((self.root / "releases").exists())

    def test_install_refuses_existing_user_content(self):
        (self.base / "bin").mkdir()
        existing = self.base / "bin/znas"
        existing.write_text("user binary")
        with i.installation_lock(self.root):
            self.payload(self.args.version)
            with self.assertRaisesRegex(RuntimeError, "existing non-symlink"):
                i.install(self.args, self.root, {})
        self.assertEqual(existing.read_text(), "user binary")
        self.assertFalse((self.root / "current").exists())

    def test_failure_mid_transaction_restores_old_release(self):
        self.install_fixture()
        original = self.state()
        new = self.payload("v0.1.7-beta.2")
        real = i.atomic_json

        def interrupted(path, value):
            if path.name == "state.json" and value.get("current") == new.name:
                raise OSError("disk full")
            real(path, value)

        with patch.object(i, "atomic_json", side_effect=interrupted):
            with self.assertRaisesRegex(OSError, "disk full"):
                i.activate(self.root, original, new, [])
        self.assertEqual(self.state(), original)
        self.assertEqual((self.root / "current").resolve().name, original["current"])
        self.assertFalse((self.root / "transaction.json").exists())

    def test_next_run_recovers_interrupted_transaction(self):
        self.install_fixture()
        original = self.state()
        current = self.root / "current"
        old = os.readlink(current)
        new = self.payload("v0.1.7-beta.2")
        i.atomic_json(self.root / "transaction.json", {"state": original, "links": [
            {"path": str(current), "before": old, "after": str(new)}]})
        i.set_link(current, str(new))
        with i.installation_lock(self.root):
            self.assertEqual(os.readlink(current), old)
            self.assertEqual(self.state(), original)

    def test_archive_rejects_traversal_symlink_and_duplicate(self):
        for kind in ("traversal", "symlink", "duplicate"):
            with self.subTest(kind=kind):
                archive = self.base / (kind + ".tar.gz")
                with tarfile.open(archive, "w:gz") as tar:
                    member = tarfile.TarInfo("../escape" if kind == "traversal" else "file")
                    if kind == "symlink":
                        member.type, member.linkname = tarfile.SYMTYPE, "/tmp"
                    tar.addfile(member, io.BytesIO(b""))
                    if kind == "duplicate":
                        tar.addfile(member, io.BytesIO(b""))
                dest = self.base / kind
                dest.mkdir()
                with self.assertRaises(RuntimeError):
                    i.unpack(archive, dest)

    def test_payload_missing_skill_tampering_version_architecture(self):
        with i.installation_lock(self.root):
            directory = self.payload(self.args.version)
            i.validate_payload(directory, self.args.version, self.platform)
            for version, arch in (("v9.9.9", self.platform), (self.args.version, "other")):
                with self.assertRaises(RuntimeError):
                    i.validate_payload(directory, version, arch)
            skill = directory / "skills/znas-file/SKILL.md"
            skill.write_text("tampered")
            with self.assertRaises(RuntimeError):
                i.validate_payload(directory, self.args.version, self.platform)
            skill.unlink()
            with self.assertRaises(RuntimeError):
                i.validate_payload(directory, self.args.version, self.platform)

    def test_signature_and_checksum_fail_closed(self):
        key, public = self.base / "private.pem", self.base / "public.pem"
        subprocess.run(["openssl", "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-out", str(key)], check=True, capture_output=True)
        subprocess.run(["openssl", "pkey", "-in", str(key), "-pubout", "-out", str(public)], check=True, capture_output=True)
        asset = "znas-linux-x86_64.tar.gz"
        (self.base / asset).write_bytes(b"archive")
        checks = self.base / "SHA256SUMS"
        checks.write_text(i.sha256(self.base / asset) + "  " + asset + "\n")
        subprocess.run(["openssl", "dgst", "-sha256", "-sign", str(key), "-out", str(self.base / "SHA256SUMS.sig"), str(checks)], check=True)
        with patch.object(i, "PUBLIC_KEY", public.read_text()):
            i.verify_download(self.base, asset)
            (self.base / asset).write_bytes(b"corrupt")
            with self.assertRaisesRegex(RuntimeError, "checksum"):
                i.verify_download(self.base, asset)
            checks.write_text("forged")
            with self.assertRaisesRegex(RuntimeError, "signature"):
                i.verify_download(self.base, asset)

    def test_uninstall_preserves_externally_replaced_links(self):
        self.install_fixture()
        binary = self.base / "bin/znas"
        binary.unlink()
        binary.write_text("replacement")
        i.uninstall(self.args, self.root, self.state())
        self.assertEqual(binary.read_text(), "replacement")

    def test_refuses_nonempty_unmanaged_root(self):
        self.root.mkdir()
        (self.root / "personal-file").write_text("keep")
        with self.assertRaisesRegex(RuntimeError, "not empty"):
            with i.installation_lock(self.root):
                self.fail("unmanaged root was accepted")

    def test_lock_rejects_concurrent_installer(self):
        with i.installation_lock(self.root):
            with self.assertRaisesRegex(RuntimeError, "Another installation"):
                with i.installation_lock(self.root):
                    self.fail("concurrent installation accepted")


if __name__ == "__main__":
    unittest.main()
