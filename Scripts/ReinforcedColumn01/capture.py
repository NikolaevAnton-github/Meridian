"""Preserve native Epic viewport or asset evidence without image processing."""
import base64
import importlib.util
import json
import sys
import argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser()
parser.add_argument('name')
parser.add_argument('asset',nargs='?')
parser.add_argument('--evidence-root',default='Saved/ReinforcedColumn01/Candidate01')
options=parser.parse_args()
OUT=ROOT/options.evidence_root
spec=importlib.util.spec_from_file_location('ngd_capture',ROOT/'Scripts/NextGenDestructionIntegration01/capture.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
path=OUT/(options.name+'.png')
assert not path.exists()
c=module.Client()
if options.asset and options.asset.startswith('/Game/'):
    bitmap=c.call(module.APP,'CaptureAssetImage',dict(assetPath=options.asset))
    record=dict(asset=options.asset)
else:
    args=dict(bShowUI=False,captureTransform=None,annotations=dict(gridSpacing=0,gridExtent=0,gridHeight=0,maxLabelDistance=0,classFilter=dict(refPath='/Script/Engine.Actor'),maxLabels=0))
    record=c.call(module.APP,'CaptureViewport',args)
    bitmap=record.pop('image')
path.write_bytes(base64.b64decode(bitmap['data']))
path.with_suffix('.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(dict(file=str(path),bytes=path.stat().st_size)))
