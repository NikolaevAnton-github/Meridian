"""Official Epic MCP discovery/calls using the existing project client."""
from pathlib import Path
import json
import sys
import time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from Scripts.OpeningLobby.functionalbuild01_client import call
OUT=ROOT/'Saved/CombatAI01/CAI-02/Worker/Candidate01'
if len(sys.argv)>2:
    assert sys.argv[2]=='FinalReload'
    OUT=OUT/'FinalReload'
operation=sys.argv[1]
if operation=='discover':
    deadline=time.monotonic()+45
    while True:
        try:
            result=call('list_toolsets',{})
            if 'SensesTools:' in result['content'][0]['text']:break
        except Exception:
            pass
        if time.monotonic()>deadline:raise RuntimeError('Editor tools not ready within this bounded check')
        time.sleep(2)
    toolset=next(line[2:].split(':',1)[0] for line in result['content'][0]['text'].splitlines() if 'SensesTools:' in line)
    result=call('describe_toolset',{'toolset_name':toolset})
    with (OUT/'epic-toolset.json').open('x') as f:json.dump(dict(toolset=toolset,schema=result),f,indent=2)
    print(toolset)
else:
    toolset=json.loads((OUT/'epic-toolset.json').read_text())['toolset']
    result=call('call_tool',{'toolset_name':toolset,'tool_name':'action','arguments':{'operation':operation}})
    with (OUT/f'epic-{operation}.json').open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps(result))
