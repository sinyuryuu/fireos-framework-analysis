# Phase 6VE — host-side Amazon Framework IPC sink/caller inventory

Date: 2026-08-10. Scope is host-only static inspection of `artifacts/framework`, `artifacts/services`, `artifacts/amazon-services`, `decompiled/baksmali/vdexExtractor`, `decompiled/jadx`, and available Phase 6O/6Q/6V/6W/6X/6AY evidence. No service/Binder call, device contact, mutation, reboot, OTA execution, or partition write was performed.

## Result

The companion CSV contains 32 normalized rows. The primary enabled-state scan contributes 21 direct callsites plus the common PMS sink; HOME/preferred contributes 6 PMS sinks; user/settings contributes 2 Amazon user-state writers; native OTA/partition contributes 3 static registry/script sinks.

The inventory is cross-launcher. Confirmed literals/targets include `com.amazon.firelauncher`, `com.android.launcher3`, `com.amazon.tahoe.launcher.FreeTimeLauncherActivity`, and `com.amazon.tv.oobe/.RegistrationActivity`. Therefore the evidence is not limited to Fire Launcher.

## Binder/interface mapping boundary

The standard Java/package-manager callsites map to the platform `IPackageManager` service path and the Amazon calls map to an `AmazonPackageManager` wrapper/private Amazon service path. The supplied decompilation does not recover stable transaction integers for these methods; those fields are `UNKNOWN` in the CSV rather than inferred. HOME methods are PMS sinks under the `package` service-manager publication; exact transaction codes and SELinux rules remain `UNKNOWN`.

`phase6q`/`phase6mt` evidence shows Amazon Binder publication and permission checks for several interfaces, but no bounded Amazon IPC method was shown to be a HOME selector or enabled-state writer. Those non-sink interfaces are therefore not promoted into the sink rows.

## Gate and caller conclusions

- Standard PMS state writes remain behind system-server/package-manager validation. Shell reachability is a command path, not an authorization bypass.
- Preferred/HOME writes visibly check `SET_PREFERRED_APPLICATIONS` in the bounded PMS methods; caller UID and explicit `userId` markers are retained.
- KFT state writes are private Amazon user-manager logic, take `UserInfo.id`, and include profile-owner/child-user lifecycle context. They touch Fire Launcher, AOSP Launcher3, and Tahoe FreeTime Launcher in the same method.
- `setUserSetupComplete` delegates to `putIntForUser` under cleared/restored Binder identity; exact key, transaction, and SELinux/service-manager gate are UNKNOWN.
- OTA rows are native recovery/update-binary registry or script sinks, not Binder sinks. The `block_image_update` registration resolves to `PerformBlockImageUpdate`; the selected native closure includes `WriteToPartition`. No updater or partition operation ran.

## Input and provenance

Key exact-build paths and hashes are preserved per row in the CSV. The authoritative existing evidence files are:

- `artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv` (source SHA values embedded per row)
- `artifacts/phase6mw-home-state-sinks-20260810-01/sink-calls.csv` and `input-manifest.csv`
- `artifacts/phase6v/pms-control-surface-20260805-01/pms-control-surfaces.csv`
- `artifacts/phase6ay/launcher-state-services-20260805-02/launcher-state-service-methods.csv`
- `artifacts/phase6mm-updater-blockimage-20260810-01/block-image-registration.csv` and `selected-functions.csv`

The requested phase identifiers are unevenly materialized: 6O, 6Q, 6V, 6W, 6X, and 6AY exist; no standalone 6ED or 6UH directory was found in the workspace. Missing phase output, exact Binder transaction number, exact SELinux rule, and unobserved service-manager publication are explicitly `UNKNOWN` in the CSV.

## Safety and limitations

This is an inventory, not proof of runtime reachability. Native/reflective calls outside the bounded evidence, actual caller UID, package signatures, live service-manager visibility, enforcing SELinux decisions, and exact transaction numbering require inputs not present here. No mutation or runtime validation should be inferred from any static row.
