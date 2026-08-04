# Phase 5BJ：GhostLock upstream fix 與 PS7330／PS7331 source 適用性比對

日期：2026-08-04

## 結論先行

### 已證實

1. Linux upstream fix 的核心變更是把 `remove_waiter()` 的 cleanup 與最後的
   priority-chain task 從 `current` 改為 `waiter->task`。上游 patch 也明確說明
   該函式會被 `rt_mutex_start_proxy_lock()` 的 futex requeue rollback 使用，且
   `waiter::task` 不等於 `current`。[Linux stable patch](https://www.spinics.net/lists/stable/msg940814.html)
2. 本機保存的 PS7330 source-family `rtmutex.c` 在 `remove_waiter()` 內仍有
   `current->pi_blocked_on = NULL`，並把 `current` 傳給 chain-walk；分類為
   `PRE_FIX_CURRENT_TASK_CLEANUP`。
3. 官方 PS7331 build-selected `mt8183/4.4` `rtmutex.c` 也有完全相同的兩個
   pre-fix marker，分類仍為 `PRE_FIX_CURRENT_TASK_CLEANUP`。
4. fixed reference 使用 `waiter_task->pi_blocked_on = NULL`，並把
   `waiter_task` 傳給 chain-walk，分類為 `FIXED_WAITER_TASK_CLEANUP`。
5. 因此，在 source／inspected-Image 證據範圍內，7.3.3.1 沒有顯示已套用
   GhostLock fix；這仍不是 PS7330 signed binary 的直接證明。

### 高可信推論

- PS7331 不應被視為 GhostLock 修補版；升級若有價值，應是一般安全更新 A/B，
  而不是為了這個漏洞的已知修補。
- PS7330 source、PS7331 build-selected source 與目前的 Android 9／4.4.146
  runtime family 彼此一致，使 source-level applicability 很強；但沒有 exact
  PS7330 signed boot/Image，仍不能宣稱可利用或可取得 root。

### 待驗證

- Amazon 是否在 PS7330 signed image 中加入未公開的 private backport；shell
  無法讀取 exact boot block。
- PS7331 OTA 其他 vendor／firmware 成員是否含與 GhostLock 無關的安全修補；本輪
  只判定 rtmutex function marker。

### 已排除

- 「有 PS7331 boot.img 就代表它已修補 GhostLock」。
- 「source-derived layout 就等於 runtime exploit offset」。
- 「同為 MTK 或同為 trona 就可直接套用其他裝置 root payload」。

### 因風險拒絕測試

沒有執行 futex race、kernel memory 操作、native root payload、未知 ioctl、BROM/DA、
preloader/LK、fastboot、OTA、boot image 或任何分割區寫入。

## 機器比對結果

可重現腳本：[`tools/scripts/compare_phase5bj_ghostlock_fix.py`](../tools/scripts/compare_phase5bj_ghostlock_fix.py)

輸出：[`artifacts/phase5/phase5bj-ghostlock-fix-application-20260804-01/`](../artifacts/phase5/phase5bj-ghostlock-fix-application-20260804-01/)

| Input | `remove_waiter()` lines | Classification | Key marker |
|---|---:|---|---|
| PS7330 source family | 1079–1129 | `PRE_FIX_CURRENT_TASK_CLEANUP` | `current->pi_blocked_on`, chain argument `current` |
| PS7331 build-selected source | 1079–1129 | `PRE_FIX_CURRENT_TASK_CLEANUP` | `current->pi_blocked_on`, chain argument `current` |
| Fixed reference | 1517–1569 | `FIXED_WAITER_TASK_CLEANUP` | `waiter_task->pi_blocked_on`, chain argument `waiter_task` |

輸入 hashes 與結果 hashes 都保存在 artifact `summary.json`、`comparison.csv` 與
`sha256sums.txt`。這個 checker 不會輸出 kernel addresses、runtime offsets 或
exploit payload。

## 與 CVE 記錄的對照

NVD 將 CVE-2026-43499 描述為 `remove_waiter()` 在 futex proxy-lock rollback
情境使用錯誤 task，並列出 dangling `pi_blocked_on` 的 UAF 風險；[NVD record](https://nvd.nist.gov/vuln/detail/CVE-2026-43499)。
這與本次 source markers 的差異方向一致，但 NVD／upstream patch 不能取代
OEM signed-image 與 Android SELinux／post-exploitation 證據。

## 升級決策

| 目的 | 現階段決定 |
|---|---|
| GhostLock 修補 | 不支持；PS7331 function marker 仍是 pre-fix |
| 一般安全更新 | 可另立完整 OTA A/B 研究；不是本輪執行項目 |
| 單獨寫入 PS7331 boot.img | 拒絕；不是等價 OTA |
| 目前設備 | 維持 PS7330，未變更 |

本輪另保存了新的唯讀裝置快照：
`adb/phase5/PHASE5BJ-DEVICE-READONLY-20260804-01/`。它確認裝置仍為
`KFTRWI/trona/MT8183`、PS7330.4104N、green verified boot、SELinux Enforcing、
shell UID 2000，HOME 仍為 Fire Launcher。
