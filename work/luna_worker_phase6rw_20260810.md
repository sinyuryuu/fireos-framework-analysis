# Phase 6RW — host-only SystemUI/overlay/resource writer closure

Date: 2026-08-10. Scope is the saved PS7331 7.3.3.1 corpus plus existing Phase
3B/3C/6O/6RS evidence. This is a host-only static ledger: no adb, Binder,
service call, broadcast, settings/package/overlay mutation, user switch,
root/exploit/driver/OTA/recovery/reboot, or partition write was performed.

## Result

The exact PS7331 SystemUI resource arrays bootstrap listed Amazon services but
do not select Fire HOME: `amz_config_systemUIServiceComponents` is a service
list and `config_systemUIServiceComponentsPerUser` is empty. The inspected
SystemUI/AMS callbacks either resolve through PackageManager, gate visibility,
emit activity/profile events, or start a profile picker; no saved callback body
constructs `com.amazon.firelauncher/.Launcher` or calls a preferred-HOME,
package-state, or component-state writer.

The real HOME writer is the Settings `DefaultHomePicker` → PMS
`replacePreferredActivity` route, but the dashboard XML omits the HOME row and
Phase 3C/6DI show that a stored third-party preferred record remains below
Fire's manifest priority 50. PMS still has confirmed package/component state
writers, including the child/profile KFT path, but that path is user-scoped and
not a broad User-0 HOME route. OOBE component/settings writers are protected
OTA lifecycle writers and not Fire Launcher writers. Native/image overlay
provenance is negative for HOME/resource control within the reviewed PS7331
system/vendor set.

## Classification summary

| Class | Closure |
|---|---|
| Confirmed | SystemUI service-array semantics; empty per-user array; resolver/visibility callback sinks; Settings HOME controller/resource gate; PMS preferred persistence and resolver ranking; overlay inventory; child KFT package-state writer; protected OOBE writers. |
| High-confidence | No SystemUI callback-to-Fire explicit launch edge in the bounded corpus; no enabled product/vendor/system_ext HOME overlay; preferred state is not the decisive Fire selection layer. |
| Pending | Complete exact-build callback/class-loader universe; exact user propagation and ordinary caller provenance for protected lifecycle writers; complete consumer closure for profile metadata. |
| Excluded | Fire deny-list resource, cutout/dark-theme overlays, generic window/trace callbacks, Vending generic package helpers, native shared-storage/HIDL surfaces, OTA/recovery write capability. |

## Ledger

The companion CSV is the machine-readable form of the same rows. Offsets are
source line ranges or VDEX disassembly virtual offsets/line anchors as
preserved in the corpus; they are not runtime claims.

