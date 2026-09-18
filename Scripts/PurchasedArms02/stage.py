"""Stage the source gameplay dependency candidates; retain immutable provenance."""
import hashlib
import json
import shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/PurchasedArms02/Worker'

def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def main():
    dest = OUT / 'staging-manifest.json'
    assert not dest.exists(), 'Never replace provenance'
    assets = json.loads((ROOT / 'Saved/PurchasedArms02/Controller/vendor-asset-evidence.json').read_text(encoding='utf-8-sig'))['assets']
    archive = {r['original']: r for r in json.loads((ROOT / 'Assets/Archive/PurchasedArms01/manifest.json').read_text())['files']}
    queue = [k for k in assets if k.endswith(('/BP_TFA_BaseCharacter', '/DA_TFA_AssaultRifle'))]
    selected, missing = set(), set()
    while queue:
        key = queue.pop()
        if key in selected:
            continue
        if key not in assets:
            missing.add(key)
            continue
        assert '/Environment/' not in key and '/Maps/' not in key, key
        selected.add(key)
        queue.extend(assets[key]['refs'])
    rows = []
    for key in sorted(selected):
        src = Path(assets[key]['source'])
        relative = 'Content/' + key.removeprefix('/Game/') + '.uasset'
        dst = ROOT / relative
        digest = sha(src)
        if relative in archive:
            record = archive[relative]
            assert sha(ROOT / record['archived']) == digest == record['sha256'], relative
        existed = dst.exists()
        if existed:
            assert sha(dst) == digest, dst
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        rows.append(dict(package=key, source=str(src), destination=relative, sha256=digest,
            bytes=src.stat().st_size, existed=existed, archived=archive.get(relative)))
    dest.write_text(json.dumps(dict(files=rows, missing_string_candidates=sorted(missing),
        note='Read-only source audit candidate closure. Final hard runtime closure must exclude UI hints and unrelated startup.'), indent=2))
    print(json.dumps(dict(total=len(rows), new=sum(not r['existed'] for r in rows), bytes=sum(r['bytes'] for r in rows))))

if __name__ == '__main__':
    main()
