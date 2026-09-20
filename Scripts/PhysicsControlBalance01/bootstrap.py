import sys
from pathlib import Path
for folder in ['OpeningLobby', 'PurchasedArms02', 'CombatFoundation01', 'PhysicsControlDummy01', 'PhysicsControlVariants01', 'PhysicsControlBalance01']:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / folder))
import tools87
