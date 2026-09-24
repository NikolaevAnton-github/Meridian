"""Summarize focused PIE captures without changing their original evidence."""
import collections
import json
import math
import sys
from pathlib import Path

OUT=Path(__file__).resolve().parents[3]/'Saved/GASPALSAIFix01'

def norm(v):
    return math.sqrt(sum(x*x for x in v))

def angle(row):
    direction=[a-b for a,b in zip(row['combat']['decision_input']['known_aim'],row['muzzle'])]
    barrel=row['barrel']
    cosine=sum(a*b for a,b in zip(direction,barrel))/(norm(direction)*norm(barrel))
    return math.degrees(math.acos(max(-1,min(1,cosine))))

def summarize(label):
    data=json.loads((OUT/('samples-'+label+'.json')).read_text(encoding='utf-8'))
    rows=data['samples']
    reloads=[s for s in rows if s['combat']['state']=='Reload']
    aimed=[s for s in rows if s['gasp']['source_aim_weight']>=.99 and s['combat']['visible']]
    speeds=[norm(s['gasp']['capsule_velocity'][:2]) for s in rows]
    first=[s for s in rows if s['combat']['shots']==0]
    return {'label':label,'duration':data['end']-data['start'],'samples':len(rows),
        'shots_start':rows[0]['combat']['shots'],'shots_end':rows[-1]['combat']['shots'],
        'reloads_start':rows[0]['combat']['reloads'],'reloads_end':rows[-1]['combat']['reloads'],
        'states':dict(collections.Counter(s['combat']['state'] for s in rows)),
        'moving_commands':sum(norm(s['gasp']['movement_command'])>.01 for s in rows),
        'speed_range':[min(speeds),max(speeds)],
        'pre_first_shot_moving_samples':sum(norm(s['gasp']['capsule_velocity'][:2])>1 for s in first),
        'reload_samples':len(reloads),
        'reload_moving_commands':sum(norm(s['gasp']['movement_command'])>.01 for s in reloads),
        'full_aim_samples':len(aimed),'full_aim_error_range':([min(map(angle,aimed)),max(map(angle,aimed))] if aimed else None),
        'launch_gates':dict(collections.Counter(s['combat']['decision_input']['last_launch_gate'] for s in rows)),
        'peak_active_local_drives':max(s['gasp'].get('active_local_drives',0) for s in rows),
        'local_cache_primed_samples':sum(s['gasp'].get('local_pose_cache_primed',False) for s in rows),
        'end_gasp':rows[-1]['gasp']}

if __name__=='__main__':
    result=[summarize(label) for label in sys.argv[1:]]
    print(json.dumps(result,indent=2))
