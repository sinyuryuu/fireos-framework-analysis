# Phase 5CR：PS7331 Fire libc futex helper analysis

日期：2026-08-04
裝置：Amazon Fire HD 10／`KFTRWI`／`trona`／MT8183
Build：`Amazon/trona/trona:9/PS7331.4463N/0031575863172:user/amz-p,release-keys`
方法：只讀 ADB pull、主機端 ELF symbol/disassembly review
安全狀態：沒有在裝置執行 native code、futex、race、ioctl、kernel memory access 或 root payload。

## Executive result

這是本專案目前最直接的 Fire userspace 證據。實機 `/system/lib64/libc.so` 顯示：

1. Fire libc 包含隱藏的 `__futex_wait_ex` 與 `__futex_pi_lock_ex` helper。
2. `pthread_cond_wait`、`pthread_cond_timedwait` 與
   `pthread_cond_timedwait_monotonic_np` 的 call sites 都指向
   `__futex_wait_ex`。
3. PI mutex lock path 的 `PIMutexTimedLock` 指向
   `__futex_pi_lock_ex`，後者再經由 libc `syscall` helper 進入 kernel
   futex interface。
4. 本輪 bounded symbol/control-flow search 沒有在 Fire libc 建立
   `FUTEX_WAIT_REQUEUE_PI`／`FUTEX_CMP_REQUEUE_PI` caller；這是 negative
   observation，不是整個系統不存在 caller 的證明。

因此，研究結論更新為：

```text
Fire libc ordinary pthread condvar → generic futex wait/wake: confirmed
Fire libc PI mutex helper → PI lock syscall boundary: confirmed
Fire libc → requeue-PI caller: not established
Fire PS7331 runtime identity mismatch / wrong cleanup: unobserved
GhostLock live exploit / root: unproven and not executed
```

## 1. Artifact provenance

| Artifact | Remote path | Size | SHA-256 | Observation |
|---|---|---:|---|---|
| Fire libc | `/system/lib64/libc.so` | 1,126,608 | `0899e7cde39ccae24a3ba7e9f5433922a30f03ed93744af87e053639ce076681` | ELF AArch64, not stripped |
| linker64 | `/system/bin/linker64` | 1,741,640 | `124745b0cac2fa1511cd903a3982108109d8c8f38e77c63df3e97b026e6ee21b` | ELF AArch64 |
| app_process64 | `/system/bin/app_process64` | 68,960 | `c075e6bbef31b2ae03ef6336b8d605c6f430e49bf25444c44aea0563647ec01e` | ELF AArch64 |

Raw local capture:

`artifacts/phase5/phase5cr-fire-native-20260804-02/`

The capture used serial `G001LT0511550CFT`, checked ADB state `device`, recorded
`getprop`, listed the fixed paths, and used only `adb pull`. The raw capture is
not staged with this report; its hashes and commands remain in the local evidence
directory.

The reproducible host-side symbol/call-edge analysis is:

`artifacts/phase5/phase5cr-fire-libc-analysis-20260804-01/`

## 2. Fire libc control-flow observations

### 2.1 Ordinary condition variables

The pulled ELF contains these symbols:

- `pthread_cond_wait` at text offset `0x82798`;
- `pthread_cond_timedwait` at `0x82800`;
- `pthread_cond_timedwait_monotonic_np` at `0x828b0`;
- hidden helper `_Z15__futex_wait_exPVvbibPK8timespec` at `0x22048`.

The three condition-variable functions call the generic wait helper. The helper
uses the libc `syscall` boundary, but its role is ordinary futex waiting. No
requeue-PI call edge was established in these call sites.

**判定：已證實，Fire libc binary scope。**

### 2.2 PI mutex helper

The pulled ELF also contains:

- hidden helper `_Z18__futex_pi_lock_exPVvbbPK8timespec` at `0x22128`;
- `_ZL16PIMutexTimedLockR7PIMutexbPK8timespec` at `0x83ed0`;
- `pthread_mutex_lock` at `0x83dd8`.

The PI mutex path calls the PI lock helper. This establishes that Fire libc has a
native PI-lock helper and a syscall boundary for PI locking. It does **not** show
that the helper performs futex requeue-PI, nor that any caller forms a proxy waiter
for `futex_requeue()`.

**判定：已證實，Fire libc PI-helper scope；不是 GhostLock runtime proof。**

### 2.3 Bounded negative search

The following host-side searches were performed over the pulled `libc`:

- `strings`: futex helper names, pthread condition-variable names and source
  labels;
- `nm -a` / `nm -D -a`: futex, pthread mutex/condition and syscall symbols;
- `objdump -d`: helper call sites and condition-variable/mutex control flow;
- `objdump -r`: relocation names containing futex/syscall/condition references.

No Fire libc symbol or call edge named as a requeue-PI helper was established.
The generic wait helper has additional callers such as semaphore, barrier,
reader/writer-lock and `pthread_once` paths; this broadens the ordinary helper's
use but does not change its non-requeue classification.
This is deliberately classified as **negative observation only**: a private
caller can use an indirect symbol, inline code, a different library, or a
vendor service that was not part of this three-file capture.

## 3. Relation to GhostLock gates

| Gate | Current state | Evidence |
|---|---|---|
| PS7331 kernel has futex/rtmutex proxy source path | Confirmed, source/config scope | Phase 5CO/5CP |
| Fire ordinary pthread condvar reaches requeue-PI | Not supported by pulled Fire libc call sites | `P5CR-004` |
| Fire libc exposes PI lock helper | Confirmed | `P5CR-002`, `P5CR-003` |
| Fire libc PI mutex path creates requeue-PI proxy waiter | Not established | `P5CR-005` |
| Fire app/daemon outside libc calls requeue-PI | Not searched exhaustively | `P5CR-006` |
| `waiter->task != current` in stock runtime | Not observed | `P5CP-RUNTIME-001` |
| Wrong cleanup target / persistent residue | Not observed | `P5CP-RUNTIME-002` |
| Controlled memory effect or root | Unproven; not executed | `P5CR-SAFETY-001` |

The important refinement is that `__futex_pi_lock_ex` proves only a PI-lock
userspace boundary. GhostLock concerns the proxy requeue path, which is a
different semantic operation. These must not be conflated.

## 4. Next safe analysis target

The next useful step is another **offline-only** inventory of already readable
Amazon/vendor native libraries and system services, looking for indirect futex
references or private synchronization wrappers. It should record only symbol
names, caller/callee relationships and package provenance. It must not run the
library, invoke its exported functions, construct syscall arguments, or test a
race on the tablet.

## 5. Status labels

### 已證實

- The exact Fire PS7331 libc contains generic futex wait and PI-lock helpers.
- Fire pthread condition variables use the generic wait helper in the inspected
  binary.
- Fire PI mutex code reaches the PI-lock helper in the inspected binary.

### 高可信推論

- Ordinary Fire pthread condition variables are not the direct requeue-PI entry
  needed by GhostLock.

### 待驗證

- A Fire/vendor native library or daemon outside the three pulled files may call
  requeue-PI through an indirect/private path.
- Fire app-domain seccomp policy may still deny or permit a native route; this was
  not changed or probed with a trigger.

### 已排除或不支持

- `pthread_cond_wait()` alone as proof of a GhostLock requeue-PI trigger.
- `__futex_pi_lock_ex` alone as proof of a requeue-PI proxy waiter.

### 因風險拒絕測試

- Executing the helper or any futex operation on the tablet.
- Building/running a race reproducer or root payload.
- Opening kernel device nodes, using unknown ioctl, reading/writing kernel memory,
  or modifying boot/system partitions.
