"""Reuse contact math and freeze task-scoped output identities after review."""
import json,hashlib,math,subprocess,sys
from pathlib import Path
import metahuman_trial01_evidence as helper
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Saved/PlayerCharacter01/MeshUsability01/Worker';BASE=ROOT/'Assets/Source/PlayerCharacter01/MeshUsability01'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def summaries():
    rows=[]
    for p in sorted((OUT/'Compatibility05/Playback').glob('Contact04-*.json')):
        data=read(p);samples=data['samples'];reference=read(ROOT/'Saved/PlayerCharacter01/AnimationAudit01/Worker/Playback'/p.name);offsets=[];phase=[]
        for s in samples:
            nearest=min(reference['samples'],key=lambda r:abs(r['components']['character']['time']-s['components']['character']['time']))
            offsets.append(helper.distance(helper.wrist(s),helper.wrist(nearest)));phase.append(abs(nearest['components']['character']['time']-s['components']['character']['time']))
        rows.append(dict(case=p.stem,samples=len(samples),end_s=samples[-1]['components']['character']['time'],max_time_difference_s=max(abs(s['components']['character']['time']-s['components']['weapon']['time']) for s in samples),right_wrist_source_difference_cm=[min(offsets),max(offsets)],max_reference_phase_error_s=max(phase),images=[Path(f['file']).relative_to(OUT).as_posix() for f in read(p.with_suffix('')/'frames.json')]))
    write(OUT/'reload-summary-Bind05.json',rows)
    geo=[]
    for rev in ['Revision01','Revision02']:
        data=read(OUT/rev/'geometry.json');m=data['meshes'][0]
        geo.append(dict(revision=rev,sha256=data['sha256'],vertices=m['vertices'],polygons=m['faces'],triangles=m['triangles'],quads=m['quads'],ngons=m['ngons'],islands=len(m['components']),boundaries=len(m['boundary_edges']),multiface=len(m['edges_over_two_faces']),winding=len(m['inconsistent_winding_edges']),opposed_normal_faces=len(m['opposed_corner_faces']),uv_layers=len(m['uv_layers']),regional=data['regional_flags']))
    write(OUT/'source-comparison.json',geo)
    surface=read(OUT/'surface-verification-Bind05.json');digits=[r for r in surface['probes'] if r['name'][:2] in ('l_','r_')]
    for row in digits:
        displacement=row['source_defined_digit_displacement_cm'];row['max_other_digit_cm']=max(v for k,v in displacement.items() if k!=row['name'])
    write(OUT/'digit-summary-Bind05.json',digits)
    print(json.dumps(dict(reloads=rows,sources=geo,maximum_cross_digit_cm=max(r['max_other_digit_cm'] for r in digits))))

