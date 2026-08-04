# Phase 5DD evidence index

## P5DD-001 — complete preserved ELF inventory

- Inputs: `artifacts/phase5/phase5cq-fire-native-20260804-01/`,
  `phase5cr-fire-native-20260804-02/`, `phase5cs-fire-amazon-native-20260804-01/`
- Derived output: `artifacts/phase5/phase5dd-native-futex-surface-20260804-03/summary.json`
- SHA-256: `497cfe1d035d53b9056e81733d29f3b54d8e3e6656fad4896ab2b96331dc831a`
- Observed: 16 ELF files scanned; zero named requeue-PI files.
- Confidence: **Confirmed, bounded artifact-scan scope**

## P5DD-002 — full inventory table

- File: `artifacts/phase5/phase5dd-native-futex-surface-20260804-03/native-futex-surface.csv`
- SHA-256: `741ac2e975e47e45ffd922b4fd801b11ad08aee1d5aa101e6fabe2c9e95aa8e2`
- Observed: libc/linker ordinary futex/PI helper markers; ART ordinary
  compare-requeue markers; libcutils generic syscall marker; no named
  `REQUEUE_PI` marker.
- Confidence: **Confirmed, artifact-scan scope**

## P5DD-003 — marker excerpts

- File: `artifacts/phase5/phase5dd-native-futex-surface-20260804-03/native-futex-markers.csv`
- SHA-256: `b09f3725183bcbab02face08e987baae33ebc3556213e1b9a1234a9eeba38f9f`
- Interpretation: marker strings and symbol names do not prove a runtime call
  edge or syscall operation.
- Confidence: **Confirmed marker scope**

## P5DD-004 — reproducibility and safety

- Script: `tools/scripts/audit_phase5dd_native_futex_surface.py`
- SHA-256: `dd50b65c8880ee31cabcc4d0200a43022b94680e7ecbe6c919dbd188057cc84c`
- Output manifest:
  `artifacts/phase5/phase5dd-native-futex-surface-20260804-03/sha256sums.txt`
- Manifest SHA-256: `ef448549c72a06a5844e0159829031772dbd7d9c2c52bc06fcfaa94c38bbd78c`
- Safety: ELF execution false, device contact false, futex trigger false,
  kernel memory false, payload/address generation false.
- Confidence: **Confirmed safety scope**

## P5DD-005 — runtime gap

- Related files: `findings/phase-5dc-evidence-index.md`,
  `adb/phase5/PHASE5CY-RUNTIME-BOUNDARY-20260804-01/result.md`.
- Observed: static/native marker coverage did not produce same-execution
  `waiter->task != current`, cleanup residue, later consumer, memory effect or
  privilege transition.
- Confidence: **Runtime unobserved**
