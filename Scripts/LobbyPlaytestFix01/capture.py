"""Save native Epic viewport evidence; reuses the existing verified MCP client."""
import base64
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/LobbyPlaytestFix01/Candidate01'
spec = importlib.util.spec_from_file_location('ngd_capture', ROOT / 'Scripts/NextGenDestructionIntegration01/capture.py')
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)
name = sys.argv[1]
assert name.replace('-', '').replace('_', '').isalnum()
path = OUT / (name + '.png')
assert not path.exists()
args = dict(bShowUI=False, captureTransform=None, annotations=dict(gridSpacing=0, gridExtent=0, gridHeight=0, maxLabelDistance=0, classFilter=dict(refPath='/Script/Engine.Actor'), maxLabels=0))
if len(sys.argv) > 2:
    args['captureTransform'] = json.loads(Path(sys.argv[2]).read_text())
record = client.Client().call(client.APP, 'CaptureViewport', args)
bitmap = record.pop('image')
path.write_bytes(base64.b64decode(bitmap['data']))
path.with_suffix('.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
print(json.dumps(dict(file=str(path), bytes=path.stat().st_size)))
