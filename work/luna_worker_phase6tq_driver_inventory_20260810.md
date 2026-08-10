# Phase 6TQ — PS7331 GPL source / exact-build shipped image driver inventory

日期：2026-08-10；範圍：host-only static inventory。目標為 KFTRWI/trona、MT8183、Android 9、kernel 4.4.146+、PS7331.4463N。CSV 是逐項可機讀索引。

## 結論

已確認 source-level 的 Amazon 與 MediaTek userspace surfaces，包括 Amazon IDME、logger、sign-of-life、driver-test、keycombo，及 MTK GED、CMDQ、ION、M4U、MDP、USB-C/TCPC、input、RPMB。Exact shipped `boot.img`/ `Image` 也有 MTK M4U、GED 參數、Amazon device-tree marker 與 kernel 版本字串；Phase 6FU 另已確認 boot provenance 中的 CMDQ/config marker。

但「source registration → shipped object → exact node → caller/SELinux/uevent → effect」只有部分鏈路閉合。已閉合的主要是 `/proc/idme/*` read-only、`/proc/life_cycle_reason` denied、`/dev/metrics`/`/dev/vitals` root:log 0640，以及 `/proc/ged`、`/dev/mtk_cmdq` 的既有 metadata/policy/query evidence。ION、M4U、MDP、TCPC、input、RPMB、debugfs 與 Amazon `amzn_drv_test` 保留 UNKNOWN；source 不是 shipped/caller proof。

沒有任何 driver 路徑在本 inventory 中連到 PackageManager、ActivityManager、ActivityTaskManager、HOME resolver 或 Fire Launcher writer。因此未建立 root、LPE、launcher effect 或 privilege transition。所有 effect 判定僅到 source/data-flow 邊界；不把可見 node 或 `copy_from_user()` 誇大成 vulnerability。

## Evidence / integrity

- GPL source root：`firmware/extracted/PS7331-SOURCE-20250617/platform/`。
- exact `boot.img` SHA-256：`cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b`。
- unpacked `boot_unpacked/Image` SHA-256：`10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d`；strings offsets：13004815 kernel version、13566552 M4U、13724536+ GED parameters。
- Phase 6N read-only captures：`logger_modes.stdout.txt` SHA-256 `5c5fa2ed958cbe6019d665c5ee71c74d13c30f272a71f2a6a0f7e157c53b6001`、`amazon_proc_modes.stdout.txt` `c4fbc91d404888cadeab52455ef571504e04668b7ad7e89b945343399f03d86f`、`debugfs_nodes.stdout.txt` `f5141ee05bd1a1c85f16821b0fbb7d715e269256a1d87ee1ec57a8a03f59b3fb`。
- 對照：`findings/phase-6n-kernel-surface-index.md`、`findings/phase-6br-amazon-kernel-user-surfaces.md`、`findings/phase-6is-selinux-driver-route-closure.md`、`findings/phase-6np-ion-and-control-surface-closure.md`、`findings/phase-6fu-cmdq-kernel-provenance.md`、`findings/phase-9-ps7331-reference-porting-boundary.md`。

`drivers/amazon` 在 GPL tree 中不存在；實際 Amazon source 是 `platform/device/amazon/kernel/driver`。這是 ABSENT path distinction，不是 Amazon driver absent 的推論。

## Scope highlights

### Amazon

- `amzn_idme.c:62,316-347` 建立 `/proc/idme/*`，並在 child creation 前移除 write bits；`mac_sec` 有 owner/mode restriction。
- `amzn_logger.c:696-738` 只提供 logger read/poll/release，misc register 建立 `metrics`/`vitals`；exact runtime node 是 `root:log 0640`。本輪不讀取，避免消費 ring buffer。
- `amzn_sign_of_life.c:255-265` 是 read-only lifecycle proc；exported RTC setters 是 kernel-internal，不是 shell setter。runtime read denied。
- `amzn_drv_test.c:784-866` 有 `/proc/amzn_drvs/*` write dispatcher 與 `module_init`；Phase 6NP 指出 built-in image marker 不成立，故 shipped status 保留 UNKNOWN。禁止寫入。
- `amzn_keycombo.c:116-300` 是 device-tree/input triggered panic/orderly reboot surface；不是 userspace char/proc/ioctl route。

### MediaTek / selected surfaces

- GED：`ged_main.c:271-344,411,521` 有 `/proc/ged` unlocked ioctl/compat 與 mode 0644；既有 query-only evidence 僅證 telemetry/query。
- CMDQ：`cmdq_driver.c:735-741,816-824,864-896,1081` 有 `/dev/mtk_cmdq`、proc debug files、sysfs attrs、ioctl/init。Phase 6N/6IS 的 node label/mode 對照存在；count/length arithmetic 仍是 host-only UNKNOWN。
- ION：`ion.c:1478-1617,1657-1658,1920-1924` 與 `ion_drv.c:689-736,856` 形成 ioctl/device/debugfs source surface；Phase 6NP 沒有 node open/ioctl。
- M4U/MDP：均為 DMA/display/memory translation/readback surfaces；source registration 存在，但 exact node、SELinux caller 與 effect 未完整閉合。
- USB-C/TCPC：`tcpci_core.c:46-66,864-884` 有部分 0664 sysfs attrs；只表示 source writer，不能推導 shell write。
- input/RPMB：含 ioctl/debugfs/input 或 secure-storage registration；均無 HOME/PMS edge，exact caller/policy 未閉合。

## Phase 9 binary/node cross-check

Phase 9 的安全 reference boundary 只允許 source/ABI/provenance transfer，不允許把 Qualcomm reference payload、地址、gadget 或 runtime exploit material 套到 PS7331。對本輪而言，`boot.img`/`Image` 的版本與 strings 只支持「PS7331 kernel family / selected markers plausibly shipped」；Phase 6N/6BR/6IS/6NP 的 node/policy evidence 才能支持 exact node claims。

因此：`source registration` → `Image marker` 可在 GED/M4U/Amazon DT marker/CMDQ provenance 部分成立；`Image marker` → `exact node` 只有既有 Phase 6N/6BR/6IS evidence 對 selected nodes 成立；`node` → `caller/policy/effect` 不可對 UNKNOWN surfaces 補推。未取得的 symbol table、module list、uevent rule、完整 vendor policy 與 exact driver object provenance 均保留 UNKNOWN。

## Safety boundary and minimum safe follow-up

本輪沒有 ADB、binary execution、device-node open、driver open/ioctl、Binder、root、exploit、proc/sysfs/debugfs write、module load、reboot、partition access 或 payload。

最小安全後續僅限：取得新的 exact-build host artifact 後，重新 hash 並比對 config、Image symbols/strings、vendor file_contexts/SELinux allow、init/uevent declarations 與 read-only node metadata。若缺任何一段，維持 UNKNOWN；不以裝置 payload 補洞。

優先順序：

1. 補 `amzn_drv_test` 的 exact config/object/file-context closure，但不寫 `/proc/amzn_drvs`。
2. 對 ION/M4U/MDP/TCPC/input/RPMB 取得同一 build 的 node metadata + policy provenance；仍只做 host-side diff。
3. 保留 CMDQ/GED/debugfs 為 no-execution items；只有隔離、可復原 lab 且有明確安全測試契約時才另行評估，與本 Phase 6TQ 無關。

## Deliverable

本輪只新增：
- `work/luna_worker_phase6tq_driver_inventory_20260810.md`
- `work/luna_worker_phase6tq_driver_inventory_20260810.csv`

