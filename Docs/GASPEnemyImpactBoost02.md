# Stronger local rifle impact accent

Date: 2026-09-22. Direct outside-task follow-up to
[ImpactBoost01](GASPEnemyImpactBoost01.md), under the
[owner's stronger-reaction request](Approvals/GASPEnemyImpactBoost02-OwnerScope01.json).

The next owner-test defaults are fall multiplier **4** and lethal multiplier
**6**, replacing 1.5 and 2. Metadata and runtime multiplier bounds now allow up
to 6. The impulse still targets the struck physical body and contact point.
The existing mass-limited base impulse is multiplied after its base cap:
the fall accent adds three ordinary impulses to the original one, once a
recent hit is followed by committed falling; a lethal hit applies six once.
The same shot never receives both accents. Ordinary hits, damage, corpse hits,
the 0.5 game-second attribution window and reset behavior are unchanged.

This is a strength adjustment, with no joint, animation or recovery-controller
changes. The owner evaluates the actual visible motion; stronger displacement
is an intended effect, not a verified gameplay result. No firing or gameplay
tests were run, in accordance with the continuing build-only instruction.
UE 5.8.1 Development Editor build passes: 13 actions, exit code 0.
Logs and preservation hashes are in
`Saved/CombatSlice01/GASPEnemyFoundation01/ImpactBoost02/`.
