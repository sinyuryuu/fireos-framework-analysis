# Phase 6MU — AmazonApplicationFlags persistence and consumer closure

Date: 2026-08-10
Schema: `phase6mu-amazon-application-flags-v1`

## Scope and safety

Host-only analysis of the preserved PS7331 `fosservices/disassembly.log`. No
ADB, Binder/service call, private transaction, ioctl, input injection,
settings/package mutation, reboot, OTA/recovery, exploit, Root attempt, or
partition write was performed.

## Executive result

**已證實：** all four `IAmazonPackageManager` mutators are guarded by
`amazon.permission.ADD_RM_PKG_METADATA`, carry explicit package/list/user
arguments, update `AmazonApplicationFlags`, and call `writeToFile()` in the
bounded static path. The persistent file is
`/data/system/amazon_package_flags.xml`.

**已證實：** the file format uses package/user/flag/metadata records and is
loaded by `AmazonApplicationFlags.init()` → `readFromFile()`. The in-memory
structure is a user-indexed `SparseArray` containing per-package flags and
metadata.

**已證實（bounded consumers）：** the corpus shows flag reads in three
non-mutator consumers: package-recency broadcast filtering, game-mode
classification (bit `2`), and `AppCompatActivityManagerServiceCallback` package
compatibility classification (bit `1`). The package-service getter is a read
wrapper. No direct HOME resolver, preferred-activity, enabled-state writer, or
`com.amazon.firelauncher` token appears in the `AmazonApplicationFlags` class
or these first consumer methods.

**高可信推論（bounded）：** the four mutators are a persistent Amazon
package-metadata/flags database, not the control point that makes Fire Launcher
win HOME. A later consumer outside the indexed call sites remains possible but
is not evidenced in this disassembly corpus.

**待驗證：** whether any flag value is consumed indirectly through framework
objects or native code not represented by the preserved Java disassembly.

**因風險拒絕測試：** no attempt was made to call `amazonpackagemanager`, write
`/data/system/amazon_package_flags.xml`, alter flags, or replay a transaction.

## Mutator map

| Method | Range | Permission | Sink | Persistence | Classification |
|---|---|---|---|---|---|
| `removeAmazonFlagsForUser` | `95955-95972` | `checkCallingOrSelfPermission(amazon.permission.ADD_RM_PKG_METADATA)` | `removeAmazonFlagsForUser / none observed` | `not in BinderService wrapper; inner static method handles persistence` | Confirmed static permission→AmazonApplicationFlags→writeToFile path |
| `removeAmazonMetadataForUser` | `95973-95990` | `checkCallingOrSelfPermission(amazon.permission.ADD_RM_PKG_METADATA)` | `none observed / removeAmazonMetadataForUser` | `not in BinderService wrapper; inner static method handles persistence` | Confirmed static permission→AmazonApplicationFlags→writeToFile path |
| `setAmazonFlagsForUser` | `95991-96008` | `checkCallingOrSelfPermission(amazon.permission.ADD_RM_PKG_METADATA)` | `setAmazonFlagsForUser / none observed` | `not in BinderService wrapper; inner static method handles persistence` | Confirmed static permission→AmazonApplicationFlags→writeToFile path |
| `setAmazonMetadataForUser` | `96009-96026` | `checkCallingOrSelfPermission(amazon.permission.ADD_RM_PKG_METADATA)` | `none observed / setAmazonMetadataForUser` | `not in BinderService wrapper; inner static method handles persistence` | Confirmed static permission→AmazonApplicationFlags→writeToFile path |

## First persistence boundary

`AmazonApplicationFlags.writeToFile()` computes a checkpoint, serializes the
user/package flag map, and writes the XML file. `readFromFile()` parses the
same schema (`amazonflagstag`, `schemaversion`, `package`, `userid`,
`packagename`, `amazonflagsattr`, `metadata`). The bounded class contains these
package/HOME relevance tokens: `writeToFile, readFromFile, /data/system/amazon_package_flags.xml`.

