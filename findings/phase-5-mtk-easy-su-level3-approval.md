# Level 3 report — proposed `mtk-easy-su` APK execution

## Operation

Download, verify, install, and launch the public release
`mtk-easy-su-v2.2.1-KoModed2.apk` from the pinned GitHub release
`V2.1.1-Optimized1`; then manually activate its root-test control and observe
whether it obtains temporary root on `G001LT0511550CFT`.

## Purpose

Test the user's proposed MTK temporary-root route after ADB package-state
routes were rejected.

## Why ordinary ADB is insufficient

The protected-package gate rejects shell mutations before state change, and
the HOME resolver remains dominated by the privileged Fire candidate. A root
caller would be a materially different authority boundary.

## Exact staged commands proposed

These are a proposal only; none has been executed:

```text
curl -fL --output artifacts/phase5/mtk-easy-su-audit-20260803/mtk-easy-su-v2.2.1-KoModed2.apk \
  https://github.com/KoCleo/mtk-easy-su/releases/download/V2.1.1-Optimized1/mtk-easy-su-v2.2.1-KoModed2.apk
shasum -a 256 artifacts/phase5/mtk-easy-su-audit-20260803/mtk-easy-su-v2.2.1-KoModed2.apk
adb -s G001LT0511550CFT install --user 0 artifacts/phase5/mtk-easy-su-audit-20260803/mtk-easy-su-v2.2.1-KoModed2.apk
adb -s G001LT0511550CFT shell am start -n juniojsv.mtk.easy.su/.MainActivity
```

The expected release digest is
`a2c509d0b0fcee3bc503bd12986da2d29c74ebcd37abb1af8988f7f26382663d`.
The root button would be activated manually in the visible app only after a
separate explicit approval of the execution step; no automated tap or hidden
launch is proposed.

## Files or images written

- Host: one APK download under `artifacts/phase5/`.
- Device: third-party APK/user data through Package Installer.
- The app may extract opaque LFS `mtk-su`/Magisk binaries into its private data
  directory and may create temporary root state. No system image is intended
  by the app's stated design, but root code can write arbitrary device state.

## Compatibility evidence

- Device: MT8183/trona/KFTRWI, Android 9, 2024-02-01 patch, kernel 4.4.146+,
  SELinux enforcing, locked/green verified boot.
- Public project: no trona/KFTRWI/MT8183 tested entry; warns that post-March
  2020 firmware may block the method.
- The embedded LFS script and binaries are opaque in the source snapshot.

## Risks

- **Soft brick:** root code could alter services, policies, boot-related data,
  or leave persistent startup behavior.
- **Hard brick:** not expected from the app's documented data-partition design,
  but cannot be ruled out because opaque payload behavior is unverified.
- **Data loss:** possible if the payload or Magisk setup changes user data or
  causes a crash/reboot during write.
- **Rollback:** uninstalling the APK does not guarantee reversal of any root
  changes. A clean rollback is not proven without a factory reset or exact
  recovery image, both outside this operation.
- **Security:** the project requests INTERNET and boot-receiver permissions;
  its release payload is not independently audited here.

## Stop conditions

Stop immediately and do not continue if the app requests boot image patching,
Magisk installation, bootloader unlock, recovery/provisioning reset, system
partition access, or an unknown binary/command. Stop if ADB disappears, the
device boot-loops, SELinux state changes unexpectedly, or any persistent
startup component is created.

## Recovery proposal

If the app only installs and no root action occurs:

```text
adb -s G001LT0511550CFT uninstall juniojsv.mtk.easy.su
```

Then verify package absence, ADB connectivity, fingerprint, SELinux, verified
boot, HOME resolver, and foreground state. This is **not** a recovery method
for arbitrary changes made after successful root; exact recovery would require
separate firmware/recovery evidence.

## Current decision

**因風險拒絕測試，等待對上述精確 staged operation 及其不完整 rollback
風險的明確核准。** No APK has been downloaded, installed, or executed.
