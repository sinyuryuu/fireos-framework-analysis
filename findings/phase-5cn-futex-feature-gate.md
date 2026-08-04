# Phase 5CN：PS7331 futex feature gate 與 identity observation boundary

日期：2026-08-04
範圍：Fire HD 10／KFTRWI／trona／PS7331
安全範圍：主機端 source/config review；未觸發 `FUTEX_*_PI`，未執行 race、ioctl、kernel memory access 或 root payload。

## Executive result

本輪把「PI 路徑是否由 build/runtime feature gate 開放」與「實際是否出現
`waiter->task != current`」分開處理：

| 判定 | 結果 |
|---|---|
| PS7331 runtime 啟用 futex／rtmutex | 已證實 |
| build-selected source 含 PI/requeue 與 proxy-lock wiring | 已證實 |
| `FUTEX_*_PI` 在 syscall dispatch 前受 `futex_cmpxchg_enabled` 檢查 | 已證實，source scope |
| `CONFIG_HAVE_FUTEX_CMPXCHG` 的最終 arch/Kconfig 來源 | 待驗證 |
| runtime `futex_cmpxchg_enabled == 1` 的直接觀察 | 待驗證 |
| runtime `waiter->task != current` | 尚未觀察（D1 未達成） |
| 錯誤 cleanup 後的持久 invariant 或 memory effect | 尚未觀察 |

最重要的結論是：`CONFIG_FUTEX=y` 與 `CONFIG_RT_MUTEXES=y` 只證明相關
功能被編譯進 kernel；它們不是 identity mismatch 的證據，也不是 exploit
可利用性的證據。

## Source-to-gate mapping

build-selected `futex.c`：

1. 行 176–178：只有在未定義 `CONFIG_HAVE_FUTEX_CMPXCHG` 時宣告
   `futex_cmpxchg_enabled`。
2. 行 3310–3327：同一條件下，`futex_detect_cmpxchg()` 用 NULL fault
   測試 `futex_atomic_cmpxchg_inatomic()`；只有回傳 `-EFAULT` 才將
   `futex_cmpxchg_enabled` 設為 1。
3. 行 3330–3348：`futex_init()` 在建立 futex hash table 後呼叫上述 detection。
4. 行 3233–3241：`FUTEX_LOCK_PI`、`FUTEX_UNLOCK_PI`、`FUTEX_TRYLOCK_PI`、
   `FUTEX_WAIT_REQUEUE_PI`、`FUTEX_CMP_REQUEUE_PI` 在進入各自 handler 前，
   若 gate 為 false 即回傳 `-ENOSYS`。
5. 行 3264–3269：只有通過 gate 且 command 為
   `FUTEX_CMP_REQUEUE_PI`，才會進入 `futex_requeue(..., requeue_pi=1)`。

build-selected `rtmutex.c`：

1. `rt_mutex_start_proxy_lock()` 行 1658–1690 接受明確的 `task` 參數，並
   將它傳給 `task_blocks_on_rt_mutex()`。
2. `task_blocks_on_rt_mutex()` 行 972–988 先以傳入的 `task` 做 deadlock
   check、設定 `waiter->task`，並寫入該 task 的 `pi_blocked_on`。
3. `remove_waiter()` 行 1079–1090 卻以 `current->pi_blocked_on` 清理；行
   1125–1126 也把 `current` 傳給 chain adjustment。這是 D0 的 source-level
   identity separation，但不是 D1 的 runtime observation。

## Runtime evidence

實機 `PS7331-CONFIG-GATES-20260804-03` 的 `/proc/config.gz` 回報：

```text
CONFIG_FUTEX=y
CONFIG_RT_MUTEXES=y
CONFIG_SECCOMP=y
CONFIG_SECCOMP_FILTER=y
CONFIG_SECURITY_SELINUX=y
CONFIG_DEBUG_FS=y
CONFIG_KALLSYMS=y
# CONFIG_KALLSYMS_ALL is not set
```

