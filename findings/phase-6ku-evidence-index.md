# Phase 6KU Evidence Index

Date: 2026-08-10
Scope: host-only synthesis plus previously captured, reversible runtime tests

## Evidence records

### 6KU-IPC-001

Evidence ID: `6KU-IPC-001`
Source: Phase 6ER physical ordinary-app Binder test and VDEX disassembly
File: `findings/phase-6er-amazon-prewarm-confused-deputy.md:8-11,31-39,50-56,70-86`; `adb/phase6er/PHASE6ER-UNTRUSTED-SERVICE-LOOKUP-20260806-134346/`
SHA-256: report `e3f940fa236a80865d505a3c852ab5030c3265dafa8126d59f58727d949fd548`; complete raw hashes in the phase directory
Test ID: `PHASE6ER-UNTRUSTED-SERVICE-LOOKUP-20260806-134346`
Timestamp: 2026-08-06
Command: documented Phase 6ER APK lookup/prewarm probe; no shell transaction
Observed result: no-permission ordinary APK reached tx1; permission result was ignored; target process PID appeared; no HOME/package-state change
Interpretation: confirmed process/resource confused deputy with no demonstrated launcher or root sink
Confidence: `Confirmed`
Related hypothesis: an ordinary Amazon Binder service could provide a privileged User-0 HOME writer

### 6KU-IPC-002

Evidence ID: `6KU-IPC-002`
Source: Phase 6FI/FJ/FK KFT transaction boundary
File: `findings/phase-6fi-fk-amazon-user-manager-tx-boundary.md:35-45,93-112,195-230`
SHA-256: `23dd37d17af700752faeae35aeaea542e9e7a3ee39ca9eb55c619b34e07f3c08`
Test ID: `PHASE6FJ-USER10-TX3-20260807-01`; `PHASE6FK-USER0-TX3-20260807-01`
Timestamp: 2026-08-07
Command: documented structurally valid tx3 probes from temporary ordinary APKs
Observed result: User 10 rejected by cross-user permission; User 0 rejected by component-state caller gate; no Fire/Tahoe/HOME mutation
Interpretation: Amazon service-side weak check does not bypass downstream PMS authority
Confidence: `Confirmed`
Related hypothesis: KFT tx3 can disable Fire Launcher for User 0 through a confused deputy

### 6KU-IPC-003

Evidence ID: `6KU-IPC-003`
Source: private Amazon PackageManager contract and service reachability closure
File: `findings/phase-6ia-amazon-package-manager-closure.md:7-11,63-74,103-116,133-151,174-180`
SHA-256: `9169af04fe4ebee3e1645d4b097bd07c63cb6d5d3a1329bfc46c6f2421a3f500`
Test ID: `PHASE6IA-AMAZON-PACKAGE-MANAGER-READONLY-20260807-01`
Timestamp: 2026-08-07
Command: read-only service lookup, `service list`, HOME resolve, and package dumps
Observed result: `amazonpackagemanager` was not found to shell; private tx1–tx11 are metadata/proxy/query operations; facade setters delegate to standard PMS
Interpretation: no private User-0 HOME/package-state relay
Confidence: `Confirmed`
Related hypothesis: Amazon private PackageManager Binder bypasses protected-package enforcement

### 6KU-OTA-001

Evidence ID: `6KU-OTA-001`
Source: host-only Phase 6KU callback reconstruction
File: `artifacts/phase6ku/boundary-20260810-01/updater-dispatch.csv`; `result.json`
SHA-256: dispatch `83f6416cad7d5aba74e550059dd3b8aecaabbc951f61ae9b1df18e855de000e1`; result `9ea29dec2c17a72ed0758549a7a975a4245bed76739b78d8cda098264c6054de`
Test ID: `PHASE6KU-HOST-UPDATER-DISPATCH-20260810-01`
Timestamp: 2026-08-10
Command: `python3 tools/scripts/build_phase6ku_boundary.py --root . --output artifacts/phase6ku/boundary-20260810-01`
Observed result: `RegisterInstallFunctions` contains 24/24 recovered callback registrations with handler addresses and symbols
Interpretation: native updater dispatch table is reproducible from preserved artifacts
Confidence: `Confirmed`
Related hypothesis: updater capability could be directly reached by low-privilege ADB/app caller

### 6KU-OTA-002

Evidence ID: `6KU-OTA-002`
Source: host-only parsing of preserved PS7331 updater-script
File: `artifacts/phase6ku/boundary-20260810-01/updater-script-commands.csv`; `firmware/extracted/PS7331/META-INF/com/google/android/updater-script`
SHA-256: script CSV `a4c57723ae0744516409bab371a4bf7282ed457d5dd42b05d5784f3a8966d8ee`; original script `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248`
Test ID: `PHASE6KU-HOST-UPDATER-SCRIPT-20260810-01`
Timestamp: 2026-08-10
Command: same host-only parser; no recovery or updater execution
Observed result: 17 relevant commands parsed; partition-write and cache-metadata records marked `NOT_EXECUTED`; fixed named targets include system/vendor/boot and boot-chain partitions
Interpretation: script expresses high-privilege update capability, not a safe caller route
Confidence: `Confirmed`
Related hypothesis: official OTA material itself is a usable ADB launcher/root workaround

### 6KU-OTA-003

Evidence ID: `6KU-OTA-003`
Source: Phase 6KT Java verification and native updater closure
File: `findings/phase-6kt-recovery-verifier-provenance.md:8-20,44-72,101-138,140-154`
SHA-256: `484273958f44898c6b94a208da4e144936df09a191e03efe6316c18d167fe732`
Test ID: `PHASE6KT-RECOVERY-VERIFIER-AUDIT-20260810-01`
Timestamp: 2026-08-10
Command: host-only Java/artifact audit
Observed result: Java validation calls the platform recovery verification API; native updater has partition I/O; complete recovery-to-updater caller provenance is not in the preserved Java artifacts
Interpretation: low-privilege updater reachability remains unestablished
Confidence: `Strong evidence`
Related hypothesis: recovery/updater is an unguarded low-privilege entry point

### 6KU-SAFETY-001

Evidence ID: `6KU-SAFETY-001`
Source: generated Phase 6KU result policy
File: `artifacts/phase6ku/boundary-20260810-01/result.json`
SHA-256: `9ea29dec2c17a72ed0758549a7a975a4245bed76739b78d8cda098264c6054de`
Test ID: `PHASE6KU-HOST-UPDATER-DISPATCH-20260810-01`
Timestamp: 2026-08-10
Command: host-only parser invocation
Observed result: `adb`, `binder`, `apk_execution`, `native_execution`, `ota_or_recovery`, and `partition_write` are all `false`
Interpretation: this phase produced no device mutation and did not execute high-risk code
Confidence: `Confirmed`
Related hypothesis: boundary analysis can be reproduced without touching the device
