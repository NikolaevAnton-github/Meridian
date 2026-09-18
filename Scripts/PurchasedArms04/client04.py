"""Reuse the existing Epic MCP transport for focused MSQ-64 operations."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'PurchasedArms02'))
from client import epic


def work(operation, argument=''):
    value = epic('Game.Scripts.PurchasedArms04.tools04.PurchasedArms04Tools', 'action',
                 {'operation': operation, 'argument': argument})
    value = json.loads(value) if isinstance(value, str) else value
    if isinstance(value, dict) and value.get('error'):
        raise RuntimeError(value['error'])
    return value


if __name__ == '__main__':
    result = work(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else '')
    if sys.argv[1] == 'audit':
        result = {'graphs': len(result['graphs']), 'state': result['state']}
    print(json.dumps(result))
