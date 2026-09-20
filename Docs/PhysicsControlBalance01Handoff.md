# MSQ-87 owner-test handoff

Candidate05 is handed off on 2026-09-20 under the owner's
[task-specific review waiver](Approvals/PhysicsControlBalance01-OwnerTesting01.json).
The controller cancelled independent review run
`01a0bf6b-903f-758b-8786-f5f69769d742`; no independent verdict is claimed.
The owner will test the experiment. This is not final play or motion acceptance.

The completed Multica Unreal run `01a0bf36-36f0-739d-912e-197eb85f6ae8`
used native Astra/max/default with fast mode disabled. Existing executor and
reviewer profiles were not modified. One production writer implemented the change.

The [preserved executor report](PhysicsControlBalance01.md) records behavior,
tuning, assistance and limits. Its Candidate05 manifest remains immutable.
`build07.log` succeeds and `self-checks02.json` records 38 passing focused checks.
Applicable Candidate03 gameplay and Candidate04 visual evidence is retained;
later changes affect joint diagnostics only. The initial failed joint-gap check,
its diagnosis and the corrected evidence remain separately preserved.

The scoped evidence covers moderate recovery, accumulated living falls, both-leg
support loss, external disturbance, back/stomach get-up, interruption, terminal
death, blocked/unsupported recovery, F6 and one retained slowdown transition.
Six numbered fixtures render. No per-profile comparison or broad feature matrix
was added. Controller acceptance checks scope, candidate identity, evidence
applicability and preservation; it does not replace the waived independent review.

Use `/Game/Maps/L_OpeningLobby_PainterStone01` and Play. LMB/RMB/R retain firing,
aiming and reload; F6 resets without ammunition refill; F10 toggles the six
fixtures; Y retains 0.25 world/body/bullet and 0.65 player movement/firing rates.
The executor's handoff leaves the editor idle on that map with clean packages
and no transient probe actors. Any later owner session is left untouched.

Standing and get-up remain assisted by pose springs, with possible foot sliding.
Support uses static-floor proximity and temporary leg availability, not a dynamic
balance solver. Recovery clearance is bounded and does not plan a whole-body path
around obstacles. The full original 8.333/8.600-second Mixamo motions are retained.

Owner configuration, descriptor, retained map and original FBX fingerprints are
preserved. The new Unreal sources/rigs/animations are inventoried as experimental
assets in `PhysicsControlBalance01`; declared derivation is not independent art
acceptance. Existing Git LFS rules cover their binary files. Generated recordings,
logs and native build output remain under `Saved/` or ignored build directories.
MSQ-70 and other successors remain undispatched.

Evidence: `Saved/CombatSlice01/PhysicsControlBalance01/Worker/` and `Controller/`.
The controller closes the implementation as an owner-test handoff and creates the
local task-scoped commit before delivery, preserving unrelated owner edits.