tracefs inventory 中保存了 `sched`、`block`、`filelock` 等 category，但沒有
名為 `futex` 或 `rtmutex` 的專用 category。此結果只能描述 tracepoint
inventory；不能推導 futex path 未執行。部分 tracefs control files 對 shell
被拒絕，且本輪沒有嘗試 enable/filter。

## Source completeness boundary

目前保存的 PS7331 full-source member subset 含：

- build-selected `kernel/futex.c`；
- build-selected `kernel/locking/rtmutex.c`；
- `arch/arm64/configs/trona_defconfig`；
- 少量 build metadata。

這個 subset 沒有完整的 `arch/arm64/include/asm/futex.h`、完整 Kconfig 展開結果
或最終產生的 `.config`。因此：

- source 中出現 `#ifndef CONFIG_HAVE_FUTEX_CMPXCHG`，不代表該 symbol 在最終
  build 一定未定義；
- runtime config 沒有列出該 symbol，也不代表它是 unset；Android kernel
  config export 對未輸出的 symbol 不能直接作負面判定；
- 目前最多能說：PS7331 的實機啟用了 futex／rtmutex，而 source 保留一條
  受 `futex_cmpxchg_enabled` 控制的 PI 路徑。

## D1 判定

本輪沒有取得同一次 kernel path 中的：

```text
proxy task identity = waiter->task
cleanup executor    = current
waiter->task != current
```

因此 D1 仍為 **尚未觀察**。沒有把 source line、config flag、tracepoint
缺失、ADB 重啟或任何 failure symptom 當作 identity mismatch。

## 證據與信心

| Evidence ID | 來源 | 觀察 | Confidence |
|---|---|---|---|
| `P5CN-SRC-001` | `.../kernel/futex.c`，SHA-256 `ca9140...ca7a96` | PI command gate、`futex_requeue` dispatch、runtime detection | Confirmed，source scope |
| `P5CN-SRC-002` | `.../kernel/locking/rtmutex.c`，SHA-256 `6cb544...b75dde` | explicit task → waiter、`current` cleanup | Confirmed，source scope |
| `P5CN-SRC-003` | `.../arch/arm64/configs/trona_defconfig`，SHA-256 `09ca8d...ecaaac` | build target metadata；不含完整 arch futex implementation | Confirmed，scope limitation |
| `P5CN-RUNTIME-001` | `adb/phase5/PS7331-CONFIG-GATES-20260804-03/config.stdout.txt` | runtime `CONFIG_FUTEX=y`、`CONFIG_RT_MUTEXES=y` | Confirmed，runtime config |
| `P5CN-RUNTIME-002` | `.../tracing_event_categories.stdout.txt` | inventory 無 futex/rtmutex 專用 category | Confirmed，inventory scope |
| `P5CN-SAFETY-001` | `.../result.md`、`sha256sums.txt` | 本輪 read-only，未觸發 PI／ioctl／memory access | Confirmed |

完整路徑、時間、命令與檔案 hash 由既有 Phase 5CM evidence index 保存；本文件
中的縮寫路徑以該 index 的完整路徑為準。

## 下一個安全研究邊界

1. 主機端取得完整、與 PS7331 build 對應的 ARM64 source/Kconfig/build manifest，
   只做 source-to-image mapping；不把缺失的 arch file 自行補出來。
2. 若必須得到 D1，應使用隔離的 instrumented research kernel／emulator 或
   明確提供 task identity trace 的研究環境；不要在日常平板上注入 debug
   kernel、race trigger 或 root payload。
3. 在 stock PS7331 + shell visibility 不變的條件下，重複 read-only procfs／
   tracefs inventory 不會產生 D1，應避免把相同 negative observation 當成新
   動態證據。

## Safety disposition

本輪未執行且仍拒絕執行：GhostLock PoC、FUTEX PI/requeue trigger、競速器、
kernel UAF／panic trigger、未知 ioctl、ION/CMDQ request、kernel memory
read/write、BROM/DA、fastboot/boot image/partition write、remount、SELinux
修改與任何 root payload。
