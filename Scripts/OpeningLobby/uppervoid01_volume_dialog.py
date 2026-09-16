"""Read-only native window enumeration for an editor reload modal."""
import ctypes,json
from ctypes import wintypes as w
u=ctypes.windll.user32
rows=[]
@ctypes.WINFUNCTYPE(w.BOOL,w.HWND,w.LPARAM)
def visit(hwnd,param):
    pid=w.DWORD();u.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
    if pid.value==28512 and u.IsWindowVisible(hwnd):
        title=ctypes.create_unicode_buffer(2048);u.GetWindowTextW(hwnd,title,2048)
        rect=w.RECT();u.GetWindowRect(hwnd,ctypes.byref(rect))
        rows.append(dict(hwnd=hwnd,title=title.value,rect=[rect.left,rect.top,rect.right,rect.bottom]))
    return True
u.EnumWindows(visit,0);print(json.dumps(rows))
import sys
if '--confirm-reviewed-reload' in sys.argv:
    modal=[r for r in rows if r['title']=='Message'];assert len(modal)==1
    assert modal[0]['hwnd']==1050676
    # Inspected native dialog names only our recompiled extinction material.
    # Enter activates its visible default Yes button, without global input/focus.
    u.PostMessageW(w.HWND(modal[0]['hwnd']),0x0100,13,0)
    u.PostMessageW(w.HWND(modal[0]['hwnd']),0x0101,13,0)
