"""Assemble manuscript figures from registered, hashed CPU reports.

This module recomputes no free energy. It reads the registered F64A v1 block
report and v2 continuation report, verifies their SHA-256 and every value the
publication outline quotes, and draws the Result 6 temporal figure. It also
copies the completed lambda-comparator figures byte-for-byte as supplementary
panels after verifying the comparator report and each source-image hash. Outputs go to a fresh
directory; an existing output directory is never overwritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]

# Categorical slots 1-3 of the dataviz reference palette; all-pairs validated
# (worst CVD dE 9.2, normal-vision dE 24.0). Slot 3 is below 3:1 contrast on a
# light surface, so every repeat is also direct-labelled and has its own marker.
REPEAT_COLORS = ("#2a78d6", "#eb6834", "#1baf7a")
REPEAT_MARKERS = ("o", "s", "^")
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
GRID = "#e4e3df"


def sha256_file(path: str | Path) -> str:
    """Return the hex SHA-256 of ``path``."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_spec(path: str | Path) -> dict:
    """Load the figure specification YAML."""
    with open(path) as handle:
        return yaml.safe_load(handle)


def _resolve(root: Path, relative: str) -> Path:
    return (root / relative).resolve()


def load_verified_reports(spec: dict, root: Path = ROOT) -> dict[str, dict]:
    """Load every hashed input report, refusing any SHA-256 mismatch."""
    reports: dict[str, dict] = {}
    for name, entry in spec["inputs"].items():
        if "sha256" not in entry:
            continue
        path = _resolve(root, entry["path"])
        if not path.exists():
            raise FileNotFoundError(path)
        actual = sha256_file(path)
        if actual != entry["sha256"]:
            raise ValueError(
                f"{name}: SHA-256 {actual} does not match registered {entry['sha256']}"
            )
        reports[name] = json.loads(path.read_text())
    return reports


def lambda_vector(spec: dict, root: Path = ROOT) -> list[float]:
    """Return the actual lambda schedule from ``config/pipeline.yaml``."""
    with open(_resolve(root, spec["inputs"]["pipeline_config"]["path"])) as handle:
        config = yaml.safe_load(handle)
    values = config["fep"]["lambda_vector"]
    if values is None or len(values) != config["fep"]["lambda_windows"]:
        raise ValueError("pipeline lambda_vector must list every lambda window")
    return [float(value) for value in values]


