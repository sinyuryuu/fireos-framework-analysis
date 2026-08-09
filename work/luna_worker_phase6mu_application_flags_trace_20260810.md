# Phase 6MU — AmazonApplicationFlags trace (host-only, 2026-08-10)

## Scope and evidence basis

This report continues the bounded gap identified by Phase 6MS. It is a static file inventory at worktree `HEAD a38854ed89c6f663b75725746c14080e76f68585`. No device connection, ADB, Binder/service call, transaction, ioctl, OTA/recovery, root, reboot, or mutation was used. Phase 6MT's interface matrix was not repeated; it is referenced only for the already-established mutator entry points.

Primary source:

| File | SHA-256 | Used ranges |
|---|---|---|
| `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` | `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` | `AmazonPackageManagerService.BinderService` 95866–96037; `AmazonApplicationFlags` 94643–95794; `PackageRecencyCallback` 17079–17515; `GameModeHelper` 134699–134754; `AppCompatActivityManagerServiceCallback` 181521–181615 |

The Phase 6MT matrix, not reworked here, is `artifacts/phase6mt-amazon-ipc-candidates-20260810-01/method-matrix.csv`, SHA-256 `0d630a291c239decfd91f14bf0e41b6222f847b0f88de0eda9eb0de3a98b3744`. Its four relevant BinderService rows are the mutator boundary summarized below.

Classification: **Confirmed** means the static call/storage edge is directly present; **Strong** means a first-layer consumer or relevant negative result is directly present but its product/runtime effect is not proven; **Unknown/UNRESOLVED** means the corpus does not establish the next edge.

## Mutator boundary

All four methods are in `AmazonPackageManagerService.BinderService` and use `Context.checkCallingOrSelfPermission("amazon.permission.ADD_RM_PKG_METADATA")` before calling `AmazonApplicationFlags`; no `clearCallingIdentity` or `restoreCallingIdentity` appears in these bounded wrappers.

| Binder method | Source lines | First static call | Classification |
|---|---:|---|---|
| `removeAmazonFlagsForUser(List,int,int)` | `fosservices/disassembly.log:95955–95972` (bytecode call `0698ba`) | `AmazonApplicationFlags.removeAmazonFlagsForUser(List,int,int)` | **Confirmed** permission→mutator edge; explicit user argument |
| `removeAmazonMetadataForUser(String,List,int)` | `fosservices/disassembly.log:95973–95990` (call `0698f6`) | `AmazonApplicationFlags.removeAmazonMetadataForUser(String,List,int)` | **Confirmed** permission→mutator edge; explicit user argument |
| `setAmazonFlagsForUser(List,int,int)` | `fosservices/disassembly.log:95991–96008` (call `069932`) | `AmazonApplicationFlags.setAmazonFlagsForUser(List,int,int)` | **Confirmed** permission→mutator edge; explicit user argument |
| `setAmazonMetadataForUser(String,List,List,int)` | `fosservices/disassembly.log:96009–96026` (call `06996e`) | `AmazonApplicationFlags.setAmazonMetadataForUser(String,List,List,int)` | **Confirmed** permission→mutator edge; explicit user argument |

Service publication is at `fosservices/disassembly.log:96136`; the proxy/interface surface is already recorded by Phase 6MT and is intentionally not repeated as a matrix here.

## AmazonApplicationFlags in-memory update and persistence

### Data structures and mutator-to-writer path — Confirmed

`AmazonApplicationFlags` is declared at `fosservices/disassembly.log:95189`. Its static initializer creates `sAmazonFlags` and `mMetadataIndices` as `SparseArray` objects and sets the storage path to:

`/data/system/amazon_package_flags.xml`

The initializer is `fosservices/disassembly.log:95193–95214` (string assignment at `068f9a–068fa4`). The per-user object contains `mAmazonFlags` and `mAmazonMetadata` maps (`fosservices/disassembly.log:94962–95065`). `AmazonMetadata` stores package name plus a `HashMap` of metadata key/value pairs (`fosservices/disassembly.log:94722–94868`).

The four static mutators update the per-user maps and then call `writeToFile()`:

* `removeAmazonFlagsForUser` → per-package `removeApplicationInfoForUserLocked` → `writeToFile()` at `fosservices/disassembly.log:95477–95489`.
* `removeAmazonMetadataForUser` → `removeAmazonMetadataForUserLocked` → `writeToFile()` at `fosservices/disassembly.log:95490–95508`.
* `setAmazonFlagsForUser` → `setApplicationInfoForUserLocked` / `UsersAmazonApplicationInfoFlags.setFlags` → `writeToFile()` at `fosservices/disassembly.log:95518–95546`.
* `setAmazonMetadataForUser` → `setAmazonMetadataForUserLocked` / `UsersAmazonApplicationInfoFlags.setMetadata` and `updateMetadataIndices` → `writeToFile()` at `fosservices/disassembly.log:95547–95578`.