## First consumer map

| Class / method | Read | Effect | HOME relevance | Confidence |
|---|---|---|---|---|
| `PackageRecencyCallback.sendBroadcastWithDelay` | `getAmazonFlagsForUser` | package-recency broadcast filter consumer, no HOME selector | no direct HOME writer in method | Confirmed static / bounded |
| `AmazonApplicationFlags.init` | `readFromFile` | internal flags/metadata helper | no direct HOME writer in method | Confirmed static / bounded |
| `AmazonApplicationFlags.readFromFile` | `readFromFile` | internal flags/metadata helper | no direct HOME writer in method | Confirmed static / bounded |
| `AmazonApplicationFlags.readFromFile` | `setApplicationInfoForUserLocked` | internal flags/metadata helper | no direct HOME writer in method | Confirmed static / bounded |
| `AmazonApplicationFlags.readFromFile` | `setAmazonMetadataForUserLocked` | internal flags/metadata helper | no direct HOME writer in method | Confirmed static / bounded |
| `AmazonApplicationFlags.removeAmazonFlagsForUser` | `removeApplicationInfoForUserLocked` | internal flags/metadata helper | no direct HOME writer in method | Confirmed static / bounded |
| `AmazonApplicationFlags.removeAmazonFlagsForUser` | `writeToFile` | internal flags/metadata helper | no direct HOME writer in method | Confirmed static / bounded |
| `AmazonApplicationFlags.removeAmazonMetadataForUser` | `removeAmazonMetadataForUserLocked` | internal flags/metadata helper | no direct HOME writer in method | Confirmed static / bounded |
| `AmazonApplicationFlags.removeAmazonMetadataForUser` | `writeToFile` | internal flags/metadata helper | no direct HOME writer in method | Confirmed static / bounded |
| `AmazonApplicationFlags.setAmazonFlagsForUser` | `setApplicationInfoForUserLocked` | internal flags/metadata helper | no direct HOME writer in method | Confirmed static / bounded |
| `AmazonApplicationFlags.setAmazonFlagsForUser` | `writeToFile` | internal flags/metadata helper | no direct HOME writer in method | Confirmed static / bounded |
| `AmazonApplicationFlags.setAmazonMetadataForUser` | `setAmazonMetadataForUserLocked` | internal flags/metadata helper | no direct HOME writer in method | Confirmed static / bounded |
| `AmazonApplicationFlags.setAmazonMetadataForUser` | `writeToFile` | internal flags/metadata helper | no direct HOME writer in method | Confirmed static / bounded |
| `AmazonApplicationFlags.setApplicationInfoForUserLocked` | `setApplicationInfoForUserLocked` | internal flags/metadata helper | no direct HOME writer in method | Confirmed static / bounded |
| `AmazonApplicationFlags.writeToFile` | `writeToFile` | internal flags/metadata helper | no direct HOME writer in method | Confirmed static / bounded |
| `AmazonPackageManagerService.BinderService.getAmazonFlagsForUser` | `getAmazonFlagsForUser` | public/read wrapper; does not itself select HOME | no direct HOME writer in method | Confirmed static / bounded |
| `AmazonPackageManagerService.onBootPhase` | `init` | initialization path | no direct HOME writer in method | Confirmed static / bounded |
| `GameModeHelper.isGamingApp` | `getAmazonFlagsForUser` | game-mode consumer; bit-2 decision, no HOME writer | no direct HOME writer in method | Confirmed static / bounded |
| `AppCompatActivityManagerServiceCallback.isIncompatiblePackage` | `getAmazonFlagsForUser` | package compatibility consumer; bit-1 decision, no HOME writer | no direct HOME writer in method | Confirmed static / bounded |

## Reproduction

```sh
python3 tools/scripts/audit_phase6mu_amazon_application_flags.py --dry-run
python3 tools/scripts/audit_phase6mu_amazon_application_flags.py
```

Generated artifact: `artifacts/phase6mu-amazon-application-flags-20260810-01`.
