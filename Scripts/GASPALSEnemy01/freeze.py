"""Freeze verified runtime bytes without changing historical intake records."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/CombatSlice01/GASPALSEnemy01'

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

imports=[]
for name in ['pose-import.json','prop-import.json']:
    for row in json.loads((OUT/name).read_text()):
        assert digest(row['source_file'])==row['source_sha256']
        imports.append(dict(source_file=row['source_file'],source_sha256=row['source_sha256'],
            file=Path(row['destination_file']).relative_to(ROOT).as_posix(),
            sha256=digest(row['destination_file']),bytes=Path(row['destination_file']).stat().st_size))
modified=ROOT/'Plugins/GASPEnemyFoundation01/Content/Blueprints/SandboxCharacter_Mover_ABP.uasset'
before=json.loads((OUT/'modified-package-before.json').read_text())
assert digest(before['archive'])==before['sha256']
files=[modified,ROOT/'Plugins/GASPALSEnemy01/GASPALSEnemy01.uplugin']
files += [ROOT/'Source/MeridianSquad'/name for name in ['GASPEnemyFixture.h','GASPEnemyFixture.cpp',
    'GASPALSRifleAnimInstance.h','GASPALSRifleAnimInstance.cpp','GASPEnemyRifle.cpp']]
preservation=[]
for row in json.loads((OUT/'preservation-before.json').read_text(encoding='utf-8-sig'))[:3]:
    actual=digest(row['Path'])
    assert actual==row['Hash'].lower(),row['Path']
    preservation.append(dict(file=row['Path'],sha256=actual))
closure=json.loads((OUT/'dependency-closure.json').read_text())
assert len(closure['packages'])==16 and not closure['external']
result=dict(candidate='GASPALSEnemy01-Candidate01',build='build11.log',engine='5.8.3',
    imports=imports,modified_package_before=before,
    files=[dict(file=p.relative_to(ROOT).as_posix(),sha256=digest(p),bytes=p.stat().st_size) for p in files],
    binary=dict(file='Binaries/Win64/UnrealEditor-MeridianSquad.dll',sha256=digest(ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll')),
    owner_preservation=preservation,
    evidence=['Pilot02-RiflePoses','Pilot03-AimMovement','Rollout01-FallGetup','Rollout02-DeathResetSlow',
        'Fix03-AimedStop','Fix04-CrouchHitAim','Final02-ThreeRendered'],
    scope_note='Earlier passing criteria retained where final yaw/cone correction does not change the exercised behavior; superseded aiming failures are preserved separately.')
path=OUT/'Candidate01-identity.json'
with path.open('x',encoding='utf-8') as stream: json.dump(result,stream,indent=2)
print(json.dumps(dict(path=str(path),sha256=digest(path),imports=len(imports),files=len(files))))
