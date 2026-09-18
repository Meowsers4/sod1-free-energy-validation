"""Hash-bound CPU description of raw F64A energies; no new fits or cutoffs."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import math
import os
import platform
import tempfile
from pathlib import Path

import numpy as np
import yaml

from src.analysis.f64a_late_window_audit import ROOT, sha256, validate_report

DEFAULT_CONFIG = ROOT / "docs/f64a_raw_energy_audit.yaml"


def describe_series(
    x: np.ndarray, stride_ps: float, lags: list[int], quantiles: list[float]
) -> dict:
    """Descriptive moments and biased FFT autocorrelations, without error bars/tests.

    ACF(lag) = sum((x[t]-mean)*(x[t+lag]-mean))/sum((x-mean)**2).
    It is descriptive only for changing data; no independence/stationarity is inferred.
    """
    x = np.asarray(x, dtype=float)
    if x.ndim != 1 or not len(x) or not np.isfinite(x).all() or stride_ps <= 0:
        raise ValueError("invalid raw series")
    centered = x - x.mean()
    variance_sum = float(centered @ centered)
    n = len(x)
    correlations = {}
    if variance_sum > 0:
        size = 1 << (2 * n - 1).bit_length()
        spectrum = np.fft.rfft(centered, n=size)
        products = np.fft.irfft(spectrum * spectrum.conjugate(), n=size)[:n]
    for lag in lags:
        correlations[str(lag)] = (
            float(products[lag] / variance_sum)
            if variance_sum > 0 and lag < n
            else None
        )
    t = np.arange(n) * stride_ps / 1000
    t -= t.mean()
    slope = float(t @ centered / (t @ t)) if n > 1 else None
    split = n // 2
    return {
        "n_raw": n,
        "mean_kT": float(x.mean()),
        "std_kT": float(x.std()),
        "quantiles_kT": {str(q): float(np.quantile(x, q)) for q in quantiles},
        "linear_slope_kT_per_ns": slope,
        "second_half_minus_first_half_mean_kT": float(
            x[split:].mean() - x[:split].mean()
        )
        if split
        else None,
        "acf_biased": correlations,
        "acf_lags_ps": {str(lag): lag * stride_ps for lag in lags},
    }


def observables(u: np.ndarray, window: int) -> dict[str, np.ndarray]:
    """Include both adjacent energy differences; never substitute for endpoint ΔG."""
    result = {"sampled_state_u": u[window]}
    if window > 0:
        result["previous_minus_sampled_u"] = u[window - 1] - u[window]
    if window + 1 < u.shape[0]:
        result["next_minus_sampled_u"] = u[window + 1] - u[window]
    return result


def production_hashes(report: dict, windows: int, repeats: int) -> dict[str, str]:
    """Select only production output matrices, not the separately hashed source NPZs."""
    hashes = {
        Path(p).name: digest
        for p, digest in report["input_sha256"].items()
        if "/production/fep/F64A/folded/" in p and p.endswith(".npz")
    }
    expected = {f"w{w}_r{r}.npz" for w in range(windows) for r in range(repeats)}
    if set(hashes) != expected:
        raise ValueError("reference lacks exactly one hash for each production matrix")
    return hashes


def load_matrix(
    path: Path, digest: str, window: int, rep: int, pilot: dict, report: dict
) -> np.ndarray:
    """Verify exact bytes, shape, finiteness, protocol and simulation ancestry."""
    if sha256(path) != digest:
        raise ValueError(f"production NPZ hash mismatch: {path.name}")
    with np.load(path, allow_pickle=False) as data:
        expected = {
            "pilot_id": pilot["pilot_id"],
            "provenance": "gromacs_pmx",
            "lambda_index": window,
            "replicate": rep,
            "n_states": pilot["lambda_windows"],
            "protocol": report["simulation_protocol"],
            "source_protocol": pilot["source_protocol"],
        }
        for key, value in expected.items():
            if data[key].shape != () or str(data[key]) != str(value):
                raise ValueError(f"output metadata mismatch: {path.name} {key}")
        for key, expected_identity in (
            ("code_identity_json", report["simulation_code_identity"]),
            ("source_code_identity_json", report["source_code_identity"]),
        ):
            if json.loads(str(data[key])) != expected_identity:
                raise ValueError(f"output ancestry mismatch: {path.name} {key}")
        u = np.asarray(data["u_kn_window"], dtype=float)
        if (
            u.shape != (pilot["lambda_windows"], pilot["target_samples_per_window"])
            or not np.isfinite(u).all()
        ):
            raise ValueError(f"invalid raw energies: {path.name}")
    return u


def inspect_window(
    u: np.ndarray,
    window: int,
    rep: int,
    report: dict,
    blocks: list[dict],
    pilot: dict,
    spec: dict,
) -> tuple[list[dict], list[dict]]:
    """Describe full blocks and saved raw suffixes; never rerun trim detection."""
    rows, bins = [], []
    stride = pilot["energy_stride_ps"]
    for block in blocks:
        start, stop = block["start"], block["stop"]
        saved = [
            r
            for r in report["records"]
            if r["block"] == block["label"] and r["replicate"] == rep
        ]
        for label, whole in observables(u[:, start:stop], window).items():
            row = {
                "block": block["label"],
                "replicate": rep,
                "window": window,
                "observable": label,
                "units": "reduced potential (kT), not free energy",
                "full_block": describe_series(
                    whole, stride, spec["acf_lags_samples"], spec["quantiles"]
                ),
                "policy_raw_suffixes": [],
            }
            for fit in saved:
                (d,) = [d for d in fit["window_diagnostics"] if d["window"] == window]
                cut = d["trim_start_column"]
                suffix = describe_series(
                    whole[cut:], stride, spec["acf_lags_samples"], spec["quantiles"]
                )
                row["policy_raw_suffixes"].append(
                    {
                        "policy": fit["policy"],
                        "cutoff_raw_column": start + cut,
                        "cutoff_retained_ns": (start + cut) * stride / 1000,
                        "suffix_mean_minus_full_mean_kT": suffix["mean_kT"]
                        - row["full_block"]["mean_kT"],
                        "saved_selection_diagnostics": d,
                        "raw_suffix": suffix,
                    }
                )
            rows.append(row)
            for offset in range(0, len(whole), spec["bin_samples"]):
                values = whole[offset : offset + spec["bin_samples"]]
                column = start + offset
                bins.append(
                    {
                        "block": block["label"],
                        "replicate": rep,
                        "window": window,
                        "observable": label,
                        "raw_column_start": column,
                        "raw_column_stop": column + len(values),
                        "retained_time_midpoint_ns": (column + (len(values) - 1) / 2)
                        * stride
                        / 1000,
                        "n_raw": len(values),
                        "mean_kT": float(values.mean()),
                        "std_kT": float(values.std()),
                    }
                )
    return rows, bins


def plot_bins(
    bins: list[dict],
    report: dict,
    blocks: list[dict],
    pilot: dict,
    spec: dict,
    directory: Path,
) -> list[str]:
    """Draw every window/repeat, centered within each path, with fixed saved cutoffs."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = []
    labels = sorted({b["observable"] for b in bins})
    for label in labels:
        times = sorted({b["retained_time_midpoint_ns"] for b in bins})
        values = np.full(
            (pilot["replicates"], pilot["lambda_windows"], len(times)), np.nan
        )
        index = {t: i for i, t in enumerate(times)}
        for b in bins:
            if b["observable"] == label:
                values[
                    b["replicate"], b["window"], index[b["retained_time_midpoint_ns"]]
                ] = b["mean_kT"]
        for r in range(pilot["replicates"]):
            for w in range(pilot["lambda_windows"]):
                if np.isfinite(values[r, w]).any():
                    values[r, w] -= np.nanmean(values[r, w])
        bound = (
            float(np.nanpercentile(abs(values), spec["plot_color_percentile"])) or 1.0
        )
        fig, axes = plt.subplots(
            1,
            pilot["replicates"],
            figsize=(15, 7),
            constrained_layout=True,
            squeeze=False,
        )
        dt = spec["bin_samples"] * pilot["energy_stride_ps"] / 1000
        for rep, ax in enumerate(axes[0]):
            image = ax.imshow(
                values[rep],
                origin="lower",
                aspect="auto",
                cmap="coolwarm",
                vmin=-bound,
                vmax=bound,
                extent=[
                    times[0] - dt / 2,
                    times[-1] + dt / 2,
                    -0.5,
                    pilot["lambda_windows"] - 0.5,
                ],
            )
            for block in blocks:
                (saved,) = [
                    r
                    for r in report["records"]
                    if r["policy"] == "adaptive"
                    and r["block"] == block["label"]
                    and r["replicate"] == rep
                ]
                ax.scatter(
                    [
                        d["trim_start_column_global"] * pilot["energy_stride_ps"] / 1000
                        for d in saved["window_diagnostics"]
                    ],
                    [d["window"] for d in saved["window_diagnostics"]],
                    facecolors="none",
                    edgecolors="black",
                    s=18,
                    linewidths=0.7,
                )
                ax.axvline(
                    block["start"] * pilot["energy_stride_ps"] / 1000,
                    color="black",
                    alpha=0.3,
                    linewidth=0.7,
                )
            ax.set(
                title=f"Repeat r{rep}",
                xlabel="Retained time (ns)",
                ylabel="Lambda window",
            )
            ax.set_yticks(range(pilot["lambda_windows"]))
        fig.colorbar(
            image,
            ax=axes.ravel().tolist(),
            label="Bin mean minus path mean (kT); color may saturate",
        )
        fig.suptitle(
            f"{label}: raw {spec['bin_samples']}-record bin means\nCircles: saved adaptive suffix starts; no stationarity or structural inference",
            fontsize=12,
        )
        name = label + ".png"
        fig.savefig(directory / name, dpi=spec["plot_dpi"])
        plt.close(fig)
        names.append(name)
    return names


