# Phase 3B static reference index

| Symbol / behavior | Input | Location | Classification |
|---|---|---|---|
| `ActivityManagerService.getHomeIntent` | Fire OS JADX | `com/android/server/am/ActivityManagerService.java:2741-2749` | AOSP-shaped |
| `ActivityManagerService.startHomeActivityLocked` | Fire OS JADX | `com/android/server/am/ActivityManagerService.java:2751-2771` | AOSP-shaped |
| `ActivityStackSupervisor.resolveIntent` | Fire OS JADX | `com/android/server/am/ActivityStackSupervisor.java:745-772` | Amazon callback pre-hook |
| `VendorActivityStackSupervisorCallback.callResolveIntent` | Fire OS JADX | `VendorActivityStackSupervisorCallback.java:19-31` | Amazon extension point |
| `PackageManagerService.resolveIntentInternal` | Fire OS JADX | `PackageManagerService.java:3003-3022` | AOSP-shaped |
| `PackageManagerService.chooseBestActivity` | Fire OS JADX | `PackageManagerService.java:3120-3168` | AOSP-shaped priority comparison |
| `PackageManagerService.findPersistentPreferredActivityLP` | Fire OS JADX | `PackageManagerService.java:3197-3275` | AOSP-shaped persistent branch |
| `PackageManagerService.findPreferredActivity` | Fire OS JADX | `PackageManagerService.java:3288-3350` | AOSP-shaped ordinary branch |
| `PhoneWindowManager.handleShortPressOnHome` | services VDEX | `services/disassembly.log:977415-977444` | Amazon key-policy pre-hook |
| `PhoneWindowManager.startDockOrHome` | services VDEX | `services/disassembly.log:988383-988428` | Amazon vendor callbacks |
| `KeyPolicyManagerCommon.launchHomeFromHotKey` | private-services VDEX | `fosservices/disassembly.log:141914-141929` | Standard MAIN+HOME intent |
| `TabletKeyPolicyManager.handleShortPressOnHome` | private-services VDEX | `fosservices/disassembly.log:314232-314262` | Foreground/custom-home hook |
| `HomeEventHandler.handleCustomHome` | private-services VDEX | `fosservices/disassembly.log:141282-141329` | Permissioned custom broadcast |
| `AppCompatActivityStackSupervisorCallback.resolveIntent` | private-services VDEX | `fosservices/disassembly.log:41093-41138` | Queries PM; filters uninstalled app |
| `LauncherHijackPreventerActivityStackCallback.canSeeHomeTask` | private-services VDEX | `fosservices/disassembly.log:136880-136953` | Home-task visibility control |
