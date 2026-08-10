# Phase 6X2 evidence index

Each row below is normalized from a preserved CSV. Empty caller/gate/identity/sink fields are intentional UNKNOWNs; they are not inferred.

## WG-001
- Source: `work/luna_worker_phase6wg_ipc_residual_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: external dumpsys caller subject to DUMP; exact UID UNKNOWN
- Gate: android.permission.DUMP checked in dump; service-manager/SELinux rule UNKNOWN
- Identity/user scope: device/default settings user (explicit user overload absent)
- Sink: FireOsDisplayPowerControllerService$BinderService
- Observed effect: UNKNOWN
- Confidence: **static direct**
- Status: `UNKNOWN`

## WG-002
- Source: `work/luna_worker_phase6wg_ipc_residual_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: system_server input-monitor caller/publisher; external Binder caller not recovered
- Gate: system_server/internal callback; permission and SELinux/service-manager gate UNKNOWN
- Identity/user scope: system/default secure-settings scope (non-user overload)
- Sink: InputFilterMonitorInputManagerServiceCallback
- Observed effect: UNKNOWN
- Confidence: **static direct**
- Status: `UNKNOWN`

## WG-003
- Source: `work/luna_worker_phase6wg_ipc_residual_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: remote Binder caller with MODE_SWITCH; exact UID UNKNOWN
- Gate: com.amazon.alexa.permission.MODE_SWITCH enforced by checkCallingOrSelfPermission; service-manager/SELinux rule UNKNOWN
- Identity/user scope: USER_CURRENT/-2 passed to putIntForUser
- Sink: AlexaModeSwitchManagerService$AlexaModeSwitchAPIImpl
- Observed effect: UNKNOWN
- Confidence: **static direct**
- Status: `UNKNOWN`

## 6WL-ROW-004
- Source: `work/luna_worker_phase6wh_ota_residual_20260810.csv`
- Evidence file: `artifacts/phase6mk-updater-dispatch-20260810-04/registration-dispatch.csv:7,16,19-22; updater-script-entrypoints.csv:2-13; addresses 0x406b8c,0x406e0c,0x406ee4,0x406f2c,0x406f6c,0x406fac`
- SHA-256: `d88e35ec08d9ef0a55a3dbc17dc430b62d3b419810653542b6dd3077095cca24;4d0128ee85eec7b0c88716012858bef699f740907e46e854939c83a6c9e99077`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: NONE
- Confidence: **UNKNOWN**
- Status: `UNKNOWN`

## 6WL-ROW-005
- Source: `work/luna_worker_phase6wh_ota_residual_20260810.csv`
- Evidence file: `artifacts/phase6ne-updater-cache-flow-20260810-03/direct-call-edges.csv:1-5,42-43; addresses 0x417bf0,0x417ea8,0x417eb0,0x409cb4,0x409cdc`
- SHA-256: `d653e4a84898509781a333c56502087a83981781fcf6612d7026bfd79602b477`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: NONE
- Confidence: **UNKNOWN**
- Status: `UNKNOWN`

## 6WL-ROW-006
- Source: `work/luna_worker_phase6wh_ota_residual_20260810.csv`
- Evidence file: `artifacts/phase6my-bootafter-ota-package-helper-20260810-01/call-edges.csv:6MY-E03-E04,E08,E10`
- SHA-256: `1136d4815ae63011522fead17ef743bc0daa57334ae6ebb3b4c05c1d09507c52`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: NONE
- Confidence: **UNKNOWN**
- Status: `UNKNOWN`

## 6WL-ROW-007
- Source: `work/luna_worker_phase6wh_ota_residual_20260810.csv`
- Evidence file: `artifacts/phase6j/phase6j-ota-controller-holders-20260805-01/controller-permission-context.txt:10537-10541,27271-27275`
- SHA-256: `d68768263846c87ffc6b1b1d100b5b5bcd34212d5605c4e3eb1085da8c67d1e0`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: NONE
- Confidence: **UNKNOWN**
- Status: `UNKNOWN`

## 6WL-ROW-008
- Source: `work/luna_worker_phase6wh_ota_residual_20260810.csv`
- Evidence file: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/dcp/ota/SideloadMover.java:31-44; FileHelper.java:305-339`
- SHA-256: `59131cf032d8544cd44ea839ad63eb37993d2853b4925bf56d10ede721693f63;55a7f44a70735626be7ebde25e96812346f336fddbec2c87ca0fb709b980`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: NONE
- Confidence: **UNKNOWN**
- Status: `UNKNOWN`

## 6WL-ROW-009
- Source: `work/luna_worker_phase6wh_ota_residual_20260810.csv`
- Evidence file: `firmware/extracted/PS7331/vbmeta.img absent; firmware/extracted/PS7331/META-INF/com/android/avb* absent; UpdateSystemWrapper.java:33-44`
- SHA-256: `c99f6884fa298546b18722a5addb46ae35aff4c9f6003d8ad3ccaebe2edfdbd9`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: NONE
- Confidence: **UNKNOWN**
- Status: `UNKNOWN`

## WI-01
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `cmdq_driver.c=b3a54d37b4e498ff969a2717cb02cefc923ae6f39da32f5fd8529fe3dce6e899; kernel.config=eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04; Image=10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d; vendor_file_contexts=db5cd91b8d25170ad27809ace8cdbbd2a3f838ec72e2598a4f6b5a44953d322e`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: policy names device type only; no exact caller identity or framework/HOME/package sink
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **UNKNOWN**
- Status: `UNKNOWN`

## WI-02
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `ion.c=abac518864faed94439d75d204e8c16ea75cf3a74c93ee50e128e0f6928a6d63; kernel.config=eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04; vendor_file_contexts=db5cd91b8d25170ad27809ace8cdbbd2a3f838ec72e2598a4f6b5a44953d322e; native-inventory.csv=9d1313d25cb45492d5656d03f05b7e60f5d037ccef15c20d9edec5e0fdbf17f9`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: ION library labels are same_process_hal_file; no exact identity and no package/HOME/settings sink
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **UNKNOWN**
- Status: `UNKNOWN`

## WI-03
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `boot.img=cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b; Image=10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d; native-inventory.csv=9d1313d25cb45492d5656d03f05b7e60f5d037ccef15c20d9edec5e0fdbf17f9`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: no userland identity or sensitive sink identified
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **UNKNOWN**
- Status: `UNKNOWN`

## WI-04
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `amzn_idme.c=ab6484ae7a694412ec4eeabb67133ddd0c0af221076b6d989c8ab1fe7c84e61e; kernel.config=eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04; vendor_file_contexts=db5cd91b8d25170ad27809ace8cdbbd2a3f838ec72e2598a4f6b5a44953d322e`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: HAL service identity is privileged-domain context only; no exact package/HOME/PMS sink
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **UNKNOWN**
- Status: `UNKNOWN`

## WI-05
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `amzn_drv_test.c=6c2309f996cacafaab35cce3935bcb725a5259211751af89df88d3732797029e; libmt8183_diag.so=7147e161de7b3a8097bdf6079d0b414c147067d46e1f446138d041a63dd127d7; vendor_sepolicy.cil=82430bdb87b8a5f653110b635289489b99e82bdbe7bdc7a2e1ee5564e674e035`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: diagnostic HAL/domain name is not a proc caller and no package/HOME/privilege sink is joined
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **UNKNOWN**
- Status: `UNKNOWN`

## WI-06
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `vendor_file_contexts=db5cd91b8d25170ad27809ace8cdbbd2a3f838ec72e2598a4f6b5a44953d322e; vendor_sepolicy.cil=82430bdb87b8a5f653110b635289489b99e82bdbe7bdc7a2e1ee5564e674e035`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: rpmb_svc identity is a service observation; no package/HOME sink
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **UNKNOWN**
- Status: `UNKNOWN`

## WI-07
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `phase6me input-manifest=ada254be9c56572282704924eea66e2852889ec73c0a65be4558f36f77d8250a; native-inventory.csv=9d1313d25cb45492d5656d03f05b7e60f5d037ccef15c20d9edec5e0fdbf17f9; vendor_file_contexts=db5cd91b8d25170ad27809ace8cdbbd2a3f838ec72e2598a4f6b5a44953d322e`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: HAL/service identity only; no package/HOME/settings sink
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **UNKNOWN**
- Status: `UNKNOWN`

