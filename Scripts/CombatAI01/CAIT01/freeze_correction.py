"""Freeze Candidate02 once; exclude mutable controller monitors and live logs."""
from pathlib import Path
from datetime import datetime, timezone
import difflib
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'Saved/CombatAI01/CAI-T01/Worker/Candidate02'
PREVIOUS=OUT.parent/'Candidate01'
CONTROLLER=OUT.parents[1]/'Controller'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((OUT/name).read_text(encoding='utf-8-sig'))


def write(name, value):
    with (OUT/name).open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2)


manifest_path=OUT/'candidate-manifest.json'
frozen_path=OUT/'CAIT01-Candidate02-frozen.zip'
evidence_path=OUT/'CAIT01-Candidate02-evidence.zip'
assert not any(p.exists() for p in (manifest_path,frozen_path,evidence_path)), 'Frozen candidates must never be overwritten'
assert read('correction-check-check01.json')['passed']
assert read('execution-settings.json')['passed']
build=(OUT/'build01.log').read_bytes()
assert 'Result: Succeeded' in build.decode('utf-16' if build.startswith(b'\xff\xfe') else 'utf-8-sig')
dll=ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll'
loaded=read('editor-load-check.json')
assert loaded['matches_launch'] and loaded['sha256'].lower()==digest(dll)
for name in ('editor-state.json','editor-close.json'):
    state=read(name)
    assert not state['pie'] and not state['dirty']
    assert state['map']=='/Game/Maps/L_OpeningLobby_PainterStone01.L_OpeningLobby_PainterStone01'
assert read('editor-exit-check.json')['stopped']
historical=read('historical-preservation-before.json')
owner=read('owner-preservation-baseline.json')
checks=dict(historical_files=len(historical),
    historical_unchanged=all(digest(ROOT/r['path'])==r['sha256'] for r in historical),
    owner_config_project_map_unchanged=all(digest(ROOT/r['path'])==r['sha256'] for r in owner if r['path']!='AGENTS.md'),
    durable_AGENTS_unchanged=(ROOT/'AGENTS.md').read_bytes().split(b'<!-- BEGIN MULTICA-RUNTIME',1)[0].rstrip()==(CONTROLLER/'AGENTS.md').read_bytes().rstrip())
assert all(v for k,v in checks.items() if k!='historical_files'),checks
write('preservation-final.json',checks)

diff=[]
with zipfile.ZipFile(PREVIOUS/'CAIT01-Candidate01-frozen.zip') as archive:
    for name in ('EnemyCombatNavigation.cpp','EnemyCombatTactics.cpp'):
        rel='Source/MeridianSquad/'+name
        old=archive.read(rel).decode('utf-8-sig').splitlines(keepends=True)
        new=(ROOT/rel).read_text(encoding='utf-8-sig').splitlines(keepends=True)
        diff.extend(difflib.unified_diff([s.replace('\r\n','\n') for s in old],new,fromfile='Candidate01/'+rel,tofile='Candidate02/'+rel))
with (OUT/'correction-source-diff.patch').open('x',encoding='utf-8') as stream:
    stream.write(''.join(diff))

paths=sorted((ROOT/'Source/MeridianSquad').glob('*.h'))+sorted((ROOT/'Source/MeridianSquad').glob('*.cpp'))
paths += [ROOT/'Source/MeridianSquad/MeridianSquad.Build.cs',ROOT/'Docs/CombatAI01-Tactical01Correction01.md',dll,ROOT/'Binaries/Win64/UnrealEditor.modules']
scripts=['prepare_correction.py','check_correction.py','correction_prefix.cpp','correction_suffix.cpp',
         'correction_editor_tools.py','inspect_correction_editor.py','freeze_correction.py']
paths += [ROOT/'Scripts/CombatAI01/CAIT01'/name for name in scripts]
paths += [ROOT/'Scripts/check_unreal_mcp.py',ROOT/'Scripts/OpeningLobby/functionalbuild01_client.py',ROOT/'Scripts/CombatAI01/CAI00/editor_tools.py']
paths += sorted(p for p in OUT.rglob('*') if p.is_file() and p.suffix in ('.json','.log','.cpp','.patch') and p.name!='editor-load.log')
# Reuse exact immutable inputs, never mutable controller monitoring files.
paths += [PREVIOUS/name for name in ('candidate-manifest.json','build02.log','self-check-check03.json','pure-test-check03.log')]
paths += [ROOT/'Docs/CombatAI01-Tactical01Review.md',OUT.parents[1]/'Review/gap-probe-result.json']
assert len(paths)==len(set(paths))
assert all('Controller' not in p.relative_to(ROOT).parts for p in paths)
rows=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=digest(p)) for p in paths]
manifest=dict(task='MSQ-118',candidate='Candidate02/build01',baseline='5ae0fbc48a2c2f2b3cd3da64d15ec1a70446712a',
    supersedes='Candidate01 only for the CAIT-R1/R2 production corrections; historical evidence retained',
    frozen_at_utc=datetime.now(timezone.utc).isoformat(),
    verification='Native build; 25 affected behavioral assertions including 48 grid cases; 17 source/preservation/wrapper checks; exact DLL editor reload and guarded exit',
    independent_finding_closure='PENDING SAME PRIMARY REVIEWER',
    runtime_movement_position_quality_firing_physics_performance_feel='PENDING OWNER',files=rows)
write('candidate-manifest.json',manifest)
with zipfile.ZipFile(frozen_path,'x',compression=zipfile.ZIP_DEFLATED) as archive:
    for path in paths+[manifest_path]: archive.write(path,path.relative_to(ROOT).as_posix())
with zipfile.ZipFile(evidence_path,'x',compression=zipfile.ZIP_DEFLATED) as archive:
    for path in paths+[manifest_path]:
        if path.is_relative_to(OUT) or path.is_relative_to(ROOT/'Scripts') or path.suffix=='.md':
            archive.write(path,path.relative_to(ROOT).as_posix())
with zipfile.ZipFile(frozen_path) as archive:
    assert all(hashlib.sha256(archive.read(row['path'])).hexdigest()==row['sha256'] for row in rows)
write('freeze-result.json',dict(entries=len(rows),manifest_sha256=digest(manifest_path),
    frozen_sha256=digest(frozen_path),frozen_bytes=frozen_path.stat().st_size,evidence_bytes=evidence_path.stat().st_size,
    all_frozen_bytes_verified=True,mutable_controller_files_included=False))
print(json.dumps(read('freeze-result.json'),indent=2))
