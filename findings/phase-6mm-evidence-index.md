# Phase 6MM evidence index

本索引只收錄本輪新增的 host-only evidence。所有負面結果都限定在指定的
selected functions 與 direct-`BL` graph；不代表整個 binary 的全域不存在。

## 6MM-REG-001

Evidence ID: `6MM-REG-001`  
Source: PS7331 `update-binary` selected disassembly  
File: `artifacts/phase6mm-updater-blockimage-20260810-01/focus-disassembly.txt`  
SHA-256: `b9ead546cf79e1879bc2362d75b801250873dcba59958a3f5b99b7ce33093835`  
Test ID: `PHASE6MM-HOST-20260810-01`  
Timestamp: 2026-08-10  
Command: `python3 tools/scripts/audit_phase6mm_updater_blockimage_closure.py`  
Observed result: `RegisterBlockImageFunction` contains five calls to `0x41d528`; calls are at `0x40d0fc`, `0x40d144`, `0x40d190`, `0x40d1d8`, `0x40d224`.  
Interpretation: block-image command registration uses the same indirect registry boundary as install-script commands.  
Confidence: **Confirmed**  
Related hypothesis: native updater block-image handlers are statically registered, not an ADB HOME route.

## 6MM-REG-002

Evidence ID: `6MM-REG-002`  
Source: ELF data-cell and symbol correlation  
File: `artifacts/phase6mm-updater-blockimage-20260810-01/block-image-registration.csv`  
SHA-256: `778bc4774b4ade436bd979b366c1f3c8e9a1ce91fe6aa2d306040d32629cebcb`  
Test ID: `PHASE6MM-HOST-20260810-01`  
Timestamp: 2026-08-10  
Command: host-only parser over the signed updater ELF and debugdata symbol CSV  
Observed result: five command names and five function-pointer cells resolve to known symbols.  
Interpretation: registration mapping is closed for the selected block-image routine.  
Confidence: **Strong evidence**  
Related hypothesis: indirect registration can be recovered without invoking recovery.

## 6MM-CANON-001

Evidence ID: `6MM-CANON-001`  
Source: selected direct-call edge extraction  
File: `artifacts/phase6mm-updater-blockimage-20260810-01/canonicalization-call-sites.csv`  
SHA-256: `8cc6d38c1e464b6b741b29bdee8aa253113e7aea286f368ffe1cf1c0cde5983d`  
Test ID: `PHASE6MM-HOST-20260810-01`  
Timestamp: 2026-08-10  
Command: host-only direct-`BL` correlation  
Observed result: `MakeFreeSpaceOnCache:0x417bf0 -> __readlink_chk:0x4ce4e8`.  
Interpretation: a canonicalization-related call site exists in the cache-space helper; no runtime input or security impact is inferred.  
Confidence: **Confirmed**  
Related hypothesis: updater path handling requires a bounded caller/data-flow audit.

## 6MM-CALL-001

Evidence ID: `6MM-CALL-001`  
Source: selected direct-call edge table  
File: `artifacts/phase6mm-updater-blockimage-20260810-01/selected-call-edges.csv`  
SHA-256: `2e5074f461127445bfcb5633840aff16e2284545245292b5999581d672e10d65`  
Test ID: `PHASE6MM-HOST-20260810-01`  
Timestamp: 2026-08-10  
Command: host-only symbol-guided disassembly parser  
Observed result: `PerformBlockImageUpdate` calls `CacheSizeCheck`, while the selected graph has no direct canonicalization-to-write sink edge.  
Interpretation: the missing `CacheSizeCheck` body is an explicit residual; the bounded negative is not binary-wide.  
Confidence: **Probable**  
Related hypothesis: cache helper and partition-write path may be connected through an unselected or indirect call.

## 6MM-SAFETY-001

Evidence ID: `6MM-SAFETY-001`  
Source: generated phase summary  
File: `artifacts/phase6mm-updater-blockimage-20260810-01/summary.json`  
SHA-256: `a0186bb7d053d23f002dc663b9ee3f312255410b35ed997a74e864fc8f9229a6`  
Test ID: `PHASE6MM-HOST-20260810-01`  
Timestamp: 2026-08-10  
Command: host-only script; `sha256sum -c sha256sums.txt`  
Observed result: `device_contacted=false`, `updater_executed=false`, `recovery_executed=false`, `partition_written=false`; all artifact hashes pass.  
Interpretation: this phase changed no device state.  
Confidence: **Confirmed**  
Related hypothesis: updater closure can proceed without crossing the recovery/partition boundary.

## 6ML-INVENTORY-001

Evidence ID: `6ML-INVENTORY-001`  
Source: delegated read-only repository inventory  
File: `work/luna_worker_phase6ml_inventory_20260810.md`  
SHA-256: `b0e5750f81b82b0289b95f966dc308f1c8ee5a766f998cbc441805e89334e3f5`  
Test ID: `PHASE6ML-INVENTORY-20260810`  
Timestamp: 2026-08-10  
Command: read-only workspace/evidence inventory  
Observed result: no contradiction found across 6BK/6MJ/6MK; residuals remain OOBE user scope, Amazon IPC caller inventory, protected-broadcast completeness, and updater indirect verifier/canonicalization flow.  
Interpretation: Phase 6MM closes only the block-image registration portion; it does not reopen completed HOME or package-state tests.  
Confidence: **Strong evidence**  
Related hypothesis: the remaining work is bounded host-only closure rather than a new device mutation.
