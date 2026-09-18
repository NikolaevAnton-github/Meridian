# CombatFoundation01 / MSQ-68

Implemented and worker-verified, including controller-requested Correction01,
on 2026-09-19 over the retained PurchasedArms06
rifle. Valid shots consume one round and launch finite-flight bullets; collision
applies damage once. Reloads use finite reserve ammunition. The retained lobby
is saved and ready for Play. Controller review, acceptance, registry decisions,
issue administration and the local closure commit remain with the controller.
No successor was dispatched.

Scope follows [the task](Tasks/CombatFoundation01.md),
[owner time/self-hit decision](Approvals/CombatFoundation01-OwnerScope01.json)
and [focused verification rule](Approvals/FocusedVerification01.json).
This delivery adds no enemies, player health, time-ability binding, weapon,
structural destruction or permanent lobby actors.

All evidence below is relative to
`Saved/CombatSlice01/CombatFoundation01/Worker/`.

The authoritative path is `UCombatRifleComponent::TryShot`. It validates action
locks, cadence and ammunition, reserves a projectile slot, consumes one round,
then invokes the existing paired montages, recoil and muzzle presentation.
Animation notifies never create bullets or apply damage. Native bindings replace
the source fire/timer, V and reload callbacks. The source weapon's only Tick,
its demonstration underflow refill, is disabled; its `AmmoCount` becomes a
presentation mirror. The dormant vendor graphs and immutable vendor project
remain preserved. Source firing/handling sounds, shadowless arms, movement,
ADS, jump behavior and the PurchasedArms06 muzzle asset remain retained.

| Binding | Implemented behavior |
| --- | --- |
| LMB | Semi: one request per press. Auto: held fire at the existing 0.085 s cadence; no catch-up burst after a hitch. |
| V | Switch between semi and auto with the source selector animation. Empty fire follows ammunition, never a selected mode. Switching while firing or locked is rejected. |
| RMB / middle mouse | Existing ADS / canted ADS. |
| Tap R | Partial reload when rounds remain; bolt-handling empty reload at zero. |
| Hold R, 0.3 s | Read-only magazine inspection; releasing it does not also reload. |
| Q | Quick partial reload; at zero, use the empty reload with bolt handling. |
| E | Same state-based reload choice as tap R. It cannot force an artificial empty state. |
| F6 | Reset the three targets and clear bullets, impact marks, rifle VFX and physics props. Ammunition stays unchanged. |
| WASD, mouse, Shift, Alt, Space, C | Retained movement; ordinary/Shift airborne aiming and shooting remain available. |

Other purchased-pack controls remain as documented in
[PurchasedArms02](PurchasedArms02.md), with the later
[PurchasedArms05](PurchasedArms05.md) movement correction. Melee, grenade,
interaction, syringe and malfunction presentations are still gestures rather
than new combat systems.

The HUD explicitly says **COMBAT PROTOTYPE** and shows magazine/capacity,
reserve, firing mode, reload/empty state and brief hit feedback. Main magazine
depletion reads authoritative ammunition. The visible spare uses the resulting
reload load, `min(capacity, magazine + reserve)`. This prototype retains existing
rounds even in quick/empty presentation variants; thrown magazine props are
cosmetic and do not create or discard ammunition. The only adapted package is
`ABP_TFA_AR_Magazine`: its count getter now calls the native
`GetCombatMagazineRounds`. Its saved graph compiled with warnings treated as
errors and was loaded in fresh editors before the final checks.

Reloading creates one transaction and locks firing and other source actions.
Walking and permitted aim transitions continue. Repeated R/Q/E input cannot
restart that transaction. Three per-pawn transient montage copies retain the
authored animation, sounds and hand notifies. Each replaces exactly one hands
`AN_UnlockActions` notify with `CombatReloadTransfer` at the same authored time:

| Reload | Authored transfer phase | Transfer |
| --- | --- | --- |
| Partial | 2.631934 s | `min(capacity - magazine, reserve)` |
| Empty | 2.949777 s | Same accounting |
| Quick partial | 2.127141 s | Same accounting |

These are montage times, not promised wall-clock durations: the retained
montage rate can differ. The native branching notify validates the hands mesh,
montage and montage-instance ID, then commits once and unlocks. The paired weapon
montage cannot transfer ammunition. Explicit `CancelReload` or external montage
interruption before this notify leaves both counts unchanged and restores
magazine visibility. Cancellation after commitment retains the completed
transfer. A missing/interrupted notify never falls back to a timer refill.
Full magazines and zero reserve reject reloads. Held automatic intent can resume
after an ordinary action lock; after dry fire, releasing LMB rearms the trigger.
Dry feedback is at most once per held press, with a 0.3 s minimum between presses.

