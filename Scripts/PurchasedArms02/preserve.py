"""MSQ-62 preservation reuses the immutable MSQ-61 baseline implementation."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'PurchasedArms01'))
import preserve as previous
previous.OUT = previous.ROOT / 'Saved/PurchasedArms02/Worker'
if __name__ == '__main__':
    if sys.argv[1] == 'baseline':
        previous.baseline()
    elif sys.argv[1] == 'verify':
        previous.verify()
    elif sys.argv[1] == 'storage':
        print(previous.storage())
