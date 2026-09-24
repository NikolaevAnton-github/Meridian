# MSQ-120 / CAI-T03 controller acceptance

2026-09-24. **Candidate01/build03 is accepted within the authorized technical
scope and delivered for owner testing.** Native build, focused checks and the
sole primary independent review pass. No blocking finding or correction remains.
Actual motion, cover usefulness, combat feel, difficulty and performance remain
owner judgement; a running owner Play session is not an acceptance verdict.

Authority: [exact owner instruction](Approvals/CombatAI01-MobileLean01-OwnerStart01.json)
and [task](Tasks/CombatAI01/CAI-T03.md). See the
[implementation](CombatAI01-MobileLean01.md) and
[primary technical review](CombatAI01-MobileLean01Review.md).

## Scope and evidence applicability

The opponent now uses separate generation-checked movement and weapon action
ownership. It can fire while completing a bounded 1.8 m lateral walking step or
a cautious approach, retaining weapon range. Aim, burst and burst rest preserve
the route. Achieved grounded walking through 220 cm/s supports fire; running
and unsupported physical motion do not. Actual speed increases spread. Current
sight, achieved aim/stance, actual muzzle clearance, ammo/reload, finite projectiles
and world-time cadence remain authoritative.

Both cover edges now use a real signed upper-body lean through the existing
spine correction before hand IK. Default lean is 32 degrees at 120 degrees per
world second. Pelvis and legs remain outside the changed bone subtree; anchor
and firing feet coincide. Reachable protected edge selection, sampled upper-body
clearance, achieved head/chest displacement and actual muzzle clearance gate
exposure and fire. Low-cover stand/burst/crouch remains compatible. Interruption,
weapon loss, death, recovery, disable and reset clear obsolete movement/lean/fire
ownership. No player Q/E controls or unrelated successor scope is included.

The executor supplies a matching Development Editor build, **67 production
assertions**, **18 native pose-math cases**, and actual graph/bone wiring.
The primary reviewer verifies production and consumers, confirms **75 extracted
method/fragment identities**, and adds **33 passing assertions** for the concrete
missing scan-to-edge-route handoff. Both-side availability, independently blocked
sides and finite no-option fallback are covered. Applicable passing evidence is
reused; the controller did not repeat the technical review or passing tests.
ML01-ML06 pass within the documented code/math/asset-inspection boundaries.

No agent gameplay, PIE, animation playback, firing or performance probe ran.
The owner subsequently started Play in the controller-opened ordinary editor;
that session is preserved. Source/math checks do not establish visual quality
or actual Physics Control tracking. Standing-only lateral lean, conservative
static geometry, the walking-fire envelope, single-floor local navigation and
no lean-fire during travel remain explicit limits.

## Identity, preservation and execution

Manifest SHA256:
`5036d92fc6998c9af3dc7c67fc3d9975b14adb6b8ee63cb4f720badd1a1bc0af`.
DLL SHA256:
`a0a8a67d1c15450aa14c2244477f88966d06ae8408f255473b03868a8e304fc7`.

The existing controller identity validator matches all **298 current and archived
entries**; see `Saved/CombatAI01/CAI-T03/Controller/identity-Candidate01.json`.
The reviewer confirms 157 preserved asset files and 362 historical evidence files.
Owner config/project/map bytes and durable instructions are preserved. The
temporary Multica role trailer and current ProjectState update are explained
administrative changes outside the candidate. No binary asset changed and no
accepted AssetRegistry fingerprint was replaced.
The new owner-decision JSON received only CRLF-to-LF normalization for the Git
whitespace gate. Parsed values, including the exact owner message, are identical;
original bytes and the comparison are retained in controller evidence. Historical
preservation snapshots and the candidate manifest were not rewritten.

Executor and primary reviewer profiles and actual native processes use
**Astra/max/default, fast disabled**. Native turn contexts confirm Astra/max;
explicit process arguments establish default tier. Profiles remain unchanged.
The earlier read-only advisory survey was not an executor or acceptance reviewer
and is not used as technical acceptance evidence.

The executor's temporary editor ended after its run despite its recorded launch
intent. The controller reopened the ordinary editor with the matching DLL.
Official Epic MCP confirms the retained lobby in a newly active owner PIE world,
with no dirty packages. The owner session is left running; no additional lifecycle
change is required. Final process/state evidence, runtime shutdown, task status,
preservation and local commit are recorded in
`Saved/CombatAI01/CAI-T03/Controller/closure-summary.json`.
MSQ-105 through MSQ-117 remain undispatched; MSQ-101 remains coordination only.

Owner route: observe short lateral walking bursts at useful rifle range; use
either edge of a column to inspect actual torso lean and grounded feet. Check
low cover, hit interruption, F6 reset and Y slowdown. The implementation report
documents tuning and existing status/trace controls. Final motion/play acceptance
remains with the owner.
