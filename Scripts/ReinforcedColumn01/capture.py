"""Preserve native Epic viewport or asset evidence without image processing."""
import base64
import importlib.util
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/ReinforcedColumn01/Candidate01'
spec=importlib.util.spec_from_file_location('ngd_capture',ROOT/'Scripts/NextGenDestructionIntegration01/capture.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
path=OUT/(sys.argv[1]+'.png')
assert not path.exists()
c=module.Client()
if len(sys.argv)>2 and sys.argv[2].startswith('/Game/'):
    bitmap=c.call(module.APP,'CaptureAssetImage',dict(assetPath=sys.argv[2]))
    record=dict(asset=sys.argv[2])
else:
    args=dict(bShowUI=False,captureTransform=None,annotations=dict(gridSpacing=0,gridExtent=0,gridHeight=0,maxLabelDistance=0,classFilter=dict(refPath='/Script/Engine.Actor'),maxLabels=0))
    record=c.call(module.APP,'CaptureViewport',args)
    bitmap=record.pop('image')
path.write_bytes(base64.b64decode(bitmap['data']))
path.with_suffix('.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(dict(file=str(path),bytes=path.stat().st_size)))
