"""Layout03 real-input route; saved blocking faces retain 3 cm contact tolerance."""
from pathlib import Path
import json

def configuration(root):
    out = Path(root)/'Saved/OpeningLobby/Layout03'
    bounds = json.loads((out/'construction.json').read_text())['blocking_bounds']
    surfaces = {name:bounds[actor]['center'][1]-bounds[actor]['extent'][1]
                for name,actor in [('wall_collision','SideWall_1'),('column_collision','Pier_3_1')]}
    plan = [
        ('wait','spawn',1), ('mouse','mouse_yaw',30,0),('mouse','mouse_pitch',0,20),('look','restore_look',0,0),
        ('move','checkpoint_inbound',-2300,-105),('move','checkpoint_bypass',-2300,-300),('move','entrance_center',-2700,-300),
        ('move','longitudinal_start',-2850,-300),('move','longitudinal_end',2850,-300),
        ('move','inner_door',2850,0),('move','inner_crossover',2700,0),
        ('move','west_aisle_entry',2700,-1000),('move','west_complete_return',-2700,-1000),
        ('move','entrance_crossover',-2700,1000),('move','east_complete_inbound',2700,1000),
        ('hold','wall_collision','D',2),('move','leave_wall',2700,1000),
        ('move','east_complete_return',-2700,1000),('move','entrance_cross_to_detector',-2700,-105),
        ('move','checkpoint_second_inbound',-2300,-105),('move','checkpoint_outbound',-2700,-105),
        ('move','checkpoint_final_inbound',-2300,-105),('move','column_approach',420,0),
        ('hold','column_collision','D',3),('move','leave_column',420,0),('jump','gravity_jump',1.8),
        ('move','return_checkpoint_approach',-2300,-105),('move','return_to_entrance',-2850,-105),
    ]
    return dict(map='/Game/Maps/L_OpeningLobby_Layout03',out=out,plan=plan,view_plan=plan,
                collision_surfaces=surfaces,contact_tolerance_cm=3.,refresh_held_input=True)
