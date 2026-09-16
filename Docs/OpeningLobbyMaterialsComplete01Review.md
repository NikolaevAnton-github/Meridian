# Complete opaque lobby materials and stone slabs: Review02

LobbyMaterials-Complete01/SlabLayout01 passed fresh MSQ-29/Review02 for the current
opaque-material scope. Visual and technical verdicts are PASS: nine included
criteria passed, with no required correction or critical unverified requirement.
Criterion 6 and R1, entrance glazing, remain **DEFERRED_BY_OWNER**, not passed or
accepted. The batch is ready for owner viewing; resulting material bytes and final
architecture/atmosphere/performance have not been owner accepted.

## Exact reviewed package

- Candidate: `LobbyMaterials-Complete01/SlabLayout01`; 891 unique manifest entries.
- [Manifest](../Saved/OpeningLobby/MaterialsComplete01/Worker/SlabLayout01/manifest.json), SHA-256 `9f2c11c022817c871e8215c9eb95abb1664ad78fa4c28bc94391b66de70abdff`.
- Current sole map: `/Game/Maps/L_OpeningLobby_PainterStone01`.
- Map SHA-256: `c94331250d378e950ac7780c20bfee0e10145990fb28ac300b38c42477b0b62a`.
- [Independent verdict](../Saved/OpeningLobby/MaterialsComplete01/Review02/verdict.json), SHA-256 `8025a808761072432b0fc4d8b25623d65b72633806e0963c73f63c2975b41e38`.
- [Independent report](../Saved/OpeningLobby/MaterialsComplete01/Review02/report.md)
  and [first look](../Saved/OpeningLobby/MaterialsComplete01/Review02/first-look.md).
- [Author report](OpeningLobbyStoneSlabs01.md),
  [stone direction](Approvals/LobbyMaterialsComplete01-StoneSlabs01.json) and
  [glass deferral](Approvals/LobbyMaterialsComplete01-GlazingDeferred01.json).

All 44 stone components use large-format slab variants with the accepted column
gloss. Working module is 120 x 240 cm, joint width 5 mm and normal recess 0.75 mm;
these dimensions are a controller choice under the owner's large-slab instruction.
New native Unreal graph math reuses accepted Painter textures without rewriting
them. Trim and return roles use scheduled cut pieces.

Complete coverage is 107 lobby components: 101 opaque and six retained glass,
plus one separately inventoried neutral support mesh. Exactly 44 stone bindings
changed versus Correction03. All 63 nonstone assignments, 13 accepted floor/metal
bindings, owner geometry, collision, gameplay, light/exposure, glass/support and
other scene properties remain exact. Accepted native sources and 2,401 entries
across seven predecessor manifests were verified through exact archives.

Matched native evidence includes 36 frames, 16 final, at 1920 x 1080 / HFOV90 /
standing height. The resumed live scene and native graph readback matched the
saved final evidence. The sole current map is clean and PIE is off.

Useful views: [column corner](../Saved/OpeningLobby/MaterialsComplete01/Worker/SlabLayout01/Final/column-corner-90.png),
[broad wall](../Saved/OpeningLobby/MaterialsComplete01/Worker/SlabLayout01/Final/broad-wall-90.png),
[hall](../Saved/OpeningLobby/MaterialsComplete01/Worker/SlabLayout01/Final/whole-hall-90.png).

## Limits and preserved exceptions

Strong existing-light highlights and dark undersides remain; final atmosphere is
outside this pass. The joint recess is a normal effect, without silhouette depth.
No new temporal anti-shimmer or performance benchmark is claimed. The original
quiet-wall R2 target was superseded by the owner's column-gloss choice.
Fixed-axis trim origin endcaps can shade as grout if exposed; scheduled current
endcaps meet adjacent geometry. Recheck endcaps before using these trim instances
in a different exposed assembly.

Original failed preservation reports and hashes remain intact. Exact two
controller-helper changes, polling logs and the verified Multica instruction
suffix are documented administrative exceptions. Global config's old hash did
not match the resumed current file; exact old bytes could not be recovered.
The independent comparison found unrelated project trust and isolated-runtime
differences, without a model/provider/billing delta. Current global config was
preserved, and historical byte equality is explicitly unverified. See
[the scoped exception](../Saved/OpeningLobby/MaterialsComplete01/Controller/global-config-resume01-exception.json).
This is separate from exact candidate/source/property/history preservation.

Author storage measured approximately 2.286 GB lobby and 440.05 MB total batch
growth, within the 2.4 GB / 450 MB plans and 250 GB project cap. Slab growth of
92.30 MB exceeded the advisory 80 MB aim. No user assets or history were deleted.

MSQ-28 remains in review for the owner's direction decision; MSQ-29 is done.
Glass is a separate deferred backlog task; MSQ-7 atmosphere remains backlog.
Environment Artist and Visual Reviewer profiles, original instructions and task
arguments are restored to Astra/high/standard. No run remains active.
