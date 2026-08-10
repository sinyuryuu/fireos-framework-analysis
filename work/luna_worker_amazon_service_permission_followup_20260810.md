# Amazon service permission follow-up

日期：2026-08-10

公開基準：`77c076b76`（本輪僅以 host 工作樹與已保存 evidence 比對；未連接裝置）

## 範圍與結論

本輪只搜尋 host-side decompile、既有 findings/artifacts、baseline service
inventory 與既有測試結果。沒有執行 adb、service call、Binder transaction、root/
exploit、ioctl、settings/package mutation、reboot，也沒有新增 runtime probe。
未提供任何 transaction payload。

主要結果是把三個層次分開：

1. **Permission anomaly：** ASP tablet branch 讓 `hasCallerGotPermission()` 在
   檢查 `ASP_PERMISSION` 前直接允許；AmazonActivityManager prewarm 的
   `checkCallingPermission(APP_PREWARM)` 結果在 bounded method 中未被消費。
2. **實際低權限 reachability：** shell UID 2000 對 private Amazon service 的
   service-manager `find` 在 enforcing capture 中被拒；ASP/SmartSuspend/thermal/
   fosdebug 的既有可見性只代表 service check/dumpsys 層級。既有普通 APK
   prewarm 證據只支持 process/resource effect，不等於 shell 可達。
3. **下游 effect：** 目前沒有新證據把這些表面連到 User-0 HOME、PackageManager
   preferred/component state 或 root/system sink。已知 sinks 是 ASP native audio、
   SmartSuspend settings、thermal policy、debug dump、prewarm process、PiP/window
   state、native input。

## Evidence ledger

| Surface | Static observation | Existing runtime boundary | Downstream classification |
|---|---|---|---|
| `AmazonAspService` / `audiosignalprocessor` | `hasCallerGotPermission()` returns allow on `deviceFamily == "tablet"`; otherwise checks `com.amazon.permission.ASP_PERMISSION`; command/capture/injection entries call helper (`fosservices/disassembly.log:82014-82336`) | 6BE service check/dumpsys found `audiosignalprocessor`; ASP dump produced AFE header. No method invocation or audio effect was performed. Existing 6BV log contains a permission-denial observation, but it is not a proof of every method or caller. | Static permission anomaly candidate. Actual low-privilege method reachability and native effect remain unproven; no HOME/package/root sink. |
| `SmartSuspend` | Reviewed setters check `com.amazon.permission.SMARTSUSPEND_SETTINGS`; `setEnabledInternal` writes `smartsuspend_enabled` (`fosservices/disassembly.log:99639-100014`) | Service visible and read-only dump showed `STATE_ACTIVE`; no setter was called. | Permission-gated settings sink; no anomaly or HOME/package/root chain established. |
| `amazonthermalservice` | Publication literal and manager class are present (`fosservices/disassembly.log:106979`; `artifacts/phase6aq/.../fosdebug-service-inventory.txt`) but method-level permission was not recovered in this bounded scan. | 6BE/6T read-only service check/dumpsys found the service; no method call. | Visibility-only residual. Thermal policy is a possible device-control sink, but low-privilege reachability and permission are unknown; no HOME/package/root evidence. |
| `fosdebug` | `FireOSDebugService.onStart()` publishes `fosdebug`; `dump` checks `android.permission.DUMP` and brackets vendor enumeration with identity clear/restore (`fosservices/disassembly.log:000298-00058c`). | Existing 6K/6T captures show `fosdebug` found and dumpable in the capture context. | Read-only diagnostic surface; no custom transaction method or state writer identified. |
| `AmazonActivityManager` | `preWarmApplicationForUser` calls `checkCallingPermission(APP_PREWARM)`, then clears identity before package lookup and `startProcessLocked`; permission result is not consumed in the bounded method (`fosservices/disassembly.log:40453-40534`). Focus/observer paths and PiP paths were separately reviewed. | Existing Phase 6ER/6KU evidence observed ordinary APK prewarm/process effect; shell UID 2000 service lookup was denied by SELinux/service-manager policy. | Static authorization anomaly with bounded process/resource deputy only. No HOME/package/root sink. Focus observer/PiP paths have no HOME writer in existing closure. |
| `AmazonWindowManager` | `setPipVisibility` lacks a method-local marker in bounded disassembly; `stopAppPinningMode` delegates status-bar enforcement (`fosservices/disassembly.log:56150-56183`). | Shell service lookup denied; existing 6IB/6EV closure found only PiP/window/status-bar effects. | `setPipVisibility` remains an authorization review candidate, but no low-privilege reachability or HOME/package/root effect is proven. `stopAppPinningMode` is a protected control case. |
| `AmazonInputManager` | Injection path carries caller PID/UID to native; `checkInjectEventsPermission` helper/callsite enforcement remains unresolved (`findings/phase-6mr-amazon-input-manager-static-closure.md`). | Existing 6MR/6AQ evidence records shell service-manager denial and no runtime injection. | Authorization unresolved statically; native/input effect unproven and no HOME/package/root edge. |

## Phase 6BE/6K/6PV/PW delta

- **6BE:** service visibility and ASP static branch remain the strongest permission
  anomaly candidate; SmartSuspend remains a permission-gated settings sink.
- **6K:** `fosdebug` is a dump-only surface guarded by `DUMP`; prewarm is the
  important ignored-check candidate, but its observed ordinary-app effect is only
  process/resource related.
- **6PV:** broad-route integration found no new ordinary caller → Amazon service →
  HOME/PackageManager/root chain; existing normalized evidence is reused only as a
  negative boundary.
- **6PW:** current saved read-only state still resolves User 0 HOME to Fire Launcher;
  private service lookup remains policy-bounded. No new service mutation or Binder
  replay was justified.

## Status and safe continuation

The machine-readable row-level ledger is
`work/luna_worker_amazon_service_permission_followup_20260810.csv`. Status values
distinguish static anomaly, unresolved authorization, and bounded negative sink
results; they do not claim exploitability.

The only safe continuation is host-only: map remaining interface implementations,
permission protection levels, caller provenance, and native/SELinux sink boundaries
from already-preserved files. Do not infer runtime reachability from service list or
dumpsys visibility, and do not replay private transactions or mutate settings,
package, audio, thermal, input, window, or power state.
