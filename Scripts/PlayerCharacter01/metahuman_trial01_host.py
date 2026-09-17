"""Small host utilities for MSQ-54; reuses the established Epic MCP transport."""
import hashlib
import base64
import json
import os
import stat
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/PlayerCharacter01/MetaHumanTrial01/Worker'
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / 'Scripts/OpeningLobby'))
from functionalbuild01_client import call

def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def write(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')

def storage():
    sizes = {}
    for base, dirs, files in os.walk(ROOT, followlinks=False):
        dirs[:] = [d for d in dirs if not ((Path(base) / d).lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)]
        for name in files:
            p = Path(base) / name
            if not p.is_symlink():
                key = p.relative_to(ROOT).parts[0]
                try: sizes[key] = sizes.get(key, 0) + p.stat().st_size
                except OSError: pass
    return dict(bytes=sum(sizes.values()), by_root=sizes, excludes='Reparse-point directory targets and symlink files')

def baseline():
    dest = OUT / 'preservation-before.json'
    assert not dest.exists(), 'Never replace the initial baseline'
    files = []
    for prefix in ['Assets/Source/PlayerCharacter01', 'Assets/Concepts/PlayerCharacter01', 'Content', 'Config']:
        files.extend(p for p in (ROOT / prefix).rglob('*') if p.is_file())
    files.append(ROOT / 'MeridianSquad.uproject')
    write(dest.name, {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in files})
    (OUT / 'DefaultEngine.before.ini').write_bytes((ROOT / 'Config/DefaultEngine.ini').read_bytes())
    (OUT / 'MeridianSquad.before.uproject').write_bytes((ROOT / 'MeridianSquad.uproject').read_bytes())
    (OUT / 'git-before.txt').write_bytes(subprocess.check_output(['git', 'status', '--short'], cwd=ROOT))
    write('storage-before.json', storage())
    print(json.dumps(dict(protected_files=len(files), storage=json.loads((OUT / 'storage-before.json').read_text()))))

def work(op, arg=''):
    result = call('call_tool', {'toolset_name': 'Game.Scripts.PlayerCharacter01.metahuman_trial01_tools.MetaHumanTrial01Tools',
        'tool_name': 'action', 'arguments': {'operation': op, 'argument': arg}})
    value = json.loads(result['content'][0]['text']).get('returnValue')
    value=json.loads(value) if isinstance(value,str) else value
    if isinstance(value,dict) and value.get('error'):raise RuntimeError(value['error'])
    return value

if __name__ == '__main__':
    if sys.argv[1] == 'baseline': baseline()
    elif sys.argv[1] == 'storage-before':
        write('storage-before.json', storage())
        print((OUT / 'storage-before.json').read_text())
    elif sys.argv[1] == 'capture':
        result = call('call_tool', {'toolset_name': 'EditorToolset.EditorAppToolset',
            'tool_name': 'CaptureEditorImage', 'arguments': {}})
        image_data = json.loads(result['content'][0]['text'])['returnValue']
        dest = OUT / (sys.argv[2] + '.png')
        dest.write_bytes(base64.b64decode(image_data['data']))
        print(str(dest))
    elif sys.argv[1] in ('list_toolsets', 'describe_toolset'):
        result = call(sys.argv[1], {} if len(sys.argv) < 3 else {'toolset_name': sys.argv[2]})
        write(sys.argv[1] + '.json', result)
        print(json.dumps(result))
    elif sys.argv[1] in ('StartPIE','StopPIE'):
        args={'options':{'bSimulate':True,'playMode':'PlayMode_Simulate','warmupSeconds':1}} if sys.argv[1]=='StartPIE' else {}
        print(call('call_tool',dict(toolset_name='EditorToolset.EditorAppToolset',tool_name=sys.argv[1],arguments=args)))
    elif sys.argv[1] == 'playbacks02':
        import animation_audit01_client as audit_client
        audit_client.OUT=OUT/'Compatibility'
        for key in sys.argv[2:]:
            info=work('candidate_playback_start02',key)
            deadline=time.monotonic()+info['duration']*4+10
            frames=[]
            while True:
                status=work('candidate_playback_status02')
                name='Playback/'+info['key']+'/frame-'+str(len(frames)).zfill(3)
                try: file=audit_client.capture(name)
                except Exception as exc: file=None; write('viewport-capture-failure.json',{'error':str(exc)})
                frames.append(dict(file=file,sample=status['latest']))
                if not status['active']:break
                assert time.monotonic()<deadline,info
            dest=audit_client.OUT/'Playback'/info['key']/'frames.json'
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_text(json.dumps(frames,indent=2)+'\n')
            print(json.dumps(dict(key=key,frames=len(frames),samples=status['samples'])),flush=True)
    elif sys.argv[1] == 'verify':
        baseline_data = json.loads((OUT / 'preservation-before.json').read_text())
        changed = {p: {'before': h, 'after': sha(ROOT / p) if (ROOT / p).exists() else None}
                   for p, h in baseline_data.items() if not (ROOT / p).exists() or sha(ROOT / p) != h}
        write('preservation-after.json', dict(checked=len(baseline_data), changed=changed))
        write('storage-after.json', storage())
        print(json.dumps(dict(checked=len(baseline_data), changed=changed)))
    else:
        print(json.dumps(work(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else '')))
