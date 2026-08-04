# Phase 5CA：PS7331 follow-up patch mapping

日期：2026-08-04
範圍：Fire OS 7.3.3.1／PS7331 exact 4.4 source；host-only。這一輪不執行
futex、exploit、root、bootloader 或 image mutation。

## 結論

### 已證實

公開的 CVE-2026-53163 follow-up patch 有兩個獨立修補語意：

1. 在 `remove_waiter()` 取得 waiter task 後，若 waiter task 為空（代表 waiter
   尚未入 queue），直接跳過 cleanup；
2. proxy-lock wrapper 只在負值錯誤返回時呼叫 `remove_waiter()`，而不是對所有
   non-zero result 呼叫。

Patch v1 的公開 diff 可在 [Patchew patch](https://patchew.org/linux/20260507112913.1019537-1-dave%40stgolabs.net/)
核對；NVD 也記錄了同一個 early-deadlock／wrapper 條件。[NVD
CVE-2026-53163](https://nvd.nist.gov/vuln/detail/CVE-2026-53163)

PS7331 exact source 的對應狀態：

| 修補語意 | PS7331 source | 位置 | 判定 |
|---|---|---|---|
| primary cleanup 使用 waiter task | `current->pi_blocked_on = NULL` | `rtmutex.c:1089` | 未出現 |
| early deadlock 在 waiter assignment 前返回 | `return -EDEADLK` 早於 `waiter->task = task` | `rtmutex.c:973`、`977` | 已證實 |
| 未入 queue waiter guard | `if (!waiter_task) return` 類語意 | `remove_waiter()` 無此判斷 | 未出現 |
| wrapper 僅負值 cleanup | `if (unlikely(ret))` | `rtmutex.c:1683` | 未出現 |
| proxy caller | `rt_mutex_start_proxy_lock(...)` | `futex.c:1963–1965` | 已證實 |
| PI requeue entry | `FUTEX_*REQUEUE_PI` dispatch | `futex.c:3237–3269` | 已證實 |

### 高可信推論

PS7331 不能以「只把 primary `current` 換成 `waiter->task`」作為完整
backport 判定。若採用 primary fix 語意，PS7331 的早期 return 與 wrapper
control flow 仍需要獨立的未入 queue guard review；直接移植現代 patch 的行號
或 API 名稱也不能視為 4.4 編譯結果。

### 待驗證

- Amazon 是否在 release-CI 或未保存的另一份 kernel copy 中加入等價 guard；
- signed Image 的 raw branch-level follow-up guard；
- runtime 是否能到達 fault、是否只是 kernel denial/crash，以及是否有任何
  privilege transition。

### 因風險拒絕測試

沒有編譯或執行 kernel、futex race、native PoC、unknown ioctl、root payload；
沒有推導 kernel offset、gadget 或 credential target；沒有刷寫 boot image 或
任何分割區。

## Exact source evidence

Inputs：

- `rtmutex.c` SHA-256：`6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde`
- `futex.c` SHA-256：`ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96`
- source mapping JSON：`artifacts/phase5/phase5ca-ps7331-followup-patch-mapping-20260804-01/followup-mapping.json`

控制流如下：

```text
FUTEX_CMP_REQUEUE_PI
  -> futex_requeue()
  -> rt_mutex_start_proxy_lock(pi_state->pi_mutex, this->rt_waiter, this->task)
  -> task_blocks_on_rt_mutex()
       -> -EDEADLK at line 973
       -> waiter->task assignment only at line 977
  -> wrapper condition at line 1683
  -> remove_waiter(lock, waiter) at line 1684
```

這是 source-level applicability mapping，不是觸發步驟，也不代表 live
crash/root 已發生。

## 判定邊界

本輪的最強結論是：

> **PS7331 exact 4.4 source 同時保留 primary pre-fix 語意與 follow-up review
> 所針對的兩個 control-flow 風險點；這支持 static patch-status 判定，但
> 不足以證明 runtime exploitability 或 temporary root。**
