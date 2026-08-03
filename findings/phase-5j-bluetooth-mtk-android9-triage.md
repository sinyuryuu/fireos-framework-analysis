# Phase 5J — Bluetooth / MT8183 Android 9 applicability triage

## Scope

This is a bounded, read-only follow-up for the exact device build. It uses the
preserved PS7330 Bluetooth package state and pulled system artifacts only. It
does not enable Bluetooth, send HCI or AT commands, invoke a private Binder
transaction, start or stop a service, execute a vendor binary, or attempt an
exploit.

Device identity:

| Field | Observed value |
|---|---|
| Serial | `G001LT0511550CFT` |
| Fingerprint | `Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys` |
| Platform | MT8183 / Fire HD 10 (2021) |
| Android base | 9 / API 28 |
| Security patch | 2024-02-01 |
| SELinux | Enforcing |
| Verified boot | green |
| Bluetooth package | `/system/app/Bluetooth/Bluetooth.apk` |

The source of truth is the raw capture and artifact manifests, not the derived
snippets in this report.

## Evidence and reproducibility

| Evidence ID | Evidence | Result | Confidence |
|---|---|---|---|
| `P5J-BT-001` | `adb/phase5/PHASE5J-BLUETOOTH-SURFACE-20260803-01/` | Bluetooth manager reported `enabled: false`, `Bluetooth never enabled!`, zero crashes, and `Bluetooth Service not connected`; the same capture records the package, processes, services, properties, and HOME postcheck. | Confirmed, snapshot-scoped |
| `P5J-BT-002` | `adb/phase5/PHASE5J-BLUETOOTH-SURFACE-FOLLOWUP-20260803-01/` | Init files show `wmt_drv.ko` loaded on boot, `bt_drv.ko` loaded on the vendor readiness property, `btmac` as a system oneshot service, and the Mediatek Bluetooth HIDL service under the `bluetooth` user. | Confirmed, file/snapshot-scoped |
| `P5J-BT-003` | `adb/phase5/PHASE5J-BLUETOOTH-ARTIFACTS-FOLLOWUP-20260803-01/` | APK, ODEX/VDEX, system Bluetooth libraries, permission XML, and init files were pulled read-only. Vendor HAL and kernel modules returned pull failure and were preserved as failed evidence. | Confirmed, shell-visibility-scoped |
| `P5J-BT-004` | `artifacts/phase5/phase5j-bluetooth-static-analysis-20260803/` | Exact VDEX disassembly contains the Amazon Bluetooth policy/GATT classes and permission checks listed below. | Confirmed, artifact-scoped |
| `P5J-BT-005` | `adb/phase5/CMDQ-IOCTL-V3-COMPAT-T01-20260803-01/`, `findings/phase-5h-cmdq-ioctl-result.md` | The separately approved one-shot CMDQ compatibility probe returned raw `-ENOTTY`; no root or Android state change occurred. | Confirmed, runtime-scoped |

Verify the raw captures from the repository root:

```sh
shasum -a 256 -c adb/phase5/PHASE5J-BLUETOOTH-SURFACE-20260803-01/sha256sums.txt
shasum -a 256 -c adb/phase5/PHASE5J-BLUETOOTH-SURFACE-FOLLOWUP-20260803-01/sha256sums.txt
shasum -a 256 -c adb/phase5/PHASE5J-BLUETOOTH-ARTIFACTS-FOLLOWUP-20260803-01/sha256sums.txt
```

The derived VDEX index is reproducible without a device:

```sh
tools/scripts/extract_phase5j_bluetooth_focus.py \
  --log artifacts/phase5/phase5j-bluetooth-vdex-extract/vdex-extractor.log \
  --output artifacts/phase5/phase5j-bluetooth-static-analysis-<new-run-id>
```

The script refuses to overwrite an existing output directory and supports
`--dry-run`.

## Package privilege surface

The exact manifest and package dump show:

- package `com.android.bluetooth`;
- `android:sharedUserId="android.uid.bluetooth"` and user ID `1002`;
- system package at `/system/app/Bluetooth` with code in the matching ARM64
  ODEX/VDEX;
