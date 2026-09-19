import sys
from pathlib import Path
for folder in ['OpeningLobby', 'PurchasedArms02', 'CombatFoundation01', 'EnemyPrototype01']:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / folder))
import tools68
import tools69
