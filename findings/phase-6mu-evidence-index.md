# Phase 6MU evidence index — AmazonApplicationFlags closure

Generated: 2026-08-10
Test ID: `PHASE6MU-STATIC-20260810-01`
Scope: host-only; no device/Binder/ioctl/mutation/reboot.

## 6MU-E01 — four mutators

- Source: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:95866-96036`, exact wrapper method ranges in
  `artifacts/phase6mu-amazon-application-flags-20260810-01/mutator-map.csv`.
- Observed: permission check, package/list/user inputs, four
  `AmazonApplicationFlags` static calls, and write-to-file boundary.
- Confidence: Confirmed static

## 6MU-E02 — persistence file and schema

- Source: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:95189-95649`.
- Observed: `/data/system/amazon_package_flags.xml`, read/write methods, user
  indexed flags/metadata, and XML tags.
- Confidence: Confirmed static

## 6MU-E03 — first consumer call sites

- Source: all matching `AmazonApplicationFlags` call sites in `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`.
- Observed: package-recency filtering, game-mode bit 2, AppCompat package
  compatibility bit 1, and package-service read wrapper.
- Interpretation: no direct HOME/preferred/Fire Launcher writer in the bounded
  consumers.
- Confidence: Strong evidence (bounded)

## 6MU-E04 — unresolved boundary

- The audit does not prove runtime service-handle availability, SELinux access,
  caller UID, flag values supplied by trusted callers, or consumers outside the
  preserved Java corpus.
- Confidence: Unknown / not tested
