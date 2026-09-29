"""Save actual Epic MCP viewport images as immutable rollback evidence."""
import base64
import importlib.util
import json
import sys
from audit import ROOT, OUT

spec = importlib.util.spec_from_file_location('rollback_mcp_capture', ROOT / 'Scripts/NextGenDestructionIntegration01/capture.py')
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)
name = sys.argv[1]
assert name.replace('-', '').isalnum()
path = OUT / (name + '.png')
assert not path.exists()
args = dict(bShowUI=False, captureTransform=None, annotations=dict(gridSpacing=0, gridExtent=0, gridHeight=0,
            maxLabelDistance=0, classFilter=dict(refPath='/Script/Engine.Actor'), maxLabels=0))
if len(sys.argv) > 2:
    previous = json.loads((ROOT / sys.argv[2]).read_text())
    args['captureTransform'] = dict(location=previous['cameraLocation'], rotation=previous['cameraRotation'])
record = client.Client().call(client.APP, 'CaptureViewport', args)
bitmap = record.pop('image')
path.write_bytes(base64.b64decode(bitmap['data']))
with path.with_suffix('.json').open('x', encoding='utf-8') as f:
    json.dump(record, f, indent=2)
print(json.dumps({'file': path.name, 'bytes': path.stat().st_size}))
