# Phase 6C GhostLock consistency evidence index

## E6C-GC-01 — exact source chain

- Source: PS7331 GPL tree
- File: `artifacts/phase6c/phase6c-ghostlock-consistency-20260804-05/source-checks.csv`
- Observed: all 11 source landmarks found; key locations include futex dispatch `3238/3269`, no-waiter `1716`, proxy call `1963`, proxy cleanup `rtmutex.c:1683`, early owner branch `972`, waiter assignment `977`, and current cleanup `1089`.
- Interpretation: static source chain is present.
- Confidence: **已證實（source scope）**

## E6C-GC-02 — embedded config

- Source: extracted config from preserved PS7331 kernel Image
- File: `artifacts/phase6c/phase6c-ghostlock-consistency-20260804-05/config-checks.csv`
- Observed: core ARM64/FUTEX/RT_MUTEXES/SLUB/ION/RANDOMIZE_BASE gates are enabled; KASAN/DEBUG_INFO/USERFAULTFD are not enabled.
- Interpretation: static build capability and observation limits.
- Confidence: **已證實（config scope）**

## E6C-GC-03 — boot-image provenance

- Source: preserved PS7331 boot image inspection
- File: `artifacts/phase6c/phase6c-ghostlock-consistency-20260804-05/consistency.json`
- Observed: boot metadata, kernel compression/layout fields and image/kernel hashes are carried into the audit.
- Interpretation: provenance linkage; not a bit-for-bit source build proof.
- Confidence: **高可信推論**

## E6C-GC-04 — ordinary PI runtime boundary

- Source: Phase 6A report
- File: `findings/phase-6a-untrusted-app-pi-smoke-test.md`
- Observed: ordinary untrusted app completed uncontended PI lock/unlock; requeue-PI was intentionally not issued.
- Interpretation: ordinary PI capability only.
- Confidence: **已證實**

## E6C-GC-05 — GhostLock runtime gap

- Source: Phase 6C read-only capture and consistency audit
- Files: `findings/phase-6c-runtime-capture-20260804-01.md`, `artifacts/phase6c/phase6c-ghostlock-consistency-20260804-05/result.md`
- Observed: no preserved requeue return, proxy waiter, identity mismatch, cleanup residue, memory effect, or privilege transition.
- Interpretation: live exploitability remains unconfirmed.
- Confidence: **已證實（what was captured）／待驗證（unobserved runtime state）**

## E6C-GC-06 — public PoC compatibility boundary

- Source: public `ghostlock-emerald` README
- URL: `https://github.com/datfooldive/ghostlock-emerald`
- Observed: README targets Poco M6 Pro / MT6789 / Android 16 / kernel 6.12.30.
- Interpretation: it is not a direct PS7331/MT8183/Linux 4.4.146 compatibility proof.
- Confidence: **已證實（repository README scope）**

## Safety exclusions

因風險拒絕：stock-device requeue-PI trigger、paired waiter、race scheduling、
panic/DoS、heap shaping、kernel memory access、boot-policy mutation、exploit 或
root payload。