| Tuning / safety | Initial value or policy |
| --- | --- |
| Magazine / reserve | 30 / 90; native component tuning, capacity clamped to the supplied 30-round presentation and reserve to 0–9999. |
| Bullet damage / target health | 25 / 100; exposed tuning. Four hits destroy a fresh target. |
| Bullet speed | 30,000 cm/s (300 m/s); tunable 1–200,000 cm/s. Straight flight, no gravity, penetration or ricochet in this foundation. |
| Bullet radius / launch position | 0.5 cm sphere; gameplay view offset `(forward 55, right 12, down 8)` cm. |
| Range / simulation lifetime | 30,000 cm / 3 simulation seconds. Travel is clipped to the first limit before sweeping. |
| Bullet capacity | 128, tunable with a hard maximum of 256. Full capacity rejects the launch, ammunition consumption and muzzle feedback together. |
| Stopped-bullet safety | Retire after 120 real seconds, without movement, damage or ammunition refund. This safety limit is separate from simulation age. |
| Impact feedback | At most 48 records, 0.3 real seconds each. Small neutral stone flecks or short amber metal sparks. |
| Source muzzle VFX | Existing auto-destroy behavior plus independent 64-component / 4-real-second safety limits on rifle-owned Niagara components. |
| Source physics props | At most 64 casings/magazines/other vendor physics props, 8 real seconds each; oldest retired first. They do not block gameplay bullets. |

The aim ray chooses convergence only; it never deals damage. A view-to-muzzle
sweep prevents spawning beyond cover. When that path is blocked, or the aim
obstruction is closer than the nominal muzzle, the bullet begins at the view and
travels into the obstruction. All positions are ordinary gameplay-world
coordinates; the retained first-person rendering scale of 0.3 is not ballistics.
`ACombatProjectileWorld` sweeps each traveled segment, including high-speed
segments through thin geometry, and consumes a bullet before notifying damage
receivers. Existing surface materials are read for metal classification, never
edited. Nonmetal surfaces receive the neutral fallback.

Correction01 queries every round against the same step's obstruction state before
delivering damage or public hit callbacks. This is a conservative simultaneous-step
policy: both rounds stop at a foreground target even if the first damaging hit
destroys it. Neither can reach a rear target during that step. Delivery has a
deterministic hit-fraction/shot-ID order; this is not full physical subframe
simulation. A reset generation cancels any remaining queued hits and counts those
rounds as retired. New rounds launched by a listener wait until the next step.
Nested advancement is rejected. A reset during point-damage delivery also suppresses
stale post-reset impact feedback.

The future time integration point is `SetProjectileTimeScale`, clamped to
`[0, 1]`. It multiplies the manager's world delta; zero preserves position,
velocity, distance and simulation age exactly. The world keeps ticking and
player movement is untouched. The later ability must use this seam with a
coherent world policy rather than pausing the entire engine or applying the same
multiplier twice. Rifle action timing is unchanged in these development probes;
no player-facing time ability is implemented here.

After character movement, a continuous relative sweep tests bullet travel
against the previous/current upright player capsule. A stationary bullet still
detects a moving player crossing between frames. Capsule-size changes use a
conservative envelope. Each new round snapshots character capsules at launch and
uses those birth samples for its first contact interval. It cannot hit movement
that occurred before it existed. Subsequent steps use the manager's full previous
capsule history; launching a new round does not truncate older suspended rounds'
contact history. Shooter exclusion lasts only until geometric launch
clearance outside the capsule plus 2 cm; it is not a permanent ignored actor.
A launch that travels 200 cm without clearing is retired, and stopped launches
also have the real-time safety bound. Normal muzzle launches already start
outside the capsule. Restart/teleport code in later tasks should clear old
projectiles rather than treating a discontinuous relocation as physical travel.

The 120-real-second safety limit explicitly includes suspended damaging bullets.
A long stop can therefore retire them without refund; they are not indefinitely
resumable. This is safety retirement, not advancing frozen simulation age, and the
future player-facing ability must deliberately account for that prototype limit.

