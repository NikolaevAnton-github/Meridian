"""Register only; state/inspection/close use the official Epic MCP toolset."""
import sys, time, json
sys.path.insert(0,'D:/UE_5.8/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python')
import remote_execution
r=remote_execution.RemoteExecution(); r.start()
try:
    time.sleep(5)
    nodes=[n for n in r.remote_nodes if n.get('project_name')=='MeridianSquad']
    assert len(nodes)==1, [(n.get('project_name'),n.get('node_id')) for n in r.remote_nodes]
    r.open_command_connection(nodes[0]['node_id'])
    result=r.run_command("exec(open('D:/devgames/MeridianSquad/Scripts/CombatAI01/CAIT03/bootstrap.py').read())",unattended=True)
    print(json.dumps(result)); assert result['success']
finally: r.stop()
