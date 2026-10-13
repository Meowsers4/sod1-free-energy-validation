"""Admission checks for sealed GROMACS foreign-energy files."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import numpy as np
import pytest

from src.analysis.f64a_c2_analysis_core import RetainedBlocks
from src.analysis.f64a_c2_gromacs_inputs import (
    ParsedDhdl,
    compare_with_alchemlyb,
    load_sealed_dhdl_ladder,
    parse_gromacs_dhdl,
    relative_reduced_potentials,
    verify_pinned_json_manifest,
)


FIXTURE = Path(__file__).parent / "fixtures/f64a_stage_p_state0_dhdl_excerpt.xvg"
LAMBDAS = (0.0000, 0.0588, 0.1176, 0.1765, 0.2353, 0.2941,
           0.3529, 0.4118, 0.4706, 0.5294, 0.5882, 0.6471,
           0.7059, 0.7647, 0.8235, 0.8824, 0.9200, 0.9500,
           0.9750, 1.0000)


def _real_kwargs() -> dict:
    return dict(sampled_state=0, expected_lambdas=LAMBDAS,
                expected_temperature_K=298.15, origin_ps=0,
                duration_ps=4, stride_ps=0.2, tolerance_ps=1e-5,
                lambda_tolerance=1e-5, temperature_tolerance_K=1e-3,
                self_energy_tolerance_kj_mol=1e-5)


def test_user_supplied_gromacs_excerpt_layout_and_grid() -> None:
    assert sha256(FIXTURE.read_bytes()).hexdigest() == (
        'b22fbc6c5d5a2f06c743bdd26d7234e81eaf554782f78b4c9118db03a45adbd0'
    )
    parsed = parse_gromacs_dhdl(FIXTURE.read_text(), **_real_kwargs())
    assert len(parsed.foreign_dh_kj_mol) == 21
    assert all(len(row) == 20 for row in parsed.foreign_dh_kj_mol)
    assert parsed.blocks.boundary_index == 0
    assert len(parsed.blocks.early_indices) == 10
    assert len(parsed.blocks.late_indices) == 10
    assert parsed.foreign_dh_kj_mol[0][0] == 0.0
    assert parsed.foreign_dh_kj_mol[0][-1] == 54.937568
    reduced = relative_reduced_potentials(parsed)
    assert reduced.rows[0][0] == 0.0
    assert reduced.rows[0][-1] == pytest.approx(
        54.937568 / (0.00831446261815324 * 298.15)
    )


def test_user_excerpt_against_independent_alchemlyb_parser() -> None:
    pytest.importorskip('alchemlyb')
    parsed = parse_gromacs_dhdl(FIXTURE.read_text(), **_real_kwargs())
    comparison = compare_with_alchemlyb(
        FIXTURE, parsed=parsed, origin_ps=0,
        time_tolerance_ps=1e-5, lambda_tolerance=1e-5,
        reduced_tolerance=1e-8,
    )
    assert comparison['records'] == 21
    assert comparison['states'] == 20
    assert comparison['max_abs_difference_kT'] < 1e-8


def test_independent_comparison_allows_only_scaled_roundoff(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip('alchemlyb')
    import pandas as pd
    from alchemlyb.parsing import gmx

    parsed = ParsedDhdl(
        sampled_state=0, temperature_K=298.15,
        lambda_values=(0.0, 1.0), times_ps=(0.0,),
        foreign_dh_kj_mol=((0.0, 1e12),),
        blocks=RetainedBlocks(0, (), ()),
    )
    beta = 1 / (0.00831446261815324 * 298.15)
    expected = 1e12 * beta
    offset = 200_000.0
    index = pd.MultiIndex.from_tuples([(0.0, 0.0)])

    def reference(delta: float) -> pd.DataFrame:
        return pd.DataFrame([[offset, offset + expected + delta]],
                            columns=[0.0, 1.0], index=index)

    monkeypatch.setattr(gmx, 'extract_u_nk', lambda *args, **kwargs: reference(0.0001))
    result = compare_with_alchemlyb(
        Path('not-read.xvg'), parsed=parsed, origin_ps=0,
        time_tolerance_ps=0, lambda_tolerance=0,
        reduced_tolerance=1e-7, relative_tolerance=2e-15)
    assert result['max_abs_difference_kT'] > 1e-7
    monkeypatch.setattr(gmx, 'extract_u_nk', lambda *args, **kwargs: reference(1.0))
    with pytest.raises(ValueError, match='independent reduced potentials differ'):
        compare_with_alchemlyb(
            Path('not-read.xvg'), parsed=parsed, origin_ps=0,
            time_tolerance_ps=0, lambda_tolerance=0,
            reduced_tolerance=1e-7, relative_tolerance=2e-15)


def test_row_centered_conversion_preserves_constructed_mbar_contrast() -> None:
    pymbar = pytest.importorskip('pymbar')
    rng = np.random.default_rng(20261003)
    coordinates = [rng.normal(0, 1, 100), rng.normal(1, 1, 100)]
    absolute = np.concatenate(
        [np.vstack([0.5 * (x - state) ** 2 for state in range(2)])
         for x in coordinates], axis=1,
    )
    converted = []
    for sampled_state in range(2):
        group = absolute[:, sampled_state * 100:(sampled_state + 1) * 100]
        centered = group - group[sampled_state]
        parsed = ParsedDhdl(
            sampled_state=sampled_state, temperature_K=298.15,
            lambda_values=(0.0, 1.0), times_ps=tuple(range(1, 101)),
            foreign_dh_kj_mol=tuple(
                tuple(row * 0.00831446261815324 * 298.15)
                for row in centered.T
            ),
            blocks=RetainedBlocks(None, tuple(range(50)), tuple(range(50, 100))),
        )
        converted.append(np.asarray(relative_reduced_potentials(parsed).rows).T)
    relative = np.concatenate(converted, axis=1)
    original_fit = pymbar.MBAR(absolute, [100, 100])
    centered_fit = pymbar.MBAR(relative, [100, 100])
    original_dg = original_fit.compute_free_energy_differences()['Delta_f'][0, 1]
    centered_dg = centered_fit.compute_free_energy_differences()['Delta_f'][0, 1]
    assert centered_dg == pytest.approx(original_dg, abs=1e-10)


@pytest.mark.parametrize("old,new,error", [
    ("state 0:", "state 1:", "sampled-state"),
    ("to 1.0000", "to 0.9999", "lambda labels"),
    ("0.2000 -531793.62", "0.2000 nan", "nonfinite"),
    ("2.0000 -460003.34", "2.1000 -460003.34", "grid"),
])
def test_real_excerpt_rejects_identity_and_data_corruption(
    old: str, new: str, error: str,
) -> None:
    text = FIXTURE.read_text()
    assert old in text
    with pytest.raises(ValueError, match=error):
        parse_gromacs_dhdl(text.replace(old, new, 1), **_real_kwargs())


def _synthetic_xvg(state: int) -> str:
    return (f'@ subtitle "T = 298.15 (K) state {state}: '
            f'fep-lambda = {state:.4f}"\n'
            '@ s0 legend "Total Energy (kJ/mol)"\n'
            '@ s1 legend "dH/dlambda fep-lambda"\n'
            '@ s2 legend "delta H to 0.0000"\n'
            '@ s3 legend "delta H to 1.0000"\n'
            '@ s4 legend "pV (kJ/mol)"\n'
            + ''.join(f'{t} -10 1 {0 if state == 0 else 2} '
                      f'{3 if state == 0 else 0} 0\n' for t in range(5)))


def _sealed_tree(root: Path) -> tuple[dict[int, str], str]:
    paths = {}
    hashes = {}
    for state in range(2):
        name = f'baseline/state{state:02d}/run.part0002.xvg'
        file = root / name
        file.parent.mkdir(parents=True)
        file.write_text(_synthetic_xvg(state))
        hashes[name] = sha256(file.read_bytes()).hexdigest()
        paths[state] = name
    manifest = root / 'output-hashes.json'
    manifest.write_text(json.dumps(hashes, sort_keys=True) + '\n')
    return paths, sha256(manifest.read_bytes()).hexdigest()


def _load_kwargs(root: Path, paths: dict[int, str], digest: str) -> dict:
    return dict(root=root, manifest_name='output-hashes.json',
                manifest_sha256=digest, files_by_state=paths,
                expected_lambdas=(0.0, 1.0), expected_temperature_K=298.15,
                origin_ps=0, duration_ps=4, stride_ps=1,
                tolerance_ps=1e-9, lambda_tolerance=0,
                temperature_tolerance_K=0,
                self_energy_tolerance_kj_mol=0)


def test_pinned_full_manifest_and_state_files(tmp_path: Path) -> None:
    paths, digest = _sealed_tree(tmp_path)
    result = load_sealed_dhdl_ladder(**_load_kwargs(tmp_path, paths, digest))
    assert set(result) == {0, 1}
    assert result[1].foreign_dh_kj_mol[0] == (2.0, 0.0)
    (tmp_path / paths[1]).write_text(_synthetic_xvg(1).replace('1 -10', '1 -11'))
    with pytest.raises(ValueError, match='SHA-256 mismatch'):
        load_sealed_dhdl_ladder(**_load_kwargs(tmp_path, paths, digest))


def test_branch_origin_converts_absolute_time_without_reusing_boundary() -> None:
    shifted = _synthetic_xvg(0)
    shifted = ''.join(
        f'{int(line[0]) + 100}{line[1:]}' if line and line[0].isdigit() else line
        for line in shifted.splitlines(keepends=True)
    )
    parsed = parse_gromacs_dhdl(
        shifted, sampled_state=0, expected_lambdas=(0.0, 1.0),
        expected_temperature_K=298.15, origin_ps=100,
        duration_ps=4, stride_ps=1, tolerance_ps=1e-9,
        lambda_tolerance=0, temperature_tolerance_K=0,
        self_energy_tolerance_kj_mol=0,
    )
    assert parsed.times_ps == (0, 1, 2, 3, 4)
    assert parsed.blocks.early_indices == (1, 2)


def test_manifest_identity_and_path_guards(tmp_path: Path) -> None:
    paths, digest = _sealed_tree(tmp_path)
    with pytest.raises(ValueError, match='manifest SHA-256'):
        load_sealed_dhdl_ladder(**_load_kwargs(tmp_path, paths, '0' * 64))
    unsafe = {'../escape.xvg': '0' * 64}
    manifest = tmp_path / 'output-hashes.json'
    manifest.write_text(json.dumps(unsafe))
    unsafe_digest = sha256(manifest.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match='unsafe'):
        verify_pinned_json_manifest(
            tmp_path, manifest_name='output-hashes.json',
            manifest_sha256=unsafe_digest,
        )
