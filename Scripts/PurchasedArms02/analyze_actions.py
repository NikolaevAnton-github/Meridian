"""Summarize observed input-driven actions, movement and dynamic presentation."""
import json
import math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'Saved/PurchasedArms02/Worker'

def analyze(path):
    data=json.loads(path.read_text()); rows=data['rows']
    if not rows:
        return {'case':path.stem,'error':data['error'],'samples':0,'excluded':True}
    transitions=[]; previous=None
    for r in rows:
        value=(r['montage'],r['busy'],r['aim_requested'],r['crouched'],r['running'],r['sprinting'])
        if value!=previous:
            transitions.append({'t':round(r['t'],4),'action':value[0],'busy':value[1],'aim':value[2],'crouched':value[3],'run':value[4],'sprint':value[5]})
            previous=value
    return {'case':path.stem,'error':data['error'],'samples':len(rows),'actions':sorted(set(r['montage'] for r in rows)),
        'ammo':[min(r['ammo'] for r in rows),max(r['ammo'] for r in rows)],
        'fire_modes':sorted(set(r['fire_mode'] for r in rows)),'grips':sorted(set(r['grip'] for r in rows)),
        'fov':[min(r['fov'] for r in rows),max(r['fov'] for r in rows)],
        'speed_max':max(math.hypot(*r['velocity'][:2]) for r in rows),
        'jump_starts':rows[-1]['jump_starts'],'landings':rows[-1]['landings'],
        'shadow_violations':sum(any(p['shadow_flags']) for r in rows for p in r['parts']),
        'physics':sorted(set(p['actor'].split('_C_')[0] for r in rows for p in r.get('physics',[]))),
        'physics_shadow_violations':sum(p['shadow'] for r in rows for a in r.get('physics',[]) for p in a['parts']),
        'camera_animation':sorted(set(r.get('camera_animation',False) for r in rows)),
        'evaluated_dt_max':max(r['delta'] for r in rows),'transitions':transitions}

def main():
    files=sorted(ROOT.glob('Features01-*.json'))+sorted(ROOT.glob('Interactions0*-*.json'))+sorted(ROOT.glob('Feedback0*-*.json'))
    results=[analyze(p) for p in files]
    (ROOT/'actions-analysis.json').write_text(json.dumps(results,indent=2))
    print(json.dumps([{k:v for k,v in r.items() if k not in ['transitions']} for r in results],indent=2))

if __name__=='__main__': main()
