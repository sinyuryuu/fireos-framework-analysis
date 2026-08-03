# MTK Easy SU staged APK test

- Test ID: `MTK-EASY-SU-APK-T01`
- Device: `G001LT0511550CFT`
- APK: `juniojsv.mtk.easy.su` / `2.2.1-KoModed2`
- SHA-256: `a2c509d0b0fcee3bc503bd12986da2d29c74ebcd37abb1af8988f7f26382663d`

## Result

- Download: completed through the exact GitHub release asset API endpoint after the normal release URL returned HTTP 500.
- Verification: passed; local SHA-256 matched the GitHub release digest and `unzip -t` passed.
- Install: `Success`.
- Launch: `am start -W` returned `Status: ok`; `mResumedActivity` and `mCurrentFocus` were `juniojsv.mtk.easy.su/.MainActivity`.
- Root/exploit action: not executed. No button was clicked and no `mtk-su`, Magisk, boot image, partition, or SELinux operation was invoked.
- Rollback: `adb uninstall juniojsv.mtk.easy.su` returned `Success`.
- Post-rollback package: absent from `pm list packages`.
- Post-rollback HOME: `com.amazon.firelauncher/.Launcher`.
- Post-rollback foreground: `com.amazon.firelauncher/.Launcher`.
- Post-rollback verified boot: `green`.
- Post-rollback flash lock: `1`.
- Post-rollback SELinux: `Enforcing`.

## Evidence

- Pre-state: `../MTK-EASY-SU-APK-T01-PRE/`
- Install and launch raw outputs: this directory.
- Post-state: `../MTK-EASY-SU-APK-T01-POST/`
- Offline APK inspection: `../../../../artifacts/phase5/mtk-easy-su-audit-20260803/static-inspection-20260803/`
- Restore command: `SERIAL=G001LT0511550CFT ./restore.sh`

The separate root/exploit button remains outside this staged approval and was not tested.