## WJ-01
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: Saved resolver evidence remains Fire Launcher; static HOME setters/sinks do not establish ordinary caller reachability or a sustainable replacement.
- Confidence: **UNKNOWN**
- Status: `INTEGRATED`

## WJ-02
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: Package-state writers exist in framework/Amazon code, but saved gates rejected ordinary mutation and no writer is shown to reach User-0 HOME sustainably.
- Confidence: **UNKNOWN**
- Status: `INTEGRATED`

## WJ-03
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: Child/profile lifecycle and KFT component changes are real only for the target child/profile; final guards preserve User-0 Fire Launcher.
- Confidence: **UNKNOWN**
- Status: `INTEGRATED`

## WJ-04
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: DPM tests show bounded owner/admin behavior but no ordinary sustainable HOME/package-state route; static DPM sinks remain gated and caller identity is incomplete.
- Confidence: **UNKNOWN**
- Status: `INTEGRATED`

## WJ-05
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: Resource/default-home and overlay evidence does not prove runtime selection; no settings mutation or durable HOME change is established.
- Confidence: **UNKNOWN**
- Status: `INTEGRATED`

## WJ-06
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: Service visibility/candidate interfaces and static sinks do not establish a callable transaction or accepted identity; H2 holder/grant/requester remains incomplete.
- Confidence: **UNKNOWN**
- Status: `INTEGRATED`

## WJ-07
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: Exact OTA and native updater paths contain partition/cache writers statically, but no updater, recovery, OTA, reboot, or partition effect was observed.
- Confidence: **UNKNOWN**
- Status: `INTEGRATED`

## WJ-08
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: Driver and native control edges are host-side static/conditional evidence only; retail node access, process/domain load, and effect are not established.
- Confidence: **UNKNOWN**
- Status: `INTEGRATED`

## WJ-09
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: Source/config/probe logs do not close a retail privilege transition or sensitive sink; no approved device mutation is present.
- Confidence: **UNKNOWN**
- Status: `INTEGRATED`

## WJ-10
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: Tahoe/KFT/Launcher3 and accessibility/ADB foreground paths are either child-scoped or temporary; none is a sustainable User-0 formal HOME replacement.
- Confidence: **UNKNOWN**
- Status: `INTEGRATED`

## WK-001
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `186a710bb9d27f703f2c76bc1e179ac18cebbff022674e9e71f2bf7a50226327`
- Caller: DefaultPermissionGrantPolicy
- Gate: system_server/internal policy path; exact caller gate UNKNOWN
- Identity/user scope: userId argument
- Sink: DefaultPermissionGrantPolicy
- Observed effect: UNKNOWN
- Confidence: **static direct**
- Status: `UNKNOWN`

## WK-002
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `a92e54ac19e886b935b547717827ccf018d1caa554b8ecaf8467b6077d7d309e`
- Caller: UserManagerService Binder implementation
- Gate: checkManageOrCreateUsersPermission(flags); MANAGE_USERS or CREATE_USERS; system/root accepted
- Identity/user scope: system/default user scope
- Sink: UserManagerService
- Observed effect: UNKNOWN
- Confidence: **static direct**
- Status: `UNKNOWN`

## WK-003
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `a92e54ac19e886b935b547717827ccf018d1caa554b8ecaf8467b6077d7d309e`
- Caller: UserManagerService Binder implementation
- Gate: checkManageOrCreateUsersPermission(flags); MANAGE_USERS or CREATE_USERS; system/root accepted
- Identity/user scope: parent userId plus created profile
- Sink: UserManagerService
- Observed effect: UNKNOWN
- Confidence: **static direct**
- Status: `UNKNOWN`

## WK-004
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `a92e54ac19e886b935b547717827ccf018d1caa554b8ecaf8467b6077d7d309e`
- Caller: UserManagerService Binder implementation
- Gate: checkManageOrCreateUsersPermission("Only the system can remove users"); exact downstream checks UNKNOWN
- Identity/user scope: userHandle argument
- Sink: UserManagerService
- Observed effect: UNKNOWN
- Confidence: **static direct**
- Status: `UNKNOWN`

## WK-005
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `3382de2f12fc0f38c757c3fd021c06482db96c19389ec9909218423addd47274`
- Caller: UserController Binder-facing path
- Gate: INTERACT_ACROSS_USERS_FULL or amazon.aosp.permission.INTERACT_ACROSS_USERS_FULL; Binder calling pid/uid checked; shell restriction also enforced
- Identity/user scope: userId; system user rejected
- Sink: UserController
- Observed effect: UNKNOWN
- Confidence: **static direct**
- Status: `UNKNOWN`

## WK-006
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `7aafaa0ccc5336df4f8e8cb7bcd38afbd578790c3065f28843a76a1eb36c06cc`
- Caller: ActivityManagerShellCommand
- Gate: shell command plus canSwitchUsers restriction; exact shell UID enforcement in downstream path UNKNOWN
- Identity/user scope: supplied target user
- Sink: ActivityManagerShellCommand
- Observed effect: UNKNOWN
- Confidence: **static direct**
- Status: `UNKNOWN`

## WK-007
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `7aafaa0ccc5336df4f8e8cb7bcd38afbd578790c3065f28843a76a1eb36c06cc`
- Caller: ActivityManagerShellCommand
- Gate: shell command path; downstream caller and SELinux gate UNKNOWN
- Identity/user scope: supplied target user
- Sink: ActivityManagerShellCommand
- Observed effect: UNKNOWN
- Confidence: **static direct**
- Status: `UNKNOWN`

## WK-008
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `7aafaa0ccc5336df4f8e8cb7bcd38afbd578790c3065f28843a76a1eb36c06cc`
- Caller: ActivityManagerShellCommand
- Gate: shell command path; downstream INTERACT_ACROSS_USERS_FULL gate visible in UserController
- Identity/user scope: supplied target user
- Sink: ActivityManagerShellCommand
- Observed effect: UNKNOWN
- Confidence: **static direct**
- Status: `UNKNOWN`

## WK-009
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `107ba7f2925439e8bf061b39b9496a5d6cc661c00990d5be9259104f2960486f`
- Caller: AppRestrictionsHelper
- Gate: PackageManager validation; Settings UI/profile-policy caller and SELinux rule UNKNOWN
- Identity/user scope: explicit userId
- Sink: AppRestrictionsHelper
- Observed effect: UNKNOWN
- Confidence: **static direct**
- Status: `UNKNOWN`

## WK-010
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `107ba7f2925439e8bf061b39b9496a5d6cc661c00990d5be9259104f2960486f`
- Caller: AppRestrictionsHelper
- Gate: PackageManager uninstall validation; only restricted-profile branch visible
- Identity/user scope: explicit userId
- Sink: AppRestrictionsHelper
- Observed effect: UNKNOWN
- Confidence: **static direct**
- Status: `UNKNOWN`

## WK-011
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `1e15d3461b6d0e34391eba9b628e8ca83a7082590baf33bfec4ad8d00e5209df`
- Caller: UserManagerHelper
- Gate: helper checks no_add_user restriction; service permission gate remains authoritative
- Identity/user scope: current process/default user scope
- Sink: UserManagerHelper
- Observed effect: UNKNOWN
- Confidence: **static direct**
- Status: `UNKNOWN`

## WK-012
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `1e15d3461b6d0e34391eba9b628e8ca83a7082590baf33bfec4ad8d00e5209df`
- Caller: UserManagerHelper
- Gate: helper excludes system/current-user case; service permission gate remains authoritative
- Identity/user scope: userInfo.id
- Sink: UserManagerHelper
- Observed effect: UNKNOWN
- Confidence: **static direct**
- Status: `UNKNOWN`

## WK-013
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `1e15d3461b6d0e34391eba9b628e8ca83a7082590baf33bfec4ad8d00e5209df`
- Caller: UserManagerHelper
- Gate: helper checks current/foreground user only; downstream switch gate and SELinux rule UNKNOWN
- Identity/user scope: target user id
- Sink: UserManagerHelper
- Observed effect: UNKNOWN
- Confidence: **static direct**
- Status: `UNKNOWN`

