# Phase 5 — `mtk-easy-su` staged APK test

## Scope and authorization

This test covered only the explicitly approved staged sequence:

1. download the public release asset;
2. verify the release digest and ZIP integrity;
3. install the APK for user 0;
4. launch its exported `MainActivity`;
5. collect read-only state; and
6. uninstall the test package and verify rollback.

The Root/exploit control was not clicked. No `mtk-su`, Magisk, `su`, root
shell, boot image, partition, SELinux, or bootloader operation was invoked.

## Device and APK

- Serial: `G001LT0511550CFT`
- Device: `KFTRWI` / `trona`
- Build: `Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys`
- APK package: `juniojsv.mtk.easy.su`
- Version: `2.2.1-KoModed2` / version code `210`
- Release: `V2.1.1-Optimized1`, asset ID `313709550`
- SHA-256: `a2c509d0b0fcee3bc503bd12986da2d29c74ebcd37abb1af8988f7f26382663d`

The normal GitHub release URL returned HTTP 500 during this run. The exact
GitHub release-asset API endpoint returned the expected asset, and the local
hash matched the GitHub release digest. The verification record is
`artifacts/phase5/mtk-easy-su-audit-20260803/apk-release-verification.txt`.

## Static APK evidence

Offline inspection recorded:

- permissions: `INTERNET`, `RECEIVE_BOOT_COMPLETED`;
- exported launcher activity: `juniojsv.mtk.easy.su.MainActivity`;
- exported boot receiver: `juniojsv.mtk.easy.su.BootReceiver`;
- min SDK `16`, target SDK `16`, compile SDK `34`;
- embedded `mtk-su32`, `mtk-su64`, `magiskinit32`, `magiskinit64`,
  `magisk-boot.sh`, and `magisk-manager.apk` assets.

Raw output and the reproducible offline inspection script are in
`artifacts/phase5/mtk-easy-su-audit-20260803/static-inspection-20260803/` and
`tools/scripts/inspect_apk_static.sh`.

## Device results

### 已證實

- Installation returned `Success`.
- `pm path` showed a user APK under `/data/app/` and `pm list packages -U`
  reported UID `10185`.
- HOME resolution remained
  `com.amazon.firelauncher/.Launcher`; installing this non-HOME APK did not
  alter the resolver.
- `am start -W --user 0 -n juniojsv.mtk.easy.su/.MainActivity` returned
  `Status: ok`.
- During the launch snapshot, both `mResumedActivity` and `mCurrentFocus`
  were the test app's `MainActivity`.
- Logcat recorded a normal explicit Activity start and display event. No Root
  button or exploit action was invoked.
- `adb uninstall juniojsv.mtk.easy.su` returned `Success`.
- After rollback the package was absent, HOME resolver and foreground returned
  to Fire Launcher, `ro.boot.verifiedbootstate` remained `green`,
  `ro.boot.flash.locked` remained `1`, and SELinux remained `Enforcing`.

### 高可信推論

The staged APK can be installed and its UI can be launched on this build, but
that demonstrates only package/runtime compatibility. It does not demonstrate
MTK exploit compatibility or provide a HOME workaround.

### 待驗證

The behavior of the embedded exploit payload on this device remains unknown.
It was deliberately not executed because its compatibility and rollback path
are not established.

### 因風險拒絕測試

Root control activation, payload execution, Magisk installation, `su`
invocation, boot/system modification, and any partition or bootloader action
remain outside this staged test.

## Evidence and rollback

- Test record: `adb/phase5/MTK-EASY-SU-APK-T01/`
- Pre-state: `adb/phase5/MTK-EASY-SU-APK-T01-PRE/`
- Post-state: `adb/phase5/MTK-EASY-SU-APK-T01-POST/`
- Test SHA-256 manifest: `adb/phase5/MTK-EASY-SU-APK-T01/sha256sums.txt`
- Restore command: `SERIAL=G001LT0511550CFT adb/phase5/MTK-EASY-SU-APK-T01/restore.sh`

The restore result is `Success`; no Fire Launcher package or data was
modified.
