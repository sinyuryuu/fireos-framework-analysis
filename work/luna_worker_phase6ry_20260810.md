# Phase 6RY — exact permission/IPC provenance closure

Date: 2026-08-10  
Scope: PS7331 exact extracted manifests/XML, permission-holder artifacts,
VDEX/DEX disassembly, generated AIDL Stub/Proxy, and prior Phase 6RV evidence.
Host-only and read-only. No ADB, Binder/service call, broadcast, APK install,
mutation, input injection, driver access, OTA/recovery, root/exploit, reboot,
or partition operation was performed.

## Result

The exact four `IAmazonPackageManager` metadata/flags mutators are closed to
the first proven storage sink, but not to an exact holder or production caller:

`declaration -> grant/holder -> Binder entry -> caller -> identity/user -> sink`

is therefore:

`UNKNOWN declaration/holder -> generated Stub/Proxy + BinderService ->
AmazonPackageManagerImpl facade (exact framework callsite; upstream production
caller UNKNOWN) -> checkCallingOrSelfPermission, explicit userId, no bounded
clearCallingIdentity -> AmazonApplicationFlags XML persistence`

The bounded corpus does not establish a HOME, preferred-activity, component,
or ordinary package-state consumer for `ADD_RM_PKG_METADATA`. A missing custom
permission declaration or holder row is not vulnerability evidence.

## Exact `ADD_RM_PKG_METADATA` closure

The service implementation is `AmazonPackageManagerService.BinderService`.
The four methods at `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:95866-96037`
call `Context.checkCallingOrSelfPermission("amazon.permission.ADD_RM_PKG_METADATA")`
before delegating to `AmazonApplicationFlags`:

| Binder method | Transaction | exact facade edge | first sink | status |
|---|---:|---|---|---|
| `removeAmazonFlagsForUser` | 2 | `removeAmazonFlagsForPackages` → `removeAmazonFlagsForUser` | flags map/XML writer | confirmed static; holder/caller UNKNOWN |
| `removeAmazonMetadataForUser` | 1 | `removeAmazonMetadataForPackage` → `removeAmazonMetadataForUser` | metadata map/XML writer | confirmed static; holder/caller UNKNOWN |
| `setAmazonFlagsForUser` | 4 | `addAmazonFlagsForPackages` → `setAmazonFlagsForUser` | flags map/XML writer | confirmed static; holder/caller UNKNOWN |
| `setAmazonMetadataForUser` | 5 | `addAmazonMetadataForPackage` → `setAmazonMetadataForUser` | metadata map/XML writer | confirmed static; holder/caller UNKNOWN |

The interface declarations are at `boot-fosframework/disassembly.log:58318-58352`.
Generated Proxy and Stub dispatch are at `:402917-403398` and
`:404651-404714`. These are Binder contract/dispatch artifacts, not production
callers. The exact framework facade callsites are at `:367221`, `:367289`,
`:369119`, and `:369164`; the caller inventory found no caller above those
facade methods. `UserHandle`-derived/exact user arguments are preserved in the
facade records. No clear/restore identity operation appears in the bounded
service mutator blocks.

The exact first persistence/consumer review found `/data/system/amazon_package_flags.xml`
and reads used by package-recency, game-mode, and compatibility paths. The
bounded consumer corpus contains no `setHomeActivity`,
`replacePreferredActivity`, `addPersistentPreferredActivity`,
`setApplicationEnabledSetting`, or `setComponentEnabledSetting` edge from
these flags/metadata values. Thus metadata persistence is confirmed; a HOME or
package-state bridge is not found, not disproven outside the corpus.

## Declaration and holder provenance

`ADD_RM_PKG_METADATA` was not found in the bounded
`018_android.amazon.perm.xmltree.txt` custom permission listing, and no exact
grant/holder row was found in the standard permission-holder census. Its
declaration, protection level, holder package, grant source, and production
caller remain **UNKNOWN**. This is an evidence boundary, not a negative grant
claim.

For linked standard permissions, the saved permission audit establishes the
framework `android` package as declaration source with `signature|privileged`
(and `development` where applicable), and records holders separately from
callers. Relevant holder classes include system/priv-apps plus selected
Vending/data-app rows for `CHANGE_COMPONENT_ENABLED_STATE`, `MANAGE_USERS`,
`WRITE_SECURE_SETTINGS`, `INSTALL_PACKAGES`, and `DELETE_PACKAGES`. A granted
permission row does not establish that the package reached a chosen protected
target or that it was the production caller of a particular Binder entry.

The exact linked paths are retained in CSV rows 6RY-007 through 6RY-011:

- KFT child lifecycle: `CHANGE_COMPONENT_ENABLED_STATE` and `MANAGE_USERS`
  reach Fire/Tahoe/Launcher3 component/application setters only with supplied
  child/profile user data; exact ordinary caller-to-holder join is UNKNOWN.
- SettingsProvider writer family: `WRITE_SECURE_SETTINGS` reaches secure
  settings XML; exact production caller inventory is UNKNOWN and no PMS/HOME
  sink is proven.
- Install/delete writer families: package state sinks exist, but exact caller,
  target, and identity join vary and no ADD_RM bridge is shown.
- Preferred HOME: Settings/shell static APIs and PMS preferred sinks are
  present, but effective caller, holder, and runtime result remain UNKNOWN.

## Public/exported metadata and IPC boundary

The requested public/exported broadcast/provider/service review is bounded by
the exact saved manifest/fosinit corpus. The Amazon PM service publication is
present in `amazonpackagemanager_fosinit.xml`; generated interfaces and tx6/tx7
dispatch are present. Existing Phase 6IP/6RV evidence bounds tx6/tx7 to
ProxyReceiver registration/deregistration state and PendingIntent ownership or
system-creator checks; no HOME/PMS/package-state sink follows. Any public or
exported component whose exact manifest, required permission, caller, or user
mapping is absent remains UNKNOWN. No component was invoked.

## Prior Phase 6RV reconciliation

Phase 6RV already established static mutator/persistence structure, separated
SystemUI/overlay and OOBE/OTA paths, and explicitly left holder and production
caller UNKNOWN. Phase 6RY adds the exact generated interface/Proxy/Stub
transaction mapping, exact framework facade callsites, and the holder-versus-
caller distinction for linked standard permissions. It does not convert
generated code, a permission grant, or a static writer into production caller
provenance.

## Validation and hashes

The companion CSV has 12 data rows. It was inspected with Python's RFC-4180
CSV parser; all rows have the same 11 columns, and all fields containing commas
are quoted. The following source hashes were recomputed during this phase:

| Artifact | SHA-256 |
|---|---|
| `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` | `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` |
| `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log` | `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71` |
| `artifacts/phase6mx-amazon-pm-callers-20260810-01/caller-calls.csv` | `884b8636fd1baff3c1790cb4398e9cb83588dd68260643a4c660876c5269af82` |
| `artifacts/phase6mc-permission-holder-audit-20260810-05/permission-holders.csv` | `1f97fa825f8b7cd86f05653259ecf43359d496d15af4e21e0c53512274ebdb18` |
| `artifacts/phase6mc-permission-holder-audit-20260810-05/summary.json` | `f507f30499f778c94b3b52f5835cdd5ce365039ffdb88c02180509661f840103` |
| `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt` | `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed` |
| `output/tables/phase6lz-component-state-permissions/component-state-permission-holders.csv` | `8eeb03c1757832d9ea33abe4968724444ce3d0fe2befc4ea296e482b5ac398e1` |

Final output hashes are reported after creation. No runtime negative result is
claimed; risk-rejected operations remain risk-rejected.