## WK-014
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `4efc2aba8f7798fb4e026f13479f5b4929ef545deba5618b35d799555d78678b`
- Caller: external callers through exported SettingsProvider
- Gate: global/secure writes enforce WRITE_SECURE_SETTINGS; system writes use WRITE_SETTINGS or app-op; cross-user gate at 431
- Identity/user scope: calling user and requested setting namespace
- Sink: SettingsProvider
- Observed effect: UNKNOWN
- Confidence: **static direct**
- Status: `UNKNOWN`

## WK-015
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `e4f2d9d47e7fa10be2aa2d26f6549b41184762d7ff5c77c19ffa7fc7560aac70`
- Caller: SettingsProvider
- Gate: android:exported=true; sharedUserId=android.uid.system; provider write methods enforce permissions
- Identity/user scope: singleUser across users
- Sink: SettingsProvider
- Observed effect: UNKNOWN
- Confidence: **static manifest**
- Status: `UNKNOWN`

## WK-016
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `58ce4931e266384bd63147b65748edb53190d68f270b0b324dfa5c646506d5af`
- Caller: MediaSessionService
- Gate: internal service path; exact caller/permission and SELinux rule UNKNOWN
- Identity/user scope: full user id
- Sink: MediaSessionService
- Observed effect: UNKNOWN
- Confidence: **static direct**
- Status: `UNKNOWN`

## WK-017
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `a92e54ac19e886b935b547717827ccf018d1caa554b8ecaf8467b6077d7d309e`
- Caller: UserManagerService
- Gate: system_server internal; file path, DAC, SELinux and caller gate UNKNOWN
- Identity/user scope: user list and user state
- Sink: UserManagerService
- Observed effect: UNKNOWN
- Confidence: **static file sink**
- Status: `UNKNOWN`

## WF-POL-001
- Source: `UNKNOWN`
- Evidence file: `artifacts/phase6wf-product-policy-readonly-20260810-01/global_policy.xml`
- SHA-256: `2cc60c0ee80bbba2752671b7323e2bdaae8f87125b7251726f821906f58087e2`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: none; read-only
- Confidence: **UNKNOWN**
- Status: `CONFIRMED_NO_ENTRY`

## WF-POL-002
- Source: `UNKNOWN`
- Evidence file: `artifacts/phase6wf-product-policy-readonly-20260810-01/common_device_policy.xml`
- SHA-256: `75c7919d2006fc0b088996cd2048b927c419b03ca025a95b20ff31e3de9868aa`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: none; read-only
- Confidence: **UNKNOWN**
- Status: `CONFIRMED_NO_ENTRY`

## WF-POL-003
- Source: `UNKNOWN`
- Evidence file: `artifacts/phase6wf-product-policy-readonly-20260810-01/multimodal_device_policy.xml`
- SHA-256: `66f05c0e0f502e6db191904ec39be5e5b6302905f00cdacfc8a29ef327089512`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: none; read-only
- Confidence: **UNKNOWN**
- Status: `CONFIRMED_NO_ENTRY`

## WF-POL-004
- Source: `UNKNOWN`
- Evidence file: `artifacts/phase6wf-product-policy-readonly-20260810-01/receiver_filter_policy.xml`
- SHA-256: `c3a80bcd0b52250aaa72bd863ae6a633f3153df646ffc57682972bc7c39fab8c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: none; read-only
- Confidence: **UNKNOWN**
- Status: `CONFIRMED_NOT_HOME_WRITER`

## WF-POL-005
- Source: `UNKNOWN`
- Evidence file: `artifacts/phase6wf-product-policy-readonly-20260810-01/device_policy_paths.txt`
- SHA-256: `fee33721f9ea80bb151b2fb04b58de4d9e846a1de68c7c994f6e7416d217fe07`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: none; pull failed with ENOENT
- Confidence: **UNKNOWN**
- Status: `UNKNOWN_LAYOUT_MISMATCH`

## KX-IPC-001
- Source: `AmazonKeyguardService$2.dismissWithPendingIntent; fosservices disassembly lines 168487-168535; boot-fosframework Proxy lines 391141-391186`
- Evidence file: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log; decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c; fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`
- Caller: Binder caller UID from Binder.getCallingUid(); verified default package resolved from that UID
- Gate: checkUidPermission(android.permission.CONTROL_KEYGUARD) OR checkUidPermission(com.amazon.permission.AMAZON_CONTROL_KEYGUARD) in checkKeyguardPermissions; exact permission protection level and service-manager/SELinux gate UNKNOWN
- Identity/user scope: caller UID is retained and forwarded with verified package; no clearCallingIdentity/restoreCallingIdentity observed; target PendingIntent arguments are caller-supplied but downstream SystemUI receives verified UID/package
- Sink: IAmazonKeyguardServiceSystemUI.dismissWithPendingIntent; SystemUI keyguard dismissal/PendingIntent flow
- Observed effect: Static implementation confirms a privileged SystemUI/keyguard sink; no runtime success, HOME selection, package-state mutation, or exploit is established
- Confidence: **High static**
- Status: `NEW_DIFFERENCE_STATIC_ONLY`

## KX-IPC-002
- Source: `AmazonKeyguardService$2.setAccessibilityInfo; fosservices disassembly lines 168690-168730; boot-fosframework Proxy lines 391292-391321`
- Evidence file: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log; decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c; fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`
- Caller: Binder caller UID from Binder.getCallingUid(); verified default package resolved from that UID
- Gate: checkUidPermission(android.permission.CONTROL_KEYGUARD) OR checkUidPermission(com.amazon.permission.AMAZON_CONTROL_KEYGUARD) in checkKeyguardPermissions; exact protection level and service-manager/SELinux gate UNKNOWN
- Identity/user scope: caller UID and verified package are forwarded to SystemUI; no identity clear observed; user ID is not explicit in the public method signature
- Sink: IAmazonKeyguardServiceSystemUI.setAccessibilityInfo; keyguard accessibility metadata/list state
- Observed effect: Static SystemUI state sink only; no runtime reachability, arbitrary package acceptance, HOME effect, or exploit is established
- Confidence: **High static**
- Status: `NEW_DIFFERENCE_STATIC_ONLY`

## KX-IPC-003
- Source: `AmazonKeyguardService$2.setForegroundColor; fosservices disassembly lines 168732-168795; boot-fosframework Proxy lines 391322-391349`
- Evidence file: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log; decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c; fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`
- Caller: Binder caller UID from Binder.getCallingUid(); verified default package resolved from that UID
- Gate: checkUidPermission(android.permission.CONTROL_KEYGUARD) OR checkUidPermission(com.amazon.permission.AMAZON_CONTROL_KEYGUARD) in checkKeyguardPermissions; exact protection level and service-manager/SELinux gate UNKNOWN
- Identity/user scope: caller UID and verified package are forwarded to SystemUI; no identity clear observed; user ID is not explicit in the public method signature
- Sink: IAmazonKeyguardServiceSystemUI.setForegroundColor; keyguard foreground color/presentation state
- Observed effect: Static SystemUI presentation sink only; no runtime reachability, arbitrary caller acceptance, HOME effect, or exploit is established
- Confidence: **High static**
- Status: `NEW_DIFFERENCE_STATIC_ONLY`

## 6X-OTA-01
- Source: `7.3.3.1 adjacent OTA manifest`
- Evidence file: `firmware/manifests/OTA-20260803-01/README.md:1-30`
- SHA-256: `3b7971859d4df3b85a671ab5340d3ad9bb2efb8501c2f09ec71374ac74abf7a5`
- Caller: OTA privileged lifecycle is not established by this file alone
- Gate: manifest metadata records product/version/key_type; no runtime install gate is exercised
- Identity/user scope: PS7331.4463N package identity only; installed baseline is PS7330.4104N; runtime UID/SELinux UNKNOWN
- Sink: No caller-to-writer inference; no exact installed-build post-install or rollback sink
- Observed effect: NONE
- Confidence: **high**
- Status: `excluded_adjacent_version`

## 6X-OTA-02
- Source: `selected/compiled-02 debugfs-derived manifests`
- Evidence file: `firmware/extracted/PS7331/selected/extraction-manifest.tsv:1-10; firmware/extracted/PS7331/compiled-02/extraction-manifest.tsv:1-12`
- SHA-256: `b098f85287a729d03cfac1ac6f767a3ba6a15ce8c65d7f9e581cbbed75448a74;7da7040b4c7454084d8c30452edc05d4c68ce3813fe20700d4016036e4097716`
- Caller: No installer/recovery caller; extraction is host-side
- Gate: file list and per-output SHA-256 only; no package signature, recovery, or execution gate
- Identity/user scope: Derived artifact identity only; runtime process/UID/SELinux UNKNOWN
- Sink: Framework/APK/VDEX outputs are analysis inputs, not post-install/native writer execution
- Observed effect: NONE
- Confidence: **high**
- Status: `excluded_host_derived`

