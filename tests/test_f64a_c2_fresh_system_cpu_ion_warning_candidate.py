"""Only the reviewed pre-neutralization warning can pass the CPU wrapper."""

import importlib.util
import json
from pathlib import Path
import shutil

import pytest


PACKAGE = (Path(__file__).resolve().parents[1] / "packages"
           / "f64a-c2-fresh-system-cpu-ion-warning-candidate-20261013-v1")
LOADER = importlib.util.spec_from_file_location("fresh_system_cpu_ion_warning", PACKAGE / "builder.py")
assert LOADER is not None and LOADER.loader is not None
builder = importlib.util.module_from_spec(LOADER)
LOADER.loader.exec_module(builder)

IONS = ["/share/pkg.8/gromacs/2025.3/install_gpu/bin/gmx", "grompp", "-f", "ions.mdp",
        "-c", "solv.gro", "-p", "hybrid.top", "-o", "ions.tpr", "-maxwarn", "2"]
WARNING = """NOTE 1 [file hybrid.top, line 20900]:
  System has non-zero total charge: -5.000000

WARNING 1 [file hybrid.top, line 20900]:
  You are using Ewald electrostatics in a system with net charge. This can
  lead to severe artifacts, such as ions moving into regions with low
  dielectric, due to the uniform background charge. We suggest to
  neutralize your system with counter ions, possibly in combination with a
  physiological salt concentration.

There was 1 WARNING
"""


def test_candidate_sealed_and_inactive(tmp_path: Path) -> None:
    copied = tmp_path / PACKAGE.name
    shutil.copytree(PACKAGE, copied)
    spec = builder.verify_package(copied)
    assert spec["execution_authorized"] is False
    assert spec["production_authorized"] is False
    with pytest.raises(ValueError, match="not selected"):
        builder.permit(copied)


def test_only_reviewed_ion_warning_passes() -> None:
    builder.check_grompp_warning(IONS, WARNING)
    builder.check_grompp_warning(IONS, "There were 2 NOTEs\n")
    with pytest.raises(ValueError, match="unexpected"):
        builder.check_grompp_warning([*IONS[:3], "em.mdp", *IONS[4:]], WARNING)
    with pytest.raises(ValueError, match="differs"):
        builder.check_grompp_warning(IONS, WARNING.replace("-5.000000", "-4.000000"))
    with pytest.raises(ValueError, match="differs"):
        builder.check_grompp_warning(IONS, WARNING.replace("uniform background charge", "another cause"))
    with pytest.raises(ValueError, match="unexpected"):
        builder.check_grompp_warning(IONS, WARNING + "\nWARNING 2 [file hybrid.top, line 20900]:\n  Another warning.\n")


def test_saved_warning_review_requires_successful_exact_record(tmp_path: Path) -> None:
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
    path = logs / "command-07.json"
    record = {"argv": IONS, "cwd": str(system), "returncode": 0, "output": WARNING}
    path.write_text(json.dumps(record))
    reviewed = builder.review_saved_warning(PACKAGE, old)
    assert reviewed["status"] == "saved_preion_warning_review_pass"
    assert reviewed["returncode"] == 0
    assert reviewed["command_log"] == "command-07.json"
    record["returncode"] = 1
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="did not exit successfully"):
        builder.review_saved_warning(PACKAGE, old)
