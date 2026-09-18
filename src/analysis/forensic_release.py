"""Build or verify a portable forensic release without modifying the archives.

The historical manifest is verified against frozen pre-review source snapshots.
A second manifest covers the revised source, every included input, and derived outputs.
Verification uses only the Python standard library and reads tar members without extraction.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile


def digest(path: Path) -> str:
    """SHA-256 of a file using bounded memory."""
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def historical_inputs(project: Path, archive: Path, ss: Path) -> dict[str, Path]:
    """Validate every historical entry, including the frozen original source files."""
    roots = {
        "main_archive": archive,
        "ss_archive": ss,
        "repository": project / "data/forensic_baseline_repository",
    }
    prefixes = {
        "main_archive": "archives/main",
        "ss_archive": "archives/ss",
        "repository": "project/data/forensic_baseline_repository",
    }
    manifest = json.loads((project / "data/forensic_archive_manifest.json").read_text())
    selected = {}
    for entry in manifest["files"]:
        path = roots[entry["root"]] / entry["path"]
        if (
            not path.is_file()
            or path.stat().st_size != entry["size_bytes"]
            or digest(path) != entry["sha256"]
        ):
            raise ValueError(
                f"Historical manifest mismatch: {entry['root']}/{entry['path']}"
            )
        selected[f"{prefixes[entry['root']]}/{entry['path']}"] = path
    return selected


def source_files(project: Path) -> dict[str, Path]:
    """Select project source and evidence, excluding caches, secrets and build products."""
    selected = {}
    paths = list(project.glob("*.md"))
    paths += [project / ".gitignore"]
    for name in (
        "src",
        "tests",
        "config",
        "data",
        "docs",
        "scripts",
        "env",
        "workflow",
        "pilots",
    ):
        paths.extend((project / name).rglob("*"))
    for path in paths:
        if (
            path.is_file()
            and "__pycache__" not in path.parts
            and "data/structures" not in path.relative_to(project).as_posix()
            and path.name != ".DS_Store"
            and path.suffix not in (".pyc", ".npz")
        ):
            selected["project/" + path.relative_to(project).as_posix()] = path
    return selected


def require_fresh_output(output: Path) -> None:
    """Refuse existing bundle, checksum or legacy partial before reading inputs."""
    for path in (
        output,
        output.with_suffix(output.suffix + ".sha256"),
        output.with_suffix(output.suffix + ".partial"),
    ):
        if path.exists() or path.is_symlink():
            raise FileExistsError(
                f"Refusing to overwrite release evidence: {path}; choose a fresh versioned path"
            )


def source_identity(project: Path, selected: dict[str, Path]) -> dict:
    """Require committed, clean executable/config/environment sources for new builds."""
    prefixes = (
        "project/src/",
        "project/tests/",
        "project/config/",
        "project/scripts/",
        "project/env/",
        "project/workflow/",
        "project/pilots/",
    )
    paths = sorted(
        name.removeprefix("project/")
        for name in selected
        if name.startswith(prefixes)
        or (name.startswith("project/docs/") and Path(name).suffix in (".yaml", ".yml"))
    )
    if not paths:
        raise ValueError("Release has no executable source inventory")

    def git(*args):
        return subprocess.run(
            ["git", "-C", str(project), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    commit = git("rev-parse", "HEAD")
    status = git("status", "--porcelain", "--untracked-files=all", "--", *paths)
    tracked = set(git("ls-files", "--", *paths).splitlines())
    if status or tracked != set(paths):
        raise RuntimeError(
            f"Commit release executable/config/environment sources first: {status}"
        )
    return {
        "git_commit": commit,
        "executable_paths_clean": True,
        "source_sha256": {p: digest(project / p) for p in paths},
    }


def build_release(project: Path, archive: Path, ss: Path, output: Path) -> dict:
    """Create a tar.gz with complete checksums and immutable historical inputs."""
    require_fresh_output(output)
    selected = historical_inputs(project, archive, ss)
    selected.update(source_files(project))
    identity = source_identity(project, selected)
    manifest = {
        "schema_version": 2,
        "source_code_identity": identity,
        "scope": "Forensic reproduction; no GPU execution and no replacement validation gate.",
        "missing_data": [
            "A4V attempt-1 raw windows were overwritten. Only the original run-time JSON survives.",
            "This bundle reconstructs energy analysis; it is not a complete archive of all simulation trajectories and external force-field/runtime dependencies.",
            "The separate F64A v1/v2 extended raw matrices/checkpoint trees are not included by this historical-archive release builder.",
        ],
        "files": [
            {"path": name, "size_bytes": path.stat().st_size, "sha256": digest(path)}
            for name, path in sorted(selected.items())
        ],
    }
    payload = (json.dumps(manifest, indent=2) + "\n").encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    lock = output.with_name(output.name + ".lock")
    with lock.open("x") as handle:
        handle.write(f"Building release in process {os.getpid()}\n")
    try:
        require_fresh_output(output)
        with tempfile.TemporaryDirectory(
            dir=output.parent, prefix=".forensic-release-"
        ) as directory:
            temporary = Path(directory) / "bundle.tar.gz"
            with temporary.open("wb") as raw:
                with gzip.GzipFile(
                    filename="", mode="wb", fileobj=raw, mtime=0
                ) as zipped:
                    with tarfile.open(fileobj=zipped, mode="w") as tar:
                        for name, path in sorted(selected.items()):
                            info = tarfile.TarInfo(name)
                            info.size = path.stat().st_size
                            info.mode = 0o644
                            with path.open("rb") as stream:
                                tar.addfile(info, stream)
                        info = tarfile.TarInfo("RELEASE_MANIFEST.json")
                        info.size = len(payload)
                        info.mode = 0o644
                        tar.addfile(info, io.BytesIO(payload))
            verify_release(temporary)
            if source_identity(project, selected) != identity:
                raise ValueError("Release source changed during build")
            checksum = Path(directory) / "checksum"
            checksum.write_text(f"{digest(temporary)}  {output.name}\n")
            os.link(
                temporary, output
            )  # Exclusive publication; never replace existing bytes.
            os.link(checksum, output.with_suffix(output.suffix + ".sha256"))
    finally:
        lock.unlink()
    return manifest


def verify_transport(path: Path) -> None:
    """Require the matching sidecar checksum without changing either artifact."""
    sidecar = path.with_suffix(path.suffix + ".sha256")
    fields = sidecar.read_text().strip().split()
    if len(fields) != 2 or fields[1] != path.name or fields[0] != digest(path):
        raise ValueError("Release transport checksum mismatch")


def verify_release(path: Path) -> int:
    """Verify exact member inventory and contents without executing bundled code."""
    with tarfile.open(path, "r:gz") as tar:
        names = tar.getnames()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate release members")
        member = tar.extractfile("RELEASE_MANIFEST.json")
        if member is None:
            raise ValueError("Missing release manifest")
        manifest = json.load(member)
        expected = {r["path"] for r in manifest["files"]} | {"RELEASE_MANIFEST.json"}
        if set(names) != expected:
            raise ValueError("Release inventory differs from manifest")
        for row in manifest["files"]:
            info = tar.getmember(row["path"])
            if (
                not info.isfile()
                or Path(row["path"]).is_absolute()
                or ".." in Path(row["path"]).parts
            ):
                raise ValueError("Unsafe release member")
            h = hashlib.sha256()
            stream = tar.extractfile(info)
            if stream is None:
                raise ValueError("Unreadable release member")
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(block)
            if info.size != row["size_bytes"] or h.hexdigest() != row["sha256"]:
                raise ValueError(f"Corrupt release member: {row['path']}")
    return len(manifest["files"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--archive-root", type=Path)
    parser.add_argument("--ss-archive", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.verify:
        verify_transport(args.verify)
        print(f"Verified {verify_release(args.verify)} release files")
    else:
        if not all((args.archive_root, args.ss_archive, args.output)):
            parser.error("Building requires --archive-root, --ss-archive and --output")
        result = build_release(
            args.project, args.archive_root, args.ss_archive, args.output
        )
        print(f"Built {args.output} with {len(result['files'])} files")


if __name__ == "__main__":
    main()
