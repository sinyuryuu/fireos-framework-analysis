# PS7331 `/init` conservative CFG recovery

This artifact is generated from host `objdump` output. The ELF was not
executed and no device or boot state was touched.

The selected range contains **2816** parsed instructions,
**423** conservative blocks and **663** explicit
branch/fall-through edges.

**已證實：** the parser recovers the known rootable/standard call sites and
the `w5` branch target as instruction-level landmarks.

**待驗證：** indirect calls, original symbols, active boot path, and the
high-level meaning of the alternate branch.

**因風險拒絕測試：** executing `/init`, changing boot properties, selecting
policy variants, verification bypass, kernel-memory operations or root payloads.
