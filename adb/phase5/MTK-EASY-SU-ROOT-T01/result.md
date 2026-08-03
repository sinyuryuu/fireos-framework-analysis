# MTK Easy SU Root-control test — stopped at warning

- Test ID: `MTK-EASY-SU-ROOT-T01`
- Device: `G001LT0511550CFT`
- APK SHA-256: `a2c509d0b0fcee3bc503bd12986da2d29c74ebcd37abb1af8988f7f26382663d`

## Result

- Install: `Success`.
- Launch: `Status: ok`.
- Visible dialog: `Warning`.
- Message: `Misuse of superuser access can seriously damage your device, moreover you are fully responsible for your device.`
- Visible action: `Accept`.
- Warning acknowledged: no.
- Root control activated: no.
- Exploit/payload executed: no.
- `su -c id`: not run.
- Rollback: `adb uninstall juniojsv.mtk.easy.su` returned `Success`.
- Post-rollback package: absent.
- Post-rollback HOME: `com.amazon.firelauncher/.Launcher`.
- Post-rollback foreground: `com.amazon.firelauncher/.Launcher`.
- Post-rollback SELinux: `Enforcing`.
- Post-rollback verified boot: `green`.
- Post-rollback flash lock: `1`.

## Stop reason

The approved Level 3 report prohibited dismissing a security warning through
an unreviewed path. The test therefore stopped before the Root control. A
separate exact approval is required for acknowledging this warning and then
activating the Root control once.

## Evidence

- Pre-state: `../MTK-EASY-SU-ROOT-T01-PRE/`
- Exact warning UI evidence: `window.xml`.
- The `warning-logcat.txt` file is a preserved full device buffer and contains
  later activity as well; it must not be treated as an isolated T01-only
  timeline. The later observation is isolated under `../MTK-EASY-SU-ROOT-T02-OBS/`.
- Post-state: `../MTK-EASY-SU-ROOT-T01-POST/`
- Restore command: `SERIAL=G001LT0511550CFT ./restore.sh`