Hits call ordinary point damage with the original instigator and shooter as
causer. `OnBulletHit(ShotId, ShooterIdentity, Shooter, Victim, Damage, Position,
bSelfHit)` also exposes the unique shot and retained shooter path. The path
survives loss of the weak actor reference. Own-shot contact reaches the same
damage/event path. The pawn has no health implementation yet; PlayerSurvival01
must consume this contract. No per-bullet rigid-body actor is allocated.

For a repeatable setup, open `/Game/Maps/L_OpeningLobby_PainterStone01` and Play.
The game mode spawns three removable primitive targets at `(-850, -260, 135)`,
`(-850, 0, 135)` and `(-850, 260, 135)` cm. Each is 18 cm deep, 75 cm wide and
100 cm high. The center target is down the central aisle; the outer two are
accessible from the side aisles. Health labels pulse on hits; destruction hides
the block and disables its collision, retaining a DESTROYED/reset label.
`target-setup-02.json` confirms no overlaps with static scene geometry.
F6 restores target health and removes transient shot feedback without supplying
rounds. Stop/Play starts a new prototype session at 30/90. No targets or test
cover are saved into the editor map.

The target remains a gray checker cube. The runtime material audit
`target-material-Correction01.json` finds no vector parameters in its WorldGrid
material, so the existing `Color` setter has no visible mesh-color effect. Actual
feedback is the yellow health-label pulse, HUD hit text, small impact particles,
and hidden mesh/disabled collision on death. `Correction01/ADSAfterShot.png` shows
a real 25-damage hit and the yellow 75/100 label. No mesh color flash is claimed,
and no accepted material was modified to produce target feedback.

Focused verification passed **138 assertions over 14,387 sampled rows** in
`verification-summary01.json`. The additional final impact-rendering correction
passed its 957-row check in `Review/visual-correction-checks.json`.

The subsequent controller correction passes **70 focused checks over 1,915 sampled
rows**, plus the native probes included in those checks, in
`Correction01/verification02.json`. It supersedes the initial handoff for the
callback, capsule-birth and same-step obstruction contracts. The original report,
Smoke01 and exact controller source-review bytes are preserved.

| Correction01 evidence | Result |
| --- | --- |
| `corrections-Correction01.json` | A real `OnBulletHit` listener resets with three initial live rounds, cancels one other queued hit and one surviving round, and launches two replacements. Replacements retain zero age/travel until the next step; final accounting is five launches, three hits, two retirements. |
| Same native probe | The controller's capsule example (old X=0, new X=-10, new round X=28, radius 34) produces no false birth self-hit. Later crossing hits once. A separate older suspended round still detects the full crossing interval when a new round is launched afterward. |
| Same native probe | Two rounds starting at X=90 and X=0 both stop at the one-hit front target at X=100; the rear target at X=150 remains at 100 health. Reversing insertion order gives the same result. |
| `ballistics-Correction01.json` | Changed collision code still passes the narrow finite-flight, thin-wall, clock/stop/resume, self-contact, capacity, safety-expiry and cleanup probe. |
| `Correction01-LegacyADSRelease.json` | Retired refresh-before-release driver order reproduces the original symptom: scheduled held keys are empty, but actual player-controller RMB state remains down, aim stays true, and both FOVs stay at 78. |
| `Correction01-ADSReleaseReentry.json` and video | After shooting and after a real one-round reload, actual RMB state clears, aim becomes false and both camera/view FOV settle to 90. Re-entry reaches 78. Stationary comparable views show the rifle returning to hip and back to ADS; this conclusion uses actual state and images, not input labels. |
| `Correction01-Cadence60Retry.json` | At measured 59.9709 fps, the two-second automatic burst launches 24 rounds. Mean inter-shot spacing is 85.5085 ms over 23 intervals. No frame emits multiple shots; held input resumes after reload with six normally spaced rounds and stops on release. The existing phase correction is retained without another rifle-code change. |
| `Correction01-Airborne.json` and video | Ordinary and Shift jumps accept aimed fire within 0.12 s of takeoff. The Shift aim request begins during takeoff, blends to full ADS in flight, retains 540 cm/s, and keeps firing through physical landing. Both jumps/landings and release of the airborne intent latch pass. Input-binding order remains rifle bindings first, intent observers second. |
| `Correction01/build01.log`, `handoff-Correction01.json` | Corrected native code builds successfully and loads in a fresh UE 5.8.1 editor. Final PIE is stopped, packages/maps are clean, and no prototype actors leaked into the editor world. |

