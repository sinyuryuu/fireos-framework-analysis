# Phase 6AI — ProductPolicy / DCPMS static closure

Host-only, offline static closure on 2026-08-10. No adb, broadcast, service call, Binder transaction, profile mutation, or platform setter.

## Result

ProductPolicy external Binder route is negated. productpolicyservice_fosinit.xml only loads com.amazon.android.service.AmazonProductPolicyService. VDEX shows SystemService; onStart only calls publishLocalService(AmazonProductPolicyService.class,this), at fosservices disassembly 0x045b36–0x045b44. No publishBinderService, AIDL, Stub/Proxy, manifest component, or remote transaction. Thus 6AE-005 / 6X2-ROUTES-003 is a trusted system-server local-service capability, not an ordinary-app Binder surface.

A trusted ProductPolicy sink exists: EnableDisableComponentAction.enableDisableComponent(String,int,boolean), offset 0x052642 (disassembly line 293712), calls AmazonPackageManager.setComponentEnabledSetting at 0x052688/0x0526e8 or setApplicationEnabledSetting at 0x052698/0x0526f4. User scope is internal: OnUserSwitchEvent gets UserInfo from event user id and passes UserInfo.id (0x06245c–0x0624d2); mode-changed uses MultipleProfileHelper.getForegroundProfileId (0x052910–0x052918); region/PFM iterate UserInfo.id (0x052960–0x0529e6, 0x052a66–0x052aea). This closes to policy/event-selected user/profile, but exact targets contain no Fire Launcher/HOME/User-0 restoration edge.

A separate boot-only beta-to-user branch writes Settings.Secure.is_beta_build=false and sends package=android android.intent.action.FACTORY_RESET (triggerFactoryReset 0x045ba4–0x045bde; onBootPhase gate 0x04586e–0x045964). This is trusted boot policy, not a Binder caller path.

DCPMS APK SHA-256: 15ca17549bc377360d9213eb95b5e0468d1352839386e1d968bcb25282218997. Four routes terminate as follows:

- PCAActiveProfileReceiver.java:23-27 -> UpdatePCAProfileTypeAndEvalHelper.java:37-57 -> PCA/OS-user or active-app attributes -> evaluator.
- DeviceUserSwitchReceiver.java:47-57 -> UpdateOSUserTypeService.java:19-35 -> helper.java:25-47 -> CDE attributes/evaluator; child clears active-app list.
- AccountPropertyChangeReceiver.java:31-39 -> same OS-user helper; receiver has account-property signature|amazon permission/action.
- GlobalContentSyncEventReceiver.java:16-25 -> GlobalContentSyncEventService.java:23-37 -> ArcusSyncService.syncCDEPolicy.

KeyValueStore.java:12-18 uses device-protected SharedPreferences. CDEAttributesPersistenceService.java:95-147 writes only computed CDE attributes/decision. DeviceExperienceModeEvaluator.java:90-105 persists decision and emits the saved CDE decision broadcast/callback/optional ODOT outputs. No PackageManager HOME/preferred/component-state, SettingsProvider, OTA apply, or recovery edge was found.

Manifest SHA-256: 9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4. DCPMSService is exported/singleUser and has GET_DEVICE_CDE_DECISION permission (xmltree 168-175); saved state is signature|amazon. Account receiver permission is at 94-103; USER_SWITCHED is protected; GLOBAL_SYNC is at 145-153; JobIntentServices use BIND_JOB_SERVICE at 177-207.

DCPMSService.java:124-135 creates ServiceBinder; ServiceBinder.java:63-109 returns the AIDL Stub. IDeviceChildExperienceModeDecisionManager.java has descriptor and transactions 1..3 (14-18,32-75,98-128). Stub only enforceInterface; no getCallingUid/checkCallingPermission/UserHandle/user argument gate. Component permission is the first gate; after it, identity is DCPMS process identity and outputs are decision read/callback only. No clearCallingIdentity/restore edge to a platform sink was found.

SELinux/service-manager: phase6aq/service-context-audit-20260805-03/service-context-matrix.csv and saved AVC index have no ProductPolicy service-context/allow row; fosdebug-service-inventory.txt:22 only lists the vendor-service class. dcpms.xml SHA-256 f17054ab1cd901db06ce39f10595ab36a062f82718b9fcf5490003161ef8f5b0 contains only SDK library/feature, no Binder name or SELinux rule. This matches local-only publication.

## Verdict

| route | caller -> gate -> identity -> scope -> sink | verdict |
|---|---|---|
| 6AI-001 PCA / 6AE-003 / 6X2-ROUTES-002 | exported action -> DCPMS -> device PCA/profile -> CDE prefs/evaluator/notification | CLOSED_NO_PLATFORM_SINK |
| 6AI-002 USER_SWITCHED / 6AE-003 | protected action + singleUser -> DCPMS -> computed OS-user/PCA -> CDE only | CLOSED_NO_PLATFORM_SINK |
| 6AI-003 account / 6AE-004 | signature|amazon action/permission -> DCPMS -> computed OS-user/PCA -> CDE only | CLOSED_NO_PLATFORM_SINK |
| 6AI-004 sync / 6AE-004 | GLOBAL_SYNC permission -> DCPMS -> device CDE remote policy -> CDE sync only | CLOSED_NO_PLATFORM_SINK |
| 6AI-005 ProductPolicy / 6AE-005 | fosinit system-server loader -> no external Binder caller -> local identity -> event user/profile -> PM setters + boot reset | CLOSED_AS_TRUSTED_LOCAL_PATH_NO_EXTERNAL_BINDER |
| 6AI-006 DCPMS AIDL | signature|amazon service permission -> Stub/Proxy read/callback only -> singleUser | CLOSED_BOUNDED_IDENTITY_NO_SENSITIVE_SINK |

Rows 6AI-001..004 duplicate/tighten work/luna_worker_phase6tb_dcpms_consumer_20260810.md/.csv. ProductPolicy duplicates 6AE-005/6X2-ROUTES-003 and work/luna_worker_phase6z_components_20260810.md/.csv, adding exact publication/sink offsets. No ordinary-app caller, Binder confused-deputy, Fire Launcher target, HOME resolver write, or User-0 restoration edge was established.

