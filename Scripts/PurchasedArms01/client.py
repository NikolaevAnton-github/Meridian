"""Reuse the existing Epic MCP client; no second dispatcher."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'OpeningLobby'))
from functionalbuild01_client import call


def work(operation, argument=''):
    r = call('call_tool', dict(toolset_name='Game.Scripts.PurchasedArms01.purchased_arms_tools.PurchasedArms01Tools',
                             tool_name='action', arguments=dict(operation=operation, argument=argument)))
    value = json.loads(r['content'][0]['text'])['returnValue']
    value = json.loads(value) if isinstance(value, str) else value
    if isinstance(value, dict) and value.get('error'):
        raise RuntimeError(value['error'])
    return value


if __name__ == '__main__':
    print(json.dumps(work(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else '')))
