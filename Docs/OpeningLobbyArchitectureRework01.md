# Lobby architectural rework: owner selection package

**The owner selected Variant A of LobbyArchitecture-Rework01 / Candidate01 on
2026-09-14.** The [external owner decision](Approvals/LobbyArchitectureRework01-VariantA.json)
binds the unchanged manifest below. After executor clarification, the owner
explicitly authorized max-effort production. The separate
[neutral A assembly](OpeningLobbyArchitectureReworkA01Review.md) subsequently
passed technical and independent visual review and is ready for owner walkthrough.

The following review evidence describes the package before owner selection.
Independent MSQ-13 review passed the 2D visual, dimensional and evidence criteria;
no bounded correction was requested. The controller inspected the actual source
art and all eight candidate sheets, verified package identity and protected inputs,
and agrees that **A is the stronger reference match**. Selection of A does not
establish acceptance of the current lobby or any future 3D implementation.

## Reviewable result

- [A: spatial design](../Assets/Concepts/OpeningLobby/ArchitectureRework01/05-A-spatial.png)
- [B: spatial design and comparison](../Assets/Concepts/OpeningLobby/ArchitectureRework01/08-B-spatial-comparison.png)
- [A: plan and entrance elevation](../Assets/Concepts/OpeningLobby/ArchitectureRework01/03-A-plan-elevation.png)
- [A: sections and junctions](../Assets/Concepts/OpeningLobby/ArchitectureRework01/04-A-sections.png)
- [Complete package, dimensions, deltas and reproduction](../Assets/Concepts/OpeningLobby/ArchitectureRework01/README.md)
- [Independent review decision record](OpeningLobbyArchitectureRework01Review.json)

| Variant | Spatial decision | Owner-visible tradeoff |
| --- | --- | --- |
| A, recommended | Continuous tall portal, 1.6 m face-to-glass depth, separated terminal shoulder, 0.6 m upper-wall setback | Preserves the reference's vertical light field and accepted glazing; the deep jamb hides more glass on an oblique approach. |
| B | Deeper engaged end piers, 11.2 m entrance bridge and 1.2 m upper-wall setback | Stronger horizontal enclosure; upper sill rises 0.6 m and upper glass height decreases 0.6 m. Less faithful to the continuous vertical composition. |

Both retain the 60 x 24 x 18 m hall, six free pier pairs, human elements and
checkpoint positions. Both explicitly propose developed secondary geometry and
a recessed final side-bay soffit. Nominal crossover capsule margins are 1.06 m
for A and 0.46 m for B; these are drawing calculations, not engine collision tests.

## Identity and verification

Manifest: `Assets/Concepts/OpeningLobby/ArchitectureRework01/manifest.json`

SHA-256: `fb0f306ff60011d01a1008345017d9029964301b2365d81d8ca5d5eba686a4df`

The immutable submission keeps its original `pending_independent_review` field.
This external handoff and review record establish subsequent readiness for owner
selection without changing reviewed bytes. All 28 manifest entries match. The
manifest also binds six local worker-evidence files under `Saved/`; retain those
files for full-manifest verification. Generated evidence remains outside Git.
Package text uses explicit LF Git attributes to preserve its hashes; PNGs retain
the existing Git LFS policy. No commit or push was made.

Designer checks passed; independent review compared 55 shared values with the
approved scale schedule and all 26 tagged plan masses with the dimension source.
It inspected the original images before author conclusions and found no critical
or unverified drawing-stage requirement. Before/after review hashes match.
Controller verification also confirms all 150 recorded protected files unchanged
after removal of the completed runtime's managed instruction suffix. This
fingerprint baseline is scoped, not a claim to have audited every project file.

Evidence: `Saved/OpeningLobby/ArchitectureRework01/Review/` (`first-look.md`,
`report.md`, `verdict.json`, `preservation.json`) and `Controller/` (run records,
integrity check, model/skill configuration receipts and native usage snapshot).
The candidate and complete Worker directory occupy 33,612,890 bytes. The reviewer
traced reproduction source and ran the read-only verifier; it did not regenerate
the frozen PNGs or claim an exact fresh-render reproduction.

## Process change and next gate

The [authorized task](Tasks/OpeningLobbyArchitectureRework01.md) gives secondary
architecture explicit design freedom beyond the old 0.05 m proxy-envelope rule.
The accepted overall scale is retained. Project-owned reference-analysis,
architecture-production and architecture-review skills are assigned to the
existing Multica roles. The designer applied the analysis skill; the independent
reviewer applied the review skill. The production skill is assigned for later
authorized 3D work and has not yet demonstrated its effect in that phase.

MSQ-12 and MSQ-13 each completed one Multica run with native `gpt-6-astra` / `max`,
standard service and subscription authentication, with concurrency one. The
designer corrected presentation defects during its own run. No separate designer
correction run was required after independent review. The temporary effort setting
is now restored to the prior `high` baseline; specialized instructions and skill
assignments remain. Native usage is recorded using the existing summarizer, with
cached input and reasoning components separate and no double counting of reasoning
in output. These results do not establish a causal benefit from effort or skills.

The owner selected A in this named package, including its explicit depth,
upper-wall and soffit deltas. MSQ-14 subsequently built the separate neutral
entrance and adjoining bays; MSQ-15 independently passed the identified 3D
candidate for owner walkthrough. Hidden structure, door operation, off-camera
connections, material and lighting quality remain unresolved. MSQ-12, MSQ-13 and
MSQ-15 are complete; MSQ-14 remains in review for owner 3D acceptance.
MSQ-6 remains incomplete and unassigned, and MSQ-7 remains backlog.
