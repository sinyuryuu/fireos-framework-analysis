# Phase 3C Home callback analysis

Phase 3B static evidence remains the code baseline. PhoneWindowManager calls
the Amazon KeyPolicyManager hook before the framework Home path. startDockOrHome
exposes vendor PhoneWindowManager callbacks. ActivityStackSupervisor calls the
VendorActivityStackSupervisorCallback before PackageManagerInternal.

The inspected Amazon AppCompatActivityStackSupervisorCallback delegates to
IPackageManager.resolveIntent and filters uninstalled apps; it does not name
Fire Launcher. LauncherHijackPreventerActivityStackCallback.canSeeHomeTask is
a visibility/policy check, not a direct Fire launch in the inspected method.

The Phase 3C p0 mutation changed the preferred XML but did not change resolver
or foreground output at Home key, explicit HOME, lock/unlock, or reboot.

已證實: callback boundaries exist.
高可信推論: the observed normal path falls through to the standard resolver.
待驗證: a callback could return a special result in an unobserved mode,
profile, or native service condition.
