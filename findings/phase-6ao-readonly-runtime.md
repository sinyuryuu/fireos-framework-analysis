# Phase 6AO — PS7331 read-only runtime baseline

Generated from `adb/phase6ao/PHASE6AO-RO-20260805-01/` using the exact serial
`G001LT0511550CFT`.

## Scope and safety

This capture used only `adb devices`, `get-state`, `id`, `getenforce`, `uname`,
`getprop`, package dumps/queries, resolver queries, service listing, settings
and policy dumps, overlay listing, AppOps read, user listing, and
`logcat -b all -d`. It did not clear logcat, start an Activity, send a
broadcast, obtain or transact on a private Binder service, change settings or
package state, reboot, invoke OTA/recovery, or write a partition.

The raw command manifest and per-file SHA-256 values are in
`adb/phase6ao/PHASE6AO-RO-20260805-01/metadata.json` and `sha256sums.txt`.
The public commit carries a 128 KiB filtered subset at
`artifacts/phase6ao/public-summary-20260805-01/`; it deliberately omits the
full logcat, full package dump, activity/window dumps, and raw `getprop`.
The exporter records hashes back to the complete local capture.

## 已證實

1. The selected target was online as `device`, shell UID was `2000`, SELinux
   was `Enforcing`, and the kernel identified as `4.4.146+` on AArch64.
2. The observed build fingerprint was
   `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`.
3. The HOME resolver returned:

   ```text
   priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
   com.amazon.firelauncher/.Launcher
   ```

4. The read-only HOME candidate query returned seven activities. Fire
   Launcher was the only priority-50 candidate; Microsoft Launcher and the
   Phase 4 research candidates were priority 0, while Settings FallbackHome
   was priority -1000.
5. Fire Launcher was loaded from
   `/system/priv-app/com.amazon.firelauncher/com.amazon.firelauncher.apk` and
   its package dump reported `PRIVATE_FLAG ... PRIVILEGED`, UID `10120`,
   version `1.3.239105.0_89024510`.
6. `dumpsys package preferred-xml` returned an empty
   `<preferred-activities />` document in this baseline. `dumpsys role`
   returned `Can't find service: role`; this Fire OS build does not expose an
   Android Role Manager dump under that service name.
7. The service list exposed names such as
   `amazonpackagemanager`, `amazonactivitymanager`, `amazonwindowmanager`,
   `amazon_keyevent`, `amazon_input`, `amazondevicepolicymanager`, and
   `fosdebug`. Service listing alone is not evidence that shell can obtain or
   transact on any of them.
8. `com.amazon.device.software.ota` was a privileged system package at
   `/system/priv-app/DeviceSoftwareOTA`, UID `10017`; OOBE was a privileged
   system package at `/system/priv-app/com.amazon.kindle.otter.oobe`, UID
   `10023`. The OOBE dump contains a priority-100 `OobeHomeActivity` filter
   with `CATEGORY_HOME` and `CATEGORY_SETUP_WIZARD`, but this capture did not
   activate it.

## 高可信推論

The live state is consistent with the existing static Phase 6Q–6AP chain:
Fire Launcher is a privileged system candidate, ordinary third-party HOME
candidates remain present but rank at zero, and no ordinary preferred record
or Role Manager state was visible in this snapshot. The OOBE priority-100
candidate is a guarded setup/OTA lifecycle surface, not evidence of a normal
third-party HOME route.

The existence of private Amazon services does not establish a shell bypass.
Earlier SELinux and Binder-contract evidence remains the controlling evidence
for reachability; no private service was invoked in this capture.

## 已排除／尚未證明

- **已排除：** treating the service-list names as proof of shell-accessible
  Binder methods.
- **尚未證明：** that an OOBE or `BOOT_AFTER_SYSTEM_OTA` path can be safely
  replayed by a third-party app or that it would replace HOME.
- **尚未證明：** that the OOBE priority-100 setup candidate is active for the
  normal configured user; its package metadata was observed, but no lifecycle
  event was triggered.
- **因風險拒絕：** manual OOBE/OTA broadcasts, unknown Binder transactions,
  updater/recovery execution, package-state changes to Amazon core packages,
  Root, remount, or partition operations.

## Reproduction

```sh
python3 tools/scripts/capture_phase6q_readonly.py --dry-run \\
  --serial G001LT0511550CFT \\
  --output adb/phase6ao/PHASE6AO-RO-20260805-01

python3 tools/scripts/capture_phase6q_readonly.py \\
  --serial G001LT0511550CFT \\
  --output adb/phase6ao/PHASE6AO-RO-20260805-01
```

The script refuses a non-online target, requires an explicit serial, refuses
to overwrite an existing output directory, and records every command and
hash. To create the public subset from the preserved local capture:

```sh
python3 tools/scripts/export_phase6ao_public_summary.py --dry-run
python3 tools/scripts/export_phase6ao_public_summary.py \\
  --source adb/phase6ao/PHASE6AO-RO-20260805-01 \\
  --output artifacts/phase6ao/public-summary-20260805-01
```

The ADB capture command is shown for reproduction only; the committed local
capture was already completed and must not be overwritten.
