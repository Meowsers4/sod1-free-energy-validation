# Separate CPU DAG leaves the registered v2 workflow and identity untouched.
configfile: "docs/f64a_late_window_audit.yaml"

rule f64a_late_window_audit:
    input:
        report=config["input"],
        design=config["registered_design"],
        pilot=config["pilot_config"],
        audit_config="docs/f64a_late_window_audit.yaml",
        code="src/analysis/f64a_late_window_audit.py",
    output:
        config["output"],
    shell:
        "python -m src.analysis.f64a_late_window_audit --config {input.audit_config:q}"
