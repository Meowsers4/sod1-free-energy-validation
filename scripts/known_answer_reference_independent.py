#!/usr/bin/env python3
"""Independent adaptive-quadrature reference; imports no project analysis code."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import yaml
from scipy.integrate import quad


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def energy(x: float, y: float, lam: float, p: dict, r: dict) -> float:
    center = p["x_lambda_shift"] * (2 * lam - 1) + p["x_y_coupling"] * y
    barrier = r["barrier_height"] * (
        1 - r["barrier_relief"] * 4 * lam * (1 - lam)
    )
    return (
        0.5 * p["x_force_constant"] * (x - center) ** 2
        + barrier * (y * y - 1) ** 2
        + (p["base_y_tilt"] + p["lambda_y_tilt"] * (lam - 0.5)) * y
        + p["lambda_offset"] * lam
    )


def free_energy(spec: dict, regime: dict, lam: float) -> tuple[float, float]:
    x0, x1 = spec["domain"]["x"]
    y0, y1 = spec["domain"]["y"]
    grid_x = np.linspace(x0, x1, 81)
    grid_y = np.linspace(y0, y1, 81)
    shift = min(
        energy(float(x), float(y), lam, spec["potential"], regime)
        for x in grid_x
        for y in grid_y
    )
    opts = spec["reference"]

    def outer(y: float) -> float:
        value, _ = quad(
            lambda x: math.exp(
                -(energy(x, y, lam, spec["potential"], regime) - shift)
            ),
            x0,
            x1,
            epsabs=opts["independent_absolute_tolerance"],
            epsrel=opts["independent_relative_tolerance"],
            limit=200,
        )
        return value

    integral, error = quad(
        outer,
        y0,
        y1,
        epsabs=opts["independent_absolute_tolerance"],
        epsrel=opts["independent_relative_tolerance"],
        limit=200,
    )
    if not integral > 0 or not math.isfinite(integral):
        raise FloatingPointError("adaptive quadrature returned an invalid integral")
    return shift - math.log(integral), error


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("docs/known_answer_model_v2.yaml"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    spec = yaml.safe_load(args.config.read_text())
    output = args.output or Path(spec["output_dir"]) / "independent_reference.json"
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    regimes = {}
    for label, regime in spec["regimes"].items():
        absolute, errors = [], []
        for lam in spec["lambda_vector"]:
            value, error_estimate = free_energy(spec, regime, lam)
            absolute.append(value)
            errors.append(error_estimate)
        relative = [value - absolute[0] for value in absolute]
        regimes[label] = {
            "absolute_free_energies_kT": absolute,
            "relative_free_energies_kT": relative,
            "endpoint_delta_f_kT": relative[-1],
            "reported_quadrature_absolute_errors": errors,
        }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "analysis_id": spec["analysis_id"],
                "implementation": "nested scipy adaptive quadrature; independent script",
                "config_sha256": digest(args.config),
                "script_sha256": digest(Path(__file__)),
                "regimes": regimes,
            },
            indent=2,
            allow_nan=False,
        )
        + "\n"
    )
    temporary.replace(output)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
