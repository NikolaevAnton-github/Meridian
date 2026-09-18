"""Use the existing official Epic MCP transport for MSQ-62 operations."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'OpeningLobby'))
from functionalbuild01_client import call

def epic(toolset, tool, arguments=None):
    r = call('call_tool', {'toolset_name':toolset,'tool_name':tool,'arguments':arguments or {}})
    if r.get('isError'):
        raise RuntimeError(str(r))
    value = json.loads(r['content'][0]['text']).get('returnValue')
    return value

def work(operation, argument=''):
    value = epic('Game.Scripts.PurchasedArms02.tools02.PurchasedArms02Tools', 'action', {'operation':operation,'argument':argument})
    value = json.loads(value) if isinstance(value,str) else value
    if isinstance(value,dict) and value.get('error'):
        raise RuntimeError(value['error'])
    return value

if __name__ == '__main__':
    print(json.dumps(work(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else '')))
