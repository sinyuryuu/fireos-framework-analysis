# Phase 5BF：GhostLock exact-target source/config reachability review

日期：2026-08-04

裝置：Amazon Fire HD 10 2021，`KFTRWI`／`trona`／MT8183

已安裝版本：Fire OS 7.3.3.0，`PS7330.4104N`

## 結論先行

### 已證實

1. 官方 PS7331 build-selected source member
   `kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c` 的
   `remove_waiter()`（source lines 1079–1129）仍寫入
   `current->pi_blocked_on = NULL`，而該函式範圍內沒有 `waiter->task` cleanup
   reference。
2. 同一 source 的 `rt_mutex_start_proxy_lock()`（lines 1656–1691）在 error
   path 呼叫 `remove_waiter(lock, waiter)`（line 1684）。
3. build-selected `futex.c` 包含 `FUTEX_WAIT_REQUEUE_PI`、
   `FUTEX_CMP_REQUEUE_PI`、`futex_requeue()` 與
   `rt_mutex_start_proxy_lock()` 的 source path；裝置保存的 kernel config 觀察到
   `CONFIG_FUTEX=y`（line 169）與 `CONFIG_RT_MUTEXES=y`（line 248）。
4. 與修補後參考 source 的對照中，`remove_waiter()` 使用
   `struct task_struct *waiter_task = waiter->task`，並對 waiter task 清理，沒有
   同一函式範圍的 `current->pi_blocked_on` cleanup。
5. 裝置目前仍是 PS7330、ADB state=`device`，HOME resolver 仍為
   `com.amazon.firelauncher/.Launcher`；本階段沒有 ADB mutation、升級、重啟或
   分割區操作。

### 高可信推論

- 以 source/config 邊界而言，PS7331 仍是 GhostLock 相關 PI／rtmutex 路徑的
  **source-and-config reachability candidate**。這表示「程式碼與設定看起來仍具備
  相關路徑」，不是可利用性、可重現性或 root 證明。
- 目前沒有足夠證據支持「升級至 PS7331 可修補 CVE-2026-43499」。PS7331 的
  build-selected source 與已檢查的 signed Image function pattern 都仍接近修補前
  cleanup 語意。
- 因 GhostLock 目的，現階段不建議把 PS7331 寫入裝置。若未來研究一般安全更新，
  必須把官方完整 OTA 當作獨立的 full-block system mutation，而不能把抽出的
  `boot.img` 當成等價或可逆升級。

### 待驗證

- 裝置上的 PS7330 signed boot block 目前無法以 shell 讀取，因此不能把 PS7331
  source 證據直接宣稱為目前 PS7330 signed binary 的精確 function proof。
- 本階段沒有編譯 source、執行 kernel、觸發 futex/rtmutex path 或驗證 runtime
  crash／privilege transition。
- PS7331 可能包含與 GhostLock 無關的其他安全修補；本報告不對整體安全性作判斷。

### 已排除／不採用

- 將 Android boot header 的 `kernel_offset=0x800` 當作 runtime kernel offset。
- 將 source path inventory 中的 Mali hrtimer diff 誤認為 rtmutex／GhostLock patch。
- 將 source/config candidate 誤稱為 root 或可直接執行的 exploit。
- 只寫入 PS7331 standalone `boot.img` 作為升級方案。

### 因風險拒絕測試

- GhostLock futex race、kernel memory corruption、root payload、offset/slide 推導。
- 未知 ioctl、kernel memory read/write、BROM/DA、preloader/LK/TEE 操作。
- fastboot/bootloader unlock、OTA sideload、boot/system/vendor 或其他分割區寫入。

## CVE 對照

