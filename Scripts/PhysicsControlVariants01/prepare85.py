"""Immutable before-state using the retained preservation inventory."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlVariants01/Worker'
sys.path.insert(0, str(ROOT / 'Scripts/PhysicsControlDummy01'))
import preserve84
preserve84.OUT = OUT
preserve84.run()
rows = []
for root in ['Saved/CombatSlice01/PhysicsControlDummy01', 'Assets/Source/EnemyPrototype01', 'Source/MeridianSquad', 'Scripts/PhysicsControlDummy01']:
    for p in (ROOT / root).rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:
            rows.append(dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=preserve84.sha(p)))
(OUT / 'history-before.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
contract = {
    'candidate': 'Initial contract before implementation and verification',
    'reaction_metric': 'Maximum spine_03 COM displacement relative to pelvis from the pre-hit settled pose, first 1.5 world seconds; also quaternion angular excursion, ordinary-speed video and peak body speed.',
    'reaction_tolerances': {'minimum_profile1_cm': 3, 'adjacent_minimum_ratio': 1.15, 'adjacent_minimum_cm': 1.0, 'recovery_seconds': 4, 'recovered_spine_distance_cm': 2, 'quiet_body_speed_cm_s': 12, 'idle_drift_cm': 1, 'joint_length_change_cm': 3},
    'reaction_rationale': 'At least a 3 cm local motion exceeds the former 1 cm acceptance; adjacent profiles must gain both 15% and 1 cm to exceed ordinary numerical/view noise. All six require visual inspection; metrics alone cannot pass the row.',
    'clock_tolerances': {'cadence_action_seconds': 0.085, 'cadence_error_seconds': 0.00001, 'actual_movement_ratio_relative_error': 0.03, 'actual_bullet_ratio_relative_error': 0.03, 'actual_montage_rate_relative_error': 0.04, 'normal_player_rate': 1, 'preview_player_rate': 0.65, 'preview_world_rate': 0.25},
    'count_requirements': {'enabled_dummies': 6, 'disabled_dummies': 0, 'legacy_enemy': 0, 'managers': 1, 'health': 100, 'damage': 25},
    'preserve': 'All prior assets, owner config/map/descriptor and historical candidates. Grounded collapse correspondence remains an MSQ-84 limitation, not reclassified.',
    'review': 'Executor self-check only. Sole independent primary reviewer belongs to controller.'
}
(OUT / 'contract-before-verification01.json').write_text(json.dumps(contract, indent=2), encoding='utf-8')
