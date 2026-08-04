# Phase 5CE evidence index

Scope: public-source metadata review only; no exploit build or device execution.

| Evidence ID | Source | Observation | Confidence |
|---|---|---|---|
| P5CE-001 | `ghostlock-emerald` README | project identifies Poco M6 Pro/MT6789 and Android 16 kernel 6.12.30 target | Confirmed, public-source scope |
| P5CE-002 | `ghostlock-emerald` Makefile | NDK API 35 AArch64 build and root/physical-RW-related source modules are compiled | Confirmed, public-source scope |
| P5CE-003 | `src/core/target.h` | target build/layout metadata is hard-coded and build-labeled | Confirmed, public-source scope |
| P5CE-004 | `src/devices/emerald/offsets.h` | offsets entry is tied to the Emerald kernel version/profile | Confirmed, public-source scope |
| P5CE-005 | local PS7331 artifacts | Fire target is Android 9/MT8183/4.4-family with separate source/Image hashes | Confirmed, local artifact scope |
| P5CE-006 | target comparison | Emerald profile has no exact Fire PS7331 compatibility evidence | Strong evidence |
| P5CE-007 | safety record | no clone/build/install/run/ADB/bootloader/partition operation | Confirmed |

Public repository revision reviewed: `ebb355d302629a034d0959e5e579496559e8f84e`.
