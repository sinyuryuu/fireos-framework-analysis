# Phase 6C：PS7331 GhostLock source／config／image／runtime 一致性稽核

## 目的與限制

本輪把四類證據分開核對：

1. PS7331 GPL source 的 exact control-flow landmarks；
2. 從 PS7331 boot Image 擷取的 embedded kernel config；
3. 保存的 boot image metadata；
4. 已完成的唯讀 runtime／Phase 6A 報告。

稽核器只在主機上讀取文字、JSON 與雜湊。沒有編譯或執行 kernel／ELF，沒有
呼叫 futex，沒有建立 waiter／thread，沒有安排 race，沒有接觸 ADB，沒有讀寫
kernel memory，也沒有產生 exploit 或 root payload。

工具：`tools/scripts/audit_phase6c_ghostlock_consistency.py`
Canonical artifact：
`artifacts/phase6c/phase6c-ghostlock-consistency-20260804-05/`

## 輸入 provenance

| Input | SHA-256 |
|---|---|
| `kernel/futex.c` | `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96` |
| `kernel/locking/rtmutex.c` | `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde` |
| `kernel/locking/rtmutex_common.h` | `b3456f9e83a1919e41a88a6638ad1e26ed9966e800c6efc823940df1151919fc` |
| extracted `kernel.config` | `eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04` |
| `trona_defconfig` reference | `09ca8dfc3b3b5e139482e3dd9976dae79547077fb750a4cbc778814f85ecaaac` |
| `boot-image-metadata.json` | recorded in artifact `consistency.json` |

Artifact outputs:

| File | SHA-256 |
|---|---|
| `consistency.json` | `1b54e6614d47032dd988b800805ce1940c36622abd5bc1019eec197021b49f8a` |
| `source-checks.csv` | `f3f1e6645deae37539a10c70ea13784b581030e66d56e5de9d49f24a6623fb4a` |
| `config-checks.csv` | `0bc1c4fe97a1cbaccc136dfd8afbe5efa91357518eb55541ee8a9278683eabed` |
| `result.md` | `c99086a11d9636d38c2c64d9a6d26e71bebdea7cf93b13e0fbb8929e9fbcd06e` |

## 結果

### 已證實：source control-flow landmarks

Host-only source scan found:

| Landmark | Location |
|---|---|
| `FUTEX_CMP_REQUEUE_PI` dispatch | `kernel/futex.c:3238` |
| dispatch to `futex_requeue(..., &val3, 1)` | `kernel/futex.c:3269` |
| no-waiter branch | `kernel/futex.c:1716` |
| proxy call | `kernel/futex.c:1963` |
| futex-side nonzero-return cleanup | `kernel/futex.c:1971` |
| proxy wrapper | `kernel/locking/rtmutex.c:1656` |
| proxy error cleanup | `kernel/locking/rtmutex.c:1683` |
| early `owner == task` branch | `kernel/locking/rtmutex.c:972` |
| `waiter->task = task` | `kernel/locking/rtmutex.c:977` |
| `current->pi_blocked_on = NULL` | `kernel/locking/rtmutex.c:1089` |
| waiter stack documentation | `kernel/locking/rtmutex_common.h:19` |

這確認 source 中存在被研究的 dispatch／proxy／cleanup 形狀，但不確認任何
runtime branch 已被執行。

### 已證實：embedded config gate

從 boot Image 擷取的 config 開啟：

- `CONFIG_ARM64=y`
- `CONFIG_MMU=y`
- `CONFIG_SMP=y`
- `CONFIG_PREEMPT=y`
- `CONFIG_FUTEX=y`
- `CONFIG_RT_MUTEXES=y`
- `CONFIG_SLUB=y`
- `CONFIG_ION=y`、`CONFIG_MTK_ION=y`
- `CONFIG_RANDOMIZE_BASE=y`
- `CONFIG_PANIC_ON_OOPS=y`
- `CONFIG_FTRACE=y`

同一份 config 沒有開啟 `CONFIG_KASAN`、`CONFIG_DEBUG_INFO`、
`CONFIG_USERFAULTFD` 或 `CONFIG_FUNCTION_TRACER`。這說明 stock image 的
核心能力與限制；它不是 runtime mismatch 或 root 的證明。

### 高可信推論：provenance 一致，但不是 live exploit 證明

source、embedded config 與 boot metadata 在版本／架構／功能 gate 上一致，足以
支持「PS7331 是合理的靜態分析目標」。但它不能推出：

- untrusted app 能形成 matching `WAIT_REQUEUE_PI` waiter；
- `waiter->task != current` 在實機發生；
- proxy error branch 或錯誤 cleanup 被執行；
- residue 被後續 consumer 使用；
- 記憶體破壞、kernel panic 或權限提升發生。

### Runtime evidence status

既有 Phase 6A 只證明 ordinary untrusted app 可完成 uncontended PI
lock/unlock；它沒有發出 `FUTEX_CMP_REQUEUE_PI`。既有唯讀 capture 也沒有
requeue return、proxy waiter 或 identity mismatch 證據。稽核器的結果為：

| Claim | Status |
|---|---|
| source chain present | **已證實** |
| config supports core path | **已證實** |
| requeue-PI runtime return observed | **待驗證／目前否定證據** |
| proxy waiter observed | **待驗證／目前否定證據** |
| cleanup residue | **待驗證** |
| memory effect | **待驗證** |
| privilege transition／temporary root | **未證實** |

## 公開 GhostLock 專案的相容性結論

`datfooldive/ghostlock-emerald` 的公開 README 將其定位為 Poco M6 Pro、
MT6789、Android 16／kernel 6.12.30 的 root exploit；這與本研究的 MT8183、
Linux 4.4.146、PS7331 image 不同。因此該專案可作為研究流程與 provenance
對照，不可視為 PS7331 的 drop-in POC。任何移植或執行 exploit payload 都不在
本輪範圍內。

## 因風險拒絕測試

即使限制成單執行緒、單次呼叫，`FUTEX_CMP_REQUEUE_PI` 仍會進入正在研究的
核心 requeue-PI state machine，且 source 顯示 PI state／proxy path 不是純
read-only switch probe。因此本輪不在 stock device 執行該 syscall，也不執行
paired waiter、race、single-shot panic、heap shaping、ION／pipe 佔位、KASLR
live extraction、kernel memory operation 或 privilege payload。

## 下一個安全 gate

下一個可做的 gate 是 LAB_ONLY：在隔離環境以 debug symbols／KASAN 對保存 source
做 control-flow instrumentation，僅觀察 state-machine invariants。現有 readiness
audit 已顯示 host 缺少完整 QEMU AArch64／KASAN／DEBUG_INFO 組合；在該 gate 通過
前，不應把任何測試 binary 或修改過的 image 放到 PS7331。

## 重現

```sh
python3 tools/scripts/audit_phase6c_ghostlock_consistency.py --dry-run \
  --source-root firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4 \
  --config artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config \
  --defconfig firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig \
  --boot-metadata artifacts/phase5/ps7331-boot-image-inspection-20260804-01/boot-image-metadata.json \
  --runtime-report findings/phase-6c-runtime-capture-20260804-01.md \
  --phase6a-report findings/phase-6a-untrusted-app-pi-smoke-test.md \
  --output artifacts/phase6c/phase6c-ghostlock-consistency-YYYYMMDD-NN
```
