# Project inventory — 2026-08-10

This inventory describes the working tree used by the Fire OS 7 framework and
privilege-surface research. It is a map, not a claim that every local artifact
is public or suitable for redistribution. Original firmware and source files
are kept under separate paths and are never overwritten by generated output.

## Current device reference

The latest read-only capture is
`adb/phase6x2/PHASE6X2-DEVICE-READONLY-20260810-01/` for serial
`G001LT0511550CFT`.

| Field | Observation |
|---|---|
| Product | Amazon Fire HD 10 / `trona` |
| Fire OS build | `PS7331.4463N` |
| Build incremental | `0031575863172` |
| Android base | Android 9 / API 28 |
| Security patch | `2024-08-01` |
| SELinux | Enforcing |
| Current user | User 0 |
| User 0 HOME | `com.amazon.firelauncher/.Launcher`, effective priority 50 |
| User 0 candidates | Fire Launcher 50, Microsoft Launcher 0, FallbackHome -1000 |
| Package state | Fire Launcher enabled for User 0; saved User 10 state is separate |
| Capture safety | `mutation=false`, `binder_transaction=false`, `reboot=false` |

The capture directory contains raw stdout/stderr, metadata, and a local
`sha256sums.txt`. It is observational evidence only.

## Directory map

| Directory | Contents and role |
|---|---|
| `device/` | Device properties, package/service/process/mount/security baselines. |
| `adb/` | Immutable raw device-test evidence, snapshots, logcat, before/after data, and rollback records. |
| `firmware/original/` | Original downloaded OTA/GPL archives; do not edit in place. |
| `firmware/extracted/` | Read-only extraction of PS7331 images and the GPL source package. |
| `firmware/manifests/` | Provenance, command manifests, and SHA-256 records for firmware/artifacts. |
| `artifacts/phase5/` | Kernel/boot-image, futex/GhostLock, CVE surface, and native/driver analysis artifacts. |
| `artifacts/phase6*` | Framework, IPC, OTA/OOBE, package-state, profile, driver, and broad privilege-surface analysis artifacts. |
| `decompiled/` | JADX/apktool/baksmali and normalized outputs; never used as replacements for originals. |
| `aosp/` | AOSP Android 9 reference sources and comparison material. |
| `diff/` | AOSP/Fire OS method, resource, framework, and report comparisons. |
| `findings/` | Human-readable phase reports, evidence indexes, risk registers, and this inventory. |
| `output/` | CSV tables, Mermaid call graphs, rendered reports, and generated summaries. |
| `tools/scripts/` | Reproducible collection, static-analysis, evidence-generation, and verification scripts. |
| `tools/phase4-accessibility/` | Explicit-consent, visible-toggle foreground-assist test source; not a formal HOME writer. |
| `tools/test-launcher-*` | Minimal test APK sources/build outputs used for bounded resolver experiments. |
| `work/` | Worker reports and intermediate host-only analysis; raw inputs remain separately hashed. |

## Important firmware and kernel inputs

| Path | Role | Provenance / hash |
|---|---|---|
| `firmware/original/Fire_HD10-7.3.3.0-20240730.tar.bz2` | Historical Fire HD 10 GPL source package | Original archive; see adjacent manifest |
| `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` | PS7331 GPL source package | Original archive; see adjacent manifest |
| `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` | Official PS7331 OTA package | SHA-256 `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5` |
| `firmware/extracted/PS7331/boot.img` | Extracted signed boot image | Extracted read-only artifact; see PS7331 manifest |
| `firmware/extracted/PS7331/system.img` | Extracted system image | Extracted read-only artifact; see PS7331 manifest |
| `firmware/extracted/PS7331/vendor.img` | Extracted vendor image | Extracted read-only artifact; see PS7331 manifest |
| `firmware/extracted/PS7331/ota.prop` | OTA build metadata | SHA-256 `f91b4c792339c605d81a2d6d5e819fee5d522a7514111daa1468717e07319ded` |
| `firmware/extracted/PS7331-SOURCE-20250617/platform.tar` | Amazon GPL source payload | SHA-256 `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd` |
| `artifacts/phase5/ps7331-boot-image-inspection-20260804-01/kernel.Image` | Boot-image kernel payload used for static comparison | Hash recorded in its artifact manifest |
| `artifacts/phase5/ps7331-ikconfig-20260804-01/` | Extracted kernel configuration evidence | Hashes recorded in its artifact manifest |
| `artifacts/phase5/phase5by-ps7331-ghostlock-fix-chain-20260804-02/` | GhostLock/upstream patch-chain comparison | Host-only static evidence |
| `artifacts/phase5/phase5dc-requeue-pi-caller-audit-20260804-*/` | User-space PI futex caller audits | Host-only/static and bounded runtime evidence |

The 7.3.3.1 source package contains the MT8183/MediaTek 4.4 kernel tree and
Amazon kernel-driver material. The bounded source audit did not find a complete
`system/core/init/selinux.cpp` policy-loader tree; `/init` conclusions therefore
remain tied to the saved binary/AOSP anchor rather than an assumed GPL source
file.

## Current public phase bundle

The public branch currently includes Phase 6X at commit
`429c013abb4f6d4bf11b4ef4de00e1532ed6f405`. The new Phase 6X2 bundle is
generated from:

- `output/tables/phase6x-control-surface.csv`;
- four new worker CSV/Markdown pairs under `work/`;
- the exact-serial read-only snapshot under `adb/phase6x2/`.

Generated Phase 6X2 outputs are separate from pre-existing `Phase 6AA` files so
older user evidence is not overwritten:

- `findings/phase-6x2-report.md`;
- `findings/phase-6x2-evidence-index.md`;
- `output/tables/phase6x2-control-surface.csv`;
- `output/tables/phase6x2-input-manifest.sha256`;
- `output/call-graphs/phase6x2-control-surfaces.mmd` and `.md`.

## Evidence and safety rules

- Original archives/images are read-only inputs; generated/decompiled files use
  separate directories.
- A static capability is not an exploit finding without caller, gate, identity,
  user scope, sink, and observed effect.
- Unknown Binder transaction codes, driver opens/ioctls, OTA/recovery execution,
  root exploits, Fire Launcher mutation, partition writes, remounts, and
  destructive recovery actions are not part of the Phase 6X2 work.
- Every new raw capture has a unique directory and SHA-256 manifest.
