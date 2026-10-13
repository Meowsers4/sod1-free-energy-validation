# Manuscript figure assembly v1. CPU-only; reads hashed reports, recomputes nothing.
# Explicit target only (`snakemake manuscript_figures_v1`); `all` is unchanged.
# The spec is loaded into its own variable rather than via `configfile:`, which
# would merge keys such as `output_dir` into the global config used by other rules.
import yaml as _manuscript_yaml

with open("docs/manuscript_figures_v1.yaml") as _handle:
    manuscript_spec = _manuscript_yaml.safe_load(_handle)

rule manuscript_figures_v1:
    input:
        spec="docs/manuscript_figures_v1.yaml",
        code="src/analysis/manuscript_figures.py",
        reports=[entry["path"] for entry in manuscript_spec["inputs"].values()],
        supplement=[
            str(Path(manuscript_spec["inputs"]["lambda_comparator"]["path"]).parent / item["source"])
            for item in manuscript_spec["supplement"]
        ],
    output:
        directory(manuscript_spec["output_dir"]),
    resources:
        gpu=0,
    shell:
        "python -m src.analysis.manuscript_figures --spec {input.spec:q}"
