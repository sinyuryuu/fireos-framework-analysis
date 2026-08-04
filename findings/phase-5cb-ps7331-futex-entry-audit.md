# Phase 5CB：PS7331 futex/PI entry and direct gate audit

日期：2026-08-04
範圍：Fire OS 7.3.3.1／PS7331 exact `mt8183/4.4` source 與 embedded
IKCONFIG；host-only。沒有執行 syscall、futex race、PoC、root 或裝置操作。

## Executive verdict

### 已證實（source scope）

PS7331 source 保留以下完整控制流：

```text
SYSCALL_DEFINE6(futex)       futex.c:3275
  -> do_futex()               futex.c:3218
  -> FUTEX_*_REQUEUE_PI       futex.c:3237-3269
  -> futex_requeue()          futex.c:1756
  -> rt_mutex_start_proxy_lock()  futex.c:1963-1965
  -> remove_waiter()          rtmutex.c:1684
```

`do_futex()` 對 PI/requeue-P​​I command 有 `futex_cmpxchg_enabled` feature gate；
這是功能／架構能力檢查，不是 Android UID permission check。

在以下 scoped functions 中沒有觀察到直接的 `capable()`、`ns_capable()` 或
`security_*()` 呼叫：

- `SYSCALL_DEFINE6(futex)`；
- `do_futex()`；
- `futex_requeue()`；
- `rt_mutex_start_proxy_lock()`。

這表示 source 層沒有顯式 capability gate，但不表示普通 Android process
必然能通過 SELinux、seccomp、Bionic ABI、架構 feature 或其他 runtime policy。

### 高可信推論

PS7331 的 GhostLock 相關 path 不只是孤立的 `rtmutex.c` pattern；在 exact
source 中確實有 Android kernel futex syscall 到 PI proxy path 的連接。這比
只看到 `CONFIG_FUTEX=y` 更強，但仍是 source reachability，不是 runtime
trigger 或 privilege transition 證明。

### 待驗證

- `CONFIG_HAVE_FUTEX_CMPXCHG` 的 PS7331 arm64 build result；保存的 selected
  source members 未包含完整 arch header/Kconfig 展開結果；
- installed Android SELinux policy 對測試 process 的 syscall／futex 行為；
- seccomp filter、Bionic wrapper 與 process domain 是否改變實際可達性；
- signed Image 的 source path 是否完整匹配（既有 Image marker 已支持
  `rtmutex` primary pre-fix，但未保存 raw syscall branch disassembly）。

### 已排除／不採用

- 不能把「沒有 `capable()`」解讀成 SELinux bypass。
- 不能把 source path 解讀成可取得 root。
- 不提供 syscall argument sequence、race timing、kernel address、offset、
  gadget 或 payload。

## Configuration context

PS7331 embedded IKCONFIG（SHA-256
`eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04`）包含：

- `CONFIG_FUTEX=y`；
- `CONFIG_RT_MUTEXES=y`；
- `CONFIG_SECCOMP=y`；
- `CONFIG_SECURITY_SELINUX=y`。

因此 policy 層必須獨立驗證；kernel source 中的 entry/path evidence 不足以
替代裝置上的 SELinux/seccomp observation。

## Evidence

| Evidence ID | File | Observation | Confidence |
|---|---|---|---|
| P5CB-001 | `.../kernel/futex.c` SHA `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96` | futex syscall、dispatch、requeue 與 proxy call | Confirmed, exact source |
| P5CB-002 | `.../kernel/locking/rtmutex.c` SHA `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde` | `rt_mutex_start_proxy_lock()` 與 `remove_waiter()` | Confirmed, exact source |
| P5CB-003 | `.../kernel.config` SHA `eefb8db484f65e196a7bb401ae0165f434f08b13041ae6762917e284d013d04` | futex/rtmutex/seccomp/SELinux config | Confirmed, embedded config |
| P5CB-004 | `artifacts/phase5/phase5cb-ps7331-futex-entry-audit-20260804-01/entry-audit.json` | reproducible source entry result | Confirmed |
| P5CB-005 | scoped function search | no direct capability/security hook observed | Confirmed, scoped only |
| P5CB-006 | safety boundary | no device I/O or PoC execution | Confirmed |

## Final classification

`SYSCALL_TO_PI_REQUEUE_PROXY_PATH_PRESENT` with
`NO_DIRECT_CAPABILITY_GATE_OBSERVED_IN_SCOPED_FUNCTIONS`, while
`userspace_policy_status=UNRESOLVED_FROM_KERNEL_SOURCE_ONLY`.

This advances PS7331 from static source/config applicability to a source-level
Android entry-path candidate. It still does not establish a live GhostLock
crash, kernel memory effect, root, or privilege gain.
