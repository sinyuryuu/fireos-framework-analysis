# Phase 5DG — GhostLock Emerald reference architecture audit

日期：2026-08-04

本輪只讀分析公開 datfooldive/ghostlock-emerald repository 的 source
與 build metadata。分析對象 commit：
ebb355d302629a034d0959e5e579496559e8f84e。

沒有編譯、執行、模擬或移植該 repository；沒有擷取 offsets 供 PS7331
使用，沒有產生 futex trigger、kernel address、kernel read/write operation
或 root payload，也沒有接觸平板。

## 參考專案的目標差異

README／Makefile 顯示該專案目標是：

- POCO M6 Pro／MediaTek MT6789；
- Linux 6.12.30／Android 16；
- AArch64 Android NDK executable；
- device-specific offsets；
- 以 KernelSU／ReSukiSU 作為後續 root layer。

這與本案 PS7331 的 KFTRWI／MT8183／Linux 4.4.146／Android 9 不同。不能
把 Emerald 的 offsets、kernel layout、allocator assumptions 或 primitive
直接套用到 Fire 平板。

## 高層架構

公開 source 的結構可分成五段：

1. **PI/requeue orchestration**：slide.c 具名使用
   FUTEX_LOCK_PI、FUTEX_WAIT_REQUEUE_PI、FUTEX_CMP_REQUEUE_PI、
   FUTEX_UNLOCK_PI，並以多執行緒控制 waiter／owner／consumer。
2. **Kernel layout / slide discovery**：slide.c、target.h 與 device
   offsets 描述 target-specific layout、KASLR／boot-id 等假設。
3. **Kernel memory primitive**：fops.c、pipe_physrw.c 顯示後續
   pipe/configfs/physrw 讀寫階段的 source markers。
4. **Credential／execution transition**：root.c、umh_root.c 顯示
   後續 credential 或 usermode-helper root stage 的 source markers。
5. **Validation／cleanup**：main.c 與各 stage state flags 用於檢查
   route、read/write、root result。

完整 marker 行號與 selected-file hashes：

artifacts/phase5/phase5dg-ghostlock-emerald-architecture-20260804-01/

重現腳本：

    python3 tools/scripts/audit_ghostlock_reference_architecture.py \
      --reference-dir /path/to/ghostlock-emerald \
      --output artifacts/phase5/phase5dg-ghostlock-emerald-architecture-REPLACE

腳本拒絕覆寫既有 output，且只讀 source。

## 與 PS7331 證據的對照

| Gate | Emerald reference | PS7331 current evidence |
|---|---|---|
| Kernel requeue-PI dispatch | source + explicit reference caller | kernel source dispatch confirmed |
| Userspace named PI/requeue caller | present in reference slide.c | not found in preserved Fire ELF / non-kernel source; bounded negative |
| Target layout | device-specific MT6789/6.12 data | separate MT8183/4.4 artifacts; no reuse permitted |
| Later kernel-memory primitive | present in reference source | not established on Fire |
| Credential/root transition | present in reference source | not established or tested on Fire |
| Live runtime mismatch | not independently established for PS7331 | not observed |

## 判定

- **已證實：** Emerald reference contains an explicit named PI/requeue
  orchestration and separate target-specific post-trigger stages.
- **高可信推論：** A working GhostLock port requires more than matching
  remove_waiter semantics: it requires a target-specific userspace caller,
  target-specific layout/allocator assumptions, a later memory effect, and a
  credential transition.
- **待驗證：** Whether PS7331 can form the same proxy waiter state from a
  newly authored userspace caller; whether its 4.4 allocator and device surfaces
  provide a later primitive.
- **已排除／不支持：** Treating Emerald's MT6789/6.12 offsets or binary
  architecture as evidence for MT8183/4.4; treating its source presence as
  proof of PS7331 runtime exploitability.
- **因風險拒絕測試：** compiling, sideloading, running, or adapting the
  reference root chain; invoking PI/requeue races; probing kernel memory;
  attempting credential modification.

## 下一個安全研究門檻

目前最有資訊量的下一步不是移植 root chain，而是取得更完整的 Fire
userspace provenance（未擷取 native libraries、symbols 或 build mapping）
並把任何結果限制在 source／artifact evidence。若要證明 runtime
identity mismatch，需隔離且可觀測的 LAB_ONLY kernel environment；stock
PS7331 不應以 root PoC 作為探針。
