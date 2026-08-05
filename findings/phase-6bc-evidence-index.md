# Phase 6BC evidence index

本索引只列公開報告可重現的證據。含裝置序號的 raw ADB snapshot 保留於本機，
未納入公開 commit。

| Evidence ID | Source / file | Observation | Confidence | Classification |
|---|---|---|---|---|
| `6BC-SRC-001` | `artifacts/phase6bc/ps7331-provenance-control-20260805-02/source-focus.csv`; official PS7331 source | MT8183/trona `futex.c`、`rtmutex.c`、`trona_defconfig` 與 build scripts 存在，focus hashes recorded | Confirmed | Host-only provenance |
| `6BC-SRC-002` | same `source-focus.csv`; extracted source scope | `platform/system/core/init/selinux.cpp` absent；framework tree 與 Fire Launcher implementation count 為 0 in scope | Confirmed, scope-limited | Source scope only |
| `6BC-SRC-003` | official source/boot/OTA manifests; existing Phase 5/6 reports | PS7331 source、boot image、OTA metadata 對應 `trona`／PS7331 | Confirmed, existing provenance | Version identity |
| `6BC-OTA-001` | `findings/phase-6y-evidence-index.md`; `SideloadMover.java:31-44` | basename-derived staging under OTA data directory | Confirmed | Static review |
| `6BC-OTA-002` | same; `FileHelper.java:61-64,305-339` | rename / copy-delete fallback and MD5 handling | Confirmed | Static review |
| `6BC-OTA-003` | `findings/phase-6j-ota-apk-deep-review.md`; `SideloadVerifier.java`, `SideloadInstaller.java`, `UpdateSystemWrapper.java` | verification and privileged install hand-off chain | Confirmed | Static review |
| `6BC-OOBE-001` | `findings/phase-6r-bootafter-system-ota-authorization.md`; `findings/phase-6k-report.md` | guarded OTA/OOBE receiver can enable priority-100 `OobeHomeActivity` and write setup state | Confirmed static | High-risk lifecycle |
| `6BC-IPC-001` | `findings/phase-6bb-report.md`; `fosservices/disassembly.log:40453-40534` | `preWarmApplicationForUser` permission check, identity clear and process-start sink | Strong evidence | Static authorization candidate |
| `6BC-IPC-002` | saved enforcing service visibility capture; `findings/phase-6bb-report.md` | shell lacks inspected Amazon private service handle | Confirmed for capture scope | No live Binder path |
| `6BC-HOME-001` | existing Phase 3A/3C and Phase 6K reports | ordinary preferred record persists but effective HOME remains Fire | Confirmed, not repeated here | Existing result |
| `6BC-FALLBACK-001` | `adb/phase6bc/PHASE6BC-REDIRECT-STATE-20260805-01/` pre-state | two research APKs present; redirect service state was visible before cleanup | Confirmed, local raw | Mutation pre-state |
| `6BC-FALLBACK-002` | same `after-rollback/` snapshot | APK paths absent, Accessibility service empty, accessibility disabled, HOME/top activity Fire, ADB connected | Confirmed, cleanup scope | Rollback result |
| `6BC-FALLBACK-003` | `findings/phase-6k-launcher-fallback-assessment.md`; `output/tables/phase6k-launcher-fallback.csv` | prior Accessibility implementation measured 0/30 reliable foreground handoffs | Confirmed for implementation/build | Workaround assessment |
| `6BC-SAFETY-001` | `artifacts/phase6bc/ps7331-provenance-control-20260805-02/summary.json` | host audit contacted no device, executed no updater, constructed no payload | Confirmed | Safety control |

## Evidence handling

- Local raw captures are append-only and were not overwritten.
- Public files contain no device serial.
- Large source/OTA archives are not copied into the Git commit.
- No conclusion in this index upgrades a static candidate to a live exploit.
