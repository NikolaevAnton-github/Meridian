"""Capture the actual PIE window with WGC, preserving ordinary wall-clock timing.

Task-local backend for the retained runner: desktop capture twice lost focus.
No editor/world pause, no time resampling, and no hidden source animation render.
"""
import ctypes
import json
import sys
import time
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Saved/PurchasedArms04/Worker/PythonPackages'))
sys.path.insert(0,str(ROOT/'Saved/CombatSlice01/PhysicsControlBalance01/Worker/PythonPackages'))
sys.path.insert(0,str(ROOT/'Scripts/PurchasedArms02'))
import av
from windows_capture import WindowsCapture
from capture02 import window_for_pid

pid,name,duration=int(sys.argv[1]),sys.argv[2],float(sys.argv[3])
out=Path(sys.argv[4]); out.mkdir(parents=True,exist_ok=True)
path=out/(name+'.mp4'); assert not path.exists()
ctypes.windll.user32.SetProcessDPIAware()
hwnd,title=window_for_pid(pid)
assert 'Preview' in title,title
capture=WindowsCapture(cursor_capture=False,draw_border=False,monitor_index=None,window_name=title)
container=av.open(str(path),'w')
stream=None
start=None
last=-1
records=[]

@capture.event
def on_frame_arrived(frame,control):
    global stream,start,last
    now=time.monotonic()
    if start is None:
        start=now
        stream=container.add_stream('libx264',rate=30)
        scale=min(1280/frame.width,900/frame.height,1)
        stream.width=int(frame.width*scale)//2*2
        stream.height=int(frame.height*scale)//2*2
        stream.pix_fmt='yuv420p'
        stream.time_base=Fraction(1,1000)
        stream.options={'crf':'20','preset':'ultrafast'}
        (out/(name+'.ready.json')).write_text(json.dumps(dict(wall=start,hwnd=hwnd,title=title,backend='Windows Graphics Capture')))
    elapsed=now-start
    if elapsed>=duration:
        control.stop(); return
    if elapsed-last<1/30: return
    last=elapsed
    vf=av.VideoFrame.from_ndarray(frame.frame_buffer,format='bgra').reformat(stream.width,stream.height,format='yuv420p')
    vf.pts=round(elapsed*1000); vf.time_base=Fraction(1,1000)
    for packet in stream.encode(vf): container.mux(packet)
    records.append(dict(t=elapsed,source_timespan=frame.timespan))

@capture.event
def on_closed():
    pass

try:
    capture.start()
finally:
    if stream:
        for packet in stream.encode(): container.mux(packet)
    container.close()
    (out/(name+'.capture.json')).write_text(json.dumps(dict(backend='WGC',title=title,frames=records),separators=(',',':')))
assert records and records[-1]['t']>=duration-.5,'Window capture ended early'
print(path)
