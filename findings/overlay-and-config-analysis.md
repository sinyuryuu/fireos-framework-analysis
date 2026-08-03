# Overlay, configuration, and background-rewrite analysis

## Captured runtime configuration

The canonical baseline retains raw outputs for:

- `cmd overlay list`
- `settings list secure/global/system`
- `dumpsys device_policy`
- `service list`, `dumpsys -l`, process list, package list
- `BOOTCLASSPATH`, `SYSTEMSERVERCLASSPATH`, and `DEX2OATBOOTCLASSPATH`

`device_config list` exited `127` on this build and the HOME role-holder query
exited `20`. Those are availability limits, not evidence that the stores are
empty.

## Amazon registration inputs

The preserved `artifacts/amazon-services/*_fosinit.xml` files register:

- `TabletKeyPolicyManager` and `KeyInterceptorCallback`;
- `AmazonActivityManagerService` and its ActivityManager callback;
- `AmazonPackageManagerService` and `ControlProtectedPackagesCallback`;
- `LauncherHijackPreventer` ActivityManager/ActivityStack/PackageManager callbacks.

These registrations establish candidate extension points. They do not state
that a callback rewrites the ordinary preferred HOME record.

## Fire package references

The private-services disassembly contains exact Fire package references in
non-resolver contexts, including external-app notification and the KFT child
launcher enable/disable path. Those references are not evidence of a primary
User 0 resolver ranking branch. The inspected resolver methods contain no
selected Fire package-name condition.

## Background rewrite status

No Phase 3B operation modified preferred state or rebooted the device, by
design. The preserved Phase 3A reboot result shows Fire after the Microsoft
preferred write, but priority ordering already explains that result. A watchdog
or boot receiver rewrite is therefore **Unknown**, not confirmed.

## Next safe static target

Enumerate every concrete class implementing the registered
`VendorActivityStackSupervisorCallback` and
`VendorPhoneWindowManagerCallback` bases in the matching private-services VDEX,
then inspect only their HOME-related methods. This is offline and does not
require stopping a service or changing device state.
