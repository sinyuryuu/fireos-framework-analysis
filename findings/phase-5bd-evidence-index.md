# Phase 5BD evidence index

| Evidence ID | File | Observation | Classification |
|---|---|---|---|
| P5BD-OTA-001 | `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/summary.json` | Official local OTA is 1,301,005,356 bytes, SHA-256 `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`, target `trona`/PS7331/API28 | 已證實 |
| P5BD-OTA-002 | `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/updater-script.txt` | Updater writes system/vendor/boot plus preloader, LK, TEE, SPMFW, SSPM and camera VPU partitions | 已證實 |
| P5BD-OTA-003 | `output/tables/phase5bd-ota-partition-risk.csv` | Partition-level host-only risk table derived from the official updater script | 已證實（metadata scope） |
| P5BD-GHOST-001 | `findings/phase-5bc-ghostlock-semantic-boundary.md`; `artifacts/phase5/ghostlock-source-semantics-20260804-01/` | PS7331 build-selected source retains the pre-fix `current->pi_blocked_on` pattern; compiled review is consistent | 高可信推論，GhostLock scope |
| P5BD-REDIRECT-001 | `adb/phase5/PHASE5BD-ACCESSIBILITY-PENDINGINTENT-T01/measure-run/measure/summary.tsv` | 30/30 samples did not show the alias package as resumed/focused | 已證實，test scope |
| P5BD-REDIRECT-002 | `adb/phase5/PHASE5BD-ACCESSIBILITY-PENDINGINTENT-T01/measure-run/logcat_after_measure.stdout.txt` | 30 PendingIntent dispatch logs; ActivityManager records Accessibility UID 10189 start requests as stopped; shell probe starts separately | 已證實，runtime observation |
| P5BD-REDIRECT-003 | `adb/phase5/PHASE5BD-ACCESSIBILITY-PENDINGINTENT-T01/restore-home-resolver.stdout.txt`; `restore-home-activities.stdout.txt` | Toggle restored off; HOME resolver and resumed activity are Fire Launcher | 已證實，rollback scope |
| P5BD-DEVICE-001 | `adb/phase5/PHASE5BD-ACCESSIBILITY-PENDINGINTENT-T01/before/`; `after/` | Before/after state snapshots preserve device identity and package/HOME state; no Fire Launcher mutation | 已證實 |
| P5BD-DEVICE-002 | `adb/phase5/PHASE5BD-DEVICE-POSTCHECK-20260804-01/` | Independent final postcheck: ADB `device`, PS7330 fingerprint, Fire Launcher priority 50 resolver and resumed activity | 已證實 |

Raw outputs are accompanied by SHA-256 manifests. No OTA, boot-chain,
partition, kernel, root, exploit, or unknown ioctl operation was performed.
