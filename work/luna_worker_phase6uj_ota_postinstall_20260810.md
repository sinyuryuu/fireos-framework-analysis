# Fire HD 10 / Fire OS 7.3.3.1 OTA post-install static inventory

Host-only inventory completed 2026-08-10. Scope is the exact locally present PS7331 package and preserved derived artifacts. No download, malformed-payload test, sideload, flash, reboot, updater execution, recovery execution, tablet contact, or partition mutation was performed.

## Inputs and hashes

- OTA: `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin`, 1,301,005,356 bytes, SHA-256 `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`.
- Extracted `META-INF/com/google/android/update-binary`: SHA-256 `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b`.
- Extracted `META-INF/com/google/android/updater-script`: SHA-256 `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248`.
- Extracted `META-INF/com/android/otacert`: SHA-256 `5d52405362dcc9e755a4d972074ac7f886a5450e18fb6a6c2c2dad2b55730fe1`.
- Extracted `META-INF/com/android/metadata`: SHA-256 `9501caa9c986904bda3fe0f0e5f21134f968edaf30a4949779357d2aeb66bbf2`.
- DeviceSoftwareOTA APK: SHA-256 `35b2cd7ab72549277b691e603039a155d26a9a850c753f80c7cda968053c88ce`.
- DeviceSoftwareOTA contracts APK: SHA-256 `815e38eb47f6d9090087f9a399e1d9e5aebd1aefc441d9a82128e4f92f76685c`.

The package metadata identifies `Fire OS 7.3.3.1 (PS7331.4463N/4463)`, product `trona`, `ota-type=BLOCK`, `key_type=release-keys`, `sign_type=release`, post-timestamp `1746234888`, and a 27-member ZIP. The preserved member table includes `META-INF/com/android/otacert`, `update-binary`, `updater-script`, boot-chain images, system/vendor transfer data, and no post-install shell script member.

## Static findings

1. The script gates on build timestamp and `ro.product.device == "trona"` (`firmware/extracted/PS7331/META-INF/com/google/android/updater-script:1-2`). It then invokes `block_image_update` for system and vendor and `package_extract_file` for boot, preloader, lk, tee1/tee2, spmfw, sspm_1, cam_vpu1/2/3 (`:6-23`). It writes `target.blocklist` to `/cache/recovery/last_blocklist` (`:24`). These are privileged partition/cache sinks, but are normal full-OTA behavior and not evidence of an exploit.

2. `update-binary` statically registers `package_extract_file`, `getprop`, `file_getprop`, `apply_patch`, `block_image_update`, `write_value`, `run_program`, `wipe_block_device`, `reboot_now`, and related handlers (`artifacts/phase6mk-updater-dispatch-20260810-04/registration-dispatch.csv:1-25`; symbol anchors `RegisterInstallFunctions=0x406978`, `PackageExtractFileFn=0x401fb8`, `WriteToPartition=0x413c40`, `ota_open=0x426338`, `ota_write=0x426d58`). Direct selected edges reach `open`, `write`, `rename`, `chown`, and OTA file extraction (`artifacts/phase6md-native-updater-path-audit-20260810-02/path-write-call-edges.csv`). This establishes a privileged sink surface, not runtime reachability from an untrusted caller.

3. Block-image dispatch is indirect but symbol-resolved: `block_image_update` maps to `BlockImageUpdateFn` and then `PerformBlockImageUpdate`; `PerformBlockImageUpdate` reaches `ota_open`, `open`, `chown`, `rename`, and `WriteToPartition` (`artifacts/phase6mm-updater-blockimage-20260810-01/block-image-registration.csv:1-6`; `selected-functions.csv:1-13`; `canonicalization-call-sites.csv:1`). SHA-1/block verification symbols and `VerifyBlocks` are present in the selected symbol set. Cache handling calls `CacheSizeCheck`, `MakeFreeSpaceOnCache`, `__readlink_chk`, `unlink`, and `FreeSpaceForFile` (`artifacts/phase6ne-updater-cache-flow-20260810-03/direct-call-edges.csv`; `return-branches.csv`).

4. Path-hardening is unresolved. `realpath`, `symlink_realpath`, `readlink`, `readlinkat`, and `__readlink_chk` markers exist, and one direct `MakeFreeSpaceOnCache -> __readlink_chk` edge is preserved. The selected updater graph has no direct canonicalization edge into extraction or partition write; this is bounded negative evidence only. No malformed, symlink, traversal, or replacement-input test was performed.

5. Signature/rollback gates: package metadata and `otacert` are present; the script has a timestamp anti-newer-build check and product gate (`updater-script.txt:1-2`). Preserved Java OTA source shows metadata/version/product/signature-transition/PVT checks, recovery verification, and the final `UpdateSystem.install` sink (`artifacts/phase6j/ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/dcp/ota/SideloadMetadataChecker.java:24-71`, `SideloadVerifier.java:15-66`, `SideloadInstaller.java:40-74`, `com/amazon/device/framework/UpdateSystemWrapper.java:34-43`). These are static source contracts; no arbitrary package was verified. AVB rollback-index enforcement is UNKNOWN: exact local paths `firmware/extracted/PS7331/vbmeta.img`, `firmware/extracted/PS7331/META-INF/com/android/avb*`, and recovery verifier implementation source are not present.

6. Post-install hook: the preserved system-server disassembly shows `AmazonPackageManagerService.onBootPhase` sending `BOOT_AFTER_SYSTEM_OTA` only at boot phase 550 and when `PackageManagerService.isUpgrade()` is true (`artifacts/phase6my-bootafter-ota-package-helper-20260810-01/call-edges.csv:6MY-E01`, `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96087-96126`). `BootAfterSystemOTAReceiver` gates the action and OOBE/demo state, enables only `OobeHomeActivity`, and writes `user_setup_complete=0` / `isOOBEActive=1` through secure settings (`call-edges.csv:6MY-E02-E07`; source anchors in `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/...`). The reviewed chain contains no Fire Launcher or ordinary preferred-HOME API. Exact numeric user scope remains unresolved.

7. Init/service definitions: the local system-image-derived fosinit extraction contains `fireossystemota_fosinit.xml:9-12`, registering `VendorRecoverySystemCallback -> com.amazon.android.os.ota.FireOSSystemOTACallback`; `amazonpackagemanager_fosinit.xml:9-24` registers the Amazon Package Manager service and system-server callbacks; `amazonactivitymanager_fosinit.xml:9-28` registers the Amazon Activity Manager service/manager. These definitions are present in `artifacts/phase6jd-fosinit-20260808-01`, not as a separate raw OTA member, so exact source-to-package provenance is medium confidence.

## Conservative conclusion

The local evidence is sufficient to classify this as a signed-release, full block OTA with explicit recovery/update-binary gates and direct privileged partition, cache, file, and post-OTA lifecycle sinks. The reviewed static material does not prove that untrusted input reaches those sinks without the package/product/version/signature/recovery and lifecycle gates. It also does not close native recovery verification, AVB rollback enforcement, indirect dispatch, canonicalization, or exact user-scope questions. Therefore the conservative result is **high-impact update boundary; no confirmed untrusted-to-privileged bypass; several implementation details UNKNOWN**.
