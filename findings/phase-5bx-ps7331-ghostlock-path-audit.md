# Phase 5BX：PS7331 GhostLock exact source path audit

日期：2026-08-04

## 結論

**已證實（PS7331 source/config scope）**：build-selected PS7331 source 包含
完整的 PI requeue/proxy-lock source path：

```text
FUTEX_WAIT_REQUEUE_PI / FUTEX_CMP_REQUEUE_PI
        ↓
futex_requeue()
        ↓
rt_mutex_start_proxy_lock(..., this->task)
        ↓
remove_waiter(lock, waiter)      [proxy error path]
        ↓
current->pi_blocked_on = NULL     [pre-fix semantic]
```

**已證實（static patch status）**：PS7331 `remove_waiter()` 的 cleanup 與
priority-chain task 仍是公開修補前形態；fixed reference 使用
`waiter->task`。本輪使用 build-selected source `-20260804-02` 重跑既有
host-only analyzer，結果為 `SOURCE_AND_CONFIG_REACHABILITY_CANDIDATE`。

**高可信推論**：若 PS7331 signed Image 與保存的 source/Image markers 一致，
該 kernel 具備 GhostLock 的 source-level exposure candidate。這不是 race
成功、memory corruption、kernel control 或 root 的證明。

**已排除／不採用**：目前沒有可歸因於 `KFTRWI/trona/MT8183/PS7331` 的公開
root payload。KoCleo `mtk-easy-su` 是舊式通用 `mtk-su`/Magisk wrapper，
其 pinned `mtk-su64` 已在本機相同裝置路徑失敗；不重跑相同 payload，也不把
LauncherHijack 的 foreground redirect 當作 GhostLock 或正式 HOME replacement。

## 精確 source 證據

### `futex.c`

檔案：
`artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/kernel/futex.c`

- `futex_requeue()` 定義：lines 1756–1989。
- proxy waiter 呼叫：lines 1959–1965，傳入 `this->task`。
- `FUTEX_WAIT_REQUEUE_PI` dispatch：lines 3237、3264。
- `FUTEX_CMP_REQUEUE_PI` dispatch：lines 3238、3268–3269。
- SHA-256：`ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96`。

### `rtmutex.c`

檔案：
`artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c`

- `remove_waiter()`：lines 1079–1129。
- current-task cleanup：line 1089。
- priority-chain call 使用 `current`：lines 1125–1126。
- `rt_mutex_start_proxy_lock()`：lines 1656–1691。
- proxy error path 呼叫 `remove_waiter(lock, waiter)`：line 1684。
- SHA-256：`6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde`。

### kernel config

檔案：`artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config`，SHA-256：
`eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04`。

- `CONFIG_FUTEX=y`：line 169。
- `CONFIG_RT_MUTEXES=y`：line 248。
- `CONFIG_PREEMPT=y`：line 363。
- `CONFIG_DEBUG_RT_MUTEXES` 未啟用：line 4184。

舊版 4.4 tree 沒有獨立 `CONFIG_FUTEX_PI` literal；本報告不把該字串缺失
解讀成 PI disabled，而是以 source dispatch 與 `FUTEX`/`RT_MUTEXES` config
作為 scope-bounded 判斷。

## 修補比對

fixed reference：
`artifacts/phase5/public-source-review/linux-rtmutex/linux-stable-v6.1.175.c`
（SHA-256 `c307ed54156d1f16e82387df7b214445dddf27be8a880f31575f698ca07d880a`）。

它在 `remove_waiter()` 中綁定 `waiter_task = waiter->task`，使用 waiter task
清除 `pi_blocked_on`，並將同一 task 傳給 priority-chain adjustment。這與
PS7331 的 `current` 版本不同。公開修補說明可參考 [NVD
CVE-2026-43499](https://nvd.nist.gov/vuln/detail/CVE-2026-43499) 與
[Linux stable patch](https://www.spinics.net/lists/stable/msg940408.html)。

## 公開 root／替代路線相容性

### KoCleo `mtk-easy-su`

公開 README 將它描述為使用 Magisk 與 `mtk-su` 的 bootless-root wrapper，並
警告 2020 年 3 月後的 firmware 可能阻擋該方法；其公開測試清單沒有
`KFTRWI`、`trona` 或 `MT8183`。[公開專案](https://github.com/KoCleo/mtk-easy-su)

既有 source metadata 顯示 pinned `mtk-su64` LFS object 與已執行的本機 binary
相同；本機測試結果為 `Failed critical init step 3`、exit code 1、沒有 UID 0。
這條 route 已是**相同 payload 的已測失敗**，不是本輪新候選。

### LauncherHijack

既有 pinned source 顯示它是 Accessibility／事件觀察器，然後 explicit-start
選定 launcher；它不修改 PackageManager HOME resolver。既有 controlled run
為 0/30 foreground handoff，因此只保留為歷史參考，不用未知 APK 或破壞
default-launcher state 補足 GhostLock 證據。

## 可重現命令

```sh
python3 -B tools/scripts/analyze_phase5bf_ghostlock_reachability.py --dry-run \
  --rtmutex artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c \
  --futex artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/kernel/futex.c \
  --config artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config \
  --fixed-reference artifacts/phase5/public-source-review/linux-rtmutex/linux-stable-v6.1.175.c \
  --output artifacts/phase5/phase5bx-ps7331-exact-path-audit-20260804-01
```

輸出：`artifacts/phase5/phase5bx-ps7331-exact-path-audit-20260804-01/`。

## 最終邊界

- **已證實**：PS7331 source/config 的 GhostLock path 與 pre-fix semantic。
- **高可信推論**：保存的 PS7331 Image markers 與此 source path 一致。
- **待驗證**：真機 race、UAF/memory effect、control-flow、root。
- **因風險拒絕測試**：futex trigger、kernel memory read/write、exploit
  payload、unknown ioctl、BROM/DA、preloader/LK patch、fastboot/OTA/partition
  write。這些不是「只會重啟」的可控測試。