| ID | Surface / control flow | Caller → gate → identity/user → sink | Evidence (file:method:offset) | Classification | Disposition |
|---|---|---|---|---|---|
| 6RW-001 | SystemUI service resource bootstrap | `SystemUIApplication` reads service component array using SystemUI system context → constructs listed service instances/lifecycle | `decompiled/jadx/ota-PS7331/systemui/resources/res/values/arrays.xml:3-37`; prior RT `6RT-001` | confirmed | Service registration only; no HOME/package writer. |
| 6RW-002 | SystemUI per-user resource branch | Per-user loader reads `config_systemUIServiceComponentsPerUser` → array is empty → no per-user service/component sink | `.../systemui/resources/res/values/arrays.xml:344-349`; prior RT `6RT-002` | confirmed | No per-user Fire/HOME edge in exact resource. |
| 6RW-003 | AppCompat HOME pre-resolution callback | `ActivityStackSupervisor.resolveIntent` dispatches vendor callback → AppCompat asks PM for `ResolveInfo` and filters uninstalled result → PM resolver remains sink | `decompiled/baksmali/vdexExtractor/services/disassembly.log:796418-796497`; `.../fosservices/disassembly.log:41093-41147`; findings `phase-6al-home-resolve-callbacks.md` | high-confidence | Callback can preempt only with PM result; no Fire component construction found. |
| 6RW-004 | Eve HOME callback | Same dispatcher → Eve callback returns null/base result in saved slice → framework calls `PackageManagerInternal.resolveIntent` | `services/disassembly.log:796418-796497`; `fosservices/disassembly.log:41093-41147`; prior RT `6RT-009` | confirmed | Falls through; not a HOME writer. |
| 6RW-005 | LauncherHijackPreventer | Activity/stack callback receives caller uid/pid → Leanback/SELinux `see_home_task` or signature gate → returns visibility/permission boolean | `fosservices/disassembly.log:136857-137040`; `artifacts/amazon-services/launcherhijackpreventer_fosinit.xml:9-16` | confirmed | HOME-task visibility gate only; no preferred/package mutation. |
| 6RW-006 | Amazon activity/profile callbacks | AMS lifecycle supplies resumed `ComponentName`/user → in-process policy/observer checks → notification or conditional profile-picker start | `fosservices/disassembly.log:180180-180210`; `artifacts/amazon-services/amazonactivitymanager_fosinit.xml:12-22`; prior RT `6RT-011/012` | confirmed | Activity/profile event route; no PMS HOME/package writer shown. |
| 6RW-007 | Profile metadata writer | Package lifecycle event → `readMetaDataFromAppInfo` / service handler → metadata package/activity pair → `mLaunchDataInfoMap`/`launch_info_map_key` persistence | `findings/phase-6er-amazon-profile-metadata-tx41-boundary.md:39-58,112-146`; prior RT `6RT-014` | confirmed | Metadata sink confirmed; consumer and provider authenticity remain incomplete. |
| 6RW-008 | OOBE component writer | Protected `BOOT_AFTER_SYSTEM_OTA` → `BootAfterSystemOTAReceiver.onReceive` action/OOBE/retail gates → receiver context PackageManager → enables `OobeHomeActivity` | `BootAfterSystemOTAReceiver.java:27-61`; `PackageHelper.java:11-22`; `work/luna_worker_ps7331_residual_writer_inventory_20260810.csv:RWI-02` | confirmed | Lifecycle-only OOBE writer, not Fire Launcher/HOME. No replay. |
| 6RW-009 | OOBE settings writer | Same protected OTA/OOBE branch → receiver `ContentResolver` user inherited from context → `user_setup_complete=0`, `isOOBEActive=1` | `OOBEActivationHelper.java:53-56`; `SettingsDBUtils.java:51-64`; prior RWI-03 | confirmed | Settings sink confirmed; exact numeric user unresolved; no HOME sink. |
| 6RW-010 | Settings HOME availability/resource gate | `DefaultAppSettings.buildPreferenceControllers` constructs `DefaultHomePreferenceController` → `isAvailable` reads `config_show_default_home=true` and key `default_home` → controller reports PM default | `decompiled/jadx/ota-PS7331/settings/sources/com/android/settings/applications/DefaultAppSettings.java`; `.../defaultapps/DefaultHomePreferenceController.java`; `.../settings/resources/res/values/bools.xml`; prior 6PZ follow-up | confirmed | Resource/controller only; dashboard XML has no HOME row. |
| 6RW-011 | Settings HOME picker writer | Internal `DefaultHomePicker.setDefaultKey` flattens selected `ComponentName` → `replacePreferredActivity` with HOME filter → starts implicit HOME intent | `decompiled/jadx/ota-PS7331/settings/sources/com/android/settings/applications/defaultapps/DefaultHomePicker.java`; `.../settings/resources/res/xml/default_home_settings.xml`; prior 6PZ follow-up | confirmed | Formal stored-preference writer, but route is not exposed in saved dashboard and must not be invoked. |
| 6RW-012 | PMS preferred persistence | PMS preferred setter → `PreferredIntentResolver`/`Settings` → per-user `preferred-activities` and `persistent-preferred-activities` XML | `decompiled/jadx/ota-PS7331/systemui/sources/com/android/server/pm/Settings.java`; `services/disassembly.log:515118-515124,518609-518664` | confirmed | Stored resolver state, not a Settings-provider key or overlay. |
| 6RW-013 | PMS HOME selection comparator | `resolveIntentInternal` → `chooseBestActivity` → compares candidate priority before ordinary preferred tie path → Fire manifest candidate wins priority 50 over third-party priority 0 | `services/disassembly.log:951258-951309`; `decompiled/jadx/ota-PS7331/firelauncher/resources/AndroidManifest.xml`; Phase 3B `P3B-STATIC-PMS-001`, Phase 3C `P3C-PREF-001` | confirmed | Explains stored-but-ineffective preferred state; no SystemUI override inferred. |
| 6RW-014 | PMS package/component-state writers | AmazonUserManagerService KFT child lifecycle → supplied `UserInfo.id` → `setComponentEnabledSetting` / `setApplicationEnabledSetting` for Tahoe/Fire/Launcher3 components | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54310-54324`; table `output/tables/phase6mh-package-state-writers.csv` | confirmed | Real writer, child/profile-scoped; target and caller path are not broad User-0 HOME control. |
| 6RW-015 | Amazon PM metadata/flags writer surface | Private `IAmazonPackageManager` tx1/2/4/5 → permission `amazon.permission.ADD_RM_PKG_METADATA` → AmazonApplicationFlags sink | `fosservices/disassembly.log:402917-403398,95866-96037`; `output/tables/phase6rs-ru-privilege-surface.csv:SRS-06/SRS-07` | pending | Static sink confirmed, production caller/token and PMS/HOME consumer not found. Do not transact. |
| 6RW-016 | Resource deny-list | `amazon.fireos` `package_manager_deny_list` raw resource → package-management policy consumer → deny-list behavior | `output/tables/phase6ap-denylist-resource.csv`; `artifacts/phase6ap/denylist-resource-closure-20260805-01` | excluded | Resource is real but not a SystemUI/HOME/navigation/user/settings writer. |
| 6RW-017 | Product/vendor/system_ext overlay inventory | Image overlay trees → overlay manager resource selection; saved runtime list shows only cutout and dark-theme entries, disabled | `findings/phase-6je-native-overlay-provenance-closure.md:65-76,233-240`; `adb/phase3c/PHASE3C-BASELINE-20260803-02/overlay/list.stdout.txt`; `findings/phase-3c-overlay-analysis.md:1-12` | high-confidence | No relevant enabled HOME/framework-res/SystemUI overlay; unlisted-build provenance remains bounded. |
| 6RW-018 | Native overlay/framework closure | Selected PS7331 system/vendor native libraries and overlay trees → symbol/literal scan and provenance join → no HOME/package-state/resource writer edge | `output/tables/phase6je-native-overlay.csv`; `findings/phase-6je-native-overlay-provenance-closure.md:65-75` | high-confidence | Negative within enumerated exact image set; no native write route established. |
| 6RW-019 | Generic window/trace callbacks | WMS/PhoneWindowManager/ViewRoot callbacks → window permission/type checks → flags, visibility, trace, PIP or scheduling sink | `fosservices/disassembly.log:196540-196700,203322-203390`; prior RT `6RT-004/005/006/007` | excluded | Not package/component/HOME/navigation-state writer in saved slices. |
| 6RW-020 | Corpus completeness boundary | `fosinit` loader → 123 saved registrations → callback class set/dispatch; exact loader inputs not fully recovered | `artifacts/phase6jd-fosinit-20260808-01`; `services/disassembly.log:222435-222489`; prior RWI-05 | pending | Host-only recover/diff loader and complete class universe if new artifacts appear. |

## Evidence hashes

Hashes below are SHA-256 of the current host files used for this closure:

| Input | SHA-256 |
|---|---|
| PS7331 SystemUI `arrays.xml` | `c59d8f5e41cdab1b1c040835ba4580f4c549de7e66375a6b73bd06363b8a6e7e` |
| PS7331 `PackageManagerService.java` | `47cda8ecce8ad5ac0343dec5a202aded878a838fd7d6a8659ff38b3439ac738b` |
| PS7331 `Settings.java` | `738a3f8d07cb4de3a09badfe447f602e4e14a2e223af83f7abfa42d2c4b14e28` |
| PS7331 `DefaultHomePicker.java` | `56e7319492ee910d53c89f1d9c09eb18bdc7cc304106c403ee2e1049ebe2b9a7` |
| PS7331 Settings `DefaultHomePreferenceController.java` | `39f282503e5c27322ac1e000c1edafa9a514ba036757ac45e40a619f030749c4` |
| PS7331 Settings `bools.xml` | `e17d1f54abc2bf55d8a50c75821f96f9a4122d03e014de8c15f054e0d9a758db` |
| PS7331 Fire Launcher manifest | `4a7fbfd42cbce6f37a90147751afe7adb18d99de43efe10e0938f48694b1936f` |
| PS7331 FOS services disassembly | `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` |
| PS7331 framework services disassembly | `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53` |
| Phase 3C overlay list | `c28af7d0130e3ff02806dcb953a6299955d44c1887d42f22f26d43f96296ae1d` |

Output hashes are reported after final write in the handoff message. The CSV
contains the same evidence paths, offsets, classifications, and input hashes.
