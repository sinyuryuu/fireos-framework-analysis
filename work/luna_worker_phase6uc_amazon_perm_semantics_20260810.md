# Phase 6UC — `android.amazon.perm` custom-permission semantics

## Scope and result

This is a host-only, static review of the saved exact-build artifacts and the
available AOSP Android 9 source comparison. No Binder transaction, service
call, broadcast, package mutation, permission mutation, OTA, reboot, or device
probe was performed.

The exact package artifact is `/system/framework/android.amazon.perm/android.amazon.perm.apk`,
SHA-256 `5b72bdfcfb91b28d2c751e548f60d406de5c3cbb235e47e232014abdebcdc058`.
Its manifest identifies package `android.amazon.perm`, `sharedUserId`
`android.uid.system`, `coreApp=true`, target/platform API 28. The saved manifest
audit reports 158 protected-broadcast declarations. This establishes source
package membership and package metadata; it does not establish a caller path
for any ordinary APK or shell.

## Owner package and permission records

The owner/source package record is `android.amazon.perm`. The package is a
framework APK under `/system/framework`, uses the system shared UID, and is
marked `coreApp`. The manifest XML-tree contains custom permission definitions
owned by that package. Representative exact records:

| Permission record | Manifest protection value | Decoded static meaning | Evidence |
|---|---:|---|---|
| `com.amazon.permission.GLOBAL_SYNC` | `0x80000002` | signature base plus Amazon vendor flag | `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt:180` |
| `com.amazon.permission.ParentalControl` | `0x80000002` | signature plus Amazon vendor flag | same file `:205` |
| `com.amazon.permission.APP_VERIFICATION` | `0x2` | signature base without the observed Amazon flag | same file `:230` |
| `com.amazon.CONTENT_PROVIDER_ACCESS` | `0x80000012` | non-signature base/flag combination; exact semantic label requires the platform constants/parser | same file `:25` |
| `com.amazon.permission.RECEIVE_HOME_LONGPRESSED_ACTION` | `0x80000002` | signature plus Amazon vendor flag | same file `:510` |
| `com.amazon.permission.RECEIVE_CUSTOM_HOME` | `0x80000002` | signature plus Amazon vendor flag | same file `:513` |
| `com.amazon.permission.RECEIVE_BOOT_AFTER_SYSTEM_OTA` | `0x80000002` | signature plus Amazon vendor flag | same file `:553` |

The XML-tree also shows a permission group (`amazon.permission-group.MAGIC_WINDOW`)
and group-associated permissions. The exact full owner-to-record inventory is
preserved in the XML-tree; this report records representative rows and the
eligibility-relevant classes. The image-policy XML extract did not itself
contain the `android.amazon.perm` manifest declarations: the source is the APK
manifest artifact, not `system/etc/permissions` policy XML.

## Framework/parser/policy comparison

In the available AOSP Android 9 r61 `PackageManagerService` source, permission
declaration handling checks redefinition ownership and signing capability. A
package cannot redefine an existing non-system permission without the required
permission-capable signing relationship; a system-owned redefinition is logged
and ignored. The same source prevents a non-platform package from changing an
existing non-runtime permission into a dangerous/runtime permission. Relevant
slice: `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java:17350-17440`.

The available AOSP slice also shows `checkPermission`/`checkUidPermission`
delegation and uses `PROTECTION_MASK_BASE` when classifying runtime permissions
(`PackageManagerService.java:5357-5380`; `ActivityManagerService.java:9110-9120`).
This supports the comparison that the base protection class is distinct from
vendor/auxiliary protection flags. It does not prove the FireOS/Amazon parser's
internal handling of the Amazon bit because that FireOS parser source is not in
the bounded source set.

Therefore:

* `0x80000002` is **confirmed as an encoded signature-base permission with an
  additional Amazon flag** from the exact manifest value and the Android
  protection-level encoding convention.
* The exact FireOS symbolic constant/name and every downstream policy decision
  for the Amazon flag are **UNKNOWN** from the available source slice.
* `0x80000012`, `0x40000002`, and other non-`0x80000002` values must not be
  normalized to `signature|amazon`; they remain distinct encoded records unless
  a matching exact-build parser/constant artifact is supplied.

## Grant source and eligibility

The owner package's system shared UID explains why its own package record is a
trusted framework source package, but it is not a general grant mechanism. The
exact saved evidence shows package ownership and manifest declarations only.
The following grant-source fields remain bounded as follows:

| Candidate source | Static conclusion | Status |
|---|---|---|
| Permission declaration by `android.amazon.perm` | Defines the permission records and protected broadcasts in the package manifest | Confirmed |
| System-package scan / PackageManager permission state | AOSP comparison shows scan-time declaration ownership and signature checks; exact FireOS runtime record is not captured here | Partly confirmed; runtime record UNKNOWN |
| `privapp_permissions.xml` allowlist | Separate mechanism for privileged grants; no evidence here that it grants these custom `signature|amazon` records | No grant link shown / UNKNOWN |
| Ordinary APK requesting the permission | A manifest request alone does not satisfy signature matching; no exact signing-certificate equivalence or runtime grant record was supplied | Not established; UNKNOWN |
| Shell UID 2000 | No static evidence in this bounded slice grants the custom permission to shell; shell identity is not equivalent to owner/signature | Not established; UNKNOWN |
| UID 1000 / system shared UID | Explains owner package identity and trusted system package context, but does not imply arbitrary callers inherit the permission | Owner context only; not a caller path |

For `signature` permissions, eligibility requires the framework's permission
grant/check path and the applicable signing relationship (plus any exact-build
vendor policy). A package being system/privileged, sharing a UID, or having a
same-looking package name is not by itself proof of signature equivalence.

## Shell vs ordinary-app boundary

No shell or ordinary-app eligibility is confirmed for these custom permissions.
The exact artifact confirms the owner package and its system shared UID only.
There is no Binder or service-call result in this phase, and no package-state
record proving a grant to UID 2000 or to an ordinary application. In
particular, this report does **not** infer an exploitable route from either
signature matching or UID 1000 ownership. A later eligibility claim would need
the exact permission record plus the requesting package's signing/grant state
and the concrete protected consumer; those inputs are outside this bounded
slice.

## Protected-broadcast note

The source-package audit records 158 protected-broadcast declarations, including
`amazon.intent.action.BOOT_AFTER_SYSTEM_OTA`, with the source package
`android.amazon.perm` and shared UID `android.uid.system`. This is a declaration
and source-membership result only. The audit itself states that other packages
or runtime inputs may contribute to the runtime protected-broadcast set; it is
not sender reachability proof.

## Evidence and limitations

Primary exact-build artifacts:

* `artifacts/phase6ac/android-amazon-perm-device-20260805-01/capture-metadata.md`
* `artifacts/phase6ac/android-amazon-perm-device-20260805-01/sha256sums.txt`
* `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
* `artifacts/phase6ac/protected-broadcast-source-audit-20260805-02/summary.json`
* `artifacts/phase6ac/protected-broadcast-source-audit-20260805-02/protected-broadcasts.csv`

AOSP comparison sources:

* `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java`
* `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/am/ActivityManagerService.java`

Missing exact-build inputs are deliberately marked `UNKNOWN`: FireOS's full
`PermissionInfo`/`PackageParser` implementation and symbolic Amazon protection
constant, complete runtime permission records, signing-certificate comparison
for every potential requester, and shell/ordinary-app grant records.
