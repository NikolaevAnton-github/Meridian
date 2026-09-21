# MSQ-98 Candidate01 controller handoff

All three active enemy fixtures now use the migrated GASP
`SandboxCharacter_Mover_Ragdoll` foundation. The final Development Editor build
and the task's six focused executor criteria pass, with recorded limits.
Independent review is waived for this execution. Controller scope/evidence
acceptance and owner motion/play judgment remain separate.

The full implementation, ownership table, criterion-to-evidence mapping, controls
and reuse rationale are in [GASPEnemyFoundation01.md](GASPEnemyFoundation01.md).
Evidence root: `Saved/CombatSlice01/GASPEnemyFoundation01/Worker/`.

## Candidate and verification

- `Candidate01/manifest.json` freezes all production paths, binary/package hashes,
  compiled module, selected evidence and the Git baseline. Do not replace its hashes.
- `Candidate01/implementation.zip` preserves code, task scripts, configuration,
  compiled module and the five authored/new packages. Unchanged migrated packages
  are fingerprinted in place; their Git/LFS closure belongs to the controller.
- `build10.log`: UE 5.8.1 CL 56057345, Development Editor, succeeded in 14.04 s.
- `final-analysis02.json`: 13 applicable case summaries. Final01/02/03 use build10;
  narrower Pilot reuse is explicitly mapped in the implementation report.
- `controls-analysis02.json`: normal/slow rifle intervals 0.085/0.340 s, world and
  bullets 0.25, net player movement 0.65, F6 ammunition preserved at 17/90, F10
  wrapper/child counts 0/3 with no orphan rows, bounded assistance and toggles.
- Real moving hit: one recovery step, 25 HP damage, then locomotion. Final fall
  sequence: two interrupted get-ups, eventual GASP get-up, 288.9 cm resumed travel.
  Displaced-leg segment: two completed steps. Successive torso case: three hits,
  two steps, no fall. Death case: four live hits, one death, nine corpse contacts.
- Final blocked case waits for clearance and gets up at the physical location.
  Support removal during get-up releases to unpowered falling. Actual arm/trunk
  collisions carry positive Chaos normal impulses. Analyzed rows have no competing
  source/native controls or uncapped source controls; one impulse per rifle contact.

For owner viewing, start with `Video/Final01-ThreeRendered.mp4`,
`Video/Pilot09-MovingTorso.mp4`, `Video/Final01-FallInterruptResume.mp4`,
`Video/Final03-Blocked.mp4` and `Video/Final01-DeathCorpse.mp4`.
Videos are continuous ordinary-speed WGC captures; the capture rate is about
15 FPS while gameplay sampling targets 30 FPS. JSON observations, capture
timestamps and clock anchors accompany them. `visual-check01.json` identifies
sampled-frame inspection, without claiming owner motion acceptance.

## Provenance and controller closure

`asset-inventory01.json` supplies the complete 3,018-package final inventory
(4,701,512,573 bytes), source/initial migration relationships and final hashes.
`migration-result01.json` and `source-registry-full01.json` preserve native migration
provenance. The four authored/recompiled migrated packages are the Mover character,
Mover Ragdoll character, Mover ABP and CMC ABP. The fifth is the new
`PA_MSQ98_Recovery`. No retargeting or source-skeleton substitution occurred.

`source-preservation-after01.json` verifies all 3,906 original GASP files unchanged,
with no additions or omissions. `owner-preservation-after01.json` verifies the
retained map hash, exact owner engine-config prefix and owner project semantics.
Mover is the only appended project-level plugin. `capacity-after01.json` measures
about 45 GB of project data before the small snapshot, within the 250 GB cap.

The existing controller registry generator can consume the frozen candidate:
candidate name `Candidate01`, freeze evidence
`Saved/CombatSlice01/GASPEnemyFoundation01/Worker/Candidate01/manifest.json`.
It has not been run by the executor. The controller owns registry acceptance,
task/ProjectState administration and the verified task-scoped local closure commit.
No worker issue comment, status/profile update, commit or successor dispatch occurred.

## Integration and limits

`AGASPEnemyFixture` remains the combat/damage wrapper; its GASP child owns the
visible mesh, bodies, capsule, Mover and single PhysicsControl component. Native
recovery drives and GASP source controls have mutually exclusive authority.
MSQ-70 can use `SetMovementCommand`, `StopMovementCommand`, `GetMovementPawn`,
`ReceiveBullet` and `SetHandOccupancy`. Current damage remains one authoritative
regional contact and impulse. The active path uses GASP pose history, chooser and
Mover get-up montages; old Manny/Mixamo sources and candidates remain preserved.

The final moving fixture reaches a lobby wall after 18.1 cm of resumed travel;
the unobstructed Pilot09 footage demonstrates the longer shared sequence. Foot
compliance can leave about 0.5-1.3 cm penetration under disturbance. Severe impacts
can exhaust recovery and fall. The support-removal probe may log Mover's
base-relative start-location warning on its movable diagnostic floor; it does not
accept moving-platform behavior. Optional MovieSceneAnimMixer is excluded because
it conflicts with the purchased-arm AnimBP in this engine build. MSQ-93..96,
MSQ-70 AI and owner subjective motion acceptance remain outside this delivery.

Every capture-owned Play session ended and temporary performance settings were
restored. A new Play session started during closure and was preserved. The final
read-only snapshot records three GASP fixtures, no dirty packages, background
throttling true, MaxFPS 0 and no pending harness override. Editor PID 20976 remains
available in the retained lobby; its log is `Worker/editor10.log`.
