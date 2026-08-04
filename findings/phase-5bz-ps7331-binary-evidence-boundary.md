# Phase 5BZ：PS7331 binary evidence boundary

日期：2026-08-04
範圍：只分析 Fire OS 7.3.3.1／PS7331 保存的官方 boot image、其
address-sanitized `rtmutex` marker、PS7331 exact source 與 embedded IKCONFIG。
不分析 PS7330、不執行 exploit、不刷寫裝置。

## Executive verdict

### 已證實

1. 保存的 PS7331 decompressed kernel `Image`（SHA-256
   `10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d`）的
   address-sanitized binary output 同時包含：

   - `remove_waiter` 的 current-task source marker；
   - `remove_waiter` 經由該 current-task register 清除 blocked-on 欄位的
     marker；
   - `rt_mutex_start_proxy_lock` 的 `remove_waiter` proxy-error-path marker。

   這三個 marker 與 PS7331 source 的 pre-primary-fix 語意一致。原始 marker
   輸出 SHA-256 為
   `0ee3da7513051f2fa32b221918c6e671bc78b2a8e192fa0ab7ad65cc6e53475d`。

2. 同一份 PS7331 IKCONFIG（SHA-256
   `eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04`）確認
   `CONFIG_FUTEX=y`、`CONFIG_RT_MUTEXES=y`、`CONFIG_PREEMPT=y`、
   `CONFIG_SECCOMP=y`、`CONFIG_SECCOMP_FILTER=y`、
   `CONFIG_RANDOMIZE_BASE=y`、`CONFIG_KALLSYMS=y`，以及 ARM64 4K/VA39。
   這是 source/config/image reachability 證據，不是 exploitability 或 root
   證據。

3. PS7331 source fix-chain result（SHA-256
   `4e15b1302f3b3b3691fe3310298f639207365c3c78c6afece780fdb2791667d9`）確認：

   - `task_blocks_on_rt_mutex()` 的 early deadlock return 位於
     `waiter->task = task` 之前；
   - `rt_mutex_start_proxy_lock()` 的 wrapper 仍有 conditional
     `remove_waiter(lock, waiter)`；
   - source 仍為 primary GhostLock fix 前的 `current->pi_blocked_on` cleanup。

### 高可信推論

PS7331 檢查到的 signed-kernel code path 沒有呈現 CVE-2026-43499 的
`waiter->task` primary fix。這個結論現在由 source、IKCONFIG 與保存的 Image
marker 三者共同支持，不再只依賴 build date 或 source archive。

### 待驗證

follow-up guard 的 binary-level 狀態仍未驗證。保存的 parser metadata 明確說明
reconstructed ELF 與 raw disassembly 不保存在 repo，且 marker output 刻意省略
branch target、絕對位址及 return-value branch 關係。因此本輪只能說
`NOT_OBSERVABLE_FROM_SAVED_SANITIZED_OUTPUT`，不能把這個缺口推成 guard 已存在或
已缺失。

### 已排除／不採用

- Android boot header 的 `kernel_offset=0x800` 不是 runtime exploit offset。
- `CONFIG_RANDOMIZE_BASE=y`、VA39 或 kernel symbols 的存在，不等於可取得
  kernel address，也不等於可以建立 exploit。
- Source/Image marker 的一致性不等於已觸發 race、記憶體破壞、credential
  overwrite 或 root。
- `CVE-2026-43503` 與本輪 GhostLock `rtmutex` 問題不是同一條漏洞路徑。

## Evidence map

