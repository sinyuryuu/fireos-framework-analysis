# Phase 5BY：GhostLock primary／follow-up fix-chain audit

日期：2026-08-04

## 為什麼新增這一輪

公開資料新增了 `CVE-2026-53163`：它描述的是在第一個
`waiter->task` 修補之後，`remove_waiter()` 可能處理尚未 enqueue 的 waiter
的 follow-up regression。這代表「把 3bfdc639 的單一 hunk backport 到 4.4」
不能直接稱為完整修補。

參考：[NVD CVE-2026-53163](https://nvd.nist.gov/vuln/detail/CVE-2026-53163)、
[NVD CVE-2026-43499](https://nvd.nist.gov/vuln/detail/CVE-2026-43499)。

## 結論

**已證實（PS7331 source scope）**：PS7331 仍是第一個 GhostLock 修補之前的
形態：`remove_waiter()` 使用 `current->pi_blocked_on`，而不是
`waiter->task`。

**已證實（control-flow scope）**：`task_blocks_on_rt_mutex()` 在 line 973
可以因 early deadlock 直接回傳 `-EDEADLK`；`waiter->task = task` 要到 line
977 才設定。`rt_mutex_start_proxy_lock()` 在 lines 1683–1684 以
`if (unlikely(ret))` 呼叫 `remove_waiter()`。這是「若把第一個修補 backport
進來，必須重新檢查未 enqueue waiter guard」的靜態證據。

**高可信推論**：PS7331 不是一個已套用 primary fix、再因 follow-up regression
而受影響的 modern kernel；它更早，primary fix 本身就未出現。對 PS7331 做
任何自製 4.4 backport 時，必須同時設計與驗證兩個修補語意，不能只替換
`current` 字串。

**待驗證**：Amazon release-CI 是否有未保存的 backport、signed Image 的
實際 machine code，以及任何 runtime crash／UAF／root 效果。

## PS7331 控制流

輸入：
`artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c`

- `task_blocks_on_rt_mutex()`：lines 952–1032。
- early deadlock return：line 973。
- waiter assignment：line 977。
- `remove_waiter()` current cleanup：line 1089。
- `rt_mutex_start_proxy_lock()`：lines 1656–1691。
- conditional cleanup：line 1683。
- `remove_waiter(lock, waiter)`：line 1684。

host-only checker 結果：
`PRE_PRIMARY_FIX_WITH_EARLY_RETURN_GUARD_REVIEW`。

這個名稱是 source-review classification，不是 CVE-2026-53163 的 exact
product assignment，也不是 exploitability 結論。

## 修補版本的正確解讀

Phase 5BW 的 v6.1.175 reference 只用來表示 primary fix 的
`waiter->task` 語意；它不是「所有 GhostLock 修補完成」的 reference。NVD
將 v6.1.175 列在 CVE-2026-53163 的受影響區間，直到後續修補版本。因此本
專案現在把兩種狀態分開：

| 狀態 | 意義 |
|---|---|
| primary-fix reference | `remove_waiter()` 使用 waiter task |
| complete-fix claim | 必須另外確認未 enqueue waiter guard；本專案未把 v6.1.175 稱為 complete |
| PS7331 current source | primary fix 尚未出現；follow-up guard 只列為 backport review point |

## 與 live POC 的界線

這一輪沒有：

- 編譯或執行 kernel；
- 建立或執行 futex race/reproducer；
- 讀寫 kernel memory、尋找 offset、產生 payload；
- 執行 root、unknown ioctl、BROM/DA、fastboot、OTA 或 partition write。

因此不能把「PS7331 source 具備 pre-fix control flow」寫成「已在平板上
取得 root」。公開研究頁面雖提供 reproducer/exploit 連結，但本專案只引用
其修補與適用性敘述，不下載或執行 exploit。[NebuSec GhostLock
overview](https://nebusec.ai/buglist/CVE-2026-43499/)

## 可重現命令

```sh
python3 -B -m unittest discover -s tests \
  -p 'test_phase5by_ghostlock_fix_chain.py'

python3 -B tools/scripts/analyze_phase5by_ghostlock_fix_chain.py \
  --source artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c \
  --output artifacts/phase5/phase5by-ps7331-ghostlock-fix-chain-20260804-02
```

## 判定

- **已證實**：PS7331 source 是 primary GhostLock fix 前的語意。
- **高可信推論**：任何 4.4 backport 都需要獨立處理 follow-up guard；單一
  `waiter->task` 替換不足以宣稱 complete fix。
- **待驗證**：signed PS7331 Image 是否與 source 完全一致，以及 runtime
  effect。
- **因風險拒絕測試**：為了驗證 crash/UAF/root 而把 reproducer 或 patch
  image 放到裝置上；該操作不是可控的「只重啟」測試。
