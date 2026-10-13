import json
import hashlib
from pathlib import Path
import subprocess
import sys

from src.analysis.gromacs_protein_runtime_package import create_package
from src.analysis import gromacs_protein_restart as protein_restart
from src.analysis import gromacs_protein_runtime_checks as protein_checks
from src.analysis import gromacs_gpu_smoke_runtime as smoke_runtime


ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def seal(directory):
    lines = [f"{sha(path)}  {path.relative_to(directory)}" for path in
             sorted(directory.rglob("*")) if path.is_file() and path.name != "SHA256SUMS"]
    (directory / "SHA256SUMS").write_text("\n".join(lines) + "\n")


def test_package_is_sealed_and_cpu_import_is_separate(tmp_path):
    package = tmp_path / "protein-runtime"
    create_package(package, root=ROOT)
    assert not (package / "prepared").exists()
    assert not (package / "attempt").exists()
    spec = json.loads((package / "contract.json").read_text())
    assert spec["execution_authorized"] is False
    assert spec["production_authorized"] is False
    assert spec["scheduler"]["pe"] == "omp16"
    assert spec["scheduler"]["ranks"] == 20
    assert spec["prepared_source"]["manifest_sha256"] == \
        "858070ac1c8d757d0fdb0fa744148865e24abdccb8d82e3d1a670698734e77b9"
    check = subprocess.run(["sha256sum", "-c", "SHA256SUMS"], cwd=package,
                           capture_output=True, text=True)
    assert check.returncode == 0, check.stdout + check.stderr
    assert "-w v" in (package / "VALIDATE_QUEUE_ON_SCC.sh").read_text()
    assert "qsub" not in (package / "IMPORT_ON_SCC.sh").read_text()
    assert "import-protein-prepared" in (package / "IMPORT_ON_SCC.sh").read_text()
    assert "test ! -e attempt" in (package / "SUBMIT_ON_SCC.sh").read_text()


