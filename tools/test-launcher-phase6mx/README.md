# Phase 6MX service-handle lookup probe

This is a no-permission, non-HOME APK used only to test whether an ordinary
application can obtain a raw handle from `ServiceManager.getService()` for
selected Amazon service names. It does not call `IBinder.transact()`, does not
construct a `Parcel`, and does not invoke any private service method.

## Reproducible build

```sh
PATH=/opt/homebrew/opt/openjdk@17/bin:$PATH \
  tools/test-launcher-phase6mx/build_lookup_only.sh \
  --output tools/test-launcher-phase6mx/dist/<unique-output> \
  --keystore /path/to/local-debug.keystore \
  --keystore-password '<supplied-out-of-band>' \
  --key-alias androiddebugkey
```

The build records JDK, SDK, manifest, source, APK, and source-archive hashes.
Do not commit a private keystore or password.

## Reversible device probe

Use an explicit serial and a new output directory:

```sh
python3 -B tools/scripts/probe_phase6mx_service_handle_lookup.py \
  --serial DEVICE_SERIAL \
  --apk tools/test-launcher-phase6mx/dist/<unique-output>/org.fireosresearch.phase6mx.lookup.apk \
  --output adb/phase6mx/PHASE6MX-SERVICE-HANDLE-LOOKUP-<timestamp>
```

The runner verifies the device state, captures before/after snapshots, installs
only the test APK on User 0, starts its visible activity, reads tagged logcat,
uninstalls only that test package, and verifies the package path is absent.
It never disables, hides, suspends, force-stops, or clears Fire Launcher and
never sends a Binder transaction, reboot, OTA, or partition command.
