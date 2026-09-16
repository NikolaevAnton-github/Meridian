# Lobby tasks closed; remaining work deferred

On 2026-09-16 the owner instructed us to defer all remaining lobby work and
close the current tasks. The owner will provide a new list after gameplay has
been integrated into this space. The authoritative decision is
[LobbyDeferred01-OwnerClosure01](Approvals/LobbyDeferred01-OwnerClosure01.json).

The seven open tasks are closed in Multica with terminal status `cancelled`
and disposition `CLOSED_BY_OWNER_DEFERRAL`:

| Issue | Closed scope | Previous status |
| --- | --- | --- |
| MSQ-4 | Overall lobby walkthrough milestone | in_progress |
| MSQ-6 | Remaining architecture/material work and acceptance | in_progress |
| MSQ-7 | Remaining atmosphere and final walkthrough acceptance | in_progress |
| MSQ-14 | Historical Variant A neutral 3D owner-review gate | in_review |
| MSQ-20 | Functional 3D assembly owner-review gate | in_review |
| MSQ-28 | Complete opaque materials and stone slab owner-review gate | in_review |
| MSQ-30 | Entrance glazing refinement | backlog |

This status records closure at the owner's request. Retained work has not been
rejected, and deferred work has not been declared complete or newly accepted.
Previous scoped acceptances and completed reviews keep their original meaning.
UpperVoid01 remains owner accepted; MSQ-31 and MSQ-32 remain done.

Deferred items include glass refinement; dressing, signage, fixtures and any
chosen static damage; final scene route/performance verification; outstanding
whole-lobby/material acceptance and stable accepted asset registration/handoff.
Existing movement and collision remain implemented. Old pending/backlog wording
in task documents and historical reports does not authorize further execution.

The current saved map is `/Game/Maps/L_OpeningLobby_PainterStone01`.
Its observed SHA-256 is
`b28fa0f6e8bb80dcc71b4789df9c3e2375a3cf8b1da67021225584e4560fd92f`.
Administrative closure makes no scene, asset, source or gameplay changes and
preserves owner edits and all prior evidence. Future owner/gameplay edits need
not preserve this dated snapshot hash.

Issue updates use `--no-start` (`suppress_run=true`). No production or gameplay
run is commissioned by this closure. Exact before/after issue records, original
document snapshots and the closure verification are under
`Saved/OpeningLobby/OwnerDeferral01/Controller/`.
