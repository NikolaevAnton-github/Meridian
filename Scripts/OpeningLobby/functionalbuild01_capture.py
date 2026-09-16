"""Scoped reuse of native ReworkA01 PIE still capture and settings restoration."""
import types
from functionalbuild01_data import ROOT,D

source=(ROOT/'Scripts/OpeningLobby/reworka01_capture.py').read_text()
source=source.replace('from reworka01_data import OUT,MAP,D','from functionalbuild01_data import OUT,MAP,D')
source=source.replace('from reworka01_unreal import guard','from functionalbuild01_unreal import guard')
source=source.replace('L_OpeningLobby_ArchitectureReworkA01','L_OpeningLobby_FunctionalBuild01')
_capture=types.ModuleType('functionalbuild01_existing_capture')
exec(compile(source,str(ROOT/'Scripts/OpeningLobby/reworka01_capture.py'),'exec'),_capture.__dict__)
_capture.VIEWS={name+'-90':(c['xyz'][0]*100,c['xyz'][1]*100,c['yaw'],c['pitch']) for name,c in D['drawing_cameras'].items()}
_capture.VIEWS.update({
    'aisle-negative-90':(-1000,-1000,180,13),
    'inner-door-positive-90':(2610,80,90,5),
    'inner-door-negative-90':(2610,-80,-90,5),
    'elevator-detail-90':(2500,0,0,6),
    'checkpoint-context-90':(-1900,0,180,5),
    'room-junction-90':(-1670,400,150,30),
    'column-contact-90':(-2100,0,0,45),
    'C1-90':(-1900,0,0,0),'C2-90':(1900,0,180,0)})
prepare=_capture.prepare
camera=_capture.camera
shoot=_capture.shoot
restore=_capture.restore
