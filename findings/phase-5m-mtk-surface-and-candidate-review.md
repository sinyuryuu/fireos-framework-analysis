# Phase 5M — MTK surface, public-source ABI, and candidate-root review

## Executive result

**已證實：** 公開 kernel／Android ION source 可以重建「編譯期 ABI 與控制流」的一部分。對目前裝置已拉取的 AArch64 userspace library 做離線反組譯後，`libion_mtk.so` 的多個 helper 都把 ION custom request 組成 `0xc0104906`；公開 Android ION UAPI 將這個形狀定義為 `ION_IOC_CUSTOM`（`_IOWR('I', 6, struct ion_custom_data)`）。這確認了裝置上存在標準 ION custom ABI 的 userspace 包裝層。

**不能由此推出：** `/dev/ion` 可被 shell 利用、ION driver 有任意讀寫、GhostLock 可在此 4.4.146 vendor kernel 觸發，或任何 CVE 能取得 root。這些都需要 exact PS7330 kernel／boot artifact、vendor source/config 對應及新的高風險 runtime operation；本 Phase 沒有開啟 `/dev/ion`、送 ioctl、啟動 Bluetooth/HCI、執行 exploit 或讀寫分割區。

目前最重要的結論是：Phase 5M 沒有找到一條可在現有 ADB/shell 權限下安全驗證的新 temporary-root 路徑。`/dev/ion` 的 Unix mode 看起來寬鬆，但 SELinux label、driver permission、實際 ioctl 行為及 vendor patch 仍未證實；它只能列為靜態攻擊面，不能列為可用入口。

## 1. Exact device baseline

| Field | Captured value |
|---|---|
| Serial | `G001LT0511550CFT` |
| Model / product | `KFTRWI` / `trona` |
| Build fingerprint | `Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys` |
| Android / API | Android 9 / API 28 |
| Security patch | `2024-02-01` |
| SoC / board | MediaTek MT8183 / `mt8183` |
| Kernel | `Linux 4.4.146+`, arm64 |
| Verified boot | `green` |
| Flash lock | `1` |
| SELinux | `Enforcing` |
| HOME | `com.amazon.firelauncher/.Launcher`, effective priority `50` |

The complete raw read-only collection is under
`adb/phase5/PHASE5M-RECON-20260804-01/` and the MTK surface collection is under
`adb/phase5/PHASE5M-MTK-SURFACE-20260804-01/`. Their manifests are preserved in
the [Phase 5M evidence index](phase-5m-evidence-index.md).

## 2. What was collected, and what was deliberately not done

### Read-only device collection

The collectors captured:

- `getprop`, `id`, `getenforce`, kernel version and boot security properties;
- service/process lists and bounded `/dev`, sysfs, init, binary and library
  path inventories;
- the current HOME resolver result;
- Bluetooth manager/package/process/HAL surface and package metadata;
- remote file metadata and SHA-256 for a bounded set of userspace libraries.

All collectors require an explicit serial, refuse an existing output directory,
and support `--dry-run`:

```sh
tools/scripts/capture_phase5_low_level_baseline.sh --serial G001LT0511550CFT \
  --output adb/phase5/PHASE5M-RECON-20260804-01

tools/scripts/capture_phase5m_mtk_surface_inventory.sh --serial G001LT0511550CFT \
  --output adb/phase5/PHASE5M-MTK-SURFACE-20260804-01

tools/scripts/pull_phase5m_mtk_userspace_artifacts.sh --serial G001LT0511550CFT \
  --output adb/phase5/PHASE5M-MTK-LIBS-20260804-01
```

### Host-only inspection

The new analyzer runs only `file`, `nm`, `objdump`, `strings`, and SHA-256
operations against files already pulled to the host. It never loads a shared
object as code:

```sh
python3 tools/scripts/analyze_phase5m_ion_userspace_static.py \
  --input-dir adb/phase5/PHASE5M-MTK-LIBS-20260804-01/files \
  --output artifacts/phase5/mtk-ion-static-analysis-20260804-03 --dry-run

python3 tools/scripts/analyze_phase5m_ion_userspace_static.py \
  --input-dir adb/phase5/PHASE5M-MTK-LIBS-20260804-01/files \
  --output artifacts/phase5/mtk-ion-static-analysis-20260804-03
```

