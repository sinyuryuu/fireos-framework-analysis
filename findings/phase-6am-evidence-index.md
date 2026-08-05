# Phase 6AM evidence index

All evidence in this phase is host-only. The source input is
`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` with SHA-256 `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`.

| Evidence ID | Source | Observed result | Confidence |
|---|---|---|---|
| `6AM-HJ-001` | `artifacts/amazon-services/*_fosinit.xml` | Four LauncherHijackPreventer callback registrations are preserved | Confirmed |
| `6AM-HJ-002` | `LauncherHijackPreventerActivityStackCallback.canSeeHomeTask` | SELinux/signature visibility boolean; no ResolveInfo/component construction | Confirmed |
| `6AM-HJ-003` | `LauncherHijackPreventerActivityManagerServiceCallback.checkPermission` | Leanback-dependent permission-name return | Confirmed |
| `6AM-HJ-004` | `LauncherHijackPreventerPackageManagerCallback.onShutdown` | Revokes READ_LOGS for stored package/user pairs | Confirmed |
| `6AM-HJ-005` | `LauncherHijackPreventerPermissionManagerCallback.blockDevelopmentPermPersist` | Records READ_LOGS package/user pairs | Confirmed |
| `6AM-HJ-006` | `LauncherHijackPreventerPackageStore` | In-memory support for permission cleanup | Confirmed |
| `6AM-HJ-007` | `PackageWhitelisterCallback` | fdrw/update bookkeeping; no HOME operation in class block | Strong evidence |
| `6AM-HJ-008` | All inspected class/method blocks | No direct Fire HOME selector in bounded scope | Strong evidence |

Device contact: none. Binder transactions: none. Package/settings mutation:
none. Fire Launcher state: unchanged.
