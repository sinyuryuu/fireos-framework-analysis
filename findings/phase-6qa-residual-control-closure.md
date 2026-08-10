# Phase 6QA — residual IPC、Vending 與 Settings control-surface closure

日期：2026-08-10
公開基準：`d34b2909f968d20496a0929822e36586a7e8729b`（Phase 6PZ）
裝置 comparator：`G001LT0511550CFT` / `KFTRWI` / `trona` / `PS7331.4463N`

## Executive result

本輪只做 host-only 靜態分析與證據正規化，整合三個 Phase 6PZ 後續 worker：

- Play/Vending `LauncherConfigurationReceiver` 與 `DseService`：2 rows；
- `IAmazonPackageManager` transaction 6/7：2 rows；
- Settings、PMS 與 overlay 的 HOME resource/state surface：14 rows。

合計 18 rows。**沒有新增低權限 caller → system/root identity → User-0
PackageManager、HOME、Fire Launcher 或 partition sink 的閉合鏈。** 這是目前
保存 artifacts 的 bounded conclusion，不是宣稱不存在未取得的程式碼、服務或
漏洞。

本輪沒有連接裝置，也沒有執行 Binder/service call、broadcast、settings 或
overlay mutation、APK 安裝、OTA/recovery、reboot、Root、exploit、ioctl 或
分割區操作。

## Evidence classification

### 已證實（Confirmed）

- `LauncherConfigurationReceiver` 是 exported receiver，接收
  `com.android.launcher3.action.FIRST_SCREEN_ACTIVE_INSTALLS`；其 recovered
  body 要求 `verificationToken`、比對 PendingIntent creator/current launcher，
  並檢查 setup/HOME qualification。接受後的第一個 state consumer 是 Play
  restore/hotseat/workspace bookkeeping（`aoba.k`、`aofc.y`），不是
  `replacePreferredActivity`、`setComponentEnabledSetting` 或直接啟動 Fire
  Launcher。
- `DseService` 的 exported bind surface 受
  `com.google.android.finsky.permission.DSE`、DeviceSetup flag，以及
  `Binder.getCallingUid()` 對 caller package 的 authorization helper 所限。
  recovered sinks 是 default browser/search、secure-settings eligibility、
  Setup Wizard search selector 與 install bookkeeping；沒有 Fire/HOME/root
  sink。
- `IAmazonPackageManager` tx6/tx7 的已恢復實作是 ProxyReceiver 的暫存
  PendingIntent receiver map。tx6 的關鍵接受條件是 creator package 的
  `ApplicationInfo.FLAG_SYSTEM` 與 broadcast receiver query；tx7 只允許
  creator UID 等於目前 Binder calling UID 的 owner 移除。兩條已恢復路徑都
  沒有 PackageManager enabled-state、preferred activity、HOME 或 Fire
  Launcher writer。
- Settings/Home 靜態資料中，已知相關 identifier 是 `default_home` 與
  `config_show_default_home=true`。dashboard XML 未放入 `default_home`；
  `DefaultHomePicker`/`default_home_settings.xml` 是 dormant/internal route。
  PMS 的 preferred/persistent-preferred XML 是每 user resolver state，不是
  新的 Settings provider key。
- 18-row normalized matrix 與 manifest 是由 host-only、write-once script
  產生，script 的 dry-run 宣告未接觸裝置、未 dispatch Binder、未修改設定。

### 高可信推論（Strong evidence / Probable）

- tx6/tx7 若有 production caller，仍須先提供 system-created PendingIntent、
  `FLAG_SYSTEM` creator 與正常 broadcast receiver set；現有 corpus 找不到
  production static caller。Phase 6IP 的 ordinary self-created PendingIntent
  曾被拒絕（`tx6=false`、`receiver_hits=0`），但本輪沒有重播。
- Vending DSE 的 `normal` permission metadata 不能單獨推導任意 caller 可用，
  因為 `DseService` 還有 DeviceSetup 與 calling-UID/package authorization
  邊界。
- Settings 的 `default_home` controller 存在不等於使用者可由正常 dashboard
  進入 picker；現有 Phase 6FO/6DI runtime evidence 已顯示普通 exported route
  未暴露可取代 Fire 的 HOME selector。
- 本輪結果維持 Phase 6PZ：Fire 的 User-0 formal HOME、protected-package
  membership 與既有 preferred-vs-priority 行為沒有被新證據推翻；child Tahoe
  和 Accessibility/ADB foreground redirect 仍分別是 per-user 與暫時替代。

