# Phase 5CT evidence index

本輪為公開 source 與本機既有 evidence 的 host-side 架構對照；沒有下載／
編譯／執行 exploit，也沒有裝置操作。

| Evidence ID | Source | Evidence | Interpretation | Confidence |
|---|---|---|---|---|
| `P5CT-001` | Emerald README／Makefile | README 描述 Poco M6 Pro／MT6789／Android 16／6.12.30；Makefile 編入 trigger、memory 與 root stage | 不是 PS7331 可直接套用的同 build binary | Confirmed, public source |
| `P5CT-002` | Emerald `main.c` | public source contains target selection and separate waiter/owner/consumer roles | 公開 POC 有完整 trigger architecture，但不是 Fire runtime evidence | Confirmed, source scope |
| `P5CT-003` | Emerald `target.h`／device metadata | build-specific kernel/profile metadata exists | 需要 target profile；不能只靠 Android API／SoC 名稱移植 | Confirmed, source scope |
| `P5CT-004` | PS7331 exact source | futex requeue → proxy lock → cleanup pattern in saved `futex.c`／`rtmutex.c` | defect family source path exists on PS7331 | Confirmed, source scope |
| `P5CT-005` | Fire libc／ART | ordinary wait and PI-lock helpers confirmed; requeue-PI caller not established; ART marker maps to ordinary compare-requeue | userspace trigger gate remains open | Strong evidence, bounded scope |
| `P5CT-006` | Phase 5CP runtime boundary | no stock observation of `waiter->task != current`, cleanup residue or later consumer | not dynamic validation | Unobserved |
| `P5CT-007` | Phase 5 device safety | no exploit build/execution, no futex trigger, no kernel memory/payload/root operation | device unchanged | Confirmed safety scope |

## Public source references

- [Emerald README](https://github.com/datfooldive/ghostlock-emerald/blob/main/README.md)
- [Emerald `main.c`](https://github.com/datfooldive/ghostlock-emerald/blob/main/src/core/main.c)
- [Emerald `target.h`](https://github.com/datfooldive/ghostlock-emerald/blob/main/src/core/target.h)
- [Emerald offsets](https://github.com/datfooldive/ghostlock-emerald/blob/main/src/devices/emerald/offsets.h)
- [Emerald Makefile](https://github.com/datfooldive/ghostlock-emerald/blob/main/Makefile)
