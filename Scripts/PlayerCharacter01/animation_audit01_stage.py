"""Stage byte-identical selected art and explicit dependency candidates only."""
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/PlayerCharacter01/AnimationAudit01/Worker'
SOURCE = ROOT / 'Assets/Source/PlayerCharacter01/AnimationAudit01'
WEAPON = Path('D:/devgames/Weapon/TacticalFPSAnimations')
TEMPLATE = Path('D:/UE_5.8/Templates/TemplateResources/High/Characters/Content')


def refs(path):
    return sorted(set(x.decode() for x in re.findall(rb'/Game/[A-Za-z0-9_/]+', path.read_bytes())))


def main():
    SOURCE.mkdir(parents=True, exist_ok=True)
    final=SOURCE/'selected-sources.json'
    if final.exists() and json.loads(final.read_text()).get('schema')==2:
        for row in json.loads(final.read_text())['files']:
            src=Path(row['source']);dst=ROOT/row['destination']
            assert hashlib.file_digest(src.open('rb'),'sha256').hexdigest()==row['sha256'],src
            if dst.exists():
                assert hashlib.file_digest(dst.open('rb'),'sha256').hexdigest()==row['sha256'],dst
            else:
                dst.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(src,dst)
        print('Verified/restored the exact final selected subset without rebaselining it.')
        return
    mapping = {'/Game/InfimaGames/TacticalFPSAnimations/' + p.relative_to(WEAPON).with_suffix('').as_posix(): p
               for p in WEAPON.rglob('*.uasset')}
    mapping.update({'/Game/Characters/' + p.relative_to(TEMPLATE).with_suffix('').as_posix(): p
                    for p in TEMPLATE.rglob('*.uasset')})
    seeds = []
    for key, p in mapping.items():
        n = p.stem
        if '/Weapons/AssaultRifle/Animations/' in key and n.startswith(('A_', 'BS_')) and not any(x in n for x in
            ['Quick', 'Emergency', 'Inspect', 'Jam', 'Melee', 'Grenade', 'Syringe', 'MagCheck', 'Check', 'Heal']):
            seeds.append(key)
        if '/Anims/Rifle/' in key and any(x in key for x in ['/Walk/', '/Jog/', '/Jump/']):
            seeds.append(key)
        if n in ['SK_TFA_AR', 'SK_TFA_AR_Magazine', 'SM_TFA_AR_Magazine_Full',
                 'SM_TFA_AR_Magazine_Empty', 'SM_TFA_AR_Handguard_Default', 'SM_TFA_AR_ATT_Sight_Front',
                 'SM_TFA_AR_ATT_Sight_Rear', 'SKM_FP_Manny_Simple', 'SKM_Manny_Simple']:
            seeds.append(key)
    selected, unresolved, excluded = {}, [], []
    queue = list(seeds)
    while queue:
        key = queue.pop()
        if key in selected:
            continue
        if key not in mapping:
            if key not in unresolved:
                unresolved.append(key)
            continue
        p = mapping[key]
        if '/Core/' in key or '/Demo/' in key or p.stem.startswith(('ABP_TFA_', 'AM_')):
            excluded.append(key)
            continue
        selected[key] = p
        queue.extend(d for d in refs(p) if d != key and d not in selected)
    records = []
    for key, p in sorted(selected.items()):
        dst = ROOT / 'Content' / (key.removeprefix('/Game/') + '.uasset')
        sha = hashlib.file_digest(p.open('rb'), 'sha256').hexdigest()
        if dst.exists():
            assert hashlib.file_digest(dst.open('rb'), 'sha256').hexdigest() == sha, dst
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
        records.append(dict(package=key, source=str(p), destination=dst.relative_to(ROOT).as_posix(),
                            bytes=p.stat().st_size, sha256=sha, seed=key in seeds))
    result = dict(schema=1, selection='MSQ-52 diagnostic selected art, not original-character acceptance',
                  engine='5.8.1-56057345', files=records, unresolved_string_references=sorted(unresolved),
                  excluded_demo_references=sorted(set(excluded)),
                  dependency_note='Binary path candidates; runtime AssetRegistry verification follows.')
    (SOURCE / 'selected-sources.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    demo = {k:refs(p) for k,p in mapping.items() if p.stem.startswith('AM_')}
    (OUT / 'source-montage-references.json').write_text(json.dumps(demo, indent=2))
    print(json.dumps(dict(count=len(records), bytes=sum(x['bytes'] for x in records),
                          unresolved=unresolved, excluded=sorted(set(excluded)))))


if __name__ == '__main__':
    main()