- `directBootAware=true` and default device-protected storage;
- `android:persistent=false` in the manifest;
- granted privileged permissions including `BLUETOOTH_PRIVILEGED`,
  `BLUETOOTH_STACK`, `WRITE_SECURE_SETTINGS`, `MODIFY_PHONE_STATE`,
  `MANAGE_APP_OPS_MODES`, `PACKAGE_USAGE_STATS`, and cross-user permissions.

This is a high-privilege system Bluetooth identity. It is not the shell UID,
and the evidence does not show a route for an ordinary ADB shell to assume the
shared UID or call its privileged interfaces. The package privilege surface is
therefore **not** root evidence.

The relevant files are:

- `decompiled/jadx/phase5j-bluetooth/resources/AndroidManifest.xml`
- `adb/phase5/PHASE5J-BLUETOOTH-SURFACE-20260803-01/device.bluetooth-package.stdout.txt`
- `adb/phase5/PHASE5J-BLUETOOTH-ARTIFACTS-FOLLOWUP-20260803-01/files/system__app__Bluetooth__oat__arm64__Bluetooth.odex`
- `adb/phase5/PHASE5J-BLUETOOTH-ARTIFACTS-FOLLOWUP-20260803-01/files/system__app__Bluetooth__oat__arm64__Bluetooth.vdex`

## Amazon code found in the exact VDEX

### `AmazonBtPolicyManagerAdapter`

The disassembly identifies class `#1586` at source-log lines 160770 onward:

`artifacts/phase5/phase5j-bluetooth-static-analysis-20260803/focus-classes/com_android_bluetooth_amznbtpolicymgr_AmazonBtPolicyManagerAdapter.txt`

The class contains private native declarations for BTPM operations, including
LE connect/disconnect, scan, client registration, request priority, scan
parameters, link count, initialization, and cleanup. Its Java-side callbacks
forward connection, registration, scan-parameter, and request-priority events
to `FosGattService` through methods such as:

- `onBtpmConnNotifyCallback`
- `onBtpmConnReqCallback`
- `onBtpmDisconnNotifyCallback`
- `onBtpmDisconnReqCallback`
- `onBtpmPreferredConnParamsCallback`
- `onBtpmUpdateScanParamsCallback`
- `onBtpmRegisterAppCallback`
- `onBtpmSetConnScanParamsCallback`
- `onBtpmSetReqPriorityCallback`

The class is a singleton and has a `setGattService(FosGattService)` link. This
confirms an Amazon Bluetooth policy adapter in the exact VDEX. It does **not**
show that it accepts shell callers, changes Android package state, or provides
a privilege transition.

### `FosGattService`

The disassembly identifies class `#2843` at source-log lines 507658 onward.
The service extends the standard GATT service and adds an extended binder plus
an Amazon client map. Relevant methods include:

- `registerClient(...)` overloads;
- `setAmazonBluetoothGattCallback(...)`;
- `setRequestPriority(...)`;
- `startScan(...)` and `unregisterClient(...)`;
- `onBtpm*Callback(...)` methods;
- native `gattConnectionParameterUpdateNative(...)`.

The entry points enforce `android.permission.BLUETOOTH` and, on selected paths,
call `enforceAdminPermission()` or `enforcePrivilegedPermission()`. The
`setAmazonBluetoothGattCallback` implementation looks up the UUID/client and
stores an `IAmazonBluetoothGattCallback`; it does not contain a Fire Launcher,
PackageManager, HOME, or shell-UID branch in the reviewed slice.

### Native boundary

The pulled `libbluetooth_jni.so` exports the ordinary Bluetooth/GATT JNI
registration and the `gattConnectionParameterUpdateNative` implementation.
Its dynamic dependencies include `libbluetooth-binder.so` and the standard
Android runtime libraries. The reviewed exported symbol/string set does not
identify the private BTPM native registration point. That location remains
unresolved; this is an analysis gap, not evidence that the native method is
reachable by shell.

## Public vulnerability scope versus this device

