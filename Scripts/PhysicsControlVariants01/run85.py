"""Reuse the existing foreground runner and real-time video capture."""
import json
import sys
from pathlib import Path
from client85 import epic, work
import run68

OUT = Path(__file__).resolve().parents[2] / 'Saved/CombatSlice01/PhysicsControlVariants01/Worker'
run68.OUT = OUT
run68.work = work

def capture_epic(toolset, tool, arguments=None):
    if tool == 'StartPIE': arguments['options']['playMode'] = 'PlayMode_InEditorFloating'
    return epic(toolset, tool, arguments)

run68.epic = capture_epic

if __name__ == '__main__':
    for case in json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig')):
        if len(sys.argv) > 2: case['video_pid'] = int(sys.argv[2])
        run68.run(case)
