# Phase 6NA evidence index

| Evidence ID | Source | Command/operation | Observed result | Classification |
|---|---|---|---|---|
| 6NA-R01 | `adb/phase6mx/PHASE6MX-SERVICE-HANDLE-LOOKUP-20260810-01/probe-logcat.stdout.txt` | Start no-permission APK; reflection-only `ServiceManager.getService` | Three Amazon service handles returned `true`; UID 10011 | Confirmed |
| 6NA-R02 | `.../before-home_resolve.stdout.txt` and `.../after-rollback-home_resolve.stdout.txt` | Read-only HOME resolver snapshots | Both resolve to `com.amazon.firelauncher/.Launcher`, priority 50 | Confirmed |
| 6NA-R03 | `.../before-fire_package.stdout.txt` and `.../after-rollback-fire_package.stdout.txt` | Read-only Fire Launcher package snapshots | User 0 state unchanged | Confirmed |
| 6NA-R04 | `.../install.stdout.txt`, `.../uninstall.stdout.txt`, `.../after-rollback-test_path.stdout.txt` | Install/remove only the test APK | Install and rollback succeeded; test path absent | Confirmed |
| 6NA-R05 | `.../metadata.json`; `tools/test-launcher-phase6mx/` | Static APK design and build hash | No declared permissions or HOME filter; no transaction code | Confirmed |
| 6NA-R06 | `.../sha256sums.txt` | `sha256sum -c sha256sums.txt` | Every captured file verified | Confirmed |

No evidence in this index authorizes or supports an unknown Binder transaction,
Fire Launcher mutation, privilege escalation, or root claim.
