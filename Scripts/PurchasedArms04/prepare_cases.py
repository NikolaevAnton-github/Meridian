"""Only sprint-jump behavior and its directly affected transitions."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / 'Saved/PurchasedArms04/Worker'


def tap(t, key):
    return [[t, key, 1], [t + .1, key, 0]]


def case(name, duration, events):
    return {'name': name, 'duration': duration, 'events': sorted(events, key=lambda e: e[0])}


def main():
    cases = [
        case('Jump01-Ordinary', 3.6, [[.1, 'W', 1], [2.8, 'W', 0]] + tap(1, 'SpaceBar')),
        case('Jump01-ShiftHeld', 3.6, [[.1, 'W', 1], [.1, 'LeftShift', 1],
             [2.8, 'W', 0], [3, 'LeftShift', 0]] + tap(1, 'SpaceBar')),
        case('Jump01-ShiftReleased', 5.4, [[.1, 'W', 1], [.1, 'LeftShift', 1],
             [1.22, 'LeftShift', 0], [4.8, 'W', 0]] + tap(1, 'SpaceBar') + tap(1.4, 'SpaceBar') + tap(3, 'SpaceBar')),
        case('Jump01-StationaryShift', 3.1, [[.1, 'LeftShift', 1], [2.5, 'LeftShift', 0]] + tap(1, 'SpaceBar')),
        case('Jump01-Alt', 3.6, [[.1, 'W', 1], [.1, 'LeftAlt', 1],
             [2.8, 'W', 0], [3, 'LeftAlt', 0]] + tap(1, 'SpaceBar')),
        case('Jump01-CrouchGate', 2.5, tap(.1, 'C') + tap(1, 'SpaceBar') + tap(1.6, 'C')),
        case('Jump01-BusyGate', 4.8, tap(.1, 'R') + tap(.7, 'SpaceBar')),
    ]
    path = OUT / 'jump-cases.json'
    assert not path.exists()
    path.write_text(json.dumps(cases, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
