# HOME Resolver AOSP vs Fire OS Difference Report

## Method presence and source locations

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

Fire OS method inventory:

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

## r1 vs r61 selected-body comparison

| Method | Result | Classification |
|---|---|---|
| `chooseBestActivity` | `no_selected_line_difference` | `AOSP_STANDARD` |
| `findPreferredActivity` | `no_selected_line_difference` | `AOSP_STANDARD` |
| `findPersistentPreferredActivityLP` | `no_selected_line_difference` | `AOSP_STANDARD` |
| `resolveIntent` | `no_selected_line_difference` | `AOSP_STANDARD` |
| `resolveIntentInternal` | `no_selected_line_difference` | `AOSP_STANDARD` |
| `queryIntentActivitiesInternal` | `no_selected_line_difference` | `AOSP_STANDARD` |
| `adjustPriority` | `no_selected_line_difference` | `AOSP_STANDARD` |
| `sortResults` | `no_selected_line_difference` | `AOSP_STANDARD` |

## Evidence-based Fire OS differences

| Difference | Classification | Evidence |
|---|---|---|
| `VendorActivityStackSupervisorCallback.callResolveIntent()` is invoked before PackageManagerInternal resolution | `AMAZON_ADDITION` | Fire ActivityStackSupervisor VDEX method `resolveIntent`, codeOff `0x11a138` |
| `VendorProtectedPackagesCallback` exists in the protected-package path | `AMAZON_ADDITION` | Existing Phase 2 static evidence; not a HOME ranking proof |
| Fire priority 50 in the HOME manifest | `AMAZON_ADDITION` | Existing Phase 2 manifest evidence; not a resolver code patch |
| Non-privileged positive intent-filter priority is capped in `adjustPriority()` | `AOSP_STANDARD` | AOSP r1/r61 `PackageManagerService.adjustPriority()` and Fire `ActivityIntentResolver.adjustPriority()` VDEX at codeOff `0x2abde4` |
| Fire-specific resolver ranking condition | `UNKNOWN` | No direct literal/package branch found in selected scan |

The `AMAZON_ADDITION` label here describes an Amazon package/resource choice, not proof that PackageManager resolver code was modified.
