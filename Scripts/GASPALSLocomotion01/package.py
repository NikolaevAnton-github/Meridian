"""Prepare provenance/registry input, then freeze a reviewable task-only candidate.

Never stages, commits, registers, changes admin documents or writes the source.
"""
from pathlib import Path
from datetime import datetime,timezone
import difflib,json,shutil,subprocess,sys,zipfile
from prepare import ROOT,OUT,SOURCE,files,sha

ORIGINALS=ROOT/'Assets/Source/GASPALSLocomotion01'
CANDIDATE=OUT/'Candidate01'
REVISION=ORIGINALS/'revision-Candidate01.json'
REGISTRY=ROOT/'Scripts/AssetRegistry/manifests/GASPALSLocomotion01-Candidate01.json'
ADAPTED='Plugins/GASPALS/Content/Blueprints/ABP_SandboxCharacter.uasset'
CHILD='Content/Development/GASPALSLocomotion01/Candidate01/BP_GASPALSEnemy_Candidate01.uasset'

def row(path):
    p=ROOT/path
    return dict(path=path,size_bytes=p.stat().st_size,sha256=sha(p))

def prepare():
    assert not REVISION.exists() and not REGISTRY.exists()
    original=json.loads((OUT/'Before/identity.json').read_text())
    changed=[]
    for entry in original['files']:
        if sha(ROOT/entry['path'])!=entry['sha256']:changed.append(entry['path'])
    assert all(p.startswith('Source/MeridianSquad/') or p=='MeridianSquad.uproject' for p in changed),changed
    before=(OUT/'Before/MeridianSquad.uproject').read_bytes()
    project=(ROOT/'MeridianSquad.uproject').read_bytes()
    newline=b'\r\n' if b'\r\n' in before else b'\n'
    addition=newline.join([b'\t\t{',b'\t\t\t"Name": "GASPALS",',b'\t\t\t"Enabled": true',b'\t\t},'])+newline
    assert project.count(addition)==1 and project.replace(addition,b'',1)==before
    (OUT/'owner-project-addition.diff').write_text(''.join(difflib.unified_diff(
        before.decode().splitlines(True),project.decode().splitlines(True),fromfile='owner-before',tofile='MSQ-121-after')))
    intake=json.loads((ORIGINALS/'intake-manifest.json').read_text())
    revision=[]
    for entry in intake['files']:
        assert sha(SOURCE/entry['source_relative'])==entry['sha256'],entry['source_relative']
        final=row(entry['destination'])
        if final['sha256']!=entry['sha256']:assert final['path']==ADAPTED,final['path']
        final.update(source_relative=entry['source_relative'],source_sha256=entry['sha256'],
            relationship='authored adaptation' if final['path']==ADAPTED else 'exact byte copy')
        revision.append(final)
    revision.append(dict(**row(CHILD),relationship='new child of canonical source CBP_SandboxCharacter'))
    backup='Assets/Source/GASPALSLocomotion01/Before/ABP_SandboxCharacter.uasset'
    assert sha(ROOT/backup)==next(x['source_sha256'] for x in revision if x['path']==ADAPTED)
    revision.append(dict(**row(backup),relationship='exact original before local adaptation'))
    data=dict(task='MSQ-121',candidate='Candidate01',source_project=str(SOURCE),source_head=intake['source_head'],
        runtime_source_dependency=False,files=revision,
        adaptations=['Canonical source AnimBP derives from native lean-only AnimInstance; original 1084 graph nodes retained.',
            'Additive spine_01 tactical lean after original source pose; four scoped cvar inputs retain source defaults.',
            'New child selects Masculine/Rifle and disables auto possession.',
            'Demo engine/map/render config is archival only. Owner config is exact; project plugin enablement is additive.'])
    REVISION.write_text(json.dumps(data,indent=2))
    artifacts=[]
    for entry in revision+[row(REVISION.relative_to(ROOT).as_posix()),row((ORIGINALS/'intake-manifest.json').relative_to(ROOT).as_posix())]:
        artifacts.append({k:entry[k] for k in ('path','size_bytes','sha256')}|dict(role='gaspals_locomotion_candidate01',
            evidence=[dict(source='Docs/GASPALSLocomotion01.md',note='Executor Candidate01. Source provenance in revision-Candidate01.json. Independent/controller and owner motion acceptance remain separate.')]))
    REGISTRY.write_text(json.dumps(dict(asset='GASPALSLocomotion01-Candidate01',artifacts=artifacts,dependencies=[]),indent=2))
    finish()

