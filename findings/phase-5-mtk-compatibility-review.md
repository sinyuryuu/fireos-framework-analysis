# Phase 5 — MT8183 and low-level compatibility review

## Executive conclusion

The current evidence is insufficient to select or execute a safe MTK BROM,
preloader, DA, unlock, or exploit operation for this exact tablet. The device
is MT8183, but chipset name alone does not identify the preloader revision,
boot-ROM security state, Download Agent policy, Amazon signing requirements,
or a recoverable image set.

No low-level operation was executed.

## Current device facts

The read-only baseline reports:

- `ro.board.platform=mt8183`
- `ro.boot.hardware=mt8183`
- fingerprint `Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys`
- `ro.boot.flash.locked=1`
- `ro.boot.verifiedbootstate=green`
- `ro.boot.unlocked_kernel=false`
- `ro.boot.rpmb_state=2`
- SELinux enforcing

These facts support a locked, verified production configuration. They do not
prove that any particular vulnerability, loader, or unlock procedure applies.

## Vendor bulletin review

MediaTek's March 2022 bulletin lists several preloader USB issues affecting
MT8183, including CVE-2022-20055, CVE-2022-20056, CVE-2022-20058,
CVE-2022-20059, CVE-2022-20060, CVE-2022-20069, and CVE-2022-20073. The same
bulletin tables identify affected software families as Android 10/11/12, not
this device's Android 9-based Fire OS build. The April 2022 bulletin also lists
MT8183 in related rows. This establishes chipset/software-family relevance
only; it does not establish exploitability against PS7330.4104N.

Later bulletins checked for MT8183 entries describe other software generations
or other components. They do not provide a verified PS7330 Android 9 preloader
procedure.

## Public tool compatibility

A re-check pinned the public `mtkclient` source at commit
`0542a8729993000661e2325e838217ee754d1632`. Its BROM configuration does contain
a merged entry at source lines 1491-1495:

```text
dacode=0x6771
name="MT6771/MT8385/MT8183/MT8666"
damode=DAmodes.XFLASH
loader="mt6771_payload.bin"
```

The repository also contains `mt6771_payload.bin` (612 bytes; Git blob SHA
`70fa67c93df1c1b6fb9cc563a8825c86b0c9a0ec`), `src/stage1/targets/mt6771.h`,
and preloader files named `preloader_asus8183_adol_p030.bin` and
`preloader_fih_mt6771_64.bin`. This upgrades the result from “no public
MT8183 label” to “a public generic MT8183 alias and payload family exists.”

It still does not establish exact support for Amazon `trona`/PS7330: the
configuration groups multiple SoCs under a shared `mt6771` payload, the
preloader filenames are for other vendor/device families, and no Amazon
`trona` PS7330 preloader, DA, authentication state, or recovery set has been
matched. The source also contains both BROM/preloader paths and write-capable
operations, so simply installing or invoking it would not be a read-only
experiment.

The public tool documentation also warns that newer devices may require a
valid DA and that DAA/SLA/remote-auth conditions can block generic operation.
No exact PS7330 loader, DA, auth state, or recovery path is present in this
workspace.

## Firmware mismatch

The only extracted preloader/LK pair in the repository is from PS7331, not the
current PS7330 build:

| File | SHA-256 | Status |
|---|---|---|
| `firmware/extracted/PS7331/images/preloader.img` | `25d8d377d059ec3d5117aa4e749f4f54ef1bfbe8153ae51b309bf20d30eed904` | `VERSION_MISMATCH` |
| `firmware/extracted/PS7331/images/lk.img` | `1f52e5700058df32ffceeed3fb46d7867f8cc3463286f8177cf17dfcf80de495` | `VERSION_MISMATCH` |

Neither file is a recovery backup for the device under test. Neither was
written to the device.

## Compatibility verdict

- **已證實：** MT8183 appears in selected historical MediaTek preloader
  bulletin rows.
- **高可信推論：** those rows cannot be promoted to exact exploit support for
  this locked PS7330 Android 9 tablet because the affected software family,
  patch level, preloader revision, and auth state are not matched.
- **已證實：** the pinned public mtkclient source has a merged MT8183 alias
  under the `0x6771`/`mt6771_payload.bin` configuration.
- **已證實：** the public source contains vendor-specific 8183/6771
  preloader files, but none is identified as Amazon `trona` PS7330.
- **待驗證：** exact BROM ID, preloader build, DA/SLA/DAA state, and a complete
  signed recovery set for PS7330.
- **因風險拒絕測試：** BROM payloads, DA upload, seccfg/lock-state changes,
  preloader/LK writes, exploit attempts, and any image flashing.

The lower-risk next step, if separately approved, is a bootloader transition
followed only by read-only fastboot `getvar` queries. That step is documented,
but not executed, in `findings/phase-5-level3-approval-report.md`.
