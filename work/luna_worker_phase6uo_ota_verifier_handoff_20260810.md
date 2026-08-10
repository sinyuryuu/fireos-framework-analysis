# PS7331 OTA verifier / native handoff closure

Date: 2026-08-10. Host-only static closure for the exact locally extracted Fire HD 10 PS7331 package. Reviewed only existing OTA, updater, recovery/init, Java/decompiled, native, and system-server artifacts. No updater/recovery execution, malformed or symlink input, sideload, reboot, flash, device contact, or partition mutation was performed.

## Identity and result

The package is `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin`, SHA-256 `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`. Preserved metadata identifies Fire OS 7.3.3.1 / PS7331.4463, product `trona`, `ota-type=BLOCK`, `key_type=release-keys`, `sign_type=release`, and post-timestamp `1746234888`. The extracted certificate member is present (`otacert`, SHA-256 `5d52405362dcc9e755a4d972074ac7f886a5450e18fb6a6c2c2dad2b55730fe1`), as are metadata (`9501caa9c986904bda3fe0f5e0f21134f968edaf30a4949779357d2aeb66bbf2`), `update-binary` (`02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b`), and `updater-script` (`4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248`).

Verified static edges close the signed-package Java checks through the `UpdateSystem.install` API boundary and independently close the shipped native updater's recovery-context write capability. They do not close the native recovery verifier implementation, exact recovery-to-`update-binary` caller identity, or low-privilege caller reachability. No bypass or exploit claim is made.

## Verified edges

1. `updater-script:1-2` checks the installed build timestamp and `ro.product.device == "trona"`; `:6-10` invokes `block_image_update` for system/vendor; `:13-23` extracts boot/preloader/LK/TEE/SPMFW/SSPM/camera firmware; `:24` writes `target.blocklist` to `/cache/recovery/last_blocklist`. This is a fixed full-OTA target set and a privileged sink, not evidence of arbitrary input reachability.
2. `OSUpdateValidator.java:73-78` calls hash assertion, `RecoverySystemWrapper.java:21-23` delegates to `android.os.RecoverySystem.verifyPackage`, and `SideloadVerifier.java:31-48,55-59` performs metadata/sanity checks followed by recovery verification. `SideloadInstaller.java:65-84,87-95` preserves the integrity/recovery-check path before `SideloadMover` and install; the method name `verifySideloadWithoutRecoveryCheck` is not treated as a bypass.
3. `SideloadMover.java:31-44` derives a destination from the OTA external-data directory plus the input basename and calls `FileHelper.moveFile`. Java-side canonicalization, no-follow flags, native staging policy, and race behavior are not recovered.
4. `UpdateSystemWrapper.java:33-44` performs path remapping/state handling and calls `UpdateSystem.install`. This is the last verified Java edge; the native/recovery caller identity after this API boundary is missing.
5. The shipped AArch64 `update-binary` statically reaches `main` → `RegisterInstallFunctions` / `RegisterBlockImageFunctions` (`0x400cac`, `0x400cb0`) → common registry (`RegisterFunction`, `0x41d528`). `PackageExtractFileFn` (`0x401fb8`) reaches `ota_open` (`0x426338`) and file I/O; `block_image_update` resolves to `BlockImageUpdateFn` / `PerformBlockImageUpdate`, with `VerifyBlocks` and selected edges to `open`, `chown`, `rename`; `WriteToPartition` (`0x413c40` / selected body `0x413dcc-0x4142f0`) reaches `ota_write` and libc `write`. This confirms capability in the shipped recovery updater, not execution.
6. Cache analysis preserves `PerformBlockImageUpdate` → `CacheSizeCheck` and `MakeFreeSpaceOnCache` → `__readlink_chk`, with `stat`/`unlink` markers. The selected graph does not close a canonicalization return/dataflow edge into extraction or partition writing. No symlink, traversal, replacement, or malformed-input test was performed.
7. Post-install system-server evidence closes `AmazonPackageManagerService.onBootPhase` at phase 550 plus `PackageManagerService.isUpgrade()` → protected `BOOT_AFTER_SYSTEM_OTA` dispatch. `BootAfterSystemOTAReceiver` can enable `OobeHomeActivity` and write `user_setup_complete=0` / `isOOBEActive=1` under its observed predicates. Exact numeric user scope and arbitrary broadcast caller acceptance remain unresolved; no ordinary HOME-selector writer was found.

## Missing or unresolved paths

- The exact platform recovery verifier implementation and its certificate-chain/key identity are absent. `otacert` presence plus Java delegation proves an input/contract boundary, not that cryptographic verification was replayed or that a particular key was accepted.
- Exact local `firmware/extracted/PS7331/vbmeta.img` and `firmware/extracted/PS7331/META-INF/com/android/avb*` paths are absent. AVB descriptor parsing and rollback-index enforcement are therefore UNKNOWN.
- Recovery `UpdateSystem.install` → native recovery entry → `update-binary` provenance, execution flags, SELinux context, and argument identity are absent. The native writer is classified as recovery/high-privilege capability only.
- Native indirect dispatch, complete cache/path canonicalization dataflow, and staging atomicity are not closed. Static `readlink`/`realpath` strings are not treated as proof of a traversal or TOCTOU condition.
- Existing init XML registers `VendorRecoverySystemCallback -> com.amazon.android.os.ota.FireOSSystemOTACallback` (`fireossystemota_fosinit.xml:6-12`), but callback implementation, SELinux allow rules, and final recovery exec edge are absent.

## Conservative disposition

Status: **verified capability and verifier-adjacent gates; handoff/caller/AVB closure UNKNOWN; no exploit claim**. The evidence supports a signed-release block OTA with product/build/timestamp gates, certificate and recovery-verification contracts, block verification markers, fixed partition targets, and a guarded post-install callback. It does not establish an untrusted app or shell path to those sinks.

Machine-readable row ledger: `work/luna_worker_phase6uo_ota_verifier_handoff_20260810.csv`.
