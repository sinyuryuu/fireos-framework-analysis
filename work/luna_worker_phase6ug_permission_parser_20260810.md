# Phase 6UG bounded ledger — FireOS/Amazon protectionLevel parser semantics

Date: 2026-08-10  
Scope: host-only static search. No permission changes, Binder/service calls, or device operations.

## Result

The bounded corpus proves an Amazon-specific compiled grant hook, but does not
prove the entire FireOS XML parser or every symbolic constant mapping. Rows
whose compiled control flow or source definition was not established are
explicitly `UNKNOWN`.

### Exact-build inputs

- `artifacts/framework/framework.jar` — SHA-256
  `1c16f5976318fadcf7add92c518a93896f99e2a78f742b7347d8539103264882`.
- `artifacts/services/fosservices.jar` — SHA-256
  `364603c0228058973ed976ff1bef51c3cab2fa8fc163c63c727157bb92dec96`.
- `artifacts/services/fosservices.vdex` — SHA-256
  `584673e398894936dcba7a79c07d1f5abda7f2d03b3e36bd1792f764dd4dcffa`.
- `artifacts/services/services.vdex` — SHA-256
  `06cb78333df89d97da741b921d7c62680b4a931aade45b83581b39d498cdbdc4`.
- `artifacts/framework/boot-fosframework.vdex` — SHA-256
  `d91bb12295e9ac55da414347643ff0e880e431eedc675f0944ad3f30cae06714`.
- `artifacts/framework/boot-framework.vdex` — SHA-256
  `9a160fc8d64b147beb3c19a16bbf40a9ccc2007c3d595092d15ae4437dfc6404`.
- `artifacts/phase6ac/android-amazon-perm-device-20260805-01/android.amazon.perm.apk` — SHA-256
  `5b72bdfcfb91b28d2c751e548f60d406de5c3cbb235e47e232014abdebcdc058`.

The manifest projection from the APK shows package `android.amazon.perm`,
`coreApp=true`, platform build 28, and permission values including
`0x80000002` and `0x80000012`. These are classified `AMAZON` as artifact-level
vendor evidence; the dump alone does not name the vendor symbolic constants.

## Confirmed compiled semantics

In `fosservices` disassembly,
`com.android.server.pm.permission.AmazonPermissionsGranter.grantSignaturePermission`
at `codeOff=0xd242a` first reads `BasePermission.protectionLevel`, masks
`0x80000000`, and returns the SELinux grant result when that bit is present.
It then masks `0x40000000`, consults
`FireOsSystemConfig.getAmzRestrictedPermissions(packageName)`, and grants only
when the permission is in the restricted set. This is an Amazon-specific
compiled control-flow finding, not an inferred parser rule.

The neighboring `addAmazonPermissions` method at `codeOff=0xd24ca` checks
SELinux policy `amazon_policies/grant_amazon_permissions` and adds Amazon
cross-user permission names. This confirms a vendor grant extension, while
the exact source of all permission declarations remains separate.

## AOSP Android 9 comparison

AOSP r1 source confirms the standard API/check surface:

- `PackageManagerService.checkPermission` and `checkUidPermission` delegate to
  `mPermissionManager` (lines 5320–5333).
- Permission scanning uses `PROTECTION_FLAG_INSTANT` and
  `PROTECTION_MASK_BASE`, including protection-change checks (lines
  17310–17323 and 17376–17388).
- `ActivityManagerService.PermissionController.checkPermission` delegates to
  AMS, and `isRuntimePermission` masks `PROTECTION_MASK_BASE` (lines
  9046–9074). AMS `checkPermission` denies null and calls
  `checkComponentPermission` (lines 9121–9126).

These rows are `AOSP_STANDARD`; they are comparison evidence, not proof that
FireOS uses only the AOSP path.

## UNKNOWN ledger

The bounded AOSP tree does not contain `android/content/pm/PermissionInfo.java`
or `android/content/pm/PackageParser.java`. Therefore the exact AOSP
`PROTECTION_FLAG_*` numeric declarations, `fixProtectionLevel`,
`protectionToString`, and XML parser handling cannot be cited from present
source. The exact-build `services` disassembly contains PermissionManagerService
and PermissionInfo references, but this search did not establish a complete
method-local parser/grant chain for every requested symbolic constant.

The CSV is the authoritative row-level ledger, including SHA, path, class,
method, offset/line anchor, and `AOSP_STANDARD` / `AMAZON` / `UNKNOWN` class.
