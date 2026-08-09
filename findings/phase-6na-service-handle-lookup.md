# Phase 6NA — ordinary-app Amazon service-handle lookup

Test ID: `PHASE6MX-SERVICE-HANDLE-LOOKUP-20260810-01`

## Scope and safety

This was a bounded, reversible runtime probe on the authorized PS7331 device.
The test APK had no declared permissions, no HOME intent filter, and only used
reflection to call `android.os.ServiceManager.getService(String)`. It did not
import or call `Parcel`, `IBinder.transact()`, `service call`, an Amazon
interface method, an ioctl, or a package/settings mutation API.

The only device state change was installation of the test APK on User 0,
followed by force-stopping and uninstalling that same test package. Fire
Launcher was not disabled, hidden, suspended, force-stopped, or cleared.

## Result

**已證實:** an ordinary application process with no requested permissions
obtained non-null Binder handles for:

```text
amazonpackagemanager
amazonusermanagerservice
amazonprofileservice
```

The probe log reports UID `10011`. The shell-side `service list` also listed
the names, while the earlier shell `service check` boundary had reported
`not found`. Therefore “shell service check cannot resolve it” and “an app can
obtain a raw handle through `ServiceManager.getService`” are distinct
observations.

**已證實:** this handle visibility did not change HOME. Both snapshots
resolved User 0 to:

```text
priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
com.amazon.firelauncher/.Launcher
```

**已證實:** the test package was removed successfully, its package path was
absent after rollback, and the Fire Launcher package dump retained the same
User 0 state (`installed=true`, `hidden=false`, `suspended=false`,
`stopped=false`, `enabled=0`) in the before/after captures.

**未證明:** a raw handle does not prove that any transaction is callable, that
the caller passes an authorization check, or that any method can alter HOME,
package state, or user state. No transaction was sent deliberately. The
existing static Phase 6MX interface inventory remains the authority for which
methods are present; this experiment adds only handle-visibility evidence.

## Device and artifact identity

| Field | Value |
|---|---|
| Serial | `G001LT0511550CFT` |
| Fingerprint | `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys` |
| Foreground user | `0` |
| Test APK SHA-256 | `22dd02f58d0f2c0b2a80e1a47bae48b7087e56af2deb79e8bcd77ed3c342b859` |
| Test APK source | `tools/test-launcher-phase6mx/` |

## Evidence

| Evidence ID | File | Observation | Confidence |
|---|---|---|---|
| 6NA-R01 | `adb/phase6mx/PHASE6MX-SERVICE-HANDLE-LOOKUP-20260810-01/probe-logcat.stdout.txt` | UID 10011 and all three service handles are `true`; no transaction output exists | Confirmed |
| 6NA-R02 | `.../before-home_resolve.stdout.txt`, `.../after-rollback-home_resolve.stdout.txt` | HOME remained Fire Launcher with priority 50 | Confirmed |
| 6NA-R03 | `.../before-fire_package.stdout.txt`, `.../after-rollback-fire_package.stdout.txt` | Fire Launcher User 0 state remained installed/enabled and not hidden/suspended/stopped | Confirmed |
| 6NA-R04 | `.../install.stdout.txt`, `.../uninstall.stdout.txt`, `.../after-rollback-test_path.stdout.txt` | Test APK installed, then uninstalled; package path absent after rollback | Confirmed |
| 6NA-R05 | `.../metadata.json`, APK build manifest and SHA manifest | No permissions, no HOME filter, handle-only test design | Confirmed |
| 6NA-R06 | `.../sha256sums.txt` | All captured output hashes verify | Confirmed |

## Interpretation

The result opens a **static-analysis boundary**, not a demonstrated confused
deputy. The next safe question is to map the exact generated Stub/API methods
and permission checks for these services, especially `amazonusermanagerservice`,
without sending a transaction. Any attempt to invoke an unknown transaction or
to use a handle to change Fire Launcher state is outside this probe and must
not be inferred from the handle result.

Classification: **handle visibility confirmed; HOME replacement not shown;
root not shown; no workaround established.**
