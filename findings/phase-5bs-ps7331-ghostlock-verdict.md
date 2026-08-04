# Phase 5BS：PS7331 GhostLock source／boot Image 確認

日期：2026-08-04
範圍：只分析 Fire OS 7.3.3.1／PS7331 的官方 source 與本機保存的
official OTA-derived boot image；不分析 PS7330、不執行 exploit、不刷機。

## Executive verdict

### 已證實

1. PS7331 exact build-selected source
   `kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c` 的 SHA-256 是
   `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde`。
2. 重新執行 source semantics checker 顯示：

   ```text
   remove_waiter(): lines 1079–1129
   current_pi_blocked_on_cleanup: true
   waiter_task_reference_in_remove_waiter: false
   proxy_error_remove_waiter_call_present: true
   classification: PRE_FIX_CURRENT_TASK_CLEANUP_PATTERN
   ```

3. fixed reference 的 SHA-256 是
   `c307ed54156d1f16e82387df7b214445dddf27be8a880f31575f698ca07d880a`，其
   `remove_waiter()` 使用 `waiter->task`，且沒有 current-task cleanup。
4. PS7331 boot image SHA-256 是
   `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b`。
   既有 sanitized static Image analysis 的三個關鍵 marker 均存在：
   `remove_waiter` current-task source、current-task blocked-on clear，以及
   proxy error path 呼叫 `remove_waiter`。
5. 新 verifier 對 boot hash、source JSON、sanitized Image pattern CSV 與
   semantic comparison JSON 的所有檢查均通過，結果位於
   `artifacts/phase5/phase5bs-ps7331-evidence-verification-20260804-01/`。

### 高可信推論

**PS7331 的官方 source 與已檢查 boot Image 一致顯示：CVE-2026-43499 的
`waiter->task` 修補沒有出現在目前檢查的 PS7331 kernel function。** 因此
「升級到 7.3.3.1 就能修好 GhostLock」目前是不成立的研究假設。

這比單純 source review 更強，因為同時有：

```text
PS7331 exact source  ── pre-fix
PS7331 inspected Image ── pre-fix-consistent
fixed reference ── waiter-task
```

### 待驗證

- PS7331 在裝置上實際啟動後的 runtime exploitability。
- 是否存在其他未檢查的 PS7331 kernel copy、release-CI backport 或不同 boot
  artifact。
- GhostLock 的 Android 9／MT8183 觸發條件是否足以形成 privilege transition。

### 已排除／不採用

- 將 Android boot header `kernel_offset=0x800` 當成 runtime exploit offset。
- 將 `waiter->task` 修補語意誤寫成已取得 root。
- 將 source／Image marker 結果誤稱為 live PoC 成功。

### 因風險拒絕測試

沒有執行 futex race、kernel memory access、native root payload、未知 ioctl、
fastboot、OTA、boot image 寫入、BROM/DA、preloader/LK 或任何分割區操作。

## 關鍵 source 對照

PS7331 `remove_waiter()`（lines 1079–1129）包含：

```c
raw_spin_lock_irqsave(&current->pi_lock, flags);
rt_mutex_dequeue(lock, waiter);
current->pi_blocked_on = NULL;
raw_spin_unlock_irqrestore(&current->pi_lock, flags);
...
rt_mutex_adjust_prio_chain(..., current);
```

fixed reference 的對應語意改為以 `waiter_task = waiter->task` 取得 task，
並在該 task 的 `pi_lock` 下清除其 blocked-on 狀態，再把 `waiter_task` 傳入
priority-chain adjustment。

這是漏洞修補的核心語意；沒有需要或允許輸出 runtime address、offset 或
payload 才能完成此判定。

## Binary evidence scope

既有 PS7331 Image review 使用已保存的 reconstructed ELF 與 address-sanitized
pattern output；重建 metadata 記錄：

- decompressed Image SHA-256：
  `10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d`；
- reconstructed ELF SHA-256：
  `fd9424539a6e005a948f713965c09a3a61996be6481ca1fb7e83469b60e3dc49`；
- analysis output deliberately omits absolute addresses, branch targets,
  gadget data and exploit offsets.

新 verifier 沒有重新執行 ELF；它只核對保存的 input hash、pattern 與 semantic
verdict，因此不把 verifier 本身誤稱為第二次 binary disassembly。

## 最終判定

| 問題 | 判定 |
|---|---|
| PS7331 source 是否含 GhostLock fix？ | **已證實：否，檢查的 exact source 為 pre-fix** |
| PS7331 inspected boot Image 是否與 fix 一致？ | **已證實：否，pattern 與 pre-fix source 一致** |
| PS7331 是否已證明可被 GhostLock root？ | **待驗證；沒有 live PoC** |
| 升級 PS7331 是否值得作 GhostLock remediation？ | **高可信推論：不值得作為此漏洞的修補升級** |
| 是否執行 7.3.3.1 刷機／PoC？ | **否，因風險拒絕** |

## Reproduction

```sh
python3 -B tools/scripts/check_phase5_ghostlock_source_semantics.py \
  --source artifacts/phase5/exact-kernel-source-review-7331-nested-platform-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c \
  --output artifacts/phase5/phase5bs-ps7331-source-semantic-recheck-YYYYMMDD-NN/ps7331.json

python3 -B tools/scripts/verify_phase5bs_ps7331_ghostlock_evidence.py \
  --boot-image firmware/extracted/PS7331/boot.img \
  --source-result artifacts/phase5/phase5bs-ps7331-source-semantic-recheck-YYYYMMDD-NN/ps7331.json \
  --image-patterns artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/instruction-patterns.csv \
  --semantic-comparison artifacts/phase5/ps7331-source-binary-semantic-20260804-01/semantic-comparison.json \
  --output artifacts/phase5/phase5bs-ps7331-evidence-verification-YYYYMMDD-NN
```
