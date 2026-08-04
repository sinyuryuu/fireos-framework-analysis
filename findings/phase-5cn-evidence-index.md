# Phase 5CN evidence index

本輪只使用既有 PS7331 source/config/tracing evidence，沒有新增裝置狀態修改。

| Evidence ID | Source | File | SHA-256 | Test ID | Interpretation | Confidence |
|---|---|---|---|---|---|---|
| `P5CN-SRC-001` | Official PS7331 source member | `artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/kernel/futex.c` | `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96` | host-only | `futex_cmpxchg_enabled` declaration/detection and PI dispatch gate | Confirmed，source scope |
| `P5CN-SRC-002` | Official PS7331 source member | `artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c` | `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde` | host-only | explicit proxy task and `current` cleanup semantics | Confirmed，source scope |
| `P5CN-SRC-003` | Official PS7331 source member | `artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig` | `09ca8dfc3b3b5e139482e3dd9976dae79547077fb750a4cbc778814f85ecaaac` | host-only | target defconfig is present; complete arch futex include/Kconfig is not in subset | Confirmed，scope limitation |
| `P5CN-RUNTIME-001` | PS7331 device read-only capture | `adb/phase5/PS7331-CONFIG-GATES-20260804-03/config.stdout.txt` | `803ae046bd72a33481f8472591b11b29090561ac3f254a2772aaf9e0322d823d` | `PS7331-CONFIG-GATES-20260804-03` | `CONFIG_FUTEX=y`, `CONFIG_RT_MUTEXES=y`, and security/debug config flags | Confirmed，runtime config |
| `P5CN-RUNTIME-002` | PS7331 device read-only capture | `adb/phase5/PS7331-CONFIG-GATES-20260804-03/tracing_event_categories.stdout.txt` | `038b514dc88aef8f3dad29a8303358167d49b727098ef9b8a175c0d5c67aadc0` | `PS7331-CONFIG-GATES-20260804-03` | event inventory has no named futex/rtmutex category; not path absence proof | Confirmed，inventory scope |
| `P5CN-SAFETY-001` | PS7331 device read-only capture | `adb/phase5/PS7331-CONFIG-GATES-20260804-03/result.md` | `dee9ccf5d55ea24021371ce4bcd40e261654858302d36aa3a09cf53055a8101c` | `PS7331-CONFIG-GATES-20260804-03` | no PI trigger, device-node open/ioctl, or device mutation | Confirmed |

## Negative result

No evidence row in this index observes `waiter->task != current`. D1 remains
**unobserved**.
