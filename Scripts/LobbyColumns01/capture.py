"""Save the verified Epic MCP viewport capture without using the Rider screenshot path."""
import base64
import json
from pathlib import Path
from urllib.request import Request, build_opener, ProxyHandler

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/LobbyColumns01'
endpoint='http://127.0.0.1:8000/mcp'
opener=build_opener(ProxyHandler({}))
headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
counter=0
def rpc(method,params,notification=False):
    global counter
    counter+=1
    payload=dict(jsonrpc='2.0',method=method,params=params)
    if not notification: payload['id']=counter
    with opener.open(Request(endpoint,data=json.dumps(payload).encode(),headers=headers),timeout=30) as response:
        if method=='initialize': headers['Mcp-Session-Id']=response.headers['Mcp-Session-Id']
        raw=response.read()
    if notification: return
    message=json.loads(raw)
    assert 'error' not in message,message
    return message['result']
try:
    r=rpc('initialize',dict(protocolVersion='2025-11-25',capabilities={},clientInfo=dict(name='LobbyColumns01Capture',version='1')))
    headers['Mcp-Protocol-Version']=r['protocolVersion']
    rpc('notifications/initialized',{},True)
    result=rpc('tools/call',dict(name='call_tool',arguments=dict(toolset_name='EditorToolset.EditorAppToolset',tool_name='CaptureViewport',arguments=dict(
        captureTransform=dict(location=dict(x=-698.085581,y=94.637687,z=172.150004),rotation=dict(pitch=-13.48675,yaw=14.290327,roll=0),scale=dict(x=1,y=1,z=1)),
        annotations=dict(gridSpacing=0,gridExtent=0,gridHeight=0,maxLabelDistance=0,classFilter=dict(refPath='/Script/Engine.Actor'),maxLabels=0),bShowUI=False))))
    image=json.loads(result['content'][0]['text'])['returnValue']['image']
    (OUT/'editor-final.png').write_bytes(base64.b64decode(image['data']))
    print(str(OUT/'editor-final.png'))
finally:
    if 'Mcp-Session-Id' in headers:
        with opener.open(Request(endpoint,headers=headers,method='DELETE'),timeout=5): pass
