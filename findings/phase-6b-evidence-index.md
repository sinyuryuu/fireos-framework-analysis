# Phase 6B Evidence Index

| Evidence ID | Source | File | Observed result | Confidence |
|---|---|---|---|---|
| P6B-RO-001 | Read-only ADB | `adb/phase6b/PHASE6B-BOUNDARY-RO-20260804-01/getprop.stdout.txt` | PS7331 fingerprint、KFTRWI、security patch 2024-08-01 | Confirmed |
| P6B-RO-002 | Read-only ADB | `adb/phase6b/PHASE6B-BOUNDARY-RO-20260804-01/id.stdout.txt`, `getenforce.stdout.txt` | shell UID 2000；SELinux Enforcing | Confirmed |
| P6B-RO-003 | Read-only ADB | `adb/phase6b/PHASE6B-BOUNDARY-RO-20260804-01/kallsyms-*` | `/proc/kallsyms` permission denied | Confirmed |
| P6B-RO-004 | Read-only ADB | `adb/phase6b/PHASE6B-BOUNDARY-RO-20260804-01/slabinfo-*` | `/proc/slabinfo` 不存在 | Confirmed |
| P6B-RO-005 | Read-only ADB | `adb/phase6b/PHASE6B-BOUNDARY-RO-20260804-01/randomize_va_space-*` | `/proc/sys/kernel/randomize_va_space` permission denied | Confirmed |
| P6B-RO-006 | Read-only ADB | `adb/phase6b/PHASE6B-BOUNDARY-RO-20260804-01/proc-version.stdout.txt` | Linux 4.4.146+、Android clang、SMP/PREEMPT | Confirmed |
| P6B-SRC-001 | PS7331 source | `kernel/futex.c:2844`, `kernel/futex.c:2866-2869` | requeue-PI waiter 是 local stack object | Confirmed |
| P6B-SRC-002 | PS7331 source | `kernel/locking/rtmutex_common.h:18-25` | waiter 文件註解指定 kernel stack storage | Confirmed |
| P6B-SRC-003 | Host Clang probe | `artifacts/phase6b/phase6b-host-layout-20260804-02/` | source/config layout model 已產生並通過 SHA-256 | Strong evidence |
| P6B-SRC-004 | PS7331 source | `fs/pipe.c:614-625` | pipe metadata 與 buffer array 分開配置 | Confirmed |
| P6B-SRC-005 | PS7331 source | `drivers/staging/android/ion/ion.c:106-117` | ion_buffer metadata 由 kzalloc 配置 | Confirmed |
| P6B-SRC-006 | PS7331 source | `kernel/fork.c:307-316` | task_struct 使用 dedicated kmem_cache | Confirmed |
| P6B-GATE-001 | Safety boundary | 本報告 | 未執行 device-side Requeue-PI、race、panic、spray 或 root | Confirmed |

原始裝置 run 含有連接裝置清單；公開整理時應移除與本研究無關的其他裝置
識別資訊，不要直接把該目錄當作公開證據發布。
