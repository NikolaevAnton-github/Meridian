# UpperVoid01: remove the close-column apparent cutoff (HC-R1)

Continue the owner-authorized high-ceiling atmosphere correction through Multica
MSQ-31, Astra/high/standard. The current HeightCorrection01 passed height placement,
side-aisle preservation and all technical scene checks, but fresh MSQ-32 Review01
requires one visual correction. Read its exact `report.md` and `verdict.json` in
`Saved/OpeningLobby/UpperVoid01/HeightCorrection01/Review01/` and open the actual
failed `Worker/Movement/close_column_up.png` and `motion-005.png`.

At camera approximately (-1551.15,230.16,172.15) cm, yaw0/pitch74.91/HFOV90,
two central shafts appear to end together along a narrow bright-to-black edge.
No physical exposed roof/top was demonstrated. Correct this perceived cutoff
while preserving the owner's high onset near 14 m and visible lower side ceilings.
OwnerHeightMarkup01 remains authoritative; no geometry or height change.

## Scope and implementation choices

Tune only dedicated atmosphere response and, if useful, six central fills to
extend visible decay of detail/brightness/edge contrast within the high zone.
Preserve the twelve side fills, readable long shafts above the beam tier, lower
gloss, both aisle enclosures, and absence of main roof/contact/reflection reveal.
Do not move a blanket fade back into the side corridors. Native world-position
anchoring, fixed exposure and all surface material/source bytes remain required.

Read-only analysis suggests three hypotheses, not prescribed results: replace
the flat-then-steep quintic response with earlier visible decline and a longer
dark tail (provisional onset 13.7–14 m, full extinction 17.5–17.8 m); avoid overly
concentrated attenuation from identical light-function and postprocess curves;
reduce the upper central highlight immediately below disappearance if it still
outlines a cap. Choose a bounded supported solution from actual native trials.
No new effect dependent on viewport height, camera pitch, time or a screen mask.

At most two small purposeful trials, inspecting the exact failed pose and nearby
approach/turn views early. Preserve every trial. The earlier raised placement and
readable aisles must not regress. No geometry, surface materials, bindings,
glass/support, collision/gameplay or configuration changes. No dressing or models.

## Identity and evidence

- New candidate: `LobbyAtmosphere-UpperVoid01/HeightCorrection02`.
- New evidence: `Saved/OpeningLobby/UpperVoid01/HeightCorrection02/Worker/`.
- Source: `Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection02/`.
- New helpers: `Scripts/OpeningLobby/uppervoid01_soft_*.py`.
- Report: `Docs/OpeningLobbyUpperVoid01HeightCorrection02.md`.
- Current map: `/Game/Maps/L_OpeningLobby_PainterStone01`, in place.
- Rollback: `HeightCorrection02/Controller/BeforeCorrection/archive.json`.

Verify current clean live project/map/PIE and exact archive before editing.
Do not edit HeightCorrection01's manifest, report, source, helpers or evidence.
Archive changed map and dedicated atmosphere assets; resolve every old manifest
entry through explicit exact archive paths, never silent rebaselining. Reuse
inspected pure primitives and adapters with new outputs, not frozen entrypoints.

Carry forward unchanged passing evidence. This is a targeted correction, not a
repeat of the full original production. Capture the exact close pose at native
resolution, plus compact context/axis/corner/both-aisle/reflection regression views
with honest resolution and pose metadata. For secondary regression views 960x540
is sufficient; use original 1920 views as references without claiming same pixel
dimensions. Actual input approach/turn and a >=5-second close upward hold must
provide compact timestamped frames and continuous telemetry. Earlier full-route
coverage remains valid for unchanged gameplay; do not invent new traversal code.
If lighting/graph cost changes, take one bounded matching performance sample with
the same reported limits. Save/reopen, capture final properties and graph/source
readback, verify all 107 bindings and zero unexplained deltas, restore temporary
controls and stop PIE, then freeze a new exact manifest.

Budget: aim <=15 MB additional retained correction data; total HeightCorrection01
and this required correction should remain <=100 MB. Keep full schema copies and
redundant baseline images out of the new package where immutable referenced files
suffice. Controller will count archives/review as well. Existing cumulative lobby
planning variance is explicitly documented (~2.462 GB vs 2.4 GB); completing this
small required correction is authorized under the original <=100 MB bound and
250 GB hard project cap. Report all actual sizes and the planning variance; never
delete history or claim the 2.4 GB planning target passed.

One editor writer, one heavy workload, subscription only; official Epic MCP.
Minimal Rider helper registration remains allowed if required. No delegation,
task comments/admin, controller/approval/instruction/config edits, installs,
paid APIs, registry, commits/pushes or later dispatch. Write English.

Fresh independent recheck in MSQ-32 must inspect actual correction images first,
then verify HC-R1 closure and visible regressions, exact identity/preservation and
bounded evidence. Preserve Review01 unchanged. Controller remains through any
necessary bounded correction and the verified owner-viewing handoff. Passing
review does not establish owner acceptance; glass remains DEFERRED_BY_OWNER.
