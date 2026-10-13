"""Checks for the pinned, non-production GROMACS Singularity definition."""

from copy import deepcopy
import hashlib
import os
from pathlib import Path
import subprocess

import pytest

from src.analysis import gromacs_container_spec


def test_current_definition_is_build_ready_but_not_runtime_eligible():
    report = gromacs_container_spec.evaluate(gromacs_container_spec.load_spec())
    assert report["ready_to_build"] is True
    assert report["eligible_now"] is False
    assert report["production_authorized"] is False
    assert report["build_executed"] is False
    assert report["gpu_smoke_executed"] is False
    assert report["runtime_contract"]["candidate_host_count"] == 1
    assert report["runtime_contract"]["mpi_ranks"] == 20
    assert report["runtime_contract"]["candidate_gpu_count"] == 4
    assert len(report["definition_sha256"]) == 64


def test_current_definition_pins_combined_mpi_cuda_and_l40s_target():
    report = gromacs_container_spec.evaluate(gromacs_container_spec.load_spec())
    assert report["toolchain"]["gromacs"]["version"] == "2025.3"
    assert report["toolchain"]["openmpi"]["version"] == "4.1.5"
    assert report["toolchain"]["cuda"] == "12.8.0"
    assert report["runtime_contract"]["gpu_model"] == "L40S"
    assert report["checks"]["internal_mpi_only"] is True


def test_authorization_or_multi_host_drift_fails_closed(tmp_path):
    authorized = deepcopy(gromacs_container_spec.load_spec())
    authorized["production_authorized"] = True
    path = tmp_path / "authorized.yaml"
    import yaml

    path.write_text(yaml.safe_dump(authorized))
    with pytest.raises(ValueError, match="cannot authorize production"):
        gromacs_container_spec.load_spec(path)


def test_missing_required_definition_fragment_fails(tmp_path):
    spec = deepcopy(gromacs_container_spec.load_spec())
    definition = tmp_path / "bad.def"
    definition.write_text("Bootstrap: docker\n")
    spec["artifact"]["definition"] = str(definition)
    with pytest.raises(ValueError, match="missing required fragments"):
        gromacs_container_spec.evaluate(spec)


@pytest.mark.parametrize("component", ["gromacs", "regressiontests", "openmpi", "cmake", "fftw"])
@pytest.mark.parametrize("field", ["version", "url", "digest"])
def test_toolchain_drift_is_rejected(component, field):
    spec = deepcopy(gromacs_container_spec.load_spec())
    pin = spec["toolchain"][component]
    if field == "digest":
        algorithm = "md5" if "md5" in pin else "sha256"
        pin[algorithm] = "0" * len(pin[algorithm])
    elif field == "url":
        pin[field] = pin[field].replace("https://", "https://other.example/")
    else:
        pin[field] = "0.0.0"
    with pytest.raises(ValueError, match="disagrees"):
        gromacs_container_spec.evaluate(spec)


@pytest.mark.parametrize("section,key,value", [
    ("toolchain", "compiler", "gcc-toolset-11"),
    ("toolchain", "cuda", "12.7.0"),
    ("artifact", "runtime_image", "other:latest"),
    ("artifact", "definition_sha256", "0" * 64),
    ("build_contract", "gromacs_mpi", False),
    ("build_contract", "gromacs_thread_mpi", True),
    ("build_contract", "cuda_target_sm", "90"),
    ("runtime_contract", "openmpi_plm", "rsh"),
    ("build_contract", "runtime_packages", []),
    ("runtime_contract", "openmpi_session_tmpdir", "/scratch"),
])
def test_build_contract_drift_is_rejected(section, key, value):
    spec = deepcopy(gromacs_container_spec.load_spec())
    spec[section][key] = value
    with pytest.raises(ValueError, match="disagree"):
        gromacs_container_spec.evaluate(spec)


def test_changed_definition_bytes_are_rejected(tmp_path):
    spec = deepcopy(gromacs_container_spec.load_spec())
    definition = Path(spec["artifact"]["definition"]).read_text()
    candidate = tmp_path / "changed.def"
    candidate.write_text(definition + "\n# unreviewed change\n")
    spec["artifact"]["definition"] = str(candidate)
    with pytest.raises(ValueError, match="SHA-256"):
        gromacs_container_spec.evaluate(spec)


