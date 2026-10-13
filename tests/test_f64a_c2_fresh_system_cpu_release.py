"""The inactive r3 CPU release has a sealed identity and rejects submission."""

import importlib.util
from pathlib import Path
import shutil

import pytest


PACKAGE = (Path(__file__).resolve().parents[1] / "packages"
           / "f64a-c2-fresh-system-cpu-execution-release-candidate-20261011-v1")
LOADER = importlib.util.spec_from_file_location("fresh_system_cpu_release", PACKAGE / "builder.py")
assert LOADER is not None and LOADER.loader is not None
builder = importlib.util.module_from_spec(LOADER)
LOADER.loader.exec_module(builder)


def test_inactive_release_blocks_submission_before_side_effects() -> None:
    spec = builder.verify_package(PACKAGE)
    assert spec["execution_authorized"] is False
    assert spec["production_authorized"] is False
    assert spec["gpu_requested"] is False
    assert spec["requested_cpu_slots"] == 8
    with pytest.raises(ValueError, match="not selected"):
        builder.permit(PACKAGE)
    assert not (PACKAGE / "submission").exists()
    assert not (PACKAGE / "prepared.incomplete").exists()


def test_release_rejects_provenance_tampering(tmp_path: Path) -> None:
    copied = tmp_path / PACKAGE.name
    shutil.copytree(PACKAGE, copied)
    (copied / "candidate-SHA256SUMS").write_text("tampered\n")
    with pytest.raises(ValueError, match="checksum mismatch"):
        builder.verify_package(copied)
