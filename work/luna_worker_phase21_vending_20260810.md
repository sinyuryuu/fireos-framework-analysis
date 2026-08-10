# Phase 21B — Vending/DSE host-only closure

Date: 2026-08-10  
Input: P20D-VENDING-002 and its bounded Vending downstream artifacts.  
Scope: static provenance only for `LauncherConfigurationReceiver`, DSE `g()`, manifest exposure, and downstream settings/browser/search sinks.

## Boundary

This audit reads the saved host artifacts and prior findings only. It does not execute or invoke a broadcast, `PendingIntent`, Binder call, secure-setting write, APK installation, sideload, recovery, reboot, or device operation. Capability is not treated as reachability. The receiver and DSE surfaces are not called HOME or root; the evidence below does not establish either property.

## Findings

| ID | Closure result |
|---|---|
| P21B-001 | `LauncherConfigurationReceiver` is manifest-exported and has no manifest permission, but the code requires the `verificationToken` extra and rejects a missing token. The token's creator package is the next identity input; sender UID/provenance is not established by the bounded source. |
| P21B-002 | Receiver acceptance is creator-qualified: the creator must equal the current launcher, or pass the Setup/ApplicationInfo/launcher-qualification branch. The exact external caller and profile/user binding remain unclosed; exported status alone is not reachability to the accepted path. |
| P21B-003 | On acceptance, the receiver only consumes item-list extras and updates in-memory/restore bookkeeping through `aoba`/`aofc`. No direct HOME resolver, component setter, Fire Launcher literal, root transition, or privileged package-state writer was found in the recovered body. |
| P21B-004 | `DseService` is exported with `com.google.android.finsky.permission.DSE`; the saved declaration has no explicit protection level. `mi()` additionally gates on DeviceSetup, and `o()` authorizes `Binder.getCallingUid()` through package resolution and the DeviceSetup authorization configuration. The arbitrary-caller/bypass edge is not proven. |
| P21B-005 | DSE `g()` has JADX duplicated-block warnings and a repeated tail around the empty/non-empty choice branches. Exact reconstructed branch equivalence is unresolved; the observable sinks remain DSE/search selection, metrics, cleanup, and install bookkeeping. No evidence supports treating the duplicate as a privilege bypass. |
| P21B-006 | DSE browser selection reaches `setDefaultBrowserPackageNameAsUser()` using `UserHandle.myUserId()` after package/selection gates. This is a browser-default sink only; caller-to-user/profile provenance is not fully recovered and it is not a HOME sink. |
| P21B-007 | DSE `h()` constructs the Setup Wizard search-selector intent and can carry a supplied first-party `PendingIntent`; `i()` can send that supplied token under the DeviceDefaultAppSelection feature gate. These are downstream capability paths only; no invocation was performed and no untrusted-token reachability was established. |
| P21B-008 | DSE `j()` delegates an eligibility secure-settings write to an injected writer callback. The exact key, provider, target user, and caller provenance are absent from the bounded method, so the sink is identified but not closed as an arbitrary secure-setting write. |
| P21B-009 | `aocc` is a static install-event caller: matching selected browser packages call DSE browser selection, while matching selected search packages can call `uez.a()`. `uez.a()` is gated and writes a `WEB_SEARCH` + `DEFAULT` preferred activity via `replacePreferredActivity`; no HOME action or HOME resolver write is present. |
| P21B-010 | DSE install-facing `mph` methods call `o()` and feature gates before routing to `f()`/`g()` or scheduling work through injected managers. The bounded code does not execute APK installation; exact installer authority, account/user handoff, and completion callback provenance remain missing. |
| P21B-011 | Generic package-state/setter inventory and the recovered receiver/DSE paths contain no `com.amazon.firelauncher` target and no HOME component writer. This is a bounded negative for the requested Vending/DSE closure, not proof that unrelated framework surfaces are safe. |

## Evidence anchors

- `artifacts/phase6ps-vending-receiver-20260810-01/LauncherConfigurationReceiver.java` — SHA-256 `71d17a064272f88d02f4619a2f4fa6fedf0ae91a233c29e0ad6d4110643b6b47`; identical follow-up copy was also checked.
- `artifacts/phase6mb-vending-jadx-20260810-01/base/sources/com/google/android/finsky/setup/dse/impl/DseService.java` — SHA-256 `79c903844c1e80f6f04423de1a3cff6a456490339bebd12f7cef824070dd7beb`.
- `artifacts/phase6mb-vending-jadx-20260810-01/base/sources/defpackage/mph.java` — SHA-256 `93ffc418fb31cb58038f6ecbdefc020e4fb5221f8b80cce141a48b3591be30a1`.
- `artifacts/phase6mb-vending-jadx-20260810-01/base/sources/defpackage/uez.java` — SHA-256 `a60801882f5b1ada40110f32010a697aa2d809484dff1ce9b16fae6aba8d3497`.
- `artifacts/phase6mb-vending-static-20260810-01/manifest-print.txt` — SHA-256 `e332aa77041fd4c4c58c4861471341a8563c7f6c51fc64f54c651fccb27e61c4`.
- Base Vending APK recorded by prior evidence: SHA-256 `a5f456832018bbf571f915e949ea9dcd707ad514c269899e916e9b25d5297a50`.
- Prior input and context: `work/luna_worker_vending_downstream_closure_20260810.md/.csv`, `work/luna_worker_vending_unclosed_surface_20260810.md`, and `work/luna_worker_vending_skipped_methods_followup_20260810.md`.

## Residual closure edges

The remaining open edges are exact external caller provenance, sender UID/profile binding, the decompiler-ambiguous `g()` branch reconstruction, the injected secure-settings writer's key/user/provider, and DSE installer/account handoff. Closing those would require artifacts outside this host-only bounded set; no runtime or device action is authorized for this phase.
