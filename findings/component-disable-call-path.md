# Component Disable Protected-Package Call Path

Status: `Confirmed` for the tested Fire OS build and shell caller. The exact package-set membership is `Strong evidence` because the device-side deny-list file is not readable by shell.

## 1. Runtime entry points

The two preserved tests used different shell front ends:

```text
pm disable-user --user 0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher
cmd package disable-user --user 0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher
```

Both returned:

```text
Security exception: Cannot disable a protected package: com.amazon.firelauncher
```

Evidence: `P2-RUN-001`, `P2-RUN-002`.

The runtime Java line-number stack is:

```text
PackageManagerService.setEnabledSetting(PackageManagerService.java:21128)
PackageManagerService.setComponentEnabledSetting(PackageManagerService.java:21057)
PackageManagerShellCommand.runSetEnabledSetting(PackageManagerShellCommand.java:1624)
PackageManagerShellCommand.onCommand(...)
PackageManagerService.onShellCommand(...)
IPackageManager$Stub.onTransact(...)
```

This is the observed component path. The package path is also present in the same Fire OS PMS VDEX and converges on the same private helper.

## 2. Minimum confirmed call graph

```text
pm / cmd package
  -> PackageManagerShellCommand.runSetEnabledSetting(int)
  -> IPackageManager.setComponentEnabledSetting(ComponentName,int,int,int)
  -> PackageManagerService.setComponentEnabledSetting(ComponentName,int,int,int)
  -> PackageManagerService.setEnabledSetting(String,String,int,int,int,String)
  -> ProtectedPackages.isPackageStateProtected(int,String)
  -> SecurityException("Cannot disable a protected package: ...")
```

For whole-package requests, `PackageManagerShellCommand.runSetEnabledSetting(int)` calls `IPackageManager.setApplicationEnabledSetting(String,int,int,int,String)` instead. Fire OS `PackageManagerService.setApplicationEnabledSetting` also enters the same `setEnabledSetting` helper. This establishes the shared protected gate without assuming that the two shell commands have identical parsing code.

## 3. Static instruction evidence

### `PackageManagerShellCommand.runSetEnabledSetting`

File: `decompiled/baksmali/vdexExtractor/services/disassembly.log:500701-500765`.

- Method descriptor: `runSetEnabledSetting(I)I`.
- Code offset: `0x2dbac8`.
- Whole-package branch invokes `IPackageManager.setApplicationEnabledSetting(Ljava/lang/String;IIILjava/lang/String;)V` at instruction offset `0x2dbb62`.
- Component branch invokes `IPackageManager.setComponentEnabledSetting(Landroid/content/ComponentName;III)V` at instruction offset `0x2dbbc2`.

Evidence: `P2-STATIC-003` plus runtime `P2-RUN-001`/`P2-RUN-002`.

### `PackageManagerService.setComponentEnabledSetting`

File: `services/disassembly.log:966830-966833`.

- Method descriptor: `setComponentEnabledSetting(Landroid/content/ComponentName;III)V`.
- Code offset: `0x2d42f0`.
- The method delegates to the package/class helper rather than providing a second independent protected-package decision.

### `PackageManagerService.setEnabledSetting`

File: `services/disassembly.log:953377-953543`.

- Method descriptor: `setEnabledSetting(Ljava/lang/String;Ljava/lang/String;IIILjava/lang/String;)V`.
- Code offset: `0x2d432c`.
- Caller and cross-user permission checks occur before the protected-package check.
- The protected check loads `mProtectedPackages` at `0x2d458a`.
- It calls `ProtectedPackages.isPackageStateProtected(ILjava/lang/String;)Z` at `0x2d458e`.
- If true, it constructs a `SecurityException` at `0x2d459c` and uses the exact string `Cannot disable a protected package: ` at `0x2d45aa`.
- The later shell UID/test-only restriction is not the observed cause; the protected-package branch is earlier.

Evidence: `P2-STATIC-001`.

## 4. ProtectedPackages expansion on Fire OS

File: `services/disassembly.log:505721-505832`.

### Constructor

