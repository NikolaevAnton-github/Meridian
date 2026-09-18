# PurchasedArms05: airborne weapons and physical landing

MSQ-65 worker handoff, 2026-09-18, **Correction02**. Implementation and focused
verification are complete. Controller review, acceptance, issue administration
and the task-scoped local commit remain controller-owned.

## Behavior and implementation

Ordinary and Shift jumps allow immediate ADS and hip/aimed fire after actual
takeoff, including with Shift held. Their existing 320/352 cm/s vertical settings
and achieved 360/540 cm/s horizontal movement are preserved. Releasing Shift in
flight retains momentum; landing clears the retained cap and restores ordinary
jump height. Alt rejects Space during its input activation boundary and active
tactical sprint, including combined Shift+Alt.

The authored jump's contact footstep occurs at **0.392494 seconds**, followed by
the main weapon dip around 0.40-0.50. The former 0.65 hold therefore played the
impact in flight; seeking to 0.85 at contact skipped the meaningful landing.
The native adapter now holds at 0.30, clamping before the next mesh tick, and
resumes at 0.38 only from physical `Landed`. The extended-fall recording retains
the flight pose until collision and shows the impact dip afterward.

Each pawn duplicates the jump montage transiently, retaining source poses and
foley while removing its ADS-block and action-unlock notifies. Native playback
does not acquire the generic weapon busy lock. Shots retain the original source
animation, ammo, recoil, effects and timer path. They may replace the jump
presentation; landing never resurrects an interrupted jump or clears another
action's lock. No asset bytes or shared weapon gates were changed.

After Blueprint input binding, only the source Run/Sprint handlers are replaced.
Their original enhanced-input mappings, hold thresholds and grounded
stance/ADS/busy predicates remain. Fast locomotion cannot reassert itself in
flight; physical momentum is stored separately. An airborne fire hold continues
through contact until release. Held Shift resumes naturally after weapon input
ends. Triggered input intent is reconciled after all callbacks, avoiding a
one-frame Run End transition when firing is released.

**Correction01** extends the compatible pose guard through airborne weapon
recovery. The initial candidate let Run End overlay held ADS after landing when
shooting had already replaced the jump. Evaluated telemetry identifies
`AnimGraphNode_SequencePlayer_7` as `A_TFA_FP_AR_Transition_Run_End`: its maximum
weight during the first 0.5 seconds of grounded ADS changed from **1.0 to 0.0**
in both held-Shift and released-Shift takes. Actual corrected frames retain the
aiming line through contact and recovery. The initial failed views remain intact.

**Correction02** separates a pending request from confirmed takeoff. Only
`OnJumped` starts presentation and increments the actual-jump counter. Release
before takeoff, or rejection by movement, cancels the pending request and restores
the ordinary jump setting without touching an existing action or landing tail.
This resolves the controller's short-tap cancellation finding.

## Focused results

Real `PlayerController` input drives every take. ADS/fire requests occur after
the first confirmed airborne observation or the following observation. Responses
were observed about **8.3-12.2 ms** later in game time, while still ascending.
Actual ADS offsets interpolate during flight; fully aimed views are visibly
aligned. Shots are supported by ammo decrements, evaluated firing animation,
casings and visible weapon effects.

| Check | Result |
| --- | --- |
| Ordinary semi and automatic fire | Immediate hip/ADS shots; automatic take has 8 airborne and 8 grounded shots, ammo 30 to 14. |
| Corrected held-Shift hip fire | 9 airborne and 7 grounded shots; held fire survives contact, then running resumes after release. Extra airborne Space adds no jump. |
| Corrected held-Shift ADS/fire | 9 airborne and 6 grounded shots; no Run End overlay while ADS/fire remain held. |
| Corrected released-Shift ADS/fire | 8 airborne and 6 grounded shots; 540 cm/s retained in flight. Subsequent ordinary jump resets to 320 cm/s, 360 cm/s and about 52.24 cm rise. |
| ADS without firing | Ordinary and Shift aim transitions work while the jump montage remains active. Corrected Shift aim stays aligned beyond the montage tail until RMB release. |
| Trajectories and landing | Ordinary rise about 52.24 cm; Shift about 63.21 cm. Jump phase never exceeds 0.30 in flight. Extended Shift flight lasts about 1.24 s before collision releases recovery. |
| Alt boundary/release | Space rejected on simultaneous Alt press, the 0.3 s activation boundary and established sprint. Ordinary and Shift jumps work after Alt release. |
| Busy ownership | A reload replacing an airborne jump retains busy through landing; fire and additional jumps stay blocked until the source unlocks. |
| Canceled request | Same-frame Space down/up produces one cancellation, no takeoff/montage/grounded hold, and running continues. The next press takes off 58 ms later; airborne ADS and a shot succeed. |

