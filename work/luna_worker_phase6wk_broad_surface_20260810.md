# Phase 6WK — broad privileged-surface ledger

Date: 2026-08-10. Host-only static search; no device contact, Binder/service invocation, mutation, exploit, root, reboot, OTA execution, or partition write.

## Result

The companion CSV has **17 validated rows** (`WK-001` through `WK-017`), with 15 columns and unique IDs. It records additional high-impact sinks not represented in the Phase 6VE/6VF framework sink inventory: default runtime-permission grants; user/profile creation and removal; user switching/start/stop paths; package hiding and restricted-profile package deletion; the exported SettingsProvider write surface; a media-button secure-setting write; and system-server user-state persistence.

All rows are static evidence only. Reachability is not claimed. Caller identity, exact Binder transaction, service-manager publication details, SELinux decisions, package signatures, and runtime policy are marked `UNKNOWN` where the corpus does not establish them.

## Search scope and corpus identity

Primary exact-build inputs searched:

- `artifacts/framework/`: framework JAR/APK and boot VDEX files.
- `artifacts/services/`: services/fosservices JAR, ODEX, and VDEX files.
- `artifacts/amazon-services/`: Amazon `fosinit` policy/config XML and parental-controls APK.
- `decompiled/baksmali/vdexExtractor/`: boot framework, boot fosframework, services, and fosservices disassembly logs.
- `decompiled/jadx/`: exact-build system-server, Settings, SettingsProvider, SystemUI, Amazon Settings, and Amazon parental-controls sources/resources.

Representative corpus hashes (SHA-256):

```text
artifacts/framework/framework.jar                         1c16f5976318fadcf7add92c518a93896f99e2a78f742b7347d8539103264882
artifacts/framework/fosframework.jar                      fd57eea7793993361b3811651a905ea6be34f5c7a72b1fcea81cf798d0e3f481
artifacts/services/services.vdex                           06cb78333df89d97da741b921d7c62680b4a931aade45b83581b39d498cdbdc4
artifacts/services/fosservices.vdex                        584673e398894936dcba7a79c07d1f5abda7f2d03b3e36bd1792f764dd4dcffa
decompiled/baksmali/vdexExtractor/services/disassembly.log 373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53
decompiled/baksmali/vdexExtractor/fosservices/disassembly.log ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c
```

The exact source-file hashes used for each row are in `evidence_sha256` in the CSV. The output CSV hash is `413bf7a4e9150ea0046fef4d44d8f306b595610a4e8593d3078952f5de762d57`.

## Evidence ledger highlights

- `WK-001`: `DefaultPermissionGrantPolicy.java:106-121` calls the runtime grant path for requested runtime permissions under a system-server default-permission policy.
- `WK-002`/`WK-003`/`WK-004`: `UserManagerService.java:1957-1975,2112-2115` exposes create-user, create-profile, and remove-user sinks. The same file at `1309-1348` shows MANAGE_USERS/CREATE_USERS and system/root checks.
- `WK-005`: `UserController.java:255-270` checks both `INTERACT_ACROSS_USERS_FULL` and `amazon.aosp.permission.INTERACT_ACROSS_USERS_FULL`, rejects system-user stop, and applies the shell restriction.
- `WK-006`/`WK-007`/`WK-008`: `ActivityManagerShellCommand.java:1611-1634,1686-1704` parses target users and calls switch/start/stop interfaces. The downstream authorization remains separate and is not inferred.
- `WK-009`/`WK-010`: `AppRestrictionsHelper.java:105-119` invokes `setApplicationHiddenSettingAsUser` and, for restricted profiles, `deletePackageAsUser` with an explicit user ID.
- `WK-014`/`WK-015`: `SettingsProvider.java:344-418,658-910` implements insert/update/delete settings operations and permission checks; its manifest declares an exported `settings` authority (`AndroidManifest.xml:16-31`) with `sharedUserId=android.uid.system`.
- `WK-017`: `UserManagerService.java:1585-1591,1668-1701` writes user state and the user list using atomic file writers; paths and runtime policy are not recovered in this ledger.

## Cross-reference and exclusions

The Phase 6VE framework inventory (`work/luna_worker_phase6ve_framework_sink_inventory_20260810.csv`, SHA-256 `42d609d5d427fb691031e54caf9d25ee62718f9be64f7bf32fbc53d7eb88ab6a`) already represented enabled-state/PMS sinks, HOME/preferred activity sinks, Amazon user setup/sorted-list writers, and OTA block-image/partition sinks. Those were excluded from this ledger except where a new caller or sink family was necessary to show the broader surface.

Searches also covered trust/certificate/keystore terms, init/policy loading terms, exported component declarations, and native/file-write patterns. No additional exact-build trust/certificate update sink or native privileged file-write sink was promoted beyond the already represented OTA rows. Keyword hits alone were not treated as sinks; no reachability was inferred from a manifest export, shell parser, helper call, or static file writer.

## Validation

```text
CSV parser rows: 17
CSV columns per row: 15
Unique IDs: 17
Validated ID range: WK-001..WK-017
Device/runtime actions: none
```
