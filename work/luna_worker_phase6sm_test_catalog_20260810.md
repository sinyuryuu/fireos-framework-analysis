# Phase 6SM — Existing Phase 5/6 test catalog and gaps

Date: 2026-08-10 (Asia/Taipei). This is a host-only catalog of evidence already
in the current worktree. No device command, Binder transaction, driver/ioctl,
OTA/recovery/updater action, root/exploit attempt, child-user operation, or
Fire Launcher state change was performed for this catalog.

The row-level ledger is [the CSV](./luna_worker_phase6sm_test_catalog_20260810.csv).
Every cited path was checked for existence. Hashes are SHA-256 values of each
row's primary report/index file; related raw directories are cited as corpus
locations and were not assigned a fabricated directory hash.

## Bottom line

Existing evidence supports a protected Fire User-0 HOME boundary and a
child/profile-scoped KFT writer. It does not close an ordinary-app or shell
route to a durable User-0 third-party HOME, Fire package-state writer, system
identity, or partition/OTA sink. The accessibility/ADB monitor is a measured
foreground fallback, not a formal HOME replacement.

## Catalog findings

- Phase 5 covers the canonical low-level baseline, protected package gates,
  non-root APK staging/rollback, futex/CMDQ/MTK source and read-only runtime
  review, and OTA/boot safety boundaries. Root, exploit, loader, partition,
  and recovery routes remain unproven or explicitly refused.
- Phase 6 covers PendingIntent smoke, KFT child lifecycle and service
  reachability, prewarm, PMS/HOME sink inventories, resolver regressions,
  accessibility redirect, child UI, driver policy, OTA/OOBE, OOBE user scope,
  updater static paths, and the current read-only runtime baseline.
- The largest duplicate family is HOME resolver/foreground/package guard
  capture. Keep one canonical run per exact build, user state, and candidate
  set; a new filename does not create a new result.
- Changed-premise triggers are: build fingerprint/security patch, current
  user/profile topology, package/artifact corpus, protected-broadcast or
  permission inventory, policy/image marker, or a natural legal lifecycle
  event. Without one of these changes, rerunning the corresponding device
  test adds little evidence.

## Missing evidence and safe next actions

The remaining gaps are provenance gaps, not authorization to probe the device:

1. Complete Amazon caller → permission/identity → user → sink mapping for the
   KFT, PMS/HOME, prewarm, DPM, and private-service candidates.
2. Join driver source/ioctl/policy to the exact retail image, native client,
   device-node access, active branch, and sensitive sink effect.
3. Close OOBE/OTA exact numeric user propagation, natural post-OTA state, and
   ordinary sender acceptance without delivering a broadcast or OTA payload.
4. Verify updater archive EOF/completeness and native return/caller closure
   from already-held files.

Safely repeatable checks are host-only: SHA-256 manifest validation, CSV/schema
validation, source-to-policy/caller/data-flow joins, report-to-raw-path
existence checks, archive EOF/provenance review, and comparison of saved
resolver/package/user snapshots. Do not repeat private Binder calls, driver
ioctl or node access, package/PMS setters, child creation or switching,
Accessibility isolation/redirect replay, OOBE/OTA/recovery/updater delivery,
or root/exploit work.

## Output integrity

The CSV contains 19 rows (excluding its header). Output SHA-256 values are
reported in the handoff message after final local validation.
