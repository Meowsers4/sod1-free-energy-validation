# Work-package B CPU-only calibration. No rule can schedule a GPU producer.
configfile: "docs/known_answer_model_v2.yaml"

rule known_answer_reference:
    input:
        config="docs/known_answer_model_v2.yaml",
        code="src/analysis/known_answer_model.py",
    output:
        config["output_dir"] + "/reference.json",
    resources:
        gpu=0,
    shell:
        "python -m src.analysis.known_answer_model --config {input.config:q} reference"

rule known_answer_reference_independent:
    input:
        config="docs/known_answer_model_v2.yaml",
        code="scripts/known_answer_reference_independent.py",
    output:
        config["output_dir"] + "/independent_reference.json",
    resources:
        gpu=0,
    shell:
        "python {input.code:q} --config {input.config:q} --output {output:q}"

rule known_answer_calibration:
    input:
        reference=rules.known_answer_reference.output,
        independent=rules.known_answer_reference_independent.output,
        config="docs/known_answer_model_v2.yaml",
        code="src/analysis/known_answer_model.py",
    output:
        report=config["output_dir"] + "/calibration.json",
        reference_figure=config["output_dir"] + "/reference_profiles.png",
        errors=config["output_dir"] + "/heldout_errors.png",
        diagnostics=config["output_dir"] + "/diagnostics_vs_error.png",
    resources:
        gpu=0,
    shell:
        "MPLCONFIGDIR=/tmp/sod1fep-mpl python -m src.analysis.known_answer_model "
        "--config {input.config:q} evaluate"
