"""Candidate evidence inspection, protected hashes, measured section and freeze."""
import hashlib
import json
import math
import struct
import sys
from pathlib import Path
from functionalbuild01_data import ROOT,OUT,SRC,D
from functionalbuild01_preflight import walk,digest

def section():
    probes=json.loads((OUT/'imported-profile-probes.json').read_text())
    assert probes['passed']
    byname={p['name']:p for p in probes['probes']}
    low=byname['inner_band_roof_1']['impact_cm'][2]/100
    high=byname['inner_aisle_roof_1']['impact_cm'][2]/100
    beam=byname['roof_step_beam_contact_1']['impact_cm'][1]/100
    # Technical section is code-native SVG from actual reopened scene measurements,
    # distinct from in-engine context imagery. No inferred interior destination.
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000">
<rect width="1600" height="1000" fill="#f5f3ec"/>
<g font-family="Arial" fill="#253b3b"><text x="65" y="70" font-size="33">FunctionalBuild01 / measured roof and door sections</text>
<text x="65" y="110" font-size="21">TECHNICAL EVIDENCE / reopened Unreal complex traces and saved module bounds / metres</text>
<text x="65" y="160" font-size="23">Positive inner room, transverse cut X 25.0</text>
<path d="M130 790 H820" stroke="#253b3b" stroke-width="4"/>
<path d="M130 790 V368 H150 V790" fill="#c5b496" stroke="#253b3b" stroke-width="2"/>
<rect x="130" y="350" width="120" height="18" fill="#c5b496" stroke="#253b3b" stroke-width="2"/>
<rect x="130" y="210" width="120" height="140" fill="#788c87" stroke="#253b3b" stroke-width="2"/>
<rect x="250" y="310" width="200" height="18" fill="#c5b496" stroke="#253b3b" stroke-width="2"/>
<rect x="432" y="328" width="18" height="462" fill="#c5b496" stroke="#253b3b" stroke-width="2"/>
<g stroke="#007b7d" stroke-width="2" fill="none"><path d="M150 368 L520 400"/><path d="M350 328 L520 340"/><path d="M250 290 L520 270"/><path d="M130 350 L520 460"/></g>
<g font-size="21"><text x="535" y="407">Band underside Z {low:.2f}</text><text x="535" y="347">Aisle underside Z {high:.2f}</text>
<text x="535" y="277">Beam side |Y| {beam:.2f}</text><text x="535" y="467">Band top Z 8.40 / beam bottom</text>
<text x="80" y="835">|Y|5.6</text><text x="225" y="835">8.0</text><text x="420" y="835">12.0</text>
<text x="85" y="890">Roof thickness 0.36; upper tier top 9.20; main beam top 11.20.</text>
<text x="85" y="925">No internal Y8 partition. Retained entrance coffer edges stay enclosed at the other end.</text></g>
<g transform="translate(930 190)"><text x="0" y="0" font-size="23">Service door / longitudinal section</text>
<path d="M0 600 H550" stroke="#253b3b" stroke-width="3"/>
<path d="M180 600 V180 H216 V600" fill="#c5b496" stroke="#253b3b" stroke-width="2"/>
<rect x="180" y="360" width="12" height="240" fill="#253b3b"/>
<rect x="204" y="360" width="6" height="240" fill="#53635f"/>
<rect x="180" y="348" width="36" height="12" fill="#253b3b"/>
<g font-size="20"><text x="255" y="390">Opening 1.20 x 2.40</text><text x="255" y="430">Recess 0.24 / leaf 0.06</text><text x="255" y="470">Wall 0.36 / frame 0.12</text>
<text x="15" y="650">Face X -19.80; closed leaf X -20.04</text><text x="15" y="690">Threshold Z0; approach from +X</text></g></g>
<text x="65" y="970" font-size="17">Section diagram, not a playable interior or visual acceptance claim. Evidence: imported-profile-probes.json, construction.json.</text></g></svg>'''
    (OUT/'measured-section.svg').write_text(svg)
    print(json.dumps({'section':'measured-section.svg','actual_roof_undersides':[low,high],'beam_side':beam}))

def validate():
    failures=[];summary={}
    for name in ['construction.json','asset-audit.json','imported-profile-probes.json','scheduled-measurements.json','saved-source-audit.json','runtime-verification.json','ElevatorRecheck/runtime-verification.json','capture-settings-restored.json']:
        r=json.loads((OUT/name).read_text());passed=r.get('passed',r.get('matched',False))
        summary[name]=passed
        if not passed:failures.append(name)
    before=json.loads((OUT/'protected-before.json').read_text());changed=[]
    for item in before['entries']:
        p=ROOT/item['path']
        if not p.is_file() or digest(p)!=item['sha256']:changed.append(item['path'])
    if changed:failures.append('protected bytes changed')
    images=[]
    for p in OUT.glob('*-90.png'):
        raw=p.read_bytes();size=list(struct.unpack('>II',raw[16:24]));camera=json.loads(p.with_name(p.stem+'-camera.json').read_text())
        pose_error=max(abs(a-b) for a,b in zip(camera['requested_xyz_cm'],camera['actual_xyz_cm']))
        rotation_error=max(abs((a-b+180)%360-180) for a,b in zip(camera['actual_rotation'][:2],[camera['pitch'],camera['yaw']]))
        passed=size==[1920,1080] and pose_error<1 and rotation_error<.01 and camera['actual_hfov']==90
        images.append({'path':p.relative_to(ROOT).as_posix(),'resolution':size,'pose_error_cm':pose_error,'rotation_error_degrees':rotation_error,'passed':passed,'sha256':digest(p)})
        if not passed:failures.append(p.name)
    if len(images)!=13:failures.append('Expected 13 native images')
    final=json.loads((OUT/'final-state.json').read_text())
    if final['pie'] or final['dirty_content'] or final['dirty_maps'] or not final['capture_overrides_restored'] or not final['throttle_restored']:failures.append('final editor state')
    total=sum(p.stat().st_size for p in walk(ROOT));growth=total-before['project_bytes']
    report={'passed':not failures,'failures':failures,'checks':summary,'protected_files':len(before['entries']),'protected_changes':changed,'images':images,'project_bytes':total,'project_growth_bytes':growth}
    (OUT/'evidence-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='images'}))
    return report

def annotate_identity():
    map_path=ROOT/'Content/Maps/L_OpeningLobby_FunctionalBuild01.umap';sha=digest(map_path)
    for p in OUT.glob('*-90-camera.json'):
        record=json.loads(p.read_text());record['candidate_map_sha256_after_final_reopen']=sha
        record['identity_note']='Final saved scene audit passed after capture; asset bytes frozen alongside image in manifest.'
        p.write_text(json.dumps(record,indent=2))
    print(json.dumps({'map_sha256':sha}))

def verify():
    p=OUT/'manifest.json';manifest=json.loads(p.read_text());expected=(OUT/'manifest.sha256').read_text().split()[0]
    failures=[]
    if digest(p)!=expected:failures.append('manifest digest')
    for item in manifest['entries']:
        f=ROOT/item['path']
        if not f.is_file() or f.stat().st_size!=item['bytes'] or digest(f)!=item['sha256']:failures.append(item['path'])
    print(json.dumps({'verified':not failures,'manifest_sha256':expected,'entries':len(manifest['entries']),'failures':failures}))
    assert not failures

def freeze():
    assert validate()['passed']
    paths=list(walk(SRC))+list(walk(ROOT/'Content/OpeningLobby/FunctionalBuild01'))
    paths+=list((ROOT/'Scripts/OpeningLobby').glob('functionalbuild01_*.py'))
    paths+=[ROOT/'Content/Maps/L_OpeningLobby_FunctionalBuild01.umap',ROOT/'Docs/OpeningLobbyFunctionalBuild01.md']
    paths+=list(walk(OUT))
    entries=[]
    for p in sorted(set(paths)):
        if p.name in ['manifest.json','manifest.sha256'] or 'BrowserProfile' in p.parts:continue
        entries.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)})
    report={'candidate':'LobbyFunctional-Build01/WorkerCandidate01','status':'pending_independent_review_and_owner_walkthrough','drawing_manifest_sha256':'440064e9a1df1180cec92cc3e43be78034b7de30a6e94ef94d0a9d0534b0ecd1','entries':entries}
    p=OUT/'manifest.json';p.write_text(json.dumps(report,indent=2)+'\n');sha=digest(p);(OUT/'manifest.sha256').write_text(sha+'  manifest.json\n')
    print(json.dumps({'manifest_sha256':sha,'entries':len(entries),'bytes':sum(x['bytes'] for x in entries)}))

if __name__=='__main__':globals()[sys.argv[1]]()