公開 CVE 描述將 CVE-2026-43499 定位在 Linux futex PI／rtmutex proxy-lock rollback
路徑，修補重點是清理 waiter task，而不是呼叫者的 current task；參考：
[NVD CVE-2026-43499](https://nvd.nist.gov/vuln/detail/CVE-2026-43499)、
[上游 stable patch reference](https://www.spinics.net/lists/stable/msg940408.html)。
這些公開資料支持本報告的 source-level semantic comparison，但不會替代
KFTRWI／trona 的 signed-image 或 runtime 證據。

`CVE-2026-43503` 是另一條 Linux networking／skb 相關問題，不是本報告的
GhostLock rtmutex 路徑；參考：[Ubuntu CVE-2026-43503](https://ubuntu.com/security/CVE-2026-43503)。

## 證據鏈

| Evidence | 檔案 | 觀察 | 判定 |
|---|---|---|---|
| `P5BF-SOURCE-001` | `artifacts/phase5/exact-kernel-source-review-7331-nested-platform-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c` | `remove_waiter()` 清理 `current->pi_blocked_on`；proxy error line 呼叫它 | Confirmed，source scope |
| `P5BF-SOURCE-002` | `artifacts/phase5/exact-kernel-source-review-7331-nested-platform-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/futex.c` | PI requeue tokens、`futex_requeue()` 與 proxy-lock call site 存在 | Confirmed，source scope |
| `P5BF-CONFIG-001` | `adb/phase5/PHASE5AQ-DEVICE-CONFIG-20260804-02/kernel.config` | `CONFIG_FUTEX=y`、`CONFIG_RT_MUTEXES=y`；沒有把缺少的 literal `CONFIG_FUTEX_PI` 解讀成 disabled | Confirmed，captured-config scope |
| `P5BF-FIX-001` | `artifacts/phase5/public-source-review/linux-rtmutex/linux-stable-v6.1.175.c` | 對照版 `remove_waiter()` 取 `waiter->task` 清理 | Confirmed，reference scope |
| `P5BF-BINARY-001` | `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/summary.json` | 已保存的 PS7331 Image inspection 觀察到 current-task pattern 與 proxy call | Confirmed，inspected-function scope |
| `P5BF-DEVICE-001` | `adb/phase5/PHASE5BD-DEVICE-POSTCHECK-20260804-01/` | PS7330 fingerprint、ADB state、Fire Launcher resolver | Confirmed，snapshot scope |
| `P5BF-OTA-001` | `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/` | PS7331 是 full-block OTA，涉及 system/vendor/boot 及 boot-chain/firmware 成員 | Confirmed，metadata scope |
| `P5BF-MODEL-001` | `artifacts/phase5/ghostlock-reachability-review-20260804-04/reachability.json` | deterministic host-only analyzer 输出 candidate；明确关闭 device I/O、payload、address 与 execution | Confirmed，analysis scope |

## 精確 source observations

### PS7331 build-selected `rtmutex.c`

- SHA-256：`6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde`
- `remove_waiter()`：lines 1079–1129
- `current->pi_blocked_on = NULL`：line 1089
- `rt_mutex_start_proxy_lock()`：lines 1656–1691
- `remove_waiter(lock, waiter)`：line 1684

### PS7331 build-selected `futex.c`

- SHA-256：`ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96`
- `futex_requeue()`：line 1756
- proxy-lock call site：lines 1963–1965
- PI dispatch：lines 3237–3238、3264–3269

### Captured device config

- SHA-256：`9fae0dc507c20842b68f8d0c26b8db8fe7d86c7459acb29cfa5b622e2666cbc9`
- `CONFIG_FUTEX=y`：line 169
- `CONFIG_RT_MUTEXES=y`：line 248
- `CONFIG_PREEMPT=y`：line 363
- `CONFIG_RANDOMIZE_BASE=y`：line 431
- `CONFIG_ARM64_4K_PAGES=y`：line 350
- `CONFIG_ARM64_VA_BITS=39`：line 355

`CONFIG_FUTEX_PI` 沒有 literal line。由於本樹的 PI operations 是由 source
dispatch 與 `CONFIG_FUTEX`／`CONFIG_RT_MUTEXES` 關係觀察，本報告不把該缺行
當作「PI disabled」證據。

## PS7331 升級決策

| 問題 | 目前答案 | 信心 |
|---|---|---|
| PS7331 source 是否仍有相關 pre-fix semantic pattern？ | 是 | Confirmed，source scope |
| PS7331 inspected Image 是否顯示相同方向？ | 是 | Confirmed，inspected-function scope |
| PS7331 是否已證明修補 GhostLock？ | 否 | Confirmed，未達 remediation proof |
| PS7331 是否可能有其他安全更新？ | 可能 | Hypothesis／未做完整 security diff |
| 是否應為 GhostLock 單一目的升級？ | 不建議 | Strong evidence |
| 是否已執行升級？ | 否 | Confirmed |

官方 PS7331 OTA archive SHA-256 為
`9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`；其 metadata
與 updater script 已保存並雜湊。該 OTA 不是單純 boot image 替換，故本專案保留
完整 OTA 作為一般安全更新 A/B 的候選，不把它當作本輪可逆測試。

## 主機端重現

先查看計畫：

```sh
python3 tools/scripts/analyze_phase5bf_ghostlock_reachability.py \\
  --rtmutex artifacts/phase5/exact-kernel-source-review-7331-nested-platform-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c \\
  --futex artifacts/phase5/exact-kernel-source-review-7331-nested-platform-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/futex.c \\
  --config adb/phase5/PHASE5AQ-DEVICE-CONFIG-20260804-02/kernel.config \\
  --fixed-reference artifacts/phase5/public-source-review/linux-rtmutex/linux-stable-v6.1.175.c \\
  --output artifacts/phase5/ghostlock-reachability-review-new \\
  --dry-run
```

實際分析只能使用新的 output directory；工具拒絕覆寫既有輸出，且不會
連接 ADB、執行輸入檔、編譯 source、輸出 offset/address 或建立 payload。

既有結果：

- `artifacts/phase5/ghostlock-reachability-review-20260804-04/reachability.json`
  SHA-256：`71de526dc9aebe11d1a40b1f6cba664b2abb5be6e7ae21b27b666f10c1421d1e`
- `observations.csv` SHA-256：`97e6b7f84a94b7eff29e54edc8062ec2fca2430e53b7028796c9c8f32eb5c508`
- `result.md` SHA-256：`1c1ac1948b91017c9aceee2ecaad556b5ad041d5a41d726c4f6128b312cd4cd2`

## 安全界線與下一步

本階段不再需要重跑已失敗的 mtk-su，也不需要直接執行 GhostLock。若研究
目標改為「一般安全更新 A/B」，下一個安全步驟是先完成 PS7330／PS7331
framework、vendor 與 kernel security diff 的主機端報告；只有在研究者另行
決定要做裝置升級時，才提交完整 OTA 的 Level 3 風險報告。即使使用者已表示
願意承擔設備風險，本專案仍不會自動執行 exploit、bootloader、分割區寫入或
未知 ioctl。
