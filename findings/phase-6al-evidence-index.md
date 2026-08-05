# Phase 6AL evidence index — HOME resolve callback closure

This index is generated from preserved PS7331 artifacts.  No ADB command,
Binder lookup/transaction, activity start, settings write, package mutation,
or reboot was performed.

| Evidence ID | Surface | Control flow | HOME effect | Confidence |
|---|---|---|---|---|
| `6AL-CB-001` | `framework_dispatcher` | iterate callback array; return the first non-null ResolveInfo; otherwise return null | OEM callbacks can preempt the normal ActivityStackSupervisor fallback only by returning a ResolveInfo | **Confirmed** |
| `6AL-CB-002` | `framework_fallback` | call callback dispatcher; return callback result when non-null; otherwise call PackageManagerInternal.resolveIntent | Home-key ActivityTaskManager path has a pre-PM hook, then AOSP-shaped PM fallback | **Confirmed** |
| `6AL-CB-003` | `registered_callback` | calls IPackageManager.resolveIntent with added match flags; filters only an uninstalled ResolveInfo; returns the PM result or null on error | Can preempt the later fallback with a PM-produced ResolveInfo; no component/package replacement is visible | **Strong evidence** |
| `6AL-CB-004` | `registered_callback` | overrides lifecycle telemetry callOnRestartActivity; inherits base resolveIntent returning null | does not supply a ResolveInfo to the dispatcher in the inspected class | **Confirmed** |
| `6AL-CB-005` | `base_callback` | returns null | unimplemented callbacks fall through to PackageManagerInternal | **Confirmed** |
| `6AL-CB-006` | `registration` | two concrete registrations for VendorActivityStackSupervisorCallback were found in the preserved Amazon registration scope | defines the callback set used by findCallbacks() | **Strong evidence** |
| `6AL-CB-007` | `callback_scope` | AppCompat delegates to PM; Eve/base return null; fallback delegates to PM | no inspected callback creates an explicit Fire Launcher component or bypasses PM ranking | **Strong evidence** |

## Input hashes

| Input | SHA-256 |
|---|---|
| `decompiled/baksmali/vdexExtractor/services/disassembly.log` | `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53` |
| `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` | `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` |
| `artifacts/phase6k/readonly-device-20260805-01/home_resolve.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` |
| `artifacts/phase6k/readonly-device-20260805-01/home_candidates.stdout.txt` | `7c2233e63cd5ca1bd7af1451a369e7cb53797d61e9a6932eae207330f5e284d4` |

## Registrations

| Implementation | Registration file |
|---|---|
| `com.amazon.android.server.am.AppCompatActivityStackSupervisorCallback` | `artifacts/amazon-services/appcompatsupport_fosinit.xml` |
| `com.fireos.eve.EveActivityStackSupervisorCallback` | `artifacts/amazon-services/eve_launch_time_fosinit.xml` |
