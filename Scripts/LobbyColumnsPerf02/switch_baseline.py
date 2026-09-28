"""Guarded temporary A/B source switch; never overwrite a changed owner file."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/LobbyColumnsPerf02'
paths=['Source/MeridianSquad/'+x for x in ['CombatProjectileWorld.cpp','CombatProjectileWorld.h','DemoColumnCladding.cpp','DemoColumnCladding.h']]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mode=sys.argv[1]
expected=json.loads((OUT/('compile03.json' if mode=='baseline' else 'baseline-source.json')).read_text())['hashes']
for p in paths: assert sha(ROOT/p)==expected[p], 'Source changed; preserve it: '+p
if mode=='baseline':
    for p in paths:
        data=subprocess.check_output(['git','show','83181e1:'+p],cwd=ROOT).decode('utf-8')
        if p.endswith('.cpp'):
            category='ProjectileBlockers' if 'CombatProjectile' in p else 'LobbyColumns'
            marker='#include "Serialization/JsonSerializer.h"'
            data=data.replace(marker,marker+'\n#include "ProfilingDebugging/CsvProfiler.h"\n\nCSV_DEFINE_CATEGORY('+category+', true);')
            if category=='ProjectileBlockers':
                for signature,metric in [
                    ('TMap<TWeakObjectPtr<UPrimitiveComponent>, ACombatProjectileWorld::FBlockerSample> ACombatProjectileWorld::SampleBlockers() const','Collect'),
                    ('bool ACombatProjectileWorld::BlockersMatch(const TMap<TWeakObjectPtr<UPrimitiveComponent>, FBlockerSample>& Samples) const','Compare')]:
                    data=data.replace(signature+'\n{',signature+'\n{\n    CSV_SCOPED_TIMING_STAT(ProjectileBlockers, '+metric+');')
            else:
                for signature,metric in [
                    ('void UDemoColumnCladding::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)','CladdingTick'),
                    ('void UDemoColumnCladding::UpdateDebris(float DeltaTime)','DebrisUpdate'),
                    ('void UDemoColumnCladding::UpdateFacingImpacts()','FacingImpacts')]:
                    data=data.replace(signature+'\n{',signature+'\n{\n    CSV_SCOPED_TIMING_STAT(LobbyColumns, '+metric+');')
        (ROOT/p).write_bytes(data.encode('utf-8'))
    (OUT/'baseline-source.json').write_text(json.dumps(dict(base='83181e1',instrumentation_only=True,
        hashes={p:sha(ROOT/p) for p in paths}),indent=2))
else:
    assert mode=='candidate'
    for p in paths:(ROOT/p).write_bytes((OUT/'compile03-source'/Path(p).name).read_bytes())
    final=json.loads((OUT/'compile03.json').read_text())['hashes']
    assert all(sha(ROOT/p)==final[p] for p in paths)
print(mode+' sources selected; unrelated files untouched')
