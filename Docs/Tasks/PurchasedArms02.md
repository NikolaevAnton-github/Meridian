# Purchased rifle gameplay integration and reload recovery

Multica implementation: **MSQ-62**.

Authorized by the owner's 2026-09-18 follow-up after playing PurchasedArms01.
Read [the exact scope](../Approvals/PurchasedArms02-OwnerScope01.json).
This task supersedes the earlier minimal gameplay exclusions. Original protagonist
and lobby architecture tasks remain paused.

## Required result

Integrate the complete actual rifle-pack gameplay from `D:/devgames/Weapon` into
the retained `/Game/Maps/L_OpeningLobby_PainterStone01` lobby. Include its supplied
movement, aiming, shooting, ammunition, reload variants, recoil, feedback and
other working player/rifle controls. Exclude the vendor arena and tutorial hints.
Inspect source implementation and produce an explicit source-to-project feature
matrix: distinguish working gameplay, animation demonstrations, presentation
settings and absent features. Do not silently reduce scope to the prior minimal
native sampler, and do not invent mechanics merely because a clip exists.

Fix the owner's three observed recovery defects: walking continues but arm bob
pauses after reload; the aimed hand/rifle drifts left after reload; the hip rifle
dips after reload. Establish the cause from source and actual runtime evidence,
including continuous samples before, through and for several seconds after
completion. Preserve animation phase and coherent base/additive blending. Verify
all ordinary/empty and hip/aimed reloads with walking, held aim, changed aim,
direction changes, repeated input, firing and supplied movement transitions.

Choose a faithful integration based on the source pack; migrating its reusable
gameplay/animation logic is allowed. Keep the existing native lobby pawn/game mode
as the integration entry point where practical, but prior implementation choices
must not prevent functional parity. Record necessary integration adaptations.
Keep all player arms, rifle and magazine components shadowless. Preserve camera
comfort, lobby collision and player access; no body is requested.

## Execution and preservation

One production executor through existing Multica, Astra/max/standard, one editor
writer and one heavy workload. Verify actual native settings. Read ProjectState,
this task, PurchasedArms01 implementation/review and relevant animation audit.
Controller's read-only source audit is under `Saved/PurchasedArms02/Controller/`.
Use official Epic MCP, verify live project/PIE/dirty state before mutations.
If debugger evidence is needed and Rider tools are callable, use debugging-code;
otherwise document the exact unavailable capability and use evaluated runtime
telemetry. Reuse existing input and evidence tools; no new dispatcher or benchmark.

Record starting Git status and hashes, preserve bounded rollback for any changed
binary. Keep the lobby map bytes unchanged if code/configuration suffice; otherwise
preserve exact owner state and justify the minimal gameplay-only change. Never
overwrite or save the untouched vendor project. Restore required archived art only
after verifying its recorded hash; preserve the old manifest and record new active
locations separately. Prefer copying only required vendor dependencies. Exclude
the arena and hints from the active dependency closure; do not bulk-copy the pack.
Preserve all owner/source/history bytes and unrelated edits, use Git LFS for new
binaries, measure storage and stay below 250 GB. No paid service or new art.

## Acceptance and handoff

- Build and load successfully in a fresh editor with the retained lobby ready.
- Complete feature matrix with actual input-driven tests of each supplied feature
  and interactions; unsupported features must be sourced, not guessed.
- Continuous reload recovery evidence catches a pause or pose drift even when
  clocks and attachment transforms are technically synchronized. Inspect actual
  comparable first-person views, including a held-aim stationary baseline and
  moving recovery. No capture-induced pause may be mistaken for a gameplay pass.
- Verify no-shadow flags, attachments, missing dependencies and owner preservation.
- Exclude arena, tutorial hints and unrelated showcase startup paths from play.
- Deliver `Docs/PurchasedArms02.md` with controls, cause/fix, feature parity,
  verification, honest limits and exact changed-file inventory; generated evidence
  under `Saved/PurchasedArms02/Worker/`. Leave PIE stopped and lobby ready for Play.

Worker owns implementation and checks, not commits, issue/profile administration,
registry or controller/task/approval documents. Controller owns independent review,
bounded corrections, Multica closure and the verified local task-scoped commit.
Continue until a verified playable result; diagnosis or dispatch alone is not done.
