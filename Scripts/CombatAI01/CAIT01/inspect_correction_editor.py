"""Discover and invoke the correction lifecycle tools through official Epic MCP."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from Scripts.OpeningLobby.functionalbuild01_client import call
from Scripts import check_unreal_mcp as probe

OUT = ROOT/'Saved/CombatAI01/CAI-T01/Worker/Candidate02'
operation = sys.argv[1]
if operation=='discover':
    probe.OUTPUT=OUT/'EpicReload'
    probe.check()
    names=call('list_toolsets', {})
    (OUT/'epic-correction-toolsets.json').write_text(json.dumps(names,indent=2),encoding='utf-8')
    print(json.dumps(names))
else:
    names=json.loads((OUT/'epic-correction-toolsets.json').read_text())
    text=names['content'][0]['text']
    toolset=next(line[2:].split(':',1)[0] for line in text.splitlines() if 'TacticalCorrectionTools:' in line)
    if operation=='schema':
        result=call('describe_toolset', {'toolset_name':toolset})
    else:
        result=call('call_tool', {'toolset_name':toolset,'tool_name':'action','arguments':{'operation':operation}})
    with (OUT/f'epic-correction-{operation}.json').open('x',encoding='utf-8') as stream:
        json.dump(result,stream,indent=2)
    print(json.dumps(result))
