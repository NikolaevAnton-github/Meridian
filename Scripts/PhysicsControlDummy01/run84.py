"""Use the retained foreground runner and ordinary-speed recorder for MSQ-84."""
import json
import sys
from pathlib import Path
from client84 import epic, work
import run68

OUT = Path(__file__).resolve().parents[2] / 'Saved/CombatSlice01/PhysicsControlDummy01/Worker'
run68.OUT = OUT
run68.work = work

def capture_epic(toolset, tool, arguments=None):
    if tool == 'StartPIE':
        arguments['options']['playMode'] = 'PlayMode_InEditorFloating'
    return epic(toolset, tool, arguments)

run68.epic = capture_epic

if __name__ == '__main__':
    if sys.argv[1] == 'probe':
        assert not epic('EditorToolset.EditorAppToolset','IsPIERunning')
        work('performance')
        try:
            epic('EditorToolset.EditorAppToolset','StartPIE',{'options':dict(bSimulate=False,playMode='PlayMode_InViewPort',warmupSeconds=1)})
            print(json.dumps(work('probe',sys.argv[2])))
        finally:
            if epic('EditorToolset.EditorAppToolset','IsPIERunning'): epic('EditorToolset.EditorAppToolset','StopPIE')
            work('performance','restore')
    else:
        for case in json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig')):
            if len(sys.argv)>2: case['video_pid'] = int(sys.argv[2])
            run68.run(case)
