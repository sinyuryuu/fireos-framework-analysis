# Phase 6RV — host-only exact permission holder/caller closure

Date: 2026-08-10. Scope is PS7331 host artifacts and prior evidence only. No ADB, Binder/service call, installation, mutation, root/exploit, driver, OTA, reboot, or device write was performed. The companion CSV is the deterministic row ledger.

## Result

The exact `AmazonApplicationFlags` closure is:

`declaration (signature|amazon) -> holder UNKNOWN -> static facade/Binder callers -> checkCallingOrSelfPermission -> explicit user -> AmazonApplicationFlags -> /data/system/amazon_package_flags.xml`.

The declaration is present in `android.amazon.perm`, but the supplied PS7331 host corpus has no exact package-grant row for `amazon.permission.ADD_RM_PKG_METADATA`. Therefore the holder remains `UNKNOWN`; no package is inferred from system/privileged status or from unrelated permission grants.

Static callers are bounded to `AmazonPackageManagerImpl` flag/metadata facade methods plus generated `IAmazonPackageManager` proxy/stub and the system-server Binder implementation. The exact production instantiator, runtime UID, and legitimate package holder are not established. The service mutators show no bounded `clearCallingIdentity`; the explicit user argument reaches `AmazonApplicationFlags`.

`AmazonApplicationFlags` is a real atomic XML persistence sink. The visible static consumers are PackageRecency (recency broadcast), GameMode (classification), and AppCompat (incompatibility classification). The bounded corpus finds no edge from these mutators, persistence writer, or visible consumers to `setHomeActivity`, preferred-activity APIs, `setApplicationEnabledSetting`, or `setComponentEnabledSetting`. External/native/generated metadata consumers remain `UNKNOWN`.

## Other package/user/settings writer permissions

The ledger retains observed holder facts for `CHANGE_COMPONENT_ENABLED_STATE`, `MANAGE_USERS`, `WRITE_SECURE_SETTINGS`, `INSTALL_PACKAGES`, and `DELETE_PACKAGES`, but does not equate a granted package permission with a caller. Static package-state writers include the child/profile-scoped AmazonUserManager KFT path; static settings writers include SettingsProvider; PMS preferred activity has its own `SET_PREFERRED_APPLICATIONS` gate. None closes an `ADD_RM_PKG_METADATA -> HOME/package-state` join.

Evidence classes are literal and conservative: `OBSERVED HOLDER` means a saved package/grant artifact lists the package; `STATIC_ONLY` means a decompiled caller/gate/sink edge; `UNKNOWN` means the corpus does not establish the edge. The CSV preserves these labels and all unresolved values.

## Primary inputs and hashes

| Input | SHA-256 | Use |
|---|---|---|
| `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` | `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` | Binder mutators, persistence, consumers |
| `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log` | `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71` | interface and facade callers |
| `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt` | `not separately recorded in prior evidence` | exact permission declaration |
| `artifacts/phase6mc-permission-holder-audit-20260810-05/summary.json` | `not separately recorded in prior evidence` | generic permission holder counts/protection |
| `artifacts/phase6mx-amazon-pm-callers-20260810-01/caller-calls.csv` | `884b8636fd1baff3c1790cb4398e9cb83588dd68260643a4c660876c5269af82` | Amazon PM caller inventory |

## Disposition

No vulnerability or low-privilege route is inferred. The exact remaining gap is offline provenance: an exact-build package grant/permission-state artifact and a complete production caller instantiation for `ADD_RM_PKG_METADATA`; absent those, holder and runtime caller stay `UNKNOWN`.
