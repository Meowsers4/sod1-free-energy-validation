"""The explicit-login CPU package is sealed and remains unselected."""

import importlib.util
from pathlib import Path
import shutil

import pytest


PACKAGE = (Path(__file__).resolve().parents[1] / "packages"
           / "f64a-c2-fresh-system-cpu-explicit-login-candidate-20261012-v2")
LOADER = importlib.util.spec_from_file_location("fresh_system_cpu_explicit_login", PACKAGE / "builder.py")
assert LOADER is not None and LOADER.loader is not None
builder = importlib.util.module_from_spec(LOADER)
LOADER.loader.exec_module(builder)


def test_sealed_candidate_requires_new_selection() -> None:
    spec = builder.verify_package(PACKAGE)
    assert spec["execution_authorized"] is False
    assert spec["production_authorized"] is False
    with pytest.raises(ValueError, match="not selected"):
        builder.permit(PACKAGE)
    assert not (PACKAGE / "submission").exists()
    wrapper = (PACKAGE / "cpu-system.sge").read_text()
    body = (PACKAGE / "run-system-login.sh").read_text()
    assert 'exec /bin/bash -l "$package_dir/run-system-login.sh"' in wrapper
    assert "shopt -q login_shell" in body
    assert "source scripts/scc_env.sh" in body


def test_login_body_tampering_breaks_seal(tmp_path: Path) -> None:
    copied = tmp_path / PACKAGE.name
    shutil.copytree(PACKAGE, copied)
    (copied / "run-system-login.sh").write_text("exit 0\n")
    with pytest.raises(ValueError, match="checksum mismatch"):
        builder.verify_package(copied)
