# Independent CPU-only DAG: never changes or schedules the registered GPU arm.
configfile: "docs/f64a_raw_energy_audit.yaml"

import yaml
with open(config["report_config"]) as handle:
    evidence = yaml.safe_load(handle)
with open(evidence["pilot_config"]) as handle:
    pilot = yaml.safe_load(handle)

rule f64a_raw_energy_audit:
    input:
        matrices=expand(config["npz_dir"] + "/w{w}_r{r}.npz",
                        w=range(pilot["lambda_windows"]), r=range(pilot["replicates"])),
        report=evidence["input"],
        design=evidence["registered_design"],
        pilot=evidence["pilot_config"],
        evidence_config=config["report_config"],
        config=config["audit_config"],
        code="src/analysis/f64a_raw_energy_audit.py",
        validator="src/analysis/f64a_late_window_audit.py",
    output:
        report=config["output_dir"] + "/raw_energy_audit.json",
        sampled=config["output_dir"] + "/sampled_state_u.png",
        previous=config["output_dir"] + "/previous_minus_sampled_u.png",
        next=config["output_dir"] + "/next_minus_sampled_u.png",
    shell:
        "python -m src.analysis.f64a_raw_energy_audit --config {input.config:q} "
        "--npz-dir {config[npz_dir]:q} --output-dir {config[output_dir]:q}"
