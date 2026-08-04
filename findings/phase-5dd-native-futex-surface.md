# Phase 5DD — preserved Fire native futex surface

日期：2026-08-04

本輪對 16 個已保存的 PS7331 Fire ELF 做主機端 `file`、`strings` 與 dynamic
symbol metadata scan。沒有執行任何 ELF，沒有反組譯 exploit branch、產生
kernel address/syscall argument、呼叫 futex、接觸裝置或修改系統。

## Result

| 結果 | 數量 |
|---|---:|
| named `REQUEUE_PI` marker | 0 |
| ordinary futex / PI-helper marker | 5 |
| generic syscall boundary only | 1 |
| no named marker | 10 |

完整逐 ELF 結果與 hash：

`artifacts/phase5/phase5dd-native-futex-surface-20260804-03/`

公開摘要：
`output/tables/phase5dd-native-futex-summary.csv`。

## 觀察

### Fire libc / linker

`libc` 與 `linker64` 保留：

- generic `__futex_wait_ex`；
- `__futex_pi_lock_ex` / `PIMutexTimedLock`；
- `pthread_cond`/condition-variable symbols；
- generic `syscall` surface。

但沒有 `FUTEX_WAIT_REQUEUE_PI`、`FUTEX_CMP_REQUEUE_PI` 或
`futex_*requeue_pi` 的 named marker。這與 Phase 5CR 一致：PI-lock helper
不等於 requeue-PI proxy caller。

### ART / Android runtime

`libart.so` 有：

- `futex wait failed for`；
- `timed futex wait failed for`；
- `futex cmp requeue failed for`；
- `ThreadList::SuspendAllInternal` 相關 marker；
- generic `syscall` symbol。

這些支持 ordinary ART compare-requeue 的語意映射，但沒有證明
`FUTEX_CMP_REQUEUE_PI`。`libandroid_runtime.so` 有 condition/policy setup
markers，亦沒有 named requeue-PI caller。

### Amazon native selection

本輪掃描的 `libAmazon_tat_jni.so`、`libamazon_remotes.so`、
`libamazonaspservice.so`、`libamazonmediaanalytica.so`、
`libamazonwifiservice.so`、`libbinder.so`、`libutils.so`、`libcutils.so`
中，沒有 named requeue-PI marker。`libcutils.so` 的 generic `syscall`
surface 不包含操作名稱，因此不能將它歸因為 futex caller。

## 判定

- **已證實：**保存的 Fire libc/ART/Amazon ELF 可見的 synchronization
  surface；16 個檔案的 hash 與 marker inventory。
- **高可信推論：**目前保存的 ordinary futex、PI-lock 與 ART compare-requeue
  marker 不足以形成 GhostLock requeue-PI caller 證據。
- **待驗證：**未擷取的 native libraries、stripped/inline/indirect caller、
  Fire seccomp 實際 allow/deny，以及 stock runtime execution。
- **已排除／不支持：**把 generic `syscall` import、PI-lock helper 或 ART
  compare-requeue diagnostic 當作 `FUTEX_*_REQUEUE_PI` execution。
- **因風險拒絕測試：**在平板上執行 direct futex syscall、race、crash、
  kernel memory 或 root payload。

## 重要限制

ELF strings/symbols 是 presence evidence，不是 control-flow proof。編譯器
可能 inline 操作、用 numeric command、經由 indirect wrapper，或由未擷取的
library 提供 caller。因此本輪把結果標為 bounded negative observation，
不宣稱 GhostLock 在 PS7331 runtime 不可能發生。
