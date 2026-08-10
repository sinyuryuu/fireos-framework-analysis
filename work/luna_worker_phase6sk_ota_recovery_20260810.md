# Phase 6SK — OTA/recovery provenance reconciliation

Date: 2026-08-10. Host-only review of preserved PS7331 / Fire OS 7.3.3.1 OTA and source artifacts, reconciled against Phase 6SH and the recorded PS7330 / Fire OS 7.3.3.0 device baseline. No OTA, sideload, recovery, reboot, partition write, device command, or payload construction was performed.

## Outcome

The bounded evidence confirms the Java verification and install handoffs, protected OTA controller boundary, post-OTA lifecycle/OOBE receiver surface, and native updater write capability. It does not establish a low-privilege caller reaching the verifier/install handoff, `update-binary`, or a partition writer. The native updater and fixed updater-script targets are capability evidence only; the relevant execution edges remain recovery/high-privilege gated and unexecuted.

The PS7331 artifact is adjacent-version evidence: the manifest records the installed baseline as Fire OS 7.3.3.0 / PS7330 and the extracted OTA as Fire OS 7.3.3.1 / PS7331. No exact-PS7330 OTA/source equivalence is inferred.

## Reconciled findings

- `OSUpdateValidator` performs hash, recovery verification, and update-property validation. `SideloadVerifier` calls `RecoverySystemWrapper.verifyPackage`, which delegates to `android.os.RecoverySystem.verifyPackage`. This confirms the Java-side verifier caller, not the platform/native recovery implementation or its caller identity.
- `SideloadInstaller` reaches `SideloadMover` and `UpdateSystemWrapper.install` / `UpdateSystem.install` after the validation branch. The method name `verifySideloadWithoutRecoveryCheck` is not evidence of a bypass: the preserved flow still performs sideload metadata/integrity validation, and no low-privilege caller-to-install chain was established.
- `SideloadMover` constructs the staging destination from the OTA external-data directory plus the input basename. The bounded Java corpus shows no `canonicalPath` or `NOFOLLOW` marker. `FileHelper` uses `renameTo`, buffered copy fallback, source deletion, and an existing-destination MD5 comparison. Canonicalization, symlink behavior, race/atomicity, framework/native staging, SELinux context, and recovery-side checks remain UNKNOWN; no traversal or symlink vulnerability is claimed.
- The archive/path audit reports no symlink entries, duplicate paths, or non-fixed bootdevice targets and classifies the archive/script boundary clean. This is static archive evidence, not proof that block-image contents are semantically safe or that the package was executed.
- `update-binary` statically contains registration/evaluation, block-image verification/update, `ota_open`/`ota_write`, and `WriteToPartition` capability. `updater-script` names fixed `by-name` targets for system/vendor and boot/firmware partitions. The saved reports explicitly leave data-driven dispatch, omitted/indirect callers, recovery staging, and runtime reachability unresolved.
- DeviceSoftwareOTA's controller permission is `signature|privileged` (`0x3`) in the preserved manifest union. Phase 6SD's system-server `onBootPhase(550)` plus `PMS.isUpgrade()` to protected `BOOT_AFTER_SYSTEM_OTA` receiver is a confirmed lifecycle edge; OOBE action/predicate handling is present, but exact delivery user and complete native post-install provenance are partial/UNKNOWN. It is not evidence of an arbitrary broadcast or preferred-HOME writer.
- Reconciliation with Phase 6SH: classifications remain **Confirmed** for Java handoff/capability/protected lifecycle observations, **Unknown** for canonicalization and native recovery implementation details, and **Strong evidence negative boundary** for a shell/ordinary-app route. Absence of a marker or a caller in this bounded corpus is not a universal proof of absence.

## Evidence classification policy

`CONFIRMED` means directly observed in a preserved source/report or static artifact. `OBSERVED-CAPABILITY` means a static implementation capability without execution or reachability. `UNKNOWN` means the cited corpus does not resolve the control. `NEGATIVE-BOUNDARY` means no route was found in the bounded corpus; it is not universal absence. `VERSION-BOUNDARY` marks PS7331 evidence that must not be treated as exact PS7330 evidence.

## Preserved input hashes

The CSV records hashes for the principal Java sources and extracted `update-binary` / `updater-script`: `SideloadVerifier` `4ba31d323419575c4f9294d430bd6e758b38db68b7ff67405150a697cd549eea`; `SideloadInstaller` `98fe15a329e96ec793fc3f50172d945d9d409b734efce084af38bbef49248e4a`; `SideloadMover` `59131cf032d8544cd44ea839ad63eb37993d2853b4925bf56d10ede721693f63`; `RecoverySystemWrapper` `5cea16a23aadebf9c043791fffb80c4e3a78ca629e8f7c64c82a366983790287`; `UpdateSystemWrapper` `c99f6884fa298546b18722a5addb46ae35aff4fa9c9f6003d8ad3ccaebe2edfdbd9`; `OSUpdateValidator` `36fca220ec2332bee5e5af3c9c2317056a425b90507951345d5b729c76c6f256`; `update-binary` `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b`; `updater-script` `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248`.

Final output SHA-256 values are supplied in the handoff message. The CSV contains 14 evidence rows (excluding its header); output self-hashes are intentionally not embedded to avoid self-referential mutation.
