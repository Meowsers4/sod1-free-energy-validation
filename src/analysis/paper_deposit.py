"""Stage a local paper deposit with explicit base commit and working-tree overlays."""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

from src.analysis.paper_package import ROOT, digest, fresh, manifest, verified_spec


def add_bytes(archive: tarfile.TarFile, name: str, content: bytes) -> None:
    """Write a regular archive member with a portable permission mode."""
    member=tarfile.TarInfo(name);member.size=len(content);member.mode=0o644
    archive.addfile(member,io.BytesIO(content))


def build(out: Path) -> None:
    """Validate energies and stage data/code without publishing or assigning rights."""
    spec=verified_spec()
    historical=ROOT/'releases/sod1fep-forensic-review.tar.gz'
    expected='09cc1b2c7575b60afa1af38216b78ca8f126a668b83aa6ef283c06ff8eba7114'
    if digest(historical)!=expected:raise ValueError('Historical release changed')
    comparator=json.loads((ROOT/'results/cpu_audits/f64a_lambda_comparator_v1/lambda_comparator.json').read_text())
    raw=ROOT/'results/pilots/f64a_sampling_extension_v2/production/fep/F64A/folded'
    import numpy as np
    if len(comparator['input_npz_sha256'])!=60:raise ValueError('Expected 60 continuation files')
    for name,sha in comparator['input_npz_sha256'].items():
        if digest(raw/name)!=sha:raise ValueError(f'Continuation hash mismatch: {name}')
        with np.load(raw/name,allow_pickle=False) as data:
            if data['u_kn_window'].shape!=(20,15001):raise ValueError(f'Unexpected shape: {name}')
    fresh(out)
    shutil.copyfile(historical,out/historical.name)
    shutil.copyfile(Path(str(historical)+'.sha256'),out/(historical.name+'.sha256'))
    # Capture committed paths from HEAD, then overlay only this paper's reviewed local work.
    # Concurrent cluster documentation and untracked packages are deliberately not captured.
    paths=['src','tests','config','env','docs','data','workflow','scripts','pilots','README.md','citations.md','.gitignore','Snakefile']
    tracked=subprocess.check_output(['git','ls-files','-z','--',*paths],cwd=ROOT).decode().split('\0')
    tracked=[p for p in tracked if p and not p.startswith('data/structures/')]
    overlays=['README.md','citations.md','src/analysis/manuscript_figures.py',
              'src/analysis/paper_package.py','src/analysis/paper_deposit.py',
              'tests/test_manuscript_figures.py','docs/manuscript_figures_v1.yaml',
              'workflow/manuscript_figures.smk']
    overlays += [str(p.relative_to(ROOT)) for p in (ROOT/'docs/manuscript').glob('*') if p.is_file()]
    overlay=set(overlays)
    provenance={'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                'status':'uncommitted local paper overlays; not a sealed committed-source release',
                'overlay_sha256':{p:digest(ROOT/p) for p in sorted(overlay)},
                'snapshot_sha256':{}}
    with tarfile.open(out/'paper_source_snapshot.tar.gz','w:gz') as tar:
        for path in sorted(set(tracked)|overlay):
            data=(ROOT/path).read_bytes() if path in overlay else subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT)
            import hashlib
            provenance['snapshot_sha256'][path]=hashlib.sha256(data).hexdigest()
            add_bytes(tar,'project/'+path,data)
        add_bytes(tar,'SOURCE_SNAPSHOT.json',(json.dumps(provenance,indent=2)+'\n').encode())
    # The v2 arrays are cumulative and contain the earlier paths; original checkpoint
    # state and the original v1 NPZ byte identities are not claimed to be recoverable.
    roots=['results/pilots/f64a_sampling_extension_v2/production/fep/F64A/folded',
           'results/cpu_audits/f64a_raw_energy_v1','results/cpu_audits/f64a_lambda_comparator_v1',
           'results/cpu_audits/f64a_late_window_v1']
    files=[]
    for name in roots:
        for path in (ROOT/name).rglob('*'):
            if path.is_file() and path.suffix in ('.npz','.json','.csv','.png','.pdf'):
                files.append(path)
    inventory={str(p.relative_to(ROOT)):{'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(files)}
    with tarfile.open(out/'later_f64a_evidence.tar.gz','w:gz') as tar:
        for p in sorted(files):tar.add(p,arcname='project/'+str(p.relative_to(ROOT)),recursive=False)
        add_bytes(tar,'LATER_EVIDENCE_MANIFEST.json',(json.dumps(inventory,indent=2)+'\n').encode())
    (out/'SOURCE_SNAPSHOT.json').write_text(json.dumps(provenance,indent=2)+'\n')
    (out/'LATER_EVIDENCE_MANIFEST.json').write_text(json.dumps(inventory,indent=2)+'\n')
    metadata={'title':'Diagnostic cancellation and benchmark mismatch in SOD1 folding free energy calculations',
              'resource_type':'dataset and software',
              'status':'local deposit candidate; no upload or DOI reservation',
              'description':'Historical energy-analysis release plus cumulative F64A continuation energies, saved reports and paper-source snapshot. A4V attempt-1 folded raw energies are lost; historical run-time estimates survive. Structural trajectories were not retained.',
              'creators':[], 'license':None,'doi':None,
              'pending_fields':['creators','license','funding','related manuscript DOI'],
              'keywords':['SOD1','alchemical free energy','validation','sampling diagnostics','reproducibility']}
    (out/'deposit_metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    shutil.copyfile(ROOT/'docs/manuscript/deposit_instructions.txt',out/'README.txt')
    manifest(out,spec)
    (out/'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in sorted(out.iterdir()) if p.is_file() and p.name!='SHA256SUMS'))
    print(f'Staged {len(inventory)} later evidence files, 60 verified cumulative NPZs, and {len(provenance["snapshot_sha256"])} source files at {out}')


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',required=True,type=Path)
    args=parser.parse_args();build(args.output_dir)


if __name__=='__main__':main()
