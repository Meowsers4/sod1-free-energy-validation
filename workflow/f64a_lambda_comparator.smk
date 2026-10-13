# Fresh-output CPU-only work-package A1 analysis. It has no GPU producer.
configfile: "docs/f64a_lambda_comparator.yaml"

import yaml
with open(config["pilot_config"]) as handle:
    lambda_pilot = yaml.safe_load(handle)

rule f64a_lambda_comparator:
    input:
        matrices=expand(
            config["npz_dir"] + "/w{w}_r{r}.npz",
            w=range(lambda_pilot["lambda_windows"]),
            r=range(lambda_pilot["replicates"]),
        ),
        raw=config["raw_audit"],
        continuation=config["continuation_report"],
        pilot=config["pilot_config"],
        design=config["analysis_design"],
        config="docs/f64a_lambda_comparator.yaml",
        code="src/analysis/f64a_lambda_comparator.py",
        raw_code="src/analysis/f64a_raw_energy_audit.py",
        validator="src/analysis/f64a_late_window_audit.py",
    output:
        report=config["output_dir"] + "/lambda_comparator.json",
        neighbor=config["output_dir"] + "/neighbor_full_block_metrics.png",
        context=config["output_dir"] + "/selection_context.png",
        fixed=config["output_dir"] + "/fixed_pair_metrics.png",
    resources:
        gpu=0,
    shell:
        "python -m src.analysis.f64a_lambda_comparator --config {input.config:q} "
        "--npz-dir {config[npz_dir]:q} --output-dir {config[output_dir]:q}"
