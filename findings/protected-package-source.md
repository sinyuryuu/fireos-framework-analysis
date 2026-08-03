# Protected-Package Source Analysis

Status: the enforcement chain is `Confirmed`; the literal Fire Launcher entry in the runtime deny-list is `Strong evidence`, not a direct file-content confirmation.

## 1. Source chain

```text
Fire OS PackageManagerService
  -> ProtectedPackages.isPackageStateProtected(userId, packageName)
  -> ProtectedPackages.isProtectedPackage(packageName)
  -> VendorProtectedPackagesCallback.callShouldProtectPackage(...)
  -> ControlProtectedPackagesCallback.shouldProtectPackage(uid, packageName, context)
  -> system-app check
  -> PackageManagerDenyList / DenyListKeyPackages membership
  -> uid == Process.SHELL_UID (2000)
  -> protected = true
```

The source chain is supported by `P2-STATIC-001` through `P2-STATIC-006`. The runtime package error is `P2-RUN-001` and `P2-RUN-002`.

## 2. Classification of possible sources

| Candidate source | Evidence | Determination |
|---|---|---|
| Java hard-coded `com.amazon.firelauncher` in `PackageManagerService` gate | Focused VDEX inspection shows a generic package argument, standard provisioning check, vendor callback, and no Fire literal in the gate | `Disproved` as the inspected gate mechanism |
| Java hard-coded Fire Launcher in Amazon callback | `ControlProtectedPackagesCallback` reads a set and checks membership; no Fire literal was found in its method body | `Disproved` as a literal callback rule; runtime membership remains possible |
| Resource deny-list JSON | `DenyListArcusHelper.processJSON()` opens a system raw resource and parses `packages_deny_list` | `Strong evidence` |
| Device-protected SharedPreferences | Callback uses `PackageManagerDenyList` and `DenyListKeyPackages`; device metadata shows `/data/system/PackageManagerDenyList` exists | `Confirmed` as storage path/key design; contents unavailable to shell |
| Arcus/runtime update | `getDenyList(String)` parses external JSON and `saveProtectedPackages` replaces the string set | `Strong evidence` |
| Device Owner/Profile Owner package | `ProtectedPackages` has an owner branch; current policy evidence shows parental-controls Profile Owner, not Fire Launcher | `Confirmed` as a separate possible branch; `Disproved` as the observed Fire shell-error cause |
| Package metadata (`persistent`, `coreApp`, `requiredForSystemUser`) | Fire package dump shows system/privileged flags but no `PERSISTENT` or `CORE_APP` flag in the relevant summary | Not the demonstrated source of this shell-specific error; metadata alone is insufficient |

## 3. Deny-list storage and producer

### Consumer

`ControlProtectedPackagesCallback.getSharedPrefPackages(Context)` creates a device-protected storage context, obtains the data-system directory, and opens the `PackageManagerDenyList` shared-preferences file. `shouldDisableAmazonApp()` checks the set under `DenyListKeyPackages`.

Evidence: `fosservices/disassembly.log` around the `ControlProtectedPackagesCallback` class at `P2-STATIC-004`.

### Initial producer

`DenyListArcusHelper.extractListFromResorces()` checks whether `DenyListKeyPackages` exists. If absent, it invokes `processJSON()`, converts the result to a set, and commits it with `SharedPreferences.Editor.putStringSet("DenyListKeyPackages", ...)`.

`processJSON()` opens a system raw resource (`0x7e05000a` in the extracted code), parses JSON, reads the `packages_deny_list` array, and returns its package strings.

Evidence: `P2-STATIC-006`.

### Runtime producer/update

The same helper has a JSON parsing/update path that reads `packages_deny_list`, then `saveProtectedPackages()` removes/replaces the stored string set. The surrounding class initializes an Arcus handler and reads a `persist.sys.denylist_arcusid` property before registering synchronization/broadcast behavior.

This establishes that the set can be runtime-backed. It does not establish which service last populated the current device file.

## 4. Device observation

The read-only configuration capture records:

```text
-rw-rw---- 1 system system 2645 ... /data/system/PackageManagerDenyList
```

Attempts to list/read the corresponding shared-preferences XML as shell were denied. No content was copied or bypassed. Therefore the following statement is the strongest supported conclusion:

> `com.amazon.firelauncher` is treated as protected for shell enabled-state mutation, and the Amazon callback is the code path that can make a system app protected when it is in the deny list. The exact current list entry has not been directly read.

Confidence: `Strong evidence` (`P2-RUN-001`, `P2-STATIC-004`, `P2-STATIC-005`, `P2-STATIC-007`).

## 5. Fire Launcher package metadata

The User 0 package dump identifies Fire Launcher as:

| Field | Observed value | Meaning for this question |
|---|---|---|
| Package | `com.amazon.firelauncher` | Runtime target |
| Code path | `/system/priv-app/com.amazon.firelauncher` | System/priv-app location |
| UID | `10120` | Package UID, not the shell caller UID |
| Runtime flags | System package flags shown; private flags include privileged | Satisfies the callback's system-app class of test |
| Persistent flag | Not shown in the relevant flags | Not used as proof of protection |
| Core-app flag | Not shown in the relevant flags | Not used as proof of protection |
| User 0 state | Installed, visible, not suspended; enabled state default | Confirms no post-rejection mutation |

Evidence: package dump cited by `P2-STATE-001` and the Fire Launcher manifest evidence `P2-MAN-001`.

## 6. What would make membership `Confirmed`

One of the following would be sufficient without rerunning the disproved component test:

1. An authorized offline copy of the device-protected `PackageManagerDenyList` content with a preserved hash and the Fire package string.
2. A system-server diagnostic that prints the callback's `DenyListKeyPackages` set, captured read-only.
3. A matching Fire OS artifact/resource whose `packages_deny_list` array contains `com.amazon.firelauncher`, with exact build/variant match recorded.

No access-control bypass is proposed. If the data can only be obtained through Root or a partition read unavailable through authorized ADB/OTA artifacts, that becomes a Level 3 decision and must not be performed automatically.
