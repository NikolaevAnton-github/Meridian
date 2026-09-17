"""Reuse the project's official Epic MCP transport for MSQ-52."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'OpeningLobby'))
from functionalbuild01_client import call

OUT = Path(__file__).resolve().parents[2] / 'Saved/PlayerCharacter01/AnimationAudit01/Worker'


def work(operation, argument=''):
    result = call('call_tool', {
        'toolset_name': 'Game.Scripts.PlayerCharacter01.animation_audit01_tools.PlayerAnimationAudit01Tools',
        'tool_name': 'action', 'arguments': {'operation': operation, 'argument': argument}})
    value = json.loads(result['content'][0]['text'])['returnValue']
    if isinstance(value, str):
        value = json.loads(value)
    if isinstance(value, dict) and value.get('error'):
        raise RuntimeError(value['error'])
    return value


def capture(name):
    import base64
    r=call('call_tool',dict(toolset_name='EditorToolset.EditorAppToolset',tool_name='CaptureViewport',arguments={'captureTransform':None,'annotations':None,'bShowUI':False}))
    v=json.loads(r['content'][0]['text'])['returnValue']
    dest=OUT/(name+'.png')
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(base64.b64decode(v['image']['data']))
    v.pop('image')
    dest.with_suffix('.json').write_text(json.dumps(v,indent=2))
    return str(dest)


if __name__ == '__main__':
    if sys.argv[1] == 'simulate':
        print(call('call_tool',dict(toolset_name='EditorToolset.EditorAppToolset',tool_name='StartPIE',arguments={
            'options':{'bSimulate':True,'playMode':'PlayMode_Simulate','warmupSeconds':1}})))
    elif sys.argv[1] == 'capture':
        print(capture(sys.argv[2]))
    elif sys.argv[1] == 'playbacks':
        import time
        for key in sys.argv[2:]:
            info=work('playback_start',key)
            deadline=time.monotonic()+info['duration']*4+10
            frames=[]
            while True:
                status=work('playback_status')
                name='Playback/'+info['key']+'/frame-'+str(len(frames)).zfill(3)
                frames.append(dict(file=capture(name),sample=status['latest']))
                if not status['active']:break
                assert time.monotonic()<deadline,info
                time.sleep(.25)
            (OUT/'Playback'/info['key']/'frames.json').write_text(json.dumps(frames,indent=2))
            print(json.dumps(dict(key=key,frames=len(frames),samples=status['samples'])),flush=True)
    else:
        print(json.dumps(work(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else '')))