### Explicitly not performed

- no `open()` of `/dev/ion`, `/dev/mtk_cmdq`, `/dev/stpbt`, or any other
  device node;
- no ioctl, HCI packet, private Binder transaction, service start/stop, or
  Bluetooth enable;
- no exploit compilation for the tablet, crash reproducer, kernel trigger,
  root attempt, BROM/DA/MTK client action, fastboot write, remount, or
  partition read/write;
- no package, setting, HOME, launcher, or user-state mutation.

## 3. MTK runtime surface

The read-only `/dev` listing showed:

| Node | Observed mode / SELinux label | Scope of conclusion |
|---|---|---|
| `/dev/ion` | `crw-rw-rw-`, `u:object_r:ion_device:s0` | A device node is listed; Unix mode alone does not bypass SELinux or driver checks |
| `/dev/mtk_cmdq` | `crw-r--r--`, `u:object_r:mtk_cmdq_device:s0` | Existing CMDQ surface; prior exact v3 compatibility probe already returned `-ENOTTY` |
| `/dev/Vcodec` / `Vcodec2` | media/system or root-only labels | Visible video surface, not a shell root result |
| `/dev/stpbt`, `/dev/stpwmt`, `/dev/wmtWifi`, `/dev/wmtdetect` | Bluetooth/system/wifi labels | Platform transport surface only; no traffic was sent |
| `/dev/sramrom` | not present in filtered snapshot | Absence is snapshot-scoped, not proof the driver is not compiled |
| `/dev/geniezone` | not present in filtered snapshot | Absence is snapshot-scoped, not proof the driver is not compiled |

The exact device is in the `u:r:shell:s0` ADB domain and remains SELinux
enforcing. Therefore the `/dev/ion` mode is not sufficient to classify it as
shell-usable. A proof would require opening it and exercising a carefully
bounded command; because ION allocation/custom ioctl paths can affect kernel
memory and DMA state, that is a new Level 3 operation, not a read-only probe.

## 4. ION userspace ABI reconstruction

### Device-side inputs

The bounded pull recorded these remote hashes:

| Remote file | SHA-256 |
|---|---|
| `/system/lib64/libion.so` | `0c7d4d9ce775124f8bc2e9f2cfac561d3a61bba3ecb17fb8f4c90da1896dbe6e` |
| `/vendor/lib64/libion_mtk.so` | `1873465ef7b68a97976af7b6bda41a41f0aa3dd3d230c71e3fc723ce43519bd8` |
| `/vendor/lib64/libion_ulit.so` | `262657c2b9cd26c151d80c5dfcc0184b9fe9c9e87666032eb6bc1401baca2a22` |

The raw `.so` files are intentionally local-only. Their hashes, metadata and
host-derived disassembly are retained; `.gitignore` prevents accidental
publication of the binary inputs.

### Static call sites

`artifacts/phase5/mtk-ion-static-analysis-20260804-03/ioctl-call-sites.tsv`
records the recovered request constants. The important subset is:

| Library | Function / callsite | Recovered request | Static interpretation |
|---|---|---:|---|
| `libion_mtk.so` | `mt_ion_open` / `0x0c0c` | `0xc0104906` | `ION_IOC_CUSTOM`-shaped request |
| `libion_mtk.so` | `ion_alloc_camera_pool` / `0x0d74` | `0xc0104906` | custom ION wrapper |
| `libion_mtk.so` | `ion_custom_ioctl` / `0x0e90` | `0xc0104906` | custom ION wrapper |
| `libion_mtk.so` | cache/DMA helpers / `0x112c`–`0x161c` | `0xc0104906` | custom ION wrapper family |
| `libion.so` | allocation/map/share/import/sync helpers | standard `ION_IOC_*` shapes | ordinary ION userspace API |

