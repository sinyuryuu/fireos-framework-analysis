# Phase 5DB evidence index

## P5DB-E01 — exact device/OTA match

- File: `adb/phase5/PS7331-EXACT-MATCH-20260804-01/metadata.json`
- Manifest SHA-256: `788c7501a951c4d97e6df649d2db8614daf58e2c8bb0525863a062be3e347cfe`
- Command: `tools/scripts/capture_phase5db_exact_ps7331_match.sh`
- Observed: fingerprint, incremental, product, and security patch all match
  the official OTA metadata.
- Classification: **Confirmed, read-only runtime/OTA scope**

## P5DB-E02 — official PS7331 OTA identity

- File: `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/summary.json`
- OTA SHA-256: `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`
- Observed: full OTA, product `trona`, post-build PS7331 fingerprint,
  incremental `0031575863172`, patch `2024-08-01`.
- Classification: **Confirmed, metadata scope**

## P5DB-E03 — exact source semantics

- File: `artifacts/phase5/phase5db-ps7331-exact-source-semantics-20260804-01/ps7331.json`
- Source SHA-256: `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde`
- Observed: `PRE_FIX_CURRENT_TASK_CLEANUP_PATTERN`; current cleanup and proxy
  remove-waiter call present.
- Classification: **Confirmed, source scope**

## P5DB-E04 — boot Image provenance

- File: `artifacts/phase5/ps7331-boot-image-inspection-20260804-01/boot-image-metadata.json`
- Boot image SHA-256: `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b`
- Observed: PS7331 OTA-derived boot Image metadata; gzip kernel payload.
- Classification: **Confirmed, preserved artifact scope**

## P5DB-E05 — sanitized Image markers

- File: `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/instruction-patterns.csv`
- Observed: current-task source, current-task blocked-on clear, and proxy
  remove-waiter call markers.
- Classification: **Confirmed, sanitized static Image scope**

## P5DB-E06 — chain verifier

- File: `artifacts/phase5/phase5db-ps7331-exact-chain-verification-20260804-01/verification.json`
- Observed: all 13 checks passed; no code execution or device I/O.
- Classification: **Confirmed, host-only verification scope**

## P5DB-E07 — runtime gap

- File: `adb/phase5/PHASE5CY-RUNTIME-BOUNDARY-20260804-01/result.md`
- Observed: no runtime identity mismatch or cleanup residue observed in the
  bounded read-only capture.
- Classification: **Confirmed negative observation; D1-R through D4 remain unobserved**
