# Phase 6AL — HOME pre-resolution callback closure

Generated: 2026-08-05T00:44:55.909408+00:00

## Scope and safety

This is a host-only, static control-flow audit of the PS7331 Android 9
`VendorActivityStackSupervisorCallback` path.  It reads the saved
`services`/`fosservices` disassembly, preserved Amazon `fosinit` registrations,
and the saved HOME resolver snapshot.  It does not call private services,
send Binder transactions, replay broadcasts, start activities, change package
or settings state, or contact the device.

## Executive result

### 已證實

1. `ActivityStackSupervisor.resolveIntent()` calls
   `VendorActivityStackSupervisorCallback.callResolveIntent()` first.  A
   non-null callback result is returned immediately; otherwise the method
   calls `PackageManagerInternal.resolveIntent()`.  Evidence: `6AL-CB-001`,
   `6AL-CB-002`.
2. The preserved `fosinit` scope contains exactly two registrations for this
   callback base: `AppCompatActivityStackSupervisorCallback` and
   `EveActivityStackSupervisorCallback`.  Evidence: `6AL-CB-006`.
3. AppCompat calls `IPackageManager.resolveIntent()` and filters an
   uninstalled result; its exact method block contains no
   `com.amazon.firelauncher` literal and no explicit component construction.
   Evidence: `6AL-CB-003`.
4. Eve does not override `resolveIntent()` in the preserved class block; it
   records lifecycle data through `callOnRestartActivity`, while the base
   implementation returns null.  Evidence: `6AL-CB-004`, `6AL-CB-005`.

### 高可信推論

- The inspected callback set is AOSP-shaped at the selection boundary: a
  callback may return a PM-produced `ResolveInfo`, but no inspected callback
  injects Fire as an explicit component.
- The live Fire result therefore remains best explained by the PM candidate /
  preferred state (privileged Fire candidate with effective priority 50) or by
  a callback/native path outside the preserved registration and method scope.

### 待驗證

- Whether an additional registration is loaded from an artifact outside the
  preserved `artifacts/amazon-services/*.xml` scope.
- Whether AppCompat's added match flags alter a particular HOME candidate set
  in an unobserved edge case; its method still delegates to PM rather than
  selecting a package directly.
- Runtime callback return values for a real Home-key event.  No instrumentation
  or private callback invocation was used; the saved end result is only the
  final resolver observation.

### 已排除／因風險拒絕

- **已排除於 inspected scope：** a direct literal `com.amazon.firelauncher`
  injection in the callback dispatcher, ActivityStackSupervisor method,
  AppCompat resolver method, or Eve callback class.
- **因風險拒絕：** unknown Binder calls, manual callback invocation,
  OOBE/OTA replay, package-state mutation, framework injection, root, or
  SELinux changes.

## Exact control flow

```text
Home key / ActivityStarter
  → ActivityStackSupervisor.resolveIntent
  → VendorActivityStackSupervisorCallback.callResolveIntent
  → AppCompat.resolveIntent
      → IPackageManager.resolveIntent
      → uninstalled-result filter
      → ResolveInfo or null
  → Eve.resolveIntent (inherited base null)
  → PackageManagerInternal.resolveIntent fallback
  → Activity start
```

The dispatcher is first-non-null, not first-callback-wins.  Because AppCompat
delegates to the PackageManager, a returned Fire result at that point would be
the PM's result, not proof that AppCompat selected Fire.

## Evidence table

| Evidence ID | Surface | Control flow | HOME effect | Confidence |
|---|---|---|---|---|
| `6AL-CB-001` | `framework_dispatcher` | iterate callback array; return the first non-null ResolveInfo; otherwise return null | OEM callbacks can preempt the normal ActivityStackSupervisor fallback only by returning a ResolveInfo | **Confirmed** |
| `6AL-CB-002` | `framework_fallback` | call callback dispatcher; return callback result when non-null; otherwise call PackageManagerInternal.resolveIntent | Home-key ActivityTaskManager path has a pre-PM hook, then AOSP-shaped PM fallback | **Confirmed** |
| `6AL-CB-003` | `registered_callback` | calls IPackageManager.resolveIntent with added match flags; filters only an uninstalled ResolveInfo; returns the PM result or null on error | Can preempt the later fallback with a PM-produced ResolveInfo; no component/package replacement is visible | **Strong evidence** |
| `6AL-CB-004` | `registered_callback` | overrides lifecycle telemetry callOnRestartActivity; inherits base resolveIntent returning null | does not supply a ResolveInfo to the dispatcher in the inspected class | **Confirmed** |
| `6AL-CB-005` | `base_callback` | returns null | unimplemented callbacks fall through to PackageManagerInternal | **Confirmed** |
| `6AL-CB-006` | `registration` | two concrete registrations for VendorActivityStackSupervisorCallback were found in the preserved Amazon registration scope | defines the callback set used by findCallbacks() | **Strong evidence** |
| `6AL-CB-007` | `callback_scope` | AppCompat delegates to PM; Eve/base return null; fallback delegates to PM | no inspected callback creates an explicit Fire Launcher component or bypasses PM ranking | **Strong evidence** |

## Reproduction

```sh
python3 tools/scripts/audit_phase6al_home_resolve_callbacks.py --dry-run
python3 tools/scripts/audit_phase6al_home_resolve_callbacks.py \
  --output artifacts/phase6al/home-resolve-callback-20260805-01
```

The script is host-only and refuses to overwrite existing output.  It writes
method snippets, registration inventory, input hashes, CSV, Mermaid graph and
SHA-256 manifest.

## Decision

Phase 6AL closes the preserved Java/DEX callback set without finding a direct
Fire Launcher selector.  The remaining high-value question is not whether the
callback hook exists—it does—but whether the PM result it receives is altered
by candidate filtering, preferred-state validation, or an unpreserved native /
registration source.  No new ADB workaround or root path was established.
