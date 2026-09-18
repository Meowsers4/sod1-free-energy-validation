"""Scientific regression tests for the exploratory audit (separate from the gate)."""
from pathlib import Path

import numpy as np
import pytest

import src.analysis.diagnostic_audit as diagnostic_audit
from src.analysis.diagnostic_audit import (
    adjacent_discrepancies, block_boundaries, cluster_indices, correlations,
    fraction_bounds, load_leg_replicate_interval, temporal_cohort,
)
from src.analysis.methods_figures import g93a_redox_summary


def test_signed_window_discrepancies_can_cancel():
    # The first adjacent pair disagrees by +2 kT, the second by -2 kT.
    windows = [np.array([[0.], [1.], [0.]]),
               np.array([[1.], [0.], [-1.]]),
               np.array([[0.], [-1.], [0.]])]
    discrepancies = adjacent_discrepancies(windows, 1.)
    assert discrepancies == pytest.approx([2., -2.])
    assert abs(discrepancies.sum()) == 0
    assert abs(discrepancies).sum() == 4


def test_bootstrap_never_separates_dependent_siblings():
    rows = [{'variant': v, 'replicate': r} for v in ('A', 'B', 'C') for r in range(3)]
    indices = cluster_indices(rows, 'variant', np.random.default_rng(13))
    for v in ('A', 'B', 'C'):
        counts = [sum(rows[i]['variant']==v and rows[i]['replicate']==r for i in indices) for r in range(3)]
        assert len(set(counts)) == 1
    assert len(indices) == len(rows)


def test_spearman_uses_average_ranks_for_ties():
    _, rho = correlations(np.array([1.,1.,3.,4.]), np.array([1.,2.,3.,4.]))
    assert rho == pytest.approx(0.9486832980505138)
    assert correlations(np.ones(4), np.arange(4)) == [None, None]


def test_redox_interval_includes_variation_in_both_arms():
    def record(values):
        return {'legs':[{'leg':'folded','replicate':i,'dg_kcal':v} for i,v in enumerate(values)]}
    a, b = record([0.,1.,2.]), record([1.,2.,3.])
    result = g93a_redox_summary(a,b,0.95)
    assert result['shift'] == 1
    assert result['shift_standard_error'] == pytest.approx(np.sqrt(2/3))
    assert result['welch_degrees_of_freedom'] == pytest.approx(4)
    assert result['shift_interval'] == pytest.approx([-1.2669579355,3.2669579355])


def _write_temporal_windows(root: Path, columns: int = 8) -> None:
    directory = root/'fep'/'F64A'/'folded'
    directory.mkdir(parents=True)
    for window in range(2):
        data = np.vstack([np.arange(columns), np.arange(columns) + window + 1.0])
        np.savez(directory/f'w{window}_r0.npz', u_kn_window=data,
                 lambda_index=window, provenance='gromacs_pmx', protocol='test')


def test_quarter_blocks_cover_columns_once_without_overlap():
    blocks = block_boundaries(11)
    assert blocks == [(0, 2), (2, 5), (5, 8), (8, 11)]
    assert [i for start, stop in blocks for i in range(start, stop)] == list(range(11))
    assert fraction_bounds(11, 0, .75)[1] == fraction_bounds(11, .75, 1)[0]


def test_early_interval_is_selected_before_decorrelation(tmp_path):
    _write_temporal_windows(tmp_path)
    _, counts, windows, info = load_leg_replicate_interval(
        tmp_path/'fep', 'F64A', 'folded', 0, 2, 0, .25, decorrelate=False)
    assert counts.tolist() == [2, 2]
    assert all(window.shape == (2, 2) for window in windows)
    assert all(np.max(window[0]) == 1 for window in windows)
    assert info['bounds'] == [(0, 2, 8), (0, 2, 8)]


def test_full_interval_matches_unsliced_loader(tmp_path):
    _write_temporal_windows(tmp_path)
    full = load_leg_replicate_interval(
        tmp_path/'fep', 'F64A', 'folded', 0, 2, 0, 1, decorrelate=False)
    original = diagnostic_audit.load_leg_replicate(
        tmp_path/'fep', 'F64A', 'folded', 0, 2, decorrelate=False)
    assert np.array_equal(full[0], original[0])
    assert np.array_equal(full[1], original[1])
    assert all(np.array_equal(a, b) for a, b in zip(full[2], original[2]))


def test_a4v_cannot_enter_primary_temporal_cohort():
    settings = {'primary_variants': ['F64A'], 'secondary_variants': ['A4V']}
    assert temporal_cohort('F64A', settings) == 'primary'
    assert temporal_cohort('A4V', settings) == 'A4V_attempt2'
    with pytest.raises(ValueError, match='not assigned'):
        temporal_cohort('G127X', settings)


def test_failed_interval_is_recorded_not_silently_dropped(tmp_path, monkeypatch):
    _write_temporal_windows(tmp_path)
    cfg = {
        'fep': {'lambda_windows': 2, 'decorrelate': False, 'temperature_K': 298.15},
        'forensic_review': {'temporal': {
            'primary_variants': ['F64A'], 'secondary_variants': [],
            'retained_duration_ns': {'primary': {'folded': 3.0}},
        }},
    }
    monkeypatch.setattr(diagnostic_audit, 'solve_leg_mbar',
                        lambda *_: (_ for _ in ()).throw(RuntimeError('solver stopped')))
    row, adjacent = diagnostic_audit._solve_temporal_interval(
        cfg, tmp_path, 'F64A', 'folded', 0, 0, .25, 'prefix')
    assert row['status'] == 'failed'
    assert row['failure'] == 'RuntimeError: solver stopped'
    assert adjacent == []
