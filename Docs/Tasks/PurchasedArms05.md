# PurchasedArms05: airborne weapon actions and landing timing

Multica implementation: **MSQ-65**.

Authorized by the owner's 2026-09-18 play-session feedback; see
[exact scope](../Approvals/PurchasedArms05-OwnerScope01.json).
This supersedes PurchasedArms04's Alt jump and airborne action restrictions.

## Required result

1. Correct the visibly premature landing motion after the Shift jump. Identify
   the actual authored contact/recovery phase and bind landing presentation to
   physical floor contact. Merely delaying a montage call while a prior segment
   already looks like landing is insufficient. Preserve coherent takeoff, flight
   and recovery, including a longer fall if needed to expose premature motion.
2. Space must not initiate a jump during Alt tactical sprint. Keep ordinary and
   Shift jumps and their current heights, horizontal momentum and reset behavior.
   Block the real tactical-sprint input path, including its activation transition;
   do not let transient state clearing admit a tactical jump.
3. Immediately after either ordinary or Shift takeoff, the player may enter ADS
   and fire. Do not require releasing held Shift or waiting for the jump montage
   or landing. Preserve immediate fire from hip and ADS, fire continuity while
   airborne and natural held/released input recovery at landing. Preserve the
   existing heading-independent ADS alignment and compatible jump pose base.

## Execution and focused acceptance

Use the existing Multica Unreal executor, Astra/max/standard, production
concurrency one. Read ProjectState, this task, the linked decision and relevant
PurchasedArms04 implementation/source only. An independent read-only audit may
be available at `Saved/PurchasedArms05/Controller/source-audit.md`.

Record starting Git status and affected hashes. Verify configured and actual
native model/reasoning/tier, live project, PIE and dirty state. Prefer official
Epic MCP. Apply the debugging-code skill if runtime diagnosis cannot be resolved
confidently from source or existing logs; use semantic refactoring tools only
when needed. Preserve owner edits, sources and historical evidence unchanged.

Make a bounded production change; reuse existing native input/evaluated telemetry,
MCP and capture utilities. No new dispatcher or test framework. Prefer keeping
asset bytes unchanged where a coherent native solution suffices. If assets change,
preserve exact rollback bytes and create a new revision manifest, not a rewrite
of prior fingerprints. Worker may edit affected native/Blueprint code and narrow
probe/capture adapters, plus `Docs/PurchasedArms05.md`.

Verify real input-driven ordinary and Shift jumps: first-frame/next-frame ADS and
hip/aimed fire requests, actual aiming blend and visible alignment, actual shot
evidence and continued fire, no artificial jump lockout, physical flight and
landing presentation. Include held Shift and released Shift, natural landing
recovery, and one subsequent ordinary jump to show state reset. Combine cases
where practical. Verify Alt rejects Space during established sprint and its
activation boundary; ordinary/Shift still work after Alt release. Check only the
directly shared unrelated-busy gate if the implementation modifies it. A focused
extended-airborne case is appropriate to establish contact-driven landing.

Use short actual first-person recordings and correlate landing motion with
collision telemetry. Montage activity, requested booleans and successful compile
alone do not prove visual success or a shot. Do not run the full animation,
reload, action, movement or unrelated ADS matrix. Build/load affected code and
inspect relevant script/Blueprint errors. One heavy workload at a time.

Leave PIE stopped, retained lobby ready for Play, no unsaved task mutations.
Deliver concise English implementation/results/limitations, exact changed paths
and evidence under `Saved/PurchasedArms05/Worker/`. Continue through bounded
corrections until verified. No purchases, deletion, unrelated cleanup or paused
character/environment work. Controller owns task/approval/ProjectState/AGENTS
edits, profiles, registry, issue closure and the task-scoped local commit.

## Bounded controller review corrections

Independent source review identified a canceled-request edge: Space press/release
before movement consumes `Jump()` can prevent takeoff while leaving presentation
state set. Handle unachieved/canceled takeoff without a grounded animation or speed
lock, and verify only cancellation plus immediate input/next-jump recovery.
The precise finding is preserved in
`Saved/PurchasedArms05/Controller/implementation-review-note.md`.

Actual initial Shift ADS recordings showed a second issue: after floor contact,
the deferred Run End layer tilted the rifle away from the sight line while aiming
and firing remained active. Correct that pose ownership through held actions and
their release. Recheck only affected held/released Shift landing transitions;
preserve initial recordings. See
`Saved/PurchasedArms05/Controller/ads-landing-review-note.md` and the independent
visual/evidence review. Boolean ADS and continued shots alone do not establish
visual alignment.
