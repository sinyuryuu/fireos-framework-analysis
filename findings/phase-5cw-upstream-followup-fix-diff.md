# Phase 5CW：GhostLock upstream primary／follow-up 修補差異

日期：2026-08-04

## 結論摘要

本輪只做已保存原始碼的 host-side marker audit，沒有連接裝置、編譯或
執行 kernel、呼叫 futex、讀寫 kernel memory、計算位址／offset，亦沒有
產生 exploit payload。

### 已證實

- PS7331 exact source 的 `remove_waiter()` 在 lines 1079–1129 仍使用
  `current->pi_blocked_on = NULL`（line 1089），並以 `current` 作為 priority
  chain walk 的最後參數（line 1121 附近）。
- PS7331 `rt_mutex_start_proxy_lock()` 在 lines 1656–1691 仍以
  `if (unlikely(ret))` 呼叫 `remove_waiter(lock, waiter)`（lines 1683–1684）。
- PS7331 `task_blocks_on_rt_mutex()` 的 `-EDEADLK` return 在 line 973，早於
  `waiter->task = task`（line 977）。這是「可能沒有完成 waiter binding」的
  source-level early-return 邊界。
- 本地保存的 Linux v6.1.175 參考已採用 primary fix 的形狀：
  `remove_waiter()` 取得 `waiter->task`，以該 task 清理 `pi_blocked_on`，並以
  `waiter_task` 作 chain walk 參數。其檔案 SHA-256 為
  `c307ed54156d1f16e82387df7b214445dddf27be8a880f31575f698ca07d880a`。
- upstream primary commit `3bfdc63936dd` 明確說明 proxy-lock rollback
  情況下 `waiter::task` 可以不同於 `current`，原本的 current-based cleanup
  會遺留 waiter task 的 dangling `pi_blocked_on`。參考：
  [Linux commit 3bfdc63936dd](https://github.com/torvalds/linux/commit/3bfdc63936dd)。
- 後續 upstream fix `40a25d59e85b3c8709ac2424d44f65610467871e` 又處理另一個
  邊界：deadlock detection 可能使 `waiter->task` 尚未設定，且 wrapper 不應
  對成功取得 lock 的正值呼叫 `remove_waiter()`；patch 加入未入隊 waiter
  防護並將條件收窄為 `ret < 0`。參考：
  [Patchew follow-up patch](https://patchew.org/linux/20260507112913.1019537-1-dave%40stgolabs.net/)。

### 高可信推論

- PS7331 的 exact source 同時保留 primary fix 前的 identity-cleanup 形狀，
  以及 follow-up guard 前的 broad-return cleanup 形狀；因此 `current`、
  `waiter->task`、early return 與 `ret` domain 必須在同一條 runtime trace
  中共同觀察，不能只以單一 source marker 下 exploit 結論。
- PS7331 的 `futex_requeue()` 確實把保存的 waiter task 傳入
  `rt_mutex_start_proxy_lock()`（exact `futex.c` line 1963 附近）；這支持
  「proxy path 的 caller identity 與 cleanup context 可能不同」的靜態模型，
  但仍未證明 stock Fire userspace 實際建立了 mismatch。

### 待驗證

- PS7331 stock runtime 是否曾在同一次 execution 觀察到
  `waiter->task != current`。
- mismatch 後是否留下可重現、持久且可由後續正常路徑消費的 state
  inconsistency。
- 其後是否只有 deadlock／重啟，或存在 memory-safety effect。

### 因風險拒絕測試

- 以 `FUTEX_CMP_REQUEUE_PI` 或其他 PI-requeue 序列主動製造 mismatch／race。
- 執行或改造公開 GhostLock／Emerald trigger。
- 透過 kernel crash、KASAN、未知 ioctl、kernel memory read/write 或 root
  payload 驗證 residue。

這些動作會直接進入核心漏洞觸發與提權路徑，不是一般唯讀診斷；本專案
目前只保留 source-level evidence。

## 精確 source mapping

Input A：
`artifacts/phase5/ps7331-full-source-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c`

- SHA-256：`6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde`
- `task_blocks_on_rt_mutex()`：lines 952–1032
- early deadlock return：line 973
- waiter assignment：line 977
- `remove_waiter()`：lines 1079–1129
- current cleanup：line 1089
- `rt_mutex_start_proxy_lock()`：lines 1656–1691
- broad cleanup condition：line 1683
- cleanup call：line 1684

Input B：
`artifacts/phase5/public-source-review/linux-rtmutex/linux-stable-v6.1.175.c`

- SHA-256：`c307ed54156d1f16e82387df7b214445dddf27be8a880f31575f698ca07d880a`
- fixed `remove_waiter()`：lines 1517–1569
- `waiter_task` binding：line 1522
- waiter-task cleanup：line 1529
- waiter-task chain walk：line 1566

Machine result：
`artifacts/phase5/phase5cw-upstream-followup-markers-20260804-01/summary.json`

## 「identity mismatch」判定規則

本輪不把下列任一項誤稱為 dynamic identity mismatch：

1. source 中存在 `rt_mutex_start_proxy_lock(..., task)`；
2. source 中使用 `current` 作 cleanup target；
3. upstream commit 說明 proxy path 的一般語意；
4. offline model 推導出 `waiter->task` 與 `current` 可不同。

只有在同一次 PS7331 runtime execution 中，同時取得足夠的、非推測性的
waiter identity 與 cleanup context observation，才可標為「dynamic identity
mismatch captured」。目前此欄位仍是 **未觀察**。

## 可重現性與範圍

執行：

```sh
python3 tools/scripts/compare_phase5cw_upstream_followup.py --dry-run \
  --ps7331 artifacts/phase5/ps7331-full-source-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c \
  --fixed-reference artifacts/phase5/public-source-review/linux-rtmutex/linux-stable-v6.1.175.c \
  --output /tmp/phase5cw-dry-run

python3 tools/scripts/compare_phase5cw_upstream_followup.py \
  --ps7331 artifacts/phase5/ps7331-full-source-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c \
  --fixed-reference artifacts/phase5/public-source-review/linux-rtmutex/linux-stable-v6.1.175.c \
  --output artifacts/phase5/phase5cw-upstream-followup-markers-20260804-01
```

工具只輸出 sanitized markers；它不輸出 kernel address、offset、trigger、
payload 或裝置命令。
