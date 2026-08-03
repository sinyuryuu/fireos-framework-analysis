# Phase 5Y evidence index

Canonical test ID: `PHASE5X-ROUTE-SURFACE-20260804-06`

Serial: `G001LT0511550CFT`

Capture window: `2026-08-03T19:30Z` UTC
Mode: metadata-only and access-check-only

| Evidence ID | Command / source | File | SHA-256 | Observation | Interpretation | Confidence |
|---|---|---|---|---|---|---|
| `P5Y-DEVICE-001` | `adb shell ls -lZ /dev/aed0 /dev/aed1 /dev/atf_log /sys/class/misc/aed0 /sys/class/misc/aed1` | `aee_nodes.stdout.txt` | `ac6e43ec97a228127bcc65df2ceba199ef2a141907de15913654140370fc2e5e` | `aed0/aed1` are root-only `aed_device`; `atf_log` is root-only | AEE/AED and secure-log node surfaces exist | 已證實，runtime metadata scope |
| `P5Y-DEVICE-002` | shell `test -r` / `test -w` access checks | `aee_access.stdout.txt` | `d0d5f507b8c4919b71299ebdc6ae308bce7e764a64dc1811b7ccb01583f148ed` | All three nodes report `read=0 write=0` | Ordinary shell cannot use the normal POSIX access path | 已證實，access-check scope |
| `P5Y-DEVICE-003` | `ps`, `pm list packages`, `service list`, init enumeration | Phase 5X-06 corresponding raw files | Hashes in `adb/phase5/PHASE5X-ROUTE-SURFACE-20260804-06/sha256sums.txt` | No userspace AEE daemon/package/service/init endpoint observed | Node presence is not proof of daemon reachability | Strong evidence, runtime scope |
| `P5Y-DEVICE-004` | HOME and identity read-only checks | `home.stdout.txt`, `identity.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6`; `7bb4a293663f02c546ed9222fac711bbc22aa451bbfdada564d7019e8e4daff8` | HOME remains Fire Launcher; caller remains UID 2000 shell | Follow-up did not alter device state | 已證實 |
| `P5Y-SOURCE-001` | Exact Fire MT8183 defconfig | `artifacts/phase5/exact-kernel-source-review-20260804-01/members/mt8183_defconfig.e1495a4e51db.txt:1611-1615` | Existing artifact manifest | `CONFIG_MTK_AEE_FEATURE/AED/IPANIC/MRDUMP=y` | AEE kernel family is enabled in source/config | 已證實，source/config scope |
| `P5Y-WEB-001` | MediaTek December 2025 bulletin | [official bulletin](https://corp.mediatek.com/product-security-bulletin/December-2025) | Web source | `CVE-2025-20765`: AEE daemon double-free/race, MT8183 | External scope; no exact PS7330 patch or PoC | Strong evidence, external scope |
| `P5Y-HOST-001` | Host-only generator | `artifacts/phase5/public-route-review-20260804-03/candidate-matrix.csv` | `cde6e3a251c885e06c79f6d7535ebe041e489108e1b4092017e03629b7c5ab82` | Matrix now records AEE nodes and shell access result | Reproducible route classification | 已證實 |
| `P5Y-SAFE-001` | Collector result and hash manifest | `adb/phase5/PHASE5X-ROUTE-SURFACE-20260804-06/result.md`, `sha256sums.txt` | Manifest verified with `shasum -a 256 -c` | No node open, exploit, reboot, write or package/settings mutation | Safety boundary held | 已證實 |

## Explicit non-findings

The evidence does **not** establish:

- that `CVE-2025-20765` is unpatched in PS7330;
- that `/dev/aed0` or `/dev/aed1` has a useful ioctl for shell;
- that a userspace AEE daemon is installed, running, or exported;
- that a kernel crash or AEE race would produce root;
- that any bootloader, partition or Launcher mutation is justified.
