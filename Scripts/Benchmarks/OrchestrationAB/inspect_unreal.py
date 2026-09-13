"""Independent acceptance of the benchmark through official Epic MCP."""
import argparse
import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, build_opener, ProxyHandler

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'Saved/AgentSetup/OrchestrationAB'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_id', choices=['BenchA', 'BenchB'])
    opts = parser.parse_args()
    run_id = opts.run_id
    out = BASE / 'Independent' / run_id
    out.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    opener = build_opener(ProxyHandler({}))
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}
    seq = 0
    def rpc(method, params=None, notification=False):
        nonlocal seq
        seq += 1
        msg = {'jsonrpc': '2.0', 'method': method}
        if not notification:
            msg['id'] = seq
        if params is not None:
            msg['params'] = params
        req = Request('http://127.0.0.1:8000/mcp', data=json.dumps(msg).encode(), headers=headers, method='POST')
        with opener.open(req, timeout=180) as response:
            if method == 'initialize':
                headers['Mcp-Session-Id'] = response.headers['Mcp-Session-Id']
            raw = response.read()
        if notification:
            return None
        result = json.loads(raw)
        if result.get('error'):
            raise RuntimeError(result['error'])
        result = result['result']
        if result.get('isError'):
            raise RuntimeError(result.get('content'))
        return result
    def call(toolset, name, args):
        result = rpc('tools/call', {'name': 'call_tool', 'arguments': {'toolset_name': toolset, 'tool_name': name, 'arguments': args}})
        return json.loads(next(c['text'] for c in result['content'] if c['type'] == 'text'))['returnValue']
    initialized = rpc('initialize', {'protocolVersion': '2025-11-25', 'capabilities': {}, 'clientInfo': {'name': 'MeridianSquadIndependentAcceptance', 'version': '1'}})
    headers['Mcp-Protocol-Version'] = initialized['protocolVersion']
    rpc('notifications/initialized', notification=True)
    program = 'editor_toolset.toolsets.programmatic.ProgrammaticToolset'
    # The controller read these instructions and used tool output schemas before writing the template.
    env = call(program, 'get_execution_environment', {})
    (out / 'epic-environment.json').write_text(json.dumps(env, indent=2), encoding='utf-8')
    script = Path(__file__).with_name('inspect_unreal.template.py').read_text().replace('__RUN_ID__', run_id)
    report = json.loads(call(program, 'execute_tool_script', {'script': script}))
    physical = ROOT / 'Content/Development/Benchmark' / run_id
    saved_assets = []
    for name in report['assets']:
        path = physical / (name + '.uasset')
        exists = path.is_file()
        saved_assets.append({'path': path.relative_to(ROOT).as_posix(), 'exists': exists,
                             'bytes': path.stat().st_size if exists else None,
                             'sha256': hashlib.file_digest(path.open('rb'), 'sha256').hexdigest() if exists else None})
        if not exists:
            report['failures'].append('asset_not_saved:' + name)
    report['saved_assets'] = saved_assets
    image_path = out / 'UnrealCrate.png'
    try:
        capture = call('EditorToolset.EditorAppToolset', 'CaptureAssetImage', {'assetPath': '/Game/Development/Benchmark/' + run_id + '/SM_' + run_id + '_Crate'})
        image_data = base64.b64decode(capture['data'])
        image_path.write_bytes(image_data)
        report['thumbnail'] = {'path': image_path.relative_to(ROOT).as_posix(), 'mime_type': capture['mimeType'], 'sha256': hashlib.sha256(image_data).hexdigest()}
    except Exception as exc:
        report['thumbnail'] = {'warning': type(exc).__name__ + ': ' + str(exc)}
    report['started_at'] = started.isoformat()
    report['completed_at'] = datetime.now(timezone.utc).isoformat()
    report['passed'] = not report['failures']
    (out / 'unreal-verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'run_id': run_id, 'passed': report['passed'], 'triangles': report['triangles'], 'failures': report['failures'], 'thumbnail': str(image_path)}))
    return 0 if report['passed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
