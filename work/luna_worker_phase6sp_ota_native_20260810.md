# Phase 6SP — OTA/recovery native-boundary closure

Date: 2026-08-10. Host-only static review of the preserved PS7331 OTA, OTA Java
corpus, recovery/init artifacts, firmware manifests, and Phase 6SK/6MV/6Q*/6R*
reports. No OTA, sideload, recovery, reboot, image modification/repack, unknown
code execution, or partition write was performed.

## Result

The exact shipped artifact under review is the extracted PS7331 OTA member
`firmware/extracted/PS7331/META-INF/com/google/android/update-binary`. It is an
ARM64 statically linked ELF (1,749,792 bytes; SHA-256
`02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b`). Its
native capability closes statically as:

```text
main
 -> RegisterInstallFunctions / RegisterBlockImageFunctions
 -> RegisterFunction (Edify registry, indirect command dispatch)
 -> PackageExtractFileFn or BlockImageUpdateFn
 -> ota_open / ota_write
 -> open / write
```

The preserved PS7331 `updater-script` supplies fixed targets for system, vendor,
boot, and firmware partitions. This proves privileged write capability in the
shipped updater, not execution or low-privilege reachability. The direct
canonicalization marker is bounded to `MakeFreeSpaceOnCache` calling
`__readlink_chk`; no selected direct edge from that helper to extraction or a
partition writer was recovered. Function-pointer targets, omitted CFG edges,
all callers of `MakeFreeSpaceOnCache`/`CacheSizeCheck`, and readlink return/error
data flow remain UNKNOWN.

## Artifact classification and version boundary

- **Shipped artifact:** the PS7331 OTA container and its extracted
  `META-INF/.../update-binary`, `updater-script`, transfer lists, images, and
  OTA certificate. `firmware/manifests/OTA-20260803-01/README.md:18-30`
  records the official PS7331 package and hash; `README.md:46-48` explicitly
  marks it `VERSION_MISMATCH` against the installed PS7330/7.3.3.0 baseline.
- **Source/decompilation only:** the JADX Java files under
  `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/` are
  recovered source views, not proof of the platform native verifier or runtime
  caller identity.
- **Generic AOSP/source-only:** the GPL source contains generic
  `platform/system/core/libcutils/android_reboot.cpp`; its `android_reboot()`
  only maps reboot commands and calls `property_set` at lines 26-52. The saved
  GPL tar scopes do not contain Amazon `/init`, complete recovery, or framework
  source. Do not promote this generic helper to exact Fire OS recovery policy.
- **Fire OS init artifact:**
  `artifacts/phase6jd-fosinit-20260808-01/system/fireos/etc/init/fireossystemota_fosinit.xml:6-12`
  registers `VendorRecoverySystemCallback` to
  `com.amazon.android.os.ota.FireOSSystemOTACallback`. This is a preserved
  init/config callback edge; the callback implementation, native recovery
  verifier identity, SELinux allow rule, and final updater exec edge are not
  present in this artifact.

## Closed edges

1. `OSUpdateValidator.validateOSUpdate` calls hash assertion, recovery package
   verification, and update-property validation at
   `.../OSUpdateValidator.java:73-78`; the wrapper delegates to
   `android.os.RecoverySystem.verifyPackage` at
   `.../RecoverySystemWrapper.java:21-23`. This is Java-side verifier provenance.
2. `SideloadVerifier.verifySideloadPackage` calls the same wrapper after sanity
   and metadata checks at `.../SideloadVerifier.java:31-48`; the normal checked
   path is `verifySideloadWithRecoveryCheck` lines 55-59.
3. `SideloadInstaller.installSideload` performs
   `verifySideloadWithoutRecoveryCheck`, moves the file, and calls install at
   `.../SideloadInstaller.java:65-84`. The method name alone is not a bypass:
   `buildSideload` invokes `verifySideloadIntegrity` (lines 51-63), whose
   recovery-check path is lines 87-95.
4. `SideloadMover.maybeMoveSideloadFile` creates the destination from the OTA
   external-data directory plus the input basename and calls `moveFile` at
   `.../SideloadMover.java:31-44`. Java-level canonicalPath/NOFOLLOW behavior,
   framework/native staging behavior, and race semantics are UNKNOWN.
