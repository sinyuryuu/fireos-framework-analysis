# Phase 6X3 evidence index

The index retains unknown caller, gate, identity, user-scope, and sink edges as UNKNOWN. Static capability is not treated as a privilege transition.

## WG-001
- Phase/surface: `6WL` / `6WG Framework IPC residual`
- Source: `work/luna_worker_phase6wg_ipc_residual_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: external dumpsys caller subject to DUMP; exact UID UNKNOWN
- Gate: android.permission.DUMP checked in dump; service-manager/SELinux rule UNKNOWN
- Identity/user scope: device/default settings user (explicit user overload absent)
- Sink: FireOsDisplayPowerControllerService$BinderService
- Effect: UNKNOWN
- Confidence: **static direct**; status `UNKNOWN`

## WG-002
- Phase/surface: `6WL` / `6WG Framework IPC residual`
- Source: `work/luna_worker_phase6wg_ipc_residual_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: system_server input-monitor caller/publisher; external Binder caller not recovered
- Gate: system_server/internal callback; permission and SELinux/service-manager gate UNKNOWN
- Identity/user scope: system/default secure-settings scope (non-user overload)
- Sink: InputFilterMonitorInputManagerServiceCallback
- Effect: UNKNOWN
- Confidence: **static direct**; status `UNKNOWN`

## WG-003
- Phase/surface: `6WL` / `6WG Framework IPC residual`
- Source: `work/luna_worker_phase6wg_ipc_residual_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: remote Binder caller with MODE_SWITCH; exact UID UNKNOWN
- Gate: com.amazon.alexa.permission.MODE_SWITCH enforced by checkCallingOrSelfPermission; service-manager/SELinux rule UNKNOWN
- Identity/user scope: USER_CURRENT/-2 passed to putIntForUser
- Sink: AlexaModeSwitchManagerService$AlexaModeSwitchAPIImpl
- Effect: UNKNOWN
- Confidence: **static direct**; status `UNKNOWN`

## 6WL-ROW-004
- Phase/surface: `6WL` / `6WH OTA residual`
- Source: `work/luna_worker_phase6wh_ota_residual_20260810.csv`
- Evidence file: `artifacts/phase6mk-updater-dispatch-20260810-04/registration-dispatch.csv:7,16,19-22; updater-script-entrypoints.csv:2-13; addresses 0x406b8c,0x406e0c,0x406ee4,0x406f2c,0x406f6c,0x406fac`
- SHA-256: `d88e35ec08d9ef0a55a3dbc17dc430b62d3b419810653542b6dd3077095cca24;4d0128ee85eec7b0c88716012858bef699f740907e46e854939c83a6c9e99077`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: NONE
- Confidence: **UNKNOWN**; status `UNKNOWN`

## 6WL-ROW-005
- Phase/surface: `6WL` / `6WH OTA residual`
- Source: `work/luna_worker_phase6wh_ota_residual_20260810.csv`
- Evidence file: `artifacts/phase6ne-updater-cache-flow-20260810-03/direct-call-edges.csv:1-5,42-43; addresses 0x417bf0,0x417ea8,0x417eb0,0x409cb4,0x409cdc`
- SHA-256: `d653e4a84898509781a333c56502087a83981781fcf6612d7026bfd79602b477`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: NONE
- Confidence: **UNKNOWN**; status `UNKNOWN`

## 6WL-ROW-006
- Phase/surface: `6WL` / `6WH OTA residual`
- Source: `work/luna_worker_phase6wh_ota_residual_20260810.csv`
- Evidence file: `artifacts/phase6my-bootafter-ota-package-helper-20260810-01/call-edges.csv:6MY-E03-E04,E08,E10`
- SHA-256: `1136d4815ae63011522fead17ef743bc0daa57334ae6ebb3b4c05c1d09507c52`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: NONE
- Confidence: **UNKNOWN**; status `UNKNOWN`

## 6WL-ROW-007
- Phase/surface: `6WL` / `6WH OTA residual`
- Source: `work/luna_worker_phase6wh_ota_residual_20260810.csv`
- Evidence file: `artifacts/phase6j/phase6j-ota-controller-holders-20260805-01/controller-permission-context.txt:10537-10541,27271-27275`
- SHA-256: `d68768263846c87ffc6b1b1d100b5b5bcd34212d5605c4e3eb1085da8c67d1e0`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: NONE
- Confidence: **UNKNOWN**; status `UNKNOWN`

## 6WL-ROW-008
- Phase/surface: `6WL` / `6WH OTA residual`
- Source: `work/luna_worker_phase6wh_ota_residual_20260810.csv`
- Evidence file: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/dcp/ota/SideloadMover.java:31-44; FileHelper.java:305-339`
- SHA-256: `59131cf032d8544cd44ea839ad63eb37993d2853b4925bf56d10ede721693f63;55a7f44a70735626be7ebde25e96812346f336fddbec2c87ca0fb709b980`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: NONE
- Confidence: **UNKNOWN**; status `UNKNOWN`

## 6WL-ROW-009
- Phase/surface: `6WL` / `6WH OTA residual`
- Source: `work/luna_worker_phase6wh_ota_residual_20260810.csv`
- Evidence file: `firmware/extracted/PS7331/vbmeta.img absent; firmware/extracted/PS7331/META-INF/com/android/avb* absent; UpdateSystemWrapper.java:33-44`
- SHA-256: `c99f6884fa298546b18722a5addb46ae35aff4c9f6003d8ad3ccaebe2edfdbd9`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: NONE
- Confidence: **UNKNOWN**; status `UNKNOWN`

## WI-01
- Phase/surface: `6WL` / `6WI native driver caller`
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `cmdq_driver.c=b3a54d37b4e498ff969a2717cb02cefc923ae6f39da32f5fd8529fe3dce6e899; kernel.config=eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04; Image=10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d; vendor_file_contexts=db5cd91b8d25170ad27809ace8cdbbd2a3f838ec72e2598a4f6b5a44953d322e`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: policy names device type only; no exact caller identity or framework/HOME/package sink
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **UNKNOWN**; status `UNKNOWN`

## WI-02
- Phase/surface: `6WL` / `6WI native driver caller`
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `ion.c=abac518864faed94439d75d204e8c16ea75cf3a74c93ee50e128e0f6928a6d63; kernel.config=eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04; vendor_file_contexts=db5cd91b8d25170ad27809ace8cdbbd2a3f838ec72e2598a4f6b5a44953d322e; native-inventory.csv=9d1313d25cb45492d5656d03f05b7e60f5d037ccef15c20d9edec5e0fdbf17f9`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: ION library labels are same_process_hal_file; no exact identity and no package/HOME/settings sink
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **UNKNOWN**; status `UNKNOWN`

## WI-03
- Phase/surface: `6WL` / `6WI native driver caller`
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `boot.img=cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b; Image=10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d; native-inventory.csv=9d1313d25cb45492d5656d03f05b7e60f5d037ccef15c20d9edec5e0fdbf17f9`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: no userland identity or sensitive sink identified
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **UNKNOWN**; status `UNKNOWN`

## WI-04
- Phase/surface: `6WL` / `6WI native driver caller`
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `amzn_idme.c=ab6484ae7a694412ec4eeabb67133ddd0c0af221076b6d989c8ab1fe7c84e61e; kernel.config=eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04; vendor_file_contexts=db5cd91b8d25170ad27809ace8cdbbd2a3f838ec72e2598a4f6b5a44953d322e`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: HAL service identity is privileged-domain context only; no exact package/HOME/PMS sink
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **UNKNOWN**; status `UNKNOWN`

## WI-05
- Phase/surface: `6WL` / `6WI native driver caller`
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `amzn_drv_test.c=6c2309f996cacafaab35cce3935bcb725a5259211751af89df88d3732797029e; libmt8183_diag.so=7147e161de7b3a8097bdf6079d0b414c147067d46e1f446138d041a63dd127d7; vendor_sepolicy.cil=82430bdb87b8a5f653110b635289489b99e82bdbe7bdc7a2e1ee5564e674e035`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: diagnostic HAL/domain name is not a proc caller and no package/HOME/privilege sink is joined
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **UNKNOWN**; status `UNKNOWN`

## WI-06
- Phase/surface: `6WL` / `6WI native driver caller`
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `vendor_file_contexts=db5cd91b8d25170ad27809ace8cdbbd2a3f838ec72e2598a4f6b5a44953d322e; vendor_sepolicy.cil=82430bdb87b8a5f653110b635289489b99e82bdbe7bdc7a2e1ee5564e674e035`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: rpmb_svc identity is a service observation; no package/HOME sink
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **UNKNOWN**; status `UNKNOWN`

## WI-07
- Phase/surface: `6WL` / `6WI native driver caller`
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `phase6me input-manifest=ada254be9c56572282704924eea66e2852889ec73c0a65be4558f36f77d8250a; native-inventory.csv=9d1313d25cb45492d5656d03f05b7e60f5d037ccef15c20d9edec5e0fdbf17f9; vendor_file_contexts=db5cd91b8d25170ad27809ace8cdbbd2a3f838ec72e2598a4f6b5a44953d322e`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: HAL/service identity only; no package/HOME/settings sink
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **UNKNOWN**; status `UNKNOWN`

## WJ-01
- Phase/surface: `6WL` / `6WJ test reconciliation`
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: Saved resolver evidence remains Fire Launcher; static HOME setters/sinks do not establish ordinary caller reachability or a sustainable replacement.
- Confidence: **UNKNOWN**; status `INTEGRATED`

## WJ-02
- Phase/surface: `6WL` / `6WJ test reconciliation`
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: Package-state writers exist in framework/Amazon code, but saved gates rejected ordinary mutation and no writer is shown to reach User-0 HOME sustainably.
- Confidence: **UNKNOWN**; status `INTEGRATED`

## WJ-03
- Phase/surface: `6WL` / `6WJ test reconciliation`
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: Child/profile lifecycle and KFT component changes are real only for the target child/profile; final guards preserve User-0 Fire Launcher.
- Confidence: **UNKNOWN**; status `INTEGRATED`

## WJ-04
- Phase/surface: `6WL` / `6WJ test reconciliation`
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: DPM tests show bounded owner/admin behavior but no ordinary sustainable HOME/package-state route; static DPM sinks remain gated and caller identity is incomplete.
- Confidence: **UNKNOWN**; status `INTEGRATED`

## WJ-05
- Phase/surface: `6WL` / `6WJ test reconciliation`
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: Resource/default-home and overlay evidence does not prove runtime selection; no settings mutation or durable HOME change is established.
- Confidence: **UNKNOWN**; status `INTEGRATED`

## WJ-06
- Phase/surface: `6WL` / `6WJ test reconciliation`
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: Service visibility/candidate interfaces and static sinks do not establish a callable transaction or accepted identity; H2 holder/grant/requester remains incomplete.
- Confidence: **UNKNOWN**; status `INTEGRATED`

## WJ-07
- Phase/surface: `6WL` / `6WJ test reconciliation`
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: Exact OTA and native updater paths contain partition/cache writers statically, but no updater, recovery, OTA, reboot, or partition effect was observed.
- Confidence: **UNKNOWN**; status `INTEGRATED`

## WJ-08
- Phase/surface: `6WL` / `6WJ test reconciliation`
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: Driver and native control edges are host-side static/conditional evidence only; retail node access, process/domain load, and effect are not established.
- Confidence: **UNKNOWN**; status `INTEGRATED`

## WJ-09
- Phase/surface: `6WL` / `6WJ test reconciliation`
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: Source/config/probe logs do not close a retail privilege transition or sensitive sink; no approved device mutation is present.
- Confidence: **UNKNOWN**; status `INTEGRATED`

## WJ-10
- Phase/surface: `6WL` / `6WJ test reconciliation`
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: Tahoe/KFT/Launcher3 and accessibility/ADB foreground paths are either child-scoped or temporary; none is a sustainable User-0 formal HOME replacement.
- Confidence: **UNKNOWN**; status `INTEGRATED`

## WK-001
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `186a710bb9d27f703f2c76bc1e179ac18cebbff022674e9e71f2bf7a50226327`
- Caller: DefaultPermissionGrantPolicy
- Gate: system_server/internal policy path; exact caller gate UNKNOWN
- Identity/user scope: userId argument
- Sink: DefaultPermissionGrantPolicy
- Effect: UNKNOWN
- Confidence: **static direct**; status `UNKNOWN`

## WK-002
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `a92e54ac19e886b935b547717827ccf018d1caa554b8ecaf8467b6077d7d309e`
- Caller: UserManagerService Binder implementation
- Gate: checkManageOrCreateUsersPermission(flags); MANAGE_USERS or CREATE_USERS; system/root accepted
- Identity/user scope: system/default user scope
- Sink: UserManagerService
- Effect: UNKNOWN
- Confidence: **static direct**; status `UNKNOWN`

## WK-003
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `a92e54ac19e886b935b547717827ccf018d1caa554b8ecaf8467b6077d7d309e`
- Caller: UserManagerService Binder implementation
- Gate: checkManageOrCreateUsersPermission(flags); MANAGE_USERS or CREATE_USERS; system/root accepted
- Identity/user scope: parent userId plus created profile
- Sink: UserManagerService
- Effect: UNKNOWN
- Confidence: **static direct**; status `UNKNOWN`

## WK-004
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `a92e54ac19e886b935b547717827ccf018d1caa554b8ecaf8467b6077d7d309e`
- Caller: UserManagerService Binder implementation
- Gate: checkManageOrCreateUsersPermission("Only the system can remove users"); exact downstream checks UNKNOWN
- Identity/user scope: userHandle argument
- Sink: UserManagerService
- Effect: UNKNOWN
- Confidence: **static direct**; status `UNKNOWN`

## WK-005
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `3382de2f12fc0f38c757c3fd021c06482db96c19389ec9909218423addd47274`
- Caller: UserController Binder-facing path
- Gate: INTERACT_ACROSS_USERS_FULL or amazon.aosp.permission.INTERACT_ACROSS_USERS_FULL; Binder calling pid/uid checked; shell restriction also enforced
- Identity/user scope: userId; system user rejected
- Sink: UserController
- Effect: UNKNOWN
- Confidence: **static direct**; status `UNKNOWN`

## WK-006
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `7aafaa0ccc5336df4f8e8cb7bcd38afbd578790c3065f28843a76a1eb36c06cc`
- Caller: ActivityManagerShellCommand
- Gate: shell command plus canSwitchUsers restriction; exact shell UID enforcement in downstream path UNKNOWN
- Identity/user scope: supplied target user
- Sink: ActivityManagerShellCommand
- Effect: UNKNOWN
- Confidence: **static direct**; status `UNKNOWN`

## WK-007
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `7aafaa0ccc5336df4f8e8cb7bcd38afbd578790c3065f28843a76a1eb36c06cc`
- Caller: ActivityManagerShellCommand
- Gate: shell command path; downstream caller and SELinux gate UNKNOWN
- Identity/user scope: supplied target user
- Sink: ActivityManagerShellCommand
- Effect: UNKNOWN
- Confidence: **static direct**; status `UNKNOWN`

## WK-008
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `7aafaa0ccc5336df4f8e8cb7bcd38afbd578790c3065f28843a76a1eb36c06cc`
- Caller: ActivityManagerShellCommand
- Gate: shell command path; downstream INTERACT_ACROSS_USERS_FULL gate visible in UserController
- Identity/user scope: supplied target user
- Sink: ActivityManagerShellCommand
- Effect: UNKNOWN
- Confidence: **static direct**; status `UNKNOWN`

