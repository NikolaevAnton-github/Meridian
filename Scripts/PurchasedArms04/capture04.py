"""Use the existing ordinary-speed capture with MSQ-64 output isolation."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/PurchasedArms04/Worker'
sys.path.insert(0, str(OUT / 'PythonPackages'))
sys.path.insert(0, str(ROOT / 'Scripts/PurchasedArms02'))
import capture02

if __name__ == '__main__':
    capture02.main(OUT / 'Video')
