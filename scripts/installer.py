#!/usr/bin/env python3
"""Signed, versioned user installation. Python standard library only; POSIX hosts."""
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

REPOSITORY = "zettlab/zettos-ainas-cli"
PUBLIC_KEY = '-----BEGIN PUBLIC KEY-----\nMIIBojANBgkqhkiG9w0BAQEFAAOCAY8AMIIBigKCAYEAsAd5E+NSteQwBHdkJ6C1\nll9fRqK9eeLzyGYIDdU/AaQ3U7QsijWQmjEJ9mTM3yBFu/IZgaqB9udjzKnPkwJh\n6VLgSQuNtaTFMHU0/PlEpmaTrvxGkIVfTHeR3oeATpLoxrQa6K3XEFfXskR+hK5v\ndduprwlBrTju2HOsu2vLrJC6Tu8401aBgUisfVbeoPpye6kq4g4LoWb0fEngthE4\ndAjU6gzUZGGdZA3+sDvFUnoeaoAT5X2kMmg28LIdvHHhqnMNSQN9JqvtAAeIIO5f\nD9VhJwnYotTPYcbwgaLpyQogXhab2U5yVTS+9k6NGZGEcHo2qEoUG6JE9A2pm0AB\nEq7UwZy9Rtjf7obHHVK/Jm80U9LNWWhWLv/KmkZhJaO2F/ZTgf6MLT3P1qH4I/6T\n1WriLDdT2CcdLB4v0y3DnvsaOpeopQvzAVlp2O5zpxXB6/3HEjU+w8jdD9L3YIXq\nBAVy5CI/aWMTXygocSSsfO6bDwV/4tHnix5RCaVRs4kXAgMBAAE=\n-----END PUBLIC KEY-----\n'
SKILLS = ["znas-" + name for name in (
    "shared", "file", "settings", "app-store", "docker", "photos",
    "coder", "theater", "desktop-shell")]
VERSION = re.compile(r"v[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?\Z")
MAX_ARCHIVE = 256 * 1024 * 1024
MAX_EXPANDED = 512 * 1024 * 1024


def fail(message):
    raise RuntimeError(message)


class HTTPSRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not newurl.startswith("https://"):
            fail("Refusing a non-HTTPS redirect")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url, destination, limit=MAX_ARCHIVE):
    if not url.startswith("https://"):
        fail("Release downloads require HTTPS")
    opener = urllib.request.build_opener(HTTPSRedirect())
    req = urllib.request.Request(url, headers={"User-Agent": "zettos-ainas-cli-installer"})
    with opener.open(req, timeout=60) as response, destination.open("wb") as out:
        total = 0
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > limit:
                fail("Download exceeds size limit")
            out.write(chunk)


def resolve_version(value):
    if value == "latest":
        opener = urllib.request.build_opener(HTTPSRedirect())
        with opener.open(f"https://github.com/{REPOSITORY}/releases/latest", timeout=30) as r:
            value = r.url.rsplit("/", 1)[-1]
    if not VERSION.fullmatch(value):
        fail("Specify a release version such as v0.1.7-beta.1; latest needs a stable release")
    return value


def host_platform():
    system = {"Linux": "linux", "Darwin": "macos"}.get(platform.system())
    arch = {"x86_64": "x86_64", "AMD64": "x86_64", "aarch64": "aarch64", "arm64": "aarch64"}.get(platform.machine())
    value = f"{system}-{arch}"
    if value not in ("linux-x86_64", "linux-aarch64", "macos-aarch64"):
        fail("Supported: Linux x86_64/ARM64 and macOS Apple Silicon. Windows and Intel Mac are not supported.")
    return value


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_download(directory, asset):
    key = directory / "release-signing-public.pem"
    key.write_text(PUBLIC_KEY)
    result = subprocess.run([
        "openssl", "dgst", "-sha256", "-verify", str(key),
        "-signature", str(directory / "SHA256SUMS.sig"), str(directory / "SHA256SUMS")
    ], capture_output=True)
    if result.returncode:
        fail("Release signature verification failed; nothing installed")
    entries = {}
    for line in (directory / "SHA256SUMS").read_text().splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9._-]+)", line)
        if not match or match[2] in entries:
            fail("Invalid or duplicate checksum entry")
        entries[match[2]] = match[1]
    if entries.get(asset) != sha256(directory / asset):
        fail("Archive checksum mismatch; nothing installed")


