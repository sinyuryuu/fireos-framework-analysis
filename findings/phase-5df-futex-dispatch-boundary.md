# Phase 5DF — PS7331 futex requeue-PI dispatch boundary

日期：2026-08-04

本輪只讀取官方 PS7331 kernel source，以文字方式抽取 futex syscall
dispatch、proxy waiter/task dataflow 與 cleanup landmarks。沒有編譯或執行
source，沒有呼叫 futex、建立 race、讀寫 kernel memory、產生 address/payload，
也沒有接觸裝置。

## 直接證據

輸入檔案：

- `kernel/futex.c`，SHA-256：由 artifact `summary.json` 保存；
- `kernel/locking/rtmutex.c`，SHA-256：由同一 artifact 保存。

完整行號與 excerpt：
`artifacts/phase5/phase5df-futex-dispatch-boundary-20260804-01/futex-dispatch-landmarks.csv`。

重現：

```sh
python3 tools/scripts/audit_phase5df_futex_dispatch_boundary.py \
  --kernel-root firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4 \
  --output artifacts/phase5/phase5df-futex-dispatch-boundary-REPLACE
```

輸出目錄必須不存在；腳本拒絕覆寫既有 evidence。

## 靜態控制流邊界

在保存的 PS7331 source 中可以直接看到：

1. futex syscall entry 將 requeue 參數轉換後交給 `do_futex`；
2. dispatch switch 含 `FUTEX_WAIT_REQUEUE_PI` 與 `FUTEX_CMP_REQUEUE_PI`；
3. `FUTEX_CMP_REQUEUE_PI` 進入 `futex_requeue(..., requeue_pi=1)`；
4. requeue-PI path 先呼叫 proxy try-lock，再於每個待 requeue waiter 呼叫
   `rt_mutex_start_proxy_lock(&pi_state->pi_mutex, this->rt_waiter,
   this->task)`；
5. `rt_mutex_start_proxy_lock()` 將 `task_blocks_on_rt_mutex()` 的回傳值
   送入 `if (unlikely(ret)) remove_waiter(lock, waiter)`；
6. `task_blocks_on_rt_mutex()` 的 `owner == task` early return 位於
   `waiter->task = task` 之前，而 `remove_waiter()` 仍清除
   `current->pi_blocked_on`。

這些是 source-level path facts，不是 runtime observation。特別是第 4 點
只證明 kernel 內部 proxy API 收到 waiter task 參數；不證明 stock Android
userspace 已建立符合條件的 waiter，也不證明 `waiter->task != current` 在
真機實際發生。

## 判定

- **已證實：** PS7331 source 含 requeue-PI syscall dispatch、proxy lock call
  site、`this->rt_waiter`／`this->task` dataflow，以及 pre-fix cleanup
  landmarks。
- **高可信推論：** 若某個 userspace／kernel path 真正滿足 requeue-PI 的
  paired waiter、PI target、lock ownership 與 error-return 條件，該 source
  path 在結構上能到達 proxy cleanup branch。
- **待驗證：** Fire shipped userspace 是否有 caller；stock runtime 是否能
  形成 `waiter->task != current`；cleanup 後是否有 residue 或 later consumer。
- **已排除／不支持：** 將 source dispatch 存在誤稱為 runtime trigger、memory
  corruption 或 root。
- **因風險拒絕測試：** 在 stock tablet 上呼叫 requeue-PI、安排 race、製造
  error branch、觀察 kernel memory 或執行提權 payload。

## 對 Phase 6A 的意義

這輪把「source path 是否存在」與「runtime identity mismatch」切成兩個獨立
證據門檻。結合 Phase 5DD／5DE：目前保存的 native ELF 與非 kernel source
沒有 named requeue-PI caller；因此下一個安全研究目標是擴充 artifact/source
provenance 或在隔離、明確標示 `LAB_ONLY` 的 instrumented environment 做
觀測，而不是在 stock PS7331 上觸發該路徑。
