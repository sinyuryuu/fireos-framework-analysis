# Package Protection

Status: `CONFIRMED` for the tested shell disable operation.

## Runtime result

`adb/package-tests/PACKAGE-T01/disable_user.txt:1-14`, `PACKAGE-T03/disable_user.txt:1-14` and `PACKAGE-T05/disable_user.txt:1-14`:

```text
Security exception: Cannot disable a protected package: com.amazon.firelauncher
at com.android.server.pm.PackageManagerService.setEnabledSetting(PackageManagerService.java:21128)
```

The before/after/final package snapshots at line 825 are unchanged: User 0 still has Fire Launcher installed, visible, unsuspended, unstopped and enabled.

`PACKAGE-T02` is the control: Microsoft Launcher changes to `enabled=3` under `pm disable-user` and returns to `enabled=0` after `default-state`. Therefore shell UID 2000 is not globally barred from package state changes. `PACKAGE-T05` uses the equivalent `cmd package disable-user` entrypoint and reaches the same service-side protected-package exception. `PACKAGE-T04` is preserved as an invalid `cmd disable-user` command and is not used as causal evidence.

## Code path

```text
pm disable-user / cmd package disable-user (shell UID 2000)
  -> PackageManagerService.setEnabledSetting()
  -> ProtectedPackages.isPackageStateProtected()
  -> ProtectedPackages.isProtectedPackage()
  -> VendorProtectedPackagesCallback.callShouldProtectPackage()
  -> Amazon ControlProtectedPackagesCallback.shouldProtectPackage()
  -> system app && PackageManagerDenyList contains package && UID == 2000
  -> SecurityException
```

Static evidence:

- `decompiled/baksmali/vdexExtractor/services/disassembly.log:953377-953546` — PackageManager state mutation gate and exact exception string.
- `decompiled/baksmali/vdexExtractor/services/disassembly.log:505771-505837` — ProtectedPackages vendor callback path.
- `decompiled/baksmali/vdexExtractor/services/disassembly.log:539225-539250` — callback aggregation.
- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96950-97049` — Amazon callback reads `DenyListKeyPackages`, requires a system app and checks UID 2000.
- `artifacts/amazon-services/amazonpackagemanager_fosinit.xml:22-24` — Amazon callback registration.

## Determination

- `Confirmed`: PackageManager, not a later watchdog, rejects this request.
- `Confirmed`: both `pm` and `cmd package` reach the same PackageManager protection gate for Fire Launcher.
- `Disproved`: a blanket shell-UID restriction is not the explanation; the Microsoft control package can be disabled and restored.
- `Strong evidence`: Amazon's deny-list callback supplies the vendor-specific protection decision.
- `Hypothesis`: the exact package membership is stored in `/data/system/PackageManagerDenyList`; shell could see the path but not read its contents.
- `Disproved`: “the package was disabled and immediately re-enabled” does not describe `PACKAGE-T01`; the state-changing operation never passed the gate.
- `Confirmed observation`: system/privileged flags are present, but `PERSISTENT` and `CORE_APP` were not shown in the captured package dump.

## Component-level confirmation

The same test was applied to the declared HOME component `com.amazon.firelauncher/com.amazon.firelauncher.Launcher`. Both `pm disable-user` (`COMPONENT-T01`) and `cmd package disable-user` (`COMPONENT-T02`) return the protected-package exception through `PackageManagerService.setComponentEnabledSetting()`. The `disabledComponents` list, HOME resolver and foreground component are unchanged before and after the request. See [component-protection.md](component-protection.md) and the raw runs under `adb/component-tests/`.

## DevicePolicy context

`POLICY-T01` records `com.amazon.parentalcontrols` as the User 0 Profile Owner, with no Device Owner, `Device managed: false` and no effective user restrictions (`adb/probes/POLICY-T01/device_policy.txt:1-12`; `user.txt:9-28`). The decompiled parental-controls APK references Fire Launcher, but its inspected policy implementation calls `DevicePolicyManager.setApplicationRestrictions()` (`decompiled/jadx/parentalcontrols/sources/com/amazon/parentalcontrols/policy/policyImpl/PolicyAppRestriction.java:33-48`) and its package-change hiding path filters for third-party apps before calling `setApplicationHidden()` (`.../receivers/PackageChangesReceiver.java:22-77`; `.../policy/policyImpl/PolicyAppHidden.java:19-33`).

`Confirmed for the tested request`: the active Profile Owner is not the immediate cause of the `pm`/`cmd package` exception; the captured stack terminates at the PackageManager protected-package gate before a DevicePolicy operation. `Hypothesis`: parental controls may still affect Fire Launcher content or UI behavior through application restrictions; the current per-package restriction bundle was not exposed by the read-only shell dump.