The public Android ION header defines `ION_IOC_MAGIC` as `'I'` and
`ION_IOC_CUSTOM` as `_IOWR(ION_IOC_MAGIC, 6, struct ion_custom_data)`. On the
captured 64-bit ABI, `struct ion_custom_data` has a 4-byte command field plus
an 8-byte pointer with padding, producing a 16-byte ioctl payload and the
`0xc0104906` request shape. See the [public Android ION UAPI header](https://android.googlesource.com/platform/system/core/+/ac5c122/libion/original-kernel-headers/linux/ion.h).

The public MediaTek 3.18 reference driver shows the historical custom path:
it copies `ion_custom_data` from userspace, dispatches system or multimedia
subcommands, and copies the result back. See
[`ion_drv.c` in the public MediaTek kernel tree](https://android.googlesource.com/kernel/mediatek/+/android-mtk-3.18/drivers/staging/android/ion/mtk/ion_drv.c).
That reference is useful for ABI interpretation but is not proof that the
Fire OS 4.4.146 vendor driver has the same validation or patch state.

### Static finding

**已證實：** the pulled MTK userspace library contains a standard ION custom
ioctl wrapper and several buffer/cache/DMA helper call sites.

**高可信推論：** ION is a relevant platform attack surface to audit against
the exact vendor kernel source, especially the custom subcommand structures and
handle validation.

**待驗證：** whether PS7330's ION kernel implementation has an information
disclosure, arbitrary physical mapping, DMA, or privilege-escalation defect.
The present evidence does not establish any of those conditions.

**因風險拒絕測試：** non-zero allocation, custom subcommand, physical-address,
DMA, cache-sync, malformed-structure, or repeated ioctl requests. A source
ABI match is not authorization to send them to a live kernel.

## 5. Candidate vulnerability review

The complete candidate matrix is
`output/tables/phase-5m-mtk-cve-matrix.csv`.

### SRAMROM and GenieZone

The official [MediaTek December 2021 bulletin](https://corp.mediatek.com/product-security-bulletin/December-2021)
lists CVE-2021-0904 on SRAMROM for MT8183 across Android 8.1–11 and
CVE-2021-0676 on GenieZone for MT8183 across Android 8.1–11. The bulletin's
required privilege and issue descriptions matter: this is not evidence that an
ordinary ADB shell can reach either path.

**已證實（surface-scoped）：** neither `/dev/sramrom` nor `/dev/geniezone`
appeared in the filtered read-only node inventory.

**待驗證：** exact PS7330 driver presence, node naming, patch status, and any
reachable caller. No node guess or trigger was attempted.

### Bluetooth candidates

The official [MediaTek February 2022 bulletin](https://corp.mediatek.com/product-security-bulletin/February-2022)
lists several MT8183 Bluetooth issues across Android 8.1–12, including OOB,
permission and UAF classes. The [July 2022 bulletin](https://corp.mediatek.com/product-security-bulletin/July-2022)
lists CVE-2022-21767 and CVE-2022-21768 for MT8183/Android 8.1–12. The NVD
entry for [CVE-2022-21767](https://nvd.nist.gov/vuln/detail/CVE-2022-21767)
records the MediaTek patch ID `ALPS06784430` and the affected scope.

**已證實（runtime snapshot）：** Bluetooth was OFF, the Bluetooth service was
not connected, zero crashes were reported, and no HCI node appeared in the
filtered path view. A vendor HIDL process and Bluetooth libraries exist, but
that is not an active exploit channel.

**待驗證:** exact PS7330 Bluetooth patch status and reachability.

**因風險拒絕測試:** enabling Bluetooth solely to drive malformed HCI traffic,
using private HIDL/Binder calls, or running a memory-corruption PoC. Those are
new device-state and crash-risk operations, not ordinary read-only validation.

### CMDQ and legacy `mtk-su`

The earlier exact CMDQ evidence already explains why the tested legacy route is
not a productive next step: the approved v3 compatibility request returned
`-ENOTTY`, and the direct `mtk-su` route ended with `Failed critical init step 3`
without changing UID, SELinux, HOME, or verified-boot state. The route was not
repeated in Phase 5M.

The public [mtk-easy-su project](https://github.com/JunioJsv/mtk-easy-su)
warns about post-March-2020 firmware compatibility and does not provide an
exact KFTRWI/trona/MT8183 profile. It remains historical compatibility evidence,
not a current-device exploit recommendation.

**已排除（tested route）：** repeating the same `mtk-su`/v2-CMDQ path without a
changed prerequisite.

### GhostLock and CVE-2026-43503

The [NebuSec IonStack Part II research](https://nebusec.ai/research/ionstack-part-2/)
describes GhostLock as `CVE-2026-43499` and gives a source-level rtmutex
control-flow issue. The project already calculated a bounded v4.4.146
`struct rt_mutex_waiter` layout from public source and captured config. That
does not calculate runtime kernel addresses, KASLR, physical-map locations, or
an exact PS7330 exploit target.

`CVE-2026-43503` is a separate `sk_buff` issue. The captured config gives only
partial XFRM/ESP surface information and no proof of the complete vulnerable
path. No packet trigger was run.

**高可信推論（upstream-source scope）：** unmodified upstream 4.4.146 source
overlaps the pre-fix GhostLock pattern already documented.

**待驗證（device-binary scope）：** Amazon's vendor source or binary may have
backported the fix or changed reachability. The exact PS7330 boot/vmlinux is not
available through the tested shell boundary.

**因風險拒絕測試：** compiling, pushing, triggering, or adapting either kernel
issue on this device.

## 6. Candidate decision table

| Area | Result |
|---|---|
| Public source calculation | **已證實, limited:** source/config can calculate compile-time struct/ABI facts and identify source-level vulnerable branches |
| Exact runtime exploit offsets | **待驗證 / unavailable:** exact PS7330 boot/vmlinux and complete vendor build inputs are missing |
| ION userspace surface | **已證實:** `/dev/ion` and `libion_mtk.so` custom wrappers exist; shell exploitability is not proven |
| SRAMROM / GenieZone | **待驗證:** public chipset/version scope, but no node in this snapshot and no exact PoC |
| Bluetooth CVEs | **待驗證:** external scope only; no active HCI service/node in this snapshot; no trigger run |
| Legacy CMDQ/mtk-su route | **已排除 for tested payload/path:** prior exact evidence is a failure and was not repeated |
| GhostLock | **待驗證:** upstream source overlap; exact vendor binary/backport and exploitability unknown |
| CVE-2026-43503 | **低可信假說:** partial config surface only, no trigger or exact vendor source proof |

## 7. Next safe research value

The single highest-value safe step is not another live probe. It is a complete
host-only comparison of the public Fire HD 10 source archive's exact MT8183
ION/rtmutex paths against the captured build configuration and the pulled
userspace ABI, with explicit version/hash provenance. The source archive is
build material and not a signed exact PS7330 boot artifact; it must not be used
to invent runtime offsets.

If that comparison finds a concrete, version-matched defect, the next step must
be a new operation-specific Level 3 report containing the exact trigger, expected
failure mode, data-loss/brick risk and recovery path. It must not be folded into
the prior CMDQ approval. If the comparison finds no exact defect, the low-level
root branch should be recorded as unresolved rather than repeatedly probing
generic CVEs.

## 8. Final Phase 5M verdict

**已證實：** public kernel source can calculate useful compile-time information,
and the exact device exposes an ION/MTK userspace surface that can be mapped
offline.

**已排除：** the present evidence does not justify claiming that the device is
rootable through `/dev/ion`, SRAMROM, GenieZone, Bluetooth, GhostLock,
CVE-2026-43503, or a repeated legacy CMDQ route.

**待驗證：** exact PS7330 vendor kernel patch status and any legitimate,
version-matched kernel vulnerability.

**因風險拒絕測試：** all operations that would cross from source/metadata review
into live ION/Bluetooth/kernel exploitation or boot-chain/partition access.
