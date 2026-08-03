# Phase 5B — Root failure boundary and next-route matrix

## Scope

This note records what was learned after the approved `mtk-easy-su` Root-control
test failed. It does not repeat the APK test, execute another exploit, or
select a generic MTK payload for the tablet.

Device: `KFTRWI` / `trona`, MT8183, Fire OS 7.3.3.0,
`PS7330.4104N`, Android 9/API 28, security patch `2024-02-01`.

The new read-only baseline is:

`adb/phase5/PHASE5-LOWLEVEL-BASELINE-20260803-02/`

Its SHA-256 manifest was verified from the repository root with:

```sh
shasum -a 256 -c adb/phase5/PHASE5-LOWLEVEL-BASELINE-20260803-02/sha256sums.txt
```

## Device state after the failed test

**已證實：** the tablet is still in normal Android ADB `device` state. The
HOME resolver is still `com.amazon.firelauncher/.Launcher`, the test package
`juniojsv.mtk.easy.su` is absent, SELinux is enforcing, verified boot is green,
and `ro.boot.flash.locked=1`.

The new baseline additionally records these shell-readable boot metadata:

| Property | Value | Interpretation |
|---|---|---|
| `ro.boot.pl_build_desc` | `d1a4a4b-20231011_072631` | Preloader build descriptor exposed by Android; useful identity evidence, not a loader image |
| `ro.boot.pl_version` | `0x010b` | Preloader version property |
| `ro.boot.lk_build_desc` | `79172a1-20231008_072039` | LK build descriptor |
| `ro.boot.lk_version` | `0x010a` | LK version property |
| `ro.boot.secure_cpu` | `1` | Production secure-CPU signal |
| `ro.boot.rpmb_state` | `2` | RPMB state remains enabled/initialized according to the device property |
| `ro.boot.bootreason` | `wdt_by_pass_pwk` | Boot metadata only; no claim is made about cause or exploitability |

The same bootreason was present in the earlier low-level baseline, so it is
not evidence that the Root test changed the boot chain.

## Exact Root failure boundary

### Evidence sequence

1. The verified APK installed and launched normally in the ordinary app UID.
2. The later controlled observation captured the Root-handler preflight in the
   untrusted-app SELinux domain.
3. `getprop ro.vendor.product.model` and `cat /proc/version` were denied by
   property/SELinux policy.
4. No `uid=0`, successful `su -c id`, permissive SELinux state, or successful
   `/sbin/su` check was recorded.
5. The package was removed and the device returned to its pre-test state.

The narrow conclusion is:

**已證實：** the app reached its ordinary-user preflight, but the recorded
evidence contains no successful privilege transition.

**高可信推論：** the current path fails at or before the `mtk-su` temporary
root/Magisk transition on this PS7330 build. The evidence does not identify a
single native return branch because the native process result and final UI text
were not preserved as an isolated trace.

**已排除：** the test did not disable, hide, suspend, uninstall, or clear Fire
Launcher; it did not write a system/boot partition; and it did not change the
verified-boot or flash-lock state.

## Public route matrix

| Route | Exact-device match | What the source actually supports | Decision |
|---|---|---|---|
| `mtk-easy-su` / `mtk-su` | No KFTRWI/trona/MT8183 entry; current device is 2024-02 patched and enforcing | Bootless temporary root wrapper; project warns post-March-2020 firmware may block it | **Failed on device; do not repeat blindly** |
| `amonet` | No; public README names Fire HD 8 (2018), KFKAWI | Fire HD 8/Karnak-specific MediaTek BootROM + LK chain | **Rejected as cross-device evidence** |
| Generic `mtkclient` MT8183 alias | Partial only; shared `0x6771`/`mt6771_payload.bin` entry, no Amazon preloader/DA/auth match | BROM/preloader, DA, read/write, unlock and payload operations | **Compatibility unknown; no device invocation** |
| Magisk/KernelSU boot patch | No ADB-only route; requires a suitable boot image and privileged write/boot path | Systemless/kernel-based root after boot modification | **Outside current safe scope** |
| Standard fastboot unlock | Bootloader reports `trona` but locked hardware rejects lock-state queries | Unlock/erase/flash flow | **No unlock attempt** |

The public `amonet` repository explicitly identifies its target as Fire HD 8
(2018), KFKAWI, while Amazon's device specification identifies the test tablet
as Fire HD 10 (2021), KFTRWI, MT8183, Android 9/API 28. These are not the same
device family. See the source links in the Phase 5 evidence index.

The current `mtkclient` usage documentation is also not an ADB-only root
recipe: its Android 9–12 example dumps boot/vbmeta, patches boot, changes
vbmeta verification, writes boot, and its unlock flow erases userdata/metadata
and changes `seccfg`. Those operations are outside this experiment and have no
exact PS7330 recovery plan in the workspace.

## Decision

**已證實：** the attempted APK route failed without changing the device.

**高可信推論：** no public, exact-device, non-destructive root route has been
identified for `KFTRWI`/`PS7330.4104N`.

**待驗證：** the exact preloader binary corresponding to
`d1a4a4b-20231011_072631`, BROM hardware ID, DA/SLA/DAA policy, and a complete
PS7330 recovery set.

**因風險拒絕測試：** generic BROM payloads, DA upload, preloader/LK writes,
`seccfg` changes, bootloader unlock, boot/vbmeta writes, erase/format, and
unknown root APKs.

The next technically meaningful low-level step would be a narrowly scoped
MTK identification/protocol experiment, but it is not approval-ready until an
exact loader/payload boundary and recovery plan exist. The corresponding
Level 3 report remains a proposal, not an execution record.

## Reproduction and evidence

- Root observation: `adb/phase5/MTK-EASY-SU-ROOT-T02-OBS/`
- Static payload review: `findings/phase-5-mtk-easy-su-payload-analysis.md`
- Compatibility review: `findings/phase-5-mtk-compatibility-review.md`
- Read-only baseline: `adb/phase5/PHASE5-LOWLEVEL-BASELINE-20260803-02/`
- Evidence IDs: `P5-ROOT-003`, `P5-BASE-007`, `P5-WEB-010`, `P5-WEB-011`,
  `P5-WEB-012`