| Evidence ID | Source | Observation | 判定 |
|---|---|---|---|
| P5BZ-001 | `artifacts/phase5/ps7331-boot-image-inspection-20260804-01/boot-image-metadata.json` | PS7331 boot image metadata；boot image SHA-256 `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` | 已證實（artifact scope） |
| P5BZ-002 | `.../ps7331-rtmutex-static-review-20260804-01/instruction-patterns.csv` | 三個 primary pre-fix binary markers 均存在 | 已證實（saved binary output scope） |
| P5BZ-003 | `.../phase5by-ps7331-ghostlock-fix-chain-20260804-02/fix-chain.json` | early return、waiter assignment 順序與 proxy cleanup call | 已證實（source scope） |
| P5BZ-004 | `.../ps7331-rtmutex-static-review-20260804-01/parser-metadata.md` | raw reconstructed ELF/disassembly 刻意不保存；只保留脫敏 pattern | 已證實（evidence boundary） |
| P5BZ-005 | `.../ps7331-ikconfig-20260804-01/kernel.config` | futex/rtmutex、preemption、ASLR、seccomp 與 ARM64 config | 已證實（embedded-config scope） |
| P5BZ-006 | `artifacts/phase5/phase5bz-ps7331-binary-evidence-boundary-20260804-01/analysis.json` | verifier 輸出 `PRIMARY_PRE_FIX_MARKERS_CONFIRMED_FOLLOW_UP_BINARY_UNRESOLVED` | 已證實（reproducible host result） |
| P5BZ-007 | 本報告安全邊界 | 沒有 device I/O、futex race、kernel memory、payload、boot/partition write | 已證實 |

## Primary fix 與 follow-up guard 的分層

```
PS7331 exact source
  ├─ task_blocks_on_rt_mutex(): early -EDEADLK
  │    └─ waiter->task assignment occurs later
  └─ rt_mutex_start_proxy_lock(): conditional remove_waiter()

PS7331 saved Image markers
  ├─ remove_waiter(): current-task source + current-task clear
  └─ proxy path: remove_waiter call

Saved artifact boundary
  └─ no raw return/branch relation
       └─ follow-up guard: unresolved at binary level
```

NVD 對 CVE-2026-53163 的描述也把兩個條件分開：early deadlock 可能留下
未 armed 的 waiter，且 wrapper 的 cleanup 條件需要因 `try_to_take_rt_mutex()`
而收緊。[NVD CVE-2026-53163](https://nvd.nist.gov/vuln/detail/CVE-2026-53163)

NVD 對 CVE-2026-43499 描述的 primary defect 是 proxy rollback 使用
`current` 而非 `waiter->task`。[NVD CVE-2026-43499](https://nvd.nist.gov/vuln/detail/CVE-2026-43499)

## 可重現流程

這些命令只讀取已保存檔案，不連接裝置：

```sh
python3 -B -m unittest tests.test_phase5bz_ps7331_binary_boundary

python3 -B tools/scripts/analyze_phase5bz_ps7331_binary_boundary.py \
  --patterns artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/instruction-patterns.csv \
  --summary artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/summary.json \
  --source-result artifacts/phase5/phase5by-ps7331-ghostlock-fix-chain-20260804-02/fix-chain.json \
  --parser-metadata artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/parser-metadata.md \
  --kernel-image artifacts/phase5/ps7331-boot-image-inspection-20260804-01/kernel.Image \
  --kernel-config artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config \
  --output artifacts/phase5/phase5bz-ps7331-binary-evidence-boundary-20260804-01
```

## 目前不能宣稱的事情

本輪不能宣稱：

- PS7331 上已成功執行 GhostLock PoC；
- 任何 crash、UAF、KASLR defeat、kernel control 或 temporary root；
- 可以由保存的 marker 反推出裝置專用 offset、gadget 或 payload；
- 升級、刷入或改造 PS7331 boot image 後必然取得 root。

要把「靜態 pre-fix」提升為「live PoC 已確認」，需要在實機觸發 kernel race
並觀察 kernel/runtime 效果；這類操作可能造成 kernel panic、資料遺失或無法
恢復，且會進入 exploit/privilege-escalation 與高風險 boot-chain 範圍，本專案
不執行。

## 結論

對 PS7331 而言，最強且可重現的安全結論是：

> **已證實存在與 GhostLock primary pre-fix 語意一致的 source 與 signed-Image
> marker；follow-up guard 在保存的 binary 脫敏範圍內無法判定；runtime
> exploitability 與 root 仍未證明。**
