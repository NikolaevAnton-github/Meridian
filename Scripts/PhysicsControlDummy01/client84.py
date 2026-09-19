"""Reuse the retained client; no new service or benchmark infrastructure."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'CombatFoundation01'))
from client68 import epic

def work(operation, argument=''):
    result = epic('Game.Scripts.PhysicsControlDummy01.tools84.PhysicsControlDummy01Tools', 'action',
                 {'operation': operation, 'argument': argument})
    result = json.loads(result) if isinstance(result, str) else result
    if isinstance(result, dict) and result.get('error'):
        raise RuntimeError(result['error'])
    return result

if __name__ == '__main__':
    print(json.dumps(work(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else '')))
