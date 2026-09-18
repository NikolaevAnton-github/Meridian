"""Short task cases over the existing uninterrupted video/input driver."""
import json
import sys
from pathlib import Path
from client05 import work
import video_cases

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/PurchasedArms05/Worker'
video_cases.work = work
video_cases.OUT = OUT

if __name__ == '__main__':
    cases = json.loads((OUT / sys.argv[1]).read_text())
    for case in cases:
        video_cases.run(case, int(sys.argv[2]), ROOT / 'Scripts/PurchasedArms05/capture05.py')
