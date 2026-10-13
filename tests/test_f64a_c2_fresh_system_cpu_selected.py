"""Selected r3 CPU release permits exactly the reviewed one-job path."""

import importlib.util
from pathlib import Path
import shutil

import pytest


PACKAGE = (Path(__file__).resolve().parents[1] / "packages"
           / "f64a-c2-fresh-system-cpu-execution-selected-20261011-v1")
LOADER = importlib.util.spec_from_file_location("fresh_system_cpu_selected", PACKAGE / "builder.py")
assert LOADER is not None and LOADER.loader is not None
builder = importlib.util.module_from_spec(LOADER)
LOADER.loader.exec_module(builder)


def test_selected_release_requires_review_and_rejects_second_attempt(tmp_path: Path) -> None:
    copied = tmp_path / PACKAGE.name
    shutil.copytree(PACKAGE, copied)
    spec = builder.verify_package(copied)
    assert spec["execution_authorized"] is True
    assert spec["production_authorized"] is False
    assert spec["gpu_requested"] is False
    with pytest.raises(ValueError, match="passing SCC static review"):
        builder.permit(copied)
    (copied / "review.log").write_text(builder.REVIEW_MARKER + "\n")
    assert builder.permit(copied)["requested_cpu_slots"] == 8
    (copied / "submission").mkdir()
    with pytest.raises(ValueError, match="no second attempt"):
        builder.permit(copied)


def test_selected_release_rejects_selection_tampering(tmp_path: Path) -> None:
    copied = tmp_path / PACKAGE.name
    shutil.copytree(PACKAGE, copied)
    (copied / "selection.json").write_text("{}\n")
    with pytest.raises(ValueError, match="checksum mismatch"):
        builder.verify_package(copied)
