# Phase 6MB — `com.android.vending` permission and package-state writer audit

Date: 2026-08-10
Device: `KFTRWI` / `trona`
Fingerprint: `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`
Scope: read-only device capture plus offline analysis of the current Play Store split APK set.

## Executive result

`com.android.vending` is a new, bounded lead because the live package dump shows it requesting and receiving package-management-related permissions, including `CHANGE_COMPONENT_ENABLED_STATE`, `INSTALL_PACKAGES`, `DELETE_PACKAGES`, `MANAGE_USERS`, and `WRITE_SECURE_SETTINGS`. The package is installed under `/data/app` and does not show the `PRIVATE_FLAG_PRIVILEGED` private flag in the captured dump.

The lead does not presently establish a launcher-control route. In the extracted base APK's bounded static analysis:

- generic `setApplicationEnabledSetting()` and `setComponentEnabledSetting()` call sites exist;
- no literal `com.amazon.firelauncher` was found in the APK string scan or generated JADX source tree;
- no HOME preferred-activity writer, `startHomeActivity`, or explicit Fire Launcher component launch was identified;
- the package-state writers consume internally derived package/component values or verification/policy inputs;
- any call into the framework still reaches the already confirmed PackageManager protected-package gate.

Current verdict: **Strong evidence that Play Store is not the missing Fire Launcher controller; the permission provenance remains an unresolved audit item, not a bypass.** No Vending activity, receiver, service, Binder call, or package-state writer was invoked on the device.

## Evidence

### PHASE6MB-LIVE-01 — read-only device baseline — Confirmed

Source: `adb/phase6mb-vending-20260810-01/`

- `adb_get_state.txt`: device connected.
- `getprop.txt`: PS7331 fingerprint, `KFTRWI`, `trona`, security patch `2024-08-01`.
- `pm_path_vending.txt`: three split APK paths under `/data/app/com.android.vending-InxWV-Nv8Fy8x5lSfSr0mQ==/`.
- `resolve_home.txt`: `priority=50 ... isDefault=true` and `com.amazon.firelauncher/.Launcher`.
- `query_home.txt`: Fire Launcher priority 50; Microsoft Launcher priority 0; Settings FallbackHome priority -1000.
- `dumpsys_activity.txt`: current resumed task is `com.amazon.firelauncher/.Launcher`.

Raw-output SHA-256 values are in `adb/phase6mb-vending-20260810-01/sha256sums.txt`.

### PHASE6MB-LIVE-02 — permission and package metadata — Confirmed

Source: `adb/phase6mb-vending-20260810-01/dumpsys_package_vending.txt`.

The package dump records:

- `userId=10180`;
- `codePath=/data/app/...`;
- `versionCode=84893000`, `versionName=48.9.30-23 [0] [PR] 834517506`;
- flags without a `PRIVILEGED` marker in the captured private flags;
- requested/granted package-management permissions, including `CHANGE_COMPONENT_ENABLED_STATE`, `INSTALL_PACKAGES`, `DELETE_PACKAGES`, `MANAGE_USERS`, `WRITE_SECURE_SETTINGS`, `REBOOT`, and `FORCE_STOP_PACKAGES`.

This is **not** proof that the package can perform those actions against protected targets. It only establishes the package's declared/granted permission metadata. Fire Launcher’s prior PMS protected-package rejection remains the controlling evidence for Fire state mutation.

### PHASE6MB-PERM-01 — permission-source correlation — Strong evidence, version-scoped

The extracted PS7331 permission files were also searched for a direct privileged-permission grant:

- `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/system/etc/permissions/privapp_permissions.xml` — SHA-256 `643cf114ed7d7b82a642fea650ed7d2f53b5dab2291e4f043c272cbe577df732`;
- `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/system/etc/permissions/privapp-permissions-platform.xml` — SHA-256 `0b30c1624ffdab6c5454746737a060157276da5d2bd43addc74cd3919ae4aad1`.

Neither file contains `<privapp-permissions package="com.android.vending">`. The live package still reports grants for `signature|privileged` permissions, while its signature digest (`e3ca78d8`) differs from the framework package’s captured digest (`abe86ff5`). This narrows the provenance question to install-time/package-state history or another grant source; it does not identify a launcher-control capability. The correlation is version-scoped because the extracted permission files and installed Play Store package were not collected from the same immutable package snapshot.

### PHASE6MB-STATIC-01 — manifest and APK provenance — Confirmed

Source: `artifacts/phase6mb-vending-static-20260810-01/`.

The base APK hash is `a5f456832018bbf571f915e949ea9dcd707ad514c269899e916b9b25d5297a50`. The split hashes and manifest-print hash are recorded in `metadata.md` and the artifact directory. `manifest-print.txt` confirms the permissions and several exported components, including `AppRecoveryUpdateService` and package-monitor receivers. Exported status alone does not establish an authorized state-writing interface; component-specific permissions and code paths still have to be proven.

