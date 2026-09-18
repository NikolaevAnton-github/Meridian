"""Reuse immutable baseline and storage checks without copying asset packages."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'PurchasedArms01'))
import preserve as previous
previous.OUT = previous.ROOT / 'Saved/PurchasedArms05/Worker'


def verify_final():
    write = previous.write
    def revision_write(path, value):
        destination = previous.OUT / 'Correction02' / path.name
        assert not destination.exists(), destination
        write(destination, value)
    previous.write = revision_write
    previous.verify()

if __name__ == '__main__':
    {'baseline': previous.baseline, 'verify': previous.verify, 'verify_final': verify_final,
     'storage': lambda: print(previous.storage())}[sys.argv[1]]()
