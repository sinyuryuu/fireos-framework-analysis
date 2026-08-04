# Phase 5BZ evidence index

日期：2026-08-04；scope：PS7331 only；host-only。

| Evidence ID | Command / source | File | SHA-256 | Observed result | Confidence |
|---|---|---|---|---|---|
| P5BZ-001 | Offline boot-image metadata inspection | `artifacts/phase5/ps7331-boot-image-inspection-20260804-01/boot-image-metadata.json` | `32831b97cd2af84897889a69b480c2c2af60dbb3598e444678c41cba3ec7305c` | PS7331 boot image hash and gzip kernel metadata preserved | Confirmed |
| P5BZ-002 | `analyze_phase5ar_ps7331_rtmutex_binary.py` output | `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/instruction-patterns.csv` | `0ee3da7513051f2fa32b221918c6e671bc78b2a8e192fa0ab7ad65cc6e53475d` | Current-task cleanup markers and proxy cleanup call present | Confirmed, saved-binary scope |
| P5BZ-003 | `analyze_phase5by_ghostlock_fix_chain.py` output | `artifacts/phase5/phase5by-ps7331-ghostlock-fix-chain-20260804-02/fix-chain.json` | `4e15b1302f3b3b3691fe3310298f639207365c3c78c6afece780fdb2791667d9` | Pre-primary-fix source and follow-up guard review point | Confirmed, source scope |
| P5BZ-004 | Parser provenance review | `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/parser-metadata.md` | `22c1d9ff1247219249300e4434ae874140f56b7ba1a1f4f1eefb9b4f854b794b` | Raw ELF/disassembly intentionally omitted | Confirmed, limitation |
| P5BZ-005 | Offline IKCONFIG grep | `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config` | `eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04` | FUTEX/RT_MUTEXES/PREEMPT/SECCOMP/RANDOMIZE_BASE/KALLSYMS and ARM64 config present | Confirmed, config scope |
| P5BZ-006 | Host-only evidence-boundary verifier | `artifacts/phase5/phase5bz-ps7331-binary-evidence-boundary-20260804-01/analysis.json` | `e8feaa9f9587e9fc68f9ec12fcced9f4eb353810ddb7b6cbeb83240dc1f0b566` | Primary markers complete; follow-up binary status unresolved | Confirmed, derived result |
| P5BZ-007 | Host-only test | `tests/test_phase5bz_ps7331_binary_boundary.py` | repository commit hash | Synthetic fixture confirms no invented follow-up claim | Confirmed |
| P5BZ-008 | Safety boundary | `findings/phase-5bz-ps7331-binary-evidence-boundary.md` | repository commit hash | No device/exploit/boot/partition operation | Confirmed |

## Confidence vocabulary

- **Confirmed**：保存的檔案或可重現 host-only output 直接支持。
- **High-confidence inference**：多類靜態 evidence 支持，但不是 runtime proof。
- **Pending**：需要未保存的 raw disassembly 或安全上不執行的 runtime test。
- **Disproved**：與保存 evidence 矛盾。
- **Risk-rejected**：不執行的高風險操作，不以其未執行推導漏洞存在或不存在。
