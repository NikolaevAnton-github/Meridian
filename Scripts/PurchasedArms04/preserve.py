"""Preserve MSQ-64 starting bytes with the existing project preservation utility."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'PurchasedArms01'))
import preserve as previous

previous.OUT = previous.ROOT / 'Saved/PurchasedArms04/Worker'

if __name__ == '__main__':
    {'baseline': previous.baseline, 'verify': previous.verify,
     'storage': lambda: print(previous.storage())}[sys.argv[1]]()
