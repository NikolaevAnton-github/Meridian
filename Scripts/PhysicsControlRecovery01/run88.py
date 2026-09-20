"""Foreground real-input/runtime/WGC runner, using the retained MSQ-87 backend."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'PhysicsControlBalance01'))
import run87
from client88 import work
run87.run68.OUT = Path(__file__).resolve().parents[2] / 'Saved/CombatSlice01/PhysicsControlRecovery01/Worker'
run87.run68.work = work

if __name__ == '__main__':
    for case in json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig')):
        if len(sys.argv) > 2:
            case['video_pid'] = int(sys.argv[2])
        run87.run68.run(case)