## 6X-OTA-03
- Source: `existing Phase 6WH/6SD/6SP/6VB static corpus`
- Evidence file: `work/luna_worker_phase6wh_ota_residual_20260810.csv:2-7`
- SHA-256: `d88e35ec08d9ef0a55a3dbc17dc430b62d3b419810653542b6dd3077095cca24;4d0128ee85eec7b0c88716012858bef699f740907e46e854939c83a6c9e99077;d653e4a84898509781a333c56502087a83981781fcf6612d7026bfd79602b477;1136d4815ae63011522fead17ef743bc0daa57334ae6ebb3b4c05c1d09507c52;c99f6884fa298546b18722a5addb46ae35aff4c9f6003d8ad3ccaebe2edfdbd9`
- Caller: Privileged OTA lifecycle and recovery context are capability candidates; ordinary app/shell caller not shown
- Gate: metadata/hash/recovery-verification/controller gates precede handoff; indirect dispatch and complete caller join UNKNOWN
- Identity/user scope: UpdateSystem/recovery UID, SELinux domain, AVB rollback authority, and exact user scope UNKNOWN
- Sink: Edify extraction/block-image/cache/readlink paths reach high-privilege file/partition capability statically
- Observed effect: NONE
- Confidence: **high**
- Status: `duplicate_no_new_gap`

## 6X-OTA-04
- Source: `existing Java/native staging and cache evidence`
- Evidence file: `work/luna_worker_ota_canonicalization_provenance_20260810.md:1-34`
- SHA-256: `4d6bc6518f8f45773ac517225d33e9f990ed1de5c590c2b68bf827482e057e64`
- Caller: SideloadMover/MakeFreeSpaceOnCache are static callers only; external input provenance UNKNOWN
- Gate: basename staging, rename/copy-delete fallback, readlink/unlink/free-space helpers; no proven no-follow/atomicity gate
- Identity/user scope: Path owner, race semantics, helper return dataflow, and writer identity UNKNOWN
- Sink: Potential staging/cache and native writer capability remains bounded; no arbitrary-path write established
- Observed effect: NONE
- Confidence: **high**
- Status: `duplicate_unknown_boundary`

## 6XG-001
- Source: `kernel/mediatek/mt8183/4.4/drivers/input/misc/uinput.c:909-933; source SHA-256 98b41492311d9b9fb9ccbfe269a2fddc0fb436f3048b7887e1f6e5482d36211`
- Evidence file: `firmware/extracted/PS7331-SOURCE-20250617/platform.tar member kernel/mediatek/mt8183/4.4/drivers/input/misc/uinput.c`
- SHA-256: `98b41492311d9b9fb9ccbfe269a2fddc0fb436f3048b7887e1f6e5482d36211a`
- Caller: uinput_fops: read, write, unlocked_ioctl, compat_ioctl; misc_register
- Gate: CONFIG_INPUT_UINPUT=y (artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config:2146); no capable()/credential gate in inspected uinput source; final node mode/SELinux not joined
- Identity/user scope: No exact shipped native ELF open/write/ioctl callsite; package and UID/domain not established
- Sink: Synthetic input device creation and event injection into the kernel input graph; no direct PMS/HOME writer in scoped source
- Observed effect: Source capability is confirmed; shipped caller/reachability and package effect are not established
- Confidence: **high source, low caller**
- Status: `NEW_SOURCE_EVIDENCE`

## 6XG-002
- Source: `kernel/mediatek/mt8183/4.4/drivers/power/power_supply_sysfs.c:34-39,115-136,238-263; source SHA-256 54409386286849db4768d1b013b0151c3b8e52d3c5b4e434b52d8881364cc38e`
- Evidence file: `firmware/extracted/PS7331-SOURCE-20250617/platform.tar member kernel/mediatek/mt8183/4.4/drivers/power/power_supply_sysfs.c`
- SHA-256: `54409386286849db4768d1b013b0151c3b8e52d3c5b4e434b52d8881364cc38e`
- Caller: POWER_SUPPLY_ATTR store; power_supply_store_property -> power_supply_set_property
- Gate: CONFIG_POWER_SUPPLY=y; attributes are read-only by default and gain S_IWUSR only when psy->desc->property_is_writeable(psy, property)>0; no SELinux/domain caller join
- Identity/user scope: No exact shipped native sysfs write caller, package, UID, or domain established
- Sink: Battery/charger power-supply property mutation when the provider advertises a writable property; no package/HOME sink shown
- Observed effect: Generic source writer with provider callback gate; shipped path and caller unknown
- Confidence: **high source, low caller**
- Status: `NEW_SOURCE_EVIDENCE`

## 6XG-003
- Source: `kernel/mediatek/mt8183/4.4/drivers/char/rpmb/rpmb-mtk.c:2364-2544,2732-2764; source SHA-256 a6b070190ad8b97173c129509e6d8f8ae8c9f0d383bc349be44d9c919387c8d5`
- Evidence file: `firmware/extracted/PS7331-SOURCE-20250617/platform.tar member kernel/mediatek/mt8183/4.4/drivers/char/rpmb/rpmb-mtk.c`
- SHA-256: `a6b070190ad8b97173c129509e6d8f8ae8c9f0d383bc349be44d9c919387c8d5`
- Caller: rpmb_fops: open, release, unlocked_ioctl; .write=NULL; .read=NULL; cdev_add/device_create with RPMB_NAME
- Gate: CONFIG_RPMB=y; CONFIG_RPMB_INTF_DEV is not set in merged kernel.config:2235-2237; no local capable() proof; TEE/authentication is downstream, not a userspace identity proof
- Identity/user scope: Existing rpmb_svc process evidence does not identify a native open/ioctl callsite or package/UID; no ordinary-app caller established
- Sink: Authenticated persistent RPMB read/write/counter operations are available only through ioctl path in this fops; direct read/write file operations are source-negated
- Observed effect: Precise negative for read/write fops; ioctl sink remains source-only with caller/node ownership unresolved
- Confidence: **high source, medium classification**
- Status: `PRECISE_NEGATIVE_PLUS_SOURCE`

## 6XG-004
- Source: `platform archive member listing: no vendor/mediatek path; Amazon source is device/amazon/kernel/driver; kernel MediaTek tree is kernel/mediatek/...`
- Evidence file: `firmware/extracted/PS7331-SOURCE-20250617/platform.tar`
- SHA-256: `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd`
- Caller: No source registration/API because path is absent
- Gate: Archive-level path absence; do not infer that a separate vendor tree is kernel build provenance
- Identity/user scope: No caller/package/UID can be assigned to an absent path
- Sink: No driver sink attributable to absent vendor/mediatek path; any vendor ELF/policy linkage requires an exact manifest/build reference
- Observed effect: Exact negative only; no reachability or vulnerability claim
- Confidence: **high for archive path negative**
- Status: `PRECISE_NEGATIVE`

## 6XG-005
- Source: `Existing exact-build native inventory and extracted vendor policy were scanned for a path-specific /dev/uinput caller and uinput node type/allow; no tuple found`
- Evidence file: `artifacts/phase5/phase5cs-native-analysis-20260804-01/native-inventory.csv`
- SHA-256: `9d1313d25cb45492d5656d03f05b7e60f5d037ccef15c20d9edec5e0fdbf17f9`
- Caller: No exact shipped ELF open/write/ioctl caller; no uinput-specific file-context/allow tuple identified in bounded artifacts
- Gate: Inventory/policy absence is a negative join only; it does not prove node absence or denial
- Identity/user scope: No package, UID, or SELinux domain established
- Sink: No confirmed input-injection or package/HOME effect from shipped native code
- Observed effect: Precise negative for caller/policy closure; source capability remains 6XG-001
- Confidence: **medium**
- Status: `PRECISE_NEGATIVE`

