# Phase 6SJ–SM — IPC, OTA, driver and regression-surface closure

日期：2026-08-10（Asia/Taipei）
基準：公開 `62aee9edce63d790dee96267f6a23660674d1e29`；裝置快照為指定研究裝置的
唯讀採樣，序號不在本輪公開報告中。
範圍：host-only 靜態分析、既有證據整理，以及一份新的唯讀裝置快照。

## Executive result

本輪新增 50 筆 normalized rows：IPC 10、OTA/recovery 14、driver caller 7、既有測試
catalog 19。結果沒有閉合新的 ordinary app/shell → trusted identity → Fire Launcher
package state、正式 HOME、driver sensitive effect、OTA partition writer 或 root chain。

這是 **Strong evidence 的 bounded negative**，不是「所有漏洞不存在」的全域證明。所有
未閉合的 holder、caller、native indirect dispatch、recovery implementation 與 user
mapping 都保留為 `UNKNOWN`。

## 新的實機唯讀證據

公開摘要：`adb/phase6sj/PHASE6SJ-DEVICE-READONLY-20260810T040720Z/public-summary.md`
摘要 SHA-256：`6ab3386919b6652a10204f9b7670b8acfcdb706e3e2f1e17b750a850ec038b01`
未編輯的完整快照保留在研究主機本地，沒有公開。

所有 17 項採樣命令回傳 0；本輪沒有開啟 device node、Binder transaction、settings/package
mutation、reboot、OTA/recovery 或 root/exploit。

| Finding | Observation | Confidence |
|---|---|---|
| HOME resolver | `com.amazon.firelauncher/.Launcher`, priority 50；三個 candidate 為 Fire 50、Microsoft 0、FallbackHome -1000 | 已證實 |
| Preferred state | Fire record `mMatch=0x100000`, `mAlways=true`；selected set 包含 Fire/Microsoft/FallbackHome | 已證實 |
| Foreground | `mResumedActivity` 與 `mCurrentFocus` 均為 Fire Launcher | 已證實 |
| Package state | User 0 Fire `enabled=0`（default）；現況 User 10 `enabled=2`，只作觀察，不推導本輪來源 | 已證實（現況） |
| Security | SELinux Enforcing；shell 為 UID 2000 | 已證實 |
| Role | `dumpsys role` 無輸出；不能由此推論不存在其他 vendor role logic | 觀察到／範圍限定 |

HOME、candidate、preferred、package、activity、window 與 users 原始輸出均保存在本地
快照；公開版本只保留上述去識別摘要。完整 secure-settings 輸出含帳號識別資訊，故不
公開其原始檔或雜湊清單。

## 6SJ — IPC / permission

- **已證實：** `amazon.permission.ADD_RM_PKG_METADATA` 在 exact-build XML 宣告，raw
  `protectionLevel=0x80000002`，即 `signature|privileged`。
- **已證實：** Amazon Package Manager Binder methods 的 method-local
  `checkCallingOrSelfPermission` 會保護 remove/set flags/metadata，之後寫入
  `AmazonApplicationFlags` metadata sink。
- **待驗證：** exact holder/grant、production caller UID/signing identity、完整 service
  permission boundary。
- **已排除（bounded）：** 在保存 corpus 中沒有 `ADD_RM_PKG_METADATA → setHomeActivity`、
  preferred activity 或 enabled-state writer 的靜態 edge。
- **已證實但非 User-0 HOME writer：** KFT enabled-state path 使用 supplied `UserInfo.id`，
  因此是 child/profile-scoped writer；不能升格成 User-0 Fire Launcher bypass。

主要來源：
`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:95955-96026`、
`:96132-96136`、`:54310-54324`，以及
  `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt:1822-1824`。

  Note: the worker CSV preserved a stale `1936-1938` locator for this same hashed file;
  direct host verification corrects the locator to the actual `1822-1824` lines without
  changing the finding or its confidence.

## 6SK — OTA / recovery

- **已證實：** `OSUpdateValidator`／`SideloadVerifier` → `RecoverySystemWrapper` →
  `android.os.RecoverySystem.verifyPackage`；`SideloadInstaller` → `SideloadMover` →
  `UpdateSystem.install`。
- **已證實 capability：** updater 包含 block-image、`ota_open`/`ota_write` 與
  `WriteToPartition` 能力，且 script 指向固定 `by-name` targets。
- **待驗證：** native recovery caller、indirect dispatch、canonicalization、symlink
  semantics、exact post-OTA user delivery。
- **高可信推論：** controller permission 與 metadata/recovery gates 使其成為 protected
  lifecycle；沒有保存的 shell/ordinary-app → partition writer 呼叫鏈。
- **因風險拒絕測試：** malformed OTA、symlink/traversal payload、sideload、recovery、
  updater、reboot、partition write。

PS7331 source/image 是 adjacent-version evidence；不能把它直接宣稱為已驗證 PS7330
runtime equivalence。

## 6SL — MediaTek/Amazon driver caller

`/dev/mtk_cmdq`、`/dev/ion`、`/proc/perfmgr/perf_ioctl`、`/proc/m4u`、RPMB、IDME、
Amazon diagnostics 七個 target 全部為 `UNKNOWN`。每一列至少缺 exact shipped native
open/ioctl/proc caller，部分另缺 shipped node或完整 policy join。

source registration、config、SELinux allow、HAL/process presence、package presence 或
0666 metadata 都不能單獨證明 shell/ordinary app 可達，更不能證明記憶體破壞或提權。

本輪沒有開啟任何 `/dev/*`、`/proc/*` node，沒有 ioctl、proc write、module load 或
diagnostic operation。

## 6SM — Existing test catalog

19 個既有測試族群已去重並分類：

- protected package/PMS/HOME、KFT child、root APK、OTA/recovery、driver、accessibility
  redirect 等已有 canonical evidence，不應因換檔名重跑。
- 只有 build fingerprint、security patch、user/profile topology、artifact corpus、
  policy marker 或自然合法 lifecycle 改變時，才有新測試前提。
- accessibility/foreground monitor 是近似 fallback，不是正式 HOME replacement。
- 安全可重產項目限於 hash/schema/path/source-to-policy/caller join；private Binder、
  driver ioctl、package setter、child creation、OTA/recovery delivery 與 root/exploit
  均列為拒絕。

## 結論與下一個最小安全目標

目前仍沒有可證明、可持久、可還原、無 Root 的正式 HOME replacement，也沒有新的低權限
權限代理鏈。最接近可用方案仍是使用者明確授權的 foreground/accessibility redirect；
它可能有延遲、閃爍、背景限制，且不會讓第三方 Launcher 成為 PackageManager 的正式
HOME 或取得 system UID。

若繼續，最低風險順序是：

1. host-only 完成 exact permission holder/grant/caller census；
2. host-only 完成 driver source/config/node/policy/native-client join；
3. host-only 完成 recovery native verifier/staging provenance。

若三條仍無法閉合低權限 caller，應把「正式 HOME replacement 目前不可行」作為研究結論，
而不是用未知 Binder、driver ioctl 或 OTA payload 補足證據。
