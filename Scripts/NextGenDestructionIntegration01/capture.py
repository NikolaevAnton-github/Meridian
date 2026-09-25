"""Capture exact native Epic MCP viewport output to the candidate evidence directory."""
import base64
import json
import sys
from pathlib import Path
from urllib.request import Request, ProxyHandler, build_opener

OUT = Path('D:/devgames/MeridianSquad/Saved/NextGenDestructionIntegration01/NGD-01/Candidate01')
APP = 'EditorToolset.EditorAppToolset'
class Client:
    def __init__(self):
        self.opener = build_opener(ProxyHandler({}))
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}
        self.serial = 0
        self.rpc('initialize', {'protocolVersion': '2025-11-25', 'capabilities': {}, 'clientInfo': {'name': 'MSQ149Evidence', 'version': '1.0'}})
        self.rpc('notifications/initialized', notification=True)

    def rpc(self, method, params=None, notification=False):
        payload = dict(jsonrpc='2.0', method=method)
        if not notification:
            self.serial += 1
            payload['id'] = self.serial
        if params is not None:
            payload['params'] = params
        request = Request('http://127.0.0.1:8000/mcp', data=json.dumps(payload).encode(), headers=self.headers, method='POST')
        with self.opener.open(request, timeout=55) as response:
            raw = response.read()
            if method == 'initialize':
                self.headers['Mcp-Session-Id'] = response.headers['Mcp-Session-Id']
            if notification:
                return
        result = json.loads(raw)
        if 'error' in result:
            raise RuntimeError(result['error'])
        result = result['result']
        if result.get('isError'):
            raise RuntimeError(result)
        return result

    def call(self, toolset, name, arguments=None):
        result = self.rpc('tools/call', {'name': 'call_tool', 'arguments': dict(toolset_name=toolset, tool_name=name, arguments=arguments or {})})
        value = json.loads(result['content'][0]['text'])
        return value.get('returnValue', value)

if __name__ == '__main__':
    name = sys.argv[1]
    assert name.replace('-', '').replace('_', '').isalnum()
    path = OUT / (name + '.png')
    assert not path.exists(), 'Do not overwrite evidence.'
    c = Client()
    args = {'bShowUI': False, 'captureTransform': None, 'annotations': {'gridSpacing': 0, 'gridExtent': 0, 'gridHeight': 0, 'maxLabelDistance': 0, 'classFilter': {'refPath': '/Script/Engine.Actor'}, 'maxLabels': 0}}
    if len(sys.argv) > 2:
        args['captureTransform'] = json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))
    record = c.call(APP, 'CaptureViewport', args)
    bitmap = record.pop('image')
    path.write_bytes(base64.b64decode(bitmap['data']))
    path.with_suffix('.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps({'file': str(path), 'bytes': path.stat().st_size}))
