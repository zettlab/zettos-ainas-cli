import importlib.util
import json
from pathlib import Path
import struct
import tarfile
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("package_release", Path(__file__).resolve().parents[1] / "scripts/package_release.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.addCleanup(patch.stopall)
        patch.object(p, "ROOT", self.root).start()
        for name in ("LICENSE", "TOOLING-LICENSE"):
            (self.root / name).write_text("test license\n")
        for skill in p.SKILLS:
            directory = self.root / "skills" / ("znas-" + skill)
            directory.mkdir(parents=True)
            (directory / "SKILL.md").write_text("test skill\n")
        self.binary = self.root / "znas"
        header = bytearray(64)
        header[:6] = b"\x7fELF\x02\x01"
        struct.pack_into("<H", header, 18, 62)
        self.binary.write_bytes(header)
        self.notices = self.root / "THIRD-PARTY-NOTICES.txt"
        self.notices.write_text("test license notice\n" * 10)
        (self.root / "dependency-inventory.json").write_text("[]")
        (self.root / "rust-runtime-notices").mkdir()
        (self.root / "rust-runtime-notices/COPYRIGHT-library.html").write_text("test runtime notices")

    def test_deterministic_archive_includes_all_skills_and_licenses(self):
        a = p.package(self.binary, "v1.0.0", "linux-x86_64", self.notices, self.root / "a")
        b = p.package(self.binary, "v1.0.0", "linux-x86_64", self.notices, self.root / "b")
        self.assertEqual(a.read_bytes(), b.read_bytes())
        with tarfile.open(a) as tar:
            manifest = json.load(tar.extractfile("manifest.json"))
            self.assertIn("TOOLING-LICENSE", manifest["files"])
            for skill in p.SKILLS:
                self.assertIn(f"skills/znas-{skill}/SKILL.md", manifest["files"])
        with self.assertRaisesRegex(ValueError, "overwrite"):
            p.package(self.binary, "v1.0.0", "linux-x86_64", self.notices, self.root / "a")

    def test_wrong_architecture_missing_skill_and_missing_mpl_source_fail(self):
        with self.assertRaisesRegex(ValueError, "architecture"):
            p.package(self.binary, "v1.0.0", "linux-aarch64", self.notices, self.root / "bad")
        (self.root / "dependency-inventory.json").write_text(json.dumps([
            {"name": "example", "version": "1.0.0", "license": "MPL-2.0"}]))
        with self.assertRaises(FileNotFoundError):
            p.package(self.binary, "v1.0.0", "linux-x86_64", self.notices, self.root / "bad")
        (self.root / "dependency-inventory.json").write_text("[]")
        (self.root / "skills/znas-file/SKILL.md").unlink()
        with self.assertRaisesRegex(ValueError, "Missing skill"):
            p.package(self.binary, "v1.0.0", "linux-x86_64", self.notices, self.root / "bad")

    def test_complete_release_signing_refuses_incomplete_platform_set(self):
        directory = self.root / "candidate"
        p.package(self.binary, "v1.0.0", "linux-x86_64", self.notices, directory)
        with self.assertRaisesRegex(ValueError, "three platform"):
            p.sign(directory, self.root / "nonexistent-private-key")


if __name__ == "__main__":
    unittest.main()