## WK-009
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `107ba7f2925439e8bf061b39b9496a5d6cc661c00990d5be9259104f2960486f`
- Caller: AppRestrictionsHelper
- Gate: PackageManager validation; Settings UI/profile-policy caller and SELinux rule UNKNOWN
- Identity/user scope: explicit userId
- Sink: AppRestrictionsHelper
- Effect: UNKNOWN
- Confidence: **static direct**; status `UNKNOWN`

## WK-010
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `107ba7f2925439e8bf061b39b9496a5d6cc661c00990d5be9259104f2960486f`
- Caller: AppRestrictionsHelper
- Gate: PackageManager uninstall validation; only restricted-profile branch visible
- Identity/user scope: explicit userId
- Sink: AppRestrictionsHelper
- Effect: UNKNOWN
- Confidence: **static direct**; status `UNKNOWN`

## WK-011
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `1e15d3461b6d0e34391eba9b628e8ca83a7082590baf33bfec4ad8d00e5209df`
- Caller: UserManagerHelper
- Gate: helper checks no_add_user restriction; service permission gate remains authoritative
- Identity/user scope: current process/default user scope
- Sink: UserManagerHelper
- Effect: UNKNOWN
- Confidence: **static direct**; status `UNKNOWN`

## WK-012
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `1e15d3461b6d0e34391eba9b628e8ca83a7082590baf33bfec4ad8d00e5209df`
- Caller: UserManagerHelper
- Gate: helper excludes system/current-user case; service permission gate remains authoritative
- Identity/user scope: userInfo.id
- Sink: UserManagerHelper
- Effect: UNKNOWN
- Confidence: **static direct**; status `UNKNOWN`

## WK-013
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `1e15d3461b6d0e34391eba9b628e8ca83a7082590baf33bfec4ad8d00e5209df`
- Caller: UserManagerHelper
- Gate: helper checks current/foreground user only; downstream switch gate and SELinux rule UNKNOWN
- Identity/user scope: target user id
- Sink: UserManagerHelper
- Effect: UNKNOWN
- Confidence: **static direct**; status `UNKNOWN`

## WK-014
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `4efc2aba8f7798fb4e026f13479f5b4929ef545deba5618b35d799555d78678b`
- Caller: external callers through exported SettingsProvider
- Gate: global/secure writes enforce WRITE_SECURE_SETTINGS; system writes use WRITE_SETTINGS or app-op; cross-user gate at 431
- Identity/user scope: calling user and requested setting namespace
- Sink: SettingsProvider
- Effect: UNKNOWN
- Confidence: **static direct**; status `UNKNOWN`

## WK-015
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `e4f2d9d47e7fa10be2aa2d26f6549b41184762d7ff5c77c19ffa7fc7560aac70`
- Caller: SettingsProvider
- Gate: android:exported=true; sharedUserId=android.uid.system; provider write methods enforce permissions
- Identity/user scope: singleUser across users
- Sink: SettingsProvider
- Effect: UNKNOWN
- Confidence: **static manifest**; status `UNKNOWN`

## WK-016
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `58ce4931e266384bd63147b65748edb53190d68f270b0b324dfa5c646506d5af`
- Caller: MediaSessionService
- Gate: internal service path; exact caller/permission and SELinux rule UNKNOWN
- Identity/user scope: full user id
- Sink: MediaSessionService
- Effect: UNKNOWN
- Confidence: **static direct**; status `UNKNOWN`

## WK-017
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence file: `UNKNOWN`
- SHA-256: `a92e54ac19e886b935b547717827ccf018d1caa554b8ecaf8467b6077d7d309e`
- Caller: UserManagerService
- Gate: system_server internal; file path, DAC, SELinux and caller gate UNKNOWN
- Identity/user scope: user list and user state
- Sink: UserManagerService
- Effect: UNKNOWN
- Confidence: **static file sink**; status `UNKNOWN`

## WF-POL-001
- Phase/surface: `6WL` / `6WF live ProductPolicy`
- Source: `UNKNOWN`
- Evidence file: `artifacts/phase6wf-product-policy-readonly-20260810-01/global_policy.xml`
- SHA-256: `2cc60c0ee80bbba2752671b7323e2bdaae8f87125b7251726f821906f58087e2`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: none; read-only
- Confidence: **UNKNOWN**; status `CONFIRMED_NO_ENTRY`

## WF-POL-002
- Phase/surface: `6WL` / `6WF live ProductPolicy`
- Source: `UNKNOWN`
- Evidence file: `artifacts/phase6wf-product-policy-readonly-20260810-01/common_device_policy.xml`
- SHA-256: `75c7919d2006fc0b088996cd2048b927c419b03ca025a95b20ff31e3de9868aa`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: none; read-only
- Confidence: **UNKNOWN**; status `CONFIRMED_NO_ENTRY`

## WF-POL-003
- Phase/surface: `6WL` / `6WF live ProductPolicy`
- Source: `UNKNOWN`
- Evidence file: `artifacts/phase6wf-product-policy-readonly-20260810-01/multimodal_device_policy.xml`
- SHA-256: `66f05c0e0f502e6db191904ec39be5e5b6302905f00cdacfc8a29ef327089512`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: none; read-only
- Confidence: **UNKNOWN**; status `CONFIRMED_NO_ENTRY`

## WF-POL-004
- Phase/surface: `6WL` / `6WF live ProductPolicy`
- Source: `UNKNOWN`
- Evidence file: `artifacts/phase6wf-product-policy-readonly-20260810-01/receiver_filter_policy.xml`
- SHA-256: `c3a80bcd0b52250aaa72bd863ae6a633f3153df646ffc57682972bc7c39fab8c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: none; read-only
- Confidence: **UNKNOWN**; status `CONFIRMED_NOT_HOME_WRITER`

## WF-POL-005
- Phase/surface: `6WL` / `6WF live ProductPolicy`
- Source: `UNKNOWN`
- Evidence file: `artifacts/phase6wf-product-policy-readonly-20260810-01/device_policy_paths.txt`
- SHA-256: `fee33721f9ea80bb151b2fb04b58de4d9e846a1de68c7c994f6e7416d217fe07`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: none; pull failed with ENOENT
- Confidence: **UNKNOWN**; status `UNKNOWN_LAYOUT_MISMATCH`

## KX-IPC-001
- Phase/surface: `6X-IPC` / `IAmazonKeyguardService.dismissWithPendingIntent (Stub method; Proxy method; tx UNKNOWN)`
- Source: `AmazonKeyguardService$2.dismissWithPendingIntent; fosservices disassembly lines 168487-168535; boot-fosframework Proxy lines 391141-391186`
- Evidence file: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log; decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c; fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`
- Caller: Binder caller UID from Binder.getCallingUid(); verified default package resolved from that UID
- Gate: checkUidPermission(android.permission.CONTROL_KEYGUARD) OR checkUidPermission(com.amazon.permission.AMAZON_CONTROL_KEYGUARD) in checkKeyguardPermissions; exact permission protection level and service-manager/SELinux gate UNKNOWN
- Identity/user scope: caller UID is retained and forwarded with verified package; no clearCallingIdentity/restoreCallingIdentity observed; target PendingIntent arguments are caller-supplied but downstream SystemUI receives verified UID/package
- Sink: IAmazonKeyguardServiceSystemUI.dismissWithPendingIntent; SystemUI keyguard dismissal/PendingIntent flow
- Effect: Static implementation confirms a privileged SystemUI/keyguard sink; no runtime success, HOME selection, package-state mutation, or exploit is established
- Confidence: **High static**; status `NEW_DIFFERENCE_STATIC_ONLY`

## KX-IPC-002
- Phase/surface: `6X-IPC` / `IAmazonKeyguardService.setAccessibilityInfo (Stub method; Proxy method; tx UNKNOWN)`
- Source: `AmazonKeyguardService$2.setAccessibilityInfo; fosservices disassembly lines 168690-168730; boot-fosframework Proxy lines 391292-391321`
- Evidence file: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log; decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c; fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`
- Caller: Binder caller UID from Binder.getCallingUid(); verified default package resolved from that UID
- Gate: checkUidPermission(android.permission.CONTROL_KEYGUARD) OR checkUidPermission(com.amazon.permission.AMAZON_CONTROL_KEYGUARD) in checkKeyguardPermissions; exact protection level and service-manager/SELinux gate UNKNOWN
- Identity/user scope: caller UID and verified package are forwarded to SystemUI; no identity clear observed; user ID is not explicit in the public method signature
- Sink: IAmazonKeyguardServiceSystemUI.setAccessibilityInfo; keyguard accessibility metadata/list state
- Effect: Static SystemUI state sink only; no runtime reachability, arbitrary package acceptance, HOME effect, or exploit is established
- Confidence: **High static**; status `NEW_DIFFERENCE_STATIC_ONLY`

## KX-IPC-003
- Phase/surface: `6X-IPC` / `IAmazonKeyguardService.setForegroundColor (Stub method; Proxy method; tx UNKNOWN)`
- Source: `AmazonKeyguardService$2.setForegroundColor; fosservices disassembly lines 168732-168795; boot-fosframework Proxy lines 391322-391349`
- Evidence file: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log; decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c; fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`
- Caller: Binder caller UID from Binder.getCallingUid(); verified default package resolved from that UID
- Gate: checkUidPermission(android.permission.CONTROL_KEYGUARD) OR checkUidPermission(com.amazon.permission.AMAZON_CONTROL_KEYGUARD) in checkKeyguardPermissions; exact protection level and service-manager/SELinux gate UNKNOWN
- Identity/user scope: caller UID and verified package are forwarded to SystemUI; no identity clear observed; user ID is not explicit in the public method signature
- Sink: IAmazonKeyguardServiceSystemUI.setForegroundColor; keyguard foreground color/presentation state
- Effect: Static SystemUI presentation sink only; no runtime reachability, arbitrary caller acceptance, HOME effect, or exploit is established
- Confidence: **High static**; status `NEW_DIFFERENCE_STATIC_ONLY`

## 6X-OTA-01
- Phase/surface: `6X-OTA` / `version/provenance`
- Source: `7.3.3.1 adjacent OTA manifest`
- Evidence file: `firmware/manifests/OTA-20260803-01/README.md:1-30`
- SHA-256: `3b7971859d4df3b85a671ab5340d3ad9bb2efb8501c2f09ec71374ac74abf7a5`
- Caller: OTA privileged lifecycle is not established by this file alone
- Gate: manifest metadata records product/version/key_type; no runtime install gate is exercised
- Identity/user scope: PS7331.4463N package identity only; installed baseline is PS7330.4104N; runtime UID/SELinux UNKNOWN
- Sink: No caller-to-writer inference; no exact installed-build post-install or rollback sink
- Effect: NONE
- Confidence: **high**; status `excluded_adjacent_version`

## 6X-OTA-02
- Phase/surface: `6X-OTA` / `host extraction provenance`
- Source: `selected/compiled-02 debugfs-derived manifests`
- Evidence file: `firmware/extracted/PS7331/selected/extraction-manifest.tsv:1-10; firmware/extracted/PS7331/compiled-02/extraction-manifest.tsv:1-12`
- SHA-256: `b098f85287a729d03cfac1ac6f767a3ba6a15ce8c65d7f9e581cbbed75448a74;7da7040b4c7454084d8c30452edc05d4c68ce3813fe20700d4016036e4097716`
- Caller: No installer/recovery caller; extraction is host-side
- Gate: file list and per-output SHA-256 only; no package signature, recovery, or execution gate
- Identity/user scope: Derived artifact identity only; runtime process/UID/SELinux UNKNOWN
- Sink: Framework/APK/VDEX outputs are analysis inputs, not post-install/native writer execution
- Effect: NONE
- Confidence: **high**; status `excluded_host_derived`

## 6X-OTA-03
- Phase/surface: `6X-OTA` / `post-install/native updater/recovery`
- Source: `existing Phase 6WH/6SD/6SP/6VB static corpus`
- Evidence file: `work/luna_worker_phase6wh_ota_residual_20260810.csv:2-7`
- SHA-256: `d88e35ec08d9ef0a55a3dbc17dc430b62d3b419810653542b6dd3077095cca24;4d0128ee85eec7b0c88716012858bef699f740907e46e854939c83a6c9e99077;d653e4a84898509781a333c56502087a83981781fcf6612d7026bfd79602b477;1136d4815ae63011522fead17ef743bc0daa57334ae6ebb3b4c05c1d09507c52;c99f6884fa298546b18722a5addb46ae35aff4c9f6003d8ad3ccaebe2edfdbd9`
- Caller: Privileged OTA lifecycle and recovery context are capability candidates; ordinary app/shell caller not shown
- Gate: metadata/hash/recovery-verification/controller gates precede handoff; indirect dispatch and complete caller join UNKNOWN
- Identity/user scope: UpdateSystem/recovery UID, SELinux domain, AVB rollback authority, and exact user scope UNKNOWN
- Sink: Edify extraction/block-image/cache/readlink paths reach high-privilege file/partition capability statically
- Effect: NONE
- Confidence: **high**; status `duplicate_no_new_gap`

## 6X-OTA-04
- Phase/surface: `6X-OTA` / `temporary path/symlink/canonicalization`
- Source: `existing Java/native staging and cache evidence`
- Evidence file: `work/luna_worker_ota_canonicalization_provenance_20260810.md:1-34`
- SHA-256: `4d6bc6518f8f45773ac517225d33e9f990ed1de5c590c2b68bf827482e057e64`
- Caller: SideloadMover/MakeFreeSpaceOnCache are static callers only; external input provenance UNKNOWN
- Gate: basename staging, rename/copy-delete fallback, readlink/unlink/free-space helpers; no proven no-follow/atomicity gate
- Identity/user scope: Path owner, race semantics, helper return dataflow, and writer identity UNKNOWN
- Sink: Potential staging/cache and native writer capability remains bounded; no arbitrary-path write established
- Effect: NONE
- Confidence: **high**; status `duplicate_unknown_boundary`

## 6XG-001
- Phase/surface: `6XG-GPL` / `input/uinput`
- Source: `kernel/mediatek/mt8183/4.4/drivers/input/misc/uinput.c:909-933; source SHA-256 98b41492311d9b9fb9ccbfe269a2fddc0fb436f3048b7887e1f6e5482d36211`
- Evidence file: `firmware/extracted/PS7331-SOURCE-20250617/platform.tar member kernel/mediatek/mt8183/4.4/drivers/input/misc/uinput.c`
- SHA-256: `98b41492311d9b9fb9ccbfe269a2fddc0fb436f3048b7887e1f6e5482d36211a`
- Caller: uinput_fops: read, write, unlocked_ioctl, compat_ioctl; misc_register
- Gate: CONFIG_INPUT_UINPUT=y (artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config:2146); no capable()/credential gate in inspected uinput source; final node mode/SELinux not joined
- Identity/user scope: No exact shipped native ELF open/write/ioctl callsite; package and UID/domain not established
- Sink: Synthetic input device creation and event injection into the kernel input graph; no direct PMS/HOME writer in scoped source
- Effect: Source capability is confirmed; shipped caller/reachability and package effect are not established
- Confidence: **high source, low caller**; status `NEW_SOURCE_EVIDENCE`

