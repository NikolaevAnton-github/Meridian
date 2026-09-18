"""Use the retained ordinary-speed foreground capture, with task-scoped output."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Saved/PurchasedArms04/Worker/PythonPackages'))
sys.path.insert(0, str(ROOT / 'Scripts/PurchasedArms02'))
import capture02
capture02.main(Path(sys.argv[4]) if len(sys.argv) > 4 else ROOT / 'Saved/CombatSlice01/CombatFoundation01/Worker/Video')
