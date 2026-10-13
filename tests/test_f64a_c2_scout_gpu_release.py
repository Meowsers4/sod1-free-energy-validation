"""The execution release stays sealed and inert before scout selection."""

import json
from pathlib import Path
import subprocess
import sys

import pytest

from src.analysis import f64a_c2_scout_gpu_release_package as release
from src.analysis import f64a_c2_scout_gpu_runtime as core


ROOT = Path(__file__).resolve().parents[1]


def test_inactive_release_has_exact_request_and_denies_attempt(tmp_path):
    target = tmp_path / "release"
    release.package(target, root=ROOT)
    release.review_package(target)
    spec = json.loads((target / "contract.json").read_text())
    assert spec["execution_authorized"] is False
    assert spec["selected_technical_arms"] == []
    assert len(spec["states"]) == 20
    assert "-l h_rt=02:00:00" in (target / "baseline.sge").read_text()
    assert "-l h_rt=02:00:00" in (target / "hrex.sge").read_text()
    wrapper = (target / "SUBMIT_BASELINE_ON_SCC.sh").read_text()
    assert wrapper.index("runtime.py permit baseline") < wrapper.index("mkdir submission-baseline")
    assert wrapper.index("runtime.py permit baseline") < wrapper.index("qsub ")
    result = subprocess.run([sys.executable, str(target / "runtime.py"),
                             "permit", "baseline"], capture_output=True, text=True)
    assert result.returncode != 0
    assert "GPU execution is not authorized" in result.stderr
    assert not (target / "attempts").exists()
    assert not (target / "submission-baseline").exists()


def test_release_selection_requires_su_disposition_and_is_new_seal(tmp_path):
    source = ROOT / release.CANDIDATE
    with pytest.raises(ValueError, match="SU disposition"):
        release.contract_from_candidate(source, {"arms": ["baseline", "hrex"]})
    target = tmp_path / "release"
    release.package(target, root=ROOT)
    (target / "contract.json").write_text((target / "contract.json").read_text().replace(
        '"execution_authorized": false', '"execution_authorized": true'))
    with pytest.raises(ValueError, match="release package file changed"):
        release.review_package(target)


def test_selected_release_enables_baseline_but_keeps_hrex_gate(tmp_path):
    selection = json.loads((ROOT / "docs/f64a_c2_scout_execution_selection.json").read_text())
    target = tmp_path / "selected"
    release.package(target, root=ROOT, selection=selection)
    release.review_package(target)
    spec = json.loads((target / "contract.json").read_text())
    assert spec["execution_authorized"] is True
    assert spec["production_authorized"] is False
    assert spec["selected_technical_arms"] == ["baseline", "hrex"]
    assert spec["selection_record"]["su_disposition"] == "explicitly_waived"
    core.execution_guard(spec, "baseline")
    with pytest.raises(ValueError, match="baseline technical/accounting gate"):
        core.preflight_baseline_gate(target, "hrex")
    assert not (target / "attempts").exists()
