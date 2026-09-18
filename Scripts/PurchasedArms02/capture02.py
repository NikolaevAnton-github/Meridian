"""Capture ordinary-speed editor gameplay externally, without pausing Unreal."""
import ctypes
import json
import sys
import time
from fractions import Fraction
from ctypes import wintypes
from pathlib import Path
from PIL import ImageGrab
import av

def window_for_pid(pid):
    candidates = []
    user = ctypes.windll.user32
    @ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)
    def visit(hwnd,unused):
        owner = ctypes.c_ulong()
        user.GetWindowThreadProcessId(hwnd,ctypes.byref(owner))
        if owner.value == pid and user.IsWindowVisible(hwnd):
            length = user.GetWindowTextLengthW(hwnd)
            if length:
                name = ctypes.create_unicode_buffer(length+1)
                user.GetWindowTextW(hwnd,name,length+1)
                candidates.append((hwnd,name.value))
        return True
    user.EnumWindows(visit,0)
    assert candidates, pid
    return next((c for c in candidates if 'MeridianSquad' in c[1]),candidates[0])

def capture(hwnd):
    # GPU Slate windows do not paint their swapchain through PrintWindow.
    rect = wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(ctypes.c_void_p(hwnd),ctypes.byref(rect))
    return ImageGrab.grab(bbox=(rect.left,rect.top,rect.right,rect.bottom),all_screens=True)

def main(output_root=None):
    ctypes.windll.user32.SetProcessDPIAware()
    pid,name,duration = int(sys.argv[1]),sys.argv[2],float(sys.argv[3])
    root = Path(output_root) if output_root else Path(__file__).resolve().parents[2] / 'Saved/PurchasedArms02/Worker/Video'
    root.mkdir(parents=True,exist_ok=True)
    path = root / (name+'.mp4')
    assert not path.exists()
    hwnd,title = window_for_pid(pid)
    user = ctypes.windll.user32
    user.GetForegroundWindow.restype = ctypes.c_void_p
    user.SetForegroundWindow.argtypes = [ctypes.c_void_p]
    user.ShowWindow.argtypes = [ctypes.c_void_p,ctypes.c_int]
    previous = user.GetForegroundWindow()
    user.ShowWindow(hwnd,9)
    user.keybd_event(0x12,0,0,0)
    user.SetForegroundWindow(hwnd)
    user.keybd_event(0x12,0,2,0)
    time.sleep(.3)
    assert user.GetForegroundWindow() == hwnd, 'Unreal must be foreground to avoid capturing overlapping windows.'
    initial = capture(hwnd)
    initial.thumbnail((1280,900))
    width,height = initial.width//2*2,initial.height//2*2
    with av.open(str(path),'w') as output:
        stream = output.add_stream('libx264',rate=30)
        stream.width,stream.height = width,height
        stream.pix_fmt = 'yuv420p'
        stream.time_base = Fraction(1,1000)
        stream.options = {'crf':'20','preset':'ultrafast'}
        start = time.monotonic()
        (root/(name+'.ready.json')).write_text(json.dumps({'wall':start,'hwnd':hwnd,'title':title}))
        records = []
        index = 0
        next_frame = start
        milestones = iter([0,2,4,5,6,7,8,10,12])
        milestone = next(milestones,None)
        while time.monotonic()-start < duration:
            wait = next_frame-time.monotonic()
            if wait>0: time.sleep(wait)
            stamp = time.monotonic()
            assert user.GetForegroundWindow() == hwnd, 'Capture lost foreground.'
            frame = capture(hwnd).resize((width,height))
            if milestone is not None and stamp-start >= milestone:
                frame.save(root/(name+f'-{index:04d}.png'))
                milestone = next(milestones,None)
            video = av.VideoFrame.from_image(frame)
            video.pts = round((stamp-start)*1000)
            video.time_base = Fraction(1,1000)
            for packet in stream.encode(video): output.mux(packet)
            records.append({'frame':index,'wall':stamp,'elapsed':stamp-start})
            index += 1
            next_frame = max(next_frame+1/30,time.monotonic())
        for packet in stream.encode(): output.mux(packet)
    (root/(name+'.json')).write_text(json.dumps({'pid':pid,'hwnd':hwnd,'title':title,'width':width,'height':height,
        'method':'Verified foreground screen-region capture / PyAV H.264; real-time PTS; no Unreal screenshot or pause command','frames':records},indent=2))
    user.SetForegroundWindow(previous)
    print(str(path))

if __name__=='__main__': main()
