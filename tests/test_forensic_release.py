"""Reject corrupt, incomplete or non-file release contents before extraction."""

import hashlib
import io
import json
import subprocess
import tarfile

import pytest

from src.analysis import forensic_release as release
from src.analysis.forensic_release import verify_release


def _bundle(path, content, recorded):
    manifest = json.dumps(
        {
            "files": [
                {
                    "path": "project/input",
                    "size_bytes": len(recorded),
                    "sha256": hashlib.sha256(recorded).hexdigest(),
                }
            ]
        }
    ).encode()
    with tarfile.open(path, "w:gz") as tar:
        for name, data in [
            ("RELEASE_MANIFEST.json", manifest),
            ("project/input", content),
        ]:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))


def test_verify_release_detects_tampering(tmp_path):
    path = tmp_path / "bundle.tar.gz"
    _bundle(path, b"original", b"original")
    assert verify_release(path) == 1
    _bundle(path, b"changed!", b"original")
    with pytest.raises(ValueError, match="Corrupt"):
        verify_release(path)


@pytest.mark.parametrize("suffix", ["", ".sha256", ".partial", ".lock"])
def test_build_refuses_existing_evidence_before_input_access(
    tmp_path, suffix, monkeypatch
):
    output = tmp_path / "release.tar.gz"
    protected = tmp_path / (output.name + suffix)
    protected.write_bytes(b"preserved evidence")
    if suffix == ".lock":
        # Lock creation is later than inventory validation, so stub only those reads.
        monkeypatch.setattr(release, "historical_inputs", lambda *args: {})
        monkeypatch.setattr(release, "source_files", lambda *args: {})
        monkeypatch.setattr(release, "source_identity", lambda *args: {})
    with pytest.raises(FileExistsError):
        release.build_release(
            tmp_path, tmp_path / "missing", tmp_path / "missing-ss", output
        )
    assert protected.read_bytes() == b"preserved evidence"


def test_transport_checksum_verification_is_read_only(tmp_path):
    path = tmp_path / "release.tar.gz"
    _bundle(path, b"original", b"original")
    sidecar = tmp_path / (path.name + ".sha256")
    sidecar.write_text(f"{release.digest(path)}  {path.name}\n")
    release.verify_transport(path)
    original = path.read_bytes()
    sidecar.write_text("0" * 64 + f"  {path.name}\n")
    with pytest.raises(ValueError, match="transport"):
        release.verify_transport(path)
    assert path.read_bytes() == original


@pytest.fixture
def committed_project(tmp_path):
    project = tmp_path / "project"
    (project / "src").mkdir(parents=True)
    (project / "src/example.py").write_text(
        "# synthetic release fixture, not scientific results\n"
    )
    subprocess.run(["git", "init", str(project)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(project), "add", "src/example.py"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(project),
            "-c",
            "user.name=Synthetic test",
            "-c",
            "user.email=synthetic@example.invalid",
            "commit",
            "-m",
            "Synthetic fixture",
        ],
        check=True,
        capture_output=True,
    )
    return project


def test_requires_committed_clean_code(committed_project):
    project = committed_project
    selected = release.source_files(project)
    identity = release.source_identity(project, selected)
    assert len(identity["git_commit"]) == 40
    (project / "src/example.py").write_text("# changed\n")
    with pytest.raises(RuntimeError, match="Commit release"):
        release.source_identity(project, selected)


def test_new_release_records_commit_and_does_not_replace(
    committed_project, tmp_path, monkeypatch
):
    project = committed_project
    monkeypatch.setattr(release, "historical_inputs", lambda *args: {})
    output = tmp_path / "new-release.tar.gz"
    result = release.build_release(
        project, tmp_path / "unused", tmp_path / "unused-ss", output
    )
    assert result["schema_version"] == 2
    assert result["source_code_identity"]["executable_paths_clean"]
    assert release.verify_release(output) == len(result["files"])
    release.verify_transport(output)
    original = output.read_bytes()
    with pytest.raises(FileExistsError):
        release.build_release(
            project, tmp_path / "unused", tmp_path / "unused-ss", output
        )
    assert output.read_bytes() == original
    assert not list(tmp_path.glob(".forensic-release-*"))
    assert not (tmp_path / (output.name + ".lock")).exists()
