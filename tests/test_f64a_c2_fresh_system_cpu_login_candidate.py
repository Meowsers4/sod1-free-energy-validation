"""The login-shell correction remains inactive and pins the failed attempt."""

import importlib.util
from pathlib import Path
import shutil

import pytest


PACKAGE = (Path(__file__).resolve().parents[1] / "packages"
           / "f64a-c2-fresh-system-cpu-login-candidate-20261012-v1")
LOADER = importlib.util.spec_from_file_location("fresh_system_cpu_login_candidate", PACKAGE / "builder.py")
assert LOADER is not None and LOADER.loader is not None
builder = importlib.util.module_from_spec(LOADER)
LOADER.loader.exec_module(builder)


def test_candidate_is_sealed_and_cannot_submit() -> None:
    spec = builder.verify_package(PACKAGE)
    assert spec["execution_authorized"] is False
    assert spec["production_authorized"] is False
    with pytest.raises(ValueError, match="not selected"):
        builder.permit(PACKAGE)
    assert not (PACKAGE / "submission").exists()
    job = (PACKAGE / "cpu-system.sge").read_text()
    assert job.startswith("#!/bin/bash -l\n")
    assert "${MODULEPATH:-}" in job
    assert "CONDA_DEFAULT_ENV" in job
    assert "sys.version_info[:2] < (3, 11)" in job


def test_failed_attempt_provenance_is_sealed(tmp_path: Path) -> None:
    copied = tmp_path / PACKAGE.name
    shutil.copytree(PACKAGE, copied)
    (copied / "failure-evidence.json").write_text("{}\n")
    with pytest.raises(ValueError, match="checksum mismatch"):
        builder.verify_package(copied)
