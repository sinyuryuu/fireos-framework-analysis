# Phase 6AC：android.amazon.perm protected-broadcast audit

## Result

- Source package: `android.amazon.perm`
- Shared user ID: `android.uid.system`
- Protected-broadcast declarations in this manifest: **158**
- Target action: `amazon.intent.action.BOOT_AFTER_SYSTEM_OTA`
- Target action in this manifest: **True**
- Classification: **CONFIRMED_PROTECTED_BROADCAST_IN_SOURCE_PACKAGE**

The package manifest contains the protected broadcasts listed in
`protected-broadcasts.csv`; the target `BOOT_AFTER_SYSTEM_OTA` action is present
in this manifest when `target_action_present_in_this_manifest` is true. This is
stronger than a string search over an unrelated framework manifest because
`android.amazon.perm` is the saved source package for the
`RECEIVE_BOOT_AFTER_SYSTEM_OTA` permission. It still does not prove that no
other system package or runtime source can add or remove the action from
`PackageManagerService.mProtectedBroadcasts`.

## Safety

This run was host-only.  No ADB, broadcast, Binder transaction, OTA/recovery,
package/settings mutation, reboot, or partition operation was performed.
