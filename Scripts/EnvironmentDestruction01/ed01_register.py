"""Bootstrap registration only; mutations run through official Epic MCP."""
import json
import sys
import time
sys.path.insert(0, 'D:/UE_5.8/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python')
import remote_execution

r = remote_execution.RemoteExecution()
r.start()
try:
    time.sleep(3)
    nodes = [n for n in r.remote_nodes if n.get('project_name') == 'MeridianSquad']
    assert len(nodes) == 1, nodes
    r.open_command_connection(nodes[0]['node_id'])
    result = r.run_command("exec(open('D:/devgames/MeridianSquad/Scripts/EnvironmentDestruction01/ed01_bootstrap.py').read())", unattended=True)
    print(json.dumps(result))
    assert result['success']
finally:
    r.stop()