## 6XG-002
- Phase/surface: `6XG-GPL` / `power-supply sysfs`
- Source: `kernel/mediatek/mt8183/4.4/drivers/power/power_supply_sysfs.c:34-39,115-136,238-263; source SHA-256 54409386286849db4768d1b013b0151c3b8e52d3c5b4e434b52d8881364cc38e`
- Evidence file: `firmware/extracted/PS7331-SOURCE-20250617/platform.tar member kernel/mediatek/mt8183/4.4/drivers/power/power_supply_sysfs.c`
- SHA-256: `54409386286849db4768d1b013b0151c3b8e52d3c5b4e434b52d8881364cc38e`
- Caller: POWER_SUPPLY_ATTR store; power_supply_store_property -> power_supply_set_property
- Gate: CONFIG_POWER_SUPPLY=y; attributes are read-only by default and gain S_IWUSR only when psy->desc->property_is_writeable(psy, property)>0; no SELinux/domain caller join
- Identity/user scope: No exact shipped native sysfs write caller, package, UID, or domain established
- Sink: Battery/charger power-supply property mutation when the provider advertises a writable property; no package/HOME sink shown
- Effect: Generic source writer with provider callback gate; shipped path and caller unknown
- Confidence: **high source, low caller**; status `NEW_SOURCE_EVIDENCE`

## 6XG-003
- Phase/surface: `6XG-GPL` / `RPMB char device precise negative`
- Source: `kernel/mediatek/mt8183/4.4/drivers/char/rpmb/rpmb-mtk.c:2364-2544,2732-2764; source SHA-256 a6b070190ad8b97173c129509e6d8f8ae8c9f0d383bc349be44d9c919387c8d5`
- Evidence file: `firmware/extracted/PS7331-SOURCE-20250617/platform.tar member kernel/mediatek/mt8183/4.4/drivers/char/rpmb/rpmb-mtk.c`
- SHA-256: `a6b070190ad8b97173c129509e6d8f8ae8c9f0d383bc349be44d9c919387c8d5`
- Caller: rpmb_fops: open, release, unlocked_ioctl; .write=NULL; .read=NULL; cdev_add/device_create with RPMB_NAME
- Gate: CONFIG_RPMB=y; CONFIG_RPMB_INTF_DEV is not set in merged kernel.config:2235-2237; no local capable() proof; TEE/authentication is downstream, not a userspace identity proof
- Identity/user scope: Existing rpmb_svc process evidence does not identify a native open/ioctl callsite or package/UID; no ordinary-app caller established
- Sink: Authenticated persistent RPMB read/write/counter operations are available only through ioctl path in this fops; direct read/write file operations are source-negated
- Effect: Precise negative for read/write fops; ioctl sink remains source-only with caller/node ownership unresolved
- Confidence: **high source, medium classification**; status `PRECISE_NEGATIVE_PLUS_SOURCE`

## 6XG-004
- Phase/surface: `6XG-GPL` / `vendor/mediatek archive path`
- Source: `platform archive member listing: no vendor/mediatek path; Amazon source is device/amazon/kernel/driver; kernel MediaTek tree is kernel/mediatek/...`
- Evidence file: `firmware/extracted/PS7331-SOURCE-20250617/platform.tar`
- SHA-256: `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd`
- Caller: No source registration/API because path is absent
- Gate: Archive-level path absence; do not infer that a separate vendor tree is kernel build provenance
- Identity/user scope: No caller/package/UID can be assigned to an absent path
- Sink: No driver sink attributable to absent vendor/mediatek path; any vendor ELF/policy linkage requires an exact manifest/build reference
- Effect: Exact negative only; no reachability or vulnerability claim
- Confidence: **high for archive path negative**; status `PRECISE_NEGATIVE`

## 6XG-005
- Phase/surface: `6XG-GPL` / `uinput native/SELinux caller join negative`
- Source: `Existing exact-build native inventory and extracted vendor policy were scanned for a path-specific /dev/uinput caller and uinput node type/allow; no tuple found`
- Evidence file: `artifacts/phase5/phase5cs-native-analysis-20260804-01/native-inventory.csv`
- SHA-256: `9d1313d25cb45492d5656d03f05b7e60f5d037ccef15c20d9edec5e0fdbf17f9`
- Caller: No exact shipped ELF open/write/ioctl caller; no uinput-specific file-context/allow tuple identified in bounded artifacts
- Gate: Inventory/policy absence is a negative join only; it does not prove node absence or denial
- Identity/user scope: No package, UID, or SELinux domain established
- Sink: No confirmed input-injection or package/HOME effect from shipped native code
- Effect: Precise negative for caller/policy closure; source capability remains 6XG-001
- Confidence: **medium**; status `PRECISE_NEGATIVE`

## 6Y-001
- Phase/surface: `6Y-PERM` / `permission-definition`
- Source: `android.amazon.perm declares com.amazon.tv.developer.sdk.personalization.USE_SDK`
- Evidence file: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- SHA-256: `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`
- Caller: unknown/no bounded requester
- Gate: manifest declaration only; no service-side check joined; protection=0x0 (normal)
- Identity/user scope: owner android.amazon.perm sharedUserId=android.uid.system; holder/grant not established
- Sink: none joined in bounded exact manifests/disassembly
- Effect: no observed effect; low protection is a static candidate only
- Confidence: **high declaration; low reachability**; status `NEW_STATIC_LOW_PROTECTION_NO_SINK`

## 6Y-002
- Phase/surface: `6Y-PERM` / `permission-definition`
- Source: `android.amazon.perm declares com.amazon.tv.developer.sdk.content.USE_SDK`
- Evidence file: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- SHA-256: `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`
- Caller: unknown/no bounded requester
- Gate: manifest declaration only; no service-side check joined; protection=0x0 (normal)
- Identity/user scope: owner android.amazon.perm sharedUserId=android.uid.system; holder/grant not established
- Sink: none joined in bounded exact manifests/disassembly
- Effect: no observed effect; low protection is a static candidate only
- Confidence: **high declaration; low reachability**; status `NEW_STATIC_LOW_PROTECTION_NO_SINK`

## 6Y-003
- Phase/surface: `6Y-PERM` / `permission-definition`
- Source: `android.amazon.perm declares com.amazon.mw.permission.PLUGIN`
- Evidence file: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- SHA-256: `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`
- Caller: unknown/no bounded requester
- Gate: manifest declaration only; no service-side check joined; protection=0x1 (dangerous)
- Identity/user scope: owner android.amazon.perm sharedUserId=android.uid.system; holder/grant not established
- Sink: none joined in bounded exact manifests/disassembly
- Effect: no observed effect; dangerous protection is a static candidate only
- Confidence: **high declaration; low reachability**; status `NEW_STATIC_LOW_PROTECTION_NO_SINK`

## 6Y-004
- Phase/surface: `6Y-PERM` / `permission-definition`
- Source: `android.amazon.perm declares com.amazon.mw.permission.PLUGIN_CONSUMER`
- Evidence file: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- SHA-256: `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`
- Caller: unknown/no bounded requester
- Gate: manifest declaration only; no service-side check joined; protection=UNKNOWN (no protectionLevel attribute in bounded declaration)
- Identity/user scope: owner android.amazon.perm sharedUserId=android.uid.system; holder/grant not established
- Sink: none joined in bounded exact manifests/disassembly
- Effect: no observed effect; protection level cannot be safely decoded from this record
- Confidence: **medium declaration; low reachability**; status `NEW_STATIC_DEFINITION_NO_SINK`

## 6Z-001
- Phase/surface: `6Z-COMPONENT` / `OOBE-OTA-receiver`
- Source: `com.amazon.kindle.otter.oobe.BootAfterSystemOTAReceiver`
- Evidence file: `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java:27-61`
- SHA-256: `c29b32bf6874b245859357d926773193c15771a6eb254f97edac57541ae5cb90`
- Caller: SystemServer AmazonPackageManagerService.onBootPhase-550 plus PMS.isUpgrade
- Gate: protected RECEIVE_BOOT_AFTER_SYSTEM_OTA plus receiver action-OOBE-retail-demo guards; action=com.amazon.intent.action.BOOT_AFTER_SYSTEM_OTA
- Identity/user scope: system-server Context user-derived; numeric user UNKNOWN
- Sink: PackageHelper.enableComponent to OobeHomeActivity plus OOBEActivationHelper
- Effect: Enables OOBE activity and enters guarded OOBE activation; no proven Fire Launcher HOME setter
- Confidence: **high**; status `STATIC_CONFIRMED_NUMERIC_USER_UNKNOWN`

## 6Z-002
- Phase/surface: `6Z-COMPONENT` / `OOBE-settings`
- Source: `com.amazon.kindle.otter.oobe.commons.OOBEActivationHelper`
- Evidence file: `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java:29-34;53-56`
- SHA-256: `6ebcb7eef7a03459a76b9c21cd59b61a30947f2b00a5624a4646825b8e3223d2`
- Caller: BootAfterSystemOTAReceiver guarded lifecycle sender
- Gate: protected OTA lifecycle plus incremental-OOBE branch; no ordinary caller path; action=guarded BootAfterSystemOTA branch
- Identity/user scope: ContentResolver user inherited from receiver Context; numeric user UNKNOWN
- Sink: SettingsDBUtils to Settings.Secure-Global user_setup_complete=0 and isOOBEActive=1
- Effect: Mutates setup-OOBE state only when lifecycle guard passes; no HOME or preferred-package sink
- Confidence: **high**; status `STATIC_SINK_CONFIRMED_EXACT_USER_UNKNOWN`

## 6Z-003
- Phase/surface: `6Z-COMPONENT` / `exported-receiver`
- Source: `com.amazon.dcpms.fos.service.lifecycle.pca.profileswitch.PCAActiveProfileReceiver`
- Evidence file: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:115-122`
- SHA-256: `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`
- Caller: upstream producer UNKNOWN; exported entry has no component permission in saved manifest
- Gate: manifest action gate plus PROGRAM_ID and PACKAGE_NAME extras; action=com.amazon.device.ACTION_ACTIVE_PROFILE_UPDATED
- Identity/user scope: receiver application user scope and cross-user acceptance UNKNOWN
- Sink: CDE profile type and OS user type and active-app list persistence to DeviceExperienceModeEvaluator.evaluate
- Effect: Updates DCPMS policy state; no SettingsProvider PMS HOME package-state or OTA sink
- Confidence: **medium**; status `STATIC_EXPORTED_POLICY_SINK_CALLER_UNKNOWN`

## 6Z-004
- Phase/surface: `6Z-COMPONENT` / `exported-protected-action-receiver`
- Source: `com.amazon.dcpms.fos.service.lifecycle.device.userswitch.DeviceUserSwitchReceiver`
- Evidence file: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:105-113`
- SHA-256: `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`
- Caller: system/framework USER_SWITCHED producer
- Gate: protected USER_SWITCHED gate; ordinary sender not established; action=android.intent.action.USER_SWITCHED
- Identity/user scope: receiver user and profile scope UNKNOWN
- Sink: CDE PCA-profile and OS-user persistence plus child active-app-list clear to evaluator
- Effect: Updates policy and profile state; no HOME PMS package-state or OTA sink
- Confidence: **high**; status `STATIC_PROTECTED_ACTION_POLICY_SINK_CALLER_UNKNOWN`

## 6Z-005
- Phase/surface: `6Z-COMPONENT` / `exported-permissioned-receiver`
- Source: `com.amazon.dcpms.fos.service.lifecycle.device.userswitch.AccountPropertyChangeReceiver`
- Evidence file: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:94-103`
- SHA-256: `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`
- Caller: producer UNKNOWN
- Gate: caller must satisfy AmazonAccountPropertyService.property.changed; permission protection and holder UNKNOWN; action=com.amazon.dcp.sso.action.AmazonAccountPropertyService.property.changed
- Identity/user scope: receiver user scope UNKNOWN
- Sink: CDE profile type and OS-user persistence to evaluator
- Effect: Policy persistence and evaluation only; no HOME PMS package-state or OTA sink
- Confidence: **medium**; status `STATIC_PERMISSION_HOLDER_UNKNOWN`

## 6Z-006
- Phase/surface: `6Z-COMPONENT` / `exported-permissioned-receiver`
- Source: `com.amazon.dcpms.fos.service.lifecycle.device.sync.GlobalContentSyncEventReceiver`
- Evidence file: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:145-153`
- SHA-256: `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`
- Caller: producer UNKNOWN
- Gate: GLOBAL_SYNC required; holder-protection and caller route UNKNOWN; action=com.amazon.intent.SYNC
- Identity/user scope: receiver exact user scope UNKNOWN
- Sink: JobIntentService to GlobalContentSyncEventService to ArcusSyncService.syncCDEPolicy
- Effect: Triggers CDE policy sync; no OTA recovery HOME or PMS package-state sink
- Confidence: **medium**; status `STATIC_PERMISSION_HOLDER_UNKNOWN`

## 6Z-007
- Phase/surface: `6Z-COMPONENT` / `ProductPolicy-system-server-init`
- Source: `ProductPolicyService via productpolicyservice_fosinit.xml`
- Evidence file: `artifacts/phase6bg-product-policy-readonly-20260805-01/productpolicyservice_fosinit.stderr.txt`
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Caller: init and system-server loader
- Gate: registered in-process fosinit; no exported app component or external caller evidence; action=init service registration
- Identity/user scope: system-server service identity; Binder publication and caller gate UNKNOWN
- Sink: ProductPolicy service registration only; no verified HOME package Settings or OTA sink in bounded corpus
- Effect: No exported component observed; service existence is not caller reachability
- Confidence: **medium**; status `STATIC_REGISTRATION_ONLY_CALLER_AND_SINK_UNKNOWN`

## 6Z-008
- Phase/surface: `6Z-COMPONENT` / `Settings-HOME-resource-and-PMS-state`
- Source: `default_home plus config_show_default_home=true plus per-user preferred-activities`
- Evidence file: `work/luna_worker_settings_home_resource_followup_20260810.md`
- SHA-256: `UNKNOWN_REPORT_FILE_HASH`
- Caller: Settings UI or shell read path; no new writer established
- Gate: DefaultHomePreferenceController resource gate; normal dashboard omits default_home; set-home-activity is existing writer boundary; action=android.intent.action.MAIN plus CATEGORY_HOME
- Identity/user scope: per-user PMS Settings state; exact shell authorization is existing PMS gate; no new caller route
- Sink: com.android.server.pm.Settings preferred-activities and persistent-preferred-activities plus effective HOME resolver
- Effect: Existing HOME resolver and preferred-state divergence only; no new shell-writable Settings or DeviceConfig key
- Confidence: **high**; status `CONFIRMED_EXISTING_BOUNDARY_DEDUPED`

## 6X-LIVE-001
- Phase/surface: `6X-LIVE` / `device identity`
- Source: `adb read-only snapshot`
- Evidence file: `adb/phase6x/PHASE6X-DEVICE-READONLY-20260810-01/getprop.stdout.txt`
- SHA-256: `9d6158ab236efb6b72489e2109f2220506048f0dc1c77a0230fde41f655e0ea5`
- Caller: adb shell getprop
- Gate: none; observation only
- Identity/user scope: serial G001LT0511550CFT; User 0 current
- Sink: build fingerprint
- Effect: PS7331.4463N/0031575863040; incremental 0031575863172; security patch 2024-08-01
- Confidence: **Confirmed observation**; status `OBSERVED_READ_ONLY`

