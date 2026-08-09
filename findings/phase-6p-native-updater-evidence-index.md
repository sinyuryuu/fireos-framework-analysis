# Phase 6P evidence index

| Evidence ID | Source | Observation | Confidence |
|---|---|---|---|
| 6P-ELF-001 | `firmware/extracted/PS7331/META-INF/com/google/android/update-binary` | ELF64 AArch64 updater; 1,749,792 bytes; SHA-256 `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b` | Confirmed |
| 6P-SYM-001 | `artifacts/phase6s/ota-debugdata-audit-20260805-01/` | Embedded debugdata recovered; 2,886 symbols; mini-ELF SHA-256 `a1918c31c48e4ee3a6f06d0bf85a87493d6f28b7b671bb019d8957c06073988d` | Confirmed |
| 6P-CFG-001 | `artifacts/phase6s/ota-cfg-focus-20260805-01/focus-disassembly.txt` | Registration/evaluation, extraction, verification, and write functions are symbol-address aligned | Confirmed (host-only) |
| 6P-WRITE-001 | `artifacts/phase6bi/write-boundary-20260805-01/direct-call-edges.csv` | `PackageExtractFileFn` → `ota_open`/`ExtractEntryToFile`/`ota_fsync`; `WriteToPartition` → `ota_open`/`ota_write` | Confirmed (static) |
| 6P-VERIFY-001 | `artifacts/phase6ah/update-binary-validation-20260805-01/relevant-call-edges.csv` | `LoadSrcTgtVersion3` reaches `VerifyBlocks`; SHA-1 comparison branch is present in saved CFG | Confirmed (static) |
| 6P-PATH-001 | `artifacts/phase6bi/write-boundary-20260805-01/direct-call-edges.csv` | `__readlink_chk` edge is from `MakeFreeSpaceOnCache`, not package extraction/open | Strong evidence |
| 6P-REACH-001 | `findings/phase-6bi-ota-write-boundary.md` and `findings/phase-6t-ota-cfg-focus.md` | No shell/ordinary-App updater caller was demonstrated; registry/recovery provenance remains outside the proven direct-edge chain | Strong evidence / unresolved |

No evidence in this index supports bypassing OTA validation, obtaining Root, or
writing a device partition from Android shell.
