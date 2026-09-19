"""Copy a bounded, byte-identical existing art subset; never modify source/archive files."""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/EnemyPrototype01/Worker'
ARCHIVE = ROOT / 'Assets/Archive/PurchasedArms01/Content'
VENDOR = Path('D:/devgames/Weapon/TacticalFPSAnimations')
TEMPLATE = Path('D:/UE_5.8/Templates/TemplateResources/High/Characters/Content')
BASE = '/Game/InfimaGames/TacticalFPSAnimations/'
SEEDS = [BASE + p for p in [
    'Common/Characters/Mannequins/Meshes/SKM_Manny_Simple',
    'Weapons/AssaultRifle/Animations/Character/TP/Locomotion/A_TFA_TP_AR_Idle_Loop',
    'Weapons/AssaultRifle/Animations/Character/TP/Combat/A_TFA_TP_AR_Fire',
]] + ['/Game/Characters/Mannequins/Anims/Rifle/Walk/MF_Rifle_Walk_Left',
      '/Game/Characters/Mannequins/Anims/Rifle/Walk/MF_Rifle_Walk_Right']

def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()

if __name__ == '__main__':
    assert (OUT / 'preservation-before.json').exists()
    label = sys.argv[1] if len(sys.argv) > 1 else ''
    if label == 'template':
        SEEDS = ['/Game/Characters/Mannequins/Anims/Rifle/' + name for name in ['MF_Rifle_Idle_ADS', 'MM_Rifle_Fire', 'HitReact/MM_HitReact_Front_Lgt_01']]
    dest = OUT / ('staged-sources-template.json' if label else 'staged-sources.json')
    assert not dest.exists()
    mapping = {'/Game/Characters/' + p.relative_to(TEMPLATE).with_suffix('').as_posix(): p for p in TEMPLATE.rglob('*.uasset')}
    mapping.update({BASE + p.relative_to(VENDOR).with_suffix('').as_posix(): p for p in VENDOR.rglob('*.uasset')})
    mapping.update({'/Game/' + p.relative_to(ARCHIVE).with_suffix('').as_posix(): p for p in ARCHIVE.rglob('*.uasset')})
    queue, seen, rows, missing = list(SEEDS), set(), [], []
    while queue:
        package = queue.pop()
        if package in seen: continue
        seen.add(package)
        target = ROOT / 'Content' / (package.removeprefix('/Game/') + '.uasset')
        if target.exists():
            rows.append(dict(package=package, destination=target.relative_to(ROOT).as_posix(), sha256=sha(target), existing=True))
            continue
        if package not in mapping:
            missing.append(package)
            continue
        source = mapping[package]
        assert not any(s in package for s in ['/Core/', '/Demo/', '/Development/', 'ABP_']), package
        deps = set(x.decode() for x in re.findall(rb'/Game/[A-Za-z0-9_/]+', source.read_bytes()))
        # Preview links are audited at runtime; only required art is staged.
        queue.extend(d for d in deps if not any(s in d for s in ['/Core/', '/Demo/', 'ABP_', '/Animations/']))
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        assert sha(source) == sha(target)
        rows.append(dict(package=package, source=str(source), destination=target.relative_to(ROOT).as_posix(),
                         sha256=sha(target), bytes=target.stat().st_size, existing=False))
    dest.write_text(json.dumps(dict(seeds=SEEDS, files=rows, missing=missing), indent=2), encoding='utf-8')
    print(json.dumps(dict(files=len(rows), added=sum(not r['existing'] for r in rows), bytes=sum(r.get('bytes',0) for r in rows), missing=missing)))
