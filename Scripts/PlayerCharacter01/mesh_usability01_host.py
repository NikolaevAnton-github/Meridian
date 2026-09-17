"""Task-scoped transport and preservation using existing project helpers."""
import json
import sys
from pathlib import Path
import metahuman_trial01_host as host
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/PlayerCharacter01/MeshUsability01/Worker'
OUT.mkdir(parents=True, exist_ok=True)
host.OUT = OUT

def work(op, arg=''):
    result = host.call('call_tool', {'toolset_name': 'Game.Scripts.PlayerCharacter01.mesh_usability01_tools.MeshUsability01Tools',
        'tool_name': 'action', 'arguments': {'operation': op, 'argument': arg}})
    value = json.loads(result['content'][0]['text']).get('returnValue')
    value = json.loads(value) if isinstance(value, str) else value
    if isinstance(value, dict) and value.get('error'): raise RuntimeError(value['error'])
    return value

if __name__ == '__main__':
    op = sys.argv[1]
    if op == 'baseline': host.baseline()
    elif op == 'compare_rig':
        import math
        name=sys.argv[2]
        expected=json.loads((ROOT/'Assets/Source/PlayerCharacter01/AnimationAudit01/rig-contract.json').read_text())
        actual=json.loads((OUT/('inspect-'+name+'.json')).read_text())
        x={b['name']:b for b in expected['bones']};y={b['name']:b for b in actual['bones']}
        result=dict(missing=sorted(set(x)-set(y)),extra=sorted(set(y)-set(x)),parent_mismatches=[n for n in x.keys()&y.keys() if x[n]['parent']!=y[n]['parent']],errors={})
        for kind in ['local_bind','component_bind']:
            rows=[]
            for n in x.keys()&y.keys():
                a=x[n][kind];b=y[n][kind]
                qa=a['rotation_xyzw'];qb=b['rotation_xyzw']
                dot=abs(sum(i*j for i,j in zip(qa,qb)))/math.sqrt(sum(i*i for i in qa)*sum(i*i for i in qb))
                rows.append(dict(name=n,translation_cm=math.dist(a['translation'],b['translation']),rotation_deg=math.degrees(2*math.acos(min(1,dot))),scale=max(abs(i-j) for i,j in zip(a['scale'],b['scale']))))
            result['errors'][kind]={k:max(r[k] for r in rows) for k in ['translation_cm','rotation_deg','scale']}
            result[kind+'_rows']=rows
        host.write('rig-comparison-'+name+'.json',result)
        print(json.dumps({k:v for k,v in result.items() if not k.endswith('_rows')}))
    elif op == 'verify':
        before = json.loads((OUT/'preservation-before.json').read_text())
        changed = {p: host.sha(ROOT/p) if (ROOT/p).exists() else None for p,h in before.items() if not (ROOT/p).exists() or host.sha(ROOT/p)!=h}
        host.write('preservation-after.json', dict(checked=len(before),changed=changed))
        host.write('storage-after.json',host.storage())
        print(json.dumps(dict(checked=len(before),changed=changed)))
    elif op in ('list_toolsets', 'describe_toolset'):
        result=host.call(op, {} if len(sys.argv)<3 else {'toolset_name':sys.argv[2]})
        host.write(op+'.json',result)
        print(json.dumps(result))
    elif op in ('StartPIE','StopPIE'):
        args={'options':{'bSimulate':True,'playMode':'PlayMode_Simulate','warmupSeconds':1}} if op=='StartPIE' else {}
        print(host.call('call_tool',dict(toolset_name='EditorToolset.EditorAppToolset',tool_name=op,arguments=args)))
    elif op=='capture':
        import animation_audit01_client as client
        client.OUT=OUT/'Compatibility05'
        print(client.capture(sys.argv[2]))
    elif op=='playbacks':
        import time
        import animation_audit01_client as client
        client.OUT=OUT/'Compatibility05'
        for key in sys.argv[2:]:
            info=work('playback_start',key);deadline=time.monotonic()+info['duration']*4+10;frames=[]
            while True:
                status=work('playback_status')
                assert not status.get('error'),status
                file=client.capture('Playback/'+info['key']+'/frame-'+str(len(frames)).zfill(3))
                frames.append(dict(file=file,sample=status['latest']))
                if not status['active']:break
                assert time.monotonic()<deadline,info
            dest=client.OUT/'Playback'/info['key']/'frames.json';dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_text(json.dumps(frames,indent=2)+'\n')
            print(json.dumps(dict(key=key,frames=len(frames),samples=status['samples'])),flush=True)
    else: print(json.dumps(work(op, sys.argv[2] if len(sys.argv)>2 else '')))
