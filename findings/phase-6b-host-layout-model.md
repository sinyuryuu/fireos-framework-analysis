# Phase 6B：PS7331 主機端 layout／allocator 模型

## 範圍

本階段只讀取官方 PS7331 source、已保存 kernel config，以及一次主機端
AArch64 Clang record-layout probe。沒有使用 ADB 執行 futex，沒有建立 race、
heap spray、kernel address、memory primitive 或 root payload。

## 已證實

- PS7331 source path 是 `firmware/extracted/PS7331-SOURCE-20250617/.../4.4`。
- `CONFIG_FUTEX=y`、`CONFIG_RT_MUTEXES=y`、`CONFIG_SLUB=y`、
  `CONFIG_RANDOMIZE_BASE=y`；`CONFIG_USERFAULTFD`、`CONFIG_KASAN`、
  `CONFIG_DEBUG_INFO` 與 `CONFIG_DEBUG_RT_MUTEXES` 未啟用。
- AArch64 compiler probe 解析出 `struct rt_mutex_waiter` 為 72 bytes、
  `struct pipe_buffer` 為 40 bytes、`struct ion_buffer` 為 248 bytes；
  `struct task_struct` 為 3488 bytes，alignment 為 16。
- `futex_wait_requeue_pi()` 將 `rt_mutex_waiter` 宣告為區域變數；
  `rtmutex_common.h` 也明確記載 waiter 位於被阻塞 task 的 kernel stack。
  因此不能把它直接分類為可由一般 kmalloc spray 重用的 waiter slab object。
- ION metadata 由 `kzalloc(sizeof(struct ion_buffer))` 配置；source/config
  model 對應到 `kmalloc-256`。pipe path 配置的是 `pipe_buffer` 陣列，而非
  單獨的每-buffer kmalloc object；預設 16 個元素的 request 為 640 bytes，
  source model 對應到 `kmalloc-1024`。
- task_struct 由專用的 `task_struct` cache 建立，不是普通 kmalloc cache。
  其 cache alignment 由 ARM64 的 64-byte `ARCH_DMA_MINALIGN` 來源推導；
  具體 slab object rounding 只作模型，不代表任何 runtime address 或 reuse。

## 唯讀裝置邊界

證據見 `findings/phase-6b-evidence-index.md` 與本地原始 run
`adb/phase6b/PHASE6B-BOUNDARY-RO-20260804-01/`。

- fingerprint：`Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`
- kernel：`4.4.146+`，AArch64，SMP/PREEMPT
- `/proc/kallsyms`：shell 讀取被拒絕
- `/proc/slabinfo`：不存在
- `/proc/sys/kernel/randomize_va_space`：shell 讀取被拒絕
- SELinux：`Enforcing`

## 解讀

這些結果支持「核心功能與相關 source path 存在」的結論，但不能支持：

- runtime `waiter->task != current` 已發生；
- cleanup residue 或第二次 consumer 已發生；
- heap adjacency、object reuse、記憶體破壞、kernel crash；
- KASLR slide、讀寫 primitive 或權限提升。

## 結論標籤

**已證實：** source/config 的 ABI 與配置模型、以及裝置對 KASLR／slab 觀測面的
權限邊界。

**高可信推論：** 在 inspected path 中，直接以 SLUB waiter object 為目標的模型
不成立，因 waiter 是 stack-resident。

**待驗證：** requeue-PI runtime return path、proxy identity mismatch、後續
consumer 與任何安全影響。

**因風險拒絕測試：** 在 stock device 上執行 `FUTEX_CMP_REQUEUE_PI`、雙執行緒
競態、single-shot panic、heap shaping、kernel memory operation 或 root chain。
