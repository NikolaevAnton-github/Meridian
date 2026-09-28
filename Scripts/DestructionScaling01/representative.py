"""One repeatable lobby sample, not the stopped DS-01 benchmark fixture."""
import sys
from pathlib import Path
import unreal as u

ROOT = Path('D:/devgames/MeridianSquad')
sys.path.insert(0, str(ROOT/'Scripts/LobbyColumnsPerf02'))
import probe
import capture_settings

def run(name):
    probe.OUT = ROOT/'Saved/DestructionScaling01'
    capture_settings.OUT = probe.OUT
    probe.setup(2)
    capture_settings.prepare(name)
    e = [(0, 'position', ([-420,-160,90.15],)), (.1,'ammo',()),
         (.2,'aim',([-455,-560,410],)), (3,'sample',('intact',)),
         (5,'csv',('intact',)), (11,'stop',()), (34,'csv',('moving',)),
         (40,'stop',()), (42,'sample',('damaged',)), (50,'csv',('settled',)),
         (56,'stop',()), (57,'sample',('settled',))]
    for i in range(18):
        t = 12 + i * 1.1
        target = [-455 + 35*((i//3)%2), -560, 210 + 100*(i//6)]
        e.extend([(t,'aim',(target,)), (t+.25,'fire',(True,)), (t+.55,'fire',(False,))])
    probe.timeline(name, e, 58, expected_shots=18)
