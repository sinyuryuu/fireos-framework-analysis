# Phase 6BB Report：Amazon ActivityManager prewarm IPC

## Executive summary

在 PS7331 的三份對應 VDEX 中，`preWarmApplicationForUser(String,int,int)` 是一個
真實存在的 Amazon 私有 Binder API。它由 `AmazonActivityManagerService` 提供，
透過 `amazonactivitymanager` 發布，Framework proxy 使用 transaction `1`。保存的
Alexa JADX 範圍中只有一個直接 caller。

它的可見效果是對指定 package 執行 process prewarm；目前沒有證據顯示它解析或
啟動 HOME activity、寫入 preferred activity，或提供 shell／一般 sideloaded app
可用的提權入口。

最重要的靜態異常是：server method 呼叫
`checkCallingPermission("com.amazon.permission.APP_PREWARM")` 後，緊接著
`Binder.clearCallingIdentity()`，未觀察到 permission result 的消費或拒絕分支。
這是 **授權邊界的靜態 anomaly candidate**，不是可利用性證明；shell 在已保存的
Enforcing capture 中無法取得該 service，且本階段沒有發送 Binder transaction。

## 判定表

| 問題 | 判定 |
|---|---|
| Service、proxy、wrapper 與 transaction 是否存在？ | **已證實** |
| 保存的 caller 是否為受信任 Amazon path？ | **高可信推論**：目前保存 source scope 只找到 system/priv-app Alexa caller |
| permission check 是否存在控制流異常？ | **高可信靜態推論**：result 未在 clear identity 前被消費 |
| shell 能否直接使用？ | **未證實／目前不支持**：saved AVC 顯示 service-manager find 被拒 |
| 是否有 ordinary sideloaded caller？ | **待驗證**：僅限目前保存的 Alexa source scope，不能推廣到所有 APK |
| 是否能替換 HOME？ | **已排除於此介面**：分析區段沒有 HOME/resolver/preferred 操作 |
| 是否能取得 root？ | **已排除於此證據**：沒有 Binder invocation 或 privilege transition |
| KFT 是否執行過？ | **沒有**；KFT 停用 Fire Launcher 的路徑仍只作靜態記錄 |

## 靜態呼叫鏈

```text
Alexa ExplicitIntentAction.prewarmApplicationProcess
  → AmazonActivityManagerImpl.preWarmApplicationForUser
  → IAmazonActivityManager.Stub.Proxy
  → Binder transaction 1
  → AmazonActivityManagerService.BinderService
  → checkCallingPermission(APP_PREWARM)
  → clearCallingIdentity
  → getApplicationInfo
  → PreWarmCacheHelper
  → startProcessLocked(..., "prewarm", ...)
```

### Server

`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40534`：

- `40472-40474` 載入 `com.amazon.permission.APP_PREWARM` 並呼叫
  `Context.checkCallingPermission`。
- `40474-40475` 立即呼叫 `Binder.clearCallingIdentity`。
- `40476-40503` 查詢 target `ApplicationInfo`、讀取 prewarm cache hint，並呼叫
  `startProcessLocked`。
- `40532-40534` 還原 identity、結束 trace、回傳狀態。

PS7331 OTA 對應方法在
`decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:3642543-3642624`。

### Binder transport

Framework proxy 位於
`decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:394721-394751`：

- interface token：`com.amazon.android.server.am.IAmazonActivityManager`
- payload：String + int + int
- transaction：`1`
- response：exception read + int result

PS7331 OTA proxy 位於
`decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:4464666-4464696`，
具有相同協定。

### Service registration

`artifacts/amazon-services/amazonactivitymanager_fosinit.xml:8-28` 將
`com.amazon.android.server.am.AmazonActivityManagerService` 註冊為 vendor service，
並把 `activity` manager 綁定到 `amazon.app.AmazonActivityManagerImpl`。
Framework manager 在
`boot-fosframework/disassembly.log:553272-553277` 以
`ServiceManager.getService("amazonactivitymanager")` 取得 Binder。

## Caller provenance

唯一保存 source scope 中的直接 caller 是：

`artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/sources/amazon/speech/sim/router/intentrouter/ExplicitIntentAction.java:268-282`

它：

1. 不對自身 package prewarm；
2. 需要非空的 Amazon ActivityManager 與 target；
3. 傳入 target、`0` 與 foreground profile id；
4. 只把非零結果記錄為 prewarm failure。

Alexa manifest `:143-150` 宣告 `APP_PREWARM`；保存 device package dump
`:24201-24216` 顯示其 code path 是 `/system/priv-app`，private flags 含
`PRIVILEGED`；`:24450-24456` 顯示該權限已授予。

這支持 caller 是 privileged Amazon system path，但因 source scope 不是所有 Amazon
APK 的全量證明，結論標為 **Strong evidence / scope-limited**。

## 為何不是 HOME 控制面

在已對應的 server、proxy、wrapper 及 caller 中，沒有出現：

- `ACTION_MAIN` 或 `CATEGORY_HOME`；
- `resolveActivity`、`queryIntentActivities`；
- `setHomeActivity`、`setPreferredActivity`；
- Fire Launcher package/component；
- `startHomeActivity` 或 Home-key callback。

`startProcessLocked(..., "prewarm", ...)` 只啟動／預熱 process，不能由此推導成
ActivityTaskManager 的 HOME selection。這也不能解釋 `set-home-activity` preferred
record 為何被 Fire Launcher 勝出；該問題仍由 Phase 3A–3C 的 resolver evidence
處理。

## Runtime 與風險邊界

### 已保存的 runtime evidence

Phase 6K 的 Enforcing capture 記錄 shell UID 在 `service_manager find` 上被拒，
`service check amazonactivitymanager` 也沒有提供可用 service handle。這是 shell
路徑的已知邊界，不等同於證明所有 system caller 都被拒絕。

### 明確拒絕

本階段不執行：

- `service call amazonactivitymanager 1 ...`；
- 猜測 transaction parcel、target package 或 user id；
- 透過 Alexa/OOBE/KFT lifecycle 間接觸發 prewarm；
- kill、force-stop 或停用任何 Amazon 核心服務；
- 停用、hide、suspend、解除安裝或清除 Fire Launcher。

理由是 transaction 會進入 system_server 的 process-control path，且 method 的靜態
permission anomaly 尚未有可安全驗證的 caller／recovery protocol。

## 可重現產出

- `tools/scripts/audit_phase6bb_prewarm_caller_mapping.py`
- `artifacts/phase6bb/prewarm-caller-closure-20260805-04/`
- `findings/phase-6bb-evidence-index.md`
- `output/tables/phase6bb-prewarm-caller-map.csv`
- `output/call-graphs/phase6bb-prewarm-caller-flow.md`
- `output/call-graphs/phase6bb-prewarm-caller-flow.mmd`

Artifact 的 `summary.json` 明確記錄 `device_contacted=false`、
`binder_invoked=false`、`mutation_performed=false`、`root_attempted=false`；
`sha256sums.txt` 可在 artifact 目錄內直接驗證。

## 下一步

最高價值且仍低風險的下一步是擴大已保存 Amazon APK／VDEX 的 caller inventory，
只做 method signature、interface token、permission 與 call-site mapping。除非
先取得明確、可還原的 service visibility 與 permission evidence，否則不應把
private Binder invocation 當作實機測試；本介面目前不值得作為 HOME replacement
或 root 路線繼續投入。
