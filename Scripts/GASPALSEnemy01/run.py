"""Use the retained input runner and ordinary-speed WGC recording backend."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Scripts/PhysicsControlBalance01'))
sys.path.insert(0,str(ROOT/'Scripts/CombatFoundation01'))
import run87
from client68 import epic


def work(operation,argument=''):
    value = epic('Game.Scripts.GASPALSEnemy01.tools.GASPALSEnemyTools','action',dict(operation='harness_'+operation,argument=argument))
    value = json.loads(value) if isinstance(value,str) else value
    if isinstance(value,dict) and value.get('error'): raise RuntimeError(value['error'])
    return value


active_case = None
def prepare_epic(toolset,tool,arguments=None):
    result = run87.capture_epic(toolset,tool,arguments)
    if tool=='StartPIE': work('prepare',json.dumps(active_case))
    return result


run87.run68.OUT = ROOT/'Saved/CombatSlice01/GASPALSEnemy01'
run87.run68.work = work
run87.run68.epic = prepare_epic
if __name__=='__main__':
    for case in json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig')):
        active_case = case
        if len(sys.argv)>2: case['video_pid']=int(sys.argv[2])
        run87.run68.run(case)
