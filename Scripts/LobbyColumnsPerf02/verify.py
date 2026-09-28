"""Validate saved runtime evidence without starting or mutating an editor."""
import json
import sys
from pathlib import Path
OUT=Path(__file__).resolve().parents[2]/'Saved/LobbyColumnsPerf02'
checks={}
for name in sys.argv[1:]:
    r=json.loads((OUT/(name+'.json')).read_text())
    assert r.get('complete') and not r.get('error'), (name,r.get('error'))
    for label,s in r['samples'].items():
        assert len(s['columns'])==16,(name,label)
        for c in s['columns']:
            p=c['cladding']
            for key in ['render_mismatches','query_mapping_errors','protected_core_moved',
                        'unsupported_wall_tiles','debris_inside_core','retained_tile_simulating',
                        'retained_concrete_nonkinematic']:
                if key in p: assert p[key]==0,(name,label,c['prop']['id'],key,p[key])
            assert p['retention_slots']<=80
        if 'initial' in r['samples'] and label=='reset':
            prior={c['prop']['id']:c for c in r['samples']['initial']['columns']}
            for c in s['columns']:
                assert c['cladding']['attached']==768 and c['cladding']['idle']
                assert c['prop']['reset_generation']==prior[c['prop']['id']]['prop']['reset_generation']+1
        if 'blocker_registry_mismatches' in s.get('blockers',{}):
            assert s['blockers']['blocker_registry_mismatches']==0
    if 'settled' in r['samples']:
        first=r['samples']['initial']; settled=r['samples']['settled']
        assert settled['rifle']['shots']-first['rifle']['shots']==r.get('expected_shots',12)
        assert settled['rifle']['dry_fire']==first['rifle']['dry_fire']
    checks[name]=dict(passed=True,samples=len(r['samples']),frames=len(r['delta']))
(OUT/('verification-'+sys.argv[-1]+'.json')).write_text(json.dumps(checks,indent=2))
print(json.dumps(checks))
