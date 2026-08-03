# Source excerpts and scope

All references below are pinned to the public `master` branch at
`8c6871ac7c15b8e98a47e25c35ab93b87e260475` and were read as text. Line
numbers refer to the raw files fetched on 2026-08-03.

## App build and manifest

- `app/build.gradle:31-37` sets application ID
  `juniojsv.mtk.easy.su`, min SDK 16, compile SDK 34, version code 210 and
  version name `2.2.1-KoModed`.
- `app/src/main/AndroidManifest.xml:320-322` requests INTERNET and
  RECEIVE_BOOT_COMPLETED.
- `app/src/main/AndroidManifest.xml:358-376` declares an exported enabled
  `BootReceiver` for BOOT_COMPLETED and REBOOT. The source tree listing and
  direct `BootReceiver.kt` URL did not provide a matching source file; this is
  an unresolved source/build inconsistency, not evidence that the receiver is
  harmless.

## Exploit execution path

- `ExploitHandler.kt:21-51` creates files below the app private data
  directory, extracts `magisk-boot.sh`, `magiskinit32/64`, `mtk-su32/64`, and
  runs `chmod 510` on them.
- `ExploitHandler.kt:81-95` executes device inspection commands and then runs
  `sh <filesDir>/magisk-boot.sh 32|64` using `Runtime.exec`.
- `ExploitHandler.kt:97-110` treats `/sbin/su` existence as success and then
  deletes extracted files. The LFS content of `magisk-boot.sh` was not
  retrieved, so its exact system interactions remain unknown.
- `MainActivity.kt:46-61` warns when the Android security patch is on or after
  2020-03-01 and offers an ignore path; `MainActivity.kt:146-163` runs the
  exploit handler from the UI button.
- `strings.xml:4-7` describes bootless root from the data partition; this is a
  project claim, not a device compatibility proof.

## Compatibility claims

- README lines 247-252 warn that firmware after March 2020 may block the
  method.
- README lines 261-289 list tested devices. They contain no KFTRWI, trona,
  Fire HD 10, or MT8183 entry. MT6771 is explicitly listed as failed.

## External security reference

- The Android March 2020 bulletin lists CVE-2020-0069 as a High-severity
  MediaTek system elevation-of-privilege issue:
  https://source.android.com/docs/security/bulletin/2020-03-01?hl=en