`writeToFile()` computes a checkpoint, then calls `writeToFile(File,SparseArray)` only when the hash changes (`fosservices/disassembly.log:95634–95641`). The first-level storage writer uses `AtomicFile.startWrite`, `BufferedOutputStream`, and `FastXmlSerializer` (`fosservices/disassembly.log:95642–95658`). It serializes root tag `amazonflagstag`, schema `2.0`, one `package` element per user/package, `userid`, `packagename`, `amazonflagsattr`, and metadata attributes (`fosservices/disassembly.log:95658–95730`). This is a real persistent file writer, not a call into PackageManager's enabled-state API.

### Read/reload path — Confirmed

`AmazonPackageManagerService.onBootPhase(500)` calls `AmazonApplicationFlags.init()` at `fosservices/disassembly.log:96087–96100`. `init()` calls `readFromFile()` (`95331–95339`), which checks the file, wraps it in `AtomicFile`, opens an input stream, and parses XML (`fosservices/disassembly.log:95337–95455`). The parser restores `userid`, `packagename`, `amazonflagsattr`, and metadata attributes by calling `setApplicationInfoForUserLocked` and `setAmazonMetadataForUserLocked` (`fosservices/disassembly.log:95408–95440`).

The direct read APIs are:

* `getAmazonFlagsForUser(String,int)` reads `sAmazonFlags` under a monitor (`fosservices/disassembly.log:95273–95293`).
* `getAmazonMetadataForUser(String,String,int)` reads the per-user metadata map under a monitor (`fosservices/disassembly.log:95294–95314`).
* `getMetadataIndexForUser(String,int)` reads `mMetadataIndices` (`fosservices/disassembly.log:95315–95325`).

## First-layer consumers

### PackageRecency — Confirmed flags consumer, no HOME/package writer

`PackageRecencyCallback.sendBroadcastWithDelay` calls `getAmazonFlagsForUser(packageName,userId)` at `fosservices/disassembly.log:17489–17495` and passes the returned integer to `PackageRecencyUtils.shouldSendBroadcast(...)` at `17496–17499`. If allowed, it sends `com.amazon.action.PACKAGE_RECENCY_NOTIFICATION` as the current user (`17500–17538`). This is a flags-gated package-recency broadcast sink. The bounded method contains no `HOME`, `preferred`, `firelauncher`, `setApplicationEnabledSetting`, or `setComponentEnabledSetting` call.

### GameMode — Confirmed flags consumer, no HOME/package writer

`GameModeHelper.isGamingApp(String,int)` calls `getAmazonFlagsForUser` and masks bit `2` at `fosservices/disassembly.log:134746–134754`. The result is only a boolean game-mode classification. No metadata read, HOME selection, preferred activity, Fire Launcher target, or enabled-state writer appears in this bounded method.

### AppCompat activity-manager callback — Confirmed flags consumer, no HOME/package writer

`AppCompatActivityManagerServiceCallback.isIncompatiblePackage(int,String)` calls `getAmazonFlagsForUser` and masks bit `1` at `fosservices/disassembly.log:181605–181615`. It returns an incompatibility boolean. No direct HOME/preferred/component/package enabled-state call appears in this method.

### Metadata consumers — Unknown / negative bounded result

The corpus contains the public static metadata readers inside `AmazonApplicationFlags` (`getAmazonMetadataForUser` and `getMetadataIndexForUser`), but a repository-wide static search found no external callsite for either reader. Therefore the first external metadata consumer is **UNRESOLVED**. This is a bounded negative result, not proof that no consumer exists in an omitted, native, generated, or unavailable class.

## Required keyword checks and HOME relevance

The same host corpus contains unrelated enabled-state writers, including the known FreeTime child-user path (`fosservices/disassembly.log:54297–54325`), but no call chain from any of the four `AmazonApplicationFlags` mutators, `writeToFile`, or the three identified flags consumers to:

* `setApplicationEnabledSetting`;
* `setComponentEnabledSetting`;
* preferred activity APIs or a `preferred` writer;
* `HOME`/`firelauncher` target selection.

The exact `AmazonApplicationFlags` static callsite search found only the mutators, initialization, internal readers/writers, and the three flags consumers listed above. Thus the current evidence supports “Amazon-specific package flags/metadata persistence and non-HOME consumers,” not “Fire Launcher/HOME override.”

## Result and remaining unresolved boundary

* **Confirmed:** all four mutators are permission-gated; they update per-user in-memory flags/metadata; they persist atomically to `/data/system/amazon_package_flags.xml`; boot-phase reload restores the same structures.
* **Strong:** flags are consumed by PackageRecency, GameMode, and AppCompat incompatibility classification. These consumers do not reach the requested HOME/enabled-state sinks in their bounded methods.
* **Unknown/UNRESOLVED:** external metadata consumer; any native/external/generated code not represented in this disassembly corpus; runtime caller UID and actual on-device contents of the XML file. No inference is made for those boundaries.

This closes the Phase 6MS recommendation at the first persistence writer and first visible readers without redoing Phase 6MT. Only this report was added; no other file was modified, and no commit or push was made.
