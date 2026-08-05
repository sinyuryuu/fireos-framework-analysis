# Phase 6AO evidence index

| Evidence ID | Source | Observed result | Confidence |
|---|---|---|---|
| `6AO-RO-001` | `public-summary/runtime-summary.json` plus local `metadata.json` | An explicit serial-scoped capture was online; public summary redacts the serial; shell UID 2000 | Confirmed |
| `6AO-RO-002` | `public-summary/runtime-summary.json`, `target_selinux.stdout.txt`, `target_uname.stdout.txt` | PS7331 fingerprint, SELinux Enforcing, Linux 4.4.146+ AArch64 | Confirmed |
| `6AO-RO-003` | `public-summary/home_resolve.stdout.txt` | HOME resolves to `com.amazon.firelauncher/.Launcher`, effective priority 50 | Confirmed |
| `6AO-RO-004` | `public-summary/home_candidates_cmd.stdout.txt` | Seven HOME candidates; Fire Launcher priority 50, ordinary candidates priority 0, Settings FallbackHome -1000 | Confirmed |
| `6AO-RO-005` | `public-summary/firelauncher_path.stdout.txt`, `firelauncher_package_dump.stdout.txt` | Fire Launcher is `/system/priv-app`, UID 10120, privileged, version `1.3.239105.0_89024510` | Confirmed |
| `6AO-RO-006` | `public-summary/preferred_xml.stdout.txt`, `role_dump.stderr.txt` | Preferred XML empty; Role service dump unavailable under `role` | Confirmed |
| `6AO-RO-007` | `public-summary/service_list.stdout.txt` | Amazon private service names are published, including package/activity/window/input/OOBE-adjacent surfaces | Confirmed |
| `6AO-RO-008` | `public-summary/ota_package_summary.txt`, `oobe_package_summary.txt` | OTA and OOBE are privileged system packages; OOBE exposes a priority-100 setup/Home filter in package metadata | Confirmed |
| `6AO-RO-009` | `public-summary/runtime-summary.json` command flags | No broadcast, Activity start, Binder transaction, mutation, reboot, or partition write was performed | Confirmed |

The related host-only resource provenance evidence is indexed separately in
`findings/phase-6ap-evidence-index.md` as `6AP-RSRC-001` through
`6AP-RSRC-006`.
