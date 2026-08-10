# Phase 20C — MTK/Amazon driver closure

日期：2026-08-10（Asia/Taipei）

本輪以 P19C 的 caller-gap rows 為輸入，只做 source/config/Image/ELF/DTS/init/policy 的 host-side join。沒有開 `/dev`、沒有 ioctl、沒有讀寫 proc/sysfs/debugfs、沒有載入 module、root 或實機操作。P18 已閉合的 ION generic/MTK library rows 不重做；P20C 只保留非 ION closure 或 ION 之外的 caller edge。

## 結論

新的強證據是兩條 shipped diagnostic/service caller：

1. `/vendor/bin/meta_tst` 由 `meta_init.rc` 啟動，users 為 `radio system wifi`，file context/transition 為 `meta_tst`。其 ELF 匯入 gsensor API，merged CIL 明確允許 `meta_tst → gsensor_device`；因此 AUXADC/gsensor 可提升到 `PARTIAL_STATIC_CALLER`，但 gsensor API 實際 callee、selected DTB/object、node mode 仍未閉合。
2. `/vendor/bin/meta_tst` 的 ELF 含 Android USB sysfs 路徑、open/write API 與 USB mode/ACM diagnostics；CIL 明確允許 `meta_tst` 對 `sysfs_android_usb`/`sysfs_usb_cmode` write/open。這只閉合 USB sysfs diagnostic/control caller，不等於 USBDEVFS/URB caller。

RPMB 也由 `rpmb_svc` ELF、init、file context 與 CIL 接上：ELF 含 `/dev/block/mmcblk0rpmb`、RPMB authenticated API、ioctl；`rpmb_svc.rc` 無 user line，故 init default root，`tee_exec` transition 對應 `tee` domain，CIL 對 `tee` → RPMB device/block 有 open/ioctl/read/write。仍保留 `PARTIAL_STATIC_CALLER`，因 exact native control-flow、final node mode、selected object/DTB 與 TEE authentication validation 尚未由保存資料完整證明。

CMDQ、M4U、uinput/evdev、USBDEVFS/URB、performance 與 Amazon liquid detection 仍是 `UNKNOWN`。Amazon `amzn_drv_test` 維持 bounded negative；但不能把它與實際存在的 `meta_tst` 混為同一個 driver/proc route。

## Closure matrix

| ID | Surface | Status | 最強新 join | 未閉合邊 |
|---|---|---|---|---|
| P20C-001 | CMDQ/MDP | UNKNOWN | node/context/CIL candidate allows | exact ELF opener+ioctl、selected DTB/object |
| P20C-002 | M4U | UNKNOWN | source proc + init metadata | active delivery、proc TE、writer |
| P20C-003 | uinput/evdev | UNKNOWN | source/config/type only | mode/label、TE、creator |
| P20C-004 | AUXADC/gsensor | PARTIAL_STATIC_CALLER | shipped meta_tst gsensor imports + UID/domain + CIL allow | API callee/node opener、selected DTB/object、mode |
| P20C-005 | RPMB | PARTIAL_STATIC_CALLER | shipped rpmb_svc path/API + init + tee policy | exact control-flow、node mode、DT/object、TEE validation |
| P20C-006 | USBDEVFS/URB | UNKNOWN | source/config/DTS only | native usbfs client、policy、selected controller |
| P20C-007 | USB sysfs/meta_tst | PARTIAL_STATIC_CALLER | shipped meta_tst USB paths/API + CIL write allow | exact callsite、final sysfs mode、selected DTB/object |
| P20C-008 | performance/perfmgr | UNKNOWN | proc genfs and candidate CIL edges | exact native writer/proc instance/trigger |
| P20C-009 | Amazon diagnostic/test | BOUNDED_NEGATIVE_PLUS_SHIPPED_DIAGNOSTIC | amzn_drv_test absent, meta_tst shipped separately | map meta_tst inputs to exact sink |
| P20C-010 | Amazon liquid detection | UNKNOWN | source sysfs/DTS variant only | selected DTB/object、sysfs TE、writer |

## Boundary

No row reaches PackageManager, ActivityManager, SettingsProvider, Fire Launcher, HOME replacement or privilege transition. Sinks remain sensor calibration, USB control, RPMB authenticated storage, display/DMA, IOMMU, input, performance state, or diagnostic/liquid hardware state.

`PARTIAL_STATIC_CALLER` means the shipped ELF, service identity/domain and policy edge are materially joined, but one or more exact device/object/DTB/control-flow edges remain absent. `BOUNDED_NEGATIVE_PLUS_SHIPPED_DIAGNOSTIC` separates the absent `amzn_drv_test` route from the present `meta_tst` service; it is not a claim that all diagnostic paths are absent.

## Evidence anchors

- P19 input: `work/luna_worker_phase19_driver_audit_20260810.csv`。
- Native ELF: `artifacts/phase9/ps7331-runtime-binary-audit-20260806-01/vendor-bin/bin/meta_tst` and `rpmb_svc`。
- Init: `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/vendor/etc/init/hw/meta_init.rc:639-641`、`vendor/etc/init/rpmb_svc.rc:1-3`。
- Context/policy: `vendor_file_contexts:15,674`、`vendor_sepolicy.cil:5467-5473,5532,5569-5572,8958,8981,9609`。
- Selected DTB/object gap: no compiled boot-selected trona DTB/DTBO or complete built-in/module manifest was found in the preserved host corpus; DTS compatibles therefore remain source-variant evidence only。

CSV 使用唯一 `P20C-*` IDs，共 10 筆；所有欄位均保留 UNKNOWN 或 partial boundary，未複製 P18 已閉合 ION rows。
