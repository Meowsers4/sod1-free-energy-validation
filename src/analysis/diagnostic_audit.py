"""Exploratory local-hysteresis audit of frozen energy archives; never re-gates.

Statistics are descriptive. Bootstrap whole variants/sites (all their repeats together),
with leave-group-out sensitivity. No row-wise p-values or prediction thresholds are fitted.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

from src.fep.analyze import (
    _KB_KCAL, _logmeanexp, collect_provenance, _check_single_protocol,
    _check_single_provenance, decorrelate_window, load_leg_replicate, solve_leg_mbar,
)
from src.prep.build import load_config

METRICS = ("net_hysteresis", "sum_absolute_hysteresis", "max_absolute_hysteresis",
           "min_adjacent_overlap", "mbar_error")


def adjacent_discrepancies(windows: list[np.ndarray], kt: float) -> np.ndarray:
    """Return signed forward-minus-reverse Zwanzig discrepancies in kcal/mol."""
    return np.asarray([
        (-_logmeanexp(-(windows[k][k + 1] - windows[k][k]))
         - _logmeanexp(windows[k + 1][k + 1] - windows[k + 1][k])) * kt
        for k in range(len(windows) - 1)
    ])


def correlations(x: np.ndarray, y: np.ndarray) -> list[float | None]:
    """Pearson and tie-aware Spearman; undefined constant samples become null."""
    if len(x) < 3 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return [None, None]
    return [float(np.corrcoef(x, y)[0, 1]),
            float(np.corrcoef(rankdata(x), rankdata(y))[0, 1])]


def cluster_indices(rows: list[dict], key: str, rng: np.random.Generator) -> np.ndarray:
    """Resample complete groups with replacement, preserving dependent siblings."""
    groups = sorted({str(row[key]) for row in rows})
    return np.concatenate([
        [i for i, row in enumerate(rows) if str(row[key]) == group]
        for group in rng.choice(groups, len(groups), replace=True)
    ])


def grouped_statistics(rows: list[dict], settings: dict,
                       outcome: str = 'disagreement_kcal') -> dict:
    """Describe associations and sensitivity to variant/site grouping."""
    result = {"n_records": len(rows), "n_variants": len({r['variant'] for r in rows}),
              "n_sites": len({r['site'] for r in rows}), "outcome": outcome,
              "metrics": {}}
    y = np.asarray([r[outcome] for r in rows])
    alpha = (1 - settings['confidence_level']) / 2
    for metric in METRICS:
        x = np.asarray([r[metric] for r in rows])
        stat = {"pearson_spearman": correlations(x, y), "grouping": {}}
        for key in ('variant', 'site'):
            # Same resamples for every metric make comparisons traceable.
            rng = np.random.default_rng(settings['bootstrap_seed'])
            draws = np.asarray([
                [np.nan if z is None else z for z in correlations(x[idx], y[idx])]
                for _ in range(settings['bootstrap_draws'])
                for idx in [cluster_indices(rows, key, rng)]
            ])
            finite = np.isfinite(draws).all(axis=1)
            interval = np.quantile(draws[finite], [alpha, 1-alpha], axis=0).T.tolist() if finite.any() else None
            leave_out = {}
            for group in sorted({str(r[key]) for r in rows}):
                keep = np.asarray([str(r[key]) != group for r in rows])
                leave_out[group] = correlations(x[keep], y[keep])
            stat['grouping'][key] = {
                "percentile_interval_pearson_spearman": interval,
                "valid_draws": int(finite.sum()), "total_draws": settings['bootstrap_draws'],
                "leave_one_group_out": leave_out,
            }
        result['metrics'][metric] = stat
    return result


def block_boundaries(n_columns: int, n_blocks: int = 4) -> list[tuple[int, int]]:
    """Split columns deterministically, assigning every column to exactly one block."""
    if n_columns < n_blocks or n_blocks < 1:
        raise ValueError(f'cannot split {n_columns} columns into {n_blocks} non-empty blocks')
    boundaries = [int(i * n_columns // n_blocks) for i in range(n_blocks + 1)]
    return list(zip(boundaries[:-1], boundaries[1:]))


def fraction_bounds(n_columns: int, start: float, stop: float) -> tuple[int, int]:
    """Map quarter-aligned fractions onto the deterministic integer block split."""
    if not (0 <= start < stop <= 1):
        raise ValueError(f'invalid fractional interval [{start}, {stop}]')
    scaled_start, scaled_stop = start * 4, stop * 4
    if not (float(scaled_start).is_integer() and float(scaled_stop).is_integer()):
        raise ValueError('temporal boundaries must align with the four predeclared blocks')
    blocks = block_boundaries(n_columns)
    first, last = int(scaled_start), int(scaled_stop) - 1
    return blocks[first][0], blocks[last][1]


def temporal_cohort(variant: str, temporal: dict) -> str:
    """Return the predeclared cohort for a variant, rejecting accidental mixing."""
    if variant in temporal['primary_variants']:
        return 'primary'
    if variant in temporal['secondary_variants']:
        return 'A4V_attempt2'
    raise ValueError(f'{variant}: not assigned to a temporal cohort')


def load_leg_replicate_interval(
    fep_dir: Path, variant: str, leg: str, rep: int, n_states: int,
    start_fraction: float, stop_fraction: float, decorrelate: bool = True,
) -> tuple[np.ndarray, np.ndarray, list[np.ndarray], dict]:
    """Load one fractional interval, selecting raw columns before decorrelation.

    Each window is split independently with the same fractional rule. This prevents a
    full-trajectory equilibration cutoff or correlation estimate from leaking future
    samples into an early checkpoint.
    """
    per_window: list[np.ndarray] = []
    raw_counts, bounds = [], []
    for w in range(n_states):
        path = fep_dir / variant / leg / f'w{w}_r{rep}.npz'
        with np.load(path) as npz:
            raw = np.asarray(npz['u_kn_window'])
            lambda_index = int(npz['lambda_index'])
        if raw.shape[0] != n_states:
            raise ValueError(
                f'{variant}/{leg}/w{w}_r{rep}: u_kn_window has {raw.shape[0]} states '
                f'but config says {n_states}'
            )
        start, stop = fraction_bounds(raw.shape[1], start_fraction, stop_fraction)
        selected = raw[:, start:stop]
        if selected.shape[1] == 0:
            raise ValueError(f'{path}: temporal interval selected no columns')
        raw_counts.append(selected.shape[1])
        bounds.append((start, stop, raw.shape[1]))
        if decorrelate:
            selected = decorrelate_window(selected, lambda_index)
        per_window.append(selected)
    n_k = np.asarray([u.shape[1] for u in per_window])
    if (n_k <= 0).any():
        raise ValueError(f'{variant}/{leg}/r{rep}: decorrelation removed every sample')
    return np.concatenate(per_window, axis=1), n_k, per_window, {
        'raw_counts': raw_counts, 'bounds': bounds, 'n_used': int(n_k.sum()),
    }


def _solve_temporal_interval(
    cfg: dict, archive: Path, variant: str, leg: str, rep: int,
    start_fraction: float, stop_fraction: float, subset: str,
) -> tuple[dict, list[dict]]:
    """Solve one declared interval and return an explicit success/failure record."""
    fcfg = cfg['fep']
    temporal = cfg['forensic_review']['temporal']
    cohort = temporal_cohort(variant, temporal)
    base = {
        'cohort': cohort, 'variant': variant, 'leg': leg, 'replicate': rep,
        'subset': subset, 'start_fraction': start_fraction,
        'stop_fraction': stop_fraction,
        'duration_ns': (stop_fraction - start_fraction)
                       * float(temporal['retained_duration_ns'][cohort][leg]),
    }
    try:
        u, n, windows, selected = load_leg_replicate_interval(
            archive/'fep', variant, leg, rep, fcfg['lambda_windows'],
            start_fraction, stop_fraction, fcfg['decorrelate'])
        solved = solve_leg_mbar(u, n)
        kt = _KB_KCAL * fcfg['temperature_K']
        delta = adjacent_discrepancies(windows, kt)
        net, total = float(abs(delta.sum())), float(abs(delta).sum())
        bounds = selected['bounds']
        row = {
            **base, 'status': 'ok', 'failure': None,
            'first_column_min': min(b[0] for b in bounds),
            'first_column_max': max(b[0] for b in bounds),
            'stop_column_min': min(b[1] for b in bounds),
            'stop_column_max': max(b[1] for b in bounds),
            'total_columns_min': min(b[2] for b in bounds),
            'total_columns_max': max(b[2] for b in bounds),
            'n_raw': int(sum(selected['raw_counts'])), 'n_used': selected['n_used'],
            'dg_kcal': solved['dg_kT'] * kt,
            'mbar_error': solved['ddg_kT'] * kt,
            'net_hysteresis': net, 'sum_absolute_hysteresis': total,
            'max_absolute_hysteresis': float(max(abs(delta))),
            'cancellation_fraction': float(1-net/total) if total else 0.0,
            'min_adjacent_overlap': solved['min_adjacent'],
            'solver_notes': solved['solver_notes'],
        }
        adjacent = [{
            'cohort': cohort, 'variant': variant, 'leg': leg, 'replicate': rep,
            'subset': subset, 'stop_fraction': stop_fraction,
            'from_window': k, 'to_window': k + 1,
            'signed_discrepancy_kcal': float(value),
        } for k, value in enumerate(delta)]
        return row, adjacent
    except Exception as exc:  # every failed interval remains part of the result set
        return {**base, 'status': 'failed', 'failure': f'{type(exc).__name__}: {exc}'}, []


def audit_archive(cfg: dict, archive: Path) -> tuple[list[dict], list[dict]]:
    """Re-solve all retained baseline/archive legs and reconcile archived estimates."""
    fcfg, settings = cfg['fep'], cfg['forensic_review']
    kt = _KB_KCAL * fcfg['temperature_K']
    with open(cfg['panel']['csv']) as stream:
        panel = {row['variant']: row for row in csv.DictReader(stream)}
    rows, adjacent = [], []
    for variant in cfg['validation']['gate_subset']:
        provenances, protocols = collect_provenance(archive/'fep', variant, fcfg['legs'],
                                                   fcfg['replicates'], fcfg['lambda_windows'])
        _check_single_provenance(variant, provenances)
        if provenances != {fcfg['framework']}:
            raise ValueError(f'{variant}: wrong engine {provenances}')
        _check_single_protocol(variant, protocols)
        record = json.loads((archive/'convergence'/f'{variant}.json').read_text())
        for leg in fcfg['legs']:
            leg_rows = []
            for rep in range(fcfg['replicates']):
                u, n, windows, n_raw = load_leg_replicate(
                    archive/'fep', variant, leg, rep, fcfg['lambda_windows'], fcfg['decorrelate'])
                if not np.isfinite(u).all():
                    raise ValueError(f'{variant}/{leg}/{rep}: non-finite energies')
                solved = solve_leg_mbar(u, n)
                delta = adjacent_discrepancies(windows, kt)
                net, total = float(abs(delta.sum())), float(abs(delta).sum())
                old = next(r for r in record['legs'] if r['leg'] == leg and r['replicate'] == rep)
                dg = solved['dg_kT'] * kt
                for actual, expected in [(dg, old['dg_kcal']), (net, old['hysteresis_kcal'])]:
                    if not np.isclose(actual, expected, rtol=0, atol=settings['reproduction_atol_kcal']):
                        raise ValueError(f'{variant}/{leg}/{rep}: archived estimate mismatch')
                row = {
                    'variant': variant, 'site': int(panel[variant]['mature_pos']),
                    'leg': leg, 'replicate': rep, 'protocol': next(iter(protocols[leg])),
                    'sampling_record': 'A4V_attempt2' if variant == 'A4V' else 'attempt1',
                    'dg_kcal': dg, 'net_hysteresis': net, 'sum_absolute_hysteresis': total,
                    'max_absolute_hysteresis': float(max(abs(delta))),
                    'cancellation_fraction': float(1-net/total) if total else 0.0,
                    'min_adjacent_overlap': solved['min_adjacent'],
                    'mbar_error': solved['ddg_kT'] * kt,
                    'n_raw': n_raw, 'n_used': int(n.sum()),
                    'solver_notes': solved['solver_notes'],
                }
                leg_rows.append(row)
                for k, value in enumerate(delta):
                    adjacent.append({'variant': variant, 'leg': leg, 'replicate': rep,
                                     'from_window': k, 'to_window': k+1,
                                     'signed_discrepancy_kcal': float(value)})
            for i, row in enumerate(leg_rows):
                siblings = [r['dg_kcal'] for j, r in enumerate(leg_rows) if i != j]
                row['disagreement_kcal'] = abs(row['dg_kcal'] - float(np.mean(siblings)))
                rows.append(row)
    return rows, adjacent


def temporal_audit(cfg: dict, archive: Path) -> dict:
    """Re-estimate every declared prefix and late block without future-data leakage."""
    fcfg, settings = cfg['fep'], cfg['forensic_review']
    temporal = settings['temporal']
    checkpoints = [float(value) for value in temporal['checkpoints']]
    comparison_start, comparison_stop = map(float, temporal['comparison_block'])
    if checkpoints != [0.25, 0.5, 0.75, 1.0]:
        raise ValueError('temporal checkpoints must remain [0.25, 0.5, 0.75, 1.0]')
    if (comparison_start, comparison_stop) != (0.75, 1.0):
        raise ValueError('temporal comparison block must remain the final quarter')
    variants = list(temporal['primary_variants']) + list(temporal['secondary_variants'])
    if set(variants) != set(cfg['validation']['gate_subset']):
        raise ValueError('temporal cohorts must partition the historical gate subset')
    if set(temporal['primary_variants']) & set(temporal['secondary_variants']):
        raise ValueError('primary and secondary temporal cohorts overlap')

    with open(cfg['panel']['csv']) as stream:
        panel = {row['variant']: row for row in csv.DictReader(stream)}
    protocol_by_variant: dict[str, dict[str, str]] = {}
    for variant in variants:
        provenances, protocols = collect_provenance(
            archive/'fep', variant, fcfg['legs'], fcfg['replicates'],
            fcfg['lambda_windows'])
        _check_single_provenance(variant, provenances)
        _check_single_protocol(variant, protocols)
        if provenances != {fcfg['framework']}:
            raise ValueError(f'{variant}: wrong engine {provenances}')
        protocol_by_variant[variant] = {
            leg: next(iter(protocols[leg])) for leg in fcfg['legs']
        }

    rows: list[dict] = []
    adjacent: list[dict] = []
    for variant in variants:
        for leg in fcfg['legs']:
            for rep in range(fcfg['replicates']):
                intervals = [('late_block', comparison_start, comparison_stop)] + [
                    ('prefix', 0.0, checkpoint) for checkpoint in checkpoints
                ]
                for subset, start, stop in intervals:
                    row, local = _solve_temporal_interval(
                        cfg, archive, variant, leg, rep, start, stop, subset)
                    row['site'] = int(panel[variant]['mature_pos'])
                    row['protocol'] = protocol_by_variant[variant][leg]
                    rows.append(row)
                    adjacent.extend(local)

    # The 100% records must reproduce the frozen audit before any interpretation.
    reconciliation = []
    for variant in variants:
        historical = json.loads((archive/'convergence'/f'{variant}.json').read_text())
        for leg in fcfg['legs']:
            for rep in range(fcfg['replicates']):
                row = next(r for r in rows if r['variant'] == variant and r['leg'] == leg
                           and r['replicate'] == rep and r['subset'] == 'prefix'
                           and r['stop_fraction'] == 1.0)
                if row['status'] != 'ok':
                    raise ValueError(f'{variant}/{leg}/r{rep}: full-duration solve failed')
                old = next(r for r in historical['legs']
                           if r['leg'] == leg and r['replicate'] == rep)
                delta_dg = row['dg_kcal'] - old['dg_kcal']
                delta_hysteresis = row['net_hysteresis'] - old['hysteresis_kcal']
                if not (np.isclose(delta_dg, 0, rtol=0,
                                   atol=settings['reproduction_atol_kcal']) and
                        np.isclose(delta_hysteresis, 0, rtol=0,
                                   atol=settings['reproduction_atol_kcal'])):
                    raise ValueError(f'{variant}/{leg}/{rep}: temporal 100% mismatch')
                reconciliation.append({
                    'variant': variant, 'leg': leg, 'replicate': rep,
                    'dg_difference_kcal': float(delta_dg),
                    'hysteresis_difference_kcal': float(delta_hysteresis),
                })

    successful = {(r['variant'], r['leg'], r['replicate'], r['subset'],
                   r['stop_fraction']): r for r in rows if r['status'] == 'ok'}
    for row in rows:
        row['movement_vs_late_block_kcal'] = None
        row['movement_comparison_is_disjoint'] = False
        row['sibling_disagreement_kcal'] = None
        if row['status'] != 'ok' or row['subset'] != 'prefix':
            continue
        key = (row['variant'], row['leg'], row['replicate'])
        if row['stop_fraction'] <= comparison_start:
            late = successful.get((*key, 'late_block', comparison_stop))
            if late:
                row['movement_vs_late_block_kcal'] = abs(row['dg_kcal'] - late['dg_kcal'])
                row['movement_comparison_is_disjoint'] = True
        siblings = [successful.get((row['variant'], row['leg'], other, 'prefix', 1.0))
                    for other in range(fcfg['replicates']) if other != row['replicate']]
        siblings = [s for s in siblings if s is not None]
        if len(siblings) == fcfg['replicates'] - 1:
            row['sibling_disagreement_kcal'] = abs(
                row['dg_kcal'] - float(np.mean([s['dg_kcal'] for s in siblings])))

    ddg_rows: list[dict] = []
    for variant in variants:
        cohort = temporal_cohort(variant, temporal)
        for rep in range(fcfg['replicates']):
            intervals = [('late_block', comparison_start, comparison_stop)] + [
                ('prefix', 0.0, checkpoint) for checkpoint in checkpoints
            ]
            for subset, start, stop in intervals:
                legs = [successful.get((variant, leg, rep, subset, stop))
                        for leg in fcfg['legs']]
                base = {
                    'cohort': cohort, 'variant': variant,
                    'site': int(panel[variant]['mature_pos']), 'replicate': rep,
                    'subset': subset, 'start_fraction': start, 'stop_fraction': stop,
                }
                if any(leg is None for leg in legs):
                    ddg_rows.append({**base, 'status': 'failed',
                                     'failure': 'one or both leg estimates failed'})
                    continue
                by_name = {row['leg']: row for row in legs}
                folded, unfolded = by_name['folded'], by_name['unfolded']
                ddg_rows.append({
                    **base, 'status': 'ok', 'failure': None,
                    'ddg_kcal': folded['dg_kcal'] - unfolded['dg_kcal'],
                    'conditional_mbar_error_kcal': float(np.hypot(
                        folded['mbar_error'], unfolded['mbar_error'])),
                    'movement_vs_late_block_kcal': None,
                    'movement_comparison_is_disjoint': False,
                    'sibling_disagreement_kcal': None,
                })
    ddg_successful = {(r['variant'], r['replicate'], r['subset'], r['stop_fraction']): r
                      for r in ddg_rows if r['status'] == 'ok'}
    for row in ddg_rows:
        if row['status'] != 'ok' or row['subset'] != 'prefix':
            continue
        if row['stop_fraction'] <= comparison_start:
            late = ddg_successful.get((row['variant'], row['replicate'],
                                       'late_block', comparison_stop))
            if late:
                row['movement_vs_late_block_kcal'] = abs(row['ddg_kcal'] - late['ddg_kcal'])
                row['movement_comparison_is_disjoint'] = True
        siblings = [ddg_successful.get((row['variant'], other, 'prefix', 1.0))
                    for other in range(fcfg['replicates']) if other != row['replicate']]
        siblings = [s for s in siblings if s is not None]
        if len(siblings) == fcfg['replicates'] - 1:
            row['sibling_disagreement_kcal'] = abs(
                row['ddg_kcal'] - float(np.mean([s['ddg_kcal'] for s in siblings])))

    associations = {}
    primary_rows = [r for r in rows if r['cohort'] == 'primary'
                    and r['subset'] == 'prefix' and r['status'] == 'ok']
    for leg in fcfg['legs']:
        for checkpoint in checkpoints:
            checkpoint_rows = [r for r in primary_rows if r['leg'] == leg
                               and r['stop_fraction'] == checkpoint]
            for outcome in ('movement_vs_late_block_kcal', 'sibling_disagreement_kcal'):
                eligible = [r for r in checkpoint_rows if r[outcome] is not None]
                if eligible:
                    associations[f'{leg}/{checkpoint:.2f}/{outcome}'] = grouped_statistics(
                        eligible, settings, outcome)

    return {
        'status': 'exploratory_post_verdict_not_a_gate',
        'settings': temporal,
        'limitations': [
            'Later blocks and full repeats are comparison data, not ground truth.',
            'Only prefixes through 75% are disjoint from the final-quarter comparison.',
            'Consecutive prefixes and sibling-derived outcomes are dependent.',
            'Stable energy estimates cannot exclude a shared unvisited conformation.',
            'A4V is a separate 9 ns/3 ns attempt-2 cohort; its 3 ns folded history is lost.',
        ],
        'reconciliation': reconciliation, 'leg_records': rows,
        'ddg_records': ddg_rows, 'adjacent_records': adjacent,
        'associations': associations,
    }


def plot_audit(rows: list[dict], adjacent: list[dict], output: Path) -> None:
    """Display cancellation and associations without fitting a decision threshold."""
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    focus = [r for r in adjacent if r['variant']=='F64A' and r['leg']=='folded' and r['replicate']==1]
    axes[0,0].bar([r['from_window'] for r in focus], [r['signed_discrepancy_kcal'] for r in focus], color='#31688e')
    axes[0,0].axhline(0, color='black', linewidth=.6)
    axes[0,0].set(xlabel='Adjacent pair (starting window index)', ylabel='Signed discrepancy (kcal/mol)',
                  title='F64A folded r1: signed discrepancies cancel')
    folded = [r for r in rows if r['leg']=='folded']
    for ax, metric, label in zip(axes.flat[1:], METRICS[:3],
                                 ('Absolute net sum', 'Sum of absolute discrepancies', 'Largest absolute discrepancy')):
        for row in folded:
            focus_row = row['variant']=='F64A' and row['replicate']==1
            ax.scatter(row[metric], row['disagreement_kcal'], color='#b44747' if focus_row else '#31688e',
                       marker='s' if row['variant']=='A4V' else 'o', s=65 if focus_row else 32)
        ax.set(xlabel=f'{label} (kcal/mol)', ylabel='Sibling disagreement (kcal/mol)', title=label)
    fig.suptitle('Exploratory archive audit: 24 folded records, 8 variants, 6 sites\n'
                 'A4V squares use 9 ns; other records use 3 ns. Red: F64A r1.', fontsize=12)
    fig.tight_layout(rect=(0,0,1,.93))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_temporal_trajectories(rows: list[dict], output: Path) -> None:
    """Plot every leg/repeat prefix estimate and the separately solved late block."""
    import matplotlib.pyplot as plt

    variants = sorted({r['variant'] for r in rows},
                      key=lambda v: (v == 'A4V', v))
    fig, axes = plt.subplots(4, 4, figsize=(15, 12), sharex=True)
    colors = ('#31688e', '#35b779', '#d95f02')
    for index, (variant, leg) in enumerate(
            (item for variant in variants for item in ((variant, 'folded'),
                                                       (variant, 'unfolded')))):
        ax = axes.flat[index]
        selected = [r for r in rows if r['variant'] == variant and r['leg'] == leg
                    and r['status'] == 'ok']
        for rep, color in enumerate(colors):
            prefix = sorted([r for r in selected if r['replicate'] == rep
                             and r['subset'] == 'prefix'],
                            key=lambda r: r['stop_fraction'])
            ax.errorbar([r['stop_fraction'] for r in prefix],
                        [r['dg_kcal'] for r in prefix],
                        yerr=[r['mbar_error'] for r in prefix], marker='o',
                        color=color, linewidth=1, markersize=3, capsize=2,
                        label=f'r{rep}')
            late = next((r for r in selected if r['replicate'] == rep
                         and r['subset'] == 'late_block'), None)
            if late:
                ax.errorbar([1.08], [late['dg_kcal']], yerr=[late['mbar_error']],
                            marker='x', color=color, linestyle='none', capsize=2)
        duration = max(r['duration_ns'] for r in selected if r['subset'] == 'prefix')
        suffix = ' (separate cohort)' if variant == 'A4V' else ''
        ax.set_title(f'{variant} {leg}, {duration:g} ns{suffix}', fontsize=9)
        ax.axvspan(.75, 1.0, color='0.92', zorder=-2)
        ax.grid(alpha=.2)
        if index % 4 == 0:
            ax.set_ylabel('Leg ΔG (kcal/mol)')
        if index // 4 == 3:
            ax.set_xlabel('Cumulative retained fraction (x = late block)')
        ax.set_xticks([.25, .5, .75, 1.0, 1.08], ['25', '50', '75', '100', 'late'])
    axes.flat[0].legend(frameon=False, ncol=3, fontsize=8)
    fig.suptitle('Retrospective temporal estimates; error bars are conditional MBAR uncertainty\n'
                 'Late symbols use only the final quarter and are not ground truth', fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, .95))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_temporal_local(adjacent: list[dict], output: Path) -> None:
    """Expose signed adjacent-window discrepancies for all repeats/checkpoints."""
    import matplotlib.pyplot as plt

    prefix = [r for r in adjacent if r['subset'] == 'prefix']
    row_keys = sorted({(r['variant'], r['leg'], r['replicate']) for r in prefix},
                      key=lambda x: (x[0] == 'A4V', x[0], x[1], x[2]))
    checkpoints = sorted({r['stop_fraction'] for r in prefix})
    n_pairs = max(r['to_window'] for r in prefix)
    matrix = np.full((len(row_keys), len(checkpoints) * n_pairs), np.nan)
    row_index = {key: i for i, key in enumerate(row_keys)}
    checkpoint_index = {value: i for i, value in enumerate(checkpoints)}
    for row in prefix:
        y = row_index[(row['variant'], row['leg'], row['replicate'])]
        x = checkpoint_index[row['stop_fraction']] * n_pairs + row['from_window']
        matrix[y, x] = row['signed_discrepancy_kcal']
    finite = np.abs(matrix[np.isfinite(matrix)])
    vmax = float(np.quantile(finite, .98)) if finite.size else 1.0
    vmax = max(vmax, np.finfo(float).eps)
    fig, ax = plt.subplots(figsize=(16, 11))
    image = ax.imshow(matrix, aspect='auto', cmap='RdBu_r', vmin=-vmax, vmax=vmax,
                      interpolation='nearest')
    for i in range(1, len(checkpoints)):
        ax.axvline(i * n_pairs - .5, color='black', linewidth=.5)
    ax.set_xticks([i*n_pairs + (n_pairs-1)/2 for i in range(len(checkpoints))],
                  [f'{value:.0%}' for value in checkpoints])
    ax.set_yticks(range(len(row_keys)),
                  [f'{v} {leg[0].upper()} r{rep}' for v, leg, rep in row_keys], fontsize=7)
    ax.set_xlabel('Cumulative checkpoint (each block spans adjacent pairs 0–18)')
    ax.set_ylabel('Variant / leg / repeat')
    ax.set_title('Signed local forward−reverse discrepancies over retained time\n'
                 'Color is clipped at the 98th percentile for readability')
    fig.colorbar(image, ax=ax, label='Signed discrepancy (kcal/mol)', shrink=.8)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def write_rows_csv(path: Path, rows: list[dict]) -> None:
    """Write heterogeneous success/failure records without dropping failure fields."""
    fieldnames = list(dict.fromkeys(key for row in rows for key in row))
    with open(path, 'w') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='config/pipeline.yaml')
    parser.add_argument('--archive-root', type=Path)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--temporal', action='store_true',
                        help='run the separate retrospective checkpoint analysis')
    args = parser.parse_args()
    cfg = load_config(args.config)
    settings = cfg['forensic_review']
    archive = args.archive_root or Path(settings['main_archive'])
    temporal = settings.get('temporal') if args.temporal else None
    output = args.output_dir or Path(temporal['output_dir'] if temporal
                                    else settings['output_dir'])
    output.mkdir(parents=True, exist_ok=True)
    if temporal:
        result = temporal_audit(cfg, archive)
        outputs = temporal['outputs']
        (output/outputs['report']).write_text(
            json.dumps(result, indent=2, allow_nan=False)+'\n')
        write_rows_csv(output/outputs['leg_records'], result['leg_records'])
        write_rows_csv(output/outputs['ddg_records'], result['ddg_records'])
        write_rows_csv(output/outputs['adjacent_records'], result['adjacent_records'])
        plot_temporal_trajectories(result['leg_records'],
                                   output/outputs['trajectories_figure'])
        plot_temporal_local(result['adjacent_records'], output/outputs['local_figure'])
        failed = sum(r['status'] != 'ok' for r in result['leg_records'])
        print(f"Solved {len(result['leg_records'])-failed}/{len(result['leg_records'])} "
              f"temporal leg intervals; wrote {output}")
        return
    rows, adjacent = audit_archive(cfg, archive)
    strata = {}
    for leg in cfg['fep']['legs']:
        for cohort in ('all_retained', 'uniform_attempt1_without_A4V'):
            selected = [r for r in rows if r['leg']==leg and
                        (cohort=='all_retained' or r['variant']!='A4V')]
            strata[f'{leg}/{cohort}'] = grouped_statistics(selected, settings)
    result = {
        'status': 'exploratory_post_verdict_not_a_gate', 'settings': settings,
        'limitations': ['Few variant/site groups; bootstrap intervals are approximate.',
                       'Sibling disagreement is dependent and is not accuracy.',
                       'A4V original windows are lost; its retained data use 9 ns folded.',
                       'No new diagnostic threshold or superiority claim is validated.'],
        'rows': rows, 'strata': strata,
    }
    (output/'diagnostic_audit.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    for name, data in [('diagnostic_records.csv', rows), ('adjacent_discrepancies.csv', adjacent)]:
        write_rows_csv(output/name, data)
    plot_audit(rows, adjacent, output/'diagnostic_cancellation.png')
    print(f'Reconciled {len(rows)} records and {len(adjacent)} adjacent pairs; wrote {output}')


if __name__ == '__main__':
    main()