def _record(report: dict, replicate: int, block: str, policy: str | None) -> dict:
    matches = [
        record
        for record in report["records"]
        if record["replicate"] == replicate
        and record["block"] == block
        and record.get("policy", "adaptive") == (policy or "adaptive")
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one record for r{replicate} {block} {policy}, got {len(matches)}")
    return matches[0]


def temporal_data(spec: dict, reports: dict[str, dict]) -> dict:
    """Collect every plotted value for the temporal figure from the reports."""
    temporal = spec["temporal"]
    policy = temporal["policy"]
    v2 = reports["continuation_v2"]
    replicates = sorted({record["replicate"] for record in v2["records"]})
    if replicates != [0, 1, 2]:
        raise ValueError(f"expected repeats 0-2, got {replicates}")

    blocks = []
    for block in temporal["blocks"]:
        report = reports[block["report"]]
        rows = []
        for replicate in replicates:
            record = _record(
                report, replicate, block["label"],
                policy if block["report"] == "continuation_v2" else None,
            )
            rows.append({
                "replicate": replicate,
                "dg_kcal": record["dg_kcal"],
                "mbar_error_kcal": record["mbar_error_kcal"],
                "net_hysteresis_kcal": record["net_hysteresis_kcal"],
                "sum_absolute_hysteresis_kcal": record["sum_absolute_hysteresis_kcal"],
                "max_absolute_hysteresis_kcal": record["max_absolute_hysteresis_kcal"],
            })
        blocks.append({**block, "records": rows})

    # The 6-9 ns block appears in both registrations; they must agree exactly.
    for replicate in replicates:
        v1_record = _record(reports["blocks_v1"], replicate, "block_6_9_ns", None)
        v2_record = _record(v2, replicate, "block_6_9_ns", policy)
        if abs(v1_record["dg_kcal"] - v2_record["dg_kcal"]) > 1e-12:
            raise ValueError(f"r{replicate} 6-9 ns block differs between v1 and v2 reports")

    contrasts = {}
    for label in temporal["policies"]:
        per_repeat = [
            entry for entry in v2["contrasts"]
            if entry["policy"] == label and entry["label"] == temporal["primary_contrast"]
        ]
        summary = [
            entry for entry in v2["contrast_summaries"]
            if entry["policy"] == label and entry["label"] == temporal["primary_contrast"]
        ]
        if len(per_repeat) != len(replicates) or len(summary) != 1:
            raise ValueError(f"incomplete primary contrast for policy {label}")
        contrasts[label] = {
            "per_repeat": {e["replicate"]: e["signed_movement_kcal"] for e in per_repeat},
            "mean": summary[0]["mean_signed_movement_kcal"],
            "paired_sem": summary[0]["paired_movement_sem_kcal"],
        }

    suffix = {}
    for replicate in replicates:
        diagnostics = _record(v2, replicate, temporal["suffix_block"], policy)["window_diagnostics"]
        ordered = sorted(diagnostics, key=lambda item: item["window"])
        suffix[replicate] = [item["n_after_trim"] for item in ordered]

    ranges = {
        entry["policy"]: entry["replicate_range_kcal"]
        for entry in v2["summaries"] if entry["block"] == "block_12_15_ns"
    }
    return {
        "replicates": replicates,
        "blocks": blocks,
        "contrasts": contrasts,
        "suffix": suffix,
        "range_12_15": ranges,
    }


def check_quoted_values(spec: dict, data: dict) -> dict[str, float]:
    """Verify every outline-quoted number against the plotted data."""
    quoted = spec["temporal"]["quoted"]
    tolerance = spec["temporal"]["quoted_tolerance"]
    by_label = {block["label"]: block["records"] for block in data["blocks"]}
    early = by_label["block_0_3_ns"][1]
    late = by_label["block_6_9_ns"][1]
    adaptive = data["contrasts"]["adaptive"]
    observed = {
        "r1_early_dg": early["dg_kcal"],
        "r1_early_net_hysteresis": early["net_hysteresis_kcal"],
        "r1_early_sum_abs": early["sum_absolute_hysteresis_kcal"],
        "r1_early_max_abs": early["max_absolute_hysteresis_kcal"],
        "r1_6_9_dg": late["dg_kcal"],
        "r1_early_to_6_9_movement": late["dg_kcal"] - early["dg_kcal"],
        "adaptive_primary_mean": adaptive["mean"],
        "adaptive_primary_r1": adaptive["per_repeat"][1],
        "adaptive_primary_r2": adaptive["per_repeat"][2],
        "untrimmed_primary_mean": data["contrasts"]["untrimmed"]["mean"],
        "fixed_25_primary_mean": data["contrasts"]["fixed_25_percent"]["mean"],
        "adaptive_12_15_range": data["range_12_15"]["adaptive"],
    }
    if set(observed) != set(quoted):
        raise ValueError(f"quoted keys {sorted(quoted)} do not match checks {sorted(observed)}")
    for key, value in observed.items():
        if abs(value - quoted[key]) > tolerance:
            raise ValueError(f"{key}: report value {value!r} differs from quoted {quoted[key]!r}")
    return observed


def _style_axes(ax) -> None:
    ax.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(INK_SECONDARY)
    ax.tick_params(colors=INK_SECONDARY, labelcolor=INK, labelsize=8)


def _signed(value: float) -> str:
    """Format a signed value with a typographic minus sign."""
    return f"{value:+.3f}".replace("-", "\u2212")


def _end_labels(ax, x: float, ys: list[float], names: list[str], min_gap: float) -> None:
    """Direct-label line ends, nudging labels apart by at least ``min_gap``."""
    order = sorted(range(len(ys)), key=lambda k: ys[k])
    placed: list[float] = []
    for k in order:
        y = ys[k] if not placed else max(ys[k], placed[-1] + min_gap)
        placed.append(y)
        ax.text(x, y, names[k], color=INK, fontsize=7.5, va="center")


def _panel_label(ax, letter: str) -> None:
    ax.text(-0.14, 1.04, letter, transform=ax.transAxes, fontsize=11,
            fontweight="bold", color=INK, va="bottom")


def draw_temporal_figure(spec: dict, data: dict, lambdas: list[float]):
    """Draw the four-panel F64A temporal figure and return the matplotlib figure."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    temporal = spec["temporal"]
    replicates = data["replicates"]
    plt.rcParams.update({"font.size": 8, "pdf.fonttype": 42, "ps.fonttype": 42})
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.2))
    (ax_dg, ax_h), (ax_move, ax_suffix) = axes
    centres = [(b["start_ns"] + b["stop_ns"]) / 2 for b in data["blocks"]]
    offsets = (-0.25, 0.0, 0.25)
    boundary = temporal["registration_boundary_ns"]

    # (a) disjoint-block estimates.
    for i, replicate in enumerate(replicates):
        xs = [c + offsets[i] for c in centres]
        ys = [b["records"][i]["dg_kcal"] for b in data["blocks"]]
        errs = [b["records"][i]["mbar_error_kcal"] for b in data["blocks"]]
        ax_dg.errorbar(xs, ys, yerr=errs, color=REPEAT_COLORS[i], marker=REPEAT_MARKERS[i],
                       markersize=5, linewidth=1.4, capsize=2, elinewidth=0.9,
                       markeredgecolor="white", markeredgewidth=0.6, label=f"r{replicate}")
    _end_labels(ax_dg, centres[-1] + 0.55,
                [data["blocks"][-1]["records"][i]["dg_kcal"] for i in range(len(replicates))],
                [f"r{r}" for r in replicates], 0.12)
    early = data["blocks"][0]["records"][1]
    ax_dg.annotate(
        f"net H = {early['net_hysteresis_kcal']:.3f}",
        xy=(centres[0] + offsets[1], early["dg_kcal"]), xytext=(2.6, early["dg_kcal"] - 0.06),
        fontsize=7, color=INK, arrowprops={"arrowstyle": "-", "color": INK_SECONDARY, "lw": 0.7},
    )
    ax_dg.set_ylabel("Folded-leg ΔG estimate (kcal/mol)", color=INK)
    ax_dg.set_title("Disjoint 3-ns blocks (adaptive policy)", fontsize=8.5, color=INK)

    # (b) net hysteresis per block.
    for i, replicate in enumerate(replicates):
        xs = [c + offsets[i] for c in centres]
        ys = [b["records"][i]["net_hysteresis_kcal"] for b in data["blocks"]]
        ax_h.plot(xs, ys, color=REPEAT_COLORS[i], marker=REPEAT_MARKERS[i], markersize=5,
                  linewidth=1.4, markeredgecolor="white", markeredgewidth=0.6, label=f"r{replicate}")
    _end_labels(ax_h, centres[-1] + 0.55,
                [data["blocks"][-1]["records"][i]["net_hysteresis_kcal"] for i in range(len(replicates))],
                [f"r{r}" for r in replicates], 0.07)
    ax_h.set_ylim(bottom=0)
    ax_h.set_ylabel("Net hysteresis H = |Σ d_k| (kcal/mol)", color=INK)
    ax_h.set_title("Historical aggregate diagnostic, same blocks", fontsize=8.5, color=INK)

    for ax in (ax_dg, ax_h):
        ax.axvline(boundary, color=INK_SECONDARY, linestyle="--", linewidth=0.8)
        ax.text(boundary - 0.15, 0.98, "v1", transform=ax.get_xaxis_transform(),
                ha="right", va="top", fontsize=7, color=INK_SECONDARY)
        ax.text(boundary + 0.15, 0.98, "v2", transform=ax.get_xaxis_transform(),
                ha="left", va="top", fontsize=7, color=INK_SECONDARY)
        ax.set_xticks([b["start_ns"] for b in data["blocks"]] + [data["blocks"][-1]["stop_ns"]])
        ax.set_xlim(-0.3, data["blocks"][-1]["stop_ns"] + 1.4)
        ax.set_xlabel("Retained production time (ns)", color=INK)

    # (c) primary 9-12 -> 12-15 ns movement under each saved policy.
    policies = list(temporal["policies"])
    for p, label in enumerate(policies):
        contrast = data["contrasts"][label]
        for i, replicate in enumerate(replicates):
            ax_move.plot(p + offsets[i] * 0.8, contrast["per_repeat"][replicate],
                         color=REPEAT_COLORS[i], marker=REPEAT_MARKERS[i], markersize=6,
                         linestyle="none", markeredgecolor="white", markeredgewidth=0.6, zorder=3)
        ax_move.hlines(contrast["mean"], p - 0.32, p + 0.32, color=INK, linewidth=1.6, zorder=2)
    ax_move.axhline(0, color=INK_SECONDARY, linewidth=0.8)
    ax_move.set_xticks(
        range(len(policies)),
        [f"{temporal['policies'][p]}\nmean {_signed(data['contrasts'][p]['mean'])}" for p in policies],
    )
    ax_move.set_xlim(-0.5, len(policies) - 0.5)
    ax_move.set_ylabel("Signed movement, 9–12 → 12–15 ns (kcal/mol)", color=INK)
    ax_move.set_title("Primary v2 contrast (bar = policy mean)", fontsize=8.5, color=INK)

    # (d) adaptive selected raw suffix per window, against actual lambda.
    full = temporal["suffix_block_raw_columns"]
    for i, replicate in enumerate(replicates):
        suffix = data["suffix"][replicate]
        if len(suffix) != len(lambdas):
            raise ValueError("suffix length list does not match lambda schedule")
        ax_suffix.plot(lambdas, suffix, color=REPEAT_COLORS[i], marker=REPEAT_MARKERS[i],
                       markersize=4, linewidth=0.9, markeredgecolor="white",
                       markeredgewidth=0.5, label=f"r{replicate}")
    ax_suffix.axhline(full, color=INK_SECONDARY, linestyle=":", linewidth=0.9)
    ax_suffix.text(0.0, full * 1.02, "full 3-ns block", fontsize=7, color=INK_SECONDARY, va="bottom")
    ax_suffix.set_ylim(0, full * 1.12)
    ax_suffix.set_xlabel("Actual sampled λ", color=INK)
    ax_suffix.set_ylabel("Adaptive retained suffix (raw frames)", color=INK)
    ax_suffix.set_title("Adaptive selected suffixes, 12–15 ns block", fontsize=8.5, color=INK)

    for ax, letter in zip(axes.flat, "abcd"):
        _style_axes(ax)
        _panel_label(ax, letter)
    handles, labels = ax_dg.get_legend_handles_labels()
    fig.legend(handles, [f"repeat {label}" for label in labels], loc="upper center",
               ncol=len(labels), frameon=False, fontsize=8, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.96), h_pad=2.2, w_pad=2.2)
    return fig


def verify_supplement_sources(spec: dict, reports: dict, root: Path = ROOT) -> None:
    """Bind each supplementary image to its pinned bytes before creating outputs."""
    source_dir = _resolve(root, spec["inputs"]["lambda_comparator"]["path"]).parent
    declared = set(reports["lambda_comparator"]["figures"])
    for item in spec["supplement"]:
        if item["source"] not in declared:
            raise ValueError(f"{item['source']} is not a figure declared by the comparator report")
        source = source_dir / item["source"]
        actual = sha256_file(source)
        if actual != item["sha256"]:
            raise ValueError(
                f"{source}: SHA-256 {actual} does not match registered {item['sha256']}"
            )


def build(spec_path: str | Path, root: Path = ROOT, output_dir: str | Path | None = None) -> Path:
    """Build the temporal figure and supplementary copies into a fresh directory."""
    spec = load_spec(spec_path)
    out = Path(output_dir) if output_dir else _resolve(root, spec["output_dir"])
    if out.exists():
        raise FileExistsError(f"{out} already exists; use a new versioned directory")

    reports = load_verified_reports(spec, root)
    lambdas = lambda_vector(spec, root)
    comparator_lambdas = sorted(
        {(r["window"], r["lambda"]) for r in reports["lambda_comparator"]["neighbor_records"]}
    )
    if [value for _, value in comparator_lambdas] != lambdas:
        raise ValueError("comparator lambda labels disagree with config lambda_vector")
    data = temporal_data(spec, reports)
    observed = check_quoted_values(spec, data)

    source_dir = _resolve(root, spec["inputs"]["lambda_comparator"]["path"]).parent
    verify_supplement_sources(spec, reports, root)

    out.mkdir(parents=True, exist_ok=False)
    stem = spec["temporal"]["output_stem"]
    fig = draw_temporal_figure(spec, data, lambdas)
    outputs = {}
    for suffix, kwargs in ((".png", {"dpi": 300}), (".pdf", {})):
        path = out / f"{stem}{suffix}"
        fig.savefig(path, facecolor="white", **kwargs)
        outputs[path.name] = sha256_file(path)
    supplement = {}
    for item in spec["supplement"]:
        source = source_dir / item["source"]
        target = out / item["output"]
        shutil.copyfile(source, target)
        if sha256_file(target) != item["sha256"]:
            raise ValueError(f"copy of {source} does not match registered SHA-256")
        supplement[item["output"]] = {"source": str(source.relative_to(root)),
                                      "sha256": sha256_file(target)}

    trace = {
        "spec_id": spec["spec_id"],
        "spec_sha256": sha256_file(spec_path),
        "builder_sha256": sha256_file(Path(__file__)),
        "inputs": {name: {"path": entry["path"], "sha256": entry.get("sha256")}
                   for name, entry in spec["inputs"].items()},
        "lambda_vector": lambdas,
        "quoted_values_verified": observed,
        "plotted": data,
        "outputs": outputs,
        "supplement": supplement,
        "limitations": [
            "Error bars are conditional MBAR uncertainties; they exclude unvisited conformations.",
            "Disjoint blocks can remain correlated through slow modes.",
            "Policies reuse the same data and are not independent confirmations.",
            "Selected case; not a prospective validation cohort or experimental-accuracy result.",
        ],
    }
    (out / f"{stem}.json").write_text(json.dumps(trace, indent=1, default=str) + "\n")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True)
    parser.add_argument("--output-dir", default=None,
                        help="override the spec output directory (e.g. a scratch preview)")
    args = parser.parse_args()
    print(build(args.spec, output_dir=args.output_dir))


if __name__ == "__main__":
    main()
