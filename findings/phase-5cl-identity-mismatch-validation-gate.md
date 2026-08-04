# Phase 5CL：GhostLock identity-mismatch dynamic-validation gate

日期：2026-08-04

## 核心判定

`waiter->task != current` 的一次真實、可重現、可歸因觀察，確實是本專案
從 **static applicability** 進入 **dynamic validation** 的主要分水嶺。

但 identity mismatch 本身不是 root 證明。證據應分成以下四層：

| 層級 | 必須觀察的事 | 目前狀態 |
|---|---|---|
| D0 | source/interface 允許 proxy task 與執行 cleanup 的 `current` 分離 | 已證實，source scope |
| D1 | 真實 runtime 中出現 `waiter->task != current` | 尚未觀察 |
| D2 | mismatch 發生時 cleanup 實際寫入／清除的 task 與欄位 | 尚未觀察 |
| D3 | 錯誤狀態跨越後續正常 kernel consumer，並可重複觀察 | 尚未觀察 |
| D4 | 狀態差異形成可控 memory effect 或 privilege transition | 尚未證實；不在本專案 stock device 上執行 |

## 已有 D0 證據

PS7331 build-selected source 的介面形狀是：

- `futex_requeue()` 將 `this->task` 傳入 `rt_mutex_start_proxy_lock()`；
- `task_blocks_on_rt_mutex()` 將該 task 保存到 `waiter->task`；
- `remove_waiter()` 卻以 `current->pi_blocked_on` 與 `current` 作 cleanup。

這些觀察位於：

```text
artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/kernel/futex.c
artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c
```

既有 `P5CC`、`P5CG`、`P5CK` 證據只支持 D0 與 runtime visibility boundary，
不支持 D1–D4。

## 什麼才算 D1 的有效證據

有效證據必須同時保存：

1. 同一次 kernel path 的 proxy task identity 與 cleanup executor identity；
2. 能證明兩者不是只在不同時間、不同 syscall 或不同 task 的推測；
3. 可重複至少一次，且與同一 source／build identity 綁定；
4. 不依賴 kernel address、KASLR offset、任意讀寫或 root payload。

在研究環境中，這可以由明確的 debug/instrumented kernel event 或受控的
非 production 測試環境提供；本機 stock PS7331 的普通 shell 目前沒有這種
觀測面：`/proc/kallsyms` 被拒絕，`/proc/kcore`／`/dev/kmem` 不可用，且
本專案沒有在裝置上安裝或注入 tracing kernel。

## 不能把哪些現象當成 D1

- source 中存在 `task` 參數；
- `waiter->task` 與 `current` 在不同函式出現；
- public PoC 對另一台裝置成功；
- kernel panic、ADB 消失或裝置重啟；
- `/proc/kallsyms` denied；
- 推導出的 offset、boot header 或 symbol layout。

以上最多是 source／visibility／failure evidence，不能替代 identity observation。

## 目前裝置結論

PS7331 實機已完成唯讀 gate capture，但尚未有 D1 證據。裝置仍在首次更新後
lock/OOBE 狀態；本輪沒有觸發 futex PI／requeue、沒有 kernel memory access、
沒有未知 ioctl，也沒有執行 root exploit。這是有意識的 safety boundary，
不是把 D1 說成已完成。

## 後續安全研究方向

1. 研究者完成 OOBE 後，重新封存正常 PS7331 runtime identity；這只改善
   baseline，不會自動產生 D1。
2. 在主機端維持 source-level task/current dataflow model，並把每個假設與
   runtime evidence 分開標記。
3. 若需要 D1，使用與 stock tablet 隔離的、可回復的 instrumented research
   environment；不要把 debug instrumentation、race trigger 或 root payload
   寫入日常裝置。

## 判定

目前最準確的狀態是：

```text
D0 source identity separation: Confirmed
D1 runtime waiter->task != current: Unobserved
D2 wrong cleanup target: Unobserved
D3 persistent consumer: Unobserved
D4 controlled memory effect / root: Unproven and not executed
```