## 6Y-001
- Source: `android.amazon.perm declares com.amazon.tv.developer.sdk.personalization.USE_SDK`
- Evidence file: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- SHA-256: `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`
- Caller: unknown/no bounded requester
- Gate: manifest declaration only; no service-side check joined; protection=0x0 (normal)
- Identity/user scope: owner android.amazon.perm sharedUserId=android.uid.system; holder/grant not established
- Sink: none joined in bounded exact manifests/disassembly
- Observed effect: no observed effect; low protection is a static candidate only
- Confidence: **high declaration; low reachability**
- Status: `NEW_STATIC_LOW_PROTECTION_NO_SINK`

## 6Y-002
- Source: `android.amazon.perm declares com.amazon.tv.developer.sdk.content.USE_SDK`
- Evidence file: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- SHA-256: `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`
- Caller: unknown/no bounded requester
- Gate: manifest declaration only; no service-side check joined; protection=0x0 (normal)
- Identity/user scope: owner android.amazon.perm sharedUserId=android.uid.system; holder/grant not established
- Sink: none joined in bounded exact manifests/disassembly
- Observed effect: no observed effect; low protection is a static candidate only
- Confidence: **high declaration; low reachability**
- Status: `NEW_STATIC_LOW_PROTECTION_NO_SINK`

## 6Y-003
- Source: `android.amazon.perm declares com.amazon.mw.permission.PLUGIN`
- Evidence file: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- SHA-256: `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`
- Caller: unknown/no bounded requester
- Gate: manifest declaration only; no service-side check joined; protection=0x1 (dangerous)
- Identity/user scope: owner android.amazon.perm sharedUserId=android.uid.system; holder/grant not established
- Sink: none joined in bounded exact manifests/disassembly
- Observed effect: no observed effect; dangerous protection is a static candidate only
- Confidence: **high declaration; low reachability**
- Status: `NEW_STATIC_LOW_PROTECTION_NO_SINK`

## 6Y-004
- Source: `android.amazon.perm declares com.amazon.mw.permission.PLUGIN_CONSUMER`
- Evidence file: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- SHA-256: `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`
- Caller: unknown/no bounded requester
- Gate: manifest declaration only; no service-side check joined; protection=UNKNOWN (no protectionLevel attribute in bounded declaration)
- Identity/user scope: owner android.amazon.perm sharedUserId=android.uid.system; holder/grant not established
- Sink: none joined in bounded exact manifests/disassembly
- Observed effect: no observed effect; protection level cannot be safely decoded from this record
- Confidence: **medium declaration; low reachability**
- Status: `NEW_STATIC_DEFINITION_NO_SINK`

## 6Z-001
- Source: `com.amazon.kindle.otter.oobe.BootAfterSystemOTAReceiver`
- Evidence file: `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java:27-61`
- SHA-256: `c29b32bf6874b245859357d926773193c15771a6eb254f97edac57541ae5cb90`
- Caller: SystemServer AmazonPackageManagerService.onBootPhase-550 plus PMS.isUpgrade
- Gate: protected RECEIVE_BOOT_AFTER_SYSTEM_OTA plus receiver action-OOBE-retail-demo guards; action=com.amazon.intent.action.BOOT_AFTER_SYSTEM_OTA
- Identity/user scope: system-server Context user-derived; numeric user UNKNOWN
- Sink: PackageHelper.enableComponent to OobeHomeActivity plus OOBEActivationHelper
- Observed effect: Enables OOBE activity and enters guarded OOBE activation; no proven Fire Launcher HOME setter
- Confidence: **high**
- Status: `STATIC_CONFIRMED_NUMERIC_USER_UNKNOWN`

## 6Z-002
- Source: `com.amazon.kindle.otter.oobe.commons.OOBEActivationHelper`
- Evidence file: `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java:29-34;53-56`
- SHA-256: `6ebcb7eef7a03459a76b9c21cd59b61a30947f2b00a5624a4646825b8e3223d2`
- Caller: BootAfterSystemOTAReceiver guarded lifecycle sender
- Gate: protected OTA lifecycle plus incremental-OOBE branch; no ordinary caller path; action=guarded BootAfterSystemOTA branch
- Identity/user scope: ContentResolver user inherited from receiver Context; numeric user UNKNOWN
- Sink: SettingsDBUtils to Settings.Secure-Global user_setup_complete=0 and isOOBEActive=1
- Observed effect: Mutates setup-OOBE state only when lifecycle guard passes; no HOME or preferred-package sink
- Confidence: **high**
- Status: `STATIC_SINK_CONFIRMED_EXACT_USER_UNKNOWN`

## 6Z-003
- Source: `com.amazon.dcpms.fos.service.lifecycle.pca.profileswitch.PCAActiveProfileReceiver`
- Evidence file: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:115-122`
- SHA-256: `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`
- Caller: upstream producer UNKNOWN; exported entry has no component permission in saved manifest
- Gate: manifest action gate plus PROGRAM_ID and PACKAGE_NAME extras; action=com.amazon.device.ACTION_ACTIVE_PROFILE_UPDATED
- Identity/user scope: receiver application user scope and cross-user acceptance UNKNOWN
- Sink: CDE profile type and OS user type and active-app list persistence to DeviceExperienceModeEvaluator.evaluate
- Observed effect: Updates DCPMS policy state; no SettingsProvider PMS HOME package-state or OTA sink
- Confidence: **medium**
- Status: `STATIC_EXPORTED_POLICY_SINK_CALLER_UNKNOWN`

## 6Z-004
- Source: `com.amazon.dcpms.fos.service.lifecycle.device.userswitch.DeviceUserSwitchReceiver`
- Evidence file: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:105-113`
- SHA-256: `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`
- Caller: system/framework USER_SWITCHED producer
- Gate: protected USER_SWITCHED gate; ordinary sender not established; action=android.intent.action.USER_SWITCHED
- Identity/user scope: receiver user and profile scope UNKNOWN
- Sink: CDE PCA-profile and OS-user persistence plus child active-app-list clear to evaluator
- Observed effect: Updates policy and profile state; no HOME PMS package-state or OTA sink
- Confidence: **high**
- Status: `STATIC_PROTECTED_ACTION_POLICY_SINK_CALLER_UNKNOWN`

## 6Z-005
- Source: `com.amazon.dcpms.fos.service.lifecycle.device.userswitch.AccountPropertyChangeReceiver`
- Evidence file: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:94-103`
- SHA-256: `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`
- Caller: producer UNKNOWN
- Gate: caller must satisfy AmazonAccountPropertyService.property.changed; permission protection and holder UNKNOWN; action=com.amazon.dcp.sso.action.AmazonAccountPropertyService.property.changed
- Identity/user scope: receiver user scope UNKNOWN
- Sink: CDE profile type and OS-user persistence to evaluator
- Observed effect: Policy persistence and evaluation only; no HOME PMS package-state or OTA sink
- Confidence: **medium**
- Status: `STATIC_PERMISSION_HOLDER_UNKNOWN`

## 6Z-006
- Source: `com.amazon.dcpms.fos.service.lifecycle.device.sync.GlobalContentSyncEventReceiver`
- Evidence file: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:145-153`
- SHA-256: `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`
- Caller: producer UNKNOWN
- Gate: GLOBAL_SYNC required; holder-protection and caller route UNKNOWN; action=com.amazon.intent.SYNC
- Identity/user scope: receiver exact user scope UNKNOWN
- Sink: JobIntentService to GlobalContentSyncEventService to ArcusSyncService.syncCDEPolicy
- Observed effect: Triggers CDE policy sync; no OTA recovery HOME or PMS package-state sink
- Confidence: **medium**
- Status: `STATIC_PERMISSION_HOLDER_UNKNOWN`

## 6Z-007
- Source: `ProductPolicyService via productpolicyservice_fosinit.xml`
- Evidence file: `artifacts/phase6bg-product-policy-readonly-20260805-01/productpolicyservice_fosinit.stderr.txt`
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Caller: init and system-server loader
- Gate: registered in-process fosinit; no exported app component or external caller evidence; action=init service registration
- Identity/user scope: system-server service identity; Binder publication and caller gate UNKNOWN
- Sink: ProductPolicy service registration only; no verified HOME package Settings or OTA sink in bounded corpus
- Observed effect: No exported component observed; service existence is not caller reachability
- Confidence: **medium**
- Status: `STATIC_REGISTRATION_ONLY_CALLER_AND_SINK_UNKNOWN`

