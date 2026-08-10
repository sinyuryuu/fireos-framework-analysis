# Phase 8C — Read-only host-side SettingsProvider / HOME settings closure

Date: 2026-08-10 (Asia/Taipei)

## Scope and safety

This is a host-only static closure using the Phase 7B IPC residual baseline,
Phase 6 HOME/settings artifacts, exact-build SettingsProvider JADX/resources,
Fire Launcher JADX/manifest, framework Settings/PMS sources, overlays/resource
notes, and permission-holder/caller ledgers. No `settings put`, `content call`
or write operation, Binder transaction, broadcast, APK operation, device
mutation, root, or exploit action was performed.

## Result

The production SettingsProvider writer is the exported `settings` authority
(`singleUser=true`) with standard ContentProvider `call`, `insert`, `update`,
and `delete` entrypoints. Global and secure mutations require
`android.permission.WRITE_SECURE_SETTINGS`; system mutations use the system
write/secure-settings operation gate. The provider propagates
`UserHandle.getCallingUserId()` or an explicit `_user`/requested user and
resolves cross-user access through `ActivityManager.handleIncomingUser`.
`Binder.getCallingUid()` is used for restriction/identity-sensitive checks;
the bounded mutation paths do not clear identity before authorization.

The first mutation sink is `SettingsRegistry`/`SettingsState` persistence. No
SettingsProvider path reaches `PackageManagerService.setHomeActivity`,
`replacePreferredActivity`, a component-state setter, or a package-state
writer. Exact production callers of the generic provider remain unknown even
where permission holders are known; this is an evidence gap, not a bypass.

## HOME/default/preferred key disposition

The recovered Fire Launcher mapping contains `home_auto_cycle` and
`home_cards` in `Settings.Global`, plus launcher personalization keys in
`Settings.Secure`. These are HOME-adjacent card/UI settings, not resolver or
component selection keys. The prior HOME/settings comparison found
`default_home` as a Settings UI/controller key, not a SettingsProvider key;
its picker route calls PackageManager preferred-activity APIs and is separate
from SettingsProvider. PMS persists preferred activity records in its own
per-user XML sections. A preferred record is not equivalent to effective HOME
selection because candidate ranking can still select Fire Launcher.

## Caller / permission / identity closure

Permission-holder inventory confirms many privileged/system packages hold
`WRITE_SECURE_SETTINGS`, including Fire Launcher and Amazon Settings-related
packages, but static holder presence does not prove that a package writes a
HOME resolver key or is the production caller for a particular provider call.
The Phase 7B residual baseline correctly retains the provider production
caller as unknown. The CSV therefore separates:

- `static provider writer`: provider entrypoints and sinks directly shown;
- `caller unknown`: external production caller/permission-holder joins not
  present in the host corpus;
- `bounded negative`: no provider-to-PMS/HOME/component sink in the searched
  artifacts, and distinct PMS preferred-activity handling.

## Evidence anchors

- `decompiled/jadx/settings-provider/sources/com/android/providers/settings/SettingsProvider.java`
  — entrypoints, write gates, calling-user resolution and SettingsRegistry sink.
- `decompiled/jadx/settings-provider/resources/AndroidManifest.xml` —
  exported `settings` authority and `singleUser=true`.
- `decompiled/jadx/firelauncher/sources/com/amazon/alexa/multimodal/settings/mapping/FireOsSettingsStoreMapping.java`
  — exact HOME-adjacent key/URI mapping.
- `output/tables/phase6kv-pms-home-callers.csv` and OTA PMS source — separate
  `setHomeActivity`/preferred-activity writer boundary.
- `work/luna_worker_phase7b_ipc_residual_20260810.md` and
  `work/luna_worker_phase6rs_settings_pm_closure_20260810.md` — prior caller,
  permission, identity, and HOME/settings baselines.

The row-level inventory is
[luna_worker_phase8c_settingsprovider_home_20260810.csv](./luna_worker_phase8c_settingsprovider_home_20260810.csv).

## Remaining missing edges

The unresolved edges are exact-build production caller identity, caller-held
permission provenance at each SettingsProvider call, complete downstream
consumer closure for every mapped key, and any future/vendor code outside the
recovered artifacts. Closing these would require additional offline artifacts;
no runtime write or Binder probing is authorized for this phase.