def unpack(archive, destination):
    # Do not use extractall: links, device nodes, traversal and duplicates are forbidden.
    seen, total = set(), 0
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar:
            path = PurePosixPath(member.name)
            if (path.is_absolute() or ".." in path.parts or "\\" in member.name
                    or member.name in seen or not path.parts or len(seen) >= 10000):
                fail("Unsafe archive path or duplicate member")
            seen.add(member.name)
            target = destination.joinpath(*path.parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            if not member.isfile():
                fail("Archive must contain only regular files and directories")
            total += member.size
            if total > MAX_EXPANDED:
                fail("Expanded release exceeds size limit")
            target.parent.mkdir(parents=True, exist_ok=True)
            with tar.extractfile(member) as source, target.open("xb") as out:
                shutil.copyfileobj(source, out)
            target.chmod(0o755 if member.name == "znas" else 0o644)


def validate_payload(directory, version, target_platform, run_binary=True):
    manifest = json.loads((directory / "manifest.json").read_text())
    if manifest.get("version") != version or manifest.get("platform") != target_platform:
        fail("Release version or platform does not match the requested asset")
    expected = manifest.get("files", {})
    required = {"znas", "LICENSE", "THIRD-PARTY-NOTICES.txt"} | {
        f"skills/{skill}/SKILL.md" for skill in SKILLS}
    if not required.issubset(expected):
        fail("Incomplete release: binary, skills or license notices missing")
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    if actual != set(expected) | {"manifest.json"}:
        fail("Release manifest does not match packaged files")
    for name, digest in expected.items():
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "\\" in name:
            fail("Unsafe manifest path")
        file = directory / name
        if file.is_symlink() or sha256(file) != digest:
            fail("Release content validation failed: " + name)
    if run_binary:
        result = subprocess.run([str(directory / "znas"), "--version"], capture_output=True, text=True, timeout=20)
        if result.returncode or result.stdout.strip() != "znas " + version[1:]:
            fail("Binary failed its version preflight. Check minimum OS/libc requirements.")
    return manifest


def atomic_json(path, value):
    temp = path.with_name(path.name + ".tmp")
    with temp.open("w") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def link_value(path):
    if path.is_symlink():
        return os.readlink(path)
    if path.exists():
        fail(f"Refusing to replace an existing non-symlink: {path}. Move it aside first.")
    return None


def set_link(path, target):
    if target is None:
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".znas-tmp")
    if temp.exists() or temp.is_symlink():
        fail(f"Temporary link already exists: {temp}")
    temp.symlink_to(target)
    os.replace(temp, path)


def recover(root):
    journal = root / "transaction.json"
    if not journal.exists():
        return
    tx = json.loads(journal.read_text())
    for item in reversed(tx["links"]):
        path = Path(item["path"])
        current = link_value(path)
        if current not in (item["before"], item["after"]):
            fail(f"Recovery stopped: {path} was modified outside this installer")
        set_link(path, item["before"])
    atomic_json(root / "state.json", tx["state"])
    journal.unlink()


def activate(root, state, release, bindings):
    operations = []
    for path, target in bindings + [(root / "current", str(release))]:
        before = link_value(path)
        owned = {item["path"]: item["target"] for item in state.get("bindings", [])}
        if path != root / "current" and before is not None and owned.get(str(path)) != before:
            fail(f"Refusing to replace an unmanaged link: {path}")
        operations.append({"path": str(path), "before": before, "after": target})
    next_state = dict(state)
    old = state.get("current")
    next_state.update(current=release.name, previous=old if old != release.name else state.get("previous"))
    merged = {item["path"]: item["target"] for item in state.get("bindings", [])}
    merged.update({str(p): t for p, t in bindings})
    next_state["bindings"] = [{"path": p, "target": t} for p, t in merged.items()]
    atomic_json(root / "transaction.json", {"state": state, "links": operations})
    try:
        for item in operations:
            set_link(Path(item["path"]), item["after"])
        atomic_json(root / "state.json", next_state)
        (root / "transaction.json").unlink()
    except BaseException:
        recover(root)
        raise