def finish():
    # The revision/registry files are written only after all source and initial
    # preservation hashes pass. Reuse that work if a later metadata check fails.
    assert REVISION.exists() and REGISTRY.exists()
    original=json.loads((OUT/'Before/identity.json').read_text())
    intake=json.loads((ORIGINALS/'intake-manifest.json').read_text())
    artifacts=json.loads(REGISTRY.read_text())['artifacts']
    attributes=ROOT/'.gitattributes'
    original_attributes=(OUT/'Before/.gitattributes').read_bytes()
    exact_paths=['MeridianSquad.uproject','Source/MeridianSquad/GASPALSLocomotion*',
        'Source/MeridianSquad/CombatAIMobile.h','Source/MeridianSquad/EnemyCombatComponent.cpp',
        'Source/MeridianSquad/EnemyCombatLean.cpp','Source/MeridianSquad/EnemyCombatMobile.cpp',
        'Source/MeridianSquad/EnemyCombatObservation.cpp','Scripts/GASPALSLocomotion01/**',
        'Assets/Source/GASPALSLocomotion01/**','Docs/GASPALSLocomotion01.md',
        'Scripts/AssetRegistry/manifests/GASPALSLocomotion01-Candidate01.json','Plugins/GASPALS/**']
    addition=('\n# Preserve exact MSQ-121 candidate, source intake and registry identities.\n'+
        '\n'.join(p+' -text' for p in exact_paths)+'\n').encode()
    if attributes.read_bytes()==original_attributes: attributes.write_bytes(original_attributes+addition)
    assert attributes.read_bytes()==original_attributes+addition
    changed=[e['path'] for e in original['files'] if
        (e['path'].startswith('Source/') or e['path'] in ['MeridianSquad.uproject','.gitattributes']) and sha(ROOT/e['path'])!=e['sha256']]
    binary_paths=[x['path'] for x in artifacts if Path(x['path']).suffix in ('.uasset','.umap','.png')]
    # Binary stdin prevents Windows newline translation from adding a CR to a
    # filename read by Git's --stdin interface.
    attrs=subprocess.run(['git','check-attr','--stdin','filter'],input=('\n'.join(binary_paths)+'\n').encode(),cwd=ROOT,capture_output=True,check=True)
    output=attrs.stdout.decode()
    assert len(output.splitlines())==len(binary_paths)
    assert all(line.endswith(': filter: lfs') for line in output.splitlines())
    (OUT/'lfs-attributes.txt').write_text(output)
    result=dict(preserved_inputs=len(original['files']),changed_inputs=changed,
        preserved_existing_assets=len([e for e in original['files'] if Path(e['path']).suffix in ('.uasset','.umap')]),
        source_files_unchanged=len(intake['files']),source_copies_adapted=[ADAPTED],
        owner_config_unchanged=True,owner_project_addition_only=True,retained_map_unchanged=True,
        attributes_addition_only=True,
        lfs_binary_paths=len(binary_paths),registry_artifacts=len(artifacts),registry_mutated=False,
        production_staged_or_committed=False)
    (OUT/'preservation-check.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result))

def freeze():
    assert not CANDIDATE.exists(),'Candidate is immutable. Use a new revision for corrections.'
    assert json.loads((OUT/'build-04.json').read_text())['exit_code']==0
    CANDIDATE.mkdir()
    changed=subprocess.check_output(['git','diff','--name-only','--','Source/MeridianSquad'],cwd=ROOT,text=True).splitlines()
    paths=set(changed+['.gitattributes','MeridianSquad.uproject','Docs/GASPALSLocomotion01.md',REGISTRY.relative_to(ROOT).as_posix()])
    for folder in ['Plugins/GASPALS','Assets/Source/GASPALSLocomotion01','Content/Development/GASPALSLocomotion01','Scripts/GASPALSLocomotion01']:
        paths.update(p.relative_to(ROOT).as_posix() for p in files(ROOT/folder) if '__pycache__' not in p.parts)
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'Source/MeridianSquad').glob('GASPALSLocomotion*'))
    inventory=[]
    archive=CANDIDATE/'production.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
        for p in sorted(paths):
            inventory.append(row(p));z.write(ROOT/p,p)
        dll='Binaries/Win64/UnrealEditor-MeridianSquad.dll'
        z.write(ROOT/dll,dll)
    (CANDIDATE/'changed-files.txt').write_text('\n'.join(sorted(paths))+'\n')
    # Copy bounded evidence. Preserve initial archives in place by immutable hash.
    evidence=CANDIDATE/'Evidence';evidence.mkdir()
    selected=[p for p in OUT.iterdir() if p.is_file() and p.suffix in ('.json','.log','.diff','.txt')]
    selected+=[p for name in ('SourceGraph','Reflection') for p in files(OUT/name)]
    evidence_rows=[]
    for p in selected:
        rel=p.relative_to(OUT);dst=evidence/rel;dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,dst);evidence_rows.append(dict(path='Evidence/'+rel.as_posix(),size_bytes=dst.stat().st_size,sha256=sha(dst)))
    project_bytes=sum(p.stat().st_size for p in files(ROOT))
    assert project_bytes<250_000_000_000,project_bytes
    manifest=dict(task='MSQ-121',candidate='Candidate01',frozen_utc=datetime.now(timezone.utc).isoformat(),
        baseline_head=json.loads((OUT/'Before/identity.json').read_text())['head'],
        implementation_status='complete executor delivery; independent/controller review and owner Play remain separate',
        no_agent_play=True,production=inventory,dll=row(dll),evidence=evidence_rows,
        preserved_before=[row((OUT/'Before'/name).relative_to(ROOT).as_posix()) for name in
            ['identity.json','active-inputs.zip','execution-settings.json']],
        archive=dict(path='production.zip',size_bytes=archive.stat().st_size,sha256=sha(archive)),
        project_bytes_including_candidate=project_bytes,project_ceiling_bytes=250_000_000_000,
        disk_free_bytes=shutil.disk_usage(ROOT).free)
    with (CANDIDATE/'candidate-manifest.json').open('x') as f:json.dump(manifest,f,indent=2)
    print(json.dumps(dict(candidate=str(CANDIDATE),production_files=len(inventory),evidence_files=len(evidence_rows),
        project_bytes=project_bytes,archive_bytes=archive.stat().st_size)))

if __name__=='__main__':
    {'prepare':prepare,'finish':finish,'freeze':freeze}[sys.argv[1]]()
