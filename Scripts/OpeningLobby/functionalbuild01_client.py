"""Task-local official Epic MCP client, following the existing probe protocol."""
import json
import sys
from urllib.request import Request, build_opener, ProxyHandler

def call(name, arguments):
    opener=build_opener(ProxyHandler({}))
    headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
    seq=0
    def rpc(method,params=None,notification=False):
        nonlocal seq
        seq+=1; msg={'jsonrpc':'2.0','method':method}
        if not notification:msg['id']=seq
        if params is not None:msg['params']=params
        with opener.open(Request('http://127.0.0.1:8000/mcp',data=json.dumps(msg).encode(),headers=headers,method='POST'),timeout=180) as response:
            if method=='initialize':headers['Mcp-Session-Id']=response.headers['Mcp-Session-Id']
            raw=response.read()
        if notification:return
        result=json.loads(raw)
        if result.get('error'):raise RuntimeError(result['error'])
        result=result['result']
        if result.get('isError'):raise RuntimeError(result)
        return result
    init=rpc('initialize',{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'FunctionalBuild01','version':'1'}})
    headers['Mcp-Protocol-Version']=init['protocolVersion'];rpc('notifications/initialized',notification=True)
    try:return rpc('tools/call',{'name':name,'arguments':arguments})
    finally:
        try:opener.open(Request('http://127.0.0.1:8000/mcp',headers=headers,method='DELETE'),timeout=5).close()
        except Exception:pass

if __name__=='__main__':
    if sys.argv[1] in ['start_pie','stop_pie']:
        args={'options':{'bSimulate':False,'playMode':'PlayMode_InEditorFloating','warmupSeconds':2}} if sys.argv[1]=='start_pie' else {}
        result=call('call_tool',{'toolset_name':'EditorToolset.EditorAppToolset','tool_name':'StartPIE' if sys.argv[1]=='start_pie' else 'StopPIE','arguments':args})
    elif sys.argv[1] in ['list_toolsets','describe_toolset']:
        args={} if len(sys.argv)<3 else {'toolset_name':sys.argv[2]}
        result=call(sys.argv[1],args)
    elif sys.argv[1]=='work':
        result=call('call_tool',{'toolset_name':'Game.Scripts.OpeningLobby.functionalbuild01_tools.OpeningLobbyFunctionalBuild01Tools','tool_name':'action','arguments':{'operation':sys.argv[2],'argument':sys.argv[3] if len(sys.argv)>3 else ''}})
    else:
        args=json.loads(sys.argv[3]) if len(sys.argv)>3 else {}
        result=call('call_tool',{'toolset_name':sys.argv[1],'tool_name':sys.argv[2],'arguments':args})
    try:
        value=json.loads(result['content'][0]['text'])
        value=value.get('returnValue',value)
        if isinstance(value,str):value=json.loads(value)
        print(json.dumps(value))
    except (ValueError,KeyError,AttributeError):print(json.dumps(result))