@contextlib.contextmanager
def installation_lock(root):
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    marker = root / ".znas-installation"
    if not marker.exists():
        if any(root.iterdir()):
            fail("Installation root is not empty and is not managed by this installer")
        marker.write_text("zettos-ainas-cli\n")
    if marker.is_symlink() or marker.read_text() != "zettos-ainas-cli\n":
        fail("Invalid installation root marker")
    for name in ("releases", "state.json", "transaction.json", ".lock"):
        if (root / name).is_symlink():
            fail("Installation metadata must not be symlinks")
    with (root / ".lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            fail("Another installation is running")
        recover(root)
        yield


def install(args, root, state):
    version, target_platform = resolve_version(args.version), host_platform()
    asset = f"znas-{target_platform}.tar.gz"
    release = root / "releases" / version
    if not release.exists():
        (root / "releases").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".download-", dir=root) as temp:
            temp = Path(temp)
            base = f"https://github.com/{REPOSITORY}/releases/download/{version}"
            for name in ("SHA256SUMS", "SHA256SUMS.sig", asset):
                fetch(f"{base}/{name}", temp / name, MAX_ARCHIVE if name == asset else 1024 * 1024)
            verify_download(temp, asset)
            payload = temp / "payload"
            payload.mkdir()
            unpack(temp / asset, payload)
            validate_payload(payload, version, target_platform)
            os.replace(payload, release)
    else:
        validate_payload(release, version, target_platform)
    bindings = [(Path(args.bin_dir).expanduser().absolute() / "znas", str(root / "current/znas"))]
    if args.agent != "none":
        defaults = {"codex": "~/.codex/skills", "claudecode": "~/.claude/skills", "openclaw": "~/.agents/skills"}
        selected = args.skills_dir or defaults.get(args.agent)
        if not selected:
            fail("--agent custom requires --skills-dir")
        skills_dir = Path(selected).expanduser().absolute()
        bindings.extend((skills_dir / skill, str(root / "current/skills" / skill)) for skill in SKILLS)
    activate(root, state, release, bindings)
    print(f"Installed {version} ({target_platform})")
    print(f"Binary: {bindings[0][0]}")
    print("Keep this installer to update, rollback or uninstall. See docs/INSTALL.md.")
    if str(bindings[0][0].parent) not in os.get_exec_path():
        print(f"Add {bindings[0][0].parent} to PATH in your shell configuration.")


def rollback(root, state):
    version = state.get("previous")
    if not version or not VERSION.fullmatch(version):
        fail("No previous installed version is available")
    release = root / "releases" / version
    validate_payload(release, version, host_platform())
    activate(root, state, release, [])
    print("Rolled back binary and all linked skills to " + version)


def uninstall(args, root, state):
    if not args.yes:
        fail("Uninstall requires --yes. Credentials are kept unless --purge-credentials is also specified.")
    if args.purge_credentials:
        # Logout uses the CLI's own account registry and does not expose tokens.
        binary = root / "current/znas"
        if not binary.exists():
            fail("Credential cleanup requires an installed binary; run znas auth logout --all first")
        subprocess.run([str(binary), "auth", "logout", "--all"], check=True, timeout=30)
        configured = os.environ.get("ZETTOS_NAS_CLI_CONFIG_DIR")
        default = (Path.home() / "Library/Application Support/znas" if platform.system() == "Darwin"
                   else Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "znas")
        config = Path(configured) if configured else default
        for name in (".encryption_key", "accounts.json"):
            (config / name).unlink(missing_ok=True)
        print("Saved CLI accounts removed. Environment credentials and external files are unaffected.")
    for item in state.get("bindings", []):
        path = Path(item["path"])
        if path.is_symlink() and os.readlink(path) == item["target"]:
            path.unlink()
        elif path.exists() or path.is_symlink():
            print(f"Preserved externally modified path: {path}")
    for name in ("current", "state.json"):
        (root / name).unlink(missing_ok=True)
    if (root / "releases").exists():
        shutil.rmtree(root / "releases")
    print("Uninstalled binary and managed skills. " + ("Credentials removed." if args.purge_credentials else "Credentials retained."))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("install", "rollback", "uninstall", "status"), nargs="?", default="install")
    parser.add_argument("--version", default="latest")
    parser.add_argument("--agent", choices=("codex", "claudecode", "openclaw", "custom", "none"), default="none")
    parser.add_argument("--skills-dir")
    parser.add_argument("--bin-dir", default="~/.local/bin")
    parser.add_argument("--root", default="~/.local/share/zettos-ainas-cli")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--purge-credentials", action="store_true")
    args = parser.parse_args()
    if args.purge_credentials and args.command != "uninstall":
        parser.error("--purge-credentials is only valid with uninstall")
    root = Path(args.root).expanduser().absolute()
    if root.is_symlink() or root == Path.home() or root == Path("/"):
        fail("Installation root must be a dedicated directory, not a symlink or home/root directory")
    if args.command == "install" and not shutil.which("openssl"):
        fail("OpenSSL is required for release signature verification")
    with installation_lock(root):
        state_file = root / "state.json"
        state = json.loads(state_file.read_text()) if state_file.exists() else {}
        if args.command == "install":
            install(args, root, state)
        elif args.command == "rollback":
            rollback(root, state)
        elif args.command == "uninstall":
            uninstall(args, root, state)
        else:
            print(json.dumps(state, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError, subprocess.SubprocessError, tarfile.TarError) as error:
        print("error: " + str(error), file=sys.stderr)
        sys.exit(1)