@pytest.mark.parametrize("mpi,version,exit_code,mpi_exit,accepted", [
    ("MPI", "Open MPI v4.1.5, package: test", 0, 0, True),
    ("MPI (GPU-aware: CUDA)", "Open MPI v4.1.5, package: test", 0, 0, True),
    ("thread_mpi", "Open MPI v4.1.5", 0, 0, False),
    ("MPI", "Open MPI v4.1.50", 0, 0, False),
    ("MPI", "Open MPI v4.1.5", 2, 0, False),
    ("MPI", "Open MPI v4.1.5", 0, 42, False),
])
def test_actual_image_self_test_accepts_external_mpi_only(tmp_path, mpi, version, exit_code, mpi_exit, accepted):
    definition = Path(gromacs_container_spec.load_spec()["artifact"]["definition"]).read_text()
    script = definition.split("\n%test\n", 1)[1]
    script = script.replace("/tmp/", str(tmp_path) + "/")
    script = script.replace("/opt/", str(tmp_path / "opt") + "/")
    for relative in ("gromacs/2025.3/share/gromacs/top/residuetypes.dat", "openmpi/4.1.5/share/pmix/help-pmix-runtime.txt"):
        data = tmp_path / "opt" / relative
        data.parent.mkdir(parents=True, exist_ok=True)
        data.write_text("installed data")
    output = f"GROMACS version:     2025.3\nMPI library:         {mpi}\nMPI library version: {version}\nGPU support:         CUDA"
    fake = tmp_path / "gmx_mpi"
    session_checks = (
        'test "${OMPI_MCA_orte_tmpdir_base:-}" = /tmp || exit 98\n'
        'test -z "${OMPI_MCA_orte_local_tmpdir_base:-}" || exit 98\n'
        'test -z "${OMPI_MCA_orte_remote_tmpdir_base:-}" || exit 98\n'
    )
    fake.write_text(f"#!/bin/sh\n{session_checks}cat <<'OUTPUT'\n{output}\nOUTPUT\nexit {exit_code}\n")
    fake.chmod(0o755)
    for name in ("ompi_info", "mpirun"):
        fake = tmp_path / name
        fake.write_text(
            '#!/bin/sh\n' + session_checks + 'test "${OMPI_MCA_plm:-}" = isolated || exit 98\n'
            + f'case "$*" in *gmx_mpi*) exit {mpi_exit} ;; esac\n'
        )
        fake.chmod(0o755)
    fake = tmp_path / "ldd"
    fake.write_text("#!/bin/sh\necho 'libgomp.so.1 => /usr/lib64/libgomp.so.1 (0x1234)'\n")
    fake.chmod(0o755)
    env = {
        **os.environ, "PATH": f"{tmp_path}:{os.environ['PATH']}", "OMPI_MCA_plm": "rsh",
        "TMPDIR": "/scratch/unmounted-host-path",
        "OMPI_MCA_orte_tmpdir_base": "/scratch/unmounted-host-path",
        "OMPI_MCA_orte_local_tmpdir_base": "/scratch/unmounted-host-path",
        "OMPI_MCA_orte_remote_tmpdir_base": "/scratch/unmounted-host-path",
    }
    result = subprocess.run(["sh", "-c", script], env=env, capture_output=True, text=True)
    assert (result.returncode == 0) is accepted, result.stdout + result.stderr
    if exit_code:
        assert result.returncode == exit_code
        assert output in result.stdout
    if mpi_exit:
        assert result.returncode == mpi_exit


@pytest.mark.parametrize("ldd_status,diagnostic", [
    (0, "libgomp.so.1 => not found"),
    (1, "ldd: inspection failed"),
])
def test_final_image_dependency_failure_is_printed_before_gromacs(tmp_path, ldd_status, diagnostic):
    definition = Path(gromacs_container_spec.load_spec()["artifact"]["definition"]).read_text()
    script = definition.split("\n%test\n", 1)[1].replace("/tmp/", str(tmp_path) + "/")
    marker = tmp_path / "gromacs_started"
    for name in ("gmx_mpi", "mpirun", "ompi_info"):
        fake = tmp_path / name
        fake.write_text(f'#!/bin/sh\ntouch "{marker}"\nexit 0\n')
        fake.chmod(0o755)
    fake = tmp_path / "ldd"
    fake.write_text(f"#!/bin/sh\necho '{diagnostic}'\nexit {ldd_status}\n")
    fake.chmod(0o755)
    result = subprocess.run(
        ["sh", "-c", script], capture_output=True, text=True,
        env={**os.environ, "PATH": f"{tmp_path}:{os.environ['PATH']}"},
    )
    assert result.returncode == 1
    assert diagnostic in result.stdout
    assert "unresolved runtime dependencies" in result.stderr
    assert not marker.exists()


