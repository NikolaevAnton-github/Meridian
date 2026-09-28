"""Exercise borrowing first, then retention on each later-shot face."""

def distribution_events():
    # The stock loadout contains 120 rounds; explicitly provision this 150-shot probe.
    events = [[0, 'ammo', 30, 150], [.1, 'position', [750, 0, 90.15]]]
    positions = [[750, 0, 90.15], [0, 750, 90.15], [-750, 0, 90.15], [0, -750, 90.15]]
    clock = 2.
    # Two magazines on the first face build a large borrowed pile before
    # moving around the column. Later faces must reclaim places without reset.
    for phase, face in enumerate([0, 0, 1, 2, 3]):
        events += [[clock-1, 'position', positions[face]], [clock-.8, 'reload']]
        clock += 5
        for i in range(30):
            row = i // 3
            offset = [-62, 0, 62][row % 3]
            # Separate the second magazine's fracture sites from the first.
            z = 110 + 165*row + (75 if phase == 1 else 0)
            target = ([119.1, offset, z] if face == 0 else [offset, 119.1, z] if face == 1
                      else [-119.1, offset, z] if face == 2 else [offset, -119.1, z])
            t = clock + i*1.2
            events += [[t, 'aim', target], [t+.2, 'fire', True], [t+.6, 'fire', False]]
        clock += 51
        events.append([clock-1, 'sample', 'sector-'+str(face)+'-phase-'+str(phase)])
    events += [[clock, 'position', [850, 400, 90.15]], [clock+1, 'aim', [220, 0, 35]],
               [clock+2, 'capture', 'balanced-pile'], [clock+3, 'sample', 'settled-cap'],
               [clock+5, 'key', 'F6', True], [clock+5.5, 'key', 'F6', False],
               [clock+7, 'sample', 'final-fresh']]
    return sorted(events, key=lambda e: e[0]), clock+9


def fourth_face_events():
    events = [[0, 'ammo', 30, 90], [.1, 'position', [0, -750, 90.15]]]
    for i in range(30):
        row = i//3
        t = 10+i*1.2
        events += [[t, 'aim', [[-62,0,62][row%3], -119.1, 110+165*row]],
                   [t+.2, 'fire', True], [t+.6, 'fire', False]]
    events += [[59, 'sample', 'fourth-face-settled'], [60, 'aim', [0,-220,35]],
               [61, 'capture', 'fourth-face-pile'], [64, 'key', 'F6', True],
               [64.5, 'key', 'F6', False], [66, 'sample', 'final-fresh']]
    return events, 68
