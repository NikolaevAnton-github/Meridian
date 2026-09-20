import sys
from pathlib import Path
import unreal
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
for folder in ['OpeningLobby', 'PurchasedArms02', 'CombatFoundation01', 'PhysicsControlDummy01', 'PhysicsControlVariants01', 'PhysicsControlBalance01', 'PhysicsControlStepping01', 'PhysicsControlLegPose01', 'PhysicsControlRecoverability01']:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / folder))
import tools97
