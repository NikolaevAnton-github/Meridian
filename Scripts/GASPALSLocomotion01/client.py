import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Scripts/PurchasedArms02'))
from client import epic

def work(operation, argument=''):
    value = epic('Game.Scripts.GASPALSLocomotion01.tools.GASPALSLocomotionTools', 'action',
                 dict(operation=operation, argument=argument))
    result = json.loads(value) if isinstance(value, str) else value
    if isinstance(result, dict) and result.get('error'):
        raise RuntimeError(result['error'])
    return result

if __name__ == '__main__':
    print(json.dumps(work(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else '')))
