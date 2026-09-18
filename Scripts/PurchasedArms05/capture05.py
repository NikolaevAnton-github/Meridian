"""Reuse the existing foreground H.264 capture and already installed packages."""
import sys
import faulthandler
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Saved/PurchasedArms04/Worker/PythonPackages'))
sys.path.insert(0, str(ROOT / 'Scripts/PurchasedArms02'))
import capture02

if __name__ == '__main__':
    output = ROOT / 'Saved/PurchasedArms05/Worker/Video'
    output.mkdir(parents=True, exist_ok=True)
    with (output / (sys.argv[2] + '.capture.log')).open('w', encoding='utf-8') as log:
        faulthandler.enable(log)
        try:
            capture02.main(output)
        except Exception:
            traceback.print_exc(file=log)
            raise