## 6X-LIVE-002
- Phase/surface: `6X-LIVE` / `HOME User 0`
- Source: `cmd package resolve-activity`
- Evidence file: `adb/phase6x/PHASE6X-DEVICE-READONLY-20260810-01/home_user0.stdout.txt`
- SHA-256: `MISSING`
- Caller: shell read-only query
- Gate: resolver observation
- Identity/user scope: User 0
- Sink: formal HOME resolver
- Effect: com.amazon.firelauncher/.Launcher; priority 50
- Confidence: **Confirmed observation**; status `OBSERVED_READ_ONLY`

## 6X-LIVE-003
- Phase/surface: `6X-LIVE` / `HOME candidates User 0`
- Source: `cmd package query-activities`
- Evidence file: `adb/phase6x/PHASE6X-DEVICE-READONLY-20260810-01/home_candidates_user0.stdout.txt`
- SHA-256: `MISSING`
- Caller: shell read-only query
- Gate: resolver observation
- Identity/user scope: User 0
- Sink: candidate set
- Effect: Fire 50, Microsoft 0, FallbackHome -1000
- Confidence: **Confirmed observation**; status `OBSERVED_READ_ONLY`

## 6X-LIVE-004
- Phase/surface: `6X-LIVE` / `HOME candidates User 10`
- Source: `cmd package resolve/query-activities`
- Evidence file: `adb/phase6x/PHASE6X-CURRENT-SCOPE-READONLY-20260810-01/home_user10.stdout.txt`
- SHA-256: `90b0bcbb1461327869dd23bfe630d2c2d01971438248f0f8842bca931b5373af`
- Caller: shell read-only query
- Gate: resolver observation
- Identity/user scope: User 10 test profile
- Sink: candidate set
- Effect: FallbackHome only; Fire is user-scoped disabled in saved package dump
- Confidence: **Confirmed observation**; status `OBSERVED_READ_ONLY`

## 6X-LIVE-005
- Phase/surface: `6X-LIVE` / `Fire Launcher per-user state`
- Source: `dumpsys package com.amazon.firelauncher`
- Evidence file: `adb/phase6x/PHASE6X-CURRENT-SCOPE-READONLY-20260810-01/firelauncher_package.stdout.txt`
- SHA-256: `86b91e5270d8f737609fd64481d9d7414fdcb164a169a936d038dc58450336ef`
- Caller: shell read-only dump
- Gate: package-state observation
- Identity/user scope: User 0 enabled=0; User 10 enabled=2
- Sink: package state
- Effect: User 0 installed/visible/enabled; User 10 disabled; no cross-user User 0 effect observed
- Confidence: **Confirmed observation**; status `OBSERVED_READ_ONLY`

## 6X-LIVE-006
- Phase/surface: `6X-LIVE` / `preferred HOME record`
- Source: `dumpsys package preferred-xml`
- Evidence file: `adb/phase6x/PHASE6X-CURRENT-SCOPE-READONLY-20260810-01/preferred_activities.stdout.txt`
- SHA-256: `7750d564a29046d0eb9e6d5d0565389d38cd5f6b9b4d8010fdf54f5dd667a8c6`
- Caller: shell read-only dump
- Gate: preferred state observation
- Identity/user scope: User 0 record
- Sink: ordinary preferred activity
- Effect: preferred record names com.amazon.firelauncher/.Launcher with MAIN/HOME/DEFAULT filter
- Confidence: **Confirmed observation**; status `OBSERVED_READ_ONLY`

## 6X2-IPC-001
- Phase/surface: `6X2` / `IPC`
- Source: `UNKNOWN`
- Evidence file: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:16376-16534;16413-16464;16519-16524`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: external dump caller; UID UNKNOWN
- Gate: android.permission.DUMP protection semantics not re-derived in bounded corpus
- Identity/user scope: default/device settings user; explicit user overload absent
- Sink: Settings.System.putInt(screen_brightness)
- Effect: POSITIVE sink and gate; NEGATIVE for HOME/package/OTA
- Confidence: **UNKNOWN**; status `STATIC_SETTINGS_SINK_NOT_NEW`

## 6X2-IPC-002
- Phase/surface: `6X2` / `IPC`
- Source: `UNKNOWN`
- Evidence file: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:29308-29317;29345-29355;29384-29400;29517-29520;29570-29580`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: remote Binder caller UNKNOWN
- Gate: com.amazon.alexa.permission.MODE_SWITCH protection level/holder UNKNOWN
- Identity/user scope: USER_CURRENT=-2
- Sink: SecureSettingsHelper.putIntForUser(orientation_in_previous_mode)
- Effect: POSITIVE
- Confidence: **UNKNOWN**; status `STATIC_SETTINGS_SINK_NOT_NEW`

## 6X2-IPC-003
- Phase/surface: `6X2` / `IPC`
- Source: `UNKNOWN`
- Evidence file: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:27078-27265;27426-27435;28453-28456`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: system_server/input-monitor publisher; external caller UNKNOWN
- Gate: permission and protection UNKNOWN
- Identity/user scope: system/default secure scope; non-user overload
- Sink: Settings.Secure.putInt(camera_shutter_state)
- Effect: POSITIVE bounded callback sink; NEGATIVE external Binder reachability
- Confidence: **UNKNOWN**; status `STATIC_CALLBACK_SINK_NOT_NEW`

## 6X2-IPC-004
- Phase/surface: `6X2` / `IPC`
- Source: `UNKNOWN`
- Evidence file: `decompiled/jadx/settings/resources/AndroidManifest.xml; artifacts/phase6h/phase6h-framework-ipc-20260804-01/manifest-components.csv:202; artifacts/phase6w/exported-component-audit-20260805-01/high-impact-exported-candidates.csv:56`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: external sender UNKNOWN
- Gate: com.amazon.kindle.otter.oobe.OOBE_PERMISSION protection level and holder UNKNOWN
- Identity/user scope: receiver user scope UNKNOWN
- Sink: downstream Settings/HOME/package sink not joined
- Effect: POSITIVE exported declaration; NEGATIVE complete target sink
- Confidence: **UNKNOWN**; status `EXPORTED_PERMISSION_UNKNOWN_NO_NEW_CHAIN`

## 6X2-IPC-005
- Phase/surface: `6X2` / `IPC`
- Source: `UNKNOWN`
- Evidence file: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:94-103; work/luna_worker_phase6sv_exported_surface_20260810.csv:4`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: producer UNKNOWN
- Gate: com.amazon.dcp.sso.permission.AmazonAccountPropertyService.property.changed protection/holder UNKNOWN
- Identity/user scope: receiver user scope UNKNOWN
- Sink: CDE/profile persistence and evaluator; no HOME/PMS/OTA sink
- Effect: POSITIVE policy sink; NEGATIVE target sink
- Confidence: **UNKNOWN**; status `EXPORTED_POLICY_ONLY_DUPLICATE`

## 6X2-IPC-006
- Phase/surface: `6X2` / `IPC`
- Source: `UNKNOWN`
- Evidence file: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:95877-95954;97828-97986; work/luna_worker_amazonpm_caller_inventory_20260810.csv:2-3`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: production caller UNKNOWN; test-only callers excluded
- Gate: register: no local permission; deregister: creator UID equality gate; protection holder UNKNOWN
- Identity/user scope: user scope not explicit; receiver map only
- Sink: implicit receiver registration map; first package/HOME sink NOT_FOUND
- Effect: POSITIVE gate markers; NEGATIVE target sink
- Confidence: **UNKNOWN**; status `PROXY_RESIDUAL_DUPLICATE`

## 6X2-IPC-007
- Phase/surface: `6X2` / `IPC`
- Source: `UNKNOWN`
- Evidence file: `artifacts/phase6mc-alta-jadx-20260810-01/sources/com/amazon/alta/h2clientservice/H2ClientService.java:104-126;226-236; artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/Manifest.java:6-9`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: external client UNKNOWN
- Gate: signature BIND_SERVICE declaration; exact holder/grant join UNKNOWN
- Identity/user scope: trusted adult/child profile scope; exact user data-flow partial
- Sink: user creation/removal and profile Settings relay; no HOME/PMS component sink
- Effect: POSITIVE workflow sink; NEGATIVE HOME/package sink
- Confidence: **UNKNOWN**; status `EXPORTED_SERVICE_DUPLICATE`

## 6X2-IPC-008
- Phase/surface: `6X2` / `IPC`
- Source: `UNKNOWN`
- Evidence file: `artifacts/phase6mb-vending-jadx-20260810-01/base/sources/com/google/android/finsky/setup/dse/impl/DseService.java:272-484;576-603; output/tables/phase6qb-residual-inventory.csv:8-12`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: caller/package/account provenance UNKNOWN
- Gate: o() and qualification gates; exact permission protection UNKNOWN
- Identity/user scope: UserHandle.myUserId plus injected user/profile semantics UNKNOWN
- Sink: secure-settings-class writer; browser-default/install bookkeeping; no HOME/Fire writer
- Effect: POSITIVE bounded non-HOME sink; NEGATIVE target sink
- Confidence: **UNKNOWN**; status `VENDING_RESIDUAL_DUPLICATE`

## 6X2-OTA-001
- Phase/surface: `6X2` / `OTA`
- Source: `official OTA ZIP`
- Evidence file: `firmware/manifests/OTA-20260803-01/README.md; firmware/manifests/OTA-20260803-01/sha256sums.txt`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: official OTA ZIP
- Gate: PS7331.4463N trona release OTA; SHA-256 9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Historical README separately marks installed PS7330 mismatch
- Confidence: **UNKNOWN**; status `CONFIRMED`

## 6X2-OTA-002
- Phase/surface: `6X2` / `OTA`
- Source: `ZIP member inventory`
- Evidence file: `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/members.tsv`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: ZIP member inventory
- Gate: META-INF metadata otacert update-binary updater-script; .new.dat.br; transfer lists; boot/images
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Traditional signed BLOCK OTA
- Confidence: **UNKNOWN**; status `CONFIRMED`

## 6X2-OTA-003
- Phase/surface: `6X2` / `OTA`
- Source: `ZIP member inventory`
- Evidence file: `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/members.tsv`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: ZIP member inventory
- Gate: No payload.bin and no A/B postinstall executable member
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Postinstall executable route is negative for package-shape scope
- Confidence: **UNKNOWN**; status `NEGATIVE`

## 6X2-OTA-004
- Phase/surface: `6X2` / `OTA`
- Source: `updater-script assertions`
- Evidence file: `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/updater-script.txt`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: updater-script assertions
- Gate: Build date and ro.product.device trona assertions
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Static script gate only
- Confidence: **UNKNOWN**; status `CONFIRMED`

## 6X2-OTA-005
- Phase/surface: `6X2` / `OTA`
- Source: `SideloadMetadataChecker.check`
- Evidence file: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/dcp/ota/SideloadMetadataChecker.java:24-29`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: SideloadMetadataChecker.check
- Gate: Version signature-transition product and PVT checks
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Transition/downgrade controls are OTASettings gated
- Confidence: **UNKNOWN**; status `CONFIRMED`

## 6X2-OTA-006
- Phase/surface: `6X2` / `OTA`
- Source: `SideloadVerifier.verifySideloadWithRecoveryCheck`
- Evidence file: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/dcp/ota/SideloadVerifier.java:31-58`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: SideloadVerifier.verifySideloadWithRecoveryCheck
- Gate: Sanity metadata RecoverySystemWrapper.verifyPackage device state
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Platform verifier implementation not present in preserved Java
- Confidence: **UNKNOWN**; status `CONFIRMED`

## 6X2-OTA-007
- Phase/surface: `6X2` / `OTA`
- Source: `OSUpdateValidator.validateOSUpdate`
- Evidence file: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/device/software/ota/tasks/validate/OSUpdateValidator.java:73-78`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: OSUpdateValidator.validateOSUpdate
- Gate: Hash then RecoverySystem.verifyPackage then OSUpdatePropertiesValidator
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Call order is exact in source
- Confidence: **UNKNOWN**; status `CONFIRMED`

## 6X2-OTA-008
- Phase/surface: `6X2` / `OTA`
- Source: `SideloadMover.maybeMoveSideloadFile`
- Evidence file: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/dcp/ota/SideloadMover.java:31-44`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: SideloadMover.maybeMoveSideloadFile
- Gate: Basename destination and FileHelper.moveFile
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: No Java canonicalPath realpath lstat or O_NOFOLLOW marker
- Confidence: **UNKNOWN**; status `CONFIRMED`

## 6X2-OTA-009
- Phase/surface: `6X2` / `OTA`
- Source: `SideloadInstaller.installSideload`
- Evidence file: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/dcp/ota/SideloadInstaller.java:65-90`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: SideloadInstaller.installSideload
- Gate: Metadata/device checks then mover then installOSUpdate
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: WithoutRecoveryCheck branch is not proof of bypass because normal integrity path is separate
- Confidence: **UNKNOWN**; status `CONFIRMED`

## 6X2-OTA-010
- Phase/surface: `6X2` / `OTA`
- Source: `UpdateSystemWrapper.install`
- Evidence file: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/device/framework/UpdateSystemWrapper.java:33-43`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: UpdateSystemWrapper.install
- Gate: Path prefix remap settings write then UpdateSystem.install
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Recovery/native exec caller remains separate boundary
- Confidence: **UNKNOWN**; status `CONFIRMED`

## 6X2-OTA-011
- Phase/surface: `6X2` / `OTA`
- Source: `OTA controller holders`
- Evidence file: `artifacts/phase6j/ota-controller-holders-manifest-audit-20260805-02/com-amazon-dcp.manifest.txt; com-amazon-otter-forced-ota.manifest.txt`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: OTA controller holders
- Gate: com.amazon.dcp.ota.permission.CONTROLLER and PROCESS_UPDATES protected surface
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Holder evidence is privileged/controller capability
- Confidence: **UNKNOWN**; status `CONFIRMED`

## 6X2-OTA-012
- Phase/surface: `6X2` / `OTA`
- Source: `main to block-image registry`
- Evidence file: `findings/phase-6mm-updater-blockimage-closure.md; artifacts/phase6mm-updater-blockimage-20260810-01/block-image-registration.csv`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: main to block-image registry
- Gate: RegisterBlockImageFunction to RegisterFunction; block_image_update to BlockImageUpdateFn 0x40b8b8
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Static registration not execution
- Confidence: **UNKNOWN**; status `CONFIRMED`

## 6X2-OTA-013
- Phase/surface: `6X2` / `OTA`
- Source: `PackageExtractFileFn`
- Evidence file: `findings/phase-6kt-recovery-verifier-provenance.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: PackageExtractFileFn
- Gate: PackageExtractFileFn to ota_open to open and extraction fsync close
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Capability not reachability
- Confidence: **UNKNOWN**; status `CONFIRMED`

