# Phase 6SV — exact-build exported component / protected-broadcast inventory

日期：2026-08-10（Asia/Taipei）  
範圍：host-only static review of saved exact-build framework-res、Amazon/Settings/SystemUI/OTA/OOBE manifests、fosinit、permission/sysconfig/SELinux artifacts 與既有 findings。未執行 adb、Binder、broadcast、component start、mutation、OTA/recovery、root 或 exploit。

## 結論

去除已閉合的 `BOOT_AFTER_SYSTEM_OTA`/OOBE、Vending/LauncherConfiguration、SystemUI callback 後，保存 corpus 留下四條真正新的或仍 UNKNOWN 的 exported route。它們都落在 DCPMS 的 CDE/profile policy state，而不是 HOME resolver、PMS preferred activity、Fire Launcher component state 或 OTA/recovery sink：

1. `PCAActiveProfileReceiver`（exported、無 component permission）接受 `com.amazon.device.ACTION_ACTIVE_PROFILE_UPDATED`，由 Intent extras `PROGRAM_ID`/`PACKAGE_NAME` 分支，更新 CDE profile type、OS user type 或 active-app list，並觸發 device-experience evaluation。manifest 未保存 receiver permission；因此 caller authorization / exact producer 仍 UNKNOWN。
2. `DeviceUserSwitchReceiver`（exported、無 component permission）接受 `android.intent.action.USER_SWITCHED`，更新同一組 CDE user/profile attributes 與 child active-app list。`USER_SWITCHED` 在 exact framework-res protected-broadcast inventory 中；故無 permission 不是普通 caller 可達證明。
3. `AccountPropertyChangeReceiver`（exported、singleUser/directBootAware）要求 `com.amazon.dcp.sso.permission.AmazonAccountPropertyService.property.changed`，同樣進入 CDE user/profile persistence/evaluation。該 permission 的 exact protection level/holder 在本次 bounded permission artifacts 未閉合，故保留 UNKNOWN。
4. `GlobalContentSyncEventReceiver`（exported、singleUser）要求 `com.amazon.permission.GLOBAL_SYNC`，將 sync event 轉成 JobIntentService，呼叫 `ArcusSyncService.syncCDEPolicy()`。這是 policy persistence / evaluation route；沒有保存的 HOME、package-state 或 OTA installer sink。`GLOBAL_SYNC` caller/holder 與 policy consumer 的完整 route 仍 UNKNOWN。

這些 route 的 sink 是「static confirmed」，但低權限 caller → accepted authorization → sensitive HOME/package/OTA sink 均未閉合。CDE key/value persistence 不能等同 SettingsProvider、PMS 或 OTA sink。

## Exact-build evidence

主要 manifest 是 `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt`，SHA-256 `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`；union copy hash 相同。Component ranges：

- `AccountPropertyChangeReceiver`: lines 94–103; custom permission and `com.amazon.dcp.sso.action.AmazonAccountPropertyService.property.changed`.
- `DeviceUserSwitchReceiver`: lines 105–113; exported/singleUser/directBootAware, `USER_SWITCHED`, no component permission.
- `PCAActiveProfileReceiver`: lines 115–122; exported/singleUser, `com.amazon.device.ACTION_ACTIVE_PROFILE_UPDATED`, no component permission.
- `GlobalContentSyncEventReceiver`: lines 145–153; exported/singleUser, `com.amazon.permission.GLOBAL_SYNC`, `com.amazon.intent.SYNC`.

The same manifest requests the relevant cross-user/profile and private permissions at lines 22–55 (`INTERACT_ACROSS_USERS(_FULL)`, `MANAGE_USERS`, profile interaction/get-profile, account-property permission, `GLOBAL_SYNC`), but requested permissions are not caller provenance.

### Sink dataflow

`artifacts/phase6it-missing-priv-apps-20260807-01/jadx/sources/com/amazon/dcpms/fos/service/lifecycle/pca/profileswitch/UpdatePCAProfileTypeAndEvalHelper.java` (SHA-256 `6435dc8c9fc5ea68b921f54c124b57809aa702fe1b9bb065801e424732e375d4`) reads `PROGRAM_ID` and `PACKAGE_NAME`; it writes `setComputedDevicePCAProfileType`, `setComputedDeviceOSUserType`, or `setComputedActiveAppList`, then calls `DeviceExperienceModeEvaluator.evaluate()` (lines 20–54). The persistence implementation writes private CDE key/value stores (`CDEAttributesPersistenceService.java`, not a platform SettingsProvider).

