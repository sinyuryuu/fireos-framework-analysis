# Phase 5CY：PS7331 runtime observation boundary

日期：2026-08-04

## 結論

本輪只做 PS7331 stock device 的唯讀採集，以及一次可逆的前景恢復。沒有
呼叫 futex、建立 race、啟用 tracing、修改 settings/package、讀寫 kernel
memory、重啟、刷寫或執行 root payload。

### 已證實

- 裝置目前是 `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`、MT8183、Linux 4.4.146+、SELinux `Enforcing`、verified boot `green`。
- kernel config 有 `CONFIG_FUTEX=y`、`CONFIG_RT_MUTEXES=y`、
  `CONFIG_TRACEPOINTS=y`、`CONFIG_EVENT_TRACING=y`、`CONFIG_TRACING=y`；但
  `CONFIG_FUNCTION_TRACER`、`CONFIG_KPROBES`、debug info 與 `KALLSYMS_ALL`
  沒有提供可直接用於本輪的 production tracing 入口。
- `/sys/kernel/debug/tracing` 與 `/sys/kernel/tracing` 可見，但沒有
  `events/futex` 目錄；本輪沒有嘗試 enable 任何 event。
- `/proc/kallsyms` 對 shell denied，`/proc/kcore` 與 `/dev/kmem` 不存在，
  `perf_event_paranoid=3`。
- `system_server`、SystemUI、Microsoft Launcher、OTA process 的 status
  顯示 `Seccomp: 2`；`adbd` 是 UID 2000、`CapEff=0`、`Seccomp: 0`，不等於
  root。
- logcat 全量離線過濾 `futex|rtmutex|requeue|seccomp|SIG*` 沒有輸出，沒有
  因此宣稱「路徑不存在」。它只表示本次沒有可見的相關 runtime event。

### 目前狀態修正

唯讀 HOME snapshot 發現裝置仍處於 OOBE／研究測試殘留狀態：

- `secure:user_setup_complete=0`、`secure:device_provisioned=null`；
- HOME resolver 回傳 `com.amazon.kindle.otter.oobe/.OobeHomeActivity`；
- `org.fireosresearch.phase4.alias/.DirectBootHomeActivity` 當時在前景；
- Fire Launcher 仍位於 `/system/priv-app`，其 `enabled=0` 是 DEFAULT 狀態，
  並非停用。

我只執行了：

```text
adb -s DEVICE_SERIAL shell am start -n com.amazon.firelauncher/.Launcher
```

結果是 Fire Launcher 成為 `mResumedActivity`／`mCurrentFocus`；沒有改變
resolver、settings、package state 或資料。這個前景操作已另存為可還原的
`PHASE5CY-FOREGROUND-RESTORE-20260804-01`。

### 未觀察／不能宣稱

- 沒有同一次 kernel execution 的 `waiter->task != current` observation。
- 沒有 `remove_waiter()` 的 runtime trace、錯誤 cleanup target、residue、
  later consumer、memory effect 或 privilege transition。
- OOBE resolver 與前景 alias 不能用來支持或否定 GhostLock。

## Evidence locations

原始裝置輸出保留在本機，未把含設備識別資訊的 raw dump 自動公開：

- `adb/phase5/PHASE5CY-RUNTIME-BOUNDARY-20260804-01/`
  - `sha256sums.txt` SHA-256：`b7de1be30cca7b4bcdce3da48f976ad22bfdec036376a4df7a3c0e51b646a027`
- `adb/phase5/PHASE5CY-HOME-STATE-20260804-01/`
  - `sha256sums.txt` SHA-256：`8fddd2479cfbf74eff2e365109b134a792eed2c4edfe357100ba099c8ef367f6`
- `adb/phase5/PHASE5CY-HOME-STATE-POST-20260804-01/`
  - `sha256sums.txt` SHA-256：`d99276066da8e897429a3954c254a7076b2ff4cc72a1178c9eeb6243eff7c5f9`
- `adb/phase5/PHASE5CY-FOREGROUND-RESTORE-20260804-01/`
  - `sha256sums.txt` SHA-256：`df8f11af4c129e00c18b98955dfd85bac07eaee659992e89a7adebeb605e5d7a`

## 判定

```text
D0 source identity separation: Confirmed
D1-S source proxy-task separation: Confirmed
D1-R stock runtime identity mismatch: Unobserved
D2 wrong cleanup target: Unobserved
D3 persistent consumer: Unobserved
D4 controlled memory effect / temporary root: Unproven
```

本機 22 GiB 可用空間，沒有執行清理；原始韌體與既有 evidence 未刪除。

## 下一個合理研究環境

要取得 D1-R，stock tablet 現有 shell 觀測面不足。合理的下一步是隔離的
instrumented research kernel／emulator，只記錄 task identity、cleanup executor
與 post-cleanup invariant；不能把隔離環境結果冒充 PS7331 stock runtime，也不
應把 futex trigger 或 root payload 放入日常裝置。