The ADS reproduction isolates the Smoke01 issue to synthetic input refresh order;
no native aiming correction was needed. Refreshing a held RMB before processing
its release submitted a press and release in the same engine input frame. The
current driver processes due events first and refreshes only keys still held.
The original Smoke01's lack of a driver exception was not evidence of a successful
ADS release. Actual key state is now recorded separately as `aim_key_down`.

The first correction analyzer checked exact settled FOV during the retained
roughly 0.37-second aim blend and failed those timing assumptions. Its
`Correction01/verification.json` is retained. `verification02.json` distinguishes
immediate aim-input/fire eligibility from settled FOV after 0.4 seconds; it uses
the same unchanged telemetry and video. The first cadence capture stopped early
and its post-reload interval contains unscheduled input changes; it is retained
but excluded from final cadence/resumption acceptance. Only that case was rerun.
An initial adapter call used an unsupported Python Key constructor; its failed
`28820Correction01-LegacyADSRelease.json` is also retained. The valid retry constructs
the key through its exposed property. No full animation matrix was run.

`Scripts/CombatFoundation01/correction-cases.json` contains the bounded case set.
Use `run68.py <case-file> <fresh-prefix> <editor-pid>`; a literal `-` means no
prefix and avoids Windows dropping an empty argument. Select affected cases,
preserve old names, and use the existing native driver/recorder. The runner now
saves capture-process logs and restores the current session's throttle and frame
cap instead of applying a previous session's saved values.

| Evidence | Result |
| --- | --- |
| `ballistics-Final01.json` | Finite pre-contact travel, one collision/damage, a 2 mm wall at 2000 m/s, target death/reset, clocks 1/0.25/0, exact freeze/resume, simulation and real-time retirement, capacity, launch clearance and own-shot attribution pass. Temporary fixtures are removed. |
| `AmmoDry01.json`, `PartialLow01.json` | Held empty fire stays bounded; reserve 4 and reserve 1 transfer exactly; zero reserve cannot reload; hold-R inspection is read-only. |
| `QuickCancel01.json`, `EmptyVariants01.json` | R/Q/E select from real state; repeated input, duplicate-notify probes, pre-commit interruption and post-commit cancellation preserve accounting. Blocked reload-time fire creates no bullet. |
| `StoppedSelf01.json`, `SelfAttributionFinal01.json` | Actual W movement reaches 360 cm/s during bullet stop and contacts the suspended own bullet exactly once. Quarter-speed flight, a second stop, resumption and final shooter/shot identity pass. |
| `NearCover01.json`, `Capacity01.json` | Six hip/ADS shots are stopped by near, offset-muzzle and thin cover; removal restores damage. Capacity denial spends no round; reset frees space without refund. |
| `MovingAirborne01.json` and video | Moving ADS fire/reload; immediate aimed fire after ordinary and Shift takeoff; 540 cm/s Shift flight and sustained fire through physical landing pass. Two jumps and two landings. |
| `FeedbackExpiryFinal01.json` | Automatic cadence remains approximately 85.15 ms. Release stops firing; all tracked/actual rifle Niagara components, props and impacts expire. |
| `SurfaceResetFinal01.json` | Unchanged Painter stone/metal materials select distinct feedback. F6 clears bullets, impacts, casings and VFX with ammunition unchanged. |
| `SurfaceVisualFinal02.json` and video | Final small flecks/sparks work in hip/ADS and disappear; five shots consume five rounds, then reset leaves 25/90 and no feedback objects. |
| `build07.log`, `handoff-Final02.json` | UE 5.8.1 build succeeds. Fresh final editor has the retained map, stopped PIE, no dirty content/maps and no editor-world gameplay actor leaks. |

The task adapters reuse the existing official Epic transport, native key probe,
`verify02` lifecycle and ordinary-speed video recorder. `cases.json` preserves
the scoped case definitions; select only affected cases for a correction.
`run68.py <case-json> Review02- [editor-pid]` creates fresh evidence names and
optionally records cases marked `capture`. Existing evidence names are refused.
`run68.py ballistics <unique-name>` runs the native PIE-only foundation probe.
Neither `ProbeAmmo` nor collision fixtures operate outside PIE. This is not a
new dispatcher, benchmark framework or full animation matrix.

