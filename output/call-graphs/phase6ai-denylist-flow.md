# Phase 6AI deny-list flow

The canonical Mermaid source is
[`phase6ai-denylist-flow.mmd`](./phase6ai-denylist-flow.mmd).

```text
shell package-state mutation
  -> PackageManagerService / ProtectedPackages
  -> VendorProtectedPackagesCallback.callShouldProtectPackage
  -> ControlProtectedPackagesCallback.shouldProtectPackage
  -> PackageManagerDenyList:DenyListKeyPackages
  -> protected=true for system/privileged + UID 2000
  -> rejection before state write

AmazonPackageManagerService.onBootPhase(500)
  -> DenyListArcusHelper
  -> resource JSON seed when key absent
  -> persist.sys.denylist_arcusid
  -> Arcus sync/unmod receiver
  -> openConfiguration
  -> packages_deny_list parser
  -> saveProtectedPackages
  -> device-protected SharedPreferences
```