## 6Z-008
- Source: `default_home plus config_show_default_home=true plus per-user preferred-activities`
- Evidence file: `work/luna_worker_settings_home_resource_followup_20260810.md`
- SHA-256: `UNKNOWN_REPORT_FILE_HASH`
- Caller: Settings UI or shell read path; no new writer established
- Gate: DefaultHomePreferenceController resource gate; normal dashboard omits default_home; set-home-activity is existing writer boundary; action=android.intent.action.MAIN plus CATEGORY_HOME
- Identity/user scope: per-user PMS Settings state; exact shell authorization is existing PMS gate; no new caller route
- Sink: com.android.server.pm.Settings preferred-activities and persistent-preferred-activities plus effective HOME resolver
- Observed effect: Existing HOME resolver and preferred-state divergence only; no new shell-writable Settings or DeviceConfig key
- Confidence: **high**
- Status: `CONFIRMED_EXISTING_BOUNDARY_DEDUPED`

## 6X-LIVE-001
- Source: `adb read-only snapshot`
- Evidence file: `adb/phase6x/PHASE6X-DEVICE-READONLY-20260810-01/getprop.stdout.txt`
- SHA-256: `9d6158ab236efb6b72489e2109f2220506048f0dc1c77a0230fde41f655e0ea5`
- Caller: adb shell getprop
- Gate: none; observation only
- Identity/user scope: serial G001LT0511550CFT; User 0 current
- Sink: build fingerprint
- Observed effect: PS7331.4463N/0031575863040; incremental 0031575863172; security patch 2024-08-01
- Confidence: **Confirmed observation**
- Status: `OBSERVED_READ_ONLY`

## 6X-LIVE-002
- Source: `cmd package resolve-activity`
- Evidence file: `adb/phase6x/PHASE6X-DEVICE-READONLY-20260810-01/home_user0.stdout.txt`
- SHA-256: `MISSING`
- Caller: shell read-only query
- Gate: resolver observation
- Identity/user scope: User 0
- Sink: formal HOME resolver
- Observed effect: com.amazon.firelauncher/.Launcher; priority 50
- Confidence: **Confirmed observation**
- Status: `OBSERVED_READ_ONLY`

## 6X-LIVE-003
- Source: `cmd package query-activities`
- Evidence file: `adb/phase6x/PHASE6X-DEVICE-READONLY-20260810-01/home_candidates_user0.stdout.txt`
- SHA-256: `MISSING`
- Caller: shell read-only query
- Gate: resolver observation
- Identity/user scope: User 0
- Sink: candidate set
- Observed effect: Fire 50, Microsoft 0, FallbackHome -1000
- Confidence: **Confirmed observation**
- Status: `OBSERVED_READ_ONLY`

## 6X-LIVE-004
- Source: `cmd package resolve/query-activities`
- Evidence file: `adb/phase6x/PHASE6X-CURRENT-SCOPE-READONLY-20260810-01/home_user10.stdout.txt`
- SHA-256: `90b0bcbb1461327869dd23bfe630d2c2d01971438248f0f8842bca931b5373af`
- Caller: shell read-only query
- Gate: resolver observation
- Identity/user scope: User 10 test profile
- Sink: candidate set
- Observed effect: FallbackHome only; Fire is user-scoped disabled in saved package dump
- Confidence: **Confirmed observation**
- Status: `OBSERVED_READ_ONLY`

## 6X-LIVE-005
- Source: `dumpsys package com.amazon.firelauncher`
- Evidence file: `adb/phase6x/PHASE6X-CURRENT-SCOPE-READONLY-20260810-01/firelauncher_package.stdout.txt`
- SHA-256: `86b91e5270d8f737609fd64481d9d7414fdcb164a169a936d038dc58450336ef`
- Caller: shell read-only dump
- Gate: package-state observation
- Identity/user scope: User 0 enabled=0; User 10 enabled=2
- Sink: package state
- Observed effect: User 0 installed/visible/enabled; User 10 disabled; no cross-user User 0 effect observed
- Confidence: **Confirmed observation**
- Status: `OBSERVED_READ_ONLY`

## 6X-LIVE-006
- Source: `dumpsys package preferred-xml`
- Evidence file: `adb/phase6x/PHASE6X-CURRENT-SCOPE-READONLY-20260810-01/preferred_activities.stdout.txt`
- SHA-256: `7750d564a29046d0eb9e6d5d0565389d38cd5f6b9b4d8010fdf54f5dd667a8c6`
- Caller: shell read-only dump
- Gate: preferred state observation
- Identity/user scope: User 0 record
- Sink: ordinary preferred activity
- Observed effect: preferred record names com.amazon.firelauncher/.Launcher with MAIN/HOME/DEFAULT filter
- Confidence: **Confirmed observation**
- Status: `OBSERVED_READ_ONLY`

## 6X2-IPC-001
- Source: `UNKNOWN`
- Evidence file: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:16376-16534;16413-16464;16519-16524`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: external dump caller; UID UNKNOWN
- Gate: android.permission.DUMP protection semantics not re-derived in bounded corpus
- Identity/user scope: default/device settings user; explicit user overload absent
- Sink: Settings.System.putInt(screen_brightness)
- Observed effect: POSITIVE sink and gate; NEGATIVE for HOME/package/OTA
- Confidence: **UNKNOWN**
- Status: `STATIC_SETTINGS_SINK_NOT_NEW`

## 6X2-IPC-002
- Source: `UNKNOWN`
- Evidence file: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:29308-29317;29345-29355;29384-29400;29517-29520;29570-29580`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: remote Binder caller UNKNOWN
- Gate: com.amazon.alexa.permission.MODE_SWITCH protection level/holder UNKNOWN
- Identity/user scope: USER_CURRENT=-2
- Sink: SecureSettingsHelper.putIntForUser(orientation_in_previous_mode)
- Observed effect: POSITIVE
- Confidence: **UNKNOWN**
- Status: `STATIC_SETTINGS_SINK_NOT_NEW`

## 6X2-IPC-003
- Source: `UNKNOWN`
- Evidence file: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:27078-27265;27426-27435;28453-28456`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: system_server/input-monitor publisher; external caller UNKNOWN
- Gate: permission and protection UNKNOWN
- Identity/user scope: system/default secure scope; non-user overload
- Sink: Settings.Secure.putInt(camera_shutter_state)
- Observed effect: POSITIVE bounded callback sink; NEGATIVE external Binder reachability
- Confidence: **UNKNOWN**
- Status: `STATIC_CALLBACK_SINK_NOT_NEW`

## 6X2-IPC-004
- Source: `UNKNOWN`
- Evidence file: `decompiled/jadx/settings/resources/AndroidManifest.xml; artifacts/phase6h/phase6h-framework-ipc-20260804-01/manifest-components.csv:202; artifacts/phase6w/exported-component-audit-20260805-01/high-impact-exported-candidates.csv:56`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: external sender UNKNOWN
- Gate: com.amazon.kindle.otter.oobe.OOBE_PERMISSION protection level and holder UNKNOWN
- Identity/user scope: receiver user scope UNKNOWN
- Sink: downstream Settings/HOME/package sink not joined
- Observed effect: POSITIVE exported declaration; NEGATIVE complete target sink
- Confidence: **UNKNOWN**
- Status: `EXPORTED_PERMISSION_UNKNOWN_NO_NEW_CHAIN`

## 6X2-IPC-005
- Source: `UNKNOWN`
- Evidence file: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:94-103; work/luna_worker_phase6sv_exported_surface_20260810.csv:4`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: producer UNKNOWN
- Gate: com.amazon.dcp.sso.permission.AmazonAccountPropertyService.property.changed protection/holder UNKNOWN
- Identity/user scope: receiver user scope UNKNOWN
- Sink: CDE/profile persistence and evaluator; no HOME/PMS/OTA sink
- Observed effect: POSITIVE policy sink; NEGATIVE target sink
- Confidence: **UNKNOWN**
- Status: `EXPORTED_POLICY_ONLY_DUPLICATE`

