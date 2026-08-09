# Phase 6KT evidence index

| Evidence ID | Source | File / location | Observation | Interpretation | Confidence |
|---|---|---|---|---|---|
| 6KT-INPUT-001 | Host-only generated audit | `artifacts/phase6kt/recovery-verifier-audit-20260810-01/audit.json` | Nine preserved PS7331 OTA/Java inputs were hashed and scanned without device execution. | Reproducible provenance set. | Confirmed |
| 6KT-VERIFY-001 | PS7331 JADX | `RecoverySystemWrapper.java:21-22` | Wrapper delegates directly to `RecoverySystem.verifyPackage`. | Java wrapper is not itself the cryptographic verifier. | Confirmed |
| 6KT-VERIFY-002 | PS7331 JADX | `OSUpdateValidator.java:42-48,72-77` | Pending-update hash, recovery verification, and property validation are ordered checks. | A Java-side validation gate exists before the normal update flow. | Confirmed |
| 6KT-VERIFY-003 | PS7331 JADX | `SideloadVerifier.java:55-58` | Sideload metadata/sanity checks precede the recovery package verification call. | Sideload validation is not an unguarded direct updater call. | Confirmed |
| 6KT-STAGE-001 | PS7331 JADX | `SideloadMover.java:29-43` | Destination is constructed from the input basename and passed to `moveFile`; no Java canonical/no-follow marker appears in the bounded scan. | Native/helper staging behavior remains unknown; not a proven traversal bug. | Hypothesis |
| 6KT-HANDOFF-001 | PS7331 JADX | `SideloadInstaller.java:65-74`, `UpdateSystemWrapper.java:32-43` | Installation eventually calls `UpdateSystem.install` after staging. | High-privilege handoff is present, but caller provenance is unresolved. | Confirmed |
| 6KT-ELF-001 | PS7331 native updater | `firmware/extracted/PS7331/META-INF/com/google/android/update-binary`; Phase 6P CFG | `PackageExtractFileFn`, `WriteToPartition`, `ota_open`, and block verification paths are present. | Native updater has partition-write capability. | Confirmed |
| 6KT-TARGET-001 | Preserved updater script | `firmware/extracted/PS7331/META-INF/com/google/android/updater-script:6,10,13,15-23` | Targets are explicit `/dev/block/platform/bootdevice/by-name/...` paths. | No generic path target was observed in this script. | Confirmed |
| 6KT-REACH-001 | Safety boundary review | `findings/phase-6p-native-updater-closure.md`, `findings/phase-6o-control-boundary.md` | No shell/ordinary-app execution path to updater/recovery was established. | OTA is not a demonstrated low-privilege launcher/root route. | Strong evidence |
| 6KT-SAFETY-001 | Execution record | `tools/scripts/audit_phase6kt_recovery_provenance.py` and generated audit | No ADB, Binder, APK/native execution, OTA input, or partition write occurred. | Device remained outside this phase's mutation boundary. | Confirmed |
