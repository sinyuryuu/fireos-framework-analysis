# Phase 5CF evidence index

| Evidence ID | Source | Observation | Confidence |
|---|---|---|---|
| P5CF-001 | `adb/phase5/PHASE5CF-READONLY-20260804-01/summary.md` | explicit-serial read-only baseline completed | Confirmed |
| P5CF-002 | `device/fingerprint.stdout.txt` | installed build is `PS7330.4104N`, not PS7331 | Confirmed |
| P5CF-003 | `device/board_platform.stdout.txt`, `device/boot_hardware.stdout.txt` | MT8183 platform | Confirmed |
| P5CF-004 | `boot/flash_locked.stdout.txt`, `boot/verifiedbootstate.stdout.txt` | flash locked and verified boot green | Confirmed |
| P5CF-005 | `device/getenforce.stdout.txt` | SELinux Enforcing | Confirmed |
| P5CF-006 | `device/firelauncher_path.stdout.txt`, `device/firelauncher_package.stdout.txt` | Fire Launcher is under `/system/priv-app` and was only read | Confirmed |
| P5CF-007 | `*.exit_code.txt` | five read-only paths returned exit code 1; failures preserved | Confirmed |
| P5CF-008 | `sha256sums.txt` | raw baseline manifest verified locally | Confirmed |
| P5CF-009 | `adb/phase5/PHASE5CF-OTA-METADATA-20260804-01/ota_props.stdout.txt` | current properties identify `Fire OS 7.3.3.0 (PS7330/4104)` | Confirmed |
| P5CF-010 | `adb/phase5/PHASE5CF-OTA-METADATA-20260804-01/ota_package_paths.stdout.txt` | OTA-related packages are present; no pending update is inferred | Confirmed |
| P5CF-011 | `adb/phase5/PHASE5CF-OTA-METADATA-20260804-01/readable_ota_paths.stdout.txt` | shell cannot read `/data/ota` and `/data/ota_package`; contents remain unknown | Confirmed |
| P5CF-012 | `adb/phase5/PHASE5CF-OTA-METADATA-20260804-01/home_result.stdout.txt` | HOME resolver remains Fire Launcher priority 50 during the metadata capture | Confirmed |

The OTA capture used Test ID `PHASE5CF-OTA-METADATA-20260804-01`; its raw
directory contains a separate SHA-256 manifest. No OTA operation was invoked.

The baseline includes the device serial in raw evidence for chain-of-custody; the
public report does not treat the serial as a technical exploit input.