### 待驗證（Hypothesis / bounded unknown）

- `IAmazonPackageManager` tx6/tx7 的完整 production caller universe 仍不完整；
  目前找到的是 generated Stub/Proxy、BinderService implementation 與
  Phase 6IP test-only caller。
- `DseService` JADX `g()` 有 duplicated-block/decompiler warning；exact
  smali branch equivalence 與後續 `aofc.y`/injected writer 的完整資料流仍需
  host-only artifact 才能再縮小。
- `LauncherConfigurationReceiver` 的合法 sender provenance 及 Play restore
  bookkeeping downstream 未全部恢復；目前沒有證據把它升級為 HOME writer。
- dormant `DefaultHomePicker` 在其他未保存的入口是否可達，仍是 artifact/UI
  route 問題，不是已確認 shell-writable HOME state。

### 已排除（Disproved within reviewed scope）

- 本輪三組來源沒有證明新的 ordinary-app／ADB-shell → system identity →
  Fire Launcher disable、User-0 HOME replacement 或 root route。
- tx6/tx7 的 recovered first consumers 不是 PackageManager preferred/state
  writer；不能把 ProxyReceiver 的 PendingIntent forwarding 誤稱為 HOME
  selection。
- Vending `LauncherConfigurationReceiver` 的 recovered path 不是任意廣播
  即可觸發的 Fire Launcher replacement；缺 token/current-launcher/setup
  qualification 會提前返回或拒絕。
- Settings 靜態搜尋沒有找到新的 shell-readable HOME key、HOME-specific
  mutable overlay 或 dashboard-exposed default-home writer。

### 因風險拒絕測試（Risk-rejected）

- 不猜測或重播 `IAmazonPackageManager` private transaction payload。
- 不直接 bind/call Vending DSE、送 `FIRST_SCREEN_ACTIVE_INSTALLS` broadcast，
  也不製作偽造 verification token/PendingIntent。
- 不切換 overlay、不寫 Settings/DeviceConfig/AppOps、不觸碰 PMS XML，且不
  安裝 APK 或建立 user/profile。
- 不停用、hide、suspend、uninstall 或 clear Fire Launcher；不執行 Root、
  OTA/recovery、reboot、driver ioctl 或 partition operation。

## 1. Vending residuals

### LauncherConfigurationReceiver

Manifest evidence 位於：
`artifacts/phase6mb-vending-static-20260810-01/manifest-print.txt:1470-1479`。
receiver exported 且沒有 manifest permission，但 recovered body
`artifacts/phase6ps-vending-receiver-20260810-01/LauncherConfigurationReceiver.java:43-369`
的第一個控制邊界不是 caller UID，而是 `verificationToken` PendingIntent。
接著它比對 creator/current launcher，並依 setup state 與 package/launcher
qualification 決定是否消費 item arrays。第一個可見 consumer 是 Play Store
restore metadata：`aoba.k(...)` 與 `aofc.y(...)`。

在 recovered body 沒有找到：

- `com.amazon.firelauncher` literal；
- `replacePreferredActivity`；
- `setComponentEnabledSetting`；
- 直接 `MAIN + HOME` explicit launch。

因此它是 **Confirmed：launcher configuration/restore metadata surface**，不是
**Confirmed：Fire Launcher control surface**。

### DseService

Manifest evidence 位於：
`artifacts/phase6mb-vending-static-20260810-01/manifest-print.txt:1571-1581`。
service exported、要求 `com.google.android.finsky.permission.DSE`，並宣告
`com.android.vending.setup.IDseService.BIND`。recovered source
`DseService.java:655-673` 顯示 `mi()` 受 DeviceSetup flag 控制，`o()` 以
`Binder.getCallingUid()` 解析 caller packages，再交給 authorization helper。

已恢復的第一個 sinks：

| Method family | Effect | HOME/root classification |
|---|---|---|
| `f()` / `g()` | selected browser/search provider、install bookkeeping | no HOME/root evidence |
| `h()` | explicit Setup Wizard search-selector activity | no Fire/HOME writer recovered |
| `i()` | gated supplied PendingIntent return | target not a caller-selected Fire component |
| `j()` | secure-settings eligibility writer | not HOME selection |
| `t()` | `setDefaultBrowserPackageNameAsUser` | browser default, not HOME |
| `s()` | DSE install work/bookkeeping | no Fire/HOME/root sink |

