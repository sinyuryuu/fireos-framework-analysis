# Phase 5X evidence index

所有 Phase 5X 裝置採樣使用 serial `G001LT0511550CFT`，時間為 UTC
`2026-08-03T19:18:31Z`。原始輸出未覆寫，完整檔案與 hash 位於：

`adb/phase5/PHASE5X-ROUTE-SURFACE-20260804-03/`

## Evidence

| Evidence ID | Source / command | File | SHA-256 | Observed result | Interpretation | Confidence |
|---|---|---|---|---|---|---|
| `P5X-DEVICE-001` | `adb -s G001LT0511550CFT shell id` | `identity.stdout.txt` | `7bb4a293663f02c546ed9222fac711bbc22aa451bbfdada564d7019e8e4daff8` | UID 2000, `u:r:shell:s0` | Current caller remains ordinary shell, not system/root | 已證實，snapshot-scoped |
| `P5X-DEVICE-002` | `getprop`, `ps`, `pm list packages`, `service list`, init path enumeration | `props.stdout.txt`, `processes.stdout.txt`, `packages.stdout.txt`, `services.stdout.txt`, `init_paths.stdout.txt` | Hashes preserved in directory `sha256sums.txt` | MT8183/Android 9/PS7330; kernel AEE worker threads; no userspace AEE package/service/init match | AEE userspace endpoint not observed in normal runtime; absence is not filesystem proof | Strong evidence, runtime-scoped |
| `P5X-DEVICE-003` | `cmd package resolve-activity --brief -a MAIN -c HOME` | `home.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` | `priority=50`, `isDefault=true`, `com.amazon.firelauncher/.Launcher` | HOME state unchanged after read-only review | 已證實 |
| `P5X-DEVICE-004` | `ls -lZ /dev/sspm /dev/block/by-name/spmfw /sys/class/misc/sspm` | `node_metadata.stdout.txt` | `818a41bdbcdd5742b120059248a2608047199d8c7a049c5b44d45516b9b82cce` | `/dev/sspm` is `root:system`, `sspm_device`; `spmfw` maps to `mmcblk0p11` | Visibility/label only; no node or block read was done | 已證實，visibility-scoped |
| `P5X-DEVICE-005` | `getprop ro.apex.updatable`, APEX path listing, `cmd apexservice --help` | `apex_property.stdout.txt`, `apex_paths.stderr.txt`, `apex_help.stderr.txt` | `01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b`; `478ba717a8807832a488d32fa535071563a7e3d9edf2ddf35d03a9de536a1a4c`; `a1b098ab53a01d22fb00d3ba2fdf8bf050e43d66452a5c7cab57fb5a3ba6111b` | Property empty, APEX directories absent, `apexservice` unavailable | Android 13 APEX route not observed on this Android 9 runtime | 已證實，runtime-scoped |
| `P5X-WEB-001` | MediaTek December 2025 bulletin | [official bulletin](https://corp.mediatek.com/product-security-bulletin/December-2025) | Web source; no local file hash | `CVE-2025-20765` is AEE daemon double-free/race, MT8183; Android version not listed | External chipset scope only; does not prove exact PS7330 reachability | Strong evidence, external-scope |
| `P5X-WEB-002` | MediaTek May 2024 bulletin | [official bulletin](https://corp.mediatek.com/product-security-bulletin/May-2024) | Web source; no local file hash | `CVE-2024-20021` lists MT8183, Android 12–14 and System privilege | Version/privilege mismatch with this Android 9 shell caller | 已證實，scope-scoped |
| `P5X-WEB-003` | Public APEX advisory | [GHSA-wmcc-g67r-9962](https://github.com/metaredteam/external-disclosures/security/advisories/GHSA-wmcc-g67r-9962) | Web source; no local file hash | Demonstrated on Android 13 Lenovo Tab M10 Plus using malicious APEX update | Not an exact Android 9/Fire implementation | 已證實，scope-scoped |
| `P5X-WEB-004` | GhostLock public implementation/reference | [NebuSec IonStack Part II](https://nebusec.ai/research/ionstack-part-2/) and existing Phase 5U/5W artifacts | Existing local hashes in prior reports | Android entry is native futex PI into Linux rtmutex; target-specific layout required | Source overlap is not exploitability or root proof | 高可信推論，source-scoped |
| `P5X-WEB-005` | Candidate identifier review | [CVE-2026-3499 NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-3499) | Web source; no local file hash | Identifier does not establish GhostLock mapping | Do not use unresolved identifier to select a device action | Hypothesis / unresolved identifier |
| `P5X-PUBLIC-001` | KoCleo current public head | [commit 8c6871ac](https://github.com/KoCleo/mtk-easy-su/commit/8c6871ac7c15b8e98a47e25c35ab93b87e260475) | Web source; prior local repo metadata retained | No exact KFTRWI/trona/MT8183 profile; current README warns post-2020 firmware may block mtk-su | Same payload was already tested and failed; do not repeat | 已證實，public-source scope |
| `P5X-PUBLIC-002` | LauncherHijack current source and HELP | [commit f79aee3](https://github.com/BaronKiko/LauncherHijack/commit/f79aee3ddd10c053d6d7c55d6f2fc29436001537), [HELP.md](https://github.com/BaronKiko/LauncherHijack/blob/master/HELP.md) | Web source; prior Phase 4 raw test retained | Deprecated source; Accessibility redirect is approximate; destructive corruption route is documented | Historical reference only; destructive route rejected | 已證實，public-source scope |
| `P5X-PUBLIC-003` | Generic MTK boot-chain tool review | [mtkclient usage](https://github.com/bkerler/mtkclient/blob/main/README-USAGE.md) | Web source; no execution artifact | BROM/DA/preloader operations are pre-Android and may write/unlock | No exact PS7330 loader/DA/recovery; Level 3 boundary | 已證實，safety scope |
| `P5X-PUBLIC-004` | Bounded public Android implementation search | Existing `findings/phase-5o-android-public-poc-review.md`, `phase-5p-android-nearby-port-review.md` | Prior artifact manifests | No exact `KFTRWI/trona/MT8183/PS7330` Android implementation in recorded scope | Search absence is not global nonexistence; no new live route justified | 高可信推論，bounded-search scope |
| `P5X-HOST-001` | Host-only route matrix generator | `artifacts/phase5/public-route-review-20260804-01/candidate-matrix.csv` | `cde6e3a251c885e06c79f6d7535ebe041e489108e1b4092017e03629b7c5ab82` | Each candidate records implementation layer, exact match, privilege, runtime surface and action result | Reproducible boundary classification | 已證實，analysis-output scope |
| `P5X-HOST-002` | Existing exact defconfig / Phase 5U review | `findings/phase-5u-android-cve-applicability.md`, `P5U-MATRIX-001`, `P5U-FRAG-001` | Prior manifests | `CVE-2026-43503` is unrelated to GhostLock and its relevant config gate was not observed enabled | No live networking trigger should be added | 已證實，source/config scope |
| `P5X-SAFE-001` | Read-only capture and analyzer | `tools/scripts/capture_phase5x_route_surface.sh`, `tools/scripts/analyze_phase5x_public_routes.py`, each `result.md` and `sha256sums.txt` | Script/artifact hashes are preserved in their manifests | No device write, node open, block read, exploit or package/settings mutation | Safety boundary held | 已證實 |

## Confidence rules

- **已證實** means the exact raw output or pinned public source directly shows the
  stated fact.
- **Strong evidence** is limited to the captured runtime or official external scope;
  it is not a claim about an inaccessible binary.
- **高可信推論** is an inference from multiple scoped artifacts and must not be
  converted into a live trigger.
- **因風險拒絕測試** is recorded separately from “not vulnerable”; it means the
  proposed action crosses the project safety boundary or lacks exact recovery inputs.
