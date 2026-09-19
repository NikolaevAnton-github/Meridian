# Kimodo local experiments

Installed at `D:\devgames\Kimodo` for MSQ-86. This is the official NVIDIA
Kimodo source with an isolated native Windows environment. No Unreal integration
is installed.

**Current state:** tools, CUDA, C++ MotionCorrection, the web client, SOMA-RP-v1.1
and both LLM2Vec adapters are installed. Full Kimodo UI and text generation remain
unverified: the required Llama 3 model needs approved Hugging Face access. The
installation check also found insufficient free system RAM for a safe model load.

## First use

1. Sign in to your Hugging Face account and request/confirm access to
   [Meta-Llama-3-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct).
2. Double-click `Login-HuggingFace.cmd`. Enter your read token only at the hidden
   local prompt. Choose **No** for Git credential storage. Do not send the token
   through chat or run login under a transcript. The token stays in the local
   `cache\huggingface` directory outside the game repository.
3. Run `Prepare-Models.cmd`. This downloads the approved, pinned Llama weights
   (about 16.07 GB), using the existing cache. Access denial is reported explicitly.
4. Close other heavy applications yourself, then run `Check-Kimodo.cmd`.
   The conservative startup guard requires **20 GiB free RAM and 20 GiB free
   VRAM**. It never closes your applications. CPU text encoding is not selected
   because it would retain the large Llama model in system RAM.
5. Run `Smoke-Kimodo.cmd` once: a two-second, one-sample walking prompt, seed 42,
   20 diffusion steps. It checks the saved NPZ for nonempty finite joint data.
   This first real inference remains pending; report any error for a bounded fix.
6. Run `Start-Kimodo.cmd`, then open **http://127.0.0.1:7860** after the log says
   `Kimodo ready`. Startup runs hidden; current logs are in `logs\demo-*.log`.
   Select the retained SOMA-RP-v1.1 model, initially one sample and a short prompt.
7. Run `Stop-Kimodo.cmd` to release memory. Closing the browser does not stop the
   server. The stop command verifies PID, creation time, executable root and
   launcher command before stopping only its own process tree.

## Files and operation

- Motion saves with a relative path go to `outputs\`; the smoke produces
  `outputs\smoke-<timestamp>.npz`. The UI's Save Motion path `output` produces
  `outputs\output.npz` (or BVH when chosen). Give subsequent exports distinct names.
- Keep custom examples/exports under this installation. The upstream example
  save default is inside `source\kimodo\assets\demo\examples`.
- Source is in `source\`; dependencies' source is in `vendor\`; Python is in
  `python\`, and the environment is `.venv\`. Downloads, temporary files and
  caches stay here. Installer logs and server logs are in `logs\`.
- Normal startup is **offline** and reuses pinned models. Other model choices
  cannot silently download weights. Use only SOMA-RP-v1.1 for this setup;
  SMPL-X weights and optional model variants are not installed.
- Start/download/smoke share one workload lock. A second start reports the existing
  server or refuses while another operation is active. No encoder side service is
  started. The server binds `127.0.0.1`, with no public sharing.
- The server is a local background process without a service supervisor;
  persistence is best-effort. PID identity is recorded in `runtime\server.json`.
- The installation cap is 45 GB, including caches and outputs. Model preparation
  checks download headroom; startup leaves 1 GB below the cap. Review accumulated
  outputs/logs periodically. Nothing automatically deletes owner data.

## Reproduction and limits

`Bootstrap.ps1` uses uv 0.12.17, Python 3.11.13, PyTorch 2.10.0+cu128,
MSVC 2022 and CMake 3.31.6. `requirements.lock` records the installed dependency
versions; `models.json` pins model revisions and licenses. `Build-Frontend.ps1`
uses portable Node 20.19.0 and the official Viser npm lockfile. Its native Windows
build invocation avoids upstream's POSIX npm/npx launcher paths. No tracked
upstream files were patched. Run scripts with Windows PowerShell; `.cmd` shortcuts
set execution policy only for their process.

The dependency transport test passed HTTP 200 on loopback and then stopped;
**that was not a loaded Kimodo UI or a generation test**. Full UI startup,
successful model-server restart/stop and generated-motion validation still need
the first authenticated, memory-safe run. Optional SOMA-layer skinning, retargeting
and production animation quality are outside this installation smoke.

Project copies of these scripts: `MeridianSquad\Scripts\Kimodo`.
Evidence and exact handoff: `MeridianSquad\Docs\KimodoLocal01.md`.
Upstream: https://github.com/nv-tlabs/kimodo
