# Phase 6AM — LauncherHijackPreventer callback audit

Generated: 2026-08-05T00:58:03.997305+00:00

## Scope and safety

This is a host-only static audit of the PS7331 `fosservices` disassembly and
preserved `fosinit` registrations. It does not contact ADB, call a private
Binder service, replay a broadcast, start an activity, change a permission,
modify package/settings state, stop Fire Launcher, or touch any partition.

## Executive result

### 已證實

1. The preserved `LauncherHijackPreventer` family is registered at four
   SYSTEMSERVER callback boundaries: ActivityStack, ActivityManagerService,
   PackageManager, and PermissionManager. Evidence `6AM-HJ-001`.
2. `canSeeHomeTask(int, Context)` is a visibility boolean. It checks the
   SELinux `amazon_policies:see_home_task` permission and otherwise a platform
   signature; it does not create a `ResolveInfo`, explicit component, or HOME
   intent. Evidence `6AM-HJ-002`.
3. `checkPermission(Context)` returns a permission name for the leanback
   feature branch; it is not a launcher selector. Evidence `6AM-HJ-003`.
4. The PackageManager and PermissionManager callbacks track/revoke
   `android.permission.READ_LOGS` for stored package/user pairs. Evidence
   `6AM-HJ-004`, `6AM-HJ-005`, `6AM-HJ-006`.
5. `PackageWhitelisterCallback` handles updated-system/fdrw package
   bookkeeping and `/data/system/fdrw_apks.conf`; no HOME resolver or
   preferred-activity call appears in the inspected class block. Evidence
   `6AM-HJ-007`.

### 高可信推論

- In the preserved PS7331 class and registration scope, the name
  `LauncherHijackPreventer` does not identify the final HOME selector. The
  inspected implementation is a task-visibility and permission/package
  policy family, while HOME selection remains in the PackageManager result or
  another unpreserved/native path. Evidence `6AM-HJ-008`.
- This removes another plausible direct `com.amazon.firelauncher` injection
  point from the Java/DEX callback inventory; it does not prove that every
  native or out-of-scope path is absent.

### 待驗證

- Runtime callback return values for a real Home-key event were not captured.
- The exact raw resource behind `0x7e05000a` and the current deny-list
  membership are still not shell-readable from the device.
- The preserved artifact scope may not include every runtime-loaded native
  callback or overlay registration.

### 已排除／因風險拒絕

- **已排除於 inspected scope：** direct Fire Launcher literal/component
  construction in the inspected LauncherHijackPreventer and
  PackageWhitelister blocks.
- **因風險拒絕：** unknown Binder transactions, callback fuzzing, manual
  OOBE/OTA replay, permission/package mutation, SELinux changes, root,
  framework injection, and partition operations.

## Control-flow interpretation

```text
HOME / ActivityTaskManager
  → vendor callback fan-in
  → canSeeHomeTask()
      → SELinux/signature visibility decision (boolean)
  → normal resolver path remains responsible for ResolveInfo/component

READ_LOGS policy path
  → blockDevelopmentPermPersist()
  → store package/user pair
  → onShutdown() revokes READ_LOGS

Package update path
  → PackageWhitelisterCallback
  → fdrw metadata / /data/system/fdrw_apks.conf
```

The Mermaid graph and plain-text graph are preserved at
`output/call-graphs/phase6am-launcher-hijack-preventer.*` and in the canonical
artifact.

## Evidence table

| Evidence | Finding | Confidence |
|---|---|---|
| `6AM-HJ-001` | Four LauncherHijackPreventer callback registrations | Confirmed |
| `6AM-HJ-002` | `canSeeHomeTask` is visibility, not selection | Confirmed |
| `6AM-HJ-003` | ActivityManager callback supplies permission name | Confirmed |
| `6AM-HJ-004` | PackageManager callback performs READ_LOGS cleanup | Confirmed |
| `6AM-HJ-005` | Permission callback tracks READ_LOGS policy | Confirmed |
| `6AM-HJ-006` | Package store supports permission cleanup | Confirmed |
| `6AM-HJ-007` | PackageWhitelister is fdrw/update bookkeeping | Strong evidence |
| `6AM-HJ-008` | No direct HOME selector in inspected scope | Strong evidence |

## Reproduction

```sh
python3 tools/scripts/audit_phase6am_hijack_preventer.py --dry-run
python3 tools/scripts/audit_phase6am_hijack_preventer.py   --output artifacts/phase6am/launcher-hijack-preventer-20260805-01
```

The script refuses to overwrite existing output. It emits the extracted
method/class snippets, registration inventory, CSV, graph, summary, input
hashes, and a SHA-256 manifest.

## Decision

This phase closes the misleadingly named LauncherHijackPreventer callback
family as a direct HOME-selection explanation within the preserved PS7331
scope. It provides no new shell workaround and no safe reason to mutate the
device. The next useful static target is the remaining PackageManager
candidate/protected-state source, not another attempt to disable or invoke
the launcher-preventer callbacks.