Only affected behavior and transitions were checked. No full animation, action,
movement or heading matrix was repeated. Correction01 reran only affected Shift
weapon/landing transitions; Correction02 added one cancellation/recovery take.

## Evidence and preservation

Root: `Saved/PurchasedArms05/Worker/`.

- `authored-clip.json`, `source-audit-before.json`: authored phases, notifies,
  actual source gates and input graph.
- `focused-analysis-final.json`: scoped numerical acceptance, with the old
  combined aim-only take explicitly limited to its unchanged ordinary portion.
- `Correction02/run-end-and-cancellation.json`: exact runtime player/asset
  mapping, before/after evaluated weights and canceled-request recovery.
- `Video/Focus02-ShiftLanding.mp4`, `Final01-ExtendedShift.mp4`,
  `Final02-OrdinaryAuto.mp4`, `Final01-OrdinaryADS.mp4`,
  `Correction01-ShiftHeldHip.mp4`, `Correction01-ShiftHeldADS.mp4`,
  `Correction01-ShiftReleasedADS.mp4`, `Correction01-ShiftAimOnly.mp4`,
  `Correction02-CancelRecovery.mp4`: principal actual recordings. Matching raw
  JSON and `Views/*-frames.json` correlate views with collision/evaluated samples.
- `visual-review.json`: inspected frames and candidate distinctions. The initial
  combined `Final01-Landing` capture failed and lost native movement delivery;
  it is excluded. Initial Shift weapon landing visuals are superseded by
  Correction01. All originals, rejected evidence and rollback bytes remain.
- `Correction02/build.log`, `editor.log`, `cold-contract.json`, `log-check.json`:
  successful build/fresh load, seven preserved graph guards, unchanged ADS
  component-space/+90-degree conversion, no relevant script/Blueprint/load errors.
- `preservation-before.json`, `Correction02/preservation-after.json`: 1,419
  starting files checked. Only the three listed native source files differ;
  all Content packages, retained map, original/vendor sources and configuration
  retain their starting hashes. No binary revision manifest is required.
- `execution-receipt.json`: configured and native Astra/max, explicit default
  service tier and disabled fast mode; actual turn context confirms Astra/max.
  The turn's service-tier field is null, so no stronger server-routing claim is
  inferred. No profiles were changed.
- `changed-files-final.json`, `storage-after.json`,
  `editor-state-final-correction02.json`: exact handoff hashes, project capacity
  check, retained lobby open with PIE stopped and no dirty packages. Temporary
  background throttling is restored. Only a verified startup-generated field
  from the disabled AndroidFileServer plugin was removed from configuration.

Recordings are silent and sampled at roughly 12 fps. Clock buckets and capture
cadence limit frame-to-telemetry precision; reported response intervals are game
observations, not hardware-latency measurements. This is worker verification;
controller review and owner visual acceptance remain separate.

## Exact changed paths

```text
Source/MeridianSquad/OpeningLobbyCharacter.cpp
Source/MeridianSquad/OpeningLobbyCharacter.h
Source/MeridianSquad/PurchasedArmsAnimInstance.cpp
Docs/PurchasedArms05.md
Scripts/PurchasedArms05/analyze05.py
Scripts/PurchasedArms05/bootstrap.py
Scripts/PurchasedArms05/capture05.py
Scripts/PurchasedArms05/client05.py
Scripts/PurchasedArms05/diagnose_landing05.py
Scripts/PurchasedArms05/preserve.py
Scripts/PurchasedArms05/review05.py
Scripts/PurchasedArms05/tools05.py
Scripts/PurchasedArms05/unreal05.py
Scripts/PurchasedArms05/video05.py
```

Saved evidence is untracked. Existing owner/controller edits in AGENTS,
ProjectState, task/scope records and `.multica/` are outside this worker change.
