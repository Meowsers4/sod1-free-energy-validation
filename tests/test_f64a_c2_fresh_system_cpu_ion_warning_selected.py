"""Check the selected attempt's seal, one-job guard, and warning provenance."""

import importlib.util
import json
from pathlib import Path
import shutil

import pytest


PACKAGE = (Path(__file__).resolve().parents[1] / "packages"
           / "f64a-c2-fresh-system-cpu-ion-warning-selected-20261013-v1")
LOADER = importlib.util.spec_from_file_location("fresh_system_cpu_ion_selected",
                                                 PACKAGE / "builder.py")
assert LOADER is not None and LOADER.loader is not None
builder = importlib.util.module_from_spec(LOADER)
LOADER.loader.exec_module(builder)


def test_selected_package_needs_its_own_review_and_sealed_selection(tmp_path: Path) -> None:
    copied = tmp_path / PACKAGE.name
    shutil.copytree(PACKAGE, copied)
    spec = builder.verify_package(copied)
    assert spec["execution_authorized"] is True
    assert spec["production_authorized"] is False
    with pytest.raises(ValueError, match="passing SCC static review log"):
        builder.permit(copied)
    selection = json.loads((copied / "selection.json").read_text())
    selection["max_jobs"] = 2
    (copied / "selection.json").write_text(json.dumps(selection))
    with pytest.raises(ValueError, match="checksum mismatch"):
        builder.verify_package(copied)


def test_saved_command_hash_is_pinned_before_use(tmp_path: Path) -> None:
    old = tmp_path / "spent"
    logs = old / "prepared.incomplete" / "build-logs"
    system = old / "prepared.incomplete/results/fep/F64A/folded/system_r3"
    logs.mkdir(parents=True)
    system.mkdir(parents=True)
    (system / "ions.tpr").write_bytes(b"mock ions tpr")
    shutil.copy2(PACKAGE / "spent-selected-SHA256SUMS", old / "SHA256SUMS")
    selected = PACKAGE.parent / "f64a-c2-fresh-system-cpu-explicit-login-selected-20261012-v1"
    for line in (old / "SHA256SUMS").read_text().splitlines():
        name = line.split("  ", 1)[1]
        shutil.copy2(selected / name, old / name)
    record = {
        "argv": ["/share/pkg.8/gromacs/2025.3/install_gpu/bin/gmx", "grompp",
                 "-f", "ions.mdp", "-c", "solv.gro", "-p", "hybrid.top",
                 "-o", "ions.tpr", "-maxwarn", "2"],
        "cwd": str(system), "returncode": 0,
        "output": "There was 1 WARNING\n",
    }
    (logs / "command-07.json").write_text(json.dumps(record))
    with pytest.raises(ValueError, match="differs from reviewed SHA-256"):
        builder.review_saved_warning(PACKAGE, old)