def test_package_checksums_and_no_clobber(tmp_path):
    destination = tmp_path / "package"
    gromacs_container_spec.create_package(destination)
    for line in (destination / "SHA256SUMS").read_text().splitlines():
        expected, relative = line.split("  ", 1)
        assert hashlib.sha256((destination / relative).read_bytes()).hexdigest() == expected
    before = (destination / "SHA256SUMS").read_bytes()
    with pytest.raises(FileExistsError, match="refusing to replace"):
        gromacs_container_spec.create_package(destination)
    assert (destination / "SHA256SUMS").read_bytes() == before


def test_invalid_package_is_not_published(tmp_path):
    root = tmp_path / "repo"
    for relative in gromacs_container_spec.PACKAGE_FILES:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(relative.read_bytes())
    with (root / "containers/gromacs-2025.3-mpi-cuda-l40s.def").open("a") as handle:
        handle.write("\n# altered\n")
    destination = tmp_path / "package"
    with pytest.raises(ValueError, match="SHA-256"):
        gromacs_container_spec.create_package(destination, root)
    assert not destination.exists()


@pytest.mark.parametrize("failure", [None, "build", "test", "collision", "wrong_source"])
def test_runtime_probe_preserves_sources_and_records_failures(tmp_path, failure):
    """Exercise real recovery staging with synthetic files and a fake container engine."""
    package = tmp_path / "package"
    gromacs_container_spec.create_runtime_probe_package(package)
    with pytest.raises(FileExistsError):
        gromacs_container_spec.create_runtime_probe_package(package)
    for line in (package / "SHA256SUMS").read_text().splitlines():
        digest, relative = line.split("  ", 1)
        assert hashlib.sha256((package / relative).read_bytes()).hexdigest() == digest
    script = (package / "RUN_PROBE_ON_SCC.sh").read_text()
    script = script.replace(
        "/projectnb/rise-batteries/bode/containers/runtime-probes", str(tmp_path / "probes")
    ).replace('/scratch/$USER', str(tmp_path / "scratch"))
    runner = tmp_path / "runner.sh"
    # Run from package so dirname $0 resolves to the package whose hashes are intact.
    script = script.replace('package=$(cd "$(dirname "$0")" && pwd -P)', f'package="{package}"')
    runner.write_text(script)
    (tmp_path / "scratch").mkdir()
    retained = tmp_path / "retained"
    products = [
        "gromacs-build/bin/gmx_mpi", "gromacs-build/lib/libgromacs_mpi.so.10.0.0",
        "fftw-3.3.10/.libs/libfftw3f.so", "openmpi-4.1.5/ompi/.libs/libmpi.so",
        "openmpi-4.1.5/opal/.libs/libopen-pal.so", "openmpi-4.1.5/orte/.libs/libopen-rte.so",
        "openmpi-4.1.5/orte/tools/orterun/.libs/orterun",
        "openmpi-4.1.5/orte/tools/orted/.libs/orted",
        "openmpi-4.1.5/ompi/tools/ompi_info/.libs/ompi_info",
        "openmpi-4.1.5/orte/mca/plm/isolated/.libs/mca_plm_isolated.so",
        "openmpi-4.1.5/ompi/.libs/libmpi.so.40.30.5T",
        "openmpi-4.1.5/orte/help-test.txt",
        "openmpi-4.1.5/opal/mca/pmix/pmix3x/pmix/src/mca/psec/native/.libs/mca_psec_native.so",
        "openmpi-4.1.5/opal/mca/pmix/pmix3x/pmix/src/runtime/help-pmix-runtime.txt",
    ]
    if failure == "collision":
        products.append("openmpi-4.1.5/other/.libs/libmpi.so")
    for relative in products:
        path = retained / "work" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(relative)
        path.chmod(0o755)
    originals = {p: p.read_bytes() for p in retained.rglob("*") if p.is_file()}
    evidence = tmp_path / "evidence"
    (evidence / "source/containers").mkdir(parents=True)
    (evidence / "source/containers/gromacs-2025.3-mpi-cuda-l40s.def").write_text("old definition")
    associated = tmp_path / "wrong" if failure == "wrong_source" else retained
    (evidence / "build.log").write_text(
        f"Scratch directory (retained for inspection): {associated}\n"
        "100% tests passed, 0 tests failed out of 96\nBuild/identity exit status: 255\n"
    )
    commands = tmp_path / "commands"
    commands.mkdir()
    engine = 'if [ "$1" = build ]; then printf fake-sif > "$6"; fi\n'
    if failure in {"build", "test"}:
        engine = f'if [ "$1" = {failure} ]; then exit 42; fi\n' + engine
    for name, body in {"hostname": "echo scc-i01", "singularity": engine + "exit 0"}.items():
        executable = commands / name
        executable.write_text("#!/bin/sh\n" + body + "\n")
        executable.chmod(0o755)
    result = subprocess.run(
        ["bash", str(runner), str(retained), str(evidence)], text=True, capture_output=True,
        env={**os.environ, "PATH": f"{commands}:{os.environ['PATH']}"},
    )
    assert (result.returncode == 0) is (failure is None), result.stdout + result.stderr
    assert all(p.read_bytes() == content for p, content in originals.items())
    if failure == "wrong_source":
        assert not (tmp_path / "probes").exists()
        return
    probe, = (tmp_path / "probes").iterdir()
    assert (probe / "probe.log").exists()
    assert (probe / "RUNTIME_PROBE_COMPLETE").exists() is (failure is None)
    if failure != "collision":
        assert (probe / "payload/openmpi/4.1.5/lib/openmpi/mca_plm_isolated.so").exists()
        assert (probe / "payload/openmpi/4.1.5/lib/pmix/mca_psec_native.so").exists()
        assert (probe / "payload/openmpi/4.1.5/share/pmix/help-pmix-runtime.txt").exists()
        assert not (probe / "payload/openmpi/4.1.5/lib/openmpi/mca_psec_native.so").exists()
        assert not (probe / "payload/openmpi/4.1.5/share/openmpi/help-pmix-runtime.txt").exists()
        assert not list((probe / "payload").rglob("*T"))


