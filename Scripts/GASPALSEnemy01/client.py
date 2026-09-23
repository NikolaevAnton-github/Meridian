"""Reuse the existing official Epic MCP client; write bounded evidence."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Scripts/PurchasedArms02'))
from client import epic


def work(operation, argument=''):
    result = epic('Game.Scripts.GASPALSEnemy01.tools.GASPALSEnemyTools', 'action',
                  dict(operation=operation, argument=argument))
    result = json.loads(result) if isinstance(result, str) else result
    if isinstance(result, dict) and result.get('error'):
        raise RuntimeError(result['error'])
    return result


if __name__ == '__main__':
    result = work(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else '')
    print(json.dumps(result))
