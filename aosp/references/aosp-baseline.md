# AOSP Android 9 resolver baseline

## Selected source snapshots

| Tag | Local root | Commit | Security patch | Retrieved/recorded | Status |
|---|---|---|---|---|---|
| `android-9.0.0_r1` | `aosp/android-9/android-9.0.0_r1/platform` | `UNAVAILABLE_IN_LOCAL_SNAPSHOT` | Android 9 launch baseline | 2026-08-03 | usable source snapshot |
| `android-9.0.0_r61` | `aosp/android-9/android-9.0.0_r61/platform` | `UNAVAILABLE_IN_LOCAL_SNAPSHOT` | Android 9 maintenance baseline | 2026-08-03 | usable source snapshot |

The local directories are inside the project repository and do not preserve a
separate AOSP Git object database. The tag names above are the source of truth;
no project commit hash is presented as an AOSP commit.

## Hashes of comparison inputs

| File | SHA-256 |
|---|---|
| r1 `PackageManagerService.java` | `c36adc88a410335e980214fdc11bf4919675546e8691d0784f2e59ae4f33886b` |
| r61 `PackageManagerService.java` | `bb8d33fbb976c3463d932f65a679dafb2d541845b2989b63d07060d0db8ef179` |
| r1 `ProtectedPackages.java` | `fb64ec70c224f527890a28385eb163129a4f235fb8818cd42d31c69ec7cf4508` |
| r61 `ProtectedPackages.java` | `fb64ec70c224f527890a28385eb163129a4f235fb8818cd42d31c69ec7cf4508` |

## Resolver methods used

The primary comparison is limited to:

- `PackageManagerService.resolveIntent`
- `PackageManagerService.resolveIntentInternal`
- `PackageManagerService.chooseBestActivity`
- `PackageManagerService.findPersistentPreferredActivityLP`
- `PackageManagerService.findPreferredActivity`
- `PackageManagerService.queryIntentActivitiesInternal`
- PackageManager resolver `sortResults` implementations present in the local snapshot

The local source tree does not contain a standalone `IntentResolver.java` or
`PreferredIntentResolver.java` source file at the expected Android 9 paths.
Those entries are recorded as `NOT_FOUND`, not reconstructed from memory.
