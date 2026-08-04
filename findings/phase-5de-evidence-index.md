# Phase 5DE evidence index

## P5DE-001 — non-kernel userspace scan

- Inputs: official PS7331 source roots `platform` and `fireos`.
- Script: `tools/scripts/audit_phase5de_userspace_futex_source.py`
- Output: `artifacts/phase5/phase5de-userspace-futex-source-audit-20260804-03/summary.json`
- SHA-256: `5ad69b230ef924e06c50dd7325d391d109db4acec274413e9e12e99edc365fcd`
- Observed: kernel trees excluded; 2 files / 26 rows; 8 direct futex rows;
  zero PI and zero requeue-PI rows.
- Confidence: **Confirmed, bounded source-scan scope**

## P5DE-002 — direct ordinary futex source

- File: `fireos/fireos/external/glib/glib/gbitlock.c`
- Lines: 76, 93.
- Observed: direct `syscall(__NR_futex, ...)` with ordinary WAIT/WAKE.
- Confidence: **Confirmed, source scope**

## P5DE-003 — GLib mutex/condition source

- File: `fireos/fireos/external/glib/glib/gthread-posix.c`
- Lines: 1308-1324 and 1390-1437.
- Observed: direct ordinary WAIT/WAKE calls for mutex/condition paths; no
  requeue-PI command.
- Confidence: **Confirmed, source scope**

## P5DE-004 — build-intent boundary

- Files: `fireos/fireos/external/glib/glib/Makefile.am` lines 100-109 and
  214-216; `fireos/fireos/external/glib/gio/inotify/Android.mk` lines 16-47.
- Observed: GLib source lists the ordinary futex files and the Android module
  references GLib integration paths.
- Limitation: the referenced `glib/android.mk`, `gmodule/android.mk` and
  `antiAndroidConfig.h` are not present in the captured source roots.
- Interpretation: build intent is visible, but current-image inclusion remains
  unproven.
- Confidence: **Probable build-intent evidence; not installed-image proof**

## P5DE-005 — complete hit rows

- File: `artifacts/phase5/phase5de-userspace-futex-source-audit-20260804-03/userspace-futex-source-hits.csv`
- SHA-256: `49eecdb559588fba11f2a7744d4a455947ca6b37356b645c2f3cf2c077748339`
- Interpretation: build-input source evidence only; not proof of installed or
  executed code.
- Confidence: **Confirmed artifact scope**

## P5DE-006 — safety/reproducibility

- Script SHA-256: `7e135ee349bd22c3625c43f84c83b7b9cabba8f877e584cfe6cce4af7dbf559e`
- Output manifest SHA-256:
  `5b9bf93899acf6bfa25f305ed3e8072409b9d7a77d81b664a97b19d278db9aa0`
- Safety: source not executed, kernel not built, device not contacted, no
  futex trigger, kernel memory access, payload or address generation.
- Confidence: **Confirmed safety scope**

## P5DE-007 — GhostLock boundary

- PI/requeue-PI userspace caller in searched non-kernel source: **not observed**.
- Ordinary direct futex WAIT/WAKE source: **observed**.
- Stock runtime `waiter->task != current`: **not observed**.
- Cleanup residue/memory effect/root: **not established**.