## 6X2-IPC-006
- Source: `UNKNOWN`
- Evidence file: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:95877-95954;97828-97986; work/luna_worker_amazonpm_caller_inventory_20260810.csv:2-3`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: production caller UNKNOWN; test-only callers excluded
- Gate: register: no local permission; deregister: creator UID equality gate; protection holder UNKNOWN
- Identity/user scope: user scope not explicit; receiver map only
- Sink: implicit receiver registration map; first package/HOME sink NOT_FOUND
- Observed effect: POSITIVE gate markers; NEGATIVE target sink
- Confidence: **UNKNOWN**
- Status: `PROXY_RESIDUAL_DUPLICATE`

## 6X2-IPC-007
- Source: `UNKNOWN`
- Evidence file: `artifacts/phase6mc-alta-jadx-20260810-01/sources/com/amazon/alta/h2clientservice/H2ClientService.java:104-126;226-236; artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/Manifest.java:6-9`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: external client UNKNOWN
- Gate: signature BIND_SERVICE declaration; exact holder/grant join UNKNOWN
- Identity/user scope: trusted adult/child profile scope; exact user data-flow partial
- Sink: user creation/removal and profile Settings relay; no HOME/PMS component sink
- Observed effect: POSITIVE workflow sink; NEGATIVE HOME/package sink
- Confidence: **UNKNOWN**
- Status: `EXPORTED_SERVICE_DUPLICATE`

## 6X2-IPC-008
- Source: `UNKNOWN`
- Evidence file: `artifacts/phase6mb-vending-jadx-20260810-01/base/sources/com/google/android/finsky/setup/dse/impl/DseService.java:272-484;576-603; output/tables/phase6qb-residual-inventory.csv:8-12`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: caller/package/account provenance UNKNOWN
- Gate: o() and qualification gates; exact permission protection UNKNOWN
- Identity/user scope: UserHandle.myUserId plus injected user/profile semantics UNKNOWN
- Sink: secure-settings-class writer; browser-default/install bookkeeping; no HOME/Fire writer
- Observed effect: POSITIVE bounded non-HOME sink; NEGATIVE target sink
- Confidence: **UNKNOWN**
- Status: `VENDING_RESIDUAL_DUPLICATE`

## 6X2-OTA-001
- Source: `official OTA ZIP`
- Evidence file: `firmware/manifests/OTA-20260803-01/README.md; firmware/manifests/OTA-20260803-01/sha256sums.txt`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: official OTA ZIP
- Gate: PS7331.4463N trona release OTA; SHA-256 9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: Historical README separately marks installed PS7330 mismatch
- Confidence: **UNKNOWN**
- Status: `CONFIRMED`

## 6X2-OTA-002
- Source: `ZIP member inventory`
- Evidence file: `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/members.tsv`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: ZIP member inventory
- Gate: META-INF metadata otacert update-binary updater-script; .new.dat.br; transfer lists; boot/images
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: Traditional signed BLOCK OTA
- Confidence: **UNKNOWN**
- Status: `CONFIRMED`

## 6X2-OTA-003
- Source: `ZIP member inventory`
- Evidence file: `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/members.tsv`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: ZIP member inventory
- Gate: No payload.bin and no A/B postinstall executable member
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: Postinstall executable route is negative for package-shape scope
- Confidence: **UNKNOWN**
- Status: `NEGATIVE`

## 6X2-OTA-004
- Source: `updater-script assertions`
- Evidence file: `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/updater-script.txt`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: updater-script assertions
- Gate: Build date and ro.product.device trona assertions
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: Static script gate only
- Confidence: **UNKNOWN**
- Status: `CONFIRMED`

## 6X2-OTA-005
- Source: `SideloadMetadataChecker.check`
- Evidence file: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/dcp/ota/SideloadMetadataChecker.java:24-29`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: SideloadMetadataChecker.check
- Gate: Version signature-transition product and PVT checks
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: Transition/downgrade controls are OTASettings gated
- Confidence: **UNKNOWN**
- Status: `CONFIRMED`

## 6X2-OTA-006
- Source: `SideloadVerifier.verifySideloadWithRecoveryCheck`
- Evidence file: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/dcp/ota/SideloadVerifier.java:31-58`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: SideloadVerifier.verifySideloadWithRecoveryCheck
- Gate: Sanity metadata RecoverySystemWrapper.verifyPackage device state
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: Platform verifier implementation not present in preserved Java
- Confidence: **UNKNOWN**
- Status: `CONFIRMED`

## 6X2-OTA-007
- Source: `OSUpdateValidator.validateOSUpdate`
- Evidence file: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/device/software/ota/tasks/validate/OSUpdateValidator.java:73-78`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: OSUpdateValidator.validateOSUpdate
- Gate: Hash then RecoverySystem.verifyPackage then OSUpdatePropertiesValidator
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: Call order is exact in source
- Confidence: **UNKNOWN**
- Status: `CONFIRMED`

## 6X2-OTA-008
- Source: `SideloadMover.maybeMoveSideloadFile`
- Evidence file: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/dcp/ota/SideloadMover.java:31-44`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: SideloadMover.maybeMoveSideloadFile
- Gate: Basename destination and FileHelper.moveFile
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: No Java canonicalPath realpath lstat or O_NOFOLLOW marker
- Confidence: **UNKNOWN**
- Status: `CONFIRMED`

## 6X2-OTA-009
- Source: `SideloadInstaller.installSideload`
- Evidence file: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/dcp/ota/SideloadInstaller.java:65-90`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: SideloadInstaller.installSideload
- Gate: Metadata/device checks then mover then installOSUpdate
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: WithoutRecoveryCheck branch is not proof of bypass because normal integrity path is separate
- Confidence: **UNKNOWN**
- Status: `CONFIRMED`

## 6X2-OTA-010
- Source: `UpdateSystemWrapper.install`
- Evidence file: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/device/framework/UpdateSystemWrapper.java:33-43`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: UpdateSystemWrapper.install
- Gate: Path prefix remap settings write then UpdateSystem.install
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: Recovery/native exec caller remains separate boundary
- Confidence: **UNKNOWN**
- Status: `CONFIRMED`

## 6X2-OTA-011
- Source: `OTA controller holders`
- Evidence file: `artifacts/phase6j/ota-controller-holders-manifest-audit-20260805-02/com-amazon-dcp.manifest.txt; com-amazon-otter-forced-ota.manifest.txt`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: OTA controller holders
- Gate: com.amazon.dcp.ota.permission.CONTROLLER and PROCESS_UPDATES protected surface
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: Holder evidence is privileged/controller capability
- Confidence: **UNKNOWN**
- Status: `CONFIRMED`

## 6X2-OTA-012
- Source: `main to block-image registry`
- Evidence file: `findings/phase-6mm-updater-blockimage-closure.md; artifacts/phase6mm-updater-blockimage-20260810-01/block-image-registration.csv`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: main to block-image registry
- Gate: RegisterBlockImageFunction to RegisterFunction; block_image_update to BlockImageUpdateFn 0x40b8b8
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: Static registration not execution
- Confidence: **UNKNOWN**
- Status: `CONFIRMED`

## 6X2-OTA-013
- Source: `PackageExtractFileFn`
- Evidence file: `findings/phase-6kt-recovery-verifier-provenance.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: PackageExtractFileFn
- Gate: PackageExtractFileFn to ota_open to open and extraction fsync close
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: Capability not reachability
- Confidence: **UNKNOWN**
- Status: `CONFIRMED`

## 6X2-OTA-014
- Source: `BlockImageUpdateFn to WriteToPartition`
- Evidence file: `findings/phase-6kt-recovery-verifier-provenance.md; findings/phase-6mm-updater-blockimage-closure.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: BlockImageUpdateFn to WriteToPartition
- Gate: PerformBlockImageUpdate to WriteToPartition to ota_write to write
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: No execution or partition write
- Confidence: **UNKNOWN**
- Status: `CONFIRMED`

## 6X2-OTA-015
- Source: `updater-script`
- Evidence file: `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/updater-script.txt`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: updater-script
- Gate: system vendor boot preloader lk tee1 tee2 spmfw sspm_1 cam_vpu1 cam_vpu2 cam_vpu3 and cache blocklist
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: No arbitrary target conclusion
- Confidence: **UNKNOWN**
- Status: `CONFIRMED`

## 6X2-OTA-016
- Source: `MakeFreeSpaceOnCache`
- Evidence file: `artifacts/phase6mm-updater-blockimage-20260810-01/canonicalization-call-sites.csv; findings/phase-6mm-updater-blockimage-closure.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: MakeFreeSpaceOnCache
- Gate: 0x417bf0 to __readlink_chk 0x4ce4e8
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: Callsite is path-related but impact is unknown
- Confidence: **UNKNOWN**
- Status: `CONFIRMED`

