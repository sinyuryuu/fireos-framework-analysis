# Phase 5DC evidence index

日期：2026-08-04

本索引只引用 host-only source/native audit 與已保存的先前證據。沒有裝置
操作、source/native execution、futex syscall、race、ioctl、kernel memory
access 或 root payload。

## P5DC-001 — source-role scan

- Source: official PS7331 source extraction
- Files: `firmware/extracted/PS7331-SOURCE-20250617/platform` and `fireos`
- Derived output: `artifacts/phase5/phase5dc-requeue-pi-caller-audit-20260804-05/summary.json`
- SHA-256: `df14bb7d4a72df5d9a5f1ee39b2c1c83a6c07d5d774b02fcbd39b9cd01f6e69d`
- Command: `python3 tools/scripts/audit_phase5dc_requeue_pi_callers.py ...`
- Observed: 231 matching rows / 34 files; 60 kernel, 135 selftest, 36
  UAPI/documentation; zero userspace-candidate rows.
- Interpretation: source references are present, but no Fire framework/app
  caller was identified in the searched source roots.
- Confidence: **Confirmed, source-scan scope**
- Limitation: bounded text search; indirect, generated, stripped or unpulled
  caller paths remain possible.

## P5DC-002 — exact MT8183 kernel implementation

- Source: `kernel/mediatek/mt8183/4.4/kernel/futex.c`
- SHA-256: `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96`
- Locations: lines 1926, 1959-1965, 3233-3269.
- Observed: requeue-PI dispatch and the stored `this->task` proxy argument.
- Interpretation: exact build-selected kernel path exists.
- Confidence: **Confirmed, source scope** (`P5CP-005`–`P5CP-007` and exact
  source scan).

## P5DC-003 — exact MT8183 proxy cleanup implementation

- Source: `kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c`
- SHA-256: `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde`
- Locations: lines 1654-1684; prior cleanup at 1079-1129.
- Observed: explicit task parameter, nonzero cleanup branch, and
  `remove_waiter()` call.
- Interpretation: source-level proxy cleanup path is preserved.
- Confidence: **Confirmed, source scope** (`P5CP-008`–`P5CP-014`).

## P5DC-004 — selftest direct wrappers

- Source: `kernel/mediatek/4.4/tools/testing/selftests/futex/include/futextest.h`
- Locations: lines 180-208.
- Observed: selftest wrappers invoke `FUTEX_WAIT_REQUEUE_PI` and
  `FUTEX_CMP_REQUEUE_PI` through a generic futex helper.
- Interpretation: direct userspace-shaped examples exist only in the selftest
  source tree; no test was built or executed.
- Confidence: **Confirmed, selftest scope**

## P5DC-005 — native negative observation

- Inputs: `artifacts/phase5/phase5cr-fire-native-20260804-02/` and
  `artifacts/phase5/phase5cs-fire-amazon-native-20260804-01/`
- Derived output: `artifacts/phase5/phase5dc-requeue-pi-caller-audit-20260804-05/native-scan-hits.csv`
- SHA-256: `8ec381461d0f60501c329e695478f73091a973d9a28178a48821c524846cef32`
- Observed: zero named requeue-PI rows.
- Interpretation: no bounded named caller was established in preserved native
  scan inputs.
- Confidence: **Negative observation only**
- Limitation: no proof against indirect, inline, stripped, unpulled or generated
  callers.

## P5DC-006 — runtime boundary remains open

- Source: `adb/phase5/PHASE5CY-RUNTIME-BOUNDARY-20260804-01/result.md`
- Related evidence: `P5DB-E07`, `P5CR-RUNTIME-001`, `P5CP-RUNTIME-001/002`.
- Observed: no same-execution `waiter->task != current`, wrong-target cleanup,
  persistent residue, later consumer, memory effect or privilege transition.
- Interpretation: Phase 5DC did not advance the stock-device runtime gate.
- Confidence: **Confirmed negative observation; runtime unobserved**

## P5DC-007 — safety boundary

- Script: `tools/scripts/audit_phase5dc_requeue_pi_callers.py`
- Script SHA-256: `d061cc5edc3d1d54909cfd143bf010b95ae09a34e425a9d376dc292fdce69327`
- Output manifest: `artifacts/phase5/phase5dc-requeue-pi-caller-audit-20260804-05/sha256sums.txt`
- Output manifest SHA-256: `7e7a49ba9bd0e757f840b28b54e9297bc8e8357c7ad588997a92f7644d18bf0d`
- Observed safety flags: source/native objects not executed, device not
  contacted, no futex trigger, kernel memory, payload or address generation.
- Confidence: **Confirmed safety scope**

## Classification summary

- **已證實：** exact source path、selftest wrapper role、native bounded scan
  result與輸出 hash。
- **高可信推論：** ordinary Fire libc/ART evidence目前不足以當作
  requeue-PI caller evidence。
- **待驗證：** Fire-specific indirect caller、policy allowance、stock proxy
  execution與runtime identity mismatch。
- **已排除／不支持：** selftest/documentation/ordinary compare-requeue marker
  等同於 stock GhostLock execution。
- **因風險拒絕測試：** stock futex trigger/race、crash、kernel memory、root
  payload。
