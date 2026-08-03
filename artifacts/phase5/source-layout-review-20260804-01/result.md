# Source-derived rt_mutex_waiter layout

- Object: `struct rt_mutex_waiter`
- `sizeof`: `0x48`
- Pointer size: `8`
- Scope: source/ABI layout only; no runtime addresses or exploit header

| Field | Included | Offset | Size |
|---|---:|---:|---:|
| `tree_entry` | True | 0x0 | 0x18 |
| `pi_tree_entry` | True | 0x18 | 0x18 |
| `task` | True | 0x30 | 0x8 |
| `lock` | True | 0x38 | 0x8 |
| `ip` | False | N/A | N/A |
| `deadlock_task_pid` | False | N/A | N/A |
| `deadlock_lock` | False | N/A | N/A |
| `prio` | True | 0x40 | 0x4 |
