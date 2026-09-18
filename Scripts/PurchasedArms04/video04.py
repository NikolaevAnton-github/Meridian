"""Collect the three required jump/recovery views with the existing video driver."""
import json
import sys
from pathlib import Path
from client04 import work
import video_cases

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/PurchasedArms04/Worker'
video_cases.work = work
video_cases.OUT = OUT

if __name__ == '__main__':
    cases = json.loads((OUT / 'jump-cases.json').read_text())
    correction = len(sys.argv) > 2 and sys.argv[2] == 'correction01'
    for case in ([cases[i] for i in [0, 1, 2, 4]] if correction else cases[:3]):
        case['name'] = case['name'].replace('Jump01-', 'Correction01-' if correction else 'Views01-')
        video_cases.run(case, int(sys.argv[1]), ROOT / 'Scripts/PurchasedArms04/capture04.py')
