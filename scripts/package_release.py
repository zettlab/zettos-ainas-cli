#!/usr/bin/env python3
"""Package an already built binary; this repository never needs Rust source."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import struct
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("shared", "file", "settings", "app-store", "docker", "photos", "coder", "theater", "desktop-shell")


def binary_platform(binary):
    header = binary.read_bytes()[:64]
    if header[:4] == b"\x7fELF" and header[4:6] == b"\x02\x01":
        arch = {62: "x86_64", 183: "aarch64"}.get(struct.unpack_from("<H", header, 18)[0])
        if arch:
            return "linux-" + arch
    if header[:4] == b"\xcf\xfa\xed\xfe" and struct.unpack_from("<I", header, 4)[0] == 0x0100000C:
        return "macos-aarch64"
    raise ValueError("Unsupported binary format or architecture")


def package(binary, version, target, notices, output):
    if not re.fullmatch(r"v\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?", version):
        raise ValueError("Invalid version")
    if binary_platform(binary) != target:
        raise ValueError("Binary architecture does not match release asset")
    files = {"znas": binary.read_bytes(), "LICENSE": (ROOT / "LICENSE").read_bytes(),
             "TOOLING-LICENSE": (ROOT / "TOOLING-LICENSE").read_bytes(),
             "THIRD-PARTY-NOTICES.txt": notices.read_bytes()}
    if len(files["THIRD-PARTY-NOTICES.txt"]) < 100:
        raise ValueError("Third-party license notices are missing or empty")
    inventory_path = notices.parent / "dependency-inventory.json"
    inventory = json.loads(inventory_path.read_text())
    files["dependency-inventory.json"] = inventory_path.read_bytes()
    for dependency in inventory:
        if dependency.get("license") == "MPL-2.0":
            name = dependency["name"] + "-" + dependency["version"] + ".crate"
            content = (notices.parent / "third-party-sources" / name).read_bytes()
            if hashlib.sha256(content).hexdigest() != dependency.get("bundled_source_sha256"):
                raise ValueError("Required MPL source archive checksum mismatch")
            files["third-party-sources/" + name] = content
    for skill in SKILLS:
        directory = ROOT / "skills" / ("znas-" + skill)
        if not (directory / "SKILL.md").is_file():
            raise ValueError("Missing skill " + skill)
        for path in sorted(directory.rglob("*")):
            if path.is_symlink():
                raise ValueError("Symlinks are forbidden in distributed skills")
            if path.is_file():
                if path.suffix != ".md":
                    raise ValueError("Unexpected skill resource; review before shipping: " + str(path))
                files[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    manifest = {"version": version, "platform": target,
                "files": {name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())}}
    files["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    output.mkdir(parents=True, exist_ok=True)
    dest = output / f"znas-{target}.tar.gz"
    if dest.exists():
        raise ValueError("Refusing to overwrite a release asset: " + str(dest))
    with dest.open("xb") as out, gzip.GzipFile(filename="", fileobj=out, mode="wb", mtime=0) as zipped:
        with tarfile.open(fileobj=zipped, mode="w") as archive:
            for name, data in sorted(files.items()):
                member = tarfile.TarInfo(name)
                member.size, member.mtime = len(data), 0
                member.mode = 0o755 if name == "znas" else 0o644
                archive.addfile(member, io.BytesIO(data))
    return dest


def sign(directory, private_key):
    assets = sorted(directory.glob("znas-*.tar.gz"))
    if len(assets) != 3:
        raise ValueError("All three platform archives are required before signing")
    expected = {f"znas-{p}.tar.gz" for p in ("linux-x86_64", "linux-aarch64", "macos-aarch64")}
    if {p.name for p in assets} != expected:
        raise ValueError("Unexpected release asset names")
    public = subprocess.check_output(["openssl", "pkey", "-in", str(private_key), "-pubout"])
    if public.strip() != (ROOT / "release-signing-public.pem").read_bytes().strip():
        raise ValueError("Signing key does not match pinned public key")
    checksums = directory / "SHA256SUMS"
    checksums.write_text("".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  " + p.name + "\n" for p in assets))
    subprocess.run(["openssl", "dgst", "-sha256", "-sign", str(private_key), "-out",
                    str(directory / "SHA256SUMS.sig"), str(checksums)], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("package")
    build.add_argument("--binary", type=Path, required=True)
    build.add_argument("--version", required=True)
    build.add_argument("--platform", choices=("linux-x86_64", "linux-aarch64", "macos-aarch64"), required=True)
    build.add_argument("--notices", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    signing = sub.add_parser("sign")
    signing.add_argument("--directory", type=Path, required=True)
    signing.add_argument("--private-key", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "package":
        print(package(args.binary, args.version, args.platform, args.notices, args.output))
    else:
        sign(args.directory, args.private_key)
