# Phase 6PZ Settings/Home resource follow-up — PS7331 static exact-build comparison

Date: 2026-08-10  
Scope: host-only static comparison of saved PS7331 Settings JADX/resources, OTA-PS7331 JADX Settings, PMS/framework source, saved overlay inventory, and existing Phase 3C/6DI/6FO findings. No device access, UI click, Binder dispatch, tx66, Settings/overlay modification, or artifact overwrite was performed.

## Result

No previously unrecorded HOME-selection Settings key, resource boolean, Activity/fragment/intent route, or shell-readable HOME state was found that changes the Phase 6PZ conclusion.

The exact-build Settings surface has two relevant identifiers:

- `default_home`: the programmatic preference/controller key and App Info shortcut key.
- `config_show_default_home=true`: the Settings resource gate used by `DefaultHomePreferenceController.isAvailable()`.

The dashboard XML (`app_default_settings.xml`) contains no `default_home` item, while `DefaultAppSettings.buildPreferenceControllers()` still constructs the controller. `default_home_settings.xml` is a dormant picker screen used by `DefaultHomePicker`; reaching its `setDefaultKey()` would call `replacePreferredActivity()` and start an implicit HOME intent, but the existing Phase 6FO/6DI route boundary records that the normal exported dashboard does not expose it.

The only additional shell-readable state identified statically is the public PMS command surface: `resolve-activity` reads the effective HOME resolver result, while `dumpsys package preferred-activities` exposes the stored preferred record through the existing runtime evidence. `set-home-activity` is a writer, not a new read key; Phase 6DI already demonstrated that its preferred Microsoft record can persist while Fire's priority-50 HOME still wins over a third-party priority-0 candidate.

PMS source also makes the persistence topology explicit: per-user `preferred-activities` and `persistent-preferred-activities` XML sections are read/written by `com.android.server.pm.Settings`. This is stored resolver state, not a Settings-provider key and not an overlay boolean. The saved Phase 3C enabled-overlay list contains only internal cutout overlays and `com.android.systemui.theme.dark`; no mutable Settings/framework HOME overlay was present.

## Comparison and disposition

The CSV contains 14 rows. Rows marked `newly-recorded-*` are static evidence organization additions (OTA source equivalence, PMS persistence sink, and Fire ranking comparator), not newly discovered runtime writers. Rows marked `confirmed-*` are retained negative or already-recorded boundaries from Phase 3C, 6DI, and 6FO.

| Question | Static answer | Runtime/evidence status |
|---|---|---|
| Unrecorded HOME key? | No; `default_home` is the only Settings preference-shaped HOME key found. | Existing Phase 6FO/6DI boundary retained. |
| Unrecorded boolean? | No; `config_show_default_home=true` is the relevant gate. | Controller enabled in resources, but dashboard row omitted. |
| Unrecorded Activity/fragment/intent? | No new route; `HOME_SETTINGS` reaches `DefaultAppSettings`; `DefaultHomePicker` is dormant/internal. | Phase 6FO observed no Home selector. |
| Unrecorded shell-readable state? | No new provider key; PMS exposes effective resolution and preferred-activity persistence. | Phase 6DI already captured resolver/preferred divergence. |
| Overlay effect? | No relevant enabled overlay in saved Phase 3C inventory. | No overlay change authorized or performed. |

## Safe disposition

Phase 6PZ Settings gap is closed as a minimal-safe static gap. The next safe step, only if a new exact-build artifact is supplied, is another host-only hash/diff of Settings resources, framework-res resource tables, and overlay inventory. Do not click the picker, dispatch `tx66`, invoke private Binder transactions, switch overlays, or touch the device for this gap.

## Inputs and evidence anchors

- `decompiled/jadx/settings/` and `decompiled/jadx/ota-PS7331/settings/`
- `decompiled/jadx/ota-PS7331/systemui/sources/com/android/server/pm/Settings.java`
- `decompiled/jadx/ota-PS7331/systemui/sources/com/android/server/pm/PackageManagerService.java`
- `decompiled/jadx/ota-PS7331/systemui/sources/com/android/server/pm/PackageManagerShellCommand.java`
- `decompiled/jadx/ota-PS7331/firelauncher/resources/AndroidManifest.xml`
- `adb/phase3c/PHASE3C-BASELINE-20260803-02/overlay/list.stdout.txt`
- `findings/phase-3c-settings-key-analysis.md`
- `findings/phase-3c-overlay-analysis.md`
- `findings/phase-6di-home-priority-override.md`
- `findings/phase-6fo-gui-default-apps-home-boundary.md`
- `findings/phase-6fw-framework-home-provenance-closure.md`
