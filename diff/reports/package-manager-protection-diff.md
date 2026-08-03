# PackageManager Protected-Package Difference: AOSP Android 9 vs Fire OS 7

Comparison scope: only the enabled-state path, its direct protected-package helper, the Android 9 `ProtectedPackages` class, and the Fire OS vendor extension. This is not a full `services.jar` diff.

## 1. Baselines

| Baseline | Source | Hash / note |
|---|---|---|
| AOSP Android 9.0.0_r1 | `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java` and `ProtectedPackages.java` | Source tree present; no repository commit metadata was available locally |
| AOSP Android 9.0.0_r61 | `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java` and `ProtectedPackages.java` | PMS `bb8d33fbb976c3463d932f65a679dafb2d541845b2989b63d07060d0db8ef179`; ProtectedPackages `fb64ec70c224f527890a28385eb163129a4f235fb8818cd42d31c69ec7cf4508` |
| Fire OS installed services | `decompiled/baksmali/vdexExtractor/services/disassembly.log` | `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53` |

## 2. AOSP standard behavior

AOSP r1 and r61 both implement the relevant shape:

```text
setComponentEnabledSetting()
  -> setEnabledSetting()
  -> mProtectedPackages.isPackageStateProtected(userId, packageName)
  -> SecurityException("Cannot disable a protected package: ...")
```

AOSP `ProtectedPackages.isProtectedPackage()` checks the configured device-provisioning package. `isPackageStateProtected()` also covers Device Owner/Profile Owner protection. The relevant AOSP r1 locations are `PackageManagerService.java:20639-20715` and `ProtectedPackages.java:54-57,104-126`; r61 contains the same relevant logic with line-number drift.

Classification: `AOSP_STANDARD`.

## 3. Fire OS additions/modifications

Fire OS preserves the standard gate shape but adds a vendor callback layer:

1. `ProtectedPackages` constructor calls `VendorProtectedPackagesCallback.findCallbacks()` and stores the callback array.
2. `isProtectedPackage()` calls `VendorProtectedPackagesCallback.callShouldProtectPackage(...)` after the provisioning check.
3. `VendorProtectedPackagesCallback.callShouldProtectPackage()` iterates registered callbacks and ORs their result.
4. Amazon registers `ControlProtectedPackagesCallback` through `amazonpackagemanager_fosinit.xml`.
5. The Amazon callback protects system apps in `PackageManagerDenyList` when the caller is shell UID 2000.

Classification:

| Difference | Classification | Evidence |
|---|---|---|
| `mProtectedPackages` gate and exception string | `AOSP_STANDARD` | `P2-AOSP-001`, `P2-STATIC-001` |
| Owner/provisioning protected-package checks | `AOSP_STANDARD` | `P2-AOSP-001` |
| `VendorProtectedPackagesCallback` type/aggregation | `AMAZON_ADDITION` | `P2-STATIC-002`, `P2-STATIC-003` |
| Amazon callback registration | `AMAZON_ADDITION` | `P2-STATIC-005` |
| Shell UID + deny-list callback decision | `AMAZON_ADDITION` | `P2-STATIC-004` |
| Arcus/resource-backed deny-list producer | `AMAZON_ADDITION` | `P2-STATIC-006` |
| Source line-number differences between r1/r61 | `VERSION_DIFFERENCE` | AOSP source comparison |
| Exact Fire Launcher literal in current deny-list | `UNKNOWN` | Device file content unavailable to shell |

## 4. What this proves

`Confirmed`: Amazon did not need to replace the public Binder API to reject the tested command. Both `pm` and `cmd package` can reach the standard `IPackageManager` method, and Fire OS adds an Amazon callback inside the framework’s protected-package decision.

`Confirmed`: the observed error is not explained by a later package watchdog, because the exception is thrown before enabled-state persistence.

`Strong evidence`: the Fire Launcher is protected for shell because its system-app package name is in the Amazon deny-list consulted by the registered callback.

`Unknown`: whether the exact current list entry arrived from the initial system resource, Arcus runtime update, or another producer. The code supports both initial resource seeding and runtime update.

## 5. Smali/VDEX caution

The Fire OS source is an extracted VDEX disassembly. Decompiled Java is not treated as authoritative for the gate. The critical branch is reported using the VDEX instruction offsets `0x2d458e` and `0x2d45aa`, and the exact runtime exception stack is separately preserved in T01/T02.
