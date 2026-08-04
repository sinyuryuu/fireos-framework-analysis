# Phase 6B host-only rtmutex semantic comparison

This is a source-marker comparison only. It does not execute a kernel,
invoke ADB, generate futex arguments, create a waiter, trigger a race,
or establish exploitability.

## Result

- PS7331 `remove_waiter()` current-task cleanup: **True**.
- PS7331 `remove_waiter()` waiter-task cleanup marker: **False**.
- PS7331 proxy wrapper calls `remove_waiter()`: **True**.
- PS7331 wrapper has broad nonzero cleanup marker: **True**.
- PS7331 wrapper has negative-only cleanup marker: **False**.
- Fixed v6.1.175 proxy wrapper in the preserved slice: **UNAVAILABLE**.

The PS7331 marker set is consistent with the preserved legacy v4.4.146
pre-fix shape. The fixed v6.1.175 input is a focused remove_waiter slice,
so its proxy-wrapper absence is not treated as a semantic difference. This is
strong source-level evidence for pre-fix semantics, not runtime identity
mismatch, residue, memory corruption, crash, or privilege transition.

## Reference inputs

- legacy: `artifacts/phase5/public-source-review/linux-rtmutex/linux-stable-v4.4.146.c` SHA-256 `c4ddac5fe820c7f07670bc332425be05b0df0400ae334a147b483f0ee9b07345`
- fixed: `artifacts/phase5/public-source-review/linux-rtmutex/linux-stable-v6.1.175.c` SHA-256 `c307ed54156d1f16e82387df7b214445dddf27be8a880f31575f698ca07d880a`
- PS7331: `firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c` SHA-256 `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde`

## Evidence labels

- **已證實：** source marker、函式行號與三份輸入雜湊。
- **高可信推論：** inspected PS7331 source retains the legacy cleanup shape.
- **待驗證：** stock runtime identity mismatch and any later consumer.
- **因風險拒絕測試：** device requeue-PI trigger, race, panic, memory operation, root payload.