def test_standalone_adapter_patches_only_packaged_wrapper(tmp_path):
    package = tmp_path / "protein-runtime"
    create_package(package, root=ROOT)
    code = """import runtime, smoke_runtime, restart
assert smoke_runtime.parse_exchange is runtime.parse_exchange
assert smoke_runtime.validate_tpr_dump is runtime.validate_tpr_dump
assert smoke_runtime.verify_prepared is runtime.verify_prepared
assert restart.rt is runtime
print('PROTEIN_ADAPTER_LOADED')
"""
    result = subprocess.run([sys.executable, "-c", code], cwd=package,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PROTEIN_ADAPTER_LOADED" in result.stdout


def test_cpu_import_rehearsal_copies_all_states_without_gpu_or_qsub(tmp_path):
    package = tmp_path / "protein-runtime"
    create_package(package, root=ROOT)
    source = tmp_path / "source" / "prepared"
    source.mkdir(parents=True)
    (source / "source-spec.yaml").write_text("mock source spec\n")
    gro = ("Mock protein\n2\n"
           "    1ALA      N    1   0.000   0.000   0.000\n"
           "    1ALA     CA    2   0.100   0.000   0.000\n"
           "   1.00000   1.00000   1.00000\n")
    entries = []
    for state in range(20):
        name = f"state{state:02d}"
        output = source / "states" / name
        inputs = source / "inputs" / "states" / name
        output.mkdir(parents=True)
        inputs.mkdir(parents=True)
        (output / "topol.tpr").write_text(f"mock protein tpr {state}\n")
        (inputs / "start.gro").write_text(gro)
        (inputs / "technical.mdp").write_text(f"init-lambda-state = {state}\n")
        entries.append({"state": state, "tpr_sha256": sha(output / "topol.tpr")})
    image = tmp_path / "mock.sif"
    image.write_text("mock SIF\n")
    record = {"status": "cpu_inputs_prepared_pending_review",
              "execution_authorized": False, "production_authorized": False,
              "sif_sha256": sha(image),
              "source_spec_sha256": sha(source / "source-spec.yaml"),
              "states": entries}
    (source / "PREPARED.json").write_text(json.dumps(record) + "\n")
    seal(source)
    spec = json.loads((package / "contract.json").read_text())
    spec["prepared_source"] = {"path": str(source),
                               "manifest_sha256": sha(source / "SHA256SUMS"),
                               "source_spec_sha256": sha(source / "source-spec.yaml")}
    spec["image"]["path"] = str(image)
    spec["image"]["sha256"] = sha(image)
    (package / "contract.json").write_text(json.dumps(spec) + "\n")
    seal(package)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    singularity = bin_dir / "singularity"
    singularity.write_text("""#!/usr/bin/env python3
import json, re, sys
from pathlib import Path
spec = json.loads(Path('contract.json').read_text())
name = next(x for x in sys.argv if re.fullmatch(r'/smoke/prepared/state\\d{2}', x))
state = int(name[-2:])
print('natoms = 2')
print('nsteps = 2000')
print('init-step = 0')
print('init-lambda-state =', state)
print('n-lambdas = 20')
print('calc-lambda-neighbors = -1')
print('dt = 0.002')
print('all-lambdas:')
print('fep-lambdas =', ' '.join(str(x['lambda_value']) for x in spec['states']))
""")
    singularity.chmod(0o755)
    scratch_base = tmp_path / "scratch"
    scratch_base.mkdir()
    code = """import json, runtime
from pathlib import Path
root = Path('.').resolve()
spec = json.loads((root/'contract.json').read_text())
original = runtime.tempfile.mkdtemp
runtime.tempfile.mkdtemp = lambda **kwargs: original(prefix=kwargs['prefix'], dir=SCRATCH)
runtime.import_protein_prepared(root, spec)
runtime.verify_prepared(root, spec)
print('MOCK_PROTEIN_IMPORT_PASS')
""".replace("SCRATCH", repr(str(scratch_base)))
    env = dict(__import__("os").environ)
    env["PATH"] = str(bin_dir) + ":" + env["PATH"]
    result = subprocess.run([sys.executable, "-c", code], cwd=package,
                            env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "MOCK_PROTEIN_IMPORT_PASS" in result.stdout
    prepared = json.loads((package / "prepared" / "PREPARED.json").read_text())
    assert len(prepared["tpr_sha256"]) == 20
    assert prepared["gpu_executed"] is False
    assert not (package / "attempt").exists()


def test_protein_restart_accepts_zero_swaps_with_complete_boundary(tmp_path):
    package = tmp_path / "protein-runtime"
    create_package(package, root=ROOT)
    spec = json.loads((package / "contract.json").read_text())
    work = package / "attempt"
    work.mkdir()
    exchange = "".join(
        f"Replica exchange at step {step} time {step * 0.002}\n"
        "Repl ex " + " ".join(str(i) for i in range(20)) + "\n"
        for step in range(100, 2000, 100))
    first = protein_checks.parse_exchange(
        exchange.split("Replica exchange at step 1000", 1)[0], 20, 100, 1000)
    complete = protein_checks.parse_exchange(exchange, 20, 100, 2000)
    for state in spec["states"]:
        name, index = state["directory"], state["local_index"]
        p = work / name
        p.mkdir()
        prepared = package / "prepared" / name
        prepared.mkdir(parents=True)
        (prepared / "topol.tpr").write_bytes(b"sealed TPR")
        (p / "topol.tpr").write_bytes(b"sealed TPR")
        (p / "smoke.cpt").write_bytes(b"checkpoint " + str(index).encode())
        (p / "checkpoint.dump").write_text(
            f"step = 1000\nt = 2.0\nsimulation part # = 1\nfep_state[0]={index}\n")
        for filename in ("smoke.xvg", "energy.xvg"):
            (p / filename).write_text("".join(f"{i * .2:.1f} 1 2\n" for i in range(11)))
    for filename in ("mps-overlap.json", "device-map.json", "protein-ladder-review-first.json"):
        smoke_runtime.write_json(work / filename, {"test": True})
    smoke_runtime.write_json(work / "cpu-affinity.json", {"selected_cpu_ids": list(range(16))})
    (work / "mpi-first.log").write_text("first phase\n")
    protein_restart.seal_first_part(package, spec, first)
    for state in spec["states"]:
        p = work / state["directory"]
        index = state["local_index"]
        (p / "checkpoint.dump").write_text(
            f"step = 2000\nt = 4.0\nsimulation part # = 2\nfep_state[0]={index}\n")
        for filename in ("smoke.xvg", "energy.xvg"):
            (p / filename).write_text("".join(f"{i * .2:.1f} 1 2\n" for i in range(21)))
    protein_restart.validate_restart(package, spec, complete)
    review = json.loads((work / "restart-review.json").read_text())
    assert review["restart_verified"] is True
    assert review["combined_exchange_rounds"] == 19
    assert all(not row["accepted_pairs"] for row in complete)
