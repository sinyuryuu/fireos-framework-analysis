# HOME Resolver Method Analysis (Phase 3A)

## Scope and artifact identity

This report is generated from the matching Fire OS 7 services VDEX/FOS-services disassembly and the local Android 9 r1/r61 source snapshots. It records low-level evidence and does not infer missing code.

- Fire services disassembly: `decompiled/baksmali/vdexExtractor/services/disassembly.log`; SHA-256 `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53`.
- Fire FOS-services disassembly: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`; SHA-256 `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`.
- AOSP r1 source root: `aosp/android-9/android-9.0.0_r1/platform`.
- AOSP r61 source root: `aosp/android-9/android-9.0.0_r61/platform`.
- Classifications used: `AOSP_STANDARD`, `AMAZON_ADDITION`, `AMAZON_MODIFICATION`, `VERSION_DIFFERENCE`, `DECOMPILER_ARTIFACT`, `UNKNOWN`.

## Fire OS method inventory

| Method | Class | VDEX line | codeOff | Descriptor |
|---|---|---:|---|---|
| `chooseBestActivity` | `PackageManagerService` | 934336 | `2b5b2e` | `(Landroid/content/Intent;Ljava/lang/String;ILjava/util/List;I)Landroid/content/pm/ResolveInfo;` |
| `findPreferredActivity` | `PackageManagerService` | 959826 | `2b6206` | `(Landroid/content/Intent;Ljava/lang/String;ILjava/util/List;IZZZI)Landroid/content/pm/ResolveInfo;` |
| `findPersistentPreferredActivityLP` | `PackageManagerService` | 938922 | `2b5fc2` | `(Landroid/content/Intent;Ljava/lang/String;ILjava/util/List;ZI)Landroid/content/pm/ResolveInfo;` |
| `resolveIntent` | `PackageManagerService` | 966090 | `2b6ab8` | `(Landroid/content/Intent;Ljava/lang/String;II)Landroid/content/pm/ResolveInfo;` |
| `resolveIntentInternal` | `PackageManagerService` | 951258 | `2b6ade` | `(Landroid/content/Intent;Ljava/lang/String;IIZI)Landroid/content/pm/ResolveInfo;` |
| `queryIntentActivitiesInternal` | `PackageManagerService` | 947548 | `2c13a0` | `(Landroid/content/Intent;Ljava/lang/String;II)Ljava/util/List;` |
| `queryIntentActivitiesInternal` | `PackageManagerService` | 947566 | `2c13ca` | `(Landroid/content/Intent;Ljava/lang/String;IIIZZ)Ljava/util/List;` |
| `adjustPriority` | `PackageManagerService.ActivityIntentResolver` | 925124 | `2abde4` | `(Ljava/util/List;Landroid/content/pm/PackageParser$ActivityIntentInfo;)V` |
| `sortResults` | `IntentResolver` | 87364 | `7e5fe` | `(Ljava/util/List;)V` |
| `sortResults` | `IntentFirewall.FirewallIntentResolver` | 867494 | `35558` | `(Ljava/util/List;)V` |
| `sortResults` | `CrossProfileIntentResolver` | 923620 | `35558` | `(Ljava/util/List;)V` |
| `sortResults` | `PackageManagerService.ActivityIntentResolver` | 925837 | `2ac16e` | `(Ljava/util/List;)V` |
| `sortResults` | `PackageManagerService.ProviderIntentResolver` | 928038 | `2ac16e` | `(Ljava/util/List;)V` |
| `sortResults` | `PackageManagerService.ServiceIntentResolver` | 928509 | `2ac16e` | `(Ljava/util/List;)V` |

## AOSP method inventory

| Tag | Method | File | Lines |
|---|---|---|---:|
| android-9.0.0_r1 | `chooseBestActivity` | `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java` | 6149-6227 |
| android-9.0.0_r1 | `findPreferredActivity` | `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java` | 6306-6480 |
| android-9.0.0_r1 | `findPersistentPreferredActivityLP` | `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java` | 6247-6303 |
| android-9.0.0_r1 | `resolveIntent` | `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java` | 5967-5971 |
| android-9.0.0_r1 | `resolveIntentInternal` | `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java` | 5978-6000 |
| android-9.0.0_r1 | `queryIntentActivitiesInternal` | `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java` | 6565-6570 |
| android-9.0.0_r1 | `adjustPriority` | `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java` | 12575-12761 |
| android-9.0.0_r1 | `sortResults` | `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java` | 12921-12923 |
| android-9.0.0_r1 | `sortResults` | `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/IntentResolver.java` | `NOT_FOUND` |
| android-9.0.0_r1 | `queryIntent` | `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/IntentResolver.java` | `NOT_FOUND` |
| android-9.0.0_r1 | `filterResults` | `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/IntentResolver.java` | `NOT_FOUND` |
| android-9.0.0_r1 | `sortResults` | `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PreferredIntentResolver.java` | `NOT_FOUND` |
| android-9.0.0_r1 | `queryIntent` | `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PreferredIntentResolver.java` | `NOT_FOUND` |
| android-9.0.0_r1 | `filterResults` | `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PreferredIntentResolver.java` | `NOT_FOUND` |
| android-9.0.0_r1 | `sortResults` | `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PersistentPreferredIntentResolver.java` | `NOT_FOUND` |
| android-9.0.0_r1 | `queryIntent` | `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PersistentPreferredIntentResolver.java` | `NOT_FOUND` |
| android-9.0.0_r1 | `filterResults` | `aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PersistentPreferredIntentResolver.java` | `NOT_FOUND` |
| android-9.0.0_r61 | `chooseBestActivity` | `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java` | 6185-6263 |
| android-9.0.0_r61 | `findPreferredActivity` | `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java` | 6342-6516 |
| android-9.0.0_r61 | `findPersistentPreferredActivityLP` | `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java` | 6283-6339 |
| android-9.0.0_r61 | `resolveIntent` | `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java` | 6003-6007 |
| android-9.0.0_r61 | `resolveIntentInternal` | `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java` | 6014-6036 |
| android-9.0.0_r61 | `queryIntentActivitiesInternal` | `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java` | 6601-6606 |
| android-9.0.0_r61 | `adjustPriority` | `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java` | 12611-12797 |
| android-9.0.0_r61 | `sortResults` | `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java` | 12957-12959 |
| android-9.0.0_r61 | `sortResults` | `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/IntentResolver.java` | `NOT_FOUND` |
| android-9.0.0_r61 | `queryIntent` | `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/IntentResolver.java` | `NOT_FOUND` |
| android-9.0.0_r61 | `filterResults` | `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/IntentResolver.java` | `NOT_FOUND` |
| android-9.0.0_r61 | `sortResults` | `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PreferredIntentResolver.java` | `NOT_FOUND` |
| android-9.0.0_r61 | `queryIntent` | `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PreferredIntentResolver.java` | `NOT_FOUND` |
| android-9.0.0_r61 | `filterResults` | `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PreferredIntentResolver.java` | `NOT_FOUND` |
| android-9.0.0_r61 | `sortResults` | `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PersistentPreferredIntentResolver.java` | `NOT_FOUND` |
| android-9.0.0_r61 | `queryIntent` | `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PersistentPreferredIntentResolver.java` | `NOT_FOUND` |
| android-9.0.0_r61 | `filterResults` | `aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PersistentPreferredIntentResolver.java` | `NOT_FOUND` |

## Priority and preferred ordering

`AOSP_STANDARD`: Android 9 `resolveIntentInternal()` queries the candidate list and calls `chooseBestActivity()` when a single result is not already decisive.

`AOSP_STANDARD`: `chooseBestActivity()` first returns the only candidate. With multiple candidates it compares the first two candidates' `priority`, `preferredOrder`, and `isDefault`. If any differs, it returns the first candidate before calling `findPreferredActivity()`.

`AOSP_STANDARD`: only when those first-two ranking fields tie does `chooseBestActivity()` call `findPreferredActivity()`. `findPreferredActivity()` checks persistent preferred activities first, then ordinary preferred activities and validates their match quality and membership in the current candidate set.

`Confirmed` for this artifact: Fire OS `chooseBestActivity()` contains the same priority/preferredOrder/isDefault comparison before its `findPreferredActivity()` invocation. Therefore an `mAlways=true` Microsoft record cannot override a candidate list whose first candidate is Fire priority 50 and whose next candidate has a different priority, unless Fire OS added an earlier branch not represented in the inspected method. No such Fire package-name branch was found in the selected method evidence.

This explains the existing runtime result as follows: Microsoft can receive a preferred record and the shell command can return Success, but the resolver reaches the ranking-return path before ordinary preferred selection because Fire priority 50 differs from Microsoft's priority 0. The claim is `Strong evidence` because it is supported by both VDEX control flow and the preserved runtime test.

## Effective priority normalization

`AOSP_STANDARD`: Android 9 `ActivityIntentResolver.adjustPriority()` caps a positive intent-filter priority to `0` when the owning application is not privileged. The Fire VDEX contains the same `privateFlags & 0x8` privileged check and calls `ActivityIntentInfo.setPriority(0)` for the non-privileged branch at codeOff `0x2abe02`-`0x2abe22`.

The Phase 3A APK manifests retain their declared priorities (0, 49, 50, 51, 100), but the device's `query-activities` output reports effective priority `0` for all five sideloaded research packages. Fire Launcher is a privileged system package and retains effective priority `50`. This is `Confirmed` as the primary explanation for why a priority-51 or priority-100 ordinary APK did not outrank Fire; it is not evidence of an Amazon-only resolver ranking rule.

## Method evidence

`chooseBestActivity` — `PackageManagerService`, VDEX line 934336, codeOff `2b5b2e`.

```text
2b5bc4: 5292 bf02                              |0049: iget v2, v9, Landroid/content/pm/ResolveInfo;.priority:I // field@02bf
2b5bf0: 5282 bf02                              |005f: iget v2, v8, Landroid/content/pm/ResolveInfo;.priority:I // field@02bf
2b5c08: 5290 bf02                              |006b: iget v0, v9, Landroid/content/pm/ResolveInfo;.priority:I // field@02bf
2b5c0c: 5281 bf02                              |006d: iget v1, v8, Landroid/content/pm/ResolveInfo;.priority:I // field@02bf
2b5c14: 5290 be02                              |0071: iget v0, v9, Landroid/content/pm/ResolveInfo;.preferredOrder:I // field@02be
2b5c18: 5281 be02                              |0073: iget v1, v8, Landroid/content/pm/ResolveInfo;.preferredOrder:I // field@02be
2b5c38: 5295 bf02                              |0083: iget v5, v9, Landroid/content/pm/ResolveInfo;.priority:I // field@02bf
2b5c9e: 54a3 ff4f                              |00b6: iget-object v3, v10, Lcom/android/server/pm/PackageManagerService;.mSettings:Lcom/android/server/pm/Settings; // field@4fff
```

`findPreferredActivity` — `PackageManagerService`, VDEX line 959826, codeOff `2b6206`.

```text
2b6274: 7607 da9f 0100                         |0035: invoke-direct/range {v1, v2, v3, v4, v5, v6, v7}, Lcom/android/server/pm/PackageManagerService;.findPersistentPreferredActivityLP:(Landroid/content/Intent;Ljava/lang/String;ILjava/util/List;ZI)Landroid/content/pm/ResolveInfo; // method@9fda
2b6286: 5480 ff4f                              |003e: iget-object v0, v8, Lcom/android/server/pm/PackageManagerService;.mSettings:Lcom/android/server/pm/Settings; // field@4fff
2b62a4: 1a03 eb62                              |004d: const-string v3, "Looking for preferred activities..." // string@62eb
2b62c4: 6e5b 45a3 c239                         |005d: invoke-virtual {v2, v12, v9, v3, v11}, Lcom/android/server/pm/PreferredIntentResolver;.queryIntent:(Landroid/content/Intent;Ljava/lang/String;ZI)Ljava/util/List; // method@a345
2b62ec: 1a07 ad35                              |0071: const-string v7, "Figuring out best match..." // string@35ad
2b63aa: 5240 bb02                              |00d0: iget v0, v4, Landroid/content/pm/ResolveInfo;.match:I // field@02bb
2b63b2: 5240 bb02                              |00d4: iget v0, v4, Landroid/content/pm/ResolveInfo;.match:I // field@02bb
```

`findPersistentPreferredActivityLP` — `PackageManagerService`, VDEX line 938922, codeOff `2b5fc2`.

```text
2b5fda: 5404 ff4f                              |000a: iget-object v4, v0, Lcom/android/server/pm/PackageManagerService;.mSettings:Lcom/android/server/pm/Settings; // field@4fff
2b5fde: 5444 3551                              |000c: iget-object v4, v4, Lcom/android/server/pm/Settings;.mPersistentPreferredActivities:Landroid/util/SparseArray; // field@5135
2b5fea: 1f04 bf15                              |0012: check-cast v4, Lcom/android/server/pm/PersistentPreferredIntentResolver; // type@15bf
2b5ff6: 1a06 ec62                              |0018: const-string v6, "Looking for presistent preferred activities..." // string@62ec
2b601e: 6e52 0ca3 8479                         |002c: invoke-virtual {v4, v8, v9, v7, v2}, Lcom/android/server/pm/PersistentPreferredIntentResolver;.queryIntent:(Landroid/content/Intent;Ljava/lang/String;ZI)Ljava/util/List; // method@a30c
2b6058: 1f0c be15                              |0049: check-cast v12, Lcom/android/server/pm/PersistentPreferredActivity; // type@15be
2b606e: 1a0e c426                              |0054: const-string v14, "Checking PersistentPreferredActivity ds=" // string@26c4
2b6078: 6e10 fea2 0c00                         |0059: invoke-virtual {v12}, Lcom/android/server/pm/PersistentPreferredActivity;.countDataSchemes:()I // method@a2fe
2b6084: 6e20 00a3 6c00                         |005f: invoke-virtual {v12, v6}, Lcom/android/server/pm/PersistentPreferredActivity;.getDataScheme:(I)Ljava/lang/String; // method@a300
2b60a2: 54ce 8f50                              |006e: iget-object v14, v12, Lcom/android/server/pm/PersistentPreferredActivity;.mComponent:Landroid/content/ComponentName; // field@508f
2b60d0: 6e30 ffa2 5c06                         |0085: invoke-virtual {v12, v5, v6}, Lcom/android/server/pm/PersistentPreferredActivity;.dump:(Landroid/util/Printer;Ljava/lang/String;)V // method@a2ff
2b60d6: 54c5 8f50                              |0088: iget-object v5, v12, Lcom/android/server/pm/PersistentPreferredActivity;.mComponent:Landroid/content/ComponentName; // field@508f
2b60ee: 1a0d 5936                              |0094: const-string v13, "Found persistent preferred activity:" // string@3659
2b61a4: 1a00 4c75                              |00ef: const-string v0, "Returning persistent preferred activity: " // string@754c
```

`resolveIntent` — `PackageManagerService`, VDEX line 966090, codeOff `2b6ab8`.

```text
2b6ad2: 7607 2ca1 0000                         |000b: invoke-direct/range {v0, v1, v2, v3, v4, v5, v6}, Lcom/android/server/pm/PackageManagerService;.resolveIntentInternal:(Landroid/content/Intent;Ljava/lang/String;IIZI)Landroid/content/pm/ResolveInfo; // method@a12c
```

`resolveIntentInternal` — `PackageManagerService`, VDEX line 951258, codeOff `2b6ade`.

```text
2b6ae8: 1b00 cb3a 0100                         |0003: const-string/jumbo v0, "resolveIntent" // string@00013acb
2b6b52: 1b00 3231 0100                         |0038: const-string/jumbo v0, "queryIntentActivities" // string@00013132
2b6b78: 7608 fba0 0f00                         |004b: invoke-direct/range {v15, v16, v17, v18, v19, v20, v21, v22}, Lcom/android/server/pm/PackageManagerService;.queryIntentActivitiesInternal:(Landroid/content/Intent;Ljava/lang/String;IIIZZ)Ljava/util/List; // method@a0fb
```

`queryIntentActivitiesInternal` — `PackageManagerService`, VDEX line 947548, codeOff `2c13a0`.

```text
2c13bc: 7608 fba0 0000                         |000c: invoke-direct/range {v0, v1, v2, v3, v4, v5, v6, v7}, Lcom/android/server/pm/PackageManagerService;.queryIntentActivitiesInternal:(Landroid/content/Intent;Ljava/lang/String;IIIZZ)Ljava/util/List; // method@a0fb
```

`adjustPriority` — `PackageManagerService.ActivityIntentResolver`, VDEX line 925124, codeOff `2abde4`.

```text
2abe02: 5212 7901                              |000d: iget v2, v1, Landroid/content/pm/ApplicationInfo;.privateFlags:I // field@0179
2abe1c: 6e20 b208 4f00                         |001a: invoke-virtual {v15, v4}, Landroid/content/pm/PackageParser$ActivityIntentInfo;.setPriority:(I)V // method@08b2
2abe68: 5455 0050                              |0040: iget-object v5, v5, Lcom/android/server/pm/PackageManagerService;.mSetupWizardPackage:Ljava/lang/String; // field@5000
2abe7a: 6e20 b208 4f00                         |0049: invoke-virtual {v15, v4}, Landroid/content/pm/PackageParser$ActivityIntentInfo;.setPriority:(I)V // method@08b2
2abe92: 6e20 b208 4f00                         |0055: invoke-virtual {v15, v4}, Landroid/content/pm/PackageParser$ActivityIntentInfo;.setPriority:(I)V // method@08b2
2abed8: 6e20 b208 4f00                         |0078: invoke-virtual {v15, v4}, Landroid/content/pm/PackageParser$ActivityIntentInfo;.setPriority:(I)V // method@08b2
2abf08: 6e20 b208 4f00                         |0090: invoke-virtual {v15, v4}, Landroid/content/pm/PackageParser$ActivityIntentInfo;.setPriority:(I)V // method@08b2
2abf38: 6e20 b208 4f00                         |00a8: invoke-virtual {v15, v4}, Landroid/content/pm/PackageParser$ActivityIntentInfo;.setPriority:(I)V // method@08b2
2abf68: 6e20 b208 4f00                         |00c0: invoke-virtual {v15, v4}, Landroid/content/pm/PackageParser$ActivityIntentInfo;.setPriority:(I)V // method@08b2
2abfb0: 6e20 b208 4f00                         |00e4: invoke-virtual {v15, v4}, Landroid/content/pm/PackageParser$ActivityIntentInfo;.setPriority:(I)V // method@08b2
```

`sortResults` — `IntentResolver`, VDEX line 87364, codeOff `7e5fe`.

## Vendor callback boundary

`AMAZON_ADDITION`: Fire OS `ActivityStackSupervisor.resolveIntent()` calls `VendorActivityStackSupervisorCallback.callResolveIntent()` before invoking `PackageManagerInternal.resolveIntent()`. The callback can return a non-null `ResolveInfo`, in which case the ActivityStackSupervisor path returns it without reaching the normal PackageManagerInternal call.

The FOS-services artifact contains `AppCompatActivityStackSupervisorCallback.resolveIntent()`. Its inspected body calls `IPackageManager.resolveIntent()` and then applies `isUninstalledApp()` before deciding whether to return the result. This proves a vendor interception boundary, but does not prove that it changes HOME selection or names `com.amazon.firelauncher`.

Fire callback call sites found: `2`.
- 222444: direct_method #22969: callResolveIntent ([Lcom/android/server/am/VendorActivityStackSupervisorCallback;Landroid/content/Intent;Ljava/lang/String;II)Landroid/content/pm/ResolveInfo;
- 796462: 11a170: 7152 b959 d0fe                         |001a: invoke-static {v0, v13, v14, v15, v2}, Lcom/android/server/am/VendorActivityStackSupervisorCallback;.callResolveIntent:([Lcom/android/server/am/VendorActivityStackSupervisorCallback;Landroid/content/Intent;Ljava/lang/String;II)Landroid/content/pm/ResolveInfo; // method@59b9

Selected FOS-services resolver lines:
- 41123: virtual_method #5024: resolveIntent (Landroid/content/Intent;Ljava/lang/String;II)Landroid/content/pm/ResolveInfo;
- 41135: 037972: 7257 b502 5236                         |000d: invoke-interface {v2, v5, v6, v3, v7}, Landroid/content/pm/IPackageManager;.resolveIntent:(Landroid/content/Intent;Ljava/lang/String;II)Landroid/content/pm/ResolveInfo; // method@02b5

Status: `Strong evidence` that a vendor callback can intervene in ActivityManager's resolve path; `Hypothesis` that it affects this HOME request; `Unknown` whether any callback returns an explicit Fire component.

## Package-name special case search

Literal `com.amazon.firelauncher` occurrences in the selected Fire services disassembly: `0`.
- `[NOT_FOUND]` in selected services VDEX.

Absence of a literal does not exclude a resource, encoded string, callback-provided value, or another artifact. It does exclude a direct literal in the inspected text.

## Findings classification

| Finding | Classification | Confidence |
|---|---|---|
| Base candidate ranking and preferred ordering | `AOSP_STANDARD` | Confirmed by AOSP and Fire VDEX structure |
| Fire VDEX priority comparison before ordinary preferred lookup | `AOSP_STANDARD` | Confirmed |
| Non-privileged positive intent-filter priority is capped to zero | `AOSP_STANDARD` | Confirmed by AOSP `adjustPriority()`, Fire VDEX, and runtime candidates |
| Fire privileged-system priority 50 remains effective | `AOSP_STANDARD` plus Fire manifest choice | Strong evidence |
| Vendor ActivityStackSupervisor resolve callback | `AMAZON_ADDITION` | Strong evidence |
| Fire-specific resolver ranking or explicit component launch | `UNKNOWN` | No direct evidence in selected method scan |
| Microsoft `mAlways=true` ineffective in current HOME test | Runtime consequence of ranking path | Strong evidence |

## Limits

The current artifact is VDEX disassembly and the AOSP source snapshot is not a complete build tree for every IntentResolver source file. This report does not claim byte-for-byte equivalence, does not infer hidden vendor callback implementations, and does not replace the controlled priority APK experiment.
