# Phase 6QB-B — Play/Vending downstream closure

日期：2026-08-10。僅整理 exact-build host artifacts；沒有接觸真機，沒有送 broadcast/Binder、bind/transact、改設定、安裝 APK、Root/OTA/reboot。

## 結論

`LauncherConfigurationReceiver` 的 recovered body 已把 JADX 跳過的主要資料流恢復到可 bounded 分析：`verificationToken` → current-launcher / Setup / package qualification → hotseat/widget/workspace/folder item metadata → `aoba.k`、`aofc.y` restore/install bookkeeping。這不是已證實的 HOME resolver、Fire Launcher package/component state 或 system identity writer；合法 sender provenance 仍 UNKNOWN。

`DseService` 的 downstream 已閉合到：DeviceSetup bind gate、Binder calling UID/package authorization、browser default、search-selector activity、secure-settings eligibility writer，以及 DSE/browser install bookkeeping。`g()` 有 JADX duplicated-block warning；exact branch equivalence、注入 writer 的 secure key/user/profile、完整 mph transaction mapping 保持 UNKNOWN。browser/default-app sink 不升格為 HOME/root；目前沒有 recovered `com.amazon.firelauncher` literal、HOME preferred writer、Fire component setter、root 或 partition sink。

## Evidence / hashes

逐列證據與 hashes 在 companion [CSV](luna_worker_vending_downstream_closure_20260810.csv)，欄位包括 method/line/offset、caller、gate、identity、sink、status、next safe step。

- Receiver：`artifacts/phase6ps-vending-receiver-20260810-01/LauncherConfigurationReceiver.java:43-369`，SHA-256 `71d17a064272f88d02f4619a2f4fa6fedf0ae91a233c29e0ad6d4110643b6b47`；manifest `manifest-print.txt:1470-1479`。
- DSE：`DseService.java:233-245,272-484,487-603,656-673,699-736`；manifest `manifest-print.txt:1571-1581`，permission declaration/use at `:26,537`。
- Binder dispatch/callers：`defpackage/mph.java:24-31,611-736,1116-1150`; static browser-default caller `defpackage/aocc.java:35`.
- APK：`base.apk` SHA-256 `a5f456832018bbf571f915e949ea9dcd707ad514c269899e916b9b25d5297a50`。

## Identity and HOME boundary

Receiver's identity gate is PendingIntent `creatorPackage`, not a recovered Binder UID check. DSE's gate is `Binder.getCallingUid()` passed to `arjs.z(...)`, after `mi()` requires the DeviceSetup feature. `t()` explicitly uses `UserHandle.myUserId()` for browser default; this does not demonstrate User-0 HOME control or cross-user mutation. Secure-settings and install/account downstream user/profile binding is UNKNOWN where dependencies are injected. No evidence permits claiming that Play/Vending changes Fire Launcher state, HOME resolver state, root identity, or OTA/partition state.

## Residuals / safe next step

Only host-only exact DEX/smali recovery remains appropriate for `mph` dispatch, `arjs` authorization provenance, `aofc.y`/`aoba.k`, `DseService.g()`, and injected secure-settings/install writers. Do not broadcast `FIRST_SCREEN_ACTIVE_INSTALLS`, create a verification PendingIntent, bind/call DSE, or perform install/settings tests.
