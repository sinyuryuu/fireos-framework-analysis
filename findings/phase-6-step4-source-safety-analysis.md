# Phase 6 Step 4：PS7331 Requeue-PI exact-source safety analysis

## Scope

本文件只分析本地保存的 PS7331 kernel source，不編譯、推送或執行
`FUTEX_CMP_REQUEUE_PI`。目標是判斷「單執行緒、單次、合法參數」是否足以
把該操作視為無害的 syscall switch probe。

結論是：**不足以視為無害 probe；實體執行列為因風險拒絕測試。**

## Exact source chain

| Stage | PS7331 source | Observed behavior | Classification |
|---|---|---|---|
| syscall gate | `kernel/futex.c:3233-3241` | `FUTEX_CMP_REQUEUE_PI` 受 `futex_cmpxchg_enabled` gate 控制；失敗可回 `-ENOSYS` | 已證實，switch gate |
| dispatch | `kernel/futex.c:3268-3269` | 直接呼叫 `futex_requeue(..., &val3, 1)` | 已證實，進入 requeue-PI handler |
| PI state preparation | `kernel/futex.c:798-819`, `1770-1795` | 要求兩個不同 futex；可能由 `refill_pi_state_cache()` 執行 `kzalloc(sizeof(*pi_state))`；`nr_wake` 必須為 1 | 已證實，可能改變核心配置／PI state |
| key and bucket path | `kernel/futex.c:1798-1821` | 解析兩個 user futex key、驗證存取、鎖定 hash buckets | 已證實，非唯讀查詢 |
| proxy candidate | `kernel/futex.c:1849-1857` | 在條件成立時呼叫 `futex_proxy_trylock_atomic()` | 已證實，可能進入 proxy path |
| no-waiter branch | `kernel/futex.c:1699-1717` | 找不到 top waiter 時回傳 0 | 已證實，但只描述該分支；不能代表所有執行環境 |
| waiter validation | `kernel/futex.c:1926-1937`, `1949-1953` | 要求 WAIT_REQUEUE_PI／CMP_REQUEUE_PI 配對及 key 匹配，否則回錯誤 | 已證實 |
| proxy lock | `kernel/futex.c:1960-1965` | 將 `this->rt_waiter` 與 `this->task` 傳給 `rt_mutex_start_proxy_lock()` | 已證實，研究中的 identity 關係所在 |
| cleanup | `kernel/locking/rtmutex.c:1656-1684`, `1079-1090` | `if (unlikely(ret)) remove_waiter()`；清理使用 `current->pi_blocked_on` | 已證實，pre-fix cleanup semantics |

## 為何單執行緒不構成安全保證

1. 「沒有建立 pthread」只限制呼叫程序的 userspace 執行緒數量，不能把
   syscall 從 requeue-PI handler 變成純查詢。
2. `refill_pi_state_cache()` 可能配置並掛到目前 task 的 `pi_state_cache`；
   因此即使最後沒有找到 waiter，仍不是完全無副作用的 switch probe。
3. `futex_proxy_trylock_atomic()` 在無 waiter 時可提早回傳 0，但這是
   runtime branch，不是 userspace 可用單次呼叫保證的全域不變量。
4. 一旦存在符合 key 的 requeue waiter，後續會把 stored waiter/task 傳入
   proxy lock，並可能走到 pre-fix cleanup。這正是本研究試圖觀察的核心
   狀態，而不是安全測試的旁路。
5. 「回傳 0 或標準 errno」只能說明 syscall 的一個結果；不能證明沒有
   PI state、waiter、鎖或後續 cleanup 狀態變化，也不能證明沒有 kernel
   side effect。

## 已保存的 source identity

| File | SHA-256 |
|---|---|
| `kernel/futex.c` | `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96` |
| `kernel/locking/rtmutex.c` | `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde` |
| `kernel/locking/rtmutex_common.h` | `b3456f9e83a1919e41a88a6638ad1e26ed9966e800c6efc823940df1151919fc` |

## Evidence status

- **已證實：** PS7331 syscall dispatch、PI-state preparation、proxy call-site
  與 pre-fix cleanup source path 存在。
- **高可信推論：** 單次單執行緒呼叫不足以證明「無核心狀態變更」；它不能被
  當作 harmless reachability probe。
- **待驗證：** stock device 是否有合法 userspace caller、runtime 是否形成
  `waiter->task != current`、cleanup residue、later consumer 或 memory effect。
- **已排除：** Phase 6A ordinary private PI lock/unlock 不等於 requeue-PI
  proxy waiter；它不能替代本階段的 runtime 證據。
- **因風險拒絕測試：** 在 stock PS7331 執行 requeue-PI harness、配對 waiter、
  競態、panic、heap shaping、kernel memory operation 或 root chain。

## 安全後續

可繼續的工作限於：host-only source/ABI model、AOSP 對照、離線控制流程
摘要，以及明確標記 `LAB_ONLY` 的隔離環境設計。任何實體觸發都需要新的
風險審查，且本文件不授權該操作。
