# MSQ-120 direct combat-speed follow-up

2026-09-24. The [owner instruction](Approvals/CombatAI01-CombatSpeed01-OwnerScope01.json)
authorizes this small direct correction without a new task or reviewer.

Enabled opponents now use **360 cm/s** for ordinary standing combat movement,
matching the protagonist, instead of the imported 165 cm/s walking value.
`CombatMovement::BaseSpeed` supplies both characters and the mobile-fire envelope.
The native input producer sets the individual Mover walking mode's `WalkSpeed`
before the existing GASP gait selector runs. Disabling combat restores the
authored default for manual fixtures. No binary asset edit is required.

Mobile fire supports this new speed with 1 cm/s numerical tolerance. Moving
spread reaches its existing 1.6-degree maximum at 360 cm/s. Grounding, gait,
vertical velocity, sight, pose and muzzle gates remain. Running, crouched
movement, acceleration and the established slowdown ratios retain their tuning.
The earlier Candidate01/build03 220 cm/s fire envelope is historical.

Development Editor build succeeds. Focused inspection confirms the live
Blueprint's standing-walk selector feeds `WalkSpeed` into `MaxSpeedOverride`,
while crouch uses its separate value. Source inspection confirms the override
precedes GASP input production and all mobile-fire consumers use `FireMotion`.
Scoped diff checks pass. Evidence: `Saved/CombatAI01/CombatSpeed01/`.
Gameplay and motion feel remain for owner testing; no agent Play or firing ran.

Owner config/project/map and imported movement asset hashes are preserved.
Historical candidate manifests are unchanged. The matching native editor is
reopened on the retained lobby for the owner's next Play session.