### PHASE6MB-STATIC-02 — enterprise blocked-system-app writer — Strong evidence

Source: `decompiled/.../base/sources/defpackage/uls.java:339-365`.

The decompiled method obtains a collection from an enterprise-policy object, logs “blocked system apps,” reads each package’s enabled state, and calls:

```java
packageManager.setApplicationEnabledSetting(str6, 2, 0);
```

The target is derived from the policy collection (`bhuqVar2`), not a hard-coded Fire component. No HOME intent or resolver operation is present in this method. The decompiler output is partial, so the exact policy producer remains unconfirmed; the call site itself is clear enough to classify as a generic package-state writer.

### PHASE6MB-STATIC-03 — verifier disable-until-used writer — Strong evidence

Source: `decompiled/.../base/sources/com/google/android/finsky/verifier/impl/enforcement/UninstallTask.java:216-238`.

`UninstallTask.g()` calls `setApplicationEnabledSetting(this.j, 3, 0)` after the package name and digest/verification state have been obtained from verification inputs. This is an unsafe-package verifier path, not a HOME path. It has no Fire Launcher literal and no preferred-activity operation.

### PHASE6MB-STATIC-04 — generic restore/component writers — Strong evidence

Sources:

- `defpackage/avyd.java:16-23`: re-enables a package from an internal action object.
- `defpackage/aywk.java:55-70`: restores an internally supplied package to default enabled state.
- `defpackage/nfu.java:367-369`: re-enables a package selected by an internal action object.
- `defpackage/lry.java:8-34`, `defpackage/aasc.java:15-22`: enable/disable components supplied by internal class/component helpers.

These writers are generic and no Fire literal was found in the bounded APK scan. They do not write preferred HOME state. Any target package still encounters the framework gate.

### PHASE6MB-STATIC-05 — Home-key observation is not launcher control — Strong evidence

Sources:

- `defpackage/zic.java:698-703` registers `zib` for `android.intent.action.CLOSE_SYSTEM_DIALOGS` while a Play Store inline-details activity is resumed.
- `defpackage/zib.java:12-17` checks `reason=homekey` and calls `zoi.k()`.
- `defpackage/zol.java:202-210` shows `zoi.k()` records an internal event on the current inline-details object; it does not start an activity or modify preferred state.

This eliminates an apparent “Vending observes Home” false lead within the recovered code path.

### PHASE6MB-STATIC-06 — no Fire literal / HOME writer in bounded scan — Strong evidence, bounded

Source: `artifacts/phase6mb-vending-static-20260810-01/static-search-summary.md`.

The literal search returned zero `com.amazon.firelauncher` matches in the APK strings and generated source. The bounded source search found no preferred-activity writer, `startHomeActivity`, or direct HOME selection writer. JADX exited with code 3 after partial output, so this is not a proof about failed/deobfuscation-resistant regions, native code, or resources.

## Why the granted permission is not a bypass

The existing Fire-specific evidence shows the shell’s Fire Launcher package/component state mutations are rejected by PackageManager before state changes. A caller with a package-state API permission may be able to request ordinary package mutations, but it does not automatically remove the protected-package condition enforced in system_server. Therefore the following inference is not valid:

```text
Vending has CHANGE_COMPONENT_ENABLED_STATE
→ Vending can disable com.amazon.firelauncher
```

The missing proof would be a trusted, Fire-targeted Vending call path plus an observed successful state change. Neither exists in this audit, and deliberately invoking such a path would be an unauthorized state mutation; it was not attempted.

## Exported surface review

The manifest exposes multiple activities, providers, receivers, and `AppRecoveryUpdateService`, as well as package-monitor receivers. The manifest does not by itself show a launcher-selection contract. No exported component was invoked, no crafted broadcast was sent, and no Binder/service transaction was guessed. This is a **risk-rejected experiment**, not evidence that every exported component is harmless or unreachable.

## Classification

| Finding | Classification |
|---|---|
| Vending declares/grants package-state-related permissions in the captured package state | **Confirmed** |
| Vending is installed from `/data/app` without a captured `PRIVATE_FLAG_PRIVILEGED` flag | **Confirmed** |
| Vending contains generic package/component state writers | **Strong evidence** |
| The audited extracted PS7331 privapp XML has no direct `com.android.vending` grant block | **Strong evidence, version-scoped** |
| Vending directly selects or launches Fire Launcher | **Disproved within the bounded APK scan** |
| Vending’s generic writer can bypass the PMS protected-package gate | **Disproved as an inference; no bypass evidence** |
| Vending cannot have any hidden/native/resource path related to HOME | **Unknown** |
| Invoking exported recovery/package-monitor components is safe for this research | **Rejected** |

## Next safe research value

The only remaining value of this lead is provenance analysis: explain why a `/data/app` Play Store package has the captured grants, and whether that metadata is normal for this Fire build. This can be done by comparing the live package’s signing details, permission declaration sources, and PackageManager permission definitions offline. It does not justify calling exported components or trying to mutate Fire Launcher state.
