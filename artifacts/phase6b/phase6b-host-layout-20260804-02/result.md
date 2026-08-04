# Phase 6B host-only layout model

Device/kernel execution, race trigger, memory spray, KASLR slide calculation and root operation: **False**.

| Object | Size | Storage | Modeled cache |
|---|---:|---|---|
| `task_struct` | 3488 | dedicated task_struct kmem_cache |  |
| `rt_mutex_waiter` | 72 | blocked task kernel stack; not a kmalloc object |  |
| `pipe_buffer` | 40 | pipe_buffer array allocated by kzalloc | kmalloc-1024 |
| `ion_buffer` | 248 | ION metadata allocated by kzalloc(sizeof(struct ion_buffer)) | kmalloc-256 |

- Limitation: RANDOMIZE_BASE confirms KASLR is enabled; no runtime slide or kernel address is calculated.
- Limitation: The modeled cache class does not prove an address, adjacency, reuse, or corruption event.
- Limitation: The inspected rt_mutex_waiter is stack-resident, so it is not a direct SLUB spray target in this path.
- Limitation: No identity mismatch, cleanup residue, memory effect, crash, or privilege transition is inferred.
