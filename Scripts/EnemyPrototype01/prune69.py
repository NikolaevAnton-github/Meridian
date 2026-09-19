"""Preserve worker-only audit extras outside active Content after dependency review."""
import json
import shutil
from pathlib import Path
from preserve69 import base, ROOT, OUT

keep = set(json.loads((OUT / 'dependency-plan-01.json').read_text())['closure'])
rows = []
for name in ['staged-sources.json','staged-sources-template.json']:
    rows.extend(r for r in json.loads((OUT/name).read_text())['files'] if not r['existing'] and r['package'] not in keep)
bad = ROOT / 'Content/Development/EnemyPrototype01/A_Enemy_Idle.uasset'
if bad.exists(): rows.append(dict(destination=bad.relative_to(ROOT).as_posix(), sha256=base.sha(bad)))
plan = []
for row in rows:
    src = (ROOT / row['destination']).resolve()
    dst = (OUT / 'ExcludedAuditCopies' / row['destination']).resolve()
    assert src.is_relative_to((ROOT / 'Content').resolve())
    assert dst.is_relative_to((OUT / 'ExcludedAuditCopies').resolve())
    assert src.exists() and not dst.exists() and base.sha(src) == row['sha256']
    plan.append(dict(source=str(src), destination=str(dst), sha256=row['sha256'], bytes=src.stat().st_size))
path = OUT / 'excluded-audit-copies.json'
assert not path.exists()
path.write_text(json.dumps(plan,indent=2),encoding='utf-8')
for row in plan:
    dst = Path(row['destination'])
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.move(row['source'], dst)
    assert base.sha(dst) == row['sha256']
print(json.dumps(dict(excluded=len(plan), bytes=sum(r['bytes'] for r in plan))))
