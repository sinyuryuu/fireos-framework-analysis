# Exact PS7330 material search

## Scope

- Test ID: PHASE5-EXACT-SOURCE-SEARCH-20260803-01
- Device: KFTRWI / trona / MT8183
- Installed build: PS7330.4104N, Fire OS 7.3.3.0, Android 9/API 28
- Shell-readable boot descriptors: d1a4a4b-20231011_072631 (PL) and
  79172a1-20231008_072039 (LK)
- No device command was executed by this artifact collection.

## Result

An Amazon S3 source archive named Fire_HD10-7.3.3.0-20240730.tar.bz2 was
identified. Its HTTP metadata records a 2,588,816,416-byte bzip2 archive last
modified on 2024-07-30. This is a source-code/build-material package, not an
OTA, preloader, LK image, DA, or recovery package.

The bounded archive prefix contains README.txt and application source
directories, including apps/com.amazon.firelauncher/. The README describes
kernel, BusyBox, U-Boot, and AOSP library build workflows, but it does not
provide a signed PS7330 boot-chain image or a device recovery procedure.

The complete archive was intentionally not retained or committed because it is
about 2.59 GB. The bounded inspection cannot establish whether later archive
members contain any particular bootloader source file. It therefore does not
upgrade the exact-loader status.

## OTA history boundary

Archived redirects were checked for the device update endpoint. The captured
historical targets cover PS7319, PS7322, PS7323, PS7326, PS7328, and PS7331;
no PS7330 target was found in those snapshots. This is not proof that no
PS7330 package ever existed.

## Determination

- 已證實：an exact marketing-version Fire HD 10 11th-generation source
  package is publicly referenced, and its bounded prefix is reproducible.
- 已證實：the available complete OTA remains PS7331 and is a version mismatch
  for the installed PS7330 build.
- 高可信推論：the source package is useful for kernel/AOSP build-context
  comparison, but cannot by itself supply the signed preloader/LK/DA/recovery
  inputs needed for a BROM or boot-chain operation.
- 待驗證：whether the full source archive contains a buildable MT8183 kernel
  tree, exact defconfig, or U-Boot source relevant to the installed
  descriptors.
- 因風險拒絕測試：use of PS7331 images, generic MTK payloads, DA upload,
  preloader/LK writes, seccfg, fastboot unlock/flash/erase, and any BROM
  connection without an exact protocol and recovery plan.