## 6X2-OTA-014
- Phase/surface: `6X2` / `OTA`
- Source: `BlockImageUpdateFn to WriteToPartition`
- Evidence file: `findings/phase-6kt-recovery-verifier-provenance.md; findings/phase-6mm-updater-blockimage-closure.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: BlockImageUpdateFn to WriteToPartition
- Gate: PerformBlockImageUpdate to WriteToPartition to ota_write to write
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: No execution or partition write
- Confidence: **UNKNOWN**; status `CONFIRMED`

## 6X2-OTA-015
- Phase/surface: `6X2` / `OTA`
- Source: `updater-script`
- Evidence file: `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/updater-script.txt`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: updater-script
- Gate: system vendor boot preloader lk tee1 tee2 spmfw sspm_1 cam_vpu1 cam_vpu2 cam_vpu3 and cache blocklist
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: No arbitrary target conclusion
- Confidence: **UNKNOWN**; status `CONFIRMED`

## 6X2-OTA-016
- Phase/surface: `6X2` / `OTA`
- Source: `MakeFreeSpaceOnCache`
- Evidence file: `artifacts/phase6mm-updater-blockimage-20260810-01/canonicalization-call-sites.csv; findings/phase-6mm-updater-blockimage-closure.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: MakeFreeSpaceOnCache
- Gate: 0x417bf0 to __readlink_chk 0x4ce4e8
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Callsite is path-related but impact is unknown
- Confidence: **UNKNOWN**; status `CONFIRMED`

## 6X2-OTA-017
- Phase/surface: `6X2` / `OTA`
- Source: `selected direct-call graph`
- Evidence file: `findings/phase-6mm-updater-blockimage-closure.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: selected direct-call graph
- Gate: No selected direct edge from readlink helper to extraction/block-image/write sinks
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Not binary-wide absence and not traversal proof
- Confidence: **UNKNOWN**; status `NEGATIVE`

## 6X2-OTA-018
- Phase/surface: `6X2` / `OTA`
- Source: `CacheSizeCheck and callers`
- Evidence file: `work/luna_worker_ota_canonicalization_provenance_20260810.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: CacheSizeCheck and callers
- Gate: Body return/error branches and all indirect dispatch not fully selected
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: No symlink/traversal test
- Confidence: **UNKNOWN**; status `UNKNOWN`

## 6X2-OTA-019
- Phase/surface: `6X2` / `OTA`
- Source: `platform recovery verifier`
- Evidence file: `findings/phase-6kt-recovery-verifier-provenance.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: platform recovery verifier
- Gate: RecoverySystemWrapper delegates to platform RecoverySystem; exact native verifier absent
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Do not infer AVB bypass
- Confidence: **UNKNOWN**; status `UNKNOWN`

## 6X2-OTA-020
- Phase/surface: `6X2` / `OTA`
- Source: `otacert and verifyPackage`
- Evidence file: `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/otacert.pem; artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/android/os/RecoverySystemWrapper.java:21-23`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: otacert and verifyPackage
- Gate: Certificate material plus verification API call boundary
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Full cryptographic implementation unknown
- Confidence: **UNKNOWN**; status `CONFIRMED`

## 6X2-OTA-021
- Phase/surface: `6X2` / `OTA`
- Source: `bootloader/recovery rollback index`
- Evidence file: `findings/phase-6kt-recovery-verifier-provenance.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: bootloader/recovery rollback index
- Gate: No exact rollback-index decision branch in saved corpus
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Date/version gates are not equivalent to anti-rollback proof
- Confidence: **UNKNOWN**; status `UNKNOWN`

## 6X2-OTA-022
- Phase/surface: `6X2` / `OTA`
- Source: `shell UID / ordinary app`
- Evidence file: `findings/phase-6kt-recovery-verifier-provenance.md; findings/phase-6j-ota-apk-deep-review.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: shell UID / ordinary app
- Gate: No saved caller chain from shell or ordinary APK to UpdateSystem.install/recovery writer
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Bounded negative not universal absence
- Confidence: **UNKNOWN**; status `NEGATIVE`

## 6X2-OTA-023
- Phase/surface: `6X2` / `OTA`
- Source: `installed device snapshot`
- Evidence file: `firmware/manifests/OTA-20260803-01/README.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: installed device snapshot
- Gate: Installed snapshot PS7330.4104N versus adjacent OTA PS7331.4463N
- Identity/user scope: PS7330
- Sink: UNKNOWN
- Effect: Keep historical mismatch separate from current PS7331 package facts
- Confidence: **UNKNOWN**; status `VERSION_MISMATCH`

## AC-001
- Phase/surface: `6X2` / `User 0 MAIN+HOME resolver`
- Source: `findings/phase-6cy-accessibility-reboot-unlock-result.md; output/tables/phase6cy-reboot-unlock-result.csv`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **confirmed**; status `TRUE_HOME_FIRE`

## AC-002
- Phase/surface: `6X2` / `Original Phase 4 Accessibility direct redirect`
- Source: `findings/phase-4b-assisted-workarounds.md; adb/phase4/PHASE4-ACCESSIBILITY-T01/measure/summary.tsv`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **confirmed**; status `FAILED_FOREGROUND_REDIRECT`

## AC-003
- Phase/surface: `6X2` / `PendingIntent GUI consent boundary`
- Source: `findings/phase-6cv-accessibility-pendingintent-gui-boundary.md; output/tables/phase6cv-accessibility-pendingintent-gui-boundary.csv`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **confirmed-boundary**; status `UNKNOWN_NOT_MEASURED`

## AC-004
- Phase/surface: `6X2` / `Microsoft retry Accessibility 350/1000/1800 ms`
- Source: `findings/phase-6cy-ms-targeted-accessibility-retry.md; output/tables/phase6cy-ms-targeted-accessibility-retry.csv`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **confirmed-but-nondeterministic**; status `FOREGROUND_REDIRECT`

## AC-005
- Phase/surface: `6X2` / `Reboot plus owner unlock Accessibility retry`
- Source: `findings/phase-6cy-accessibility-reboot-unlock-result.md; findings/phase-6hb-ms-accessibility-reboot-persistence.md`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **confirmed-foreground-only**; status `UNLOCK_AFTER_REDIRECT`

## AC-006
- Phase/surface: `6X2` / `Accessibility timeout 50 ms A/B`
- Source: `findings/phase-6cy-accessibility-timeout-ab-boundary.md; output/tables/phase6cy-accessibility-reboot-persistence.csv`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **confirmed-negative-optimization**; status `FOREGROUND_REDIRECT_NOT_ADOPTED`

## AC-007
- Phase/surface: `6X2` / `Accessibility consume/key-event path`
- Source: `adb/phase6cy/PHASE6CY-CONSUME-HOME-20260807-02/result.json; findings/phase-6cy-accessibility-adb-pause-boundary.md`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **confirmed-boundary**; status `FAILED_OR_PARTIAL_FOREGROUND`

## AC-008
- Phase/surface: `6X2` / `UsageStats public third-party route`
- Source: `adb/phase6ac/PHASE6AC-RO-20260805-01/pm_dump.stdout.txt; adb/phase6ao/PHASE6AO-RO-20260805-01/package_dump_full.stdout.txt`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **unknown**; status `UNKNOWN_NOT_VALIDATED`

## AC-009
- Phase/surface: `6X2` / `ADB-connected host foreground monitor`
- Source: `findings/phase-6iq-adb-foreground-fallback.md; adb/phase6iq/PHASE6IQ-ADB-MONITOR-20260807-05/`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **confirmed-but-not-approved**; status `FOREGROUND_REDIRECT_CLOSED`

## AC-010
- Phase/surface: `6X2` / `Unlock workaround / keyguard bypass`
- Source: `findings/phase-6hb-ms-accessibility-reboot-persistence.md; findings/phase-6cy-accessibility-reboot-unlock-result.md`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **unknown**; status `UNKNOWN_NOT_A_WORKAROUND`

## AC-011
- Phase/surface: `6X2` / `Transparent resident assist candidate`
- Source: `tools/phase4-accessibility/README.md; tools/phase4-accessibility/src/org/fireosresearch/phase4/redirect/LauncherRedirectService.java`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **conditional**; status `SAFE_FOREGROUND_ASSIST_ONLY`

## 6X2-ROUTES-001
- Phase/surface: `6X2` / `OOBE receiver -> exact numeric user -> setup/component sink`
- Source: `UNKNOWN`
- Evidence file: `findings/phase-6z-evidence-index.md; work/luna_worker_phase6z_components_20260810.csv rows 6Z-001/002; artifacts/phase6mg-oobe-helper-scope-20260810-01/`
- SHA-256: `d666aab4deae3bd37ddbc528dd63680256318b709a467659925b3952ef19829c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **UNKNOWN**; status `untested_host_only`

## 6X2-ROUTES-002
- Phase/surface: `6X2` / `DCPMS exported lifecycle receiver -> producer/permission -> profile-policy sink`
- Source: `UNKNOWN`
- Evidence file: `work/luna_worker_phase6z_components_20260810.csv rows 6Z-003/005/006; artifacts/phase6bk/protected-broadcast-expanded-20260810-01/`
- SHA-256: `d666aab4deae3bd37ddbc528dd63680256318b709a467659925b3952ef19829c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **UNKNOWN**; status `untested_host_only`

## 6X2-ROUTES-003
- Phase/surface: `6X2` / `ProductPolicy fosinit registration -> Binder publication -> caller gate`
- Source: `UNKNOWN`
- Evidence file: `work/luna_worker_phase6z_components_20260810.csv row 6Z-007; artifacts/phase6bg-product-policy-readonly-20260805-01/; findings/phase-6x-report.md`
- SHA-256: `d666aab4deae3bd37ddbc528dd63680256318b709a467659925b3952ef19829c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **UNKNOWN**; status `untested_host_only`

## 6X2-ROUTES-004
- Phase/surface: `6X2` / `AmazonActivityManager preWarmApplicationForUser -> identity/user propagation -> process/state sink`
- Source: `UNKNOWN`
- Evidence file: `findings/phase-6x-prewarm-authorization.md; work/luna_worker_phase6up_asp_prewarm_closure_20260810.csv; artifacts/phase6bk/ipc-ota-closure-20260810-02/`
- SHA-256: `d666aab4deae3bd37ddbc528dd63680256318b709a467659925b3952ef19829c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **UNKNOWN**; status `untested_host_only`

## 6X2-ROUTES-005
- Phase/surface: `6X2` / `USE_SDK / PLUGIN / PLUGIN_CONSUMER declaration -> consumer/holder/grant -> sensitive sink`
- Source: `UNKNOWN`
- Evidence file: `work/luna_worker_phase6y_permission_20260810.csv; artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- SHA-256: `d666aab4deae3bd37ddbc528dd63680256318b709a467659925b3952ef19829c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **UNKNOWN**; status `untested_host_only`

## 6X2-ROUTES-006
- Phase/surface: `6X2` / `OTA verifier/canonicalization -> indirect extraction/write sink`
- Source: `UNKNOWN`
- Evidence file: `findings/phase-6y-ota-staging-boundary.md; artifacts/phase6mk-updater-dispatch-20260810-04/; artifacts/phase6kt/recovery-verifier-audit-20260810-01/`
- SHA-256: `d666aab4deae3bd37ddbc528dd63680256318b709a467659925b3952ef19829c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence: **UNKNOWN**; status `untested_host_only`

## 6AE-001
- Phase/surface: `6X3` / `OTA/OOBE`
- Source: `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java:27-61; decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96107-96126`
- Evidence file: `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java:27-61; decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96107-96126`
- SHA-256: `c29b32bf6874b245859357d926773193c15771a6eb254f97edac57541ae5cb90;ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: AmazonPackageManagerService.onBootPhase(550) -> BootAfterSystemOTAReceiver.onReceive
- Gate: isUpgrade + BOOT_AFTER_SYSTEM_OTA lifecycle; protected RECEIVE_BOOT_AFTER_SYSTEM_OTA provenance; exact ordinary sender UNKNOWN
- Identity/user scope: No ordinary Binder caller; trusted system-server lifecycle identity; clearCallingIdentity UNKNOWN/NOT APPLICABLE; Context-derived numeric user UNKNOWN
- Sink: PackageHelper.enableComponent(OobeHomeActivity); OOBEActivationHelper.activateOOBEIF
- Effect: Component/setup-state sink statically confirmed; no proven Fire HOME selector or runtime effect
- Confidence: **STATIC_LIFECYCLE_SINK_CALLER_AND_USER_UNKNOWN**; status `STATIC_LIFECYCLE_SINK_CALLER_AND_USER_UNKNOWN`

## 6AE-002
- Phase/surface: `6X3` / `OTA/OOBE settings`
- Source: `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java:29-34,53-56`
- Evidence file: `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java:29-34,53-56`
- SHA-256: `6ebcb7eef7a03459a76b9c21cd59b61a30947f2b00a5624a4646825b8e3223d2`
- Caller: BootAfterSystemOTAReceiver guarded branch -> OOBEActivationHelper
- Gate: Same protected OTA lifecycle guard; ordinary caller UNKNOWN
- Identity/user scope: No Binder caller in helper path; identity inheritance from receiver Context; clearCallingIdentity UNKNOWN; ContentResolver/Context user inherited; numeric user UNKNOWN
- Sink: SettingsDBUtils -> Settings.Secure user_setup_complete=0 and isOOBEActive=1
- Effect: Setup/OOBE settings mutation only when lifecycle predicate passes; no HOME/PMS writer
- Confidence: **STATIC_SETTINGS_SINK_USER_UNKNOWN**; status `STATIC_SETTINGS_SINK_USER_UNKNOWN`

## 6AE-003
- Phase/surface: `6X3` / `DevicePolicy/profile`
- Source: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:115-122; work/luna_worker_phase6z_components_20260810.csv:4`
- Evidence file: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:115-122; work/luna_worker_phase6z_components_20260810.csv:4`
- SHA-256: `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`
- Caller: PCAActiveProfileReceiver <- com.amazon.device.ACTION_ACTIVE_PROFILE_UPDATED -> DeviceExperienceModeEvaluator.evaluate
- Gate: Receiver exported with no local permission marker in saved manifest; producer, protection/holder, and sender UNKNOWN
- Identity/user scope: Broadcast receiver identity; Binder caller/clearCallingIdentity not present in bounded receiver evidence; Receiver application user and cross-user acceptance UNKNOWN
- Sink: CDE profile type/OS user type/active-app persistence feeding policy evaluator
- Effect: Policy/profile sink confirmed statically; no SettingsProvider, PMS, HOME, or OTA sink joined
- Confidence: **STATIC_EXPORTED_POLICY_SINK_CALLER_GATE_USER_UNKNOWN**; status `STATIC_EXPORTED_POLICY_SINK_CALLER_GATE_USER_UNKNOWN`

## 6AE-004
- Phase/surface: `6X3` / `DevicePolicy/profile`
- Source: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:105-113; work/luna_worker_phase6z_components_20260810.csv:5`
- Evidence file: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:105-113; work/luna_worker_phase6z_components_20260810.csv:5`
- SHA-256: `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`
- Caller: DeviceUserSwitchReceiver <- android.intent.action.USER_SWITCHED -> CDE/PCA policy persistence
- Gate: Protected USER_SWITCHED producer is system/framework; ordinary sender not established
- Identity/user scope: Lifecycle receiver context; no Binder caller or clearCallingIdentity evidence in bounded slice; Receiver user/profile scope UNKNOWN
- Sink: CDE PCA-profile and OS-user persistence; child active-app-list clear to evaluator
- Effect: Policy/profile state effect only; no HOME/PMS package-state or OTA sink
- Confidence: **STATIC_PROTECTED_POLICY_SINK_CALLER_USER_UNKNOWN**; status `STATIC_PROTECTED_POLICY_SINK_CALLER_USER_UNKNOWN`

