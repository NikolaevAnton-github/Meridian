# KimodoLocal01 / MSQ-86: executor handoff

2026-09-20. Local tooling is installed at **`D:\devgames\Kimodo`**.
**Text generation and the full Kimodo UI remain unverified**, pending approved
Hugging Face authentication and enough free system RAM. The independent setup
is finished. No model server is left running.

## Installed candidate

| Component | Pinned version/revision |
| --- | --- |
| [Official Kimodo](https://github.com/nv-tlabs/kimodo/tree/1aece8c124d73d255ceff5086d983b844c9f4e94) | `1aece8c124d73d255ceff5086d983b844c9f4e94` |
| Official kimodo-viser fork | `7c82ad8f8640bad9dff8ded5c5eee908eeb08f11` / 1.0.16 |
| Official NVIDIA SOMA-X | `cc1f3967755f8e36d187d2e26114633dbd651cd5` / 0.3.1 |
| Portable uv / isolated Python | 0.12.17 / 3.11.13 |
| [PyTorch CUDA build](https://pytorch.org/get-started/previous-versions/#v2100) | 2.10.0+cu128 / CUDA 12.8, native `sm_120` |
| Transformers / PEFT / Gradio | 5.1.0 / 0.18.1 / 6.9.0 |
| Hugging Face Hub | 1.32.0 |
| CMake / installed MSVC toolset | 3.31.6 / VS 2022, 14.44.35207 |
| Portable Node / npm | 20.19.0 / 10.8.2 |

All three Git source trees retain their history and have clean tracked bytes.
MotionCorrection builds natively with the existing MSVC toolchain. No upstream
patch was necessary. `Build-Frontend.ps1` invokes npm/Vite through portable
`node.exe`, avoiding the upstream autobuilder's POSIX wrapper paths, and uses
the original npm lockfile. MSBuild node reuse is disabled in the process-local
environment for subsequent builds.

Reproducible script copies, the complete Python version lock and model revisions
are in `Scripts/Kimodo/`, copied into the installation root. See
[the launcher README](../Scripts/Kimodo/README.md). No environment, model, cache,
credential, generated motion or large log is added to Git.

## Models and storage

The selected checkpoint is
[NVIDIA Kimodo-SOMA-RP-v1.1](https://huggingface.co/nvidia/Kimodo-SOMA-RP-v1.1/tree/6c9233af1180b8151e3c4703477104af5dce9dd5),
under the NVIDIA Open Model License. Its 1.13 GB checkpoint and both official
LLM2Vec adapters are cached. Exact revisions and license identities are in
`Scripts/Kimodo/models.json`; downloaded files are recorded in the evidence
`models-status.json`. No restricted SMPL-X weights were installed.

The official Llama repository denied access (**HTTP 401 initially; HTTP 403 in
the latest local preparation record**). The pinned Llama revision is
`8afb486c1db24fe5011ec46dfbe5b5dccdb575c2`; downloading its approximately 16.07 GB
inference files requires owner account approval and local authentication. The
duplicate `original/` PyTorch weights are excluded. Llama has separate license
and acceptable-use terms; adapters do not remove that requirement.

Measured installation: **10,053,789,617 bytes (10.05 GB)**, including environments,
source history, frontend, public weights, logs and caches. Temporary uv package
cache was cleared using uv's own cache command. Counting the controller's
73,039,458,929-byte project baseline gives approximately **83.1 GB** combined;
the full project was not rescanned. Adding Llama remains below the 45 GB
installation cap and 250 GB combined cap. Logical file sizes conservatively
count hardlinks. The exact final breakdown is `installation-manifest.json`.

The final host reading was 5.06 GB free RAM out of 33.73 GB usable and 23,202 MiB
free GPU memory out of 32,607 MiB (RTX 5090, driver 616.92). Available RAM varied
between approximately 4 and 5 GiB. Startup requires a conservative 20 GiB free
RAM and 20 GiB free VRAM: upstream loads the large BF16 text encoder through
system memory before moving it to CUDA. This guard is not a measured minimum
for successful generation. No owner application was closed or altered.

## Focused verification

- PASS: package compatibility check; CLI help; imports of Kimodo, SOMA, the
  Llama implementation, Viser and the compiled MotionCorrection extension.
- PASS: actual RTX 5090 float32 and bfloat16 matrix multiplication; finite
  results match CPU reference within the recorded tolerances. `sm_120` is present.
- PASS: official web client builds; isolated Viser transport serves HTTP 200
  on `127.0.0.1:7861`, binds only loopback and then stops. **This is dependency
  evidence, not a loaded Kimodo UI.**
- PASS: repeated model preparation reports zero new public-weight bytes and
  retains one cache; an active workload prevents another launcher start.
- PASS: authentication/RAM guards; stop with no owned service; refusal to stop
  a foreign command's PID; cleanup of a disposable owned five-process tree.
- PENDING: full UI at `http://127.0.0.1:7860`, first text-to-motion smoke and
  successful model-server restart/stop. Upstream constructs the text encoder
  before creating the UI server (`kimodo/demo/app.py:65`).

## Owner continuation

Run `Login-HuggingFace.cmd` locally with an approved account, then
`Prepare-Models.cmd`. Never send tokens through chat. Close heavy applications
yourself until `Check-Kimodo.cmd` passes. Run `Smoke-Kimodo.cmd` for the bounded
two-second, one-sample finite-motion check. Use `Start-Kimodo.cmd` and
`Stop-Kimodo.cmd` for experiments; logs are in `logs\demo-*.log`, relative motion
exports in `outputs\`. Normal startup is offline and reuses the pinned cache.
The server has no supervisor; background persistence is best-effort.

Evidence: `Saved/AgentSetup/KimodoLocal01/Worker/`, including CUDA/import results,
CLI output, frontend/install logs, model/access records, process-safety checks,
candidate hashes and owner-file preservation hashes. Native execution arguments
verify Astra, max reasoning, standard tier and `--disable fast_mode`. Existing
owner changes to `Config/DefaultEngine.ini`, `MeridianSquad.uproject`, `AGENTS.md`
and `Docs/ProjectState.md` retain their exact pre-run SHA-256 values.

## Controller closure

The primary independent review passed the installation-only scope with no open
technical findings. `Saved/AgentSetup/KimodoLocal01/PrimaryReview01.md` preserves
the preliminary phase and final reviewed hashes. All 18 project/installation
copies match. KIMODO-R01 was a next-step filename typo in Bootstrap's final
message; the controller corrected it to the supplied `.cmd` launchers, checked
PowerShell parsing and recorded the unchanged-size delta in
`ControllerCorrection01.json`. The original worker manifest remains unchanged.
Applicable passing worker checks were reused without another runtime test run.

The controller accepts the completed independent installation under
[the task contract](Tasks/KimodoLocal01.md). Full UI, the actual model-server
lifecycle and text generation remain pending owner authentication and available
memory; installation acceptance does not establish working text-to-motion.
ProjectState records that continuation gate. Only task-scoped scripts and
documentation enter the local closure commit; owner gameplay edits are excluded.
The executor did not change Multica status/profiles, commit, dispatch successors
or operate DCC applications.
