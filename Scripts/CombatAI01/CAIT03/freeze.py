"""Freeze current candidate once; preserve every earlier evidence identity."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, stat, subprocess, zipfile
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'Saved/CombatAI01/CAI-T03/Worker/Candidate01'
SCRIPT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(n,v):
    with (OUT/n).open('x',encoding='utf-8') as f:json.dump(v,f,indent=2)
manifest=OUT/'candidate-manifest.json';assert not manifest.exists(),'Immutable candidate already frozen'
build=read(OUT/'build-result03.json');checks=read(OUT/'checks-07.json')
assert build['exit_code']==0 and checks['passed'] and read(OUT/'execution-settings.json')['passed']
assert read(OUT/'pose-wiring.json')['passed']
assert not read(OUT/'editor-ready.json')['pie'] and not read(OUT/'editor-ready.json')['dirty']
dll=ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll';assert sha(dll)==build['dll_sha256']
pid=read(OUT/'editor-process.json')['pid']
mapped=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',f"Get-Process -Id {pid} | Select-Object Id,@{{n='module';e={{($_.Modules | Where-Object ModuleName -eq 'UnrealEditor-MeridianSquad.dll' | Select-Object -First 1).FileName}}}} | ConvertTo-Json"],text=True))
assert Path(mapped['module']).resolve()==dll.resolve(),mapped
mapped.update(sha256=sha(dll),matching_build=True);write('editor-loaded-dll.json',mapped)
for category in ('owner','historical','assets'):
    rows=read(OUT/('assets-before.json' if category=='assets' else f'{category}-preservation-before.json'))
    assert all(sha(ROOT/r['path'])==r['sha256'] for r in rows),category
project_bytes=0;project_files=0;reparse_points=0
for directory,dirs,files in os.walk(ROOT,followlinks=False):
    kept=[]
    for name in dirs:
        p=Path(directory)/name
        if p.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:reparse_points+=1
        else:kept.append(name)
    dirs[:]=kept
    for name in files:
        p=Path(directory)/name
        try:info=p.lstat()
        except FileNotFoundError:continue
        if info.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:reparse_points+=1
        else:project_bytes+=info.st_size;project_files+=1
assert project_bytes+100_000_000<250_000_000_000,project_bytes
write('storage.json',dict(project_file_bytes_before_archives=project_bytes,project_files=project_files,reparse_points_not_double_counted=reparse_points,archive_reserve_bytes=100_000_000,cap_bytes=250_000_000_000))
paths=[p for p in (ROOT/'Source/MeridianSquad').iterdir() if p.is_file()]
paths += [ROOT/r['path'] for r in read(OUT/'assets-before.json')]
paths += [ROOT/'Plugins/GASPEnemyFoundation01/Content/Characters/UEFN_Mannequin/Meshes'/n for n in ('SK_UEFN_Mannequin.uasset','SKM_UEFN_Mannequin.uasset')]
paths += [dll,ROOT/'Binaries/Win64/UnrealEditor.modules',ROOT/'Docs/CombatAI01-MobileLean01.md']
paths += [p for p in SCRIPT.iterdir() if p.suffix in ('.py','.cpp')]
paths += [ROOT/'Scripts/CombatAI01/CAIT02'/n for n in ('check.py','adapters.cpp','boundaries.cpp')]
paths += [p for p in OUT.iterdir() if p.is_file() and p.suffix in ('.json','.log','.cpp','.diff') and p.name!='editor.log']
paths += [OUT/'preserved-inputs.zip',OUT/'checks-07.exe']
paths=sorted(set(paths))
rows=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in paths]
write(manifest.name,dict(task='MSQ-120',candidate='Candidate01/build03',frozen_utc=datetime.now(timezone.utc).isoformat(),baseline=read(OUT/'baseline.json'),
    verification='PASS native Development Editor build, 67 production assertions, 18 native pose cases and actual graph/bone wiring',
    independent_review='PENDING controller dispatch',owner_gameplay='PENDING; no agent gameplay',files=rows))
archive=OUT/'CAIT03-Candidate01-frozen.zip';evidence=OUT/'CAIT03-Candidate01-evidence.zip'
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
    for p in paths+[manifest]:z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(evidence,'x',zipfile.ZIP_DEFLATED) as z:
    for p in paths+[manifest]:
        if p.suffix not in ('.zip','.dll','.exe','.uasset') and not p.is_relative_to(ROOT/'Binaries'):
            z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(archive) as z:
    assert all(hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256'] for r in rows)
assert all(sha(ROOT/r['path'])==r['sha256'] for r in rows)
assert archive.stat().st_size+evidence.stat().st_size<100_000_000
result=dict(entries=len(rows),manifest_sha256=sha(manifest),dll_sha256=sha(dll),archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,
    evidence_sha256=sha(evidence),evidence_bytes=evidence.stat().st_size,all_current_and_archived_bytes_match=True)
write('freeze-result.json',result);print(json.dumps(result,indent=2))
