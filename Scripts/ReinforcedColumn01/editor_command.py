"""Bounded local Unreal Python fallback after a stale Rider connection.

Uses Epic's bundled remote_execution client, loopback only. The live setting is
enabled through Epic MCP and restored at handoff; no project config is saved.
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0,'D:/UE_5.8/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python')
import remote_execution

parser=argparse.ArgumentParser()
parser.add_argument('script')
parser.add_argument('--result',required=True)
args=parser.parse_args()
path=Path(args.result)
assert not path.exists(), path
client=remote_execution.RemoteExecution()
client.start()
try:
    deadline=time.monotonic()+8
    while not client.remote_nodes and time.monotonic()<deadline: time.sleep(.25)
    nodes=[n for n in client.remote_nodes if n.get('project_name')=='MeridianSquad']
    assert len(nodes)==1, client.remote_nodes
    client.open_command_connection(nodes[0]['node_id'])
    source=Path(args.script).read_text(encoding='utf-8')
    result=client.run_command(source,exec_mode=remote_execution.MODE_EXEC_FILE)
    path.write_text(json.dumps(dict(node=nodes[0],result=result),indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='command'}))
    assert result['success'], result.get('result')
finally:
    client.stop()