@pytest.mark.parametrize("build_failure,identity_failure,dependency_failure", [
    (False, False, None), (True, False, None), (False, True, None),
    (False, False, "exit"), (False, False, "not found"),
    (False, False, "missing file arguments"), (False, False, "No such file or directory"),
])
def test_documented_build_preserves_failure_logs(tmp_path, build_failure, identity_failure, dependency_failure):
    """Exercise the real documented shell flow with fake container executables."""
    package = tmp_path / "package"
    gromacs_container_spec.create_package(package)
    document = (package / "docs/gromacs_hrex_singularity_plan.md").read_text()
    script = document.split("```bash\nbash <<'BUILD'\n", 1)[1].split("\nBUILD\n```", 1)[0]
    script = script.replace("/projectnb/rise-batteries/bode/containers/builds", str(tmp_path / "builds"))
    script = script.replace('/scratch/$USER', str(tmp_path / "scratch"))
    commands = tmp_path / "bin"
    commands.mkdir()
    dependency_reply = (
        'exit 44' if dependency_failure == "exit" else
        f'echo "ldd: {dependency_failure}"; exit 0' if dependency_failure else
        'echo "libmpi.so.40 => /opt/openmpi/4.1.5/lib/libmpi.so.40"; exit 0'
    )
    fakes = {
        "hostname": "printf 'scc-i01\\n'",
        "singularity": (
            'if [ "$1" = --version ]; then echo singularity-test; exit 0; fi\n'
            + 'if [ "$1" = exec ]; then test "$4" = ldd || exit 94; '
            + dependency_reply + '; fi\n'
            + ('if [ "$1" = test ]; then exit 43; fi\n' if identity_failure else 'if [ "$1" = test ]; then exit 0; fi\n')
            + 'test "$3" = --no-cleanup || exit 92\n'
            'case "$5" in */work:/tmp) test -d "${5%:/tmp}" || exit 90 ;; *) exit 91 ;; esac\n'
            'work=${5%:/tmp}\n'
            'printf complete-install > "$work/installed-toolchain.tar.gz"\n'
            '(cd "$work" && sha256sum installed-toolchain.tar.gz > installed-toolchain.sha256)\n'
            + ("exit 42" if build_failure else 'printf fake-sif > "$6"')
        ),
        "scc-singularity": "exit 43" if identity_failure else "echo mock-identity",
    }
    for name, body in fakes.items():
        target = commands / name
        target.write_text("#!/bin/sh\n" + body + "\n")
        target.chmod(0o755)
    result = subprocess.run(
        ["bash", "-c", script], cwd=package, text=True, capture_output=True,
        env={**os.environ, "PATH": f"{commands}:{os.environ['PATH']}"},
    )
    success = not (build_failure or identity_failure or dependency_failure)
    assert (result.returncode == 0) is success, result.stdout + result.stderr
    build_dir, = (tmp_path / "builds").iterdir()
    assert (build_dir / "build.log").exists()
    assert (build_dir / "source/SHA256SUMS").exists()
    assert (build_dir / "installed-toolchain.tar.gz").read_text() == "complete-install"
    assert (build_dir / "installed-toolchain.sha256").exists()
    assert (build_dir / "BUILD_AND_IDENTITY_COMPLETE").exists() is success
    assert (build_dir / "gromacs-2025.3-mpi-cuda-l40s.sif").exists() is (not build_failure)