The original `Smoke01` take exposed a frame-rounded cadence and a synthetic ADS
release issue in the adapter. The cadence phase and input-refresh order were
corrected; later cases supply acceptance evidence. The initial large radial
impact marks in `SurfaceResetFinal01.mp4` were reduced after visual inspection;
use `SurfaceVisualFinal02.mp4` and `Review/FinalStoneImpact.png` /
`FinalMetalImpact.png` for the delivered appearance. Earlier evidence is retained.
The first native build had API/type compilation errors, subsequently corrected.
Initial Python audit/class-reload failures were resolved by separating the stable
reflected tool registration from its reloadable implementation.

Recorded frames are ordinary gameplay views, approximately 11–12 captures/s;
they do not resolve every muzzle-flash peak. Frame extraction preserves the
recording and records the monotonic-clock alignment. Worker inspection covers
the actual hip/ADS, target/reset and airborne views, not independent acceptance.
`Audio/SurfaceResetFinal01.wav` has nonzero recorded game audio: 48 kHz stereo PCM,
10.4107 s, RMS 0.07195 and peak 0.80215. This mixer recording is not represented
as a synchronized video soundtrack or a physical-speaker test.

Only one existing binary changed:
`Content/InfimaGames/TacticalFPSAnimations/Weapons/AssaultRifle/Meshes/ABP_TFA_AR_Magazine.uasset`.
Its SHA-256 changed from
`aff7a61eca248ef185a750f140beeec00f4a37dbb4e32cacd951b41265445a4f`
to `bc96bc6301e42e72a07815fd4a91117eea649577d3f4d9b094d833694ee5c824`.
The existing Git LFS filter applies. `magazine-adaptation.json` records the
immediate edit; the final save/readback hash above is the delivered package.

Existing native changes are the character/game-mode integration, magazine
AnimInstance getter and the Json build dependency. New native files are
`CombatRifleComponent`, `CombatProjectileWorld`, `CombatTarget` and
`CombatPrototypeHUD` headers/implementations. New text comprises this report
and `Scripts/CombatFoundation01/`. Exact task paths, sizes and SHA-256 values are
in `changed-files-handoff.json`; rollback copies remain under `Rollback/`.
The earlier `changed-files-final.json` is retained; the handoff manifest records
the final report wording correction without changing implementation hashes.
These two manifests describe the initial delivery. The current correction's
exact source/report/adapter bytes and evidence hashes are recorded separately in
`Correction01/handoff-manifest.json`; before-correction bytes are in
`Correction01/before.json` and `Correction01/Before/`.

The direct preservation inventory checks 1,419 starting files, including the
vendor project and original protagonist sources. Its expected changes are the
one magazine package and seven native/build files; no starting file is missing.
The owner-owned `Config/DefaultEngine.ini` remains
`f3caa33c2d9a10d7e4626cdd6c3b2791fbbfa0a425f7af29f419b837f0c71bbf`;
the lobby map remains
`b28fa0f6e8bb80dcc71b4789df9c3e2375a3cf8b1da67021225584e4560fd92f`;
the PurchasedArms06 muzzle system remains
`e6a74ae3ef8e9f49abb695cd83b324578a7061fe3cc4774a3d8948bdb962e166`.
Accepted surface materials, atmosphere and geometry remain unchanged.

Project storage is approximately 28.3 GB, about 0.1 GB above the 28.17 GB start,
within the 250 GB cap; `storage-final.json` supplies exact final bytes and growth.
Saved profiles, native process arguments and actual turn context verify
Astra/max, default service tier, subscription login and disabled fast mode.
The turn context does not itself serialize a service-tier value; the persisted
profile and native arguments explicitly supply `default`. No profile change,
purchase, paid API, registry mutation, owner-asset cleanup, commit or successor
dispatch was performed. The editor was initially closed; official Epic MCP
confirmed project/map/PIE/dirty state before authoring. Rider was limited to
adapter bootstrap and the temporary audit/close fallback. Final editor PID and
log are recorded in `editor-final.pid` and `Saved/Logs/CombatFoundation01-Final.log`.

For Correction01, the starting editor was closed. The fresh corrected editor is
recorded in `Correction01/editor.pid`, with
`Saved/Logs/CombatFoundation01-Correction01.log`. The native process and actual
turn context again verify Astra/max/default despite an inherited configuration
file containing an older different effort value; explicit native arguments and
the executed turn both use max. No profile write was needed. Exact additional
disk growth and preservation results are in `Correction01/preservation.json`.
Controller documents, owner configuration, initial Smoke01 and prior reviews are
preserved. No commit, registry/status administration or successor dispatch was
performed by the worker.
