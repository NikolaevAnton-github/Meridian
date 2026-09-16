"""Foreground official Epic MCP orchestration; no task administration."""
import sys,json,types,time
from pathlib import Path
from functionalbuild01_client import call
OUT=Path(__file__).resolve().parents[2]/'Saved/OpeningLobby/MaterialsComplete01/Worker/Correction03'
def work(operation,argument=''):
    r=call('call_tool',dict(toolset_name='Game.Scripts.OpeningLobby.materialscomplete01_optics_tools.OpeningLobbyMaterialsOptics03Tools',tool_name='action',arguments=dict(operation=operation,argument=argument)))
    v=json.loads(r['content'][0]['text'])['returnValue']
    if isinstance(v,str):v=json.loads(v)
    assert not isinstance(v,dict) or not v.get('error'),v
    return v
def captures(folder,views):
    p=Path(__file__).with_name('materialscomplete01_client.py')
    m=types.ModuleType('optics_capture_client');m.__file__=str(p)
    exec(compile(p.read_text(),str(p),'exec'),m.__dict__);m.OUT=OUT;m.work=work
    return m.captures(folder,views)
if __name__=='__main__':
    if sys.argv[1]=='captures':captures(sys.argv[2],sys.argv[3:])
    else:print(json.dumps(work(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else '')))