`ProtectedPackages.<init>(Context)` calls `VendorProtectedPackagesCallback.findCallbacks()` at `0x2e1634` and stores the result in `sVendorCallbacks` at `0x2e163c`. It also reads the standard device-provisioning package resource.

### `isProtectedPackage(String)`

`ProtectedPackages.isProtectedPackage(Ljava/lang/String;)Z` has code offset `0x2e1590`. It checks the device-provisioning package and then calls:

```text
VendorProtectedPackagesCallback.callShouldProtectPackage(
    sVendorCallbacks,
    Binder.getCallingUid(),
    packageName,
    mContext)
```

The callback call is at `0x2e15ba`. This means the caller UID is an input to the vendor extension.

### `isPackageStateProtected(int,String)`

The public method starts at `services/disassembly.log:505830`, code offset `0x2e156a`. Its result combines owner protection and `isProtectedPackage(packageName)`. The owner branch is the standard Device Owner/Profile Owner path; the vendor callback is the path relevant to the shell error.

Evidence: `P2-STATIC-002`.

## 5. Vendor callback aggregation

Fire OS declares `VendorProtectedPackagesCallback` at `services/disassembly.log:539216-539249`.

`callShouldProtectPackage([VendorProtectedPackagesCallback; int; String; Context)Z` starts at code offset `0x302b30`. It loops over all registered callback objects and ORs each callback's `shouldProtectPackage(uid, packageName, context)` result at `0x302b42-0x302b4a`.

Evidence: `P2-STATIC-003`.

## 6. Amazon callback and inputs

Class: `com.amazon.android.service.pm.ControlProtectedPackagesCallback`

File: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96950-97049`.

The relevant method is:

```text
shouldProtectPackage(int uid, String packageName, Context context): boolean
```

The extracted control flow:

```text
isSystemApp(packageName, context)
  AND shouldDisableAmazonApp(packageName, context)
  AND uid == 2000 (Process.SHELL_UID)
  -> true
otherwise
  -> false
```

The callback reads a device-protected SharedPreferences file backed by the data-system path and uses the key `DenyListKeyPackages`. The `isSystemApp` helper queries `ApplicationInfo` and requires the system-related flag bits shown in the VDEX. The exact device-side set contents were not readable as shell.

Amazon connects this callback to system-server with:

```xml
<callback base="com.android.server.pm.VendorProtectedPackagesCallback"
    impl="com.amazon.android.service.pm.ControlProtectedPackagesCallback"
    classLoader="SYSTEMSERVER" />
```

File: `artifacts/amazon-services/amazonpackagemanager_fosinit.xml:22-24`.

Evidence: `P2-STATIC-004`, `P2-STATIC-005`, `P2-STATIC-007`.

## 7. What is confirmed and what is not

| Question | Result |
|---|---|
| Which class rejects the request? | `PackageManagerService`, via `setEnabledSetting`; `Confirmed`. |
| Which decision method? | `ProtectedPackages.isPackageStateProtected`; `Confirmed`. |
| Does caller UID matter? | Yes: `Binder.getCallingUid()` reaches the vendor callback; Amazon callback explicitly checks UID 2000; `Confirmed` for code path. |
| Is shell UID specifically protected? | Yes for the Amazon callback; `Confirmed` for code path. |
| Is Fire Launcher explicitly hard-coded in the gate? | Not found in the inspected gate/callback code; `Disproved` as a literal-code finding, not as package membership. |
| Is Fire Launcher a member of the runtime deny list? | The runtime error plus callback path make this `Strong evidence`; the list contents were not readable, so literal membership is not `Confirmed`. |
| Is Device Owner/Profile Owner the observed cause? | `Disproved` for the tested error path: the exception occurs in PMS protected-package logic and the Fire package is not the recorded owner package. |
| Does a later watchdog explain the component test? | `Disproved` for T01/T02: no state changed before the error. |

## 8. Remaining minimum experiment

The lowest-risk next step for exact list membership is static/runtime access as an authorized system-server or offline artifact source, not another equivalent `disable-user` command. Shell can stat `/data/system/PackageManagerDenyList` but cannot read its contents on this device. A future authorized artifact acquisition should preserve the file hash and verify whether the set contains `com.amazon.firelauncher`; no permission bypass is proposed here.