## 6AE-005
- Phase/surface: `6X3` / `service-registration/ProductPolicy`
- Source: `artifacts/phase6bg-product-policy-readonly-20260805-01/productpolicyservice_fosinit.stderr.txt:registration record; output/call-graphs/phase6jd-fosinit-registration-flow.mmd`
- Evidence file: `artifacts/phase6bg-product-policy-readonly-20260805-01/productpolicyservice_fosinit.stderr.txt:registration record; output/call-graphs/phase6jd-fosinit-registration-flow.mmd`
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Caller: fosinit productpolicyservice registration -> ProductPolicyService Binder publication
- Gate: init/system-server loader and in-process fosinit registration; external caller and Binder permission gate UNKNOWN
- Identity/user scope: system-server/service identity; clearCallingIdentity UNKNOWN; User scope UNKNOWN; no method argument/sink recovered in registration-only input
- Sink: ProductPolicy service registration only; exact downstream state sink NOT FOUND
- Effect: Registration is capability evidence only, not a vulnerability or callable route
- Confidence: **REGISTRATION_ONLY_CALLER_GATE_USER_SINK_UNKNOWN**; status `REGISTRATION_ONLY_CALLER_GATE_USER_SINK_UNKNOWN`

## 6AE-006
- Phase/surface: `6X3` / `Framework IPC/prewarm`
- Source: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40534; proxy:394721; findings/phase-6x-prewarm-authorization.md:114-121`
- Evidence file: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40534; proxy:394721; findings/phase-6x-prewarm-authorization.md:114-121`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;895cf94b87d92b16af24ff9f1b3d18309d504dec9ffd928399e7b6ff4fbff92a`
- Caller: AmazonActivityManagerImpl -> IAmazonActivityManager.preWarmApplicationForUser -> BinderService
- Gate: checkCallingPermission(com.amazon.permission.APP_PREWARM); result consumption in bounded method UNKNOWN; service-manager/SELinux gate UNKNOWN
- Identity/user scope: clearCallingIdentity observed after permission check; restore path present; caller UID handling beyond slice UNKNOWN; Explicit user int supplied; cross-user validation UNKNOWN
- Sink: IPackageManager.getApplicationInfo(target,1024,user) -> PreWarmCacheHelper -> ActivityManagerService.startProcessLocked(...,prewarm,...)
- Effect: Process-start/cache sink statically confirmed; no component-state, HOME, OTA, or privilege transition observed
- Confidence: **STATIC_AUTHORIZATION_ANOMALY_CANDIDATE_CALLER_USER_UNKNOWN**; status `STATIC_AUTHORIZATION_ANOMALY_CANDIDATE_CALLER_USER_UNKNOWN`

## 6AE-007
- Phase/surface: `6X3` / `permission declaration -> sensitive sink`
- Source: `work/luna_worker_phase6y_permission_20260810.csv:2-5; artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt:permission records`
- Evidence file: `work/luna_worker_phase6y_permission_20260810.csv:2-5; artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt:permission records`
- SHA-256: `4b0ac817fe8cd35f68e243cb9eed0c97211463ad117610a9a04ceda76616529b;89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`
- Caller: android.amazon.perm declaration -> possible USE_SDK/PLUGIN consumer; exact consumer/caller not recovered
- Gate: USE_SDK protection=normal; PLUGIN=dangerous; PLUGIN_CONSUMER protection UNKNOWN; declaration is not an enforcement proof
- Identity/user scope: No Binder transaction or identity relay joined; User scope UNKNOWN
- Sink: No exact PMS/Settings/DevicePolicy/HOME/OTA sink found in bounded join
- Effect: Declaration-only evidence; no observed effect and no vulnerability conclusion
- Confidence: **DECLARATION_ONLY_NO_SINK**; status `DECLARATION_ONLY_NO_SINK`

## 6AE-008
- Phase/surface: `6X3` / `OTA staging`
- Source: `findings/phase-6y-ota-staging-boundary.md:20-38,80-88; source methods summarized in bounded report`
- Evidence file: `findings/phase-6y-ota-staging-boundary.md:20-38,80-88; source methods summarized in bounded report`
- SHA-256: `49614a27fc9c6c4d94ad01baf44b0d270bd8fc60fa9fd1ea8764913598b15330`
- Caller: external-storage sideload discovery -> SideloadInstaller verification -> UpdateSystemWrapper.install
- Gate: Metadata/device/signature/recovery verification gates; exact caller/SELinux/native flags UNKNOWN
- Identity/user scope: No Binder caller established in saved Java path; clearCallingIdentity UNKNOWN/NOT APPLICABLE; External-storage path and OTA lifecycle scope; exact user scope UNKNOWN
- Sink: SideloadMover basename + FileHelper.renameTo/copy-delete -> UpdateSystem.install high-risk update state transition
- Effect: Partition/update sink statically confirmed; no execution, partition effect, root, or bootloader effect observed
- Confidence: **STATIC_OTA_SINK_NATIVE_CALLER_SCOPE_UNKNOWN**; status `STATIC_OTA_SINK_NATIVE_CALLER_SCOPE_UNKNOWN`

## 6AF-OTA-001
- Phase/surface: `6X3` / `verifier-to-script`
- Source: `firmware/extracted/PS7331/META-INF/com/google/android/updater-script:1-2`
- Evidence file: `firmware/extracted/PS7331/META-INF/com/google/android/updater-script:1-2`
- SHA-256: `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248`
- Caller: recovery/Edify context implied; Java verifier caller remains privileged OTA path
- Gate: recovery/Edify context implied; Java verifier caller remains privileged OTA path
- Identity/user scope: UNKNOWN
- Sink: script admission gate before named targets; AVB/rollback implementation and caller handoff are not joined
- Effect: date gate aborts when package build date is older and product gate aborts when ro.product.device != trona; no rollback-index decision is evidenced
- Confidence: **UNRESOLVED_DATE_PRODUCT_NOT_ROLLBACK**; status `UNRESOLVED_DATE_PRODUCT_NOT_ROLLBACK`

## 6AF-OTA-002
- Phase/surface: `6X3` / `verifier-provenance`
- Source: `artifacts/phase6kt/recovery-verifier-audit-20260810-01/audit.json:binary_markers.update_binary[0..5]`
- Evidence file: `artifacts/phase6kt/recovery-verifier-audit-20260810-01/audit.json:binary_markers.update_binary[0..5]`
- SHA-256: `01e29ec3a2649d85d033ce7ce65034631ebb44ef00633e34a95b0eb063f317f9`
- Caller: RecoverySystemWrapper/RecoverySystem API boundary; native recovery identity not recovered
- Gate: RecoverySystemWrapper/RecoverySystem API boundary; native recovery identity not recovered
- Identity/user scope: UNKNOWN
- Sink: native updater capability is evidenced, while verifier-to-AVB/rollback-to-exec provenance remains absent
- Effect: binary markers include package_extract_file, block_image_* , /dev/block/by-name and readlink, but audit has no AVB or rollback-index implementation edge
- Confidence: **PROVENANCE_GAP_AVB_ROLLBACK**; status `PROVENANCE_GAP_AVB_ROLLBACK`

## 6AF-OTA-003
- Phase/surface: `6X3` / `canonicalization-to-cache`
- Source: `artifacts/phase6ne-updater-cache-flow-20260810-03/focus-disassembly.txt:CacheSizeCheck 0x414720-0x41475c`
- Evidence file: `artifacts/phase6ne-updater-cache-flow-20260810-03/focus-disassembly.txt:CacheSizeCheck 0x414720-0x41475c`
- SHA-256: `ca482551bea143f0c22ca3599655a6c10bfbb66033c9f99242f72048220797ee`
- Caller: PerformBlockImageUpdate caller at 0x409cb4 and 0x409cdc; native recovery identity only
- Gate: PerformBlockImageUpdate caller at 0x409cb4 and 0x409cdc; native recovery identity only
- Identity/user scope: UNKNOWN
- Sink: CacheSizeCheck normalizes helper failure into a nonzero error result; exact cache path/size argument provenance is unresolved
- Effect: 0x414730 BL MakeFreeSpaceOnCache; 0x414734 tbnz w0,#0x1f -> 0x414740; sign-bit error logs and returns w0=1, otherwise returns w0=0
- Confidence: **NEW_ERROR_BRANCH**; status `NEW_ERROR_BRANCH`

## 6AF-OTA-004
- Phase/surface: `6X3` / `cache-result-to-writer`
- Source: `artifacts/phase6ne-updater-cache-flow-20260810-03/return-branches.csv:CacheSizeCheck rows 7-8; PerformBlockImageUpdate rows 9-10`
- Evidence file: `artifacts/phase6ne-updater-cache-flow-20260810-03/return-branches.csv:CacheSizeCheck rows 7-8; PerformBlockImageUpdate rows 9-10`
- SHA-256: `95f469e697c636a2f09bcb6d3f27540f9d336a4bf042d2a5b33b37156a28b87b`
- Caller: PerformBlockImageUpdate direct callers at 0x409cb4/0x409cdc; recovery/update-binary gate
- Gate: PerformBlockImageUpdate direct callers at 0x409cb4/0x409cdc; recovery/update-binary gate
- Identity/user scope: UNKNOWN
- Sink: decision branches are proven, but the selected evidence does not prove whether either continuation reaches WriteToPartition for every input
- Effect: 0x409cb8 cbz w0,0x409cc8 and 0x409ce0 cbz w0,0x40b27c: zero result continues; nonzero branch target is not classified as a write bypass
- Confidence: **NEW_BOUNDED_NEGATIVE**; status `NEW_BOUNDED_NEGATIVE`

## 6AF-OTA-005
- Phase/surface: `6X3` / `cache-helper-indirect-edges`
- Source: `artifacts/phase6ne-updater-cache-flow-20260810-03/direct-call-edges.csv:MakeFreeSpaceOnCache 0x417858,0x4178b0,0x4178e0,0x417904,0x41792c,0x41793c,0x417a18,0x417a5c,0x417a6c,0x417c54,0x417c84,0x417d0c,0x417d1c,0x417d24,0x417d38,0x417d7c,0x417e60,0x417f74,0x417fb4,0x417fbc`
- Evidence file: `artifacts/phase6ne-updater-cache-flow-20260810-03/direct-call-edges.csv:MakeFreeSpaceOnCache 0x417858,0x4178b0,0x4178e0,0x417904,0x41792c,0x41793c,0x417a18,0x417a5c,0x417a6c,0x417c54,0x417c84,0x417d0c,0x417d1c,0x417d24,0x417d38,0x417d7c,0x417e60,0x417f74,0x417fb4,0x417fbc`
- SHA-256: `d653e4a84898509781a333c56502087a83981781fcf6612d7026bfd79602b477`
- Caller: MakeFreeSpaceOnCache entered from CacheSizeCheck 0x414730; no untrusted caller established
- Gate: MakeFreeSpaceOnCache entered from CacheSizeCheck 0x414730; no untrusted caller established
- Identity/user scope: UNKNOWN
- Sink: cache helper's filesystem operations include readlink-check at 0x417bf0 and unlink at 0x417ea8, but function-pointer/indirect target semantics remain unknown
- Effect: rows classify address-only targets as unresolved; they are not symbol-resolved direct calls and cannot be safely joined to extraction or writer sinks
- Confidence: **UNRESOLVED_INDIRECT_DISPATCH**; status `UNRESOLVED_INDIRECT_DISPATCH`

## 6AF-OTA-006
- Phase/surface: `6X3` / `canonicalization-no-follow`
- Source: `artifacts/phase6mk-updater-dispatch-20260810-04/canonicalization-context.csv:all 5 rows; artifacts/phase6md-native-updater-path-audit-20260810-02/summary.json:18-19`
- Evidence file: `artifacts/phase6mk-updater-dispatch-20260810-04/canonicalization-context.csv:all 5 rows; artifacts/phase6md-native-updater-path-audit-20260810-02/summary.json:18-19`
- SHA-256: `44f61840637e65d7a263b4912d340d834aba1b41b7a84dc7d20382e45fd1a726;6dec85cee148a60daba1e8c781f30370389c6d95ff787623cb6ac830f058a834`
- Caller: registry dispatch is indirect; selected native updater context only
- Gate: registry dispatch is indirect; selected native updater context only
- Identity/user scope: UNKNOWN
- Sink: canonicalization-to-extraction/writer argument flow and O_NOFOLLOW semantics remain unresolved
- Effect: readlink/readlinkat/__readlink_chk/realpath markers exist, but selected direct graph has zero canonicalization direct edges; this does not prove no-follow or absence of an indirect edge
- Confidence: **BOUNDED_NEGATIVE_NO_DIRECT_EDGE**; status `BOUNDED_NEGATIVE_NO_DIRECT_EDGE`

## 6AF-OTA-007
- Phase/surface: `6X3` / `extraction-to-named-writer`
- Source: `artifacts/phase6md-native-updater-path-audit-20260810-02/path-write-call-edges.csv:PackageExtractFileFn 0x4021b4/0x4022cc/0x40238c; WriteToPartition 0x413dcc-0x413f08`
- Evidence file: `artifacts/phase6md-native-updater-path-audit-20260810-02/path-write-call-edges.csv:PackageExtractFileFn 0x4021b4/0x4022cc/0x40238c; WriteToPartition 0x413dcc-0x413f08`
- SHA-256: `7dc9e3ef02a86d978d5973640bad0273288d83c71b8e7117eefb96c7bfffdbb`
- Caller: registered Edify handlers; recovery updater identity; ordinary app/shell caller not established
- Gate: registered Edify handlers; recovery updater identity; ordinary app/shell caller not established
- Identity/user scope: UNKNOWN
- Sink: capability-to-sink exists statically; per-call named-partition argument provenance and verifier acceptance state are not closed
- Effect: direct edges prove extraction/open and writer/open/write wrappers, but do not join archive entry/path arguments to the fixed script target for a particular invocation
- Confidence: **UNRESOLVED_ARGUMENT_PROVENANCE**; status `UNRESOLVED_ARGUMENT_PROVENANCE`

## 6AF-OTA-008
- Phase/surface: `6X3` / `caller-identity-handoff`
- Source: `artifacts/phase6kt/recovery-verifier-audit-20260810-01/audit.json:inputs.recovery_wrapper; inputs.update_system_wrapper; execution_policy`
- Evidence file: `artifacts/phase6kt/recovery-verifier-audit-20260810-01/audit.json:inputs.recovery_wrapper; inputs.update_system_wrapper; execution_policy`
- SHA-256: `01e29ec3a2649d85d033ce7ce65034631ebb44ef00633e34a95b0eb063f317f9`
- Caller: Java privileged OTA path calls RecoverySystem verification and UpdateSystem.install; native recovery/SELinux identity absent
- Gate: Java privileged OTA path calls RecoverySystem verification and UpdateSystem.install; native recovery/SELinux identity absent
- Identity/user scope: UNKNOWN
- Sink: verifier acceptance, UpdateSystem handoff, recovery exec, and updater registry are separate provenance domains
- Effect: audit explicitly records recovery/native execution false and does not recover the final native caller, execution flags, or SELinux domain
- Confidence: **UNRESOLVED_NATIVE_CALLER_IDENTITY**; status `UNRESOLVED_NATIVE_CALLER_IDENTITY`

## 6AG-001
- Phase/surface: `6X3` / `Amazon path absence`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence file: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: No exact shipped native caller for /proc/idme, /proc/amzn_drvs or lifecycle nodes
- Gate: Source modes/DT permission are insufficient; exact file_contexts/vendor-TE/domain absent
- Identity/user scope: Source modes/DT permission are insufficient; exact file_contexts/vendor-TE/domain absent
- Sink: Read/diagnostic or conditional test state only; package/HOME/root effect UNKNOWN
- Effect: No literal drivers/amazon/ member; actual device/amazon/kernel/driver/{amzn_idme,amzn_drv_test,amzn_logger,amzn_sign_of_life}.c; staging Kconfig/Makefile includes Amazon chain
- Confidence: **SOURCE_ONLY; platform.tar; source_scope_driver_audit; phase6uk**; status `SOURCE_ONLY; platform.tar; source_scope_driver_audit; phase6uk`

## 6AG-002
- Phase/surface: `6X3` / `Amazon /proc/amzn_drvs`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence file: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: No exact open/write caller; com.amazon.connectivitydiag presence is not a proc caller
- Gate: proc mode/label, init import and TE allow not jointly retained; caller UID/domain UNKNOWN
- Identity/user scope: proc mode/label, init import and TE allow not jointly retained; caller UID/domain UNKNOWN
- Sink: If built/allowed, factory test dispatcher can alter diagnostic/RTC-special state; no proved package/HOME/root effect
- Effect: amzn_drv_test.c:762-866 creates writable test children and dispatches copied input; Kconfig:65-68 default n; Makefile:28
- Confidence: **SOURCE_CAPABILITY_ONLY; amzn_drv_test hash 6c2309f996cacafaab35cce3935bcb725a5259211751af89df88d3732797029e; phase6nb/6nd**; status `SOURCE_CAPABILITY_ONLY; amzn_drv_test hash 6c2309f996cacafaab35cce3935bcb725a5259211751af89df88d3732797029e; phase6nb/6nd`

## 6AG-003
- Phase/surface: `6X3` / `Amazon /proc/idme`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence file: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: IDME HAL/library evidence only; no exact ELF open/read path-specific caller
- Gate: UID 1000 is source-side handling, not caller identity; exact file_contexts, vendor-TE allow and domain join incomplete
- Identity/user scope: UID 1000 is source-side handling, not caller identity; exact file_contexts, vendor-TE allow and domain join incomplete
- Sink: Possible device metadata disclosure; no write/package/HOME/root effect established
- Effect: amzn_idme.c:316-347 registers /proc/idme root/children with read fops; DT permission handling can clear write bits; mac_sec forces 0400/uid 1000
- Confidence: **SOURCE_PLUS_CONFIG; amzn_idme hash ab6484ae7a694412ec4eeabb67133ddd0c0af221076b6d989c8ab1fe7c84e61e; phase6so/6wi**; status `SOURCE_PLUS_CONFIG; amzn_idme hash ab6484ae7a694412ec4eeabb67133ddd0c0af221076b6d989c8ab1fe7c84e61e; phase6so/6wi`

## 6AG-004
- Phase/surface: `6X3` / `RPMB char ABI`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence file: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: rpmb_svc/process evidence does not identify exact native open + ioctl callsite or package owner
- Gate: No capable()/caller policy tuple established; node mode/file_contexts/domain UNKNOWN
- Identity/user scope: No capable()/caller policy tuple established; node mode/file_contexts/domain UNKNOWN
- Sink: Authenticated persistent-storage operation is a possible state sink; no package/HOME/root effect or low-privilege reachability proved
- Effect: drivers/char/rpmb/core.c rpmb_fops exposes unlocked_ioctl; .read/.write are NULL; device_create uses RPMB_NAME 0
- Confidence: **SOURCE_ONLY_CALLER_GAP; prior phase6xg/6so RPMB rows**; status `SOURCE_ONLY_CALLER_GAP; prior phase6xg/6so RPMB rows`

## 6AG-005
- Phase/surface: `6X3` / `MediaTek perf ioctl`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence file: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: No exact shipped native ELF path-specific open/write/ioctl caller in bounded native inventory
- Gate: 0664 is owner/group writable and world-readable, not world-writable; effective owner/group, file_contexts and domain allow UNKNOWN
- Identity/user scope: 0664 is owner/group writable and world-readable, not world-writable; effective owner/group, file_contexts and domain allow UNKNOWN
- Sink: Performance/governor/control state may be affected by an authorized writer; no PMS/HOME/root effect shown
- Effect: drivers/misc/mediatek/performance/perf_ioctl/perf_ioctl.c registers /proc/perfmgr/perf_ioctl; write/ioctl/compat_ioctl; source mode 0664
- Confidence: **SOURCE_PLUS_MODE; gpl inventory/phase6so**; status `SOURCE_PLUS_MODE; gpl inventory/phase6so`

## 6AG-006
- Phase/surface: `6X3` / `AUXADC factory/debug`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence file: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: No exact shipped native caller for AUXADC ioctl or writable sysfs/proc attributes
- Gate: No capable() proof, exact mode/owner, file_contexts or TE caller allow; UID/domain UNKNOWN
- Identity/user scope: No capable() proof, exact mode/owner, file_contexts or TE caller allow; UID/domain UNKNOWN
- Sink: ADC/register diagnostic and calibration/hardware-read state may be affected; no package/HOME/root effect established
- Effect: mtk_auxadc.c:553-667 ioctl/compat ioctl; :1515-1651 attrs and writable dump/status controls; module init
- Confidence: **SOURCE_PLUS_IMAGE_MARKER; mtk_auxadc hash 5ffbce942417fc6aca773d90e4c6935f508087f9a80d96138a7ecc30561ed327; source_scope audit**; status `SOURCE_PLUS_IMAGE_MARKER; mtk_auxadc hash 5ffbce942417fc6aca773d90e4c6935f508087f9a80d96138a7ecc30561ed327; source_scope audit`

## 6AG-007
- Phase/surface: `6X3` / `PMIC debugfs`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence file: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: No exact shipped native debugfs writer or caller
- Gate: Source debugfs entries are not a policy proof; exact debugfs type, file_contexts/TE and domain UNKNOWN
- Identity/user scope: Source debugfs entries are not a policy proof; exact debugfs type, file_contexts/TE and domain UNKNOWN
- Sink: Potential PMIC register/debug state effect if writable surface is exposed; no package/HOME/root effect
- Effect: upmu_debugfs.c:323-351 creates mtk_pmic debugfs/sysfs entries including writable dump_pmic_reg
- Confidence: **SOURCE_ONLY_POLICY_GAP; upmu_debugfs hash db8dfc551225586a717af6cc96057b8d810548cfb5d5693b8ec092; phase6uk**; status `SOURCE_ONLY_POLICY_GAP; upmu_debugfs hash db8dfc551225586a717af6cc96057b8d810548cfb5d5693b8ec092; phase6uk`

## 6AG-008
- Phase/surface: `6X3` / `Input touchscreen/factory proc`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence file: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: No exact shipped native proc/sysfs write caller in bounded corpus
- Gate: No joined node mode/file_contexts/TE/domain evidence; caller identity UNKNOWN
- Identity/user scope: No joined node mode/file_contexts/TE/domain evidence; caller identity UNKNOWN
- Sink: Possible touch firmware/calibration/input-state mutation; no package/HOME/root effect proved
- Effect: MTK/Focaltech touchscreen source includes debug/factory/proc helpers under drivers/input/touchscreen/mediatek; exact write handlers vary by selected IC
- Confidence: **SOURCE_VARIANT_UNRESOLVED; tar member scan; phase6me broad inventory**; status `SOURCE_VARIANT_UNRESOLVED; tar member scan; phase6me broad inventory`

## 6AG-009
- Phase/surface: `6X3` / `power-supply writer cross-check`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence file: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: No exact shipped native writer, package, UID or domain; generic store is not a caller
- Gate: S_IWUSR is added conditionally by provider; SELinux/file_contexts/domain allow UNKNOWN
- Identity/user scope: S_IWUSR is added conditionally by provider; SELinux/file_contexts/domain allow UNKNOWN
- Sink: Battery/charger property mutation is provider-dependent; no package/HOME/root effect
- Effect: Generic power_supply_sysfs.c .store calls power_supply_set_property only when provider property_is_writeable()>0; existing phase6xg row
- Confidence: **DEDUP_CROSSCHECK_NOT_NEW; source hash 54409386286849db4768d1b013b0151c3b8e52d3c5b4e434b52d8881364cc38e; phase6xg**; status `DEDUP_CROSSCHECK_NOT_NEW; source hash 54409386286849db4768d1b013b0151c3b8e52d3c5b4e434b52d8881364cc38e; phase6xg`

## 6AG-010
- Phase/surface: `6X3` / `input/uinput cross-check`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence file: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: No exact shipped native ELF /dev/uinput open/write/ioctl caller; library/package markers absent
- Gate: No local capable()/credential gate found; node policy, UID/domain and caller allow UNKNOWN
- Identity/user scope: No local capable()/credential gate found; node policy, UID/domain and caller allow UNKNOWN
- Sink: Synthetic input injection can affect kernel input graph; no PMS/HOME/root effect
- Effect: uinput.c:909-933 misc registration with read/write/unlocked_ioctl/compat_ioctl; UI_DEV_CREATE/DESTROY and event writes
- Confidence: **DEDUP_CROSSCHECK_NOT_NEW; source hash 98b41492311d9b9fb9ccbfe269a2fddc0fb436f3048b7887e1f6e5482d36211a; phase6xg**; status `DEDUP_CROSSCHECK_NOT_NEW; source hash 98b41492311d9b9fb9ccbfe269a2fddc0fb436f3048b7887e1f6e5482d36211a; phase6xg`

## 6AG-011
- Phase/surface: `6X3` / `CMDQ/ION artifact boundary`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence file: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: ION libion/libion_mtk markers are library capability only; no top-level process consumer; CMDQ no exact ELF ioctl caller
- Gate: Policy allow/node metadata do not establish effective ordinary-app access or domain path
- Identity/user scope: Policy allow/node metadata do not establish effective ordinary-app access or domain path
- Sink: Potential DMA/display/memory-resource effect remains source/artifact-only; no package/HOME/root effect
- Effect: Existing source rows cover CMDQ ioctl and ION alloc/custom ioctl capability; this row records no new sink
- Confidence: **DEDUP_ARTIFACT_CALLER_GAP; phase6so/6wi/6xg**; status `DEDUP_ARTIFACT_CALLER_GAP; phase6so/6wi/6xg`

## R01
- Phase/surface: `6X3` / `User0 HOME`
- Source: `work/luna_worker_phase6ac_accessibility_review_20260810.csv; findings/phase-6cy-accessibility-reboot-unlock-result.md`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv; findings/phase-6cy-accessibility-reboot-unlock-result.md`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: User 0; Fire Launcher
- Gate: 已整合/已排除 as replacement; Resolver selection is not a writer; do not infer bypass
- Identity/user scope: User 0; Fire Launcher
- Sink: MAIN+HOME resolver
- Effect: Fire selected before/after; no third-party success rate claimed
- Confidence: **已整合/已排除 as replacement**; status `已整合/已排除 as replacement`