5. `UpdateSystemWrapper.install` rewrites the external-storage prefix, sets the
   screen-state setting, and invokes `UpdateSystem.install` at
   `.../UpdateSystemWrapper.java:33-44`. The saved corpus does not close the
   native/recovery caller identity after this API boundary.
6. Native `main` calls registration functions at offsets `0x400cac` and
   `0x400cb0`; `RegisterInstallFunctions` calls `RegisterFunction` at
   `0x4069cc` and `RegisterBlockImageFunctions` calls it at `0x40d0fc` (Phase
   6MD/6MM saved call-edge CSVs). The common registry target is `RegisterFunction`
   at `0x41d528`; command-to-function invocation is indirect and was not run.
7. `PackageExtractFileFn` calls `ota_open` at `0x4021b4` to `0x426338` and
   extraction helpers at `0x4022cc`/`0x40238c`; `ota_open` reaches `open` at
   `0x426354` to `0x4cc170`. This is an extraction capability edge.
8. `PerformBlockImageUpdate` calls `ota_open` at `0x409340` to `0x426210`, and
   its saved edges include verification (`VerifyBlocks` at `0x40d474` in
   `LoadSrcTgtVersion3`) plus open/rename/chown operations. The selected
   block-image registry resolves five names (`block_image_verify`,
   `block_image_update`, `block_image_recover`, `check_first_block`,
   `range_sha1`) in Phase 6MM, but runtime dispatch remains unexecuted.
9. `WriteToPartition` spans `0x413c40-0x4142f0`; it calls `ota_open` at
   `0x413dcc`, `ota_write` at `0x413e3c`, `ota_fsync`/`ota_close` in the saved
   edges, and `ota_write` reaches libc `write` at `0x426e44` to `0x4d4a10`.
   This is the actual native write sink capability; `partition_written=false`.
10. `MakeFreeSpaceOnCache` (`0x417778-0x417fc4`) calls
    `__readlink_chk` at `0x417bf0` to `0x4ce4e8`, with nearby `strncmp` at
    `0x417c08`; Phase 6MM records one direct canonicalization-related call site.
    Phase 6MD/6MM record no selected direct path-canonicalization-to-write edge.

## Script targets and caller boundary

`firmware/extracted/PS7331/META-INF/com/google/android/updater-script:6-11`
uses `block_image_update` for fixed `/dev/block/platform/bootdevice/by-name/system`
and `vendor`. Lines 13-23 use `package_extract_file` for `boot`, `preloader`,
`lk`, `tee1`, `tee2`, `spmfw`, `sspm_1`, and `cam_vpu1`–`cam_vpu3`; line 24
extracts the fixed blocklist to `/cache/recovery/last_blocklist`.

The preserved Phase 6SK/6KT/6MD/6MM evidence establishes a privileged recovery
capability, not a shell or ordinary-app caller. Phase 6SK classifies the
low-privilege chain as a bounded negative boundary, not universal absence. The
controller permission evidence is the preserved `DeviceSoftwareOTA` manifest
union (`artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/035_DeviceSoftwareOTA.xmltree.txt:12-18,182-189`),
where protection level `0x3` is signature|privileged. Exact production caller
identity from the controller into the native updater remains unresolved.

## Init/recovery and firmware-manifest limits

`firmware/manifests/OTA-20260803-01/README.md:7-16,20-30` distinguishes the
PS7330 device baseline from the PS7331 package; its `sha256sums.txt:1` records
the original package hash. The firmware manifest therefore authenticates the
saved input provenance, not execution. The Fire OS init callback XML is a
configuration artifact, not the callback implementation. The GPL source's
generic `android_reboot.cpp` is not a shipped recovery binary. No exact
platform `RecoverySystem.verifyPackage` implementation, recovery-to-update-
binary exec edge, updater SELinux domain allow rule, or dynamic dispatch caller
was recovered.

## Safe conclusion

Native parser/registry, extraction, block-image verification/update, and
partition-write capability are statically closed for the shipped PS7331
`update-binary`. Java verifier/staging/install edges are closed only as
PS7331 source/decompilation provenance. Canonicalization-to-write data flow,
native recovery identity, and low-privilege caller reachability are UNKNOWN or
bounded-negative. No conclusion of a traversal bug, verifier bypass, shell
route, root route, or executed partition write is supported.

