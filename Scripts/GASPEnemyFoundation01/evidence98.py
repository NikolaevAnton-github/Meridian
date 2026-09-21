"""Summarize actual recorded observations; keep failed attempts and raw files intact."""
import json
import math
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/GASPEnemyFoundation01/Worker'

def inspect(name):
    data = json.loads((OUT/(name+'.json')).read_text())
    rows = [r for r in data['rows'] if r.get('dummy') and 'gasp' in r['dummy']]
    transitions = []
    contacts = {}
    for r in rows:
        d=r['dummy']; g=d['gasp']
        key=[g['authority'],d['balance']['state'],d['step']['phase']]
        if not transitions or transitions[-1]['state'] != key:
            transitions.append(dict(t=r['t'],state=key,reason=d['balance']['reason'],capsule=g['capsule_location']))
        for c in d.get('contacts',[]):
            contacts[(d['name'],d['epoch'],c['shot'])]=c
    last=rows[-1]['dummy']
    finite=all(math.isfinite(v) and abs(v)<1e7 for r in rows for v in r['dummy']['gasp']['capsule_location'])
    conflict=sum(bool(r['dummy']['gasp']['enabled_source_controls'] and r['dummy']['balance']['enabled_drives']) for r in rows)
    uncapped=sum(r['dummy']['gasp'].get('unbounded_source_controls',0)>0 for r in rows)
    resumed=[r for r in rows if r['dummy']['gasp']['authority']=='Locomotion' and
        r['dummy']['gasp']['authority_changes'] and any(r['dummy']['gasp']['movement_intent'])]
    dead=[r for r in rows if r['dummy']['deaths']]
    corpse_controls=max((r['dummy']['balance']['enabled_drives']+r['dummy']['gasp']['enabled_source_controls'] for r in dead),default=0)
    handovers=[]
    for a,b in zip(rows,rows[1:]):
        if a['dummy']['gasp']['authority'] != b['dummy']['gasp']['authority']:
            handovers.append(dict(t=b['t'],before=a['dummy']['gasp']['authority'],after=b['dummy']['gasp']['authority'],
                capsule_delta_cm=math.dist(a['dummy']['gasp']['capsule_location'],b['dummy']['gasp']['capsule_location'])))
    report=dict(name=name,samples=len(rows),error=data['error'],duration=data['rows'][-1]['t'],transitions=transitions,
        final_authority=last['gasp']['authority'],health=last['health'],hits=last['physical_hits'],deaths=last['deaths'],
        steps=last['step']['completed'],falls=last['balance']['falls'],getups=last['balance']['get_ups'],
        interruptions=last['balance']['interruptions'],conflicting_control_rows=conflict,uncapped_control_rows=uncapped,
        capsule_finite_and_bounded=finite,handovers=handovers,resumed_movement_rows=len(resumed),
        resumed_movement_distance_cm=math.dist(resumed[0]['dummy']['gasp']['capsule_location'],resumed[-1]['dummy']['gasp']['capsule_location']) if resumed else 0,
        one_impulse_per_contact=all(c['impulse_count']==1 for c in contacts.values()),unique_contacts=len(contacts),
        corpse_contacts=sum(c['was_dead'] for c in contacts.values()),corpse_enabled_controls_max=corpse_controls,
        arm_trunk_contacts=last['gasp'].get('arm_trunk_contacts',{}),peak_arm_trunk_impulse=last['gasp'].get('peak_arm_trunk_impulse',0),
        fixture_count_range=[min(r['counts']['dummy'] for r in data['rows']),max(r['counts']['dummy'] for r in data['rows'])],
        footage='Video/'+name+'.mp4',events=data['events'])
    assert not data['error'] and not conflict and not uncapped and finite, report
    assert report['one_impulse_per_contact'] and not corpse_controls, report
    return report

if __name__=='__main__':
    report=[inspect(name) for name in sys.argv[2:]]
    with (OUT/(sys.argv[1]+'.json')).open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2)
    for r in report:
        print(json.dumps({k:r[k] for k in ['name','final_authority','health','hits','steps','falls','getups','interruptions',
            'resumed_movement_distance_cm','arm_trunk_contacts','corpse_contacts','fixture_count_range']}))
