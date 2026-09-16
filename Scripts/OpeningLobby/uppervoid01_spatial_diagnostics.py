"""Foreground exact-pose diagnostic capture through official Epic MCP."""
import json,time
from uppervoid01_spatial_client import work,captures,call

def start():
    return call('call_tool',dict(toolset_name='EditorToolset.EditorAppToolset',tool_name='StartPIE',arguments=dict(options=dict(bSimulate=False,playMode='PlayMode_InEditorFloating',warmupSeconds=2))))

def capture_set(folder,views):
    work('capture_prepare',folder)
    try:
        start();time.sleep(2)
        work('capture_standing',folder)
        captures(folder,views)
    finally:
        if work('state')['pie']:
            work('stop');time.sleep(2)
        work('capture_restore',folder)

if __name__=='__main__':
    for tag in ['Disabled','WorldZ','Transmission']:
        print(json.dumps(work('build',tag)),flush=True)
        capture_set(tag,['close-column-90'])
        print(json.dumps(work('audit',tag)),flush=True)
    print(json.dumps(work('build','Restore')),flush=True)
