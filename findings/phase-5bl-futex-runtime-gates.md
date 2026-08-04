# Phase 5BL：PS7330 GhostLock runtime gate snapshot

日期：2026-08-04  
裝置：Amazon Fire HD 10 11th Gen／`KFTRWI`／`trona`／MT8183  
Test ID：`PHASE5BL-FUTEX-GATES-20260804-01`

## 結論

### 已證實

1. 裝置仍運行 `PS7330.4104N`、Linux `4.4.146+`、aarch64；目前採集 caller
   是 UID 2000 `shell`、SELinux domain `u:r:shell:s0`，SELinux 為 Enforcing。
2. shell 無法讀取 `/proc/kallsyms`；`/proc/kcore` 與 `/dev/kmem` 也未提供可用
   的 shell 讀取面。此次沒有從任何 procfs 或 device node 推導地址或 offset。
3. 選定 kernel sysctl 中，`perf_event_paranoid=3` 可讀；其餘多數值回傳
   `Permission denied`，另有部分 4.4 kernel 路徑不存在。這些失敗不能被解讀成
   對應 hardening 已開啟或關閉。
4. `/dev/ion` 與 `/dev/mtk_cmdq` 的節點 metadata 可由 `ls -lZ` 看見，但本輪
   沒有 `open()`、allocation、custom request、physical-address request 或 ioctl。
5. `/proc/kallsyms` 被拒絕後，futex/rtmutex symbol grep 沒有可用結果；這是
   visibility failure，不是 symbol absence。

### 高可信推論

- 目前 exact PS7330 的普通 shell runtime 沒有提供可直接用於 GhostLock offset
  或 KASLR 推導的 symbol/procfs surface；這使「只靠 ADB 計算並觸發」的路線缺少
  一個必要觀測面。
- Phase 5BF／5BJ 的 source、config 與 PS7331 inspected Image 仍支持
  GhostLock 的 source-level applicability；但本快照沒有把它提升為 exact PS7330
  signed-binary proof 或 exploitability proof。

### 待驗證

- exact PS7330 signed boot/Image 是否含同一 `remove_waiter()` compiled pattern；
  shell 目前無法讀取該 boot block。
- Amazon 是否在 source member 之外做過未公開 backport；現有 source/Image
  evidence 不能排除所有 vendor patch。

### 已排除

- 「`/dev/ion` 或 `/dev/mtk_cmdq` 節點存在，就代表 shell 可取得 root」：本輪
  只有 metadata，沒有權限轉換證據。
- 「futex symbol grep 沒有輸出，就代表 futex/rtmutex 沒有編譯」：procfs 讀取
  被拒絕，該推論不成立。
- 「PS7331 有 signed boot.img，就能直接作為 PS7330 的 GhostLock 觸發輸入」：
  PS7331 是相鄰版本，不能替代 exact PS7330 binary。

### 因風險拒絕測試

沒有執行 futex PI／requeue 觸發、kernel memory read/write、native root payload、
未知 ioctl、ION/CMDQ request、BROM/DA、fastboot、OTA、boot image 或分割區寫入。
這些不是「只會重啟」的測試；失敗可能造成 kernel panic、ADB 消失、資料損壞或
不可恢復狀態。

## 證據

| Evidence ID | 原始證據 | 觀察 | 信心 |
|---|---|---|---|
| `P5BL-RUNTIME-001` | `adb/phase5/PHASE5BL-FUTEX-GATES-20260804-01/identity.stdout.txt` | PS7330、4.4.146+、aarch64、shell UID 2000、SELinux Enforcing | 已證實，snapshot scope |
| `P5BL-RUNTIME-002` | `.../kernel_sysctls.stdout.txt` | 多數 kernel sysctl 對 shell denied；`perf_event_paranoid=3` | 已證實，permission scope |
| `P5BL-RUNTIME-003` | `.../proc_visibility.stdout.txt` | `/proc/kallsyms` denied；`/proc/kcore`、`/dev/kmem` 不可用 | 已證實，snapshot scope |
| `P5BL-RUNTIME-004` | `.../futex_symbols.stdout.txt` | symbol 查詢受 `/proc/kallsyms` denied 影響 | 已證實，negative observation only |
| `P5BL-RUNTIME-005` | `.../proc_visibility.stdout.txt` | ION/CMDQ node metadata；沒有 open/ioctl | 已證實，metadata scope |
| `P5BL-SAFETY-001` | `.../result.md`、`sha256sums.txt` | read-only capture，沒有 device mutation | 已證實 |
| `P5BF-SOURCE-001` | Phase 5BF source artifact | PS7331 build-selected `remove_waiter()` pre-fix marker | 已證實，source scope |
| `P5BF-CONFIG-001` | Phase 5BF captured config | `CONFIG_FUTEX=y`、`CONFIG_RT_MUTEXES=y` | 已證實，config scope |
| `P5BF-BINARY-001` | Phase 5BF PS7331 Image artifact | inspected PS7331 function pattern matches old current-task direction | 已證實，inspected-function scope |

## 可重現輸出

- 採集腳本：[`capture_phase5p_futex_gates.sh`](../tools/scripts/capture_phase5p_futex_gates.sh)
- 唯讀原始資料：[`PHASE5BL-FUTEX-GATES-20260804-01/`](../adb/phase5/PHASE5BL-FUTEX-GATES-20260804-01/)
- host-only 分析器：[`analyze_phase5bl_futex_gates.py`](../tools/scripts/analyze_phase5bl_futex_gates.py)
- 分析結果：[`phase5bl-futex-gates-analysis-20260804-01/`](../artifacts/phase5/phase5bl-futex-gates-analysis-20260804-01/)

分析器只讀取已封存輸出，不連線 ADB、不開啟 device node、不執行 source 或
payload；結果與輸入 hash 均保留。

## GhostLock 判定邊界

公開記錄把 CVE-2026-43499 定位在 futex PI 的 rtmutex proxy rollback；修補方向
是由 `current` 改用 `waiter->task`。這與 Phase 5BF／5BJ 的 source 與 PS7331
inspected Image 方向一致，但目前 exact PS7330 沒有 signed Image 可做同等級的
compiled confirmation。[NVD CVE-2026-43499](https://nvd.nist.gov/vuln/detail/CVE-2026-43499)

因此目前最準確的結論是：

```text
source/config reachability: high confidence
PS7331 inspected Image old-pattern: confirmed, adjacent-version scope
PS7330 signed-binary old-pattern: unverified
live exploitability/root: unverified and not tested
```

## 下一個安全且有價值的步驟

取得合法且完全匹配的 PS7330 signed boot/vmlinux/debug artifact，或完成可驗證的
官方 source-to-build provenance，做離線 function-level comparison。若只能透過
官方完整 OTA 讓裝置變成 PS7331，應另立完整更新與復原評估；不應把 standalone
`boot.img` 或第三方 MTK payload 當成等價方案。
