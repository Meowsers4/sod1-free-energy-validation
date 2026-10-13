"""The corrected CPU selection is sealed and allows only its reviewed job."""

import importlib.util
from pathlib import Path
import shutil

import pytest


PACKAGE = (Path(__file__).resolve().parents[1] / "packages"
           / "f64a-c2-fresh-system-cpu-explicit-login-selected-20261012-v1")
LOADER = importlib.util.spec_from_file_location("fresh_system_cpu_explicit_login_selected", PACKAGE / "builder.py")
assert LOADER is not None and LOADER.loader is not None
builder = importlib.util.module_from_spec(LOADER)
LOADER.loader.exec_module(builder)


def test_one_reviewed_attempt_and_no_gpu(tmp_path: Path) -> None:
    copied = tmp_path / PACKAGE.name
    shutil.copytree(PACKAGE, copied)
    spec = builder.verify_package(copied)
    assert spec["execution_authorized"] is True
    assert spec["production_authorized"] is False
    assert spec["gpu_requested"] is False
    assert spec["requested_cpu_slots"] == 8
    assert spec["scheduler_walltime"] == "01:00:00"
    with pytest.raises(ValueError, match="passing SCC static review"):
        builder.permit(copied)
    (copied / "review.log").write_text(builder.REVIEW_MARKER + "\n")
    assert builder.permit(copied)["repeat"] == 3
    (copied / "submission").mkdir()
    with pytest.raises(ValueError, match="no second attempt"):
        builder.permit(copied)


def test_selection_and_login_body_are_sealed(tmp_path: Path) -> None:
    copied = tmp_path / PACKAGE.name
    shutil.copytree(PACKAGE, copied)
    wrapper = (copied / "cpu-system.sge").read_text()
    body = (copied / "run-system-login.sh").read_text()
    assert 'exec /bin/bash -l "$package_dir/run-system-login.sh"' in wrapper
    assert "shopt -q login_shell" in body
    assert "python builder.py prepare" in body
    (copied / "run-system-login.sh").write_text("exit 0\n")
    with pytest.raises(ValueError, match="checksum mismatch"):
        builder.verify_package(copied)