`g()` 的 decompiler warning means exact branch equivalence remains partial. The
correct label is **待驗證**, not authorization bypass.

## 2. IAmazonPackageManager tx6/tx7

Declarations/Proxy/Stub：
`decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:58318-58337,402937-403180,403368-403530`。
Service publication：
`artifacts/phase6jd-fosinit-20260808-01/system/fireos/etc/init/amazonpackagemanager_fosinit.xml:9-10`。

### tx6 — registerProxyReceiver

`BinderService` delegates to `ProxyReceiver`.
`PendingIntent.getCreatorPackage()` is resolved through `getApplicationInfo(...,
128)` and accepted only when `ApplicationInfo.FLAG_SYSTEM` is present. A new
action also requires a non-empty `queryBroadcastReceivers(...)` result. Accepted
entries are stored in `mOnTheFlyRegisteredIntents`, registered through
`Context.registerReceiver`, and later delivered through `PendingIntent.send()`.

這個 sink 是 **proxy receiver map/forwarding**。在目前 slices 沒有
`clearCallingIdentity()`、preferred/HOME writer、package enabled-state mutation
或 Fire Launcher component。

### tx7 — deregisterProxyReceiver

Stored PendingIntent entries are removed only when
`PendingIntent.getCreatorUid() == Binder.getCallingUid()`. When the action map is
empty the receiver is unregistered. 這是 owner-scoped cleanup，沒有 package、HOME
或 root consumer。

目前沒有 production static caller。Generated Stub/Proxy 與 Phase 6IP test-only
probe 不能被誤記成量產 caller。Phase 6IP 的 ordinary-app negative result 是
runtime boundary evidence，不是本輪重新測試。

## 3. Settings / PMS / overlay boundary

Exact-build static inputs found only the following HOME-shaped identifiers:

| Identifier / surface | Static meaning | Disposition |
|---|---|---|
| `default_home` | controller/picker key and App Info shortcut key | dormant/internal route; no new shell key |
| `config_show_default_home=true` | resource availability gate | enabled resource, but dashboard row omitted |
| `DefaultHomePicker` | internal picker can call `replacePreferredActivity()` | no saved normal exported route to it |
| `preferred-activities` | per-user PMS persisted resolver state | existing resolver state, not Settings provider |
| `persistent-preferred-activities` | per-user PMS persistent resolver state | existing state, not new control key |
| saved overlays | Phase 3C inventory: cutout/dark-theme overlays | no HOME overlay in saved enabled list |

The static presence of `replacePreferredActivity()` in a dormant picker does not
prove it is reachable from shell or that it can outrank Fire's effective priority.
Phase 6DI already captured the preferred-record/priority divergence.

## 4. Reproducibility and integrity

The normalized matrix was generated by:

```sh
python3 -m py_compile tools/scripts/build_phase6qa_residual_control_closure.py
python3 tools/scripts/build_phase6qa_residual_control_closure.py \
  --vending work/luna_worker_vending_skipped_methods_followup_20260810.csv \
  --amazonpm work/luna_worker_amazonpm_proxy_followup_20260810.csv \
  --settings work/luna_worker_settings_home_resource_followup_20260810.csv \
  --output output/tables/phase6qa-residual-control-closure.csv \
  --manifest output/tables/phase6qa-residual-control-closure.csv.manifest.json \
  --dry-run
```

The script refuses to overwrite outputs. The dry-run reports
`device_contacted=false`, `binder_or_settings_operation=false`,
`mutation=false`, `ota_or_recovery_executed=false`, and `root_or_exploit=false`.

Output matrix: 18 data rows. The manifest records input hashes, row counts and
output hash. Worker reports and CSVs remain raw inputs and are not overwritten.

## 5. Decision

Phase 6QA closes these three residual surfaces to the following bounded result:

```text
ordinary app / shell
  -X→ tx6/tx7 → ProxyReceiver → PendingIntent forwarding only
  -X→ Vending launcher restore → Play metadata only
  -X→ DSE → browser/search/secure-settings/install only
  -X→ Settings HOME key → no new shell-writable HOME state
```

The remaining safe research value is host-only recovery of the exact missing
caller/source branches. No current row justifies a device mutation. A future
candidate must show, in one evidence chain, a low-privilege caller, an accepted
authorization boundary, a system/root identity transition, and a package/HOME/root
sink before any reversible device test is reconsidered.

## Source evidence IDs

See `findings/phase-6qa-evidence-index.md` for hashes and row-level references.