## R02
- Phase/surface: `6X3` / `User0 HOME`
- Source: `priority replay`
- Evidence file: `priority replay`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: User 0; ordinary caller
- Gate: 已排除; No setter
- Identity/user scope: User 0; ordinary caller
- Sink: preferred/set-home/priority
- Effect: historical mutation reached API, but no durable third-party HOME; exact rate not reported
- Confidence: **已排除**; status `已排除`

## R03
- Phase/surface: `6X3` / `package-state`
- Source: `work/luna_worker_phase6qe_existing_tests_20260810.csv; adb/phase6fa/; adb/phase6bl/`
- Evidence file: `work/luna_worker_phase6qe_existing_tests_20260810.csv; adb/phase6fa/; adb/phase6bl/`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: User 0; shell/ordinary caller
- Gate: 已排除; Protected-package rejection is not a privilege transition
- Identity/user scope: User 0; shell/ordinary caller
- Sink: Fire protected package and force-stop
- Effect: component enable and force-stop rejected before mutation; no success
- Confidence: **已排除**; status `已排除`

## R04
- Phase/surface: `6X3` / `package-state`
- Source: `work/luna_worker_phase6qe_existing_tests_20260810.csv; work/luna_worker_phase6ty_user0_fire_restoration_20260810.csv`
- Evidence file: `work/luna_worker_phase6qe_existing_tests_20260810.csv; work/luna_worker_phase6ty_user0_fire_restoration_20260810.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: User 0 versus child profile
- Gate: 已整合/已排除 as User0 route; No component-state replay or grant/revoke
- Identity/user scope: User 0 versus child profile
- Sink: Tahoe enable/component state
- Effect: Tahoe package enable alone did not expose child HOME; shell component enable rejected; child-scoped writer exists
- Confidence: **已整合/已排除 as User0 route**; status `已整合/已排除 as User0 route`

## R05
- Phase/surface: `6X3` / `User10 child/KFT`
- Source: `work/luna_worker_phase6ri_existing_results_20260810.csv; findings/phase-6er-kft-child-switch-attribution.md`
- Evidence file: `work/luna_worker_phase6ri_existing_results_20260810.csv; findings/phase-6er-kft-child-switch-attribution.md`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: User 10/11 child/profile; UserInfo.id
- Gate: 已整合/已排除 as User0; Private tx3 and user lifecycle are out of scope
- Identity/user scope: User 10/11 child/profile; UserInfo.id
- Sink: KFT launcher writer
- Effect: child HOME observed in existing lifecycle; no User0 success rate
- Confidence: **已整合/已排除 as User0**; status `已整合/已排除 as User0`

## R06
- Phase/surface: `6X3` / `DPM/Profile Owner`
- Source: `work/luna_worker_phase6qe_existing_tests_20260810.csv; findings/phase-6di-kft-dpm-backup-passive.md`
- Evidence file: `work/luna_worker_phase6qe_existing_tests_20260810.csv; findings/phase-6di-kft-dpm-backup-passive.md`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: owner/admin/profile scope; not ordinary app
- Gate: 已排除 as ordinary route/待驗證 caller provenance; No provisioning/removal or Binder transaction
- Identity/user scope: owner/admin/profile scope; not ordinary app
- Sink: DPM tx100 -> PMS tx73
- Effect: owner/admin gate observed; no active writer result
- Confidence: **已排除 as ordinary route/待驗證 caller provenance**; status `已排除 as ordinary route/待驗證 caller provenance`

## R07
- Phase/surface: `6X3` / `HOME resources`
- Source: `work/luna_worker_phase6vd_test_reconciliation_20260810.csv; findings/phase-6rs-ru-report.md`
- Evidence file: `work/luna_worker_phase6vd_test_reconciliation_20260810.csv; findings/phase-6rs-ru-report.md`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: build resource and overlay; runtime user not shown
- Gate: 已排除 as proof of HOME/待驗證 static join; No settings mutation or UI dispatch
- Identity/user scope: build resource and overlay; runtime user not shown
- Sink: default-home resource/overlay/UI
- Effect: resource/UI evidence only; runtime selection not measured
- Confidence: **已排除 as proof of HOME/待驗證 static join**; status `已排除 as proof of HOME/待驗證 static join`

## R08
- Phase/surface: `6X3` / `SystemUI/navigation`
- Source: `work/luna_worker_phase6x_ipc_20260810.csv; output/tables/phase6x2-control-surface.csv`
- Evidence file: `work/luna_worker_phase6x_ipc_20260810.csv; output/tables/phase6x2-control-surface.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: verified Binder UID/package; privileged gate
- Gate: 待驗證 host-only caller/transaction join; CONTROL_KEYGUARD gate and private SystemUI boundary; no guessed transaction
- Identity/user scope: verified Binder UID/package; privileged gate
- Sink: keyguard PendingIntent/SystemUI handoff
- Effect: static capability only; no runtime success
- Confidence: **待驗證 host-only caller/transaction join**; status `待驗證 host-only caller/transaction join`

