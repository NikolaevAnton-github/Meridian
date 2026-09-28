# Demo tiled column authoring archive

DemoColumnCheckpoint01, 2026-09-28. Exact copies of the authoring inputs and
scripts previously held under `Saved/DemoTiledColumn01/`. The source-copy hash
comparison is retained at `Saved/DemoColumnCheckpoint01/source-archive.json`.

The current placed actor is Correction04. Earlier experiment packages and their
sources remain preserved; their inclusion does not promote them over Correction04.
Unreal packages are tracked with Git LFS under `Content/Experiments/DemoTiledColumn01/`.

Authoring sequence, for reference only:

1. Root `generate_tiles.py`, `tiles.json`, `create_experiment.py`: initial experiment.
2. Correction02 `generate.py`, `cladding.json`, `place.py`, `finalize.py`: separate
   cladding and material setup.
3. Correction03 `place.py`: native `BakeDemoColumnScale()` and scale-one placement.
4. Correction04 `generate.py`, `cladding.json`, `place.py`: varied cladding layout.

Scripts are archived unchanged. Several contain fixed Saved paths and mutate
assets/the lobby. Native authoring also validates those Saved source paths.
Do not rerun placement scripts against the current level to inspect this archive.
For a deliberately authorized rebuild, first prepare the corresponding Saved
workspace and inspect each script's preconditions. Correction04's generator
writes adjacent `cladding.json`; use a scratch copy to preserve these exact bytes.

The native authoring implementation is `Source/MeridianSquad/NGDColumnAuthoring.cpp`;
runtime behavior is in `DemoColumnCladding.cpp`, `DemoColumnScatter.cpp`, and the
NGD/projectile adapters. This checkpoint changes none of their behavior.
