# Phase 5BU：PS7331 embedded kernel config 與 GhostLock source-path reachability

日期：2026-08-04
範圍：只分析 PS7331 官方 `boot.img` 解出的 kernel `IKCONFIG`、官方
PS7331 build-selected source，以及已保存的 address-sanitized Image pattern。

## 結論

### 已證實

- PS7331 embedded kernel config 包含：
  - `CONFIG_FUTEX=y`（`kernel.config:169`）
  - `CONFIG_RT_MUTEXES=y`（`kernel.config:248`）
  - `CONFIG_PREEMPT=y`（`kernel.config:363`）
  - `CONFIG_PREEMPT_COUNT=y`（`kernel.config:364`）
  - `CONFIG_ARM64_4K_PAGES=y`（`kernel.config:350`）
  - `CONFIG_ARM64_VA_BITS=39`（`kernel.config:353-355`）
  - `CONFIG_RANDOMIZE_BASE=y`（`kernel.config:431`）
  - `CONFIG_KALLSYMS=y`（`kernel.config:163`）
  - `CONFIG_SECCOMP=y`（`kernel.config:411`）
- `CONFIG_DEBUG_RT_MUTEXES` 在 `kernel.config:4184` 明確為未啟用；這是
  debug instrumentation 狀態，不代表 `RT_MUTEXES` 關閉。
- build-selected PS7331 source 的 `futex.c` 仍包含
  `FUTEX_WAIT_REQUEUE_PI`／`FUTEX_CMP_REQUEUE_PI` dispatch、
  `futex_requeue()` 與 `rt_mutex_start_proxy_lock()` 呼叫。
- 已保存的 PS7331 Image pattern 也找到：
  `futex_requeue`、`rt_mutex_start_proxy_lock`、`remove_waiter`，以及
  `remove_waiter` 的 current-task source／blocked-on cleanup marker。

### 高可信推論

PS7331 inspected kernel 同時具備：

```text
FUTEX + RT_MUTEX config
        ↓
FUTEX_REQUEUE_PI source dispatch
        ↓
rt_mutex_start_proxy_lock()
        ↓
remove_waiter() pre-fix cleanup
```

因此，GhostLock 的 source-level path 在 PS7331 kernel 中具備高可信的
編譯／可達性證據；這比只看 source archive 更強。

### 待驗證

- 真機上是否能以合法 user-space workload 穩定進入特定 proxy-lock failure
  interleaving。
- 該 interleaving 是否可導致 memory corruption、control-flow effect 或
  privilege transition。
- Amazon／MediaTek release-CI 是否對保存的 Image 做過未記錄的 binary
  transformation。

### 已排除／不應混稱

- `CONFIG_FUTEX_PI` 沒有獨立 literal，不代表 PI path disabled；此舊 kernel
  tree 的 PI dispatch 由 source path 與 `CONFIG_FUTEX`／`RT_MUTEXES` 支持。
- `CONFIG_RANDOMIZE_BASE=y`、VA39 或 boot header address 不是 runtime
  exploit offset。
- source/config reachability 不是 live exploitability，也不是 root 證明。

### 因風險拒絕測試

沒有執行 futex race、故意造成 kernel memory corruption、kernel memory
read/write、root payload、未知 ioctl、bootloader、OTA、fastboot 或任何
分割區寫入。這些不是「只會重啟」的可控假設。

## 證據來源

### Embedded config

- File: `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config`
- SHA-256: `eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04`
- Metadata: `artifacts/phase5/ps7331-ikconfig-20260804-01/metadata.json`
- Decompressed Image SHA-256: `10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d`

### Source

- `rtmutex.c` SHA-256:
  `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde`
- `futex.c` SHA-256:
  `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96`
- Source/config result:
  `artifacts/phase5/phase5bu-ps7331-embedded-config-reachability-20260804-01/`

### Image pattern

- `symbol-presence.csv` reports `remove_waiter`,
  `rt_mutex_start_proxy_lock`, `rt_mutex_finish_proxy_lock` and
  `futex_requeue` present.
- `instruction-patterns.csv` reports the current-task cleanup and proxy error
  call markers.
- No addresses, branch targets, gadgets or payload data are included.

## 判定矩陣

| 問題 | 判定 |
|---|---|
| PS7331 kernel 啟用 FUTEX？ | **已證實** |
| PS7331 kernel 啟用 RT_MUTEX？ | **已證實** |
| PS7331 source 有 PI requeue/proxy path？ | **已證實** |
| inspected Image 有對應 function markers？ | **高可信推論／已保存 pattern 支持** |
| `remove_waiter()` 是 upstream fixed `waiter->task` 版本？ | **已證實：否** |
| runtime race 可達？ | **待驗證** |
| runtime exploitability？ | **待驗證** |
| root／UID 0？ | **未證明** |

## 下一個合理研究邊界

若要繼續保持可歸因與可重現，下一步應是離線建立 source-level regression
model，或在隔離的非裝置 kernel test environment 觀察合法 futex PI API 的
錯誤處理；不應把未知 exploit payload 直接送入 Android kernel。PS7331
目前已具備「未修補 + path enabled + Image marker consistent」的最大安全
靜態證據集合。
