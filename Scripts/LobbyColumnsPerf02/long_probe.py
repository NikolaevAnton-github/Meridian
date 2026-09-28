"""Matched long captures; 22-second static windows and a 30-second fire window."""
from pathlib import Path
ns={};exec(Path('D:/devgames/MeridianSquad/Scripts/LobbyColumnsPerf02/probe.py').read_text(),ns)
def run(name):
    e=[]
    def event(t,op,*args):e.append((t,op,args))
    event(0,'view');event(1,'sample','initial')
    event(3,'csv','intact');event(25,'stop');event(26,'sample','intact')
    event(29,'csv','firing')
    for j,x in enumerate([-2100,-420,420]):
        t=30+8*j
        event(t,'position',[x,-160,90.15]);event(t+.1,'ammo')
        for k in range(6):
            event(t+.2+1.25*k,'aim',[x-35,-560,22 if k<3 else 810])
            event(t+.45+1.25*k,'fire',True);event(t+.75+1.25*k,'fire',False)
        event(t+7.6,'sample','damaged-'+str(j))
    event(59,'stop');event(60,'view')
    event(74,'sample','settled-before');event(75,'csv','settled')
    event(97,'stop');event(98,'sample','settled')
    event(99,'key','F6',True);event(99.2,'key','F6',False)
    event(102,'csv','reset');event(124,'stop');event(125,'sample','reset')
    event(126,'view',True);event(129,'csv','reverse')
    event(151,'stop');event(152,'sample','reverse');event(153,'view')
    return ns['timeline'](name,e,154,18)