def audit(
    config: Path = DEFAULT_CONFIG,
    npz_dir: Path | None = None,
    output_dir: Path | None = None,
) -> Path:
    """Require all 60 raw inputs before analysis; publish a new report last."""
    spec = yaml.safe_load(config.read_text())
    evidence_config = ROOT / spec["report_config"]
    evidence = yaml.safe_load(evidence_config.read_text())
    report_path = ROOT / evidence["input"]
    if sha256(report_path) != evidence["input_sha256"]:
        raise ValueError("reference report hash mismatch")
    report = json.loads(report_path.read_text())
    design_path, pilot_path = (
        ROOT / evidence["registered_design"],
        ROOT / evidence["pilot_config"],
    )
    design, pilot = (yaml.safe_load(p.read_text()) for p in (design_path, pilot_path))
    validate_report(report, design, pilot["lambda_windows"], pilot["replicates"])
    if (
        type(spec["bin_samples"]) is not int
        or spec["bin_samples"] <= 0
        or not spec["acf_lags_samples"]
        or any(type(lag) is not int or lag <= 0 for lag in spec["acf_lags_samples"])
        or any(not math.isfinite(q) or not 0 <= q <= 1 for q in spec["quantiles"])
        or not 0 < spec["plot_color_percentile"] <= 100
        or spec["plot_dpi"] <= 0
    ):
        raise ValueError("invalid raw audit configuration")
    blocks = [b for b in design["blocks"] if b["label"] in spec["blocks"]]
    if len(blocks) != len(spec["blocks"]) or any(
        (b["stop"] - b["start"]) % spec["bin_samples"] for b in blocks
    ):
        raise ValueError("invalid blocks/bin width")
    folder = (npz_dir or ROOT / spec["npz_dir"]).resolve()
    output = (output_dir or ROOT / spec["output_dir"]).resolve()
    if output.exists():
        raise FileExistsError(f"refusing existing raw-audit output directory: {output}")
    hashes = production_hashes(report, pilot["lambda_windows"], pilot["replicates"])
    if {p.name for p in folder.glob("w*_r*.npz")} != set(hashes):
        raise FileNotFoundError(
            f"need exactly {len(hashes)} production NPZs in {folder}; no GPU producer will run"
        )
    dependencies = [
        config,
        evidence_config,
        report_path,
        design_path,
        pilot_path,
        Path(__file__),
        ROOT / "src/analysis/f64a_late_window_audit.py",
    ]
    identities = {str(p.resolve()): sha256(p) for p in dependencies}
    for w in range(pilot["lambda_windows"]):
        for r in range(pilot["replicates"]):
            name = f"w{w}_r{r}.npz"
            load_matrix(folder / name, hashes[name], w, r, pilot, report)
    rows, bins = [], []
    for w in range(pilot["lambda_windows"]):
        for r in range(pilot["replicates"]):
            name = f"w{w}_r{r}.npz"
            u = load_matrix(folder / name, hashes[name], w, r, pilot, report)
            a, b = inspect_window(u, w, r, report, blocks, pilot, spec)
            rows.extend(a)
            bins.extend(b)
            print(f"Inspected {name}", flush=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        dir=output.parent, prefix=".f64a-raw-audit-"
    ) as temp:
        staging = Path(temp)
        plots = plot_bins(bins, report, blocks, pilot, spec, staging)
        if any(
            sha256(folder / name) != digest for name, digest in hashes.items()
        ) or any(sha256(Path(p)) != digest for p, digest in identities.items()):
            raise ValueError("raw audit inputs or code changed during execution")
        value = {
            "audit_id": "f64a_raw_energy_v1",
            "exploratory_post_result": True,
            "raw_inputs_validated": len(hashes),
            "npz_dir": str(folder),
            "input_npz_sha256": hashes,
            "dependency_sha256": identities,
            "source_analysis_identity": report["analysis_identity"],
            "source_simulation_protocol": report["simulation_protocol"],
            "runtime": {
                "python": platform.python_version(),
                "packages": {
                    p: importlib.metadata.version(p)
                    for p in ("numpy", "matplotlib", "PyYAML")
                },
            },
            "configuration": spec,
            "series_records": rows,
            "time_bins": bins,
            "figures": plots,
            "limitations": [
                "No MBAR refits, new cutoffs, pass threshold, stationarity test or GPU work.",
                "Suffix summaries use unthinned raw suffixes, not the saved thinned samples.",
                "Descriptive trends, quantiles and ACF are not free energies or uncertainty estimates.",
                "Energy changes/ACF cannot identify structural mechanisms or cover unvisited conformations.",
                "NPZ hashes/metadata verified; no independent checkpoint/XVG validation.",
            ],
        }
        (staging / "raw_energy_audit.json").write_text(
            json.dumps(value, indent=2, allow_nan=False) + "\n"
        )
        output.mkdir()  # Exclusive creation after computation; no existing evidence overwritten.
        for name in plots + [
            "raw_energy_audit.json"
        ]:  # Successful JSON is published last.
            os.link(staging / name, output / name)
    print(f"Wrote {output / 'raw_energy_audit.json'}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--npz-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    audit(args.config, args.npz_dir, args.output_dir)


if __name__ == "__main__":
    main()
