"""The fresh-system CPU candidate is sealed and cannot execute as selected."""

import importlib.util
from pathlib import Path
import shutil

import pytest


PACKAGE = (Path(__file__).resolve().parents[1] / "packages"
           / "f64a-c2-fresh-system-cpu-candidate-20261006-v1")
MODULE_SPEC = importlib.util.spec_from_file_location("fresh_system_candidate", PACKAGE / "builder.py")
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
module = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(module)


def test_package_is_sealed_and_execution_disabled() -> None:
    spec = module.verify_package(PACKAGE)
    assert spec["execution_authorized"] is False
    assert spec["gpu_requested"] is False
    with pytest.raises(ValueError, match="not selected"):
        module.prepare(PACKAGE)
    assert not (PACKAGE / "prepared").exists()
    assert not (PACKAGE / "prepared.incomplete").exists()


def test_package_tampering_is_rejected(tmp_path: Path) -> None:
    destination = tmp_path / PACKAGE.name
    shutil.copytree(PACKAGE, destination)
    (destination / "source-spec.json").write_text(
        (destination / "source-spec.json").read_text() + " ")
    with pytest.raises(ValueError, match="checksum mismatch"):
        module.verify_package(destination)


def test_gro_atom_count_rejects_truncated_file(tmp_path: Path) -> None:
    path = tmp_path / "sample.gro"
    path.write_text("test\n2\n    1SOL     OW    1   0.0   0.0   0.0\n1 1 1\n")
    with pytest.raises(ValueError, match="atom count"):
        module.gro_atoms(path)
