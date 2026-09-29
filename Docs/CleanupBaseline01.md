# CleanupBaseline01: Current workspace zero point

The owner designated the current workspace as the operational zero point on
2026-09-29 and requested direct cleanup without a Multica task. The exact scope
is recorded in [the owner decision](Approvals/CleanupBaseline01-OwnerScope01.json).
Future changes start from this current state; old task reports are not a request
to restore discarded candidates or execute paused work.

## Cleanup delivered

Removed 38,327 files totaling 21,930,924,343 bytes (20.42 GiB), with no deletion
failures. These were historical project package/source copies, 17 old project
snapshot ZIPs, Unreal Intermediate/DDC/autosave/crash/log files, Python bytecode,
and three task-local installed Python dependency directories. No new archive or
duplicate project checkout was created. The project now occupies approximately
60 GiB, including retained Git/LFS and service data.

The owner closed Unreal before deletion. A guarded file manifest excluded tracked
files, rejected path escapes and reparse points, and checked file sizes/timestamps.
Only selected files and their empty parent directories were removed.

The current Content, Source, Assets, Config, project/plugin binaries and tools
remain. Unique protagonist and material experiments, technical reports,
screenshots, service databases, Git history and LFS remain. Historical documents
that refer to deleted rollback payloads describe past execution; their former
backup-retention instructions are superseded by this owner cleanup decision.

## Baseline identity and verification

- Parent source commit: `cc7333faccf6dc509a64e91d7f676a77b52a5f5e`.
- Current map: `/Game/Maps/L_OpeningLobby_PainterStone01`.
- Map SHA-256: `94dbedbe2e516fc8cdde2d394f2b4c8c0a4d9573288e94772a6ebefafd54bc57`.
- At deletion verification, all 8,349 protected current/tracked/untracked files
  matched their pre-cleanup SHA-256 hashes. The source-backup follow-up verified every
  retained source against the same baseline. Every selected target is absent.
- Pre-existing owner edits and untracked source/documents remain in the working
  tree. The cleanup commit contains only this maintenance record, its decision,
  and the ProjectState update; it is not a commit of those owner edits.
- No gameplay/source logic was changed, so no build or gameplay test was needed.
  Unreal remained closed. Generated build/dependency caches may need regeneration
  when their corresponding tools are next used.

## Evidence and independent review

Exact manifests, deletion receipts and protected-file hashes are under
`Saved/CleanupBaseline01/`. The primary independent review passed the first
manifest and a bounded 56-file source-backup delta. Its unique-source findings
were closed before deletion. Controller verification satisfied unchanged hashes
and zero failures; no duplicate full review was performed.

- `delete-manifest.json`, `deleted.jsonl`, `delete-result.json`, `verification.json`.
- `delete-source-backup-delta-manifest.json`, `delete-source-backup-delta-result.json`,
  `source-backup-delta-verification.json`.
- `protected-before.json`, `footprint-after.json`, `review/primary-review.md`,
  `review/source-backup-delta-review.json`.

Reviewer max reasoning/standard speed was requested. Actual native settings are
not exposed by the direct-agent interface and were not falsely certified.
