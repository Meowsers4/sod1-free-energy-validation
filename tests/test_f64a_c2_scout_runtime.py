"""Checks for the non-submitting C2 scout runtime candidate."""

import json
from pathlib import Path
import shutil
import tempfile
import unittest

import yaml

from src.analysis import f64a_c2_scout_runtime as runtime


ROOT = Path(__file__).resolve().parents[1]


class ScoutRuntimeCandidateTests(unittest.TestCase):
    def test_accepted_tprs_and_arm_difference(self):
        spec = yaml.safe_load((ROOT / runtime.SPEC).read_text())
        spec["accepted_tpr_sha256"] = runtime.accepted_hashes(
            (ROOT / runtime.RESULT).read_text())
        runtime.validate_contract(spec)
        base = runtime.launch_plan(spec, "baseline")
        hrex = runtime.launch_plan(spec, "hrex")
        self.assertEqual(base["mdrun_per_rank"][:-2], hrex["mdrun_per_rank"][:-4])
        self.assertEqual(base["mdrun_per_rank"][-2:], ["-replex", "0"])
        self.assertEqual(hrex["mdrun_per_rank"][-4:],
                         ["-replex", "500", "-reseed", "20260929"])
        self.assertEqual(base["scheduler_request"], hrex["scheduler_request"])
        self.assertFalse(spec["execution_authorized"])

    def test_unreviewed_resource_change_rejected(self):
        spec = yaml.safe_load((ROOT / runtime.SPEC).read_text())
        spec["accepted_tpr_sha256"] = runtime.accepted_hashes(
            (ROOT / runtime.RESULT).read_text())
        spec["scheduler"]["walltime_seconds_per_arm"] = 10800
        with self.assertRaisesRegex(ValueError, "bounds changed"):
            runtime.validate_contract(spec)

    def test_packaged_launch_plan_tamper_rejected(self):
        source = ROOT / "packages/f64a-c2-scout-runtime-cpu-20260929-v1"
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "package"
            shutil.copytree(source, destination)
            runtime.review_package(destination)
            path = destination / "plan-hrex.json"
            value = json.loads(path.read_text())
            value["mdrun_per_rank"][-1] = "100"
            path.write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError, "file hash mismatch"):
                runtime.review_package(destination)


if __name__ == "__main__":
    unittest.main()