The official MediaTek February 2022 bulletin lists several Bluetooth issues in
software families that include MT8183 and Android 9, including CVE-2022-20025
through CVE-2022-20028 and CVE-2022-20041 through CVE-2022-20046. The March 2022
bulletin also lists MT8183/Android 9 in the scope of CVE-2022-20053 and
CVE-2022-20054, but those rows concern IMS/AT-command paths rather than this
Bluetooth package.

These bulletin rows establish public chipset/software-family applicability;
they do not establish that the exact `PS7330.4104N` Bluetooth ODEX/HAL is
unpatched, that Bluetooth is active in the captured runtime, or that a shell
caller can reach the vulnerable path. The current device patch level is
2024-02-01, while the public bulletin rows are from 2022, so binary patch
status cannot be inferred from the bulletin alone.

References:

- [MediaTek February 2022 Product Security Bulletin](https://corp.mediatek.com/product-security-bulletin/February-2022)
- [MediaTek March 2022 Product Security Bulletin](https://www.mediatek.com/product-security-bulletin/March-2022)
- [NVD CVE-2022-20041](https://nvd.nist.gov/vuln/detail/CVE-2022-20041)
- [NVD CVE-2022-20027](https://nvd.nist.gov/vuln/detail/CVE-2022-20027)

## Root-route assessment

| Question | Finding | Status |
|---|---|---|
| Is Bluetooth code present? | Yes: exact package plus ODEX/VDEX and system libraries. | Confirmed |
| Is Amazon Bluetooth policy code present? | Yes: `AmazonBtPolicyManagerAdapter` and `FosGattService`. | Confirmed |
| Was Bluetooth active in the snapshot? | No: manager says never enabled and service not connected; a vendor HIDL process and init definitions are still present. | Confirmed, snapshot-scoped |
| Can shell read the vendor HAL/modules? | Tested pulls failed with permission errors; failed output is preserved. | Confirmed, shell-visibility-scoped |
| Is there a shell-to-root primitive? | None established. No exploit payload, AT command, HCI input, Binder fuzzing, or service manipulation was run. | Unknown / not established |
| Does the CMDQ probe provide root? | No. The single approved ioctl compatibility probe returned `-ENOTTY` and left the device unchanged. | Confirmed negative result for that probe |
| Is the exact Bluetooth code patched? | The pulled binary is exact-build evidence, but no vendor patch-symbol map or trusted vulnerable/fixed diff is available. | Unknown |

## Safety boundary and rejected follow-ups

The following were intentionally not performed:

- enabling Bluetooth or changing any Bluetooth setting;
- starting/stopping `btmac`, the HIDL HAL, or vendor drivers;
- sending AT commands or raw HCI packets;
- calling an unknown Bluetooth Binder transaction;
- executing the vendor HAL, kernel modules, or any exploit payload;
- retrying the approved CMDQ ioctl or changing its arguments;
- BROM/DA, fastboot write/unlock, remount, root, or boot-chain operations.

Any active Bluetooth exploit test, alternate ioctl, v3-aware payload, vendor
binary execution, or boot-chain action is a new high-risk operation and needs a
separate exact scope and approval. The current evidence supports offline
analysis only.

## Verdict

- **已證實：** the exact PS7330 Bluetooth package is a privileged shared-UID
  system component with Amazon-specific GATT/policy extensions.
- **高可信推論：** the normal ADB shell cannot directly use those privileges;
  the captured Bluetooth-off state also provides no demonstrated active
  shell-reachable Bluetooth exploit surface.
- **待驗證：** exact vulnerable/fixed status of the vendor Bluetooth ODEX/HAL,
  and the native registration path for the private BTPM methods.
- **已排除：** treating the public MT8183 CVE scope, the Bluetooth package's
  privileged UID, or the one-shot CMDQ `-ENOTTY` result as proof of root.
- **因風險拒絕測試：** active Bluetooth traffic/exploit attempts, private
  Binder probing, alternate CMDQ payloads, and all boot-chain or memory-write
  operations.

The next lowest-risk step is a host-only comparison of the exact VDEX method
signatures and Android 9 AOSP Bluetooth source, followed by static inspection
of any additional Amazon framework interface artifacts already available. No
device mutation is justified by the present evidence.
