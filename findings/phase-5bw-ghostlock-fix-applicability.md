# Phase 5BW：PS7331 GhostLock 公開修補適用性核對

日期：2026-08-04

## 結論

**已證實（source / artifact level）**：PS7331 build-selected kernel source 的
`remove_waiter()` 仍使用 `current->pi_blocked_on = NULL`，並把 `current`
傳給 `rt_mutex_adjust_prio_chain()`。相同檢查中的 fixed reference 已改用
`waiter->task`。可重跑 checker 的結果是
`PS7331_SOURCE_MATCHES_PRE_FIX_SEMANTICS`。

**高可信推論**：PS7331 的公開 source 與保存的 boot Image markers 都與
GhostLock 修補前語意一致；若該 kernel 的 `futex_requeue()` →
`rt_mutex_start_proxy_lock()` 路徑在執行時可達，這是應該由 kernel vendor
修補處理的缺陷暴露候選。這不是 Amazon 已發布安全公告的等價證明，也不是
真機 exploitability 證明。

**待驗證**：真機是否能在可控條件下觸發競態、是否造成實際 memory corruption、
是否可控制 kernel flow，以及是否能轉換為 root。這些需要核心記憶體與提權
利用；本專案不執行這類 payload、unknown ioctl、地址/offset 搜尋或 root
測試。

## 公開修補語意

公開的 Linux stable patch 將修補描述為：`remove_waiter()` 也會被
`futex_requeue()` 使用的 proxy-lock rollback 呼叫；該情境下
`waiter::task` 不等於 `current`。修補的語意是讓 dequeue、
`pi_blocked_on` 清除，以及 priority-chain 調整都使用 waiter task。參考：

- [NVD CVE-2026-43499](https://nvd.nist.gov/vuln/detail/CVE-2026-43499)
- [Linux stable patch 3bfdc639](https://www.spinics.net/lists/stable/msg940408.html)

本報告採用公開 patch 的語意作為比對基準；沒有把現代 kernel patch 直接宣稱
可套用到 MediaTek 4.4 tree，也沒有修改 PS7331 source。

## 輸入證據

| 輸入 | 內容 | SHA-256 |
|---|---|---|
| PS7331 build-selected source | `kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c` | `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde` |
| Fixed reference | preserved `linux-stable-v6.1.175.c` | `c307ed54156d1f16e82387df7b214445dddf27be8a880f31575f698ca07d880a` |
| PS7331 boot image | official local PS7331 `boot.img` | `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` |
| PS7331 source archive | official 7.3.3.1 source archive | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea` |

## 逐項比對

### PS7331 source

檔案：
`artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c`

- `remove_waiter()`：lines 1079–1129。
- `current->pi_blocked_on = NULL`：line 1089。
- priority-chain call 的最後 task argument 是 `current`：lines 1125–1126。
- `rt_mutex_start_proxy_lock()`：lines 1644–1691。
- proxy error path 在 line 1684 呼叫 `remove_waiter(lock, waiter)`。

### PS7331 futex reachability

build-selected `futex.c` 保留 `FUTEX_REQUEUE_PI`／`FUTEX_CMP_REQUEUE_PI` dispatch、
`futex_requeue()` 與 `rt_mutex_start_proxy_lock()` 的相鄰路徑。這表示 source
層級具備與修補說明相符的 proxy-lock caller；不表示競態在真機必然成功。

### Fixed reference

保存的 fixed reference 在 `remove_waiter()` 中：

- 綁定 `waiter_task = waiter->task`；
- 使用 waiter task 的 `pi_lock` 與 `pi_blocked_on`；
- 將同一個 waiter task 傳入 `rt_mutex_adjust_prio_chain()`。

checker 不以行號或全文 diff 判斷，而是檢查這三個語意標記。

## Boot Image 交叉證據

既有 PS7331 Image review 找到：

- `remove_waiter` symbol/function marker；
- `SP_EL0` current-task source；
- current task `pi_blocked_on` cleanup store；
- `rt_mutex_start_proxy_lock` 的 `remove_waiter` call marker。

既有 source-to-Image verifier 全部通過，分類為
`PS7331_INSPECTED_IMAGE_CONSISTENT_WITH_PRE_FIX_SOURCE`。這仍是靜態 marker
證據，並非完整反組譯 CFG 等價性或 live execution proof。

## 可重現命令

```sh
python3 -B -m unittest discover -s tests \
  -p 'test_phase5bv_ghostlock_semantics.py'
python3 -B -m unittest discover -s tests \
  -p 'test_phase5bw_ghostlock_fix.py'
python3 -B tools/scripts/compare_phase5bw_ghostlock_fix.py \
  --target artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c \
  --fixed-reference artifacts/phase5/public-source-review/linux-rtmutex/linux-stable-v6.1.175.c \
  --output artifacts/phase5/phase5bw-ghostlock-fix-applicability-20260804-01
```

輸出 `comparison.json` 的 SHA-256：
`b1e1b0298d4a2e24707c8934dcb8b731ffb38ff630c82efe881c0ed86ca012bd`。

## 安全界線與判定

- **已證實**：PS7331 source 語意為修補前形態。
- **高可信推論**：PS7331 是 GhostLock 的 source/config/Image exposure
  candidate；升級至 PS7331 不能以此證據宣稱已修補。
- **待驗證**：live trigger、corruption、control-flow、root。
- **已排除**：本階段沒有執行裝置端 race、kernel memory access、ioctl、
  payload、提權或 boot/partition mutation，因此不能把任何結果稱為 live
  root PoC。
- **因風險拒絕測試**：任何以 CVE-2026-43499 觸發 kernel memory corruption
  或取得 root 的操作；其失敗模式不可由 ADB 保證還原，且會跨越本專案的安全
  邊界。
