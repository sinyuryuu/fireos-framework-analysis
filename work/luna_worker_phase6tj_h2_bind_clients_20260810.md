# Phase 6TJ-A — Amazon Alta/H2ClientService host-only closure

日期：2026-08-10（Asia/Taipei）

## Scope and result

本報告只讀取 phase6mc Alta JADX/static/caller-provenance/permission-holder artifacts、phase6bk manifest/XML-tree、既有 Phase6TF 與相關 source/DEX/manifest；沒有接觸裝置、adb、service call、Binder bind/call、user/settings/package mutation、root/exploit。沒有產生 transaction code 或 exploit payload。

結論：exact service declaration、exported/direct-boot/permission 已由 XML-tree 閉合；production `IH2ClientService` Stub→workflow→user/profile sink 已由 JADX source 閉合。bounded corpus 未找到非 generated `IH2ClientService` production client。custom `BIND_SERVICE` 的 holder/grant、實際 accepted caller、以及低權限可達性沒有足夠檔案證據，保留 UNKNOWN。

## Exact manifest declaration

`com.amazon.alta.h2clientservice.H2ClientService` is declared at `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/017_com.amazon.h2clientservice.xmltree.txt:102-110` (identical hash to phase6bk union `.../028_...:102-110`):

- `android:name="com.amazon.alta.h2clientservice.H2ClientService"`
- `android:permission="com.amazon.alta.h2clientservice.permission.BIND_SERVICE"`
- `android:exported=true`, `android:singleUser=true`, `android:directBootAware=true`
- intent action `com.amazon.alta.h2shared.aidl.IH2ClientService`

The same XML-tree declares `com.amazon.alta.h2clientservice.permission.BIND_SERVICE` at `:69-73` with `android:protectionLevel=0x2` (signature). `Manifest.java:6-9` independently confirms the exact symbolic permission name. This proves the service gate is signature-level; it does not prove which package holds/grants the custom permission.

## Holder/grant and caller closure

`phase6mc-permission-holder-audit-20260810-05/permission-holders.csv` records H2 package UID 10012 and grants for `CHANGE_COMPONENT_ENABLED_STATE`, `MANAGE_USERS`, and `WRITE_SECURE_SETTINGS` (row for `com.amazon.alta.h2clientservice`), while its `summary.json` states that those are package-state observations and do not prove code reachability or signing provenance. It does not enumerate the custom `com.amazon.alta.h2clientservice.permission.BIND_SERVICE` holder/grant. Therefore:

- custom permission declaration/protection: **POSITIVE**;
- custom permission holder/grant: **UNKNOWN**;
- external accepted caller and ordinary-app/shell reachability: **UNKNOWN**;
- no low-privilege caller found in the bounded static corpus: **NEGATIVE (bounded scan only)**, not a proof that no client exists outside the corpus.

`phase6mc-caller-provenance-20260810-01/caller-provenance.csv` records the exported, signature-bound service and says `AbstractAPICall` logs `Binder.getCallingUid()`; it does not show an additional method-local caller gate in the recovered Stub. No identity-clearing edge was used to upgrade reachability. The service process is package UID 10012 in the holder audit, but service process identity is not caller identity.

## Production caller → gate → identity/user scope → sink

`H2ClientService.onBind()` returns `new IH2ClientService.Stub` at `H2ClientService.java:104-107`; method routing is at `:109-267`. The following are static production paths:

1. `IH2ClientService.addUser` (`H2ClientService.java:124-127`) → `AddUserAPICall` → `HouseholdController.createUser` (`AddUserAPICall.java:10-14,29-33`; `HouseholdController.java:323-373`) → `CreateAndroidUserCommand.executeCommand` (`:20-37`) → `AndroidUserHelper.addAndroidUser` (`AndroidUserHelper.java:78-90`) → `AmazonUserManager.createAdultUser/createChildUser`. Gate: service signature permission plus workflow input checks. User scope: household-supplied adult/child profile; `CreateAndroidUserCommand` requires a positive returned Android ID (`:27-32`). Sink is profile lifecycle, not a formal HOME selector. Classification: **POSITIVE** for static chain; caller reachability **UNKNOWN**.

2. `IH2ClientService.removeUserFromDevice` (`H2ClientService.java:226-236`) → `RemoveUserFromDeviceAPICall` → `HouseholdController.removeUserFromDevice` (`HouseholdController.java:635-652`) → `RemoveAndroidUserCommand` (`RemoveAndroidUserCommand.java:16-29`) → `AndroidUserHelper.removeAndroidUser` (`AndroidUserHelper.java:148-156`) → `AmazonUserManager.removeAmazonUser`. Gate: `z=true` produces callback failure at `H2ClientService.java:228-235`; workflow rejects protected Android IDs `<10` at `RemoveAndroidUserCommand.java:32-42`; helper rejects user 0 at `AndroidUserHelper.java:152-156`. User scope: explicit household Android profile ID; user 0 is protected. Classification: **POSITIVE** for static chain; caller reachability **UNKNOWN**.

3. Internal profile-state path: `AndroidUserHelper.setSecureString` → `MultipleProfileHelper.putStringForProfile` (`AndroidUserHelper.java:144-168`) and sorted profile path `setSortedAndroidIds/resetSortedAndroidIds` → `AmazonUserManager.setUserSortedList` (`:159-176`). This is a production sink for per-profile settings/order state, but no direct H2 Stub method-to-sink caller edge or Binder identity gate is established in this bounded evidence. Classification: **UNKNOWN** as an externally reachable H2 route; internal production sink presence is **POSITIVE**.

No bounded H2 source evidence reaches `setComponentEnabledSetting`, `setApplicationEnabledSetting`, preferred HOME, or Fire Launcher selection. This is a negative bounded scan result, not an assertion about code outside the recovered APK/source corpus.

## Non-generated client inventory

The exact Alta JADX source has the generated AIDL contract at `com/amazon/alta/h2shared/aidl/IH2ClientService.java:4-710` and the sole recovered implementation at `H2ClientService.java:104-267`. Corpus-wide static search over the specified artifacts/source/work evidence found no additional production source file that implements or binds `IH2ClientService`; receiver references to `H2ClientService` are internal start/sync paths, not clients. Result: **NEGATIVE (bounded corpus)**. Do not infer absence outside these artifacts.

## Evidence hashes

| evidence | SHA-256 |
|---|---|
| phase6bk expanded H2 XML-tree | `f14670a78cdbddf4c46375d78e1607fe491c33fd4d807de57abfe5e2b5300242` |
| phase6mc caller provenance | `fbb4f21dad1c3948bb3748fe7bcf652b6b136a6fb07e62cb4e7d7e6d51e1b11d` |
| phase6mc permission holders | `1f97fa825f8b7cd86f05653259ecf43359d496d15af4e21e0c53512274ebdb18` |
| H2ClientService.java | `a4d9635e5f3138ecc0eeaddbfa5d06f10f46651dd6925bac991c7ce8937bd1ba` |
| IH2ClientService.java | `33a17bb1f799b957be3e5545508f3f8e34c954eb140ee25d0bb72b2724fc3014` |

## Next safe step

Host-only: if additional preserved exact-build APK/source/manifest artifacts exist, repeat the bounded client inventory and custom-permission holder/signature mapping. Do not bind/call the service, construct parcels, guess transaction codes, or mutate user/settings/package state.
