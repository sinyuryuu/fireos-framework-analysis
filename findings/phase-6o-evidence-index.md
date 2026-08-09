# Phase 6O evidence index

| Evidence ID | Source and location | Observation | Confidence |
|---|---|---|---|
| 6O-KFT-001 | `artifacts/phase6ay/launcher-state-services-20260805-02/launcher-state-service-methods.csv:54297-54325`; selected snippets same range | Private KFT helper writes Tahoe/Fire/Launcher3 state for a supplied user | Confirmed (static) |
| 6O-KFT-002 | `artifacts/phase6ay/launcher-state-services-20260805-02/selected-method-snippets.txt:55053-55105` | Internal boot/user lifecycle can reach setup/KFT helpers; no transaction was sent | Strong evidence |
| 6O-USER-001 | `adb/phase6gr/PHASE6GR-GUI-SYSTEMUI-SWITCH-20260807-07/result.json` | User 10 Tahoe HOME and User 0 Fire HOME are separate; rollback succeeded | Confirmed (runtime) |
| 6O-OTA-001 | `artifacts/phase6bp/ota-manifest-20260805-01/META-INF/com/google/android/updater-script:1-25` | Fixed system/vendor block targets and fixed boot/firmware targets; no dynamic post-install operation marker | Confirmed (static) |
| 6O-OTA-002 | `artifacts/phase6bp/ota-path-audit-20260805-02/ota-path-audit.json` | No archive traversal/symlink/duplicate path and no post-install executor in preserved audit | Strong evidence |
| 6O-OTA-003 | `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/011_com.amazon.device.software.ota__0_DeviceSoftwareOTA.xmltree.txt:12-37,114-164` | OTA controller is signature|privileged; service/control receivers are single-user and gated | Confirmed (static) |
| 6O-OTA-004 | `artifacts/phase6bk/protected-broadcast-union-20260810-02/protected-broadcast-inventory.csv` | OTA lifecycle actions are system-protected broadcasts | Confirmed (static) |

## Input hashes

The canonical input hash manifest is [input-sha256.json](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/artifacts/phase6o/control-boundary-20260810-01/input-sha256.json).

Generated bundle hashes are preserved in [sha256sums.txt](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/artifacts/phase6o/control-boundary-20260810-01/sha256sums.txt).
