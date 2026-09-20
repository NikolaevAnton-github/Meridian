"""Reuse the existing foreground input/capture runner for focused transitions."""
import json
import sys
from pathlib import Path
from client87 import epic, work
import run68

_popen=run68.subprocess.Popen
def capture_popen(args,*a,**kw):
    if len(args)>1 and Path(args[1]).name=='video68.py': args[1]=str(Path(__file__).with_name('video87.py'))
    return _popen(args,*a,**kw)
run68.subprocess.Popen=capture_popen

OUT=Path(__file__).resolve().parents[2]/'Saved/CombatSlice01/PhysicsControlBalance01/Worker'
run68.OUT=OUT
run68.work=work
def capture_epic(toolset,tool,arguments=None):
    if tool=='StartPIE': arguments['options']['playMode']='PlayMode_InEditorFloating'
    return epic(toolset,tool,arguments)
run68.epic=capture_epic

if __name__=='__main__':
    for case in json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig')):
        if len(sys.argv)>2: case['video_pid']=int(sys.argv[2])
        run68.run(case)