## R09
- Phase/surface: `6X3` / `SystemUI/navigation`
- Source: `work/luna_worker_phase6vd_test_reconciliation_20260810.csv; work/luna_worker_phase6xg_driver_20260810.csv`
- Evidence file: `work/luna_worker_phase6vd_test_reconciliation_20260810.csv; work/luna_worker_phase6xg_driver_20260810.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: kernel input graph; shipped caller unknown
- Gate: 已排除 as formal HOME/待驗證 shipped caller; No input injection or node access
- Identity/user scope: kernel input graph; shipped caller unknown
- Sink: input/uinput/navigation event path
- Effect: 0/30 direct Accessibility redirect; uinput source capability only
- Confidence: **已排除 as formal HOME/待驗證 shipped caller**; status `已排除 as formal HOME/待驗證 shipped caller`

## R10
- Phase/surface: `6X3` / `Accessibility`
- Source: `work/luna_worker_phase6qe_existing_tests_20260810.csv; work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- Evidence file: `work/luna_worker_phase6qe_existing_tests_20260810.csv; work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: User 0; user consent/service state
- Gate: 已排除 as deterministic route/待驗證 consent; Do not enable Accessibility or install/update APK
- Identity/user scope: User 0; user consent/service state
- Sink: installed service binding
- Effect: service bound but callback empty; 0/30 direct route; GUI consent run not measured
- Confidence: **已排除 as deterministic route/待驗證 consent**; status `已排除 as deterministic route/待驗證 consent`

## R11
- Phase/surface: `6X3` / `Accessibility`
- Source: `work/luna_worker_phase6ac_accessibility_review_20260810.md; findings/phase-6cy-ms-targeted-accessibility-retry.md`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.md; findings/phase-6cy-ms-targeted-accessibility-retry.md`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: User 0; target foreground only
- Gate: 已整合 as limited alternative; Fire remains resolver winner; no unlock bypass
- Identity/user scope: User 0; target foreground only
- Sink: consented delayed foreground redirect
- Effect: retry variants: explicit 1/1, HOME 3/3 in cited run; reboot/unlock mixed 2/3 or 3/3; not deterministic
- Confidence: **已整合 as limited alternative**; status `已整合 as limited alternative`

## R12
- Phase/surface: `6X3` / `Accessibility`
- Source: `work/luna_worker_phase6ac_accessibility_review_20260810.csv; findings/phase-6cy-accessibility-timeout-ab-boundary.md`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.csv; findings/phase-6cy-accessibility-timeout-ab-boundary.md`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: User 0; foreground redirect
- Gate: 已排除/不採用; No timing optimization replay
- Identity/user scope: User 0; foreground redirect
- Sink: timeout A/B variant
- Effect: 50 ms variant 4/5 in cited observation; HOME reliability worse; not adopted
- Confidence: **已排除/不採用**; status `已排除/不採用`

## R13
- Phase/surface: `6X3` / `UsageStats`
- Source: `work/luna_worker_phase6ac_accessibility_review_20260810.md; adb/phase6ac/; adb/phase6ao/`
- Evidence file: `work/luna_worker_phase6ac_accessibility_review_20260810.md; adb/phase6ac/; adb/phase6ao/`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: ordinary app; PACKAGE_USAGE_STATS/app-op boundary
- Gate: 待驗證 host-only permission/consumer join; Do not add permission or use it as HOME writer
- Identity/user scope: ordinary app; PACKAGE_USAGE_STATS/app-op boundary
- Sink: third-party foreground observation
- Effect: 未驗證; no success rate
- Confidence: **待驗證 host-only permission/consumer join**; status `待驗證 host-only permission/consumer join`

## R14
- Phase/surface: `6X3` / `ADB monitor`
- Source: `findings/phase-6iq-adb-foreground-fallback.md; work/luna_worker_phase6vd_test_reconciliation_20260810.csv`
- Evidence file: `findings/phase-6iq-adb-foreground-fallback.md; work/luna_worker_phase6vd_test_reconciliation_20260810.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: ADB-connected host; not resident device route
- Gate: 已排除 as approved resident solution; No new ADB monitor or device contact
- Identity/user scope: ADB-connected host; not resident device route
- Sink: host ADB foreground relay
- Effect: 5/5 foreground relay in cited evidence; stops with ADB/monitor
- Confidence: **已排除 as approved resident solution**; status `已排除 as approved resident solution`

## R15
- Phase/surface: `6X3` / `OOBE/OTA`
- Source: `OTA replay`
- Evidence file: `OTA replay`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: system-server OTA lifecycle; numeric user unknown
- Gate: 已整合/待驗證 natural official OTA only; No broadcast injection
- Identity/user scope: system-server OTA lifecycle; numeric user unknown
- Sink: BootAfterSystemOTAReceiver -> OOBE activation
- Effect: static guarded path; no manual delivery/runtime success
- Confidence: **已整合/待驗證 natural official OTA only**; status `已整合/待驗證 natural official OTA only`

## R16
- Phase/surface: `6X3` / `OOBE/OTA`
- Source: `work/luna_worker_phase6z_components_20260810.csv; artifacts/phase6bk/protected-broadcast-expanded-20260810-01/`
- Evidence file: `work/luna_worker_phase6z_components_20260810.csv; artifacts/phase6bk/protected-broadcast-expanded-20260810-01/`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: child/profile lifecycle; producer and user handle incomplete
- Gate: 待驗證 host-only provenance; No lifecycle broadcast or profile mutation
- Identity/user scope: child/profile lifecycle; producer and user handle incomplete
- Sink: DCPMS lifecycle receiver -> profile policy
- Effect: host-only static chain; no runtime success
- Confidence: **待驗證 host-only provenance**; status `待驗證 host-only provenance`

## R17
- Phase/surface: `6X3` / `OTA`
- Source: `recovery`
- Evidence file: `recovery`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: PS7331 OTA artifact; controller/privileged path
- Gate: 已整合 static boundary/待驗證 verifier implementation; No sideload
- Identity/user scope: PS7331 OTA artifact; controller/privileged path
- Sink: metadata/signature/recovery verification
- Effect: static checks confirmed; no install success
- Confidence: **已整合 static boundary/待驗證 verifier implementation**; status `已整合 static boundary/待驗證 verifier implementation`

## R18
- Phase/surface: `6X3` / `OTA`
- Source: `work/luna_worker_phase6ab_ota_exact_20260810.csv; findings/phase-6mm-updater-blockimage-closure.md`
- Evidence file: `work/luna_worker_phase6ab_ota_exact_20260810.csv; findings/phase-6mm-updater-blockimage-closure.md`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: PS7331 recovery/updater; caller unknown
- Gate: 已排除 as ordinary route/因風險拒絕 runtime; No updater/recovery/partition execution; no bypass inference
- Identity/user scope: PS7331 recovery/updater; caller unknown
- Sink: native updater/block-image/partition writer
- Effect: writer capability confirmed statically; execution/partition effect 0 observed
- Confidence: **已排除 as ordinary route/因風險拒絕 runtime**; status `已排除 as ordinary route/因風險拒絕 runtime`

## R19
- Phase/surface: `6X3` / `app/IPC`
- Source: `work/luna_worker_phase6qf_existing_runtime_audit_20260810.csv; findings/phase-6q-evidence-index.md`
- Evidence file: `work/luna_worker_phase6qf_existing_runtime_audit_20260810.csv; findings/phase-6q-evidence-index.md`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: shell UID 2000; private service gate
- Gate: 已排除 method reachability; No unknown Binder transaction or handle guessing
- Identity/user scope: shell UID 2000; private service gate
- Sink: private Amazon service visibility/lookup
- Effect: names visible; private check/find denied/not found; no method success
- Confidence: **已排除 method reachability**; status `已排除 method reachability`

## R20
- Phase/surface: `6X3` / `app/IPC`
- Source: `work/luna_worker_phase6vd_test_reconciliation_20260810.csv; work/luna_worker_phase6tm_h2_permission_20260810.csv`
- Evidence file: `work/luna_worker_phase6vd_test_reconciliation_20260810.csv; work/luna_worker_phase6tm_h2_permission_20260810.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: external requester/holder/grant unknown
- Gate: 待驗證 host-only holder/requester join; No bind/call or guessed code
- Identity/user scope: external requester/holder/grant unknown
- Sink: H2 BIND_SERVICE custom permission
- Effect: signature gate confirmed; caller/sink unknown; no runtime call
- Confidence: **待驗證 host-only holder/requester join**; status `待驗證 host-only holder/requester join`

## R21
- Phase/surface: `6X3` / `app/IPC`
- Source: `output/tables/phase6x2-control-surface.csv; work/luna_worker_phase6z_components_20260810.csv`
- Evidence file: `output/tables/phase6x2-control-surface.csv; work/luna_worker_phase6z_components_20260810.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: producer and user scope unknown
- Gate: 待驗證 host-only caller/permission/user join; No broadcast replay or cross-user mutation
- Identity/user scope: producer and user scope unknown
- Sink: exported OOBE/account/profile receivers
- Effect: exported/static policy evidence only; target HOME/PMS sink not closed
- Confidence: **待驗證 host-only caller/permission/user join**; status `待驗證 host-only caller/permission/user join`

## R22
- Phase/surface: `6X3` / `app/IPC`
- Source: `work/luna_worker_phase6vd_test_reconciliation_20260810.csv; findings/phase-6a-untrusted-app-pi-smoke-evidence-index.md`
- Evidence file: `work/luna_worker_phase6vd_test_reconciliation_20260810.csv; findings/phase-6a-untrusted-app-pi-smoke-evidence-index.md`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: ordinary/untrusted app
- Gate: 已排除 bounded route; Private Binder out of scope; no APK/install
- Identity/user scope: ordinary/untrusted app
- Sink: untrusted PendingIntent/cross-user
- Effect: bounded smoke did not establish durable mutation; exact rate not claimed
- Confidence: **已排除 bounded route**; status `已排除 bounded route`

## R23
- Phase/surface: `6X3` / `settings`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv; work/luna_worker_phase6aa_ipc_residual_20260810.csv`
- Evidence file: `work/luna_worker_phase6wk_broad_surface_20260810.csv; work/luna_worker_phase6aa_ipc_residual_20260810.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: system/shell permission gates; user overload varies
- Gate: 已整合/待驗證 caller provenance; No settings write or settings modification
- Identity/user scope: system/shell permission gates; user overload varies
- Sink: SettingsProvider and generic settings writers
- Effect: static sink capability; no target HOME/package result
- Confidence: **已整合/待驗證 caller provenance**; status `已整合/待驗證 caller provenance`

## R24
- Phase/surface: `6X3` / `app/IPC`
- Source: `work/luna_worker_phase6qe_existing_tests_20260810.csv; work/luna_worker_phase6ty_user0_fire_restoration_20260810.csv`
- Evidence file: `work/luna_worker_phase6qe_existing_tests_20260810.csv; work/luna_worker_phase6ty_user0_fire_restoration_20260810.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: privileged/system or unknown production caller
- Gate: 待驗證 host-only provenance/已排除 replay; No grant/revoke/install/package mutation
- Identity/user scope: privileged/system or unknown production caller
- Sink: Amazon PM/Vending/package-state writers
- Effect: static writers and bounded negative caller closure; no ordinary User0 success
- Confidence: **待驗證 host-only provenance/已排除 replay**; status `待驗證 host-only provenance/已排除 replay`

## R25
- Phase/surface: `6X3` / `kernel/root`
- Source: `ioctl`
- Evidence file: `ioctl`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: retail node/caller/domain not joined
- Gate: 待驗證 host-only image/DT/relocation join; No node access
- Identity/user scope: retail node/caller/domain not joined
- Sink: driver CMDQ/ION/MDP nodes
- Effect: source/policy capability only; no node open/ioctl/effect
- Confidence: **待驗證 host-only image/DT/relocation join**; status `待驗證 host-only image/DT/relocation join`

## R26
- Phase/surface: `6X3` / `kernel/root`
- Source: `node write`
- Evidence file: `node write`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: shipped native caller unknown
- Gate: 已排除 as proven bypass/待驗證 caller only; No synthetic input
- Identity/user scope: shipped native caller unknown
- Sink: uinput/power-supply low-level path
- Effect: source capability only; no retail privilege transition
- Confidence: **已排除 as proven bypass/待驗證 caller only**; status `已排除 as proven bypass/待驗證 caller only`

## R27
- Phase/surface: `6X3` / `kernel/root`
- Source: `work/luna_worker_phase6vd_test_reconciliation_20260810.csv; findings/phase-5-evidence-index.md`
- Evidence file: `work/luna_worker_phase6vd_test_reconciliation_20260810.csv; findings/phase-5-evidence-index.md`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: device/root boundary
- Gate: 因風險拒絕; Exploit/root/payload execution explicitly excluded
- Identity/user scope: device/root boundary
- Sink: root/futex/rtmutex/privilege transition
- Effect: no approved device mutation; no success rate
- Confidence: **因風險拒絕**; status `因風險拒絕`

## R28
- Phase/surface: `6X3` / `architecture`
- Source: `work/luna_worker_phase6ad_untested_routes_20260810.md; work/luna_worker_phase6ty_user0_fire_restoration_20260810.csv`
- Evidence file: `work/luna_worker_phase6ad_untested_routes_20260810.md; work/luna_worker_phase6ty_user0_fire_restoration_20260810.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: system/in-process policy path; caller gate unknown
- Gate: 待驗證 host-only registration/permission join; No service call or policy mutation
- Identity/user scope: system/in-process policy path; caller gate unknown
- Sink: ProductPolicy/fosinit Binder publication
- Effect: static registration/sink markers; no callable transaction or HOME result
- Confidence: **待驗證 host-only registration/permission join**; status `待驗證 host-only registration/permission join`

## R29
- Phase/surface: `6X3` / `architecture`
- Source: `work/luna_worker_phase6ad_untested_routes_20260810.md; work/luna_worker_prewarm_identity_closure_20260810.csv`
- Evidence file: `work/luna_worker_phase6ad_untested_routes_20260810.md; work/luna_worker_prewarm_identity_closure_20260810.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: Amazon/system caller; user propagation incomplete
- Gate: 待驗證 host-only identity/user-flow join; No process launch or Binder invocation
- Identity/user scope: Amazon/system caller; user propagation incomplete
- Sink: ASP preWarmApplicationForUser
- Effect: static process/state sink candidate; no HOME/package success
- Confidence: **待驗證 host-only identity/user-flow join**; status `待驗證 host-only identity/user-flow join`