## 6X2-OTA-017
- Source: `selected direct-call graph`
- Evidence file: `findings/phase-6mm-updater-blockimage-closure.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: selected direct-call graph
- Gate: No selected direct edge from readlink helper to extraction/block-image/write sinks
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: Not binary-wide absence and not traversal proof
- Confidence: **UNKNOWN**
- Status: `NEGATIVE`

## 6X2-OTA-018
- Source: `CacheSizeCheck and callers`
- Evidence file: `work/luna_worker_ota_canonicalization_provenance_20260810.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: CacheSizeCheck and callers
- Gate: Body return/error branches and all indirect dispatch not fully selected
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: No symlink/traversal test
- Confidence: **UNKNOWN**
- Status: `UNKNOWN`

## 6X2-OTA-019
- Source: `platform recovery verifier`
- Evidence file: `findings/phase-6kt-recovery-verifier-provenance.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: platform recovery verifier
- Gate: RecoverySystemWrapper delegates to platform RecoverySystem; exact native verifier absent
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: Do not infer AVB bypass
- Confidence: **UNKNOWN**
- Status: `UNKNOWN`

## 6X2-OTA-020
- Source: `otacert and verifyPackage`
- Evidence file: `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/otacert.pem; artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/android/os/RecoverySystemWrapper.java:21-23`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: otacert and verifyPackage
- Gate: Certificate material plus verification API call boundary
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: Full cryptographic implementation unknown
- Confidence: **UNKNOWN**
- Status: `CONFIRMED`

## 6X2-OTA-021
- Source: `bootloader/recovery rollback index`
- Evidence file: `findings/phase-6kt-recovery-verifier-provenance.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: bootloader/recovery rollback index
- Gate: No exact rollback-index decision branch in saved corpus
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: Date/version gates are not equivalent to anti-rollback proof
- Confidence: **UNKNOWN**
- Status: `UNKNOWN`

## 6X2-OTA-022
- Source: `shell UID / ordinary app`
- Evidence file: `findings/phase-6kt-recovery-verifier-provenance.md; findings/phase-6j-ota-apk-deep-review.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: shell UID / ordinary app
- Gate: No saved caller chain from shell or ordinary APK to UpdateSystem.install/recovery writer
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Observed effect: Bounded negative not universal absence
- Confidence: **UNKNOWN**
- Status: `NEGATIVE`

## 6X2-OTA-023
- Source: `installed device snapshot`
- Evidence file: `firmware/manifests/OTA-20260803-01/README.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: installed device snapshot
- Gate: Installed snapshot PS7330.4104N versus adjacent OTA PS7331.4463N
- Identity/user scope: PS7330
- Sink: UNKNOWN
- Observed effect: Keep historical mismatch separate from current PS7331 package facts
- Confidence: **UNKNOWN**
- Status: `VERSION_MISMATCH`

## AC-001
- Source: `findings/phase-6cy-accessibility-reboot-unlock-result.md; output/tables/phase6cy-reboot-unlock-result.csv`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **confirmed**
- Status: `TRUE_HOME_FIRE`

## AC-002
- Source: `findings/phase-4b-assisted-workarounds.md; adb/phase4/PHASE4-ACCESSIBILITY-T01/measure/summary.tsv`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **confirmed**
- Status: `FAILED_FOREGROUND_REDIRECT`

## AC-003
- Source: `findings/phase-6cv-accessibility-pendingintent-gui-boundary.md; output/tables/phase6cv-accessibility-pendingintent-gui-boundary.csv`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **confirmed-boundary**
- Status: `UNKNOWN_NOT_MEASURED`

## AC-004
- Source: `findings/phase-6cy-ms-targeted-accessibility-retry.md; output/tables/phase6cy-ms-targeted-accessibility-retry.csv`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **confirmed-but-nondeterministic**
- Status: `FOREGROUND_REDIRECT`

## AC-005
- Source: `findings/phase-6cy-accessibility-reboot-unlock-result.md; findings/phase-6hb-ms-accessibility-reboot-persistence.md`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **confirmed-foreground-only**
- Status: `UNLOCK_AFTER_REDIRECT`

## AC-006
- Source: `findings/phase-6cy-accessibility-timeout-ab-boundary.md; output/tables/phase6cy-accessibility-reboot-persistence.csv`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **confirmed-negative-optimization**
- Status: `FOREGROUND_REDIRECT_NOT_ADOPTED`

## AC-007
- Source: `adb/phase6cy/PHASE6CY-CONSUME-HOME-20260807-02/result.json; findings/phase-6cy-accessibility-adb-pause-boundary.md`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **confirmed-boundary**
- Status: `FAILED_OR_PARTIAL_FOREGROUND`

## AC-008
- Source: `adb/phase6ac/PHASE6AC-RO-20260805-01/pm_dump.stdout.txt; adb/phase6ao/PHASE6AO-RO-20260805-01/package_dump_full.stdout.txt`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **unknown**
- Status: `UNKNOWN_NOT_VALIDATED`

## AC-009
- Source: `findings/phase-6iq-adb-foreground-fallback.md; adb/phase6iq/PHASE6IQ-ADB-MONITOR-20260807-05/`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **confirmed-but-not-approved**
- Status: `FOREGROUND_REDIRECT_CLOSED`

## AC-010
- Source: `findings/phase-6hb-ms-accessibility-reboot-persistence.md; findings/phase-6cy-accessibility-reboot-unlock-result.md`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **unknown**
- Status: `UNKNOWN_NOT_A_WORKAROUND`

## AC-011
- Source: `tools/phase4-accessibility/README.md; tools/phase4-accessibility/src/org/fireosresearch/phase4/redirect/LauncherRedirectService.java`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **conditional**
- Status: `SAFE_FOREGROUND_ASSIST_ONLY`

## 6X2-ROUTES-001
- Source: `UNKNOWN`
- Evidence file: `findings/phase-6z-evidence-index.md; work/luna_worker_phase6z_components_20260810.csv rows 6Z-001/002; artifacts/phase6mg-oobe-helper-scope-20260810-01/`
- SHA-256: `d666aab4deae3bd37ddbc528dd63680256318b709a467659925b3952ef19829c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **UNKNOWN**
- Status: `untested_host_only`

## 6X2-ROUTES-002
- Source: `UNKNOWN`
- Evidence file: `work/luna_worker_phase6z_components_20260810.csv rows 6Z-003/005/006; artifacts/phase6bk/protected-broadcast-expanded-20260810-01/`
- SHA-256: `d666aab4deae3bd37ddbc528dd63680256318b709a467659925b3952ef19829c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **UNKNOWN**
- Status: `untested_host_only`

## 6X2-ROUTES-003
- Source: `UNKNOWN`
- Evidence file: `work/luna_worker_phase6z_components_20260810.csv row 6Z-007; artifacts/phase6bg-product-policy-readonly-20260805-01/; findings/phase-6x-report.md`
- SHA-256: `d666aab4deae3bd37ddbc528dd63680256318b709a467659925b3952ef19829c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **UNKNOWN**
- Status: `untested_host_only`

## 6X2-ROUTES-004
- Source: `UNKNOWN`
- Evidence file: `findings/phase-6x-prewarm-authorization.md; work/luna_worker_phase6up_asp_prewarm_closure_20260810.csv; artifacts/phase6bk/ipc-ota-closure-20260810-02/`
- SHA-256: `d666aab4deae3bd37ddbc528dd63680256318b709a467659925b3952ef19829c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **UNKNOWN**
- Status: `untested_host_only`

## 6X2-ROUTES-005
- Source: `UNKNOWN`
- Evidence file: `work/luna_worker_phase6y_permission_20260810.csv; artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- SHA-256: `d666aab4deae3bd37ddbc528dd63680256318b709a467659925b3952ef19829c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **UNKNOWN**
- Status: `untested_host_only`

## 6X2-ROUTES-006
- Source: `UNKNOWN`
- Evidence file: `findings/phase-6y-ota-staging-boundary.md; artifacts/phase6mk-updater-dispatch-20260810-04/; artifacts/phase6kt/recovery-verifier-audit-20260810-01/`
- SHA-256: `d666aab4deae3bd37ddbc528dd63680256318b709a467659925b3952ef19829c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Observed effect: UNKNOWN
- Confidence: **UNKNOWN**
- Status: `untested_host_only`