def index():
    groups={name:[p.relative_to(OUT).as_posix() for p in sorted((OUT/name).glob('*.png'))] for name in ['Revision01','Revision02','Detail05','DeformationBind05Final','Bind01','Bind02','Bind03','Bind04','Bind05']}
    groups['Unreal']=[p.relative_to(OUT).as_posix() for p in sorted((OUT/'Compatibility05').rglob('*.png'))]
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Datum16 Mesh Usability 01</title><style>body{font:16px system-ui;background:#222;color:#eee;margin:24px;max-width:1500px}select{font:inherit;margin:8px}img{max-width:100%;max-height:850px}a{color:#9cd0ff}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}p{line-height:1.5;max-width:1100px}</style>
<h1>Datum16 Mesh Usability 01 — Bind05 diagnostic</h1><p>Existing topology is retained exactly. The full 161-bone round trip and four native TP reloads executed. No whole-body retopology is justified by this assessment. Gloves/cuffs, collar and boots have localized structural defects; fit, weights, crouch and surface contact still require work. This is not a production or visual acceptance.</p>
<h2>Exact source comparison</h2><select id="sourceView"></select><div class="pair"><figure><img id="rev1"><figcaption>Revision01 — preserved previous source</figcaption></figure><figure><img id="rev2"><figcaption>Revision02 — tested owner source</figcaption></figure></div>
<h2>Actual surface evidence</h2><p>Detail05 shows evaluated vertices with original polygon wire. Temporary display copies use recalculated smooth normals; hand crops hide other body surfaces beyond 25 cm of the wrist. DeformationBind05Final preserves source custom-normal behavior. Bind01–03 are retained diagnostic failures. Unreal views retain the candidate and attach the rifle to its own ik_hand_gun; no hidden donor.</p><select id="group"></select><select id="file"></select><p id="label"></p><img id="display">
<h2>Limits</h2><p>Digit isolation is measured on source-defined distal regions, not inferred from weights. Closeups show remaining seams, compression and imperfect contact. The 170 cm camera image uses a TP control pose, not authored FP animation. Sparse playback captures do not establish continuous surface contact, gameplay, final stature or appearance acceptance.</p>
<p><a href="surface-verification-Bind05.json">Topology and round trip</a> · <a href="digit-summary-Bind05.json">Ten digits</a> · <a href="reload-summary-Bind05.json">Reload measurements</a> · <a href="source-comparison.json">Sources</a> · <a href="preservation-after.json">Preservation</a></p>
<script>const groups=GROUPS;const add=(el,v)=>el.add(new Option(v,v));groups.Revision02.forEach(p=>add(sourceView,p.split('/').pop()));function compare(){rev1.src='Revision01/'+sourceView.value;rev2.src='Revision02/'+sourceView.value}sourceView.onchange=compare;compare();Object.keys(groups).forEach(k=>add(group,k));group.value='Detail05';function show(){display.src=file.value;label.textContent=file.value}function choose(){file.innerHTML='';groups[group.value].forEach(p=>add(file,p));show()}group.onchange=choose;file.onchange=show;choose();</script></html>'''
    (OUT/'index.html').write_text(page.replace('GROUPS',json.dumps(groups)),encoding='utf-8')

def manifest():
    assert not (BASE/'manifest.json').exists(),'Frozen manifests must not be replaced'
    files=[p for root in [BASE,ROOT/'Content/Development/PlayerCharacter01/MeshUsability01'] for p in root.rglob('*') if p.is_file()]
    files+=list((ROOT/'Scripts/PlayerCharacter01').glob('mesh_usability01_*'))+[ROOT/'Docs/PlayerCharacter01MeshUsability01.md']
    rows=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=helper.sha(p)) for p in sorted(files)]
    binaries=[r['path'] for r in rows if Path(r['path']).suffix in ('.blend','.fbx','.uasset')]
    policies=subprocess.check_output(['git','check-attr','filter','text','--',*[r['path'] for r in rows]],cwd=ROOT,text=True)
    (OUT/'git-attributes-audit.txt').write_text(policies,encoding='utf-8')
    missing_text=[line for line in policies.splitlines() if ': text:' in line and not line.endswith(': unset')]
    assert not missing_text,missing_text
    assert all((p+': filter: lfs') in policies for p in binaries),'Binary LFS policy missing'
    write(BASE/'manifest.json',dict(manifest_id='MSQ54-Datum16MeshUsability01-Worker01-Bind05',status='Diagnostic assessment only; full MSQ-54 incomplete',files=rows,controller_git_attribute_actions=missing_text))
    evidence=[dict(path=p.relative_to(OUT).as_posix(),bytes=p.stat().st_size,sha256=helper.sha(p)) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='evidence-manifest.json']
    write(OUT/'evidence-manifest.json',dict(files=evidence))
    print(json.dumps(dict(artifacts=len(rows),evidence=len(evidence),binary_files=len(binaries),attributes_pending=len(missing_text))))

def provenance():
    dest=BASE/'Settings';dest.mkdir(exist_ok=True)
    for name in ('Bind01','Bind02','Bind03','Bind04','Bind05'):
        (dest/(name+'.json')).write_bytes((OUT/name/'bind.json').read_bytes())
    files=['import-Datum16_Bind05.json','rig-comparison-Datum16_Bind05.json','surface-verification-Bind05.json','digit-summary-Bind05.json','reload-summary-Bind05.json']
    for name in files:(dest/name).write_bytes((OUT/name).read_bytes())
    helpers=[ROOT/'Scripts/PlayerCharacter01'/n for n in ['body_intake01.py','shoulder_intake01.py','animation_audit01_unreal.py','animation_audit01_client.py','metahuman_trial01_deform.py','metahuman_trial01_host.py','metahuman_trial01_evidence.py']]
    helpers.append(ROOT/'Scripts/OpeningLobby/functionalbuild01_client.py')
    write(BASE/'provenance.json',dict(source_revision='Datum16UndersuitInput01/OwnerExports/Revision02',source_sha256='aade1a13585f8639610e42a12cc350619ff4279e33325968f416bb4e8b8e8467',
        rig_contract_sha256=helper.sha(ROOT/'Assets/Source/PlayerCharacter01/AnimationAudit01/rig-contract.json'),donor_copy=read(OUT/'donor-copy.json'),
        reused_helpers=[dict(path=p.relative_to(ROOT).as_posix(),sha256=helper.sha(p)) for p in helpers],
        software=dict(blender='5.2.1 LTS / 9e2066aef7ef',unreal='5.8.1 / CL56057345',transport='official Epic MCP http://127.0.0.1:8000/mcp'),
        scope='Diagnostic existing-topology assessment; no visual acceptance, no blanket retopology, no successor'))
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='manifest':manifest()
    elif len(sys.argv)>1 and sys.argv[1]=='provenance':provenance()
    else:summaries();index()
