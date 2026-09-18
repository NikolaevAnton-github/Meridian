"""Run short input cases through the existing foreground verification driver."""
import json
import importlib.util
import sys
from pathlib import Path
from client04 import work

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/PurchasedArms04/Worker'
spec = importlib.util.spec_from_file_location('run_cases02', ROOT / 'Scripts/PurchasedArms02/run_cases.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
previous.work = work
previous.OUT = OUT

if __name__ == '__main__':
    for case in json.loads((OUT / sys.argv[1]).read_text()):
        previous.run(case)