`UpdateOSUserTypeAndEvalHelper.java` (SHA-256 `e54679a581777ae9ef84065884b9828fe7e6988e05a986265a31ac61327bfb18`) writes device PCA/profile type, OS user type, and clears active-app list for child mode (lines 25–45). It is reached by both account-property and USER_SWITCHED receivers:

- `AccountPropertyChangeReceiver.java`, SHA-256 `caf69e4e9012637add3057f624d56b38aa74230ab702518b55650f6f519f9263`, lines 17–39.
- `DeviceUserSwitchReceiver.java`, SHA-256 `0e7886d6d87113510891fc5277627ea2f86e6721c9b25542b012f46b4a1ea386`, lines 15–65.

`GlobalContentSyncEventReceiver.java` (SHA-256 `67ce590db5b0a55ebf56faa9520e3195b3bc4ac62026fb48625a020dbbd67320`) enqueues `GlobalContentSyncEventService`; the service (SHA-256 `e3b17a9608e5b0bc4151adbfee9fe485f5ef5f4510b151f7025e49915f8a2cbe`) calls `ArcusSyncService.syncCDEPolicy()` (lines 16–43). This is a policy-sync sink, not an OTA apply/recovery operation.

## Protected/action and policy cross-check

- `USER_SWITCHED` is listed in the exact framework-res protected-broadcast union (`artifacts/phase6bk/protected-broadcast-union-20260810-02/protected-broadcast-inventory.csv`); the framework-res manifest input is `manifests/041_framework-res.xmltree.txt`.
- `com.amazon.dcp.sso.permission.AmazonAccountPropertyService.property.changed` and `com.amazon.permission.GLOBAL_SYNC` are manifest receiver permissions. Their declaration/protection/holder provenance is not fully present in the bounded permission XML, so this report does not label either as signature-level without exact declaration evidence.
- `amazonusermanager_fosinit.xml` (SHA-256 `14ccd432e6393ce1660ad51c10430c392a3562be3ef20ee2bdfe62a2240e8678`) registers `AmazonUserManagerService` and the MultipleProfile settings callback. `fireossystemota_fosinit.xml` (SHA-256 `b2dbc77e6ab6b6ce3ac0d75a1eca49ad9d7f9ce5b448a2a665bb69278d5d09ee`) registers the system-server `VendorRecoverySystemCallback`; these are trusted system-server extension points, not new exported app entrypoints. `amazonpackagemanager_fosinit.xml` registers Amazon PM and protected-package callbacks (SHA-256 `eb53e50cf72174eddcde25fd3538e4736d2cd4cb7866bab4e5bc2b70fc514286`); no new external caller edge was found.
- `framework-sysconfig.xml` only preserves an implicit `PACKAGE_CHANGED` allowlist entry in this scope; no new route from it to the four DCPMS sinks was established. SELinux `plat_service_contexts` labels platform services (`settings`, `package`, `system_update`, `user`, `otadexopt`), but no app-domain allow edge to these DCPMS routes was found in the bounded artifact.

## Explicit exclusions / de-duplication

The OTA controller/boot/sync/deferred/check receivers in `DeviceSoftwareOTA`, OOBE `BootAfterSystemOTAReceiver`, Vending `LauncherConfigurationReceiver`, and SystemUI callback surfaces were inspected only to avoid duplication. Existing Phase 6R/6SD/6SK, 6RX/6SA/6MY, Vending closure, and 6RT findings remain authoritative for those routes; they are not repeated here.

## Boundary

No row proves ordinary-app reachability, permission holder identity, cross-user acceptance, HOME selection, package/component mutation, OTA apply, or recovery execution. The safe interpretation is: four exported DCPMS lifecycle inputs have exact static downstream CDE/policy sinks, with authorization and upstream producer provenance still bounded UNKNOWN where stated.

