# Phase 10 evidence index

Phase 10 expands the privilege/control audit to package-management, policy/profile, OTA, and driver caller boundaries. Missing edges remain UNKNOWN; static capability is not a privilege-escalation claim.

## WG-001
- Phase/surface: `6WL` / `6WG Framework IPC residual`
- Source: `work/luna_worker_phase6wg_ipc_residual_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: external dumpsys caller subject to DUMP; exact UID UNKNOWN
- Gate: android.permission.DUMP checked in dump; service-manager/SELinux rule UNKNOWN
- Identity/user scope: device/default settings user (explicit user overload absent)
- Sink: FireOsDisplayPowerControllerService$BinderService
- Effect: UNKNOWN
- Confidence/status: **static direct** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WG-002
- Phase/surface: `6WL` / `6WG Framework IPC residual`
- Source: `work/luna_worker_phase6wg_ipc_residual_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: system_server input-monitor caller/publisher; external Binder caller not recovered
- Gate: system_server/internal callback; permission and SELinux/service-manager gate UNKNOWN
- Identity/user scope: system/default secure-settings scope (non-user overload)
- Sink: InputFilterMonitorInputManagerServiceCallback
- Effect: UNKNOWN
- Confidence/status: **static direct** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WG-003
- Phase/surface: `6WL` / `6WG Framework IPC residual`
- Source: `work/luna_worker_phase6wg_ipc_residual_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: remote Binder caller with MODE_SWITCH; exact UID UNKNOWN
- Gate: com.amazon.alexa.permission.MODE_SWITCH enforced by checkCallingOrSelfPermission; service-manager/SELinux rule UNKNOWN
- Identity/user scope: USER_CURRENT/-2 passed to putIntForUser
- Sink: AlexaModeSwitchManagerService$AlexaModeSwitchAPIImpl
- Effect: UNKNOWN
- Confidence/status: **static direct** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6WL-ROW-004
- Phase/surface: `6WL` / `6WH OTA residual`
- Source: `work/luna_worker_phase6wh_ota_residual_20260810.csv`
- Evidence: `artifacts/phase6mk-updater-dispatch-20260810-04/registration-dispatch.csv:7,16,19-22; updater-script-entrypoints.csv:2-13; addresses 0x406b8c,0x406e0c,0x406ee4,0x406f2c,0x406f6c,0x406fac`
- SHA-256: `d88e35ec08d9ef0a55a3dbc17dc430b62d3b419810653542b6dd3077095cca24;4d0128ee85eec7b0c88716012858bef699f740907e46e854939c83a6c9e99077`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: NONE
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6WL-ROW-005
- Phase/surface: `6WL` / `6WH OTA residual`
- Source: `work/luna_worker_phase6wh_ota_residual_20260810.csv`
- Evidence: `artifacts/phase6ne-updater-cache-flow-20260810-03/direct-call-edges.csv:1-5,42-43; addresses 0x417bf0,0x417ea8,0x417eb0,0x409cb4,0x409cdc`
- SHA-256: `d653e4a84898509781a333c56502087a83981781fcf6612d7026bfd79602b477`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: NONE
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6WL-ROW-006
- Phase/surface: `6WL` / `6WH OTA residual`
- Source: `work/luna_worker_phase6wh_ota_residual_20260810.csv`
- Evidence: `artifacts/phase6my-bootafter-ota-package-helper-20260810-01/call-edges.csv:6MY-E03-E04,E08,E10`
- SHA-256: `1136d4815ae63011522fead17ef743bc0daa57334ae6ebb3b4c05c1d09507c52`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: NONE
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6WL-ROW-007
- Phase/surface: `6WL` / `6WH OTA residual`
- Source: `work/luna_worker_phase6wh_ota_residual_20260810.csv`
- Evidence: `artifacts/phase6j/phase6j-ota-controller-holders-20260805-01/controller-permission-context.txt:10537-10541,27271-27275`
- SHA-256: `d68768263846c87ffc6b1b1d100b5b5bcd34212d5605c4e3eb1085da8c67d1e0`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: NONE
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6WL-ROW-008
- Phase/surface: `6WL` / `6WH OTA residual`
- Source: `work/luna_worker_phase6wh_ota_residual_20260810.csv`
- Evidence: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/dcp/ota/SideloadMover.java:31-44; FileHelper.java:305-339`
- SHA-256: `59131cf032d8544cd44ea839ad63eb37993d2853b4925bf56d10ede721693f63;55a7f44a70735626be7ebde25e96812346f336fddbec2c87ca0fb709b980`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: NONE
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6WL-ROW-009
- Phase/surface: `6WL` / `6WH OTA residual`
- Source: `work/luna_worker_phase6wh_ota_residual_20260810.csv`
- Evidence: `firmware/extracted/PS7331/vbmeta.img absent; firmware/extracted/PS7331/META-INF/com/android/avb* absent; UpdateSystemWrapper.java:33-44`
- SHA-256: `c99f6884fa298546b18722a5addb46ae35aff4c9f6003d8ad3ccaebe2edfdbd9`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: NONE
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WI-01
- Phase/surface: `6WL` / `6WI native driver caller`
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `cmdq_driver.c=b3a54d37b4e498ff969a2717cb02cefc923ae6f39da32f5fd8529fe3dce6e899; kernel.config=eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04; Image=10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d; vendor_file_contexts=db5cd91b8d25170ad27809ace8cdbbd2a3f838ec72e2598a4f6b5a44953d322e`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: policy names device type only; no exact caller identity or framework/HOME/package sink
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WI-02
- Phase/surface: `6WL` / `6WI native driver caller`
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `ion.c=abac518864faed94439d75d204e8c16ea75cf3a74c93ee50e128e0f6928a6d63; kernel.config=eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04; vendor_file_contexts=db5cd91b8d25170ad27809ace8cdbbd2a3f838ec72e2598a4f6b5a44953d322e; native-inventory.csv=9d1313d25cb45492d5656d03f05b7e60f5d037ccef15c20d9edec5e0fdbf17f9`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: ION library labels are same_process_hal_file; no exact identity and no package/HOME/settings sink
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WI-03
- Phase/surface: `6WL` / `6WI native driver caller`
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `boot.img=cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b; Image=10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d; native-inventory.csv=9d1313d25cb45492d5656d03f05b7e60f5d037ccef15c20d9edec5e0fdbf17f9`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: no userland identity or sensitive sink identified
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WI-04
- Phase/surface: `6WL` / `6WI native driver caller`
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `amzn_idme.c=ab6484ae7a694412ec4eeabb67133ddd0c0af221076b6d989c8ab1fe7c84e61e; kernel.config=eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04; vendor_file_contexts=db5cd91b8d25170ad27809ace8cdbbd2a3f838ec72e2598a4f6b5a44953d322e`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: HAL service identity is privileged-domain context only; no exact package/HOME/PMS sink
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WI-05
- Phase/surface: `6WL` / `6WI native driver caller`
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `amzn_drv_test.c=6c2309f996cacafaab35cce3935bcb725a5259211751af89df88d3732797029e; libmt8183_diag.so=7147e161de7b3a8097bdf6079d0b414c147067d46e1f446138d041a63dd127d7; vendor_sepolicy.cil=82430bdb87b8a5f653110b635289489b99e82bdbe7bdc7a2e1ee5564e674e035`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: diagnostic HAL/domain name is not a proc caller and no package/HOME/privilege sink is joined
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WI-06
- Phase/surface: `6WL` / `6WI native driver caller`
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `vendor_file_contexts=db5cd91b8d25170ad27809ace8cdbbd2a3f838ec72e2598a4f6b5a44953d322e; vendor_sepolicy.cil=82430bdb87b8a5f653110b635289489b99e82bdbe7bdc7a2e1ee5564e674e035`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: rpmb_svc identity is a service observation; no package/HOME sink
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WI-07
- Phase/surface: `6WL` / `6WI native driver caller`
- Source: `work/luna_worker_phase6wi_driver_caller_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `phase6me input-manifest=ada254be9c56572282704924eea66e2852889ec73c0a65be4558f36f77d8250a; native-inventory.csv=9d1313d25cb45492d5656d03f05b7e60f5d037ccef15c20d9edec5e0fdbf17f9; vendor_file_contexts=db5cd91b8d25170ad27809ace8cdbbd2a3f838ec72e2598a4f6b5a44953d322e`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: HAL/service identity only; no package/HOME/settings sink
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WJ-01
- Phase/surface: `6WL` / `6WJ test reconciliation`
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: Saved resolver evidence remains Fire Launcher; static HOME setters/sinks do not establish ordinary caller reachability or a sustainable replacement.
- Confidence/status: **UNKNOWN** / `INTEGRATED`
- Scope: previous public Phase 9 corpus

## WJ-02
- Phase/surface: `6WL` / `6WJ test reconciliation`
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: Package-state writers exist in framework/Amazon code, but saved gates rejected ordinary mutation and no writer is shown to reach User-0 HOME sustainably.
- Confidence/status: **UNKNOWN** / `INTEGRATED`
- Scope: previous public Phase 9 corpus

## WJ-03
- Phase/surface: `6WL` / `6WJ test reconciliation`
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: Child/profile lifecycle and KFT component changes are real only for the target child/profile; final guards preserve User-0 Fire Launcher.
- Confidence/status: **UNKNOWN** / `INTEGRATED`
- Scope: previous public Phase 9 corpus

## WJ-04
- Phase/surface: `6WL` / `6WJ test reconciliation`
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: DPM tests show bounded owner/admin behavior but no ordinary sustainable HOME/package-state route; static DPM sinks remain gated and caller identity is incomplete.
- Confidence/status: **UNKNOWN** / `INTEGRATED`
- Scope: previous public Phase 9 corpus

## WJ-05
- Phase/surface: `6WL` / `6WJ test reconciliation`
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: Resource/default-home and overlay evidence does not prove runtime selection; no settings mutation or durable HOME change is established.
- Confidence/status: **UNKNOWN** / `INTEGRATED`
- Scope: previous public Phase 9 corpus

## WJ-06
- Phase/surface: `6WL` / `6WJ test reconciliation`
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: Service visibility/candidate interfaces and static sinks do not establish a callable transaction or accepted identity; H2 holder/grant/requester remains incomplete.
- Confidence/status: **UNKNOWN** / `INTEGRATED`
- Scope: previous public Phase 9 corpus

## WJ-07
- Phase/surface: `6WL` / `6WJ test reconciliation`
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: Exact OTA and native updater paths contain partition/cache writers statically, but no updater, recovery, OTA, reboot, or partition effect was observed.
- Confidence/status: **UNKNOWN** / `INTEGRATED`
- Scope: previous public Phase 9 corpus

## WJ-08
- Phase/surface: `6WL` / `6WJ test reconciliation`
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: Driver and native control edges are host-side static/conditional evidence only; retail node access, process/domain load, and effect are not established.
- Confidence/status: **UNKNOWN** / `INTEGRATED`
- Scope: previous public Phase 9 corpus

## WJ-09
- Phase/surface: `6WL` / `6WJ test reconciliation`
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: Source/config/probe logs do not close a retail privilege transition or sensitive sink; no approved device mutation is present.
- Confidence/status: **UNKNOWN** / `INTEGRATED`
- Scope: previous public Phase 9 corpus

## WJ-10
- Phase/surface: `6WL` / `6WJ test reconciliation`
- Source: `work/luna_worker_phase6wj_test_reconciliation_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: Tahoe/KFT/Launcher3 and accessibility/ADB foreground paths are either child-scoped or temporary; none is a sustainable User-0 formal HOME replacement.
- Confidence/status: **UNKNOWN** / `INTEGRATED`
- Scope: previous public Phase 9 corpus

## WK-001
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `186a710bb9d27f703f2c76bc1e179ac18cebbff022674e9e71f2bf7a50226327`
- Caller: DefaultPermissionGrantPolicy
- Gate: system_server/internal policy path; exact caller gate UNKNOWN
- Identity/user scope: userId argument
- Sink: DefaultPermissionGrantPolicy
- Effect: UNKNOWN
- Confidence/status: **static direct** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WK-002
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `a92e54ac19e886b935b547717827ccf018d1caa554b8ecaf8467b6077d7d309e`
- Caller: UserManagerService Binder implementation
- Gate: checkManageOrCreateUsersPermission(flags); MANAGE_USERS or CREATE_USERS; system/root accepted
- Identity/user scope: system/default user scope
- Sink: UserManagerService
- Effect: UNKNOWN
- Confidence/status: **static direct** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WK-003
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `a92e54ac19e886b935b547717827ccf018d1caa554b8ecaf8467b6077d7d309e`
- Caller: UserManagerService Binder implementation
- Gate: checkManageOrCreateUsersPermission(flags); MANAGE_USERS or CREATE_USERS; system/root accepted
- Identity/user scope: parent userId plus created profile
- Sink: UserManagerService
- Effect: UNKNOWN
- Confidence/status: **static direct** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WK-004
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `a92e54ac19e886b935b547717827ccf018d1caa554b8ecaf8467b6077d7d309e`
- Caller: UserManagerService Binder implementation
- Gate: checkManageOrCreateUsersPermission("Only the system can remove users"); exact downstream checks UNKNOWN
- Identity/user scope: userHandle argument
- Sink: UserManagerService
- Effect: UNKNOWN
- Confidence/status: **static direct** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WK-005
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `3382de2f12fc0f38c757c3fd021c06482db96c19389ec9909218423addd47274`
- Caller: UserController Binder-facing path
- Gate: INTERACT_ACROSS_USERS_FULL or amazon.aosp.permission.INTERACT_ACROSS_USERS_FULL; Binder calling pid/uid checked; shell restriction also enforced
- Identity/user scope: userId; system user rejected
- Sink: UserController
- Effect: UNKNOWN
- Confidence/status: **static direct** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WK-006
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `7aafaa0ccc5336df4f8e8cb7bcd38afbd578790c3065f28843a76a1eb36c06cc`
- Caller: ActivityManagerShellCommand
- Gate: shell command plus canSwitchUsers restriction; exact shell UID enforcement in downstream path UNKNOWN
- Identity/user scope: supplied target user
- Sink: ActivityManagerShellCommand
- Effect: UNKNOWN
- Confidence/status: **static direct** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WK-007
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `7aafaa0ccc5336df4f8e8cb7bcd38afbd578790c3065f28843a76a1eb36c06cc`
- Caller: ActivityManagerShellCommand
- Gate: shell command path; downstream caller and SELinux gate UNKNOWN
- Identity/user scope: supplied target user
- Sink: ActivityManagerShellCommand
- Effect: UNKNOWN
- Confidence/status: **static direct** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WK-008
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `7aafaa0ccc5336df4f8e8cb7bcd38afbd578790c3065f28843a76a1eb36c06cc`
- Caller: ActivityManagerShellCommand
- Gate: shell command path; downstream INTERACT_ACROSS_USERS_FULL gate visible in UserController
- Identity/user scope: supplied target user
- Sink: ActivityManagerShellCommand
- Effect: UNKNOWN
- Confidence/status: **static direct** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WK-009
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `107ba7f2925439e8bf061b39b9496a5d6cc661c00990d5be9259104f2960486f`
- Caller: AppRestrictionsHelper
- Gate: PackageManager validation; Settings UI/profile-policy caller and SELinux rule UNKNOWN
- Identity/user scope: explicit userId
- Sink: AppRestrictionsHelper
- Effect: UNKNOWN
- Confidence/status: **static direct** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WK-010
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `107ba7f2925439e8bf061b39b9496a5d6cc661c00990d5be9259104f2960486f`
- Caller: AppRestrictionsHelper
- Gate: PackageManager uninstall validation; only restricted-profile branch visible
- Identity/user scope: explicit userId
- Sink: AppRestrictionsHelper
- Effect: UNKNOWN
- Confidence/status: **static direct** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WK-011
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `1e15d3461b6d0e34391eba9b628e8ca83a7082590baf33bfec4ad8d00e5209df`
- Caller: UserManagerHelper
- Gate: helper checks no_add_user restriction; service permission gate remains authoritative
- Identity/user scope: current process/default user scope
- Sink: UserManagerHelper
- Effect: UNKNOWN
- Confidence/status: **static direct** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WK-012
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `1e15d3461b6d0e34391eba9b628e8ca83a7082590baf33bfec4ad8d00e5209df`
- Caller: UserManagerHelper
- Gate: helper excludes system/current-user case; service permission gate remains authoritative
- Identity/user scope: userInfo.id
- Sink: UserManagerHelper
- Effect: UNKNOWN
- Confidence/status: **static direct** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WK-013
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `1e15d3461b6d0e34391eba9b628e8ca83a7082590baf33bfec4ad8d00e5209df`
- Caller: UserManagerHelper
- Gate: helper checks current/foreground user only; downstream switch gate and SELinux rule UNKNOWN
- Identity/user scope: target user id
- Sink: UserManagerHelper
- Effect: UNKNOWN
- Confidence/status: **static direct** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WK-014
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `4efc2aba8f7798fb4e026f13479f5b4929ef545deba5618b35d799555d78678b`
- Caller: external callers through exported SettingsProvider
- Gate: global/secure writes enforce WRITE_SECURE_SETTINGS; system writes use WRITE_SETTINGS or app-op; cross-user gate at 431
- Identity/user scope: calling user and requested setting namespace
- Sink: SettingsProvider
- Effect: UNKNOWN
- Confidence/status: **static direct** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WK-015
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `e4f2d9d47e7fa10be2aa2d26f6549b41184762d7ff5c77c19ffa7fc7560aac70`
- Caller: SettingsProvider
- Gate: android:exported=true; sharedUserId=android.uid.system; provider write methods enforce permissions
- Identity/user scope: singleUser across users
- Sink: SettingsProvider
- Effect: UNKNOWN
- Confidence/status: **static manifest** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WK-016
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `58ce4931e266384bd63147b65748edb53190d68f270b0b324dfa5c646506d5af`
- Caller: MediaSessionService
- Gate: internal service path; exact caller/permission and SELinux rule UNKNOWN
- Identity/user scope: full user id
- Sink: MediaSessionService
- Effect: UNKNOWN
- Confidence/status: **static direct** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WK-017
- Phase/surface: `6WL` / `6WK broad surface`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv`
- Evidence: `UNKNOWN`
- SHA-256: `a92e54ac19e886b935b547717827ccf018d1caa554b8ecaf8467b6077d7d309e`
- Caller: UserManagerService
- Gate: system_server internal; file path, DAC, SELinux and caller gate UNKNOWN
- Identity/user scope: user list and user state
- Sink: UserManagerService
- Effect: UNKNOWN
- Confidence/status: **static file sink** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## WF-POL-001
- Phase/surface: `6WL` / `6WF live ProductPolicy`
- Source: `UNKNOWN`
- Evidence: `artifacts/phase6wf-product-policy-readonly-20260810-01/global_policy.xml`
- SHA-256: `2cc60c0ee80bbba2752671b7323e2bdaae8f87125b7251726f821906f58087e2`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: none; read-only
- Confidence/status: **UNKNOWN** / `CONFIRMED_NO_ENTRY`
- Scope: previous public Phase 9 corpus

## WF-POL-002
- Phase/surface: `6WL` / `6WF live ProductPolicy`
- Source: `UNKNOWN`
- Evidence: `artifacts/phase6wf-product-policy-readonly-20260810-01/common_device_policy.xml`
- SHA-256: `75c7919d2006fc0b088996cd2048b927c419b03ca025a95b20ff31e3de9868aa`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: none; read-only
- Confidence/status: **UNKNOWN** / `CONFIRMED_NO_ENTRY`
- Scope: previous public Phase 9 corpus

## WF-POL-003
- Phase/surface: `6WL` / `6WF live ProductPolicy`
- Source: `UNKNOWN`
- Evidence: `artifacts/phase6wf-product-policy-readonly-20260810-01/multimodal_device_policy.xml`
- SHA-256: `66f05c0e0f502e6db191904ec39be5e5b6302905f00cdacfc8a29ef327089512`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: none; read-only
- Confidence/status: **UNKNOWN** / `CONFIRMED_NO_ENTRY`
- Scope: previous public Phase 9 corpus

## WF-POL-004
- Phase/surface: `6WL` / `6WF live ProductPolicy`
- Source: `UNKNOWN`
- Evidence: `artifacts/phase6wf-product-policy-readonly-20260810-01/receiver_filter_policy.xml`
- SHA-256: `c3a80bcd0b52250aaa72bd863ae6a633f3153df646ffc57682972bc7c39fab8c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: none; read-only
- Confidence/status: **UNKNOWN** / `CONFIRMED_NOT_HOME_WRITER`
- Scope: previous public Phase 9 corpus

## WF-POL-005
- Phase/surface: `6WL` / `6WF live ProductPolicy`
- Source: `UNKNOWN`
- Evidence: `artifacts/phase6wf-product-policy-readonly-20260810-01/device_policy_paths.txt`
- SHA-256: `fee33721f9ea80bb151b2fb04b58de4d9e846a1de68c7c994f6e7416d217fe07`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: none; pull failed with ENOENT
- Confidence/status: **UNKNOWN** / `UNKNOWN_LAYOUT_MISMATCH`
- Scope: previous public Phase 9 corpus

## KX-IPC-001
- Phase/surface: `6X-IPC` / `IAmazonKeyguardService.dismissWithPendingIntent (Stub method; Proxy method; tx UNKNOWN)`
- Source: `AmazonKeyguardService$2.dismissWithPendingIntent; fosservices disassembly lines 168487-168535; boot-fosframework Proxy lines 391141-391186`
- Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log; decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c; fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`
- Caller: Binder caller UID from Binder.getCallingUid(); verified default package resolved from that UID
- Gate: checkUidPermission(android.permission.CONTROL_KEYGUARD) OR checkUidPermission(com.amazon.permission.AMAZON_CONTROL_KEYGUARD) in checkKeyguardPermissions; exact permission protection level and service-manager/SELinux gate UNKNOWN
- Identity/user scope: caller UID is retained and forwarded with verified package; no clearCallingIdentity/restoreCallingIdentity observed; target PendingIntent arguments are caller-supplied but downstream SystemUI receives verified UID/package
- Sink: IAmazonKeyguardServiceSystemUI.dismissWithPendingIntent; SystemUI keyguard dismissal/PendingIntent flow
- Effect: Static implementation confirms a privileged SystemUI/keyguard sink; no runtime success, HOME selection, package-state mutation, or exploit is established
- Confidence/status: **High static** / `NEW_DIFFERENCE_STATIC_ONLY`
- Scope: previous public Phase 9 corpus

## KX-IPC-002
- Phase/surface: `6X-IPC` / `IAmazonKeyguardService.setAccessibilityInfo (Stub method; Proxy method; tx UNKNOWN)`
- Source: `AmazonKeyguardService$2.setAccessibilityInfo; fosservices disassembly lines 168690-168730; boot-fosframework Proxy lines 391292-391321`
- Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log; decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c; fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`
- Caller: Binder caller UID from Binder.getCallingUid(); verified default package resolved from that UID
- Gate: checkUidPermission(android.permission.CONTROL_KEYGUARD) OR checkUidPermission(com.amazon.permission.AMAZON_CONTROL_KEYGUARD) in checkKeyguardPermissions; exact protection level and service-manager/SELinux gate UNKNOWN
- Identity/user scope: caller UID and verified package are forwarded to SystemUI; no identity clear observed; user ID is not explicit in the public method signature
- Sink: IAmazonKeyguardServiceSystemUI.setAccessibilityInfo; keyguard accessibility metadata/list state
- Effect: Static SystemUI state sink only; no runtime reachability, arbitrary package acceptance, HOME effect, or exploit is established
- Confidence/status: **High static** / `NEW_DIFFERENCE_STATIC_ONLY`
- Scope: previous public Phase 9 corpus

## KX-IPC-003
- Phase/surface: `6X-IPC` / `IAmazonKeyguardService.setForegroundColor (Stub method; Proxy method; tx UNKNOWN)`
- Source: `AmazonKeyguardService$2.setForegroundColor; fosservices disassembly lines 168732-168795; boot-fosframework Proxy lines 391322-391349`
- Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log; decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c; fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`
- Caller: Binder caller UID from Binder.getCallingUid(); verified default package resolved from that UID
- Gate: checkUidPermission(android.permission.CONTROL_KEYGUARD) OR checkUidPermission(com.amazon.permission.AMAZON_CONTROL_KEYGUARD) in checkKeyguardPermissions; exact protection level and service-manager/SELinux gate UNKNOWN
- Identity/user scope: caller UID and verified package are forwarded to SystemUI; no identity clear observed; user ID is not explicit in the public method signature
- Sink: IAmazonKeyguardServiceSystemUI.setForegroundColor; keyguard foreground color/presentation state
- Effect: Static SystemUI presentation sink only; no runtime reachability, arbitrary caller acceptance, HOME effect, or exploit is established
- Confidence/status: **High static** / `NEW_DIFFERENCE_STATIC_ONLY`
- Scope: previous public Phase 9 corpus

## 6X-OTA-01
- Phase/surface: `6X-OTA` / `version/provenance`
- Source: `7.3.3.1 adjacent OTA manifest`
- Evidence: `firmware/manifests/OTA-20260803-01/README.md:1-30`
- SHA-256: `3b7971859d4df3b85a671ab5340d3ad9bb2efb8501c2f09ec71374ac74abf7a5`
- Caller: OTA privileged lifecycle is not established by this file alone
- Gate: manifest metadata records product/version/key_type; no runtime install gate is exercised
- Identity/user scope: PS7331.4463N package identity only; installed baseline is PS7330.4104N; runtime UID/SELinux UNKNOWN
- Sink: No caller-to-writer inference; no exact installed-build post-install or rollback sink
- Effect: NONE
- Confidence/status: **high** / `excluded_adjacent_version`
- Scope: previous public Phase 9 corpus

## 6X-OTA-02
- Phase/surface: `6X-OTA` / `host extraction provenance`
- Source: `selected/compiled-02 debugfs-derived manifests`
- Evidence: `firmware/extracted/PS7331/selected/extraction-manifest.tsv:1-10; firmware/extracted/PS7331/compiled-02/extraction-manifest.tsv:1-12`
- SHA-256: `b098f85287a729d03cfac1ac6f767a3ba6a15ce8c65d7f9e581cbbed75448a74;7da7040b4c7454084d8c30452edc05d4c68ce3813fe20700d4016036e4097716`
- Caller: No installer/recovery caller; extraction is host-side
- Gate: file list and per-output SHA-256 only; no package signature, recovery, or execution gate
- Identity/user scope: Derived artifact identity only; runtime process/UID/SELinux UNKNOWN
- Sink: Framework/APK/VDEX outputs are analysis inputs, not post-install/native writer execution
- Effect: NONE
- Confidence/status: **high** / `excluded_host_derived`
- Scope: previous public Phase 9 corpus

## 6X-OTA-03
- Phase/surface: `6X-OTA` / `post-install/native updater/recovery`
- Source: `existing Phase 6WH/6SD/6SP/6VB static corpus`
- Evidence: `work/luna_worker_phase6wh_ota_residual_20260810.csv:2-7`
- SHA-256: `d88e35ec08d9ef0a55a3dbc17dc430b62d3b419810653542b6dd3077095cca24;4d0128ee85eec7b0c88716012858bef699f740907e46e854939c83a6c9e99077;d653e4a84898509781a333c56502087a83981781fcf6612d7026bfd79602b477;1136d4815ae63011522fead17ef743bc0daa57334ae6ebb3b4c05c1d09507c52;c99f6884fa298546b18722a5addb46ae35aff4c9f6003d8ad3ccaebe2edfdbd9`
- Caller: Privileged OTA lifecycle and recovery context are capability candidates; ordinary app/shell caller not shown
- Gate: metadata/hash/recovery-verification/controller gates precede handoff; indirect dispatch and complete caller join UNKNOWN
- Identity/user scope: UpdateSystem/recovery UID, SELinux domain, AVB rollback authority, and exact user scope UNKNOWN
- Sink: Edify extraction/block-image/cache/readlink paths reach high-privilege file/partition capability statically
- Effect: NONE
- Confidence/status: **high** / `duplicate_no_new_gap`
- Scope: previous public Phase 9 corpus

## 6X-OTA-04
- Phase/surface: `6X-OTA` / `temporary path/symlink/canonicalization`
- Source: `existing Java/native staging and cache evidence`
- Evidence: `work/luna_worker_ota_canonicalization_provenance_20260810.md:1-34`
- SHA-256: `4d6bc6518f8f45773ac517225d33e9f990ed1de5c590c2b68bf827482e057e64`
- Caller: SideloadMover/MakeFreeSpaceOnCache are static callers only; external input provenance UNKNOWN
- Gate: basename staging, rename/copy-delete fallback, readlink/unlink/free-space helpers; no proven no-follow/atomicity gate
- Identity/user scope: Path owner, race semantics, helper return dataflow, and writer identity UNKNOWN
- Sink: Potential staging/cache and native writer capability remains bounded; no arbitrary-path write established
- Effect: NONE
- Confidence/status: **high** / `duplicate_unknown_boundary`
- Scope: previous public Phase 9 corpus

## 6XG-001
- Phase/surface: `6XG-GPL` / `input/uinput`
- Source: `kernel/mediatek/mt8183/4.4/drivers/input/misc/uinput.c:909-933; source SHA-256 98b41492311d9b9fb9ccbfe269a2fddc0fb436f3048b7887e1f6e5482d36211`
- Evidence: `firmware/extracted/PS7331-SOURCE-20250617/platform.tar member kernel/mediatek/mt8183/4.4/drivers/input/misc/uinput.c`
- SHA-256: `98b41492311d9b9fb9ccbfe269a2fddc0fb436f3048b7887e1f6e5482d36211a`
- Caller: uinput_fops: read, write, unlocked_ioctl, compat_ioctl; misc_register
- Gate: CONFIG_INPUT_UINPUT=y (artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config:2146); no capable()/credential gate in inspected uinput source; final node mode/SELinux not joined
- Identity/user scope: No exact shipped native ELF open/write/ioctl callsite; package and UID/domain not established
- Sink: Synthetic input device creation and event injection into the kernel input graph; no direct PMS/HOME writer in scoped source
- Effect: Source capability is confirmed; shipped caller/reachability and package effect are not established
- Confidence/status: **high source, low caller** / `NEW_SOURCE_EVIDENCE`
- Scope: previous public Phase 9 corpus

## 6XG-002
- Phase/surface: `6XG-GPL` / `power-supply sysfs`
- Source: `kernel/mediatek/mt8183/4.4/drivers/power/power_supply_sysfs.c:34-39,115-136,238-263; source SHA-256 54409386286849db4768d1b013b0151c3b8e52d3c5b4e434b52d8881364cc38e`
- Evidence: `firmware/extracted/PS7331-SOURCE-20250617/platform.tar member kernel/mediatek/mt8183/4.4/drivers/power/power_supply_sysfs.c`
- SHA-256: `54409386286849db4768d1b013b0151c3b8e52d3c5b4e434b52d8881364cc38e`
- Caller: POWER_SUPPLY_ATTR store; power_supply_store_property -> power_supply_set_property
- Gate: CONFIG_POWER_SUPPLY=y; attributes are read-only by default and gain S_IWUSR only when psy->desc->property_is_writeable(psy, property)>0; no SELinux/domain caller join
- Identity/user scope: No exact shipped native sysfs write caller, package, UID, or domain established
- Sink: Battery/charger power-supply property mutation when the provider advertises a writable property; no package/HOME sink shown
- Effect: Generic source writer with provider callback gate; shipped path and caller unknown
- Confidence/status: **high source, low caller** / `NEW_SOURCE_EVIDENCE`
- Scope: previous public Phase 9 corpus

## 6XG-003
- Phase/surface: `6XG-GPL` / `RPMB char device precise negative`
- Source: `kernel/mediatek/mt8183/4.4/drivers/char/rpmb/rpmb-mtk.c:2364-2544,2732-2764; source SHA-256 a6b070190ad8b97173c129509e6d8f8ae8c9f0d383bc349be44d9c919387c8d5`
- Evidence: `firmware/extracted/PS7331-SOURCE-20250617/platform.tar member kernel/mediatek/mt8183/4.4/drivers/char/rpmb/rpmb-mtk.c`
- SHA-256: `a6b070190ad8b97173c129509e6d8f8ae8c9f0d383bc349be44d9c919387c8d5`
- Caller: rpmb_fops: open, release, unlocked_ioctl; .write=NULL; .read=NULL; cdev_add/device_create with RPMB_NAME
- Gate: CONFIG_RPMB=y; CONFIG_RPMB_INTF_DEV is not set in merged kernel.config:2235-2237; no local capable() proof; TEE/authentication is downstream, not a userspace identity proof
- Identity/user scope: Existing rpmb_svc process evidence does not identify a native open/ioctl callsite or package/UID; no ordinary-app caller established
- Sink: Authenticated persistent RPMB read/write/counter operations are available only through ioctl path in this fops; direct read/write file operations are source-negated
- Effect: Precise negative for read/write fops; ioctl sink remains source-only with caller/node ownership unresolved
- Confidence/status: **high source, medium classification** / `PRECISE_NEGATIVE_PLUS_SOURCE`
- Scope: previous public Phase 9 corpus

## 6XG-004
- Phase/surface: `6XG-GPL` / `vendor/mediatek archive path`
- Source: `platform archive member listing: no vendor/mediatek path; Amazon source is device/amazon/kernel/driver; kernel MediaTek tree is kernel/mediatek/...`
- Evidence: `firmware/extracted/PS7331-SOURCE-20250617/platform.tar`
- SHA-256: `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd`
- Caller: No source registration/API because path is absent
- Gate: Archive-level path absence; do not infer that a separate vendor tree is kernel build provenance
- Identity/user scope: No caller/package/UID can be assigned to an absent path
- Sink: No driver sink attributable to absent vendor/mediatek path; any vendor ELF/policy linkage requires an exact manifest/build reference
- Effect: Exact negative only; no reachability or vulnerability claim
- Confidence/status: **high for archive path negative** / `PRECISE_NEGATIVE`
- Scope: previous public Phase 9 corpus

## 6XG-005
- Phase/surface: `6XG-GPL` / `uinput native/SELinux caller join negative`
- Source: `Existing exact-build native inventory and extracted vendor policy were scanned for a path-specific /dev/uinput caller and uinput node type/allow; no tuple found`
- Evidence: `artifacts/phase5/phase5cs-native-analysis-20260804-01/native-inventory.csv`
- SHA-256: `9d1313d25cb45492d5656d03f05b7e60f5d037ccef15c20d9edec5e0fdbf17f9`
- Caller: No exact shipped ELF open/write/ioctl caller; no uinput-specific file-context/allow tuple identified in bounded artifacts
- Gate: Inventory/policy absence is a negative join only; it does not prove node absence or denial
- Identity/user scope: No package, UID, or SELinux domain established
- Sink: No confirmed input-injection or package/HOME effect from shipped native code
- Effect: Precise negative for caller/policy closure; source capability remains 6XG-001
- Confidence/status: **medium** / `PRECISE_NEGATIVE`
- Scope: previous public Phase 9 corpus

## 6Y-001
- Phase/surface: `6Y-PERM` / `permission-definition`
- Source: `android.amazon.perm declares com.amazon.tv.developer.sdk.personalization.USE_SDK`
- Evidence: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- SHA-256: `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`
- Caller: unknown/no bounded requester
- Gate: manifest declaration only; no service-side check joined; protection=0x0 (normal)
- Identity/user scope: owner android.amazon.perm sharedUserId=android.uid.system; holder/grant not established
- Sink: none joined in bounded exact manifests/disassembly
- Effect: no observed effect; low protection is a static candidate only
- Confidence/status: **high declaration; low reachability** / `NEW_STATIC_LOW_PROTECTION_NO_SINK`
- Scope: previous public Phase 9 corpus

## 6Y-002
- Phase/surface: `6Y-PERM` / `permission-definition`
- Source: `android.amazon.perm declares com.amazon.tv.developer.sdk.content.USE_SDK`
- Evidence: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- SHA-256: `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`
- Caller: unknown/no bounded requester
- Gate: manifest declaration only; no service-side check joined; protection=0x0 (normal)
- Identity/user scope: owner android.amazon.perm sharedUserId=android.uid.system; holder/grant not established
- Sink: none joined in bounded exact manifests/disassembly
- Effect: no observed effect; low protection is a static candidate only
- Confidence/status: **high declaration; low reachability** / `NEW_STATIC_LOW_PROTECTION_NO_SINK`
- Scope: previous public Phase 9 corpus

## 6Y-003
- Phase/surface: `6Y-PERM` / `permission-definition`
- Source: `android.amazon.perm declares com.amazon.mw.permission.PLUGIN`
- Evidence: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- SHA-256: `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`
- Caller: unknown/no bounded requester
- Gate: manifest declaration only; no service-side check joined; protection=0x1 (dangerous)
- Identity/user scope: owner android.amazon.perm sharedUserId=android.uid.system; holder/grant not established
- Sink: none joined in bounded exact manifests/disassembly
- Effect: no observed effect; dangerous protection is a static candidate only
- Confidence/status: **high declaration; low reachability** / `NEW_STATIC_LOW_PROTECTION_NO_SINK`
- Scope: previous public Phase 9 corpus

## 6Y-004
- Phase/surface: `6Y-PERM` / `permission-definition`
- Source: `android.amazon.perm declares com.amazon.mw.permission.PLUGIN_CONSUMER`
- Evidence: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- SHA-256: `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`
- Caller: unknown/no bounded requester
- Gate: manifest declaration only; no service-side check joined; protection=UNKNOWN (no protectionLevel attribute in bounded declaration)
- Identity/user scope: owner android.amazon.perm sharedUserId=android.uid.system; holder/grant not established
- Sink: none joined in bounded exact manifests/disassembly
- Effect: no observed effect; protection level cannot be safely decoded from this record
- Confidence/status: **medium declaration; low reachability** / `NEW_STATIC_DEFINITION_NO_SINK`
- Scope: previous public Phase 9 corpus

## 6Z-001
- Phase/surface: `6Z-COMPONENT` / `OOBE-OTA-receiver`
- Source: `com.amazon.kindle.otter.oobe.BootAfterSystemOTAReceiver`
- Evidence: `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java:27-61`
- SHA-256: `c29b32bf6874b245859357d926773193c15771a6eb254f97edac57541ae5cb90`
- Caller: SystemServer AmazonPackageManagerService.onBootPhase-550 plus PMS.isUpgrade
- Gate: protected RECEIVE_BOOT_AFTER_SYSTEM_OTA plus receiver action-OOBE-retail-demo guards; action=com.amazon.intent.action.BOOT_AFTER_SYSTEM_OTA
- Identity/user scope: system-server Context user-derived; numeric user UNKNOWN
- Sink: PackageHelper.enableComponent to OobeHomeActivity plus OOBEActivationHelper
- Effect: Enables OOBE activity and enters guarded OOBE activation; no proven Fire Launcher HOME setter
- Confidence/status: **high** / `STATIC_CONFIRMED_NUMERIC_USER_UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6Z-002
- Phase/surface: `6Z-COMPONENT` / `OOBE-settings`
- Source: `com.amazon.kindle.otter.oobe.commons.OOBEActivationHelper`
- Evidence: `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java:29-34;53-56`
- SHA-256: `6ebcb7eef7a03459a76b9c21cd59b61a30947f2b00a5624a4646825b8e3223d2`
- Caller: BootAfterSystemOTAReceiver guarded lifecycle sender
- Gate: protected OTA lifecycle plus incremental-OOBE branch; no ordinary caller path; action=guarded BootAfterSystemOTA branch
- Identity/user scope: ContentResolver user inherited from receiver Context; numeric user UNKNOWN
- Sink: SettingsDBUtils to Settings.Secure-Global user_setup_complete=0 and isOOBEActive=1
- Effect: Mutates setup-OOBE state only when lifecycle guard passes; no HOME or preferred-package sink
- Confidence/status: **high** / `STATIC_SINK_CONFIRMED_EXACT_USER_UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6Z-003
- Phase/surface: `6Z-COMPONENT` / `exported-receiver`
- Source: `com.amazon.dcpms.fos.service.lifecycle.pca.profileswitch.PCAActiveProfileReceiver`
- Evidence: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:115-122`
- SHA-256: `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`
- Caller: upstream producer UNKNOWN; exported entry has no component permission in saved manifest
- Gate: manifest action gate plus PROGRAM_ID and PACKAGE_NAME extras; action=com.amazon.device.ACTION_ACTIVE_PROFILE_UPDATED
- Identity/user scope: receiver application user scope and cross-user acceptance UNKNOWN
- Sink: CDE profile type and OS user type and active-app list persistence to DeviceExperienceModeEvaluator.evaluate
- Effect: Updates DCPMS policy state; no SettingsProvider PMS HOME package-state or OTA sink
- Confidence/status: **medium** / `STATIC_EXPORTED_POLICY_SINK_CALLER_UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6Z-004
- Phase/surface: `6Z-COMPONENT` / `exported-protected-action-receiver`
- Source: `com.amazon.dcpms.fos.service.lifecycle.device.userswitch.DeviceUserSwitchReceiver`
- Evidence: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:105-113`
- SHA-256: `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`
- Caller: system/framework USER_SWITCHED producer
- Gate: protected USER_SWITCHED gate; ordinary sender not established; action=android.intent.action.USER_SWITCHED
- Identity/user scope: receiver user and profile scope UNKNOWN
- Sink: CDE PCA-profile and OS-user persistence plus child active-app-list clear to evaluator
- Effect: Updates policy and profile state; no HOME PMS package-state or OTA sink
- Confidence/status: **high** / `STATIC_PROTECTED_ACTION_POLICY_SINK_CALLER_UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6Z-005
- Phase/surface: `6Z-COMPONENT` / `exported-permissioned-receiver`
- Source: `com.amazon.dcpms.fos.service.lifecycle.device.userswitch.AccountPropertyChangeReceiver`
- Evidence: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:94-103`
- SHA-256: `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`
- Caller: producer UNKNOWN
- Gate: caller must satisfy AmazonAccountPropertyService.property.changed; permission protection and holder UNKNOWN; action=com.amazon.dcp.sso.action.AmazonAccountPropertyService.property.changed
- Identity/user scope: receiver user scope UNKNOWN
- Sink: CDE profile type and OS-user persistence to evaluator
- Effect: Policy persistence and evaluation only; no HOME PMS package-state or OTA sink
- Confidence/status: **medium** / `STATIC_PERMISSION_HOLDER_UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6Z-006
- Phase/surface: `6Z-COMPONENT` / `exported-permissioned-receiver`
- Source: `com.amazon.dcpms.fos.service.lifecycle.device.sync.GlobalContentSyncEventReceiver`
- Evidence: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:145-153`
- SHA-256: `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`
- Caller: producer UNKNOWN
- Gate: GLOBAL_SYNC required; holder-protection and caller route UNKNOWN; action=com.amazon.intent.SYNC
- Identity/user scope: receiver exact user scope UNKNOWN
- Sink: JobIntentService to GlobalContentSyncEventService to ArcusSyncService.syncCDEPolicy
- Effect: Triggers CDE policy sync; no OTA recovery HOME or PMS package-state sink
- Confidence/status: **medium** / `STATIC_PERMISSION_HOLDER_UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6Z-007
- Phase/surface: `6Z-COMPONENT` / `ProductPolicy-system-server-init`
- Source: `ProductPolicyService via productpolicyservice_fosinit.xml`
- Evidence: `artifacts/phase6bg-product-policy-readonly-20260805-01/productpolicyservice_fosinit.stderr.txt`
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Caller: init and system-server loader
- Gate: registered in-process fosinit; no exported app component or external caller evidence; action=init service registration
- Identity/user scope: system-server service identity; Binder publication and caller gate UNKNOWN
- Sink: ProductPolicy service registration only; no verified HOME package Settings or OTA sink in bounded corpus
- Effect: No exported component observed; service existence is not caller reachability
- Confidence/status: **medium** / `STATIC_REGISTRATION_ONLY_CALLER_AND_SINK_UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6Z-008
- Phase/surface: `6Z-COMPONENT` / `Settings-HOME-resource-and-PMS-state`
- Source: `default_home plus config_show_default_home=true plus per-user preferred-activities`
- Evidence: `work/luna_worker_settings_home_resource_followup_20260810.md`
- SHA-256: `UNKNOWN_REPORT_FILE_HASH`
- Caller: Settings UI or shell read path; no new writer established
- Gate: DefaultHomePreferenceController resource gate; normal dashboard omits default_home; set-home-activity is existing writer boundary; action=android.intent.action.MAIN plus CATEGORY_HOME
- Identity/user scope: per-user PMS Settings state; exact shell authorization is existing PMS gate; no new caller route
- Sink: com.android.server.pm.Settings preferred-activities and persistent-preferred-activities plus effective HOME resolver
- Effect: Existing HOME resolver and preferred-state divergence only; no new shell-writable Settings or DeviceConfig key
- Confidence/status: **high** / `CONFIRMED_EXISTING_BOUNDARY_DEDUPED`
- Scope: previous public Phase 9 corpus

## 6X-LIVE-001
- Phase/surface: `6X-LIVE` / `device identity`
- Source: `adb read-only snapshot`
- Evidence: `adb/phase6x/PHASE6X-DEVICE-READONLY-20260810-01/getprop.stdout.txt`
- SHA-256: `9d6158ab236efb6b72489e2109f2220506048f0dc1c77a0230fde41f655e0ea5`
- Caller: adb shell getprop
- Gate: none; observation only
- Identity/user scope: serial G001LT0511550CFT; User 0 current
- Sink: build fingerprint
- Effect: PS7331.4463N/0031575863040; incremental 0031575863172; security patch 2024-08-01
- Confidence/status: **Confirmed observation** / `OBSERVED_READ_ONLY`
- Scope: previous public Phase 9 corpus

## 6X-LIVE-002
- Phase/surface: `6X-LIVE` / `HOME User 0`
- Source: `cmd package resolve-activity`
- Evidence: `adb/phase6x/PHASE6X-DEVICE-READONLY-20260810-01/home_user0.stdout.txt`
- SHA-256: `MISSING`
- Caller: shell read-only query
- Gate: resolver observation
- Identity/user scope: User 0
- Sink: formal HOME resolver
- Effect: com.amazon.firelauncher/.Launcher; priority 50
- Confidence/status: **Confirmed observation** / `OBSERVED_READ_ONLY`
- Scope: previous public Phase 9 corpus

## 6X-LIVE-003
- Phase/surface: `6X-LIVE` / `HOME candidates User 0`
- Source: `cmd package query-activities`
- Evidence: `adb/phase6x/PHASE6X-DEVICE-READONLY-20260810-01/home_candidates_user0.stdout.txt`
- SHA-256: `MISSING`
- Caller: shell read-only query
- Gate: resolver observation
- Identity/user scope: User 0
- Sink: candidate set
- Effect: Fire 50, Microsoft 0, FallbackHome -1000
- Confidence/status: **Confirmed observation** / `OBSERVED_READ_ONLY`
- Scope: previous public Phase 9 corpus

## 6X-LIVE-004
- Phase/surface: `6X-LIVE` / `HOME candidates User 10`
- Source: `cmd package resolve/query-activities`
- Evidence: `adb/phase6x/PHASE6X-CURRENT-SCOPE-READONLY-20260810-01/home_user10.stdout.txt`
- SHA-256: `90b0bcbb1461327869dd23bfe630d2c2d01971438248f0f8842bca931b5373af`
- Caller: shell read-only query
- Gate: resolver observation
- Identity/user scope: User 10 test profile
- Sink: candidate set
- Effect: FallbackHome only; Fire is user-scoped disabled in saved package dump
- Confidence/status: **Confirmed observation** / `OBSERVED_READ_ONLY`
- Scope: previous public Phase 9 corpus

## 6X-LIVE-005
- Phase/surface: `6X-LIVE` / `Fire Launcher per-user state`
- Source: `dumpsys package com.amazon.firelauncher`
- Evidence: `adb/phase6x/PHASE6X-CURRENT-SCOPE-READONLY-20260810-01/firelauncher_package.stdout.txt`
- SHA-256: `86b91e5270d8f737609fd64481d9d7414fdcb164a169a936d038dc58450336ef`
- Caller: shell read-only dump
- Gate: package-state observation
- Identity/user scope: User 0 enabled=0; User 10 enabled=2
- Sink: package state
- Effect: User 0 installed/visible/enabled; User 10 disabled; no cross-user User 0 effect observed
- Confidence/status: **Confirmed observation** / `OBSERVED_READ_ONLY`
- Scope: previous public Phase 9 corpus

## 6X-LIVE-006
- Phase/surface: `6X-LIVE` / `preferred HOME record`
- Source: `dumpsys package preferred-xml`
- Evidence: `adb/phase6x/PHASE6X-CURRENT-SCOPE-READONLY-20260810-01/preferred_activities.stdout.txt`
- SHA-256: `7750d564a29046d0eb9e6d5d0565389d38cd5f6b9b4d8010fdf54f5dd667a8c6`
- Caller: shell read-only dump
- Gate: preferred state observation
- Identity/user scope: User 0 record
- Sink: ordinary preferred activity
- Effect: preferred record names com.amazon.firelauncher/.Launcher with MAIN/HOME/DEFAULT filter
- Confidence/status: **Confirmed observation** / `OBSERVED_READ_ONLY`
- Scope: previous public Phase 9 corpus

## 6X2-IPC-001
- Phase/surface: `6X2` / `IPC`
- Source: `UNKNOWN`
- Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:16376-16534;16413-16464;16519-16524`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: external dump caller; UID UNKNOWN
- Gate: android.permission.DUMP protection semantics not re-derived in bounded corpus
- Identity/user scope: default/device settings user; explicit user overload absent
- Sink: Settings.System.putInt(screen_brightness)
- Effect: POSITIVE sink and gate; NEGATIVE for HOME/package/OTA
- Confidence/status: **UNKNOWN** / `STATIC_SETTINGS_SINK_NOT_NEW`
- Scope: previous public Phase 9 corpus

## 6X2-IPC-002
- Phase/surface: `6X2` / `IPC`
- Source: `UNKNOWN`
- Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:29308-29317;29345-29355;29384-29400;29517-29520;29570-29580`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: remote Binder caller UNKNOWN
- Gate: com.amazon.alexa.permission.MODE_SWITCH protection level/holder UNKNOWN
- Identity/user scope: USER_CURRENT=-2
- Sink: SecureSettingsHelper.putIntForUser(orientation_in_previous_mode)
- Effect: POSITIVE
- Confidence/status: **UNKNOWN** / `STATIC_SETTINGS_SINK_NOT_NEW`
- Scope: previous public Phase 9 corpus

## 6X2-IPC-003
- Phase/surface: `6X2` / `IPC`
- Source: `UNKNOWN`
- Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:27078-27265;27426-27435;28453-28456`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: system_server/input-monitor publisher; external caller UNKNOWN
- Gate: permission and protection UNKNOWN
- Identity/user scope: system/default secure scope; non-user overload
- Sink: Settings.Secure.putInt(camera_shutter_state)
- Effect: POSITIVE bounded callback sink; NEGATIVE external Binder reachability
- Confidence/status: **UNKNOWN** / `STATIC_CALLBACK_SINK_NOT_NEW`
- Scope: previous public Phase 9 corpus

## 6X2-IPC-004
- Phase/surface: `6X2` / `IPC`
- Source: `UNKNOWN`
- Evidence: `decompiled/jadx/settings/resources/AndroidManifest.xml; artifacts/phase6h/phase6h-framework-ipc-20260804-01/manifest-components.csv:202; artifacts/phase6w/exported-component-audit-20260805-01/high-impact-exported-candidates.csv:56`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: external sender UNKNOWN
- Gate: com.amazon.kindle.otter.oobe.OOBE_PERMISSION protection level and holder UNKNOWN
- Identity/user scope: receiver user scope UNKNOWN
- Sink: downstream Settings/HOME/package sink not joined
- Effect: POSITIVE exported declaration; NEGATIVE complete target sink
- Confidence/status: **UNKNOWN** / `EXPORTED_PERMISSION_UNKNOWN_NO_NEW_CHAIN`
- Scope: previous public Phase 9 corpus

## 6X2-IPC-005
- Phase/surface: `6X2` / `IPC`
- Source: `UNKNOWN`
- Evidence: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:94-103; work/luna_worker_phase6sv_exported_surface_20260810.csv:4`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: producer UNKNOWN
- Gate: com.amazon.dcp.sso.permission.AmazonAccountPropertyService.property.changed protection/holder UNKNOWN
- Identity/user scope: receiver user scope UNKNOWN
- Sink: CDE/profile persistence and evaluator; no HOME/PMS/OTA sink
- Effect: POSITIVE policy sink; NEGATIVE target sink
- Confidence/status: **UNKNOWN** / `EXPORTED_POLICY_ONLY_DUPLICATE`
- Scope: previous public Phase 9 corpus

## 6X2-IPC-006
- Phase/surface: `6X2` / `IPC`
- Source: `UNKNOWN`
- Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:95877-95954;97828-97986; work/luna_worker_amazonpm_caller_inventory_20260810.csv:2-3`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: production caller UNKNOWN; test-only callers excluded
- Gate: register: no local permission; deregister: creator UID equality gate; protection holder UNKNOWN
- Identity/user scope: user scope not explicit; receiver map only
- Sink: implicit receiver registration map; first package/HOME sink NOT_FOUND
- Effect: POSITIVE gate markers; NEGATIVE target sink
- Confidence/status: **UNKNOWN** / `PROXY_RESIDUAL_DUPLICATE`
- Scope: previous public Phase 9 corpus

## 6X2-IPC-007
- Phase/surface: `6X2` / `IPC`
- Source: `UNKNOWN`
- Evidence: `artifacts/phase6mc-alta-jadx-20260810-01/sources/com/amazon/alta/h2clientservice/H2ClientService.java:104-126;226-236; artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/Manifest.java:6-9`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: external client UNKNOWN
- Gate: signature BIND_SERVICE declaration; exact holder/grant join UNKNOWN
- Identity/user scope: trusted adult/child profile scope; exact user data-flow partial
- Sink: user creation/removal and profile Settings relay; no HOME/PMS component sink
- Effect: POSITIVE workflow sink; NEGATIVE HOME/package sink
- Confidence/status: **UNKNOWN** / `EXPORTED_SERVICE_DUPLICATE`
- Scope: previous public Phase 9 corpus

## 6X2-IPC-008
- Phase/surface: `6X2` / `IPC`
- Source: `UNKNOWN`
- Evidence: `artifacts/phase6mb-vending-jadx-20260810-01/base/sources/com/google/android/finsky/setup/dse/impl/DseService.java:272-484;576-603; output/tables/phase6qb-residual-inventory.csv:8-12`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: caller/package/account provenance UNKNOWN
- Gate: o() and qualification gates; exact permission protection UNKNOWN
- Identity/user scope: UserHandle.myUserId plus injected user/profile semantics UNKNOWN
- Sink: secure-settings-class writer; browser-default/install bookkeeping; no HOME/Fire writer
- Effect: POSITIVE bounded non-HOME sink; NEGATIVE target sink
- Confidence/status: **UNKNOWN** / `VENDING_RESIDUAL_DUPLICATE`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-001
- Phase/surface: `6X2` / `OTA`
- Source: `official OTA ZIP`
- Evidence: `firmware/manifests/OTA-20260803-01/README.md; firmware/manifests/OTA-20260803-01/sha256sums.txt`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: official OTA ZIP
- Gate: PS7331.4463N trona release OTA; SHA-256 9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Historical README separately marks installed PS7330 mismatch
- Confidence/status: **UNKNOWN** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-002
- Phase/surface: `6X2` / `OTA`
- Source: `ZIP member inventory`
- Evidence: `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/members.tsv`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: ZIP member inventory
- Gate: META-INF metadata otacert update-binary updater-script; .new.dat.br; transfer lists; boot/images
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Traditional signed BLOCK OTA
- Confidence/status: **UNKNOWN** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-003
- Phase/surface: `6X2` / `OTA`
- Source: `ZIP member inventory`
- Evidence: `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/members.tsv`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: ZIP member inventory
- Gate: No payload.bin and no A/B postinstall executable member
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Postinstall executable route is negative for package-shape scope
- Confidence/status: **UNKNOWN** / `NEGATIVE`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-004
- Phase/surface: `6X2` / `OTA`
- Source: `updater-script assertions`
- Evidence: `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/updater-script.txt`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: updater-script assertions
- Gate: Build date and ro.product.device trona assertions
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Static script gate only
- Confidence/status: **UNKNOWN** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-005
- Phase/surface: `6X2` / `OTA`
- Source: `SideloadMetadataChecker.check`
- Evidence: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/dcp/ota/SideloadMetadataChecker.java:24-29`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: SideloadMetadataChecker.check
- Gate: Version signature-transition product and PVT checks
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Transition/downgrade controls are OTASettings gated
- Confidence/status: **UNKNOWN** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-006
- Phase/surface: `6X2` / `OTA`
- Source: `SideloadVerifier.verifySideloadWithRecoveryCheck`
- Evidence: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/dcp/ota/SideloadVerifier.java:31-58`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: SideloadVerifier.verifySideloadWithRecoveryCheck
- Gate: Sanity metadata RecoverySystemWrapper.verifyPackage device state
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Platform verifier implementation not present in preserved Java
- Confidence/status: **UNKNOWN** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-007
- Phase/surface: `6X2` / `OTA`
- Source: `OSUpdateValidator.validateOSUpdate`
- Evidence: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/device/software/ota/tasks/validate/OSUpdateValidator.java:73-78`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: OSUpdateValidator.validateOSUpdate
- Gate: Hash then RecoverySystem.verifyPackage then OSUpdatePropertiesValidator
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Call order is exact in source
- Confidence/status: **UNKNOWN** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-008
- Phase/surface: `6X2` / `OTA`
- Source: `SideloadMover.maybeMoveSideloadFile`
- Evidence: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/dcp/ota/SideloadMover.java:31-44`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: SideloadMover.maybeMoveSideloadFile
- Gate: Basename destination and FileHelper.moveFile
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: No Java canonicalPath realpath lstat or O_NOFOLLOW marker
- Confidence/status: **UNKNOWN** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-009
- Phase/surface: `6X2` / `OTA`
- Source: `SideloadInstaller.installSideload`
- Evidence: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/dcp/ota/SideloadInstaller.java:65-90`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: SideloadInstaller.installSideload
- Gate: Metadata/device checks then mover then installOSUpdate
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: WithoutRecoveryCheck branch is not proof of bypass because normal integrity path is separate
- Confidence/status: **UNKNOWN** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-010
- Phase/surface: `6X2` / `OTA`
- Source: `UpdateSystemWrapper.install`
- Evidence: `artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/device/framework/UpdateSystemWrapper.java:33-43`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: UpdateSystemWrapper.install
- Gate: Path prefix remap settings write then UpdateSystem.install
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Recovery/native exec caller remains separate boundary
- Confidence/status: **UNKNOWN** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-011
- Phase/surface: `6X2` / `OTA`
- Source: `OTA controller holders`
- Evidence: `artifacts/phase6j/ota-controller-holders-manifest-audit-20260805-02/com-amazon-dcp.manifest.txt; com-amazon-otter-forced-ota.manifest.txt`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: OTA controller holders
- Gate: com.amazon.dcp.ota.permission.CONTROLLER and PROCESS_UPDATES protected surface
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Holder evidence is privileged/controller capability
- Confidence/status: **UNKNOWN** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-012
- Phase/surface: `6X2` / `OTA`
- Source: `main to block-image registry`
- Evidence: `findings/phase-6mm-updater-blockimage-closure.md; artifacts/phase6mm-updater-blockimage-20260810-01/block-image-registration.csv`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: main to block-image registry
- Gate: RegisterBlockImageFunction to RegisterFunction; block_image_update to BlockImageUpdateFn 0x40b8b8
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Static registration not execution
- Confidence/status: **UNKNOWN** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-013
- Phase/surface: `6X2` / `OTA`
- Source: `PackageExtractFileFn`
- Evidence: `findings/phase-6kt-recovery-verifier-provenance.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: PackageExtractFileFn
- Gate: PackageExtractFileFn to ota_open to open and extraction fsync close
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Capability not reachability
- Confidence/status: **UNKNOWN** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-014
- Phase/surface: `6X2` / `OTA`
- Source: `BlockImageUpdateFn to WriteToPartition`
- Evidence: `findings/phase-6kt-recovery-verifier-provenance.md; findings/phase-6mm-updater-blockimage-closure.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: BlockImageUpdateFn to WriteToPartition
- Gate: PerformBlockImageUpdate to WriteToPartition to ota_write to write
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: No execution or partition write
- Confidence/status: **UNKNOWN** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-015
- Phase/surface: `6X2` / `OTA`
- Source: `updater-script`
- Evidence: `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/updater-script.txt`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: updater-script
- Gate: system vendor boot preloader lk tee1 tee2 spmfw sspm_1 cam_vpu1 cam_vpu2 cam_vpu3 and cache blocklist
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: No arbitrary target conclusion
- Confidence/status: **UNKNOWN** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-016
- Phase/surface: `6X2` / `OTA`
- Source: `MakeFreeSpaceOnCache`
- Evidence: `artifacts/phase6mm-updater-blockimage-20260810-01/canonicalization-call-sites.csv; findings/phase-6mm-updater-blockimage-closure.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: MakeFreeSpaceOnCache
- Gate: 0x417bf0 to __readlink_chk 0x4ce4e8
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Callsite is path-related but impact is unknown
- Confidence/status: **UNKNOWN** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-017
- Phase/surface: `6X2` / `OTA`
- Source: `selected direct-call graph`
- Evidence: `findings/phase-6mm-updater-blockimage-closure.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: selected direct-call graph
- Gate: No selected direct edge from readlink helper to extraction/block-image/write sinks
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Not binary-wide absence and not traversal proof
- Confidence/status: **UNKNOWN** / `NEGATIVE`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-018
- Phase/surface: `6X2` / `OTA`
- Source: `CacheSizeCheck and callers`
- Evidence: `work/luna_worker_ota_canonicalization_provenance_20260810.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: CacheSizeCheck and callers
- Gate: Body return/error branches and all indirect dispatch not fully selected
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: No symlink/traversal test
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-019
- Phase/surface: `6X2` / `OTA`
- Source: `platform recovery verifier`
- Evidence: `findings/phase-6kt-recovery-verifier-provenance.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: platform recovery verifier
- Gate: RecoverySystemWrapper delegates to platform RecoverySystem; exact native verifier absent
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Do not infer AVB bypass
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-020
- Phase/surface: `6X2` / `OTA`
- Source: `otacert and verifyPackage`
- Evidence: `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/otacert.pem; artifacts/phase6j/phase6j-ota-apk-jadx-ps7331-20260805-01/sources/com/amazon/android/os/RecoverySystemWrapper.java:21-23`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: otacert and verifyPackage
- Gate: Certificate material plus verification API call boundary
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Full cryptographic implementation unknown
- Confidence/status: **UNKNOWN** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-021
- Phase/surface: `6X2` / `OTA`
- Source: `bootloader/recovery rollback index`
- Evidence: `findings/phase-6kt-recovery-verifier-provenance.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: bootloader/recovery rollback index
- Gate: No exact rollback-index decision branch in saved corpus
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Date/version gates are not equivalent to anti-rollback proof
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-022
- Phase/surface: `6X2` / `OTA`
- Source: `shell UID / ordinary app`
- Evidence: `findings/phase-6kt-recovery-verifier-provenance.md; findings/phase-6j-ota-apk-deep-review.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: shell UID / ordinary app
- Gate: No saved caller chain from shell or ordinary APK to UpdateSystem.install/recovery writer
- Identity/user scope: PS7331
- Sink: UNKNOWN
- Effect: Bounded negative not universal absence
- Confidence/status: **UNKNOWN** / `NEGATIVE`
- Scope: previous public Phase 9 corpus

## 6X2-OTA-023
- Phase/surface: `6X2` / `OTA`
- Source: `installed device snapshot`
- Evidence: `firmware/manifests/OTA-20260803-01/README.md`
- SHA-256: `0c3204db56e1021c12fe12d23fa90fc275fcfec4f485570bdde76afcc2241ddc`
- Caller: installed device snapshot
- Gate: Installed snapshot PS7330.4104N versus adjacent OTA PS7331.4463N
- Identity/user scope: PS7330
- Sink: UNKNOWN
- Effect: Keep historical mismatch separate from current PS7331 package facts
- Confidence/status: **UNKNOWN** / `VERSION_MISMATCH`
- Scope: previous public Phase 9 corpus

## AC-001
- Phase/surface: `6X2` / `User 0 MAIN+HOME resolver`
- Source: `findings/phase-6cy-accessibility-reboot-unlock-result.md; output/tables/phase6cy-reboot-unlock-result.csv`
- Evidence: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **confirmed** / `TRUE_HOME_FIRE`
- Scope: previous public Phase 9 corpus

## AC-002
- Phase/surface: `6X2` / `Original Phase 4 Accessibility direct redirect`
- Source: `findings/phase-4b-assisted-workarounds.md; adb/phase4/PHASE4-ACCESSIBILITY-T01/measure/summary.tsv`
- Evidence: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **confirmed** / `FAILED_FOREGROUND_REDIRECT`
- Scope: previous public Phase 9 corpus

## AC-003
- Phase/surface: `6X2` / `PendingIntent GUI consent boundary`
- Source: `findings/phase-6cv-accessibility-pendingintent-gui-boundary.md; output/tables/phase6cv-accessibility-pendingintent-gui-boundary.csv`
- Evidence: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **confirmed-boundary** / `UNKNOWN_NOT_MEASURED`
- Scope: previous public Phase 9 corpus

## AC-004
- Phase/surface: `6X2` / `Microsoft retry Accessibility 350/1000/1800 ms`
- Source: `findings/phase-6cy-ms-targeted-accessibility-retry.md; output/tables/phase6cy-ms-targeted-accessibility-retry.csv`
- Evidence: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **confirmed-but-nondeterministic** / `FOREGROUND_REDIRECT`
- Scope: previous public Phase 9 corpus

## AC-005
- Phase/surface: `6X2` / `Reboot plus owner unlock Accessibility retry`
- Source: `findings/phase-6cy-accessibility-reboot-unlock-result.md; findings/phase-6hb-ms-accessibility-reboot-persistence.md`
- Evidence: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **confirmed-foreground-only** / `UNLOCK_AFTER_REDIRECT`
- Scope: previous public Phase 9 corpus

## AC-006
- Phase/surface: `6X2` / `Accessibility timeout 50 ms A/B`
- Source: `findings/phase-6cy-accessibility-timeout-ab-boundary.md; output/tables/phase6cy-accessibility-reboot-persistence.csv`
- Evidence: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **confirmed-negative-optimization** / `FOREGROUND_REDIRECT_NOT_ADOPTED`
- Scope: previous public Phase 9 corpus

## AC-007
- Phase/surface: `6X2` / `Accessibility consume/key-event path`
- Source: `adb/phase6cy/PHASE6CY-CONSUME-HOME-20260807-02/result.json; findings/phase-6cy-accessibility-adb-pause-boundary.md`
- Evidence: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **confirmed-boundary** / `FAILED_OR_PARTIAL_FOREGROUND`
- Scope: previous public Phase 9 corpus

## AC-008
- Phase/surface: `6X2` / `UsageStats public third-party route`
- Source: `adb/phase6ac/PHASE6AC-RO-20260805-01/pm_dump.stdout.txt; adb/phase6ao/PHASE6AO-RO-20260805-01/package_dump_full.stdout.txt`
- Evidence: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **unknown** / `UNKNOWN_NOT_VALIDATED`
- Scope: previous public Phase 9 corpus

## AC-009
- Phase/surface: `6X2` / `ADB-connected host foreground monitor`
- Source: `findings/phase-6iq-adb-foreground-fallback.md; adb/phase6iq/PHASE6IQ-ADB-MONITOR-20260807-05/`
- Evidence: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **confirmed-but-not-approved** / `FOREGROUND_REDIRECT_CLOSED`
- Scope: previous public Phase 9 corpus

## AC-010
- Phase/surface: `6X2` / `Unlock workaround / keyguard bypass`
- Source: `findings/phase-6hb-ms-accessibility-reboot-persistence.md; findings/phase-6cy-accessibility-reboot-unlock-result.md`
- Evidence: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **unknown** / `UNKNOWN_NOT_A_WORKAROUND`
- Scope: previous public Phase 9 corpus

## AC-011
- Phase/surface: `6X2` / `Transparent resident assist candidate`
- Source: `tools/phase4-accessibility/README.md; tools/phase4-accessibility/src/org/fireosresearch/phase4/redirect/LauncherRedirectService.java`
- Evidence: `work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `9facf88fa4ba378ab9665cac2e6e6a69a3891a106dd9f9131f80fdc2f9014d4c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **conditional** / `SAFE_FOREGROUND_ASSIST_ONLY`
- Scope: previous public Phase 9 corpus

## 6X2-ROUTES-001
- Phase/surface: `6X2` / `OOBE receiver -> exact numeric user -> setup/component sink`
- Source: `UNKNOWN`
- Evidence: `findings/phase-6z-evidence-index.md; work/luna_worker_phase6z_components_20260810.csv rows 6Z-001/002; artifacts/phase6mg-oobe-helper-scope-20260810-01/`
- SHA-256: `d666aab4deae3bd37ddbc528dd63680256318b709a467659925b3952ef19829c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **UNKNOWN** / `untested_host_only`
- Scope: previous public Phase 9 corpus

## 6X2-ROUTES-002
- Phase/surface: `6X2` / `DCPMS exported lifecycle receiver -> producer/permission -> profile-policy sink`
- Source: `UNKNOWN`
- Evidence: `work/luna_worker_phase6z_components_20260810.csv rows 6Z-003/005/006; artifacts/phase6bk/protected-broadcast-expanded-20260810-01/`
- SHA-256: `d666aab4deae3bd37ddbc528dd63680256318b709a467659925b3952ef19829c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **UNKNOWN** / `untested_host_only`
- Scope: previous public Phase 9 corpus

## 6X2-ROUTES-003
- Phase/surface: `6X2` / `ProductPolicy fosinit registration -> Binder publication -> caller gate`
- Source: `UNKNOWN`
- Evidence: `work/luna_worker_phase6z_components_20260810.csv row 6Z-007; artifacts/phase6bg-product-policy-readonly-20260805-01/; findings/phase-6x-report.md`
- SHA-256: `d666aab4deae3bd37ddbc528dd63680256318b709a467659925b3952ef19829c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **UNKNOWN** / `untested_host_only`
- Scope: previous public Phase 9 corpus

## 6X2-ROUTES-004
- Phase/surface: `6X2` / `AmazonActivityManager preWarmApplicationForUser -> identity/user propagation -> process/state sink`
- Source: `UNKNOWN`
- Evidence: `findings/phase-6x-prewarm-authorization.md; work/luna_worker_phase6up_asp_prewarm_closure_20260810.csv; artifacts/phase6bk/ipc-ota-closure-20260810-02/`
- SHA-256: `d666aab4deae3bd37ddbc528dd63680256318b709a467659925b3952ef19829c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **UNKNOWN** / `untested_host_only`
- Scope: previous public Phase 9 corpus

## 6X2-ROUTES-005
- Phase/surface: `6X2` / `USE_SDK / PLUGIN / PLUGIN_CONSUMER declaration -> consumer/holder/grant -> sensitive sink`
- Source: `UNKNOWN`
- Evidence: `work/luna_worker_phase6y_permission_20260810.csv; artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- SHA-256: `d666aab4deae3bd37ddbc528dd63680256318b709a467659925b3952ef19829c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **UNKNOWN** / `untested_host_only`
- Scope: previous public Phase 9 corpus

## 6X2-ROUTES-006
- Phase/surface: `6X2` / `OTA verifier/canonicalization -> indirect extraction/write sink`
- Source: `UNKNOWN`
- Evidence: `findings/phase-6y-ota-staging-boundary.md; artifacts/phase6mk-updater-dispatch-20260810-04/; artifacts/phase6kt/recovery-verifier-audit-20260810-01/`
- SHA-256: `d666aab4deae3bd37ddbc528dd63680256318b709a467659925b3952ef19829c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **UNKNOWN** / `untested_host_only`
- Scope: previous public Phase 9 corpus

## 6AE-001
- Phase/surface: `6X3` / `OTA/OOBE`
- Source: `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java:27-61; decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96107-96126`
- Evidence: `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java:27-61; decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96107-96126`
- SHA-256: `c29b32bf6874b245859357d926773193c15771a6eb254f97edac57541ae5cb90;ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: AmazonPackageManagerService.onBootPhase(550) -> BootAfterSystemOTAReceiver.onReceive
- Gate: isUpgrade + BOOT_AFTER_SYSTEM_OTA lifecycle; protected RECEIVE_BOOT_AFTER_SYSTEM_OTA provenance; exact ordinary sender UNKNOWN
- Identity/user scope: No ordinary Binder caller; trusted system-server lifecycle identity; clearCallingIdentity UNKNOWN/NOT APPLICABLE; Context-derived numeric user UNKNOWN
- Sink: PackageHelper.enableComponent(OobeHomeActivity); OOBEActivationHelper.activateOOBEIF
- Effect: Component/setup-state sink statically confirmed; no proven Fire HOME selector or runtime effect
- Confidence/status: **STATIC_LIFECYCLE_SINK_CALLER_AND_USER_UNKNOWN** / `STATIC_LIFECYCLE_SINK_CALLER_AND_USER_UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6AE-002
- Phase/surface: `6X3` / `OTA/OOBE settings`
- Source: `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java:29-34,53-56`
- Evidence: `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java:29-34,53-56`
- SHA-256: `6ebcb7eef7a03459a76b9c21cd59b61a30947f2b00a5624a4646825b8e3223d2`
- Caller: BootAfterSystemOTAReceiver guarded branch -> OOBEActivationHelper
- Gate: Same protected OTA lifecycle guard; ordinary caller UNKNOWN
- Identity/user scope: No Binder caller in helper path; identity inheritance from receiver Context; clearCallingIdentity UNKNOWN; ContentResolver/Context user inherited; numeric user UNKNOWN
- Sink: SettingsDBUtils -> Settings.Secure user_setup_complete=0 and isOOBEActive=1
- Effect: Setup/OOBE settings mutation only when lifecycle predicate passes; no HOME/PMS writer
- Confidence/status: **STATIC_SETTINGS_SINK_USER_UNKNOWN** / `STATIC_SETTINGS_SINK_USER_UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6AE-003
- Phase/surface: `6X3` / `DevicePolicy/profile`
- Source: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:115-122; work/luna_worker_phase6z_components_20260810.csv:4`
- Evidence: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:115-122; work/luna_worker_phase6z_components_20260810.csv:4`
- SHA-256: `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`
- Caller: PCAActiveProfileReceiver <- com.amazon.device.ACTION_ACTIVE_PROFILE_UPDATED -> DeviceExperienceModeEvaluator.evaluate
- Gate: Receiver exported with no local permission marker in saved manifest; producer, protection/holder, and sender UNKNOWN
- Identity/user scope: Broadcast receiver identity; Binder caller/clearCallingIdentity not present in bounded receiver evidence; Receiver application user and cross-user acceptance UNKNOWN
- Sink: CDE profile type/OS user type/active-app persistence feeding policy evaluator
- Effect: Policy/profile sink confirmed statically; no SettingsProvider, PMS, HOME, or OTA sink joined
- Confidence/status: **STATIC_EXPORTED_POLICY_SINK_CALLER_GATE_USER_UNKNOWN** / `STATIC_EXPORTED_POLICY_SINK_CALLER_GATE_USER_UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6AE-004
- Phase/surface: `6X3` / `DevicePolicy/profile`
- Source: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:105-113; work/luna_worker_phase6z_components_20260810.csv:5`
- Evidence: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt:105-113; work/luna_worker_phase6z_components_20260810.csv:5`
- SHA-256: `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`
- Caller: DeviceUserSwitchReceiver <- android.intent.action.USER_SWITCHED -> CDE/PCA policy persistence
- Gate: Protected USER_SWITCHED producer is system/framework; ordinary sender not established
- Identity/user scope: Lifecycle receiver context; no Binder caller or clearCallingIdentity evidence in bounded slice; Receiver user/profile scope UNKNOWN
- Sink: CDE PCA-profile and OS-user persistence; child active-app-list clear to evaluator
- Effect: Policy/profile state effect only; no HOME/PMS package-state or OTA sink
- Confidence/status: **STATIC_PROTECTED_POLICY_SINK_CALLER_USER_UNKNOWN** / `STATIC_PROTECTED_POLICY_SINK_CALLER_USER_UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6AE-005
- Phase/surface: `6X3` / `service-registration/ProductPolicy`
- Source: `artifacts/phase6bg-product-policy-readonly-20260805-01/productpolicyservice_fosinit.stderr.txt:registration record; output/call-graphs/phase6jd-fosinit-registration-flow.mmd`
- Evidence: `artifacts/phase6bg-product-policy-readonly-20260805-01/productpolicyservice_fosinit.stderr.txt:registration record; output/call-graphs/phase6jd-fosinit-registration-flow.mmd`
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Caller: fosinit productpolicyservice registration -> ProductPolicyService Binder publication
- Gate: init/system-server loader and in-process fosinit registration; external caller and Binder permission gate UNKNOWN
- Identity/user scope: system-server/service identity; clearCallingIdentity UNKNOWN; User scope UNKNOWN; no method argument/sink recovered in registration-only input
- Sink: ProductPolicy service registration only; exact downstream state sink NOT FOUND
- Effect: Registration is capability evidence only, not a vulnerability or callable route
- Confidence/status: **REGISTRATION_ONLY_CALLER_GATE_USER_SINK_UNKNOWN** / `REGISTRATION_ONLY_CALLER_GATE_USER_SINK_UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6AE-006
- Phase/surface: `6X3` / `Framework IPC/prewarm`
- Source: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40534; proxy:394721; findings/phase-6x-prewarm-authorization.md:114-121`
- Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40534; proxy:394721; findings/phase-6x-prewarm-authorization.md:114-121`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;895cf94b87d92b16af24ff9f1b3d18309d504dec9ffd928399e7b6ff4fbff92a`
- Caller: AmazonActivityManagerImpl -> IAmazonActivityManager.preWarmApplicationForUser -> BinderService
- Gate: checkCallingPermission(com.amazon.permission.APP_PREWARM); result consumption in bounded method UNKNOWN; service-manager/SELinux gate UNKNOWN
- Identity/user scope: clearCallingIdentity observed after permission check; restore path present; caller UID handling beyond slice UNKNOWN; Explicit user int supplied; cross-user validation UNKNOWN
- Sink: IPackageManager.getApplicationInfo(target,1024,user) -> PreWarmCacheHelper -> ActivityManagerService.startProcessLocked(...,prewarm,...)
- Effect: Process-start/cache sink statically confirmed; no component-state, HOME, OTA, or privilege transition observed
- Confidence/status: **STATIC_AUTHORIZATION_ANOMALY_CANDIDATE_CALLER_USER_UNKNOWN** / `STATIC_AUTHORIZATION_ANOMALY_CANDIDATE_CALLER_USER_UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6AE-007
- Phase/surface: `6X3` / `permission declaration -> sensitive sink`
- Source: `work/luna_worker_phase6y_permission_20260810.csv:2-5; artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt:permission records`
- Evidence: `work/luna_worker_phase6y_permission_20260810.csv:2-5; artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt:permission records`
- SHA-256: `4b0ac817fe8cd35f68e243cb9eed0c97211463ad117610a9a04ceda76616529b;89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`
- Caller: android.amazon.perm declaration -> possible USE_SDK/PLUGIN consumer; exact consumer/caller not recovered
- Gate: USE_SDK protection=normal; PLUGIN=dangerous; PLUGIN_CONSUMER protection UNKNOWN; declaration is not an enforcement proof
- Identity/user scope: No Binder transaction or identity relay joined; User scope UNKNOWN
- Sink: No exact PMS/Settings/DevicePolicy/HOME/OTA sink found in bounded join
- Effect: Declaration-only evidence; no observed effect and no vulnerability conclusion
- Confidence/status: **DECLARATION_ONLY_NO_SINK** / `DECLARATION_ONLY_NO_SINK`
- Scope: previous public Phase 9 corpus

## 6AE-008
- Phase/surface: `6X3` / `OTA staging`
- Source: `findings/phase-6y-ota-staging-boundary.md:20-38,80-88; source methods summarized in bounded report`
- Evidence: `findings/phase-6y-ota-staging-boundary.md:20-38,80-88; source methods summarized in bounded report`
- SHA-256: `49614a27fc9c6c4d94ad01baf44b0d270bd8fc60fa9fd1ea8764913598b15330`
- Caller: external-storage sideload discovery -> SideloadInstaller verification -> UpdateSystemWrapper.install
- Gate: Metadata/device/signature/recovery verification gates; exact caller/SELinux/native flags UNKNOWN
- Identity/user scope: No Binder caller established in saved Java path; clearCallingIdentity UNKNOWN/NOT APPLICABLE; External-storage path and OTA lifecycle scope; exact user scope UNKNOWN
- Sink: SideloadMover basename + FileHelper.renameTo/copy-delete -> UpdateSystem.install high-risk update state transition
- Effect: Partition/update sink statically confirmed; no execution, partition effect, root, or bootloader effect observed
- Confidence/status: **STATIC_OTA_SINK_NATIVE_CALLER_SCOPE_UNKNOWN** / `STATIC_OTA_SINK_NATIVE_CALLER_SCOPE_UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6AF-OTA-001
- Phase/surface: `6X3` / `verifier-to-script`
- Source: `firmware/extracted/PS7331/META-INF/com/google/android/updater-script:1-2`
- Evidence: `firmware/extracted/PS7331/META-INF/com/google/android/updater-script:1-2`
- SHA-256: `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248`
- Caller: recovery/Edify context implied; Java verifier caller remains privileged OTA path
- Gate: recovery/Edify context implied; Java verifier caller remains privileged OTA path
- Identity/user scope: UNKNOWN
- Sink: script admission gate before named targets; AVB/rollback implementation and caller handoff are not joined
- Effect: date gate aborts when package build date is older and product gate aborts when ro.product.device != trona; no rollback-index decision is evidenced
- Confidence/status: **UNRESOLVED_DATE_PRODUCT_NOT_ROLLBACK** / `UNRESOLVED_DATE_PRODUCT_NOT_ROLLBACK`
- Scope: previous public Phase 9 corpus

## 6AF-OTA-002
- Phase/surface: `6X3` / `verifier-provenance`
- Source: `artifacts/phase6kt/recovery-verifier-audit-20260810-01/audit.json:binary_markers.update_binary[0..5]`
- Evidence: `artifacts/phase6kt/recovery-verifier-audit-20260810-01/audit.json:binary_markers.update_binary[0..5]`
- SHA-256: `01e29ec3a2649d85d033ce7ce65034631ebb44ef00633e34a95b0eb063f317f9`
- Caller: RecoverySystemWrapper/RecoverySystem API boundary; native recovery identity not recovered
- Gate: RecoverySystemWrapper/RecoverySystem API boundary; native recovery identity not recovered
- Identity/user scope: UNKNOWN
- Sink: native updater capability is evidenced, while verifier-to-AVB/rollback-to-exec provenance remains absent
- Effect: binary markers include package_extract_file, block_image_* , /dev/block/by-name and readlink, but audit has no AVB or rollback-index implementation edge
- Confidence/status: **PROVENANCE_GAP_AVB_ROLLBACK** / `PROVENANCE_GAP_AVB_ROLLBACK`
- Scope: previous public Phase 9 corpus

## 6AF-OTA-003
- Phase/surface: `6X3` / `canonicalization-to-cache`
- Source: `artifacts/phase6ne-updater-cache-flow-20260810-03/focus-disassembly.txt:CacheSizeCheck 0x414720-0x41475c`
- Evidence: `artifacts/phase6ne-updater-cache-flow-20260810-03/focus-disassembly.txt:CacheSizeCheck 0x414720-0x41475c`
- SHA-256: `ca482551bea143f0c22ca3599655a6c10bfbb66033c9f99242f72048220797ee`
- Caller: PerformBlockImageUpdate caller at 0x409cb4 and 0x409cdc; native recovery identity only
- Gate: PerformBlockImageUpdate caller at 0x409cb4 and 0x409cdc; native recovery identity only
- Identity/user scope: UNKNOWN
- Sink: CacheSizeCheck normalizes helper failure into a nonzero error result; exact cache path/size argument provenance is unresolved
- Effect: 0x414730 BL MakeFreeSpaceOnCache; 0x414734 tbnz w0,#0x1f -> 0x414740; sign-bit error logs and returns w0=1, otherwise returns w0=0
- Confidence/status: **NEW_ERROR_BRANCH** / `NEW_ERROR_BRANCH`
- Scope: previous public Phase 9 corpus

## 6AF-OTA-004
- Phase/surface: `6X3` / `cache-result-to-writer`
- Source: `artifacts/phase6ne-updater-cache-flow-20260810-03/return-branches.csv:CacheSizeCheck rows 7-8; PerformBlockImageUpdate rows 9-10`
- Evidence: `artifacts/phase6ne-updater-cache-flow-20260810-03/return-branches.csv:CacheSizeCheck rows 7-8; PerformBlockImageUpdate rows 9-10`
- SHA-256: `95f469e697c636a2f09bcb6d3f27540f9d336a4bf042d2a5b33b37156a28b87b`
- Caller: PerformBlockImageUpdate direct callers at 0x409cb4/0x409cdc; recovery/update-binary gate
- Gate: PerformBlockImageUpdate direct callers at 0x409cb4/0x409cdc; recovery/update-binary gate
- Identity/user scope: UNKNOWN
- Sink: decision branches are proven, but the selected evidence does not prove whether either continuation reaches WriteToPartition for every input
- Effect: 0x409cb8 cbz w0,0x409cc8 and 0x409ce0 cbz w0,0x40b27c: zero result continues; nonzero branch target is not classified as a write bypass
- Confidence/status: **NEW_BOUNDED_NEGATIVE** / `NEW_BOUNDED_NEGATIVE`
- Scope: previous public Phase 9 corpus

## 6AF-OTA-005
- Phase/surface: `6X3` / `cache-helper-indirect-edges`
- Source: `artifacts/phase6ne-updater-cache-flow-20260810-03/direct-call-edges.csv:MakeFreeSpaceOnCache 0x417858,0x4178b0,0x4178e0,0x417904,0x41792c,0x41793c,0x417a18,0x417a5c,0x417a6c,0x417c54,0x417c84,0x417d0c,0x417d1c,0x417d24,0x417d38,0x417d7c,0x417e60,0x417f74,0x417fb4,0x417fbc`
- Evidence: `artifacts/phase6ne-updater-cache-flow-20260810-03/direct-call-edges.csv:MakeFreeSpaceOnCache 0x417858,0x4178b0,0x4178e0,0x417904,0x41792c,0x41793c,0x417a18,0x417a5c,0x417a6c,0x417c54,0x417c84,0x417d0c,0x417d1c,0x417d24,0x417d38,0x417d7c,0x417e60,0x417f74,0x417fb4,0x417fbc`
- SHA-256: `d653e4a84898509781a333c56502087a83981781fcf6612d7026bfd79602b477`
- Caller: MakeFreeSpaceOnCache entered from CacheSizeCheck 0x414730; no untrusted caller established
- Gate: MakeFreeSpaceOnCache entered from CacheSizeCheck 0x414730; no untrusted caller established
- Identity/user scope: UNKNOWN
- Sink: cache helper's filesystem operations include readlink-check at 0x417bf0 and unlink at 0x417ea8, but function-pointer/indirect target semantics remain unknown
- Effect: rows classify address-only targets as unresolved; they are not symbol-resolved direct calls and cannot be safely joined to extraction or writer sinks
- Confidence/status: **UNRESOLVED_INDIRECT_DISPATCH** / `UNRESOLVED_INDIRECT_DISPATCH`
- Scope: previous public Phase 9 corpus

## 6AF-OTA-006
- Phase/surface: `6X3` / `canonicalization-no-follow`
- Source: `artifacts/phase6mk-updater-dispatch-20260810-04/canonicalization-context.csv:all 5 rows; artifacts/phase6md-native-updater-path-audit-20260810-02/summary.json:18-19`
- Evidence: `artifacts/phase6mk-updater-dispatch-20260810-04/canonicalization-context.csv:all 5 rows; artifacts/phase6md-native-updater-path-audit-20260810-02/summary.json:18-19`
- SHA-256: `44f61840637e65d7a263b4912d340d834aba1b41b7a84dc7d20382e45fd1a726;6dec85cee148a60daba1e8c781f30370389c6d95ff787623cb6ac830f058a834`
- Caller: registry dispatch is indirect; selected native updater context only
- Gate: registry dispatch is indirect; selected native updater context only
- Identity/user scope: UNKNOWN
- Sink: canonicalization-to-extraction/writer argument flow and O_NOFOLLOW semantics remain unresolved
- Effect: readlink/readlinkat/__readlink_chk/realpath markers exist, but selected direct graph has zero canonicalization direct edges; this does not prove no-follow or absence of an indirect edge
- Confidence/status: **BOUNDED_NEGATIVE_NO_DIRECT_EDGE** / `BOUNDED_NEGATIVE_NO_DIRECT_EDGE`
- Scope: previous public Phase 9 corpus

## 6AF-OTA-007
- Phase/surface: `6X3` / `extraction-to-named-writer`
- Source: `artifacts/phase6md-native-updater-path-audit-20260810-02/path-write-call-edges.csv:PackageExtractFileFn 0x4021b4/0x4022cc/0x40238c; WriteToPartition 0x413dcc-0x413f08`
- Evidence: `artifacts/phase6md-native-updater-path-audit-20260810-02/path-write-call-edges.csv:PackageExtractFileFn 0x4021b4/0x4022cc/0x40238c; WriteToPartition 0x413dcc-0x413f08`
- SHA-256: `7dc9e3ef02a86d978d5973640bad0273288d83c71b8e7117eefb96c7bfffdbb`
- Caller: registered Edify handlers; recovery updater identity; ordinary app/shell caller not established
- Gate: registered Edify handlers; recovery updater identity; ordinary app/shell caller not established
- Identity/user scope: UNKNOWN
- Sink: capability-to-sink exists statically; per-call named-partition argument provenance and verifier acceptance state are not closed
- Effect: direct edges prove extraction/open and writer/open/write wrappers, but do not join archive entry/path arguments to the fixed script target for a particular invocation
- Confidence/status: **UNRESOLVED_ARGUMENT_PROVENANCE** / `UNRESOLVED_ARGUMENT_PROVENANCE`
- Scope: previous public Phase 9 corpus

## 6AF-OTA-008
- Phase/surface: `6X3` / `caller-identity-handoff`
- Source: `artifacts/phase6kt/recovery-verifier-audit-20260810-01/audit.json:inputs.recovery_wrapper; inputs.update_system_wrapper; execution_policy`
- Evidence: `artifacts/phase6kt/recovery-verifier-audit-20260810-01/audit.json:inputs.recovery_wrapper; inputs.update_system_wrapper; execution_policy`
- SHA-256: `01e29ec3a2649d85d033ce7ce65034631ebb44ef00633e34a95b0eb063f317f9`
- Caller: Java privileged OTA path calls RecoverySystem verification and UpdateSystem.install; native recovery/SELinux identity absent
- Gate: Java privileged OTA path calls RecoverySystem verification and UpdateSystem.install; native recovery/SELinux identity absent
- Identity/user scope: UNKNOWN
- Sink: verifier acceptance, UpdateSystem handoff, recovery exec, and updater registry are separate provenance domains
- Effect: audit explicitly records recovery/native execution false and does not recover the final native caller, execution flags, or SELinux domain
- Confidence/status: **UNRESOLVED_NATIVE_CALLER_IDENTITY** / `UNRESOLVED_NATIVE_CALLER_IDENTITY`
- Scope: previous public Phase 9 corpus

## 6AG-001
- Phase/surface: `6X3` / `Amazon path absence`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: No exact shipped native caller for /proc/idme, /proc/amzn_drvs or lifecycle nodes
- Gate: Source modes/DT permission are insufficient; exact file_contexts/vendor-TE/domain absent
- Identity/user scope: Source modes/DT permission are insufficient; exact file_contexts/vendor-TE/domain absent
- Sink: Read/diagnostic or conditional test state only; package/HOME/root effect UNKNOWN
- Effect: No literal drivers/amazon/ member; actual device/amazon/kernel/driver/{amzn_idme,amzn_drv_test,amzn_logger,amzn_sign_of_life}.c; staging Kconfig/Makefile includes Amazon chain
- Confidence/status: **SOURCE_ONLY; platform.tar; source_scope_driver_audit; phase6uk** / `SOURCE_ONLY; platform.tar; source_scope_driver_audit; phase6uk`
- Scope: previous public Phase 9 corpus

## 6AG-002
- Phase/surface: `6X3` / `Amazon /proc/amzn_drvs`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: No exact open/write caller; com.amazon.connectivitydiag presence is not a proc caller
- Gate: proc mode/label, init import and TE allow not jointly retained; caller UID/domain UNKNOWN
- Identity/user scope: proc mode/label, init import and TE allow not jointly retained; caller UID/domain UNKNOWN
- Sink: If built/allowed, factory test dispatcher can alter diagnostic/RTC-special state; no proved package/HOME/root effect
- Effect: amzn_drv_test.c:762-866 creates writable test children and dispatches copied input; Kconfig:65-68 default n; Makefile:28
- Confidence/status: **SOURCE_CAPABILITY_ONLY; amzn_drv_test hash 6c2309f996cacafaab35cce3935bcb725a5259211751af89df88d3732797029e; phase6nb/6nd** / `SOURCE_CAPABILITY_ONLY; amzn_drv_test hash 6c2309f996cacafaab35cce3935bcb725a5259211751af89df88d3732797029e; phase6nb/6nd`
- Scope: previous public Phase 9 corpus

## 6AG-003
- Phase/surface: `6X3` / `Amazon /proc/idme`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: IDME HAL/library evidence only; no exact ELF open/read path-specific caller
- Gate: UID 1000 is source-side handling, not caller identity; exact file_contexts, vendor-TE allow and domain join incomplete
- Identity/user scope: UID 1000 is source-side handling, not caller identity; exact file_contexts, vendor-TE allow and domain join incomplete
- Sink: Possible device metadata disclosure; no write/package/HOME/root effect established
- Effect: amzn_idme.c:316-347 registers /proc/idme root/children with read fops; DT permission handling can clear write bits; mac_sec forces 0400/uid 1000
- Confidence/status: **SOURCE_PLUS_CONFIG; amzn_idme hash ab6484ae7a694412ec4eeabb67133ddd0c0af221076b6d989c8ab1fe7c84e61e; phase6so/6wi** / `SOURCE_PLUS_CONFIG; amzn_idme hash ab6484ae7a694412ec4eeabb67133ddd0c0af221076b6d989c8ab1fe7c84e61e; phase6so/6wi`
- Scope: previous public Phase 9 corpus

## 6AG-004
- Phase/surface: `6X3` / `RPMB char ABI`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: rpmb_svc/process evidence does not identify exact native open + ioctl callsite or package owner
- Gate: No capable()/caller policy tuple established; node mode/file_contexts/domain UNKNOWN
- Identity/user scope: No capable()/caller policy tuple established; node mode/file_contexts/domain UNKNOWN
- Sink: Authenticated persistent-storage operation is a possible state sink; no package/HOME/root effect or low-privilege reachability proved
- Effect: drivers/char/rpmb/core.c rpmb_fops exposes unlocked_ioctl; .read/.write are NULL; device_create uses RPMB_NAME 0
- Confidence/status: **SOURCE_ONLY_CALLER_GAP; prior phase6xg/6so RPMB rows** / `SOURCE_ONLY_CALLER_GAP; prior phase6xg/6so RPMB rows`
- Scope: previous public Phase 9 corpus

## 6AG-005
- Phase/surface: `6X3` / `MediaTek perf ioctl`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: No exact shipped native ELF path-specific open/write/ioctl caller in bounded native inventory
- Gate: 0664 is owner/group writable and world-readable, not world-writable; effective owner/group, file_contexts and domain allow UNKNOWN
- Identity/user scope: 0664 is owner/group writable and world-readable, not world-writable; effective owner/group, file_contexts and domain allow UNKNOWN
- Sink: Performance/governor/control state may be affected by an authorized writer; no PMS/HOME/root effect shown
- Effect: drivers/misc/mediatek/performance/perf_ioctl/perf_ioctl.c registers /proc/perfmgr/perf_ioctl; write/ioctl/compat_ioctl; source mode 0664
- Confidence/status: **SOURCE_PLUS_MODE; gpl inventory/phase6so** / `SOURCE_PLUS_MODE; gpl inventory/phase6so`
- Scope: previous public Phase 9 corpus

## 6AG-006
- Phase/surface: `6X3` / `AUXADC factory/debug`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: No exact shipped native caller for AUXADC ioctl or writable sysfs/proc attributes
- Gate: No capable() proof, exact mode/owner, file_contexts or TE caller allow; UID/domain UNKNOWN
- Identity/user scope: No capable() proof, exact mode/owner, file_contexts or TE caller allow; UID/domain UNKNOWN
- Sink: ADC/register diagnostic and calibration/hardware-read state may be affected; no package/HOME/root effect established
- Effect: mtk_auxadc.c:553-667 ioctl/compat ioctl; :1515-1651 attrs and writable dump/status controls; module init
- Confidence/status: **SOURCE_PLUS_IMAGE_MARKER; mtk_auxadc hash 5ffbce942417fc6aca773d90e4c6935f508087f9a80d96138a7ecc30561ed327; source_scope audit** / `SOURCE_PLUS_IMAGE_MARKER; mtk_auxadc hash 5ffbce942417fc6aca773d90e4c6935f508087f9a80d96138a7ecc30561ed327; source_scope audit`
- Scope: previous public Phase 9 corpus

## 6AG-007
- Phase/surface: `6X3` / `PMIC debugfs`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: No exact shipped native debugfs writer or caller
- Gate: Source debugfs entries are not a policy proof; exact debugfs type, file_contexts/TE and domain UNKNOWN
- Identity/user scope: Source debugfs entries are not a policy proof; exact debugfs type, file_contexts/TE and domain UNKNOWN
- Sink: Potential PMIC register/debug state effect if writable surface is exposed; no package/HOME/root effect
- Effect: upmu_debugfs.c:323-351 creates mtk_pmic debugfs/sysfs entries including writable dump_pmic_reg
- Confidence/status: **SOURCE_ONLY_POLICY_GAP; upmu_debugfs hash db8dfc551225586a717af6cc96057b8d810548cfb5d5693b8ec092; phase6uk** / `SOURCE_ONLY_POLICY_GAP; upmu_debugfs hash db8dfc551225586a717af6cc96057b8d810548cfb5d5693b8ec092; phase6uk`
- Scope: previous public Phase 9 corpus

## 6AG-008
- Phase/surface: `6X3` / `Input touchscreen/factory proc`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: No exact shipped native proc/sysfs write caller in bounded corpus
- Gate: No joined node mode/file_contexts/TE/domain evidence; caller identity UNKNOWN
- Identity/user scope: No joined node mode/file_contexts/TE/domain evidence; caller identity UNKNOWN
- Sink: Possible touch firmware/calibration/input-state mutation; no package/HOME/root effect proved
- Effect: MTK/Focaltech touchscreen source includes debug/factory/proc helpers under drivers/input/touchscreen/mediatek; exact write handlers vary by selected IC
- Confidence/status: **SOURCE_VARIANT_UNRESOLVED; tar member scan; phase6me broad inventory** / `SOURCE_VARIANT_UNRESOLVED; tar member scan; phase6me broad inventory`
- Scope: previous public Phase 9 corpus

## 6AG-009
- Phase/surface: `6X3` / `power-supply writer cross-check`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: No exact shipped native writer, package, UID or domain; generic store is not a caller
- Gate: S_IWUSR is added conditionally by provider; SELinux/file_contexts/domain allow UNKNOWN
- Identity/user scope: S_IWUSR is added conditionally by provider; SELinux/file_contexts/domain allow UNKNOWN
- Sink: Battery/charger property mutation is provider-dependent; no package/HOME/root effect
- Effect: Generic power_supply_sysfs.c .store calls power_supply_set_property only when provider property_is_writeable()>0; existing phase6xg row
- Confidence/status: **DEDUP_CROSSCHECK_NOT_NEW; source hash 54409386286849db4768d1b013b0151c3b8e52d3c5b4e434b52d8881364cc38e; phase6xg** / `DEDUP_CROSSCHECK_NOT_NEW; source hash 54409386286849db4768d1b013b0151c3b8e52d3c5b4e434b52d8881364cc38e; phase6xg`
- Scope: previous public Phase 9 corpus

## 6AG-010
- Phase/surface: `6X3` / `input/uinput cross-check`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: No exact shipped native ELF /dev/uinput open/write/ioctl caller; library/package markers absent
- Gate: No local capable()/credential gate found; node policy, UID/domain and caller allow UNKNOWN
- Identity/user scope: No local capable()/credential gate found; node policy, UID/domain and caller allow UNKNOWN
- Sink: Synthetic input injection can affect kernel input graph; no PMS/HOME/root effect
- Effect: uinput.c:909-933 misc registration with read/write/unlocked_ioctl/compat_ioctl; UI_DEV_CREATE/DESTROY and event writes
- Confidence/status: **DEDUP_CROSSCHECK_NOT_NEW; source hash 98b41492311d9b9fb9ccbfe269a2fddc0fb436f3048b7887e1f6e5482d36211a; phase6xg** / `DEDUP_CROSSCHECK_NOT_NEW; source hash 98b41492311d9b9fb9ccbfe269a2fddc0fb436f3048b7887e1f6e5482d36211a; phase6xg`
- Scope: previous public Phase 9 corpus

## 6AG-011
- Phase/surface: `6X3` / `CMDQ/ION artifact boundary`
- Source: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- Evidence: `work/luna_worker_phase6ag_driver_source_gap_20260810.csv`
- SHA-256: `8da31c63a2e988f9c1f735ac2aea0db1b824415881c539cccd1956e6a0056bac`
- Caller: ION libion/libion_mtk markers are library capability only; no top-level process consumer; CMDQ no exact ELF ioctl caller
- Gate: Policy allow/node metadata do not establish effective ordinary-app access or domain path
- Identity/user scope: Policy allow/node metadata do not establish effective ordinary-app access or domain path
- Sink: Potential DMA/display/memory-resource effect remains source/artifact-only; no package/HOME/root effect
- Effect: Existing source rows cover CMDQ ioctl and ION alloc/custom ioctl capability; this row records no new sink
- Confidence/status: **DEDUP_ARTIFACT_CALLER_GAP; phase6so/6wi/6xg** / `DEDUP_ARTIFACT_CALLER_GAP; phase6so/6wi/6xg`
- Scope: previous public Phase 9 corpus

## R01
- Phase/surface: `6X3` / `User0 HOME`
- Source: `work/luna_worker_phase6ac_accessibility_review_20260810.csv; findings/phase-6cy-accessibility-reboot-unlock-result.md`
- Evidence: `work/luna_worker_phase6ac_accessibility_review_20260810.csv; findings/phase-6cy-accessibility-reboot-unlock-result.md`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: User 0; Fire Launcher
- Gate: 已整合/已排除 as replacement; Resolver selection is not a writer; do not infer bypass
- Identity/user scope: User 0; Fire Launcher
- Sink: MAIN+HOME resolver
- Effect: Fire selected before/after; no third-party success rate claimed
- Confidence/status: **已整合/已排除 as replacement** / `已整合/已排除 as replacement`
- Scope: previous public Phase 9 corpus

## R02
- Phase/surface: `6X3` / `User0 HOME`
- Source: `priority replay`
- Evidence: `priority replay`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: User 0; ordinary caller
- Gate: 已排除; No setter
- Identity/user scope: User 0; ordinary caller
- Sink: preferred/set-home/priority
- Effect: historical mutation reached API, but no durable third-party HOME; exact rate not reported
- Confidence/status: **已排除** / `已排除`
- Scope: previous public Phase 9 corpus

## R03
- Phase/surface: `6X3` / `package-state`
- Source: `work/luna_worker_phase6qe_existing_tests_20260810.csv; adb/phase6fa/; adb/phase6bl/`
- Evidence: `work/luna_worker_phase6qe_existing_tests_20260810.csv; adb/phase6fa/; adb/phase6bl/`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: User 0; shell/ordinary caller
- Gate: 已排除; Protected-package rejection is not a privilege transition
- Identity/user scope: User 0; shell/ordinary caller
- Sink: Fire protected package and force-stop
- Effect: component enable and force-stop rejected before mutation; no success
- Confidence/status: **已排除** / `已排除`
- Scope: previous public Phase 9 corpus

## R04
- Phase/surface: `6X3` / `package-state`
- Source: `work/luna_worker_phase6qe_existing_tests_20260810.csv; work/luna_worker_phase6ty_user0_fire_restoration_20260810.csv`
- Evidence: `work/luna_worker_phase6qe_existing_tests_20260810.csv; work/luna_worker_phase6ty_user0_fire_restoration_20260810.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: User 0 versus child profile
- Gate: 已整合/已排除 as User0 route; No component-state replay or grant/revoke
- Identity/user scope: User 0 versus child profile
- Sink: Tahoe enable/component state
- Effect: Tahoe package enable alone did not expose child HOME; shell component enable rejected; child-scoped writer exists
- Confidence/status: **已整合/已排除 as User0 route** / `已整合/已排除 as User0 route`
- Scope: previous public Phase 9 corpus

## R05
- Phase/surface: `6X3` / `User10 child/KFT`
- Source: `work/luna_worker_phase6ri_existing_results_20260810.csv; findings/phase-6er-kft-child-switch-attribution.md`
- Evidence: `work/luna_worker_phase6ri_existing_results_20260810.csv; findings/phase-6er-kft-child-switch-attribution.md`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: User 10/11 child/profile; UserInfo.id
- Gate: 已整合/已排除 as User0; Private tx3 and user lifecycle are out of scope
- Identity/user scope: User 10/11 child/profile; UserInfo.id
- Sink: KFT launcher writer
- Effect: child HOME observed in existing lifecycle; no User0 success rate
- Confidence/status: **已整合/已排除 as User0** / `已整合/已排除 as User0`
- Scope: previous public Phase 9 corpus

## R06
- Phase/surface: `6X3` / `DPM/Profile Owner`
- Source: `work/luna_worker_phase6qe_existing_tests_20260810.csv; findings/phase-6di-kft-dpm-backup-passive.md`
- Evidence: `work/luna_worker_phase6qe_existing_tests_20260810.csv; findings/phase-6di-kft-dpm-backup-passive.md`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: owner/admin/profile scope; not ordinary app
- Gate: 已排除 as ordinary route/待驗證 caller provenance; No provisioning/removal or Binder transaction
- Identity/user scope: owner/admin/profile scope; not ordinary app
- Sink: DPM tx100 -> PMS tx73
- Effect: owner/admin gate observed; no active writer result
- Confidence/status: **已排除 as ordinary route/待驗證 caller provenance** / `已排除 as ordinary route/待驗證 caller provenance`
- Scope: previous public Phase 9 corpus

## R07
- Phase/surface: `6X3` / `HOME resources`
- Source: `work/luna_worker_phase6vd_test_reconciliation_20260810.csv; findings/phase-6rs-ru-report.md`
- Evidence: `work/luna_worker_phase6vd_test_reconciliation_20260810.csv; findings/phase-6rs-ru-report.md`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: build resource and overlay; runtime user not shown
- Gate: 已排除 as proof of HOME/待驗證 static join; No settings mutation or UI dispatch
- Identity/user scope: build resource and overlay; runtime user not shown
- Sink: default-home resource/overlay/UI
- Effect: resource/UI evidence only; runtime selection not measured
- Confidence/status: **已排除 as proof of HOME/待驗證 static join** / `已排除 as proof of HOME/待驗證 static join`
- Scope: previous public Phase 9 corpus

## R08
- Phase/surface: `6X3` / `SystemUI/navigation`
- Source: `work/luna_worker_phase6x_ipc_20260810.csv; output/tables/phase6x2-control-surface.csv`
- Evidence: `work/luna_worker_phase6x_ipc_20260810.csv; output/tables/phase6x2-control-surface.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: verified Binder UID/package; privileged gate
- Gate: 待驗證 host-only caller/transaction join; CONTROL_KEYGUARD gate and private SystemUI boundary; no guessed transaction
- Identity/user scope: verified Binder UID/package; privileged gate
- Sink: keyguard PendingIntent/SystemUI handoff
- Effect: static capability only; no runtime success
- Confidence/status: **待驗證 host-only caller/transaction join** / `待驗證 host-only caller/transaction join`
- Scope: previous public Phase 9 corpus

## R09
- Phase/surface: `6X3` / `SystemUI/navigation`
- Source: `work/luna_worker_phase6vd_test_reconciliation_20260810.csv; work/luna_worker_phase6xg_driver_20260810.csv`
- Evidence: `work/luna_worker_phase6vd_test_reconciliation_20260810.csv; work/luna_worker_phase6xg_driver_20260810.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: kernel input graph; shipped caller unknown
- Gate: 已排除 as formal HOME/待驗證 shipped caller; No input injection or node access
- Identity/user scope: kernel input graph; shipped caller unknown
- Sink: input/uinput/navigation event path
- Effect: 0/30 direct Accessibility redirect; uinput source capability only
- Confidence/status: **已排除 as formal HOME/待驗證 shipped caller** / `已排除 as formal HOME/待驗證 shipped caller`
- Scope: previous public Phase 9 corpus

## R10
- Phase/surface: `6X3` / `Accessibility`
- Source: `work/luna_worker_phase6qe_existing_tests_20260810.csv; work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- Evidence: `work/luna_worker_phase6qe_existing_tests_20260810.csv; work/luna_worker_phase6ac_accessibility_review_20260810.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: User 0; user consent/service state
- Gate: 已排除 as deterministic route/待驗證 consent; Do not enable Accessibility or install/update APK
- Identity/user scope: User 0; user consent/service state
- Sink: installed service binding
- Effect: service bound but callback empty; 0/30 direct route; GUI consent run not measured
- Confidence/status: **已排除 as deterministic route/待驗證 consent** / `已排除 as deterministic route/待驗證 consent`
- Scope: previous public Phase 9 corpus

## R11
- Phase/surface: `6X3` / `Accessibility`
- Source: `work/luna_worker_phase6ac_accessibility_review_20260810.md; findings/phase-6cy-ms-targeted-accessibility-retry.md`
- Evidence: `work/luna_worker_phase6ac_accessibility_review_20260810.md; findings/phase-6cy-ms-targeted-accessibility-retry.md`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: User 0; target foreground only
- Gate: 已整合 as limited alternative; Fire remains resolver winner; no unlock bypass
- Identity/user scope: User 0; target foreground only
- Sink: consented delayed foreground redirect
- Effect: retry variants: explicit 1/1, HOME 3/3 in cited run; reboot/unlock mixed 2/3 or 3/3; not deterministic
- Confidence/status: **已整合 as limited alternative** / `已整合 as limited alternative`
- Scope: previous public Phase 9 corpus

## R12
- Phase/surface: `6X3` / `Accessibility`
- Source: `work/luna_worker_phase6ac_accessibility_review_20260810.csv; findings/phase-6cy-accessibility-timeout-ab-boundary.md`
- Evidence: `work/luna_worker_phase6ac_accessibility_review_20260810.csv; findings/phase-6cy-accessibility-timeout-ab-boundary.md`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: User 0; foreground redirect
- Gate: 已排除/不採用; No timing optimization replay
- Identity/user scope: User 0; foreground redirect
- Sink: timeout A/B variant
- Effect: 50 ms variant 4/5 in cited observation; HOME reliability worse; not adopted
- Confidence/status: **已排除/不採用** / `已排除/不採用`
- Scope: previous public Phase 9 corpus

## R13
- Phase/surface: `6X3` / `UsageStats`
- Source: `work/luna_worker_phase6ac_accessibility_review_20260810.md; adb/phase6ac/; adb/phase6ao/`
- Evidence: `work/luna_worker_phase6ac_accessibility_review_20260810.md; adb/phase6ac/; adb/phase6ao/`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: ordinary app; PACKAGE_USAGE_STATS/app-op boundary
- Gate: 待驗證 host-only permission/consumer join; Do not add permission or use it as HOME writer
- Identity/user scope: ordinary app; PACKAGE_USAGE_STATS/app-op boundary
- Sink: third-party foreground observation
- Effect: 未驗證; no success rate
- Confidence/status: **待驗證 host-only permission/consumer join** / `待驗證 host-only permission/consumer join`
- Scope: previous public Phase 9 corpus

## R14
- Phase/surface: `6X3` / `ADB monitor`
- Source: `findings/phase-6iq-adb-foreground-fallback.md; work/luna_worker_phase6vd_test_reconciliation_20260810.csv`
- Evidence: `findings/phase-6iq-adb-foreground-fallback.md; work/luna_worker_phase6vd_test_reconciliation_20260810.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: ADB-connected host; not resident device route
- Gate: 已排除 as approved resident solution; No new ADB monitor or device contact
- Identity/user scope: ADB-connected host; not resident device route
- Sink: host ADB foreground relay
- Effect: 5/5 foreground relay in cited evidence; stops with ADB/monitor
- Confidence/status: **已排除 as approved resident solution** / `已排除 as approved resident solution`
- Scope: previous public Phase 9 corpus

## R15
- Phase/surface: `6X3` / `OOBE/OTA`
- Source: `OTA replay`
- Evidence: `OTA replay`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: system-server OTA lifecycle; numeric user unknown
- Gate: 已整合/待驗證 natural official OTA only; No broadcast injection
- Identity/user scope: system-server OTA lifecycle; numeric user unknown
- Sink: BootAfterSystemOTAReceiver -> OOBE activation
- Effect: static guarded path; no manual delivery/runtime success
- Confidence/status: **已整合/待驗證 natural official OTA only** / `已整合/待驗證 natural official OTA only`
- Scope: previous public Phase 9 corpus

## R16
- Phase/surface: `6X3` / `OOBE/OTA`
- Source: `work/luna_worker_phase6z_components_20260810.csv; artifacts/phase6bk/protected-broadcast-expanded-20260810-01/`
- Evidence: `work/luna_worker_phase6z_components_20260810.csv; artifacts/phase6bk/protected-broadcast-expanded-20260810-01/`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: child/profile lifecycle; producer and user handle incomplete
- Gate: 待驗證 host-only provenance; No lifecycle broadcast or profile mutation
- Identity/user scope: child/profile lifecycle; producer and user handle incomplete
- Sink: DCPMS lifecycle receiver -> profile policy
- Effect: host-only static chain; no runtime success
- Confidence/status: **待驗證 host-only provenance** / `待驗證 host-only provenance`
- Scope: previous public Phase 9 corpus

## R17
- Phase/surface: `6X3` / `OTA`
- Source: `recovery`
- Evidence: `recovery`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: PS7331 OTA artifact; controller/privileged path
- Gate: 已整合 static boundary/待驗證 verifier implementation; No sideload
- Identity/user scope: PS7331 OTA artifact; controller/privileged path
- Sink: metadata/signature/recovery verification
- Effect: static checks confirmed; no install success
- Confidence/status: **已整合 static boundary/待驗證 verifier implementation** / `已整合 static boundary/待驗證 verifier implementation`
- Scope: previous public Phase 9 corpus

## R18
- Phase/surface: `6X3` / `OTA`
- Source: `work/luna_worker_phase6ab_ota_exact_20260810.csv; findings/phase-6mm-updater-blockimage-closure.md`
- Evidence: `work/luna_worker_phase6ab_ota_exact_20260810.csv; findings/phase-6mm-updater-blockimage-closure.md`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: PS7331 recovery/updater; caller unknown
- Gate: 已排除 as ordinary route/因風險拒絕 runtime; No updater/recovery/partition execution; no bypass inference
- Identity/user scope: PS7331 recovery/updater; caller unknown
- Sink: native updater/block-image/partition writer
- Effect: writer capability confirmed statically; execution/partition effect 0 observed
- Confidence/status: **已排除 as ordinary route/因風險拒絕 runtime** / `已排除 as ordinary route/因風險拒絕 runtime`
- Scope: previous public Phase 9 corpus

## R19
- Phase/surface: `6X3` / `app/IPC`
- Source: `work/luna_worker_phase6qf_existing_runtime_audit_20260810.csv; findings/phase-6q-evidence-index.md`
- Evidence: `work/luna_worker_phase6qf_existing_runtime_audit_20260810.csv; findings/phase-6q-evidence-index.md`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: shell UID 2000; private service gate
- Gate: 已排除 method reachability; No unknown Binder transaction or handle guessing
- Identity/user scope: shell UID 2000; private service gate
- Sink: private Amazon service visibility/lookup
- Effect: names visible; private check/find denied/not found; no method success
- Confidence/status: **已排除 method reachability** / `已排除 method reachability`
- Scope: previous public Phase 9 corpus

## R20
- Phase/surface: `6X3` / `app/IPC`
- Source: `work/luna_worker_phase6vd_test_reconciliation_20260810.csv; work/luna_worker_phase6tm_h2_permission_20260810.csv`
- Evidence: `work/luna_worker_phase6vd_test_reconciliation_20260810.csv; work/luna_worker_phase6tm_h2_permission_20260810.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: external requester/holder/grant unknown
- Gate: 待驗證 host-only holder/requester join; No bind/call or guessed code
- Identity/user scope: external requester/holder/grant unknown
- Sink: H2 BIND_SERVICE custom permission
- Effect: signature gate confirmed; caller/sink unknown; no runtime call
- Confidence/status: **待驗證 host-only holder/requester join** / `待驗證 host-only holder/requester join`
- Scope: previous public Phase 9 corpus

## R21
- Phase/surface: `6X3` / `app/IPC`
- Source: `output/tables/phase6x2-control-surface.csv; work/luna_worker_phase6z_components_20260810.csv`
- Evidence: `output/tables/phase6x2-control-surface.csv; work/luna_worker_phase6z_components_20260810.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: producer and user scope unknown
- Gate: 待驗證 host-only caller/permission/user join; No broadcast replay or cross-user mutation
- Identity/user scope: producer and user scope unknown
- Sink: exported OOBE/account/profile receivers
- Effect: exported/static policy evidence only; target HOME/PMS sink not closed
- Confidence/status: **待驗證 host-only caller/permission/user join** / `待驗證 host-only caller/permission/user join`
- Scope: previous public Phase 9 corpus

## R22
- Phase/surface: `6X3` / `app/IPC`
- Source: `work/luna_worker_phase6vd_test_reconciliation_20260810.csv; findings/phase-6a-untrusted-app-pi-smoke-evidence-index.md`
- Evidence: `work/luna_worker_phase6vd_test_reconciliation_20260810.csv; findings/phase-6a-untrusted-app-pi-smoke-evidence-index.md`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: ordinary/untrusted app
- Gate: 已排除 bounded route; Private Binder out of scope; no APK/install
- Identity/user scope: ordinary/untrusted app
- Sink: untrusted PendingIntent/cross-user
- Effect: bounded smoke did not establish durable mutation; exact rate not claimed
- Confidence/status: **已排除 bounded route** / `已排除 bounded route`
- Scope: previous public Phase 9 corpus

## R23
- Phase/surface: `6X3` / `settings`
- Source: `work/luna_worker_phase6wk_broad_surface_20260810.csv; work/luna_worker_phase6aa_ipc_residual_20260810.csv`
- Evidence: `work/luna_worker_phase6wk_broad_surface_20260810.csv; work/luna_worker_phase6aa_ipc_residual_20260810.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: system/shell permission gates; user overload varies
- Gate: 已整合/待驗證 caller provenance; No settings write or settings modification
- Identity/user scope: system/shell permission gates; user overload varies
- Sink: SettingsProvider and generic settings writers
- Effect: static sink capability; no target HOME/package result
- Confidence/status: **已整合/待驗證 caller provenance** / `已整合/待驗證 caller provenance`
- Scope: previous public Phase 9 corpus

## R24
- Phase/surface: `6X3` / `app/IPC`
- Source: `work/luna_worker_phase6qe_existing_tests_20260810.csv; work/luna_worker_phase6ty_user0_fire_restoration_20260810.csv`
- Evidence: `work/luna_worker_phase6qe_existing_tests_20260810.csv; work/luna_worker_phase6ty_user0_fire_restoration_20260810.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: privileged/system or unknown production caller
- Gate: 待驗證 host-only provenance/已排除 replay; No grant/revoke/install/package mutation
- Identity/user scope: privileged/system or unknown production caller
- Sink: Amazon PM/Vending/package-state writers
- Effect: static writers and bounded negative caller closure; no ordinary User0 success
- Confidence/status: **待驗證 host-only provenance/已排除 replay** / `待驗證 host-only provenance/已排除 replay`
- Scope: previous public Phase 9 corpus

## R25
- Phase/surface: `6X3` / `kernel/root`
- Source: `ioctl`
- Evidence: `ioctl`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: retail node/caller/domain not joined
- Gate: 待驗證 host-only image/DT/relocation join; No node access
- Identity/user scope: retail node/caller/domain not joined
- Sink: driver CMDQ/ION/MDP nodes
- Effect: source/policy capability only; no node open/ioctl/effect
- Confidence/status: **待驗證 host-only image/DT/relocation join** / `待驗證 host-only image/DT/relocation join`
- Scope: previous public Phase 9 corpus

## R26
- Phase/surface: `6X3` / `kernel/root`
- Source: `node write`
- Evidence: `node write`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: shipped native caller unknown
- Gate: 已排除 as proven bypass/待驗證 caller only; No synthetic input
- Identity/user scope: shipped native caller unknown
- Sink: uinput/power-supply low-level path
- Effect: source capability only; no retail privilege transition
- Confidence/status: **已排除 as proven bypass/待驗證 caller only** / `已排除 as proven bypass/待驗證 caller only`
- Scope: previous public Phase 9 corpus

## R27
- Phase/surface: `6X3` / `kernel/root`
- Source: `work/luna_worker_phase6vd_test_reconciliation_20260810.csv; findings/phase-5-evidence-index.md`
- Evidence: `work/luna_worker_phase6vd_test_reconciliation_20260810.csv; findings/phase-5-evidence-index.md`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: device/root boundary
- Gate: 因風險拒絕; Exploit/root/payload execution explicitly excluded
- Identity/user scope: device/root boundary
- Sink: root/futex/rtmutex/privilege transition
- Effect: no approved device mutation; no success rate
- Confidence/status: **因風險拒絕** / `因風險拒絕`
- Scope: previous public Phase 9 corpus

## R28
- Phase/surface: `6X3` / `architecture`
- Source: `work/luna_worker_phase6ad_untested_routes_20260810.md; work/luna_worker_phase6ty_user0_fire_restoration_20260810.csv`
- Evidence: `work/luna_worker_phase6ad_untested_routes_20260810.md; work/luna_worker_phase6ty_user0_fire_restoration_20260810.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: system/in-process policy path; caller gate unknown
- Gate: 待驗證 host-only registration/permission join; No service call or policy mutation
- Identity/user scope: system/in-process policy path; caller gate unknown
- Sink: ProductPolicy/fosinit Binder publication
- Effect: static registration/sink markers; no callable transaction or HOME result
- Confidence/status: **待驗證 host-only registration/permission join** / `待驗證 host-only registration/permission join`
- Scope: previous public Phase 9 corpus

## R29
- Phase/surface: `6X3` / `architecture`
- Source: `work/luna_worker_phase6ad_untested_routes_20260810.md; work/luna_worker_prewarm_identity_closure_20260810.csv`
- Evidence: `work/luna_worker_phase6ad_untested_routes_20260810.md; work/luna_worker_prewarm_identity_closure_20260810.csv`
- SHA-256: `21e086aebb37a69c99b2450fb95c9b1dd57102c3940579e42c80f53100af5a3b`
- Caller: Amazon/system caller; user propagation incomplete
- Gate: 待驗證 host-only identity/user-flow join; No process launch or Binder invocation
- Identity/user scope: Amazon/system caller; user propagation incomplete
- Sink: ASP preWarmApplicationForUser
- Effect: static process/state sink candidate; no HOME/package success
- Confidence/status: **待驗證 host-only identity/user-flow join** / `待驗證 host-only identity/user-flow join`
- Scope: previous public Phase 9 corpus

## 6X4-PRODUCTPOLICY-001
- Phase/surface: `6X4` / `ProductPolicy/DCPMS closure`
- Source: `PCAActiveProfileReceiver.java:23-27; UpdatePCAProfileTypeAndEvalHelper.java:37-57; Evaluator.java:90-105`
- Evidence: `PCAActiveProfileReceiver.java:23-27; UpdatePCAProfileTypeAndEvalHelper.java:37-57; Evaluator.java:90-105`
- SHA-256: `APK:15ca17549bc377360d9213eb95b5e0468d1352839386e1d968bcb25282218997`
- Caller: PCAActiveProfileReceiver->helper->Evaluator
- Gate: exported action; no receiver permission
- Identity/user scope: no inbound Binder; DCPMS process; device PCA/profile; device-protected CDE
- Sink: CDE prefs/evaluator/notification; no PMS/HOME/settings/OTA
- Effect: CLOSED_NO_PLATFORM_SINK
- Confidence/status: **CLOSED_NO_PLATFORM_SINK** / `CLOSED_NO_PLATFORM_SINK`
- Scope: previous public Phase 9 corpus

## 6X4-PRODUCTPOLICY-002
- Phase/surface: `6X4` / `ProductPolicy/DCPMS closure`
- Source: `DeviceUserSwitchReceiver.java:47-57; UpdateOSUserTypeService.java:19-35; Helper.java:25-47`
- Evidence: `DeviceUserSwitchReceiver.java:47-57; UpdateOSUserTypeService.java:19-35; Helper.java:25-47`
- SHA-256: `manifest:9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`
- Caller: DeviceUserSwitchReceiver->UpdateOSUserTypeService
- Gate: protected USER_SWITCHED; exported singleUser
- Identity/user scope: no inbound Binder; DCPMS process; computed OS-user/PCA; child active-app clear
- Sink: CDE only
- Effect: CLOSED_NO_PLATFORM_SINK
- Confidence/status: **CLOSED_NO_PLATFORM_SINK** / `CLOSED_NO_PLATFORM_SINK`
- Scope: previous public Phase 9 corpus

## 6X4-PRODUCTPOLICY-003
- Phase/surface: `6X4` / `ProductPolicy/DCPMS closure`
- Source: `AccountPropertyChangeReceiver.java:31-39; manifest:94-103; protected inventory row 562`
- Evidence: `AccountPropertyChangeReceiver.java:31-39; manifest:94-103; protected inventory row 562`
- SHA-256: `APK:15ca17549bc377360d9213eb95b5e0468d1352839386e1d968bcb25282218997`
- Caller: AccountPropertyChangeReceiver->OS-user helper
- Gate: exported + account-property permission; protected action
- Identity/user scope: no inbound Binder; DCPMS process; computed OS-user/PCA; singleUser
- Sink: CDE only
- Effect: CLOSED_NO_PLATFORM_SINK
- Confidence/status: **CLOSED_NO_PLATFORM_SINK** / `CLOSED_NO_PLATFORM_SINK`
- Scope: previous public Phase 9 corpus

## 6X4-PRODUCTPOLICY-004
- Phase/surface: `6X4` / `ProductPolicy/DCPMS closure`
- Source: `GlobalContentSyncEventReceiver.java:16-25; GlobalContentSyncEventService.java:23-37; manifest:145-207`
- Evidence: `GlobalContentSyncEventReceiver.java:16-25; GlobalContentSyncEventService.java:23-37; manifest:145-207`
- SHA-256: `manifest:9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`
- Caller: GlobalContentSyncEventReceiver->Service->ArcusSyncService
- Gate: GLOBAL_SYNC permission; BIND_JOB_SERVICE
- Identity/user scope: no inbound Binder; DCPMS process; device CDE remote policy; no user arg
- Sink: CDE sync only
- Effect: CLOSED_NO_PLATFORM_SINK
- Confidence/status: **CLOSED_NO_PLATFORM_SINK** / `CLOSED_NO_PLATFORM_SINK`
- Scope: previous public Phase 9 corpus

## 6X4-PRODUCTPOLICY-005
- Phase/surface: `6X4` / `ProductPolicy/DCPMS closure`
- Source: `fosinit; onStart 0x045b36-0x045b44; OnUserSwitchEvent 0x06245c-0x0624d2; Action 0x052642; reset 0x045ba4-0x045bde`
- Evidence: `fosinit; onStart 0x045b36-0x045b44; OnUserSwitchEvent 0x06245c-0x0624d2; Action 0x052642; reset 0x045ba4-0x045bde`
- SHA-256: `fosinit:9d1ef392f345feb36c2f72357cf4777d5135b705ce6b360864993c14449e8bd4;VDEX:ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: ProductPolicy fosinit->onStart
- Gate: system-server loader; no exported component
- Identity/user scope: local SystemService; no Binder identity/clearCallingIdentity; UserInfo.id; foreground profile; all users
- Sink: AmazonPackageManager component/application setters; boot FACTORY_RESET
- Effect: CLOSED_AS_TRUSTED_LOCAL_PATH_NO_EXTERNAL_BINDER
- Confidence/status: **CLOSED_AS_TRUSTED_LOCAL_PATH_NO_EXTERNAL_BINDER** / `CLOSED_AS_TRUSTED_LOCAL_PATH_NO_EXTERNAL_BINDER`
- Scope: previous public Phase 9 corpus

## 6X4-PRODUCTPOLICY-006
- Phase/surface: `6X4` / `ProductPolicy/DCPMS closure`
- Source: `fosdebug-service-inventory.txt:22; service-context-matrix.csv; dcpms.xml`
- Evidence: `fosdebug-service-inventory.txt:22; service-context-matrix.csv; dcpms.xml`
- SHA-256: `dcpms:f17054ab1cd901db06ce39f10595ab36a062f82718b9fcf5490003161ef8f5b0`
- Caller: ProductPolicy publication metadata
- Gate: not applicable: no remote component/AIDL
- Identity/user scope: not applicable: local object; internal policy events
- Sink: no external service-manager name/SELinux Binder rule
- Effect: CLOSED_NEGATIVE_EXTERNAL_BINDER
- Confidence/status: **CLOSED_NEGATIVE_EXTERNAL_BINDER** / `CLOSED_NEGATIVE_EXTERNAL_BINDER`
- Scope: previous public Phase 9 corpus

## 6X4-PRODUCTPOLICY-007
- Phase/surface: `6X4` / `ProductPolicy/DCPMS closure`
- Source: `IDeviceChildExperienceModeDecisionManager.java:14-18,32-75,98-135; ServiceBinder.java:63-109; DCPMSService.java:124-135`
- Evidence: `IDeviceChildExperienceModeDecisionManager.java:14-18,32-75,98-135; ServiceBinder.java:63-109; DCPMSService.java:124-135`
- SHA-256: `manifest:9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`
- Caller: DCPMS AIDL Stub/Proxy
- Gate: GET_DEVICE_CDE_DECISION signature|amazon
- Identity/user scope: Stub no calling UID/user check; process identity; singleUser; no user arg
- Sink: decision read/register/unregister callback only
- Effect: CLOSED_BOUNDED_IDENTITY_NO_SENSITIVE_SINK
- Confidence/status: **CLOSED_BOUNDED_IDENTITY_NO_SENSITIVE_SINK** / `CLOSED_BOUNDED_IDENTITY_NO_SENSITIVE_SINK`
- Scope: previous public Phase 9 corpus

## 6X4-USERSCOPE-001
- Phase/surface: `6X4` / `OOBE/prewarm user-scope closure`
- Source: `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java:27-61; decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96107-96126`
- Evidence: `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java:27-61; decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96107-96126`
- SHA-256: `07c7875f3760a4ec9e73ed668e7423f80d2f8535d6d21d5c9c4498423eab4bee`
- Caller: AmazonPackageManagerService.onBootPhase(550) -> BootAfterSystemOTAReceiver.onReceive
- Gate: "protected RECEIVE_BOOT_AFTER_SYSTEM_OTA lifecycle provenance; exact ordinary sender UNKNOWN"
- Identity/user scope: "trusted system-server OTA lifecycle; ordinary Binder caller UNKNOWN"; "clearCallingIdentity/restoreCallingIdentity not present in bounded receiver path; UNKNOWN/NOT APPLICABLE"; "receiver Context -> PackageManager; numeric UserHandle not recovered"; User0=UNKNOWN; User10=UNKNOWN; profile=UNKNOWN
- Sink: PackageHelper.enableComponent(OobeHomeActivity); then OOBEActivationHelper.activateOOBEIF
- Effect: STATIC_LIFECYCLE_SINK_CALLER_AND_USER_UNKNOWN
- Confidence/status: **STATIC_LIFECYCLE_SINK_CALLER_AND_USER_UNKNOWN** / `STATIC_LIFECYCLE_SINK_CALLER_AND_USER_UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6X4-USERSCOPE-002
- Phase/surface: `6X4` / `OOBE/prewarm user-scope closure`
- Source: `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java:29-34,53-56`
- Evidence: `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java:29-34,53-56`
- SHA-256: `07c7875f3760a4ec9e73ed668e7423f80d2f8535d6d21d5c9c4498423eab4bee`
- Caller: BootAfterSystemOTAReceiver guarded branch -> OOBEActivationHelper
- Gate: "same protected OTA lifecycle guard; ordinary caller UNKNOWN"
- Identity/user scope: "identity inherited from receiver Context; no ordinary Binder caller established"; "no clearCallingIdentity/restoreCallingIdentity in bounded helper path; UNKNOWN"; "receiver Context.getContentResolver() -> SettingsDBUtils; numeric Settings user not recovered"; User0=UNKNOWN; User10=UNKNOWN; profile=UNKNOWN
- Sink: Settings.Secure user_setup_complete=0 and isOOBEActive=1 via setSettingSecurePutIntFG
- Effect: STATIC_SETTINGS_SINK_USER_UNKNOWN
- Confidence/status: **STATIC_SETTINGS_SINK_USER_UNKNOWN** / `STATIC_SETTINGS_SINK_USER_UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6X4-USERSCOPE-003
- Phase/surface: `6X4` / `OOBE/prewarm user-scope closure`
- Source: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40534; decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:394721-394739; findings/phase-6x3-evidence-index.md:1577-1590`
- Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40534; decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:394721-394739; findings/phase-6x3-evidence-index.md:1577-1590`
- SHA-256: `07c7875f3760a4ec9e73ed668e7423f80d2f8535d6d21d5c9c4498423eab4bee`
- Caller: AmazonActivityManagerImpl -> IAmazonActivityManager.preWarmApplicationForUser -> BinderService
- Gate: checkCallingPermission(com.amazon.permission.APP_PREWARM); bounded slice does not show result consumption
- Identity/user scope: Binder caller identity checked before clear; caller UID handling beyond slice UNKNOWN; clearCallingIdentity after permission check; restoreCallingIdentity on normal return path; exceptional cleanup/caller UID conversion UNKNOWN; explicit int user -> IPackageManager.getApplicationInfo(target,1024,user); AM service then startProcessLocked; User0=UNKNOWN; User10=UNKNOWN; profile=UNKNOWN
- Sink: PreWarmCacheHelper -> ActivityManagerService.startProcessLocked(...,reason=prewarm,...); process/cache sink only
- Effect: STATIC_AUTHORIZATION_ANOMALY_CANDIDATE_CALLER_USER_UNKNOWN
- Confidence/status: **STATIC_AUTHORIZATION_ANOMALY_CANDIDATE_CALLER_USER_UNKNOWN** / `STATIC_AUTHORIZATION_ANOMALY_CANDIDATE_CALLER_USER_UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6X4-PERMISSION-001
- Phase/surface: `6X4` / `permission consumer/holder closure`
- Source: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- Evidence: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- SHA-256: `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`
- Caller: android.amazon.perm (declaration owner only); declaration
- Gate: UNKNOWN; no bounded requester manifest; android.amazon.perm package owner; effective grant UNKNOWN; NOT_FOUND in bounded JADX/VDEX; no checkCallingPermission/checkCallingUid joined
- Identity/user scope: UNKNOWN; no Binder consumer joined; UNKNOWN
- Sink: NOT_FOUND; no downstream sensitive sink
- Effect: Declaration has raw protectionLevel=0x0 (normal); declaration alone is not requester or reachability proof
- Confidence/status: **UNKNOWN_NOT_CLOSED** / `UNKNOWN_NOT_CLOSED`
- Scope: previous public Phase 9 corpus

## 6X4-PERMISSION-002
- Phase/surface: `6X4` / `permission consumer/holder closure`
- Source: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- Evidence: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- SHA-256: `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`
- Caller: android.amazon.perm (declaration owner only); declaration
- Gate: UNKNOWN; no bounded requester manifest; android.amazon.perm package owner; effective grant UNKNOWN; NOT_FOUND in bounded JADX/VDEX; no checkCallingPermission/checkCallingUid joined
- Identity/user scope: UNKNOWN; no Binder consumer joined; UNKNOWN
- Sink: NOT_FOUND; no downstream sensitive sink
- Effect: Declaration has raw protectionLevel=0x0 (normal); declaration alone is not requester or reachability proof
- Confidence/status: **UNKNOWN_NOT_CLOSED** / `UNKNOWN_NOT_CLOSED`
- Scope: previous public Phase 9 corpus

## 6X4-PERMISSION-003
- Phase/surface: `6X4` / `permission consumer/holder closure`
- Source: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- Evidence: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- SHA-256: `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`
- Caller: android.amazon.perm (declaration owner only); declaration
- Gate: UNKNOWN; no bounded requester manifest; android.amazon.perm package owner; effective grant UNKNOWN; NOT_FOUND in bounded JADX/VDEX; no checkCallingPermission/checkCallingUid joined
- Identity/user scope: UNKNOWN; no Binder consumer joined; UNKNOWN
- Sink: NOT_FOUND; no downstream sensitive sink
- Effect: Declaration has raw protectionLevel=0x1 (dangerous); low/non-signature protection does not prove an accepted caller
- Confidence/status: **UNKNOWN_NOT_CLOSED** / `UNKNOWN_NOT_CLOSED`
- Scope: previous public Phase 9 corpus

## 6X4-PERMISSION-004
- Phase/surface: `6X4` / `permission consumer/holder closure`
- Source: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- Evidence: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`
- SHA-256: `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`
- Caller: android.amazon.perm (declaration owner only); declaration
- Gate: UNKNOWN; no bounded requester manifest; android.amazon.perm package owner; effective grant UNKNOWN; NOT_FOUND in bounded JADX/VDEX; no checkCallingPermission/checkCallingUid joined
- Identity/user scope: UNKNOWN; no Binder consumer joined; UNKNOWN
- Sink: NOT_FOUND; no downstream sensitive sink
- Effect: No protectionLevel attribute is present in bounded declaration; protection remains UNKNOWN
- Confidence/status: **UNKNOWN_NOT_CLOSED** / `UNKNOWN_NOT_CLOSED`
- Scope: previous public Phase 9 corpus

## 6X4-PERMISSION-005
- Phase/surface: `6X4` / `permission consumer/holder closure`
- Source: `artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/H2ClientService.java`
- Evidence: `artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/H2ClientService.java`
- SHA-256: `f30c3b42ce45c1e7ef717b2deb5b0402dbc01fc70cb5a86480d8b4a54e7fa9e5`
- Caller: UNKNOWN; bounded-consumer-scan
- Gate: NOT_FOUND in exact-build manifest corpus outside owner declaration; UNKNOWN; no saved grant/holder row joined; negative bounded scan; no method-local check found
- Identity/user scope: UNKNOWN; no Binder identity use joined; UNKNOWN
- Sink: negative bounded scan; no sensitive sink edge
- Effect: Bounded source corpus contains H2 AIDL implementation but no USE_SDK requester/consumer; negative is corpus-scoped
- Confidence/status: **BOUNDED_NEGATIVE_NOT_GLOBAL** / `BOUNDED_NEGATIVE_NOT_GLOBAL`
- Scope: previous public Phase 9 corpus

## 6X4-PERMISSION-006
- Phase/surface: `6X4` / `permission consumer/holder closure`
- Source: `artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/H2ClientService.java`
- Evidence: `artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/H2ClientService.java`
- SHA-256: `f30c3b42ce45c1e7ef717b2deb5b0402dbc01fc70cb5a86480d8b4a54e7fa9e5`
- Caller: UNKNOWN; bounded-consumer-scan
- Gate: NOT_FOUND in exact-build manifest corpus outside owner declaration; UNKNOWN; no saved grant/holder row joined; negative bounded scan; no method-local check found
- Identity/user scope: UNKNOWN; no Binder identity use joined; UNKNOWN
- Sink: negative bounded scan; no sensitive sink edge
- Effect: Bounded source corpus contains H2 AIDL implementation but no USE_SDK requester/consumer; negative is corpus-scoped
- Confidence/status: **BOUNDED_NEGATIVE_NOT_GLOBAL** / `BOUNDED_NEGATIVE_NOT_GLOBAL`
- Scope: previous public Phase 9 corpus

## 6X4-PERMISSION-007
- Phase/surface: `6X4` / `permission consumer/holder closure`
- Source: `artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/H2ClientService.java`
- Evidence: `artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/H2ClientService.java`
- SHA-256: `f30c3b42ce45c1e7ef717b2deb5b0402dbc01fc70cb5a86480d8b4a54e7fa9e5`
- Caller: UNKNOWN; bounded-consumer-scan
- Gate: NOT_FOUND in exact-build manifest corpus outside owner declaration; UNKNOWN; no saved grant/holder row joined; negative bounded scan; no method-local check found
- Identity/user scope: UNKNOWN; no Binder identity use joined; UNKNOWN
- Sink: negative bounded scan; no sensitive sink edge
- Effect: Bounded source corpus contains H2 AIDL implementation but no PLUGIN requester/consumer; negative is corpus-scoped
- Confidence/status: **BOUNDED_NEGATIVE_NOT_GLOBAL** / `BOUNDED_NEGATIVE_NOT_GLOBAL`
- Scope: previous public Phase 9 corpus

## 6X4-PERMISSION-008
- Phase/surface: `6X4` / `permission consumer/holder closure`
- Source: `artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/H2ClientService.java`
- Evidence: `artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/H2ClientService.java`
- SHA-256: `f30c3b42ce45c1e7ef717b2deb5b0402dbc01fc70cb5a86480d8b4a54e7fa9e5`
- Caller: UNKNOWN; bounded-consumer-scan
- Gate: NOT_FOUND in exact-build manifest corpus outside owner declaration; UNKNOWN; no saved grant/holder row joined; negative bounded scan; no method-local check found
- Identity/user scope: UNKNOWN; no Binder identity use joined; UNKNOWN
- Sink: negative bounded scan; no sensitive sink edge
- Effect: Bounded source corpus contains H2 AIDL implementation but no PLUGIN_CONSUMER requester/consumer; negative is corpus-scoped
- Confidence/status: **BOUNDED_NEGATIVE_NOT_GLOBAL** / `BOUNDED_NEGATIVE_NOT_GLOBAL`
- Scope: previous public Phase 9 corpus

## 6X4-PERMISSION-009
- Phase/surface: `6X4` / `permission consumer/holder closure`
- Source: `artifacts/phase6x/prewarm-authorization-20260805-05/com_amazon_permission_APP_PREWARM.block.txt`
- Evidence: `artifacts/phase6x/prewarm-authorization-20260805-05/com_amazon_permission_APP_PREWARM.block.txt`
- SHA-256: `4a71d4d60cdb6c45233e270e3548f02c9ea77e9d3b3b4ed33a7aeb1e130bb798`
- Caller: android.amazon.perm; permission-owner
- Gate: UNKNOWN; owner manifest is not a requester; sourcePackage=android.amazon.perm UID=1000; explicit custom grants to ten candidate packages in saved package record; No method-local checkCallingPermission in Stub path; AbstractAPICall logs Binder.getCallingUid only
- Identity/user scope: caller UID is logged but not authorizing identity; household/profile workflow
- Sink: AmazonUserManager create/remove user path
- Effect: Owner/protection and ten grants are positive candidates; actual bind client remains UNKNOWN
- Confidence/status: **POSITIVE_STATIC_SINK_CALLER_UNKNOWN** / `POSITIVE_STATIC_SINK_CALLER_UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6X4-PERMISSION-010
- Phase/surface: `6X4` / `permission consumer/holder closure`
- Source: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/001_com.amazon.parentalcontrols__0_com.amazon.parentalcontrols.xmltree.txt; artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/006_com.amazon.h2settingsfortablet.xmltree.txt; artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/007_com.amazon.avod.updated.xmltree.txt; artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/017_com.android.systemui__0_TabletSystemUI.xmltree.txt; artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/022_com_amazon_tahoe.xmltree.txt; artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/029_com.amazon.kindle.otter.oobe.xmltree.txt`
- Evidence: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/001_com.amazon.parentalcontrols__0_com.amazon.parentalcontrols.xmltree.txt; artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/006_com.amazon.h2settingsfortablet.xmltree.txt; artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/007_com.amazon.avod.updated.xmltree.txt; artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/017_com.android.systemui__0_TabletSystemUI.xmltree.txt; artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/022_com_amazon_tahoe.xmltree.txt; artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/029_com.amazon.kindle.otter.oobe.xmltree.txt`
- SHA-256: `5ef89e517f53d6d3696df3a43df40502f651d57f0a27d62a445ddc518930c9db; 6e1edce5feb0eb638e04d569f4df9752234ac3c5fd6f33b8169a56c30781ee0c; eeaa9811533647191563203fc020d7662f3b0efe9ac1c5ac888cbb1ccf7bcbee; 43fcaea0046afe885670a711c21d0bfff7d86cd568488f797fb8ea2b1d351c9a; 12055fed1f6cf5f012725aa044e215dcc8c8cdaa233ffac6f044c59198c36ae1; 98ffb904ff2fab10d5ac2ee6572d5c286999f9e5c7532123def0f02a2ac31a72`
- Caller: com.amazon.parentalcontrols; com.amazon.h2settingsfortablet; com.amazon.avod.updated; com.amazon.tahoe; com.amazon.kindle.otter.oobe; com.android.systemui; requester-manifest
- Gate: POSITIVE uses-permission entries at exact lines;grant/source positive for ten candidates; requester-to-grant join not proven; UNKNOWN; H2 service is exported;signature permission; No method-local permission gate recovered in H2 Stub;AbstractAPICall Binder.getCallingUid logging only; no clearCallingIdentity in H2 route
- Identity/user scope: UNKNOWN per actual client; UNKNOWN
- Sink: household/profile workflow; no HOME/package-state edge
- Effect: Exact requester evidence; no bindService callsite inferred from uses-permission
- Confidence/status: **MALFORMED_WORKER_CSV_ROW_RECONCILED** / `MALFORMED_WORKER_CSV_ROW_RECONCILED`
- Scope: previous public Phase 9 corpus

## 6X4-PERMISSION-011
- Phase/surface: `6X4` / `permission consumer/holder closure`
- Source: `artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/H2ClientService.java; artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/apicall/AbstractAPICall.java; artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/controllers/HouseholdController.java; artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/workflow/commands/CreateAndroidUserCommand.java; artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2shared/helpers/AndroidUserHelper.java`
- Evidence: `artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/H2ClientService.java; artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/apicall/AbstractAPICall.java; artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/controllers/HouseholdController.java; artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/workflow/commands/CreateAndroidUserCommand.java; artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2shared/helpers/AndroidUserHelper.java`
- SHA-256: `f30c3b42ce45c1e7ef717b2deb5b0402dbc01fc70cb5a86480d8b4a54e7fa9e5; 9d843f825ae30e06e2e6d7598f8b49f90904bdd66c88660e18ce1f03d02421da; 8ebf9b15185e298da784bb15918787fb0f37e805664ccbc780b6b5dca26ffcd2; 843d03e3aa01d59743dc8a5498975ff59f4930b35f6690ad3c7f5aa44fb594e2; 31de59672ee1be20760377643c25f9f673c3c7ce336537a40eca24acca489566`
- Caller: UNKNOWN; service-implementation
- Gate: NOT_APPLICABLE; owner/grants remain as row 6AK-009; Stub dispatches AIDL methods to APICall classes
- Identity/user scope: AbstractAPICall logs Binder.getCallingUid; no method-local authorization found in recovered H2 implementation; caller identity observed only as log; no accepted UID set recovered
- Sink: household/profile workflow; addUser route reaches AmazonUserManager.createAdultUser/createChildUser
- Effect: No recovered H2 path to setHomeActivity/setComponentEnabledSetting/setApplicationEnabledSetting
- Confidence/status: **POSITIVE_STATIC_SINK_CALLER_UNKNOWN** / `POSITIVE_STATIC_SINK_CALLER_UNKNOWN`
- Scope: previous public Phase 9 corpus

## 6X4-PERMISSION-012
- Phase/surface: `6X4` / `permission consumer/holder closure`
- Source: `artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/H2ClientService.java`
- Evidence: `artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/H2ClientService.java`
- SHA-256: `f30c3b42ce45c1e7ef717b2deb5b0402dbc01fc70cb5a86480d8b4a54e7fa9e5`
- Caller: UNKNOWN; service-boundary
- Gate: NOT_APPLICABLE; custom owner/grant positive but accepted caller UNKNOWN; No extra method-local gate beyond manifest permission in recovered Stub
- Identity/user scope: UID logging only; no identity clear/restore in H2 implementation; UNKNOWN
- Sink: household/profile workflow; User 0/HOME writer not joined
- Effect: Static H2 service sink is profile lifecycle; not formal HOME/package-state mutation
- Confidence/status: **BOUNDED_NEGATIVE_HOME_PACKAGE_SINK** / `BOUNDED_NEGATIVE_HOME_PACKAGE_SINK`
- Scope: previous public Phase 9 corpus

## 6X4-OTA-001
- Phase/surface: `6X4` / `OTA indirect/update closure`
- Source: `phase6ne direct-call-edges.csv; focus-disassembly.txt; phase6mm selected-call-edges.csv`
- Evidence: `phase6ne direct-call-edges.csv; focus-disassembly.txt; phase6mm selected-call-edges.csv`
- SHA-256: `1105a7ac6fe5104222394fefe2576a96419dbab8fd85b416e77209c79209ba89`
- Caller: direct native edge only; no execution or caller reachability
- Gate: direct native edge only; no execution or caller reachability
- Identity/user scope: direct native edge only; no execution or caller reachability
- Sink: PerformBlockImageUpdate -> CacheSizeCheck
- Effect: 0x409cb4 and 0x409cdc call symbol-resolved 0x414720
- Confidence/status: **closure** / `closure`
- Scope: previous public Phase 9 corpus

## 6X4-OTA-002
- Phase/surface: `6X4` / `OTA indirect/update closure`
- Source: `phase6ne focus-disassembly.txt; direct-call-edges.csv`
- Evidence: `phase6ne focus-disassembly.txt; direct-call-edges.csv`
- SHA-256: `1105a7ac6fe5104222394fefe2576a96419dbab8fd85b416e77209c79209ba89`
- Caller: callee argument provenance is static; no untrusted control established
- Gate: callee argument provenance is static; no untrusted control established
- Identity/user scope: callee argument provenance is static; no untrusted control established
- Sink: CacheSizeCheck -> MakeFreeSpaceOnCache with size argument
- Effect: 0x414730 branches to 0x417778 after preserving x0 size
- Confidence/status: **closure** / `closure`
- Scope: previous public Phase 9 corpus

## 6X4-OTA-003
- Phase/surface: `6X4` / `OTA indirect/update closure`
- Source: `phase6ne return-branches.csv; focus-disassembly.txt`
- Evidence: `phase6ne return-branches.csv; focus-disassembly.txt`
- SHA-256: `1105a7ac6fe5104222394fefe2576a96419dbab8fd85b416e77209c79209ba89`
- Caller: control-flow closure is not a bypass
- Gate: control-flow closure is not a bypass
- Identity/user scope: control-flow closure is not a bypass
- Sink: CacheSizeCheck and callers have explicit return/error branches
- Effect: negative/sign-bit result errors; zero caller result continues; non-zero errors
- Confidence/status: **closure** / `closure`
- Scope: previous public Phase 9 corpus

## 6X4-OTA-004
- Phase/surface: `6X4` / `OTA indirect/update closure`
- Source: `phase6ne direct-call-edges.csv; phase6mm canonicalization-call-sites.csv`
- Evidence: `phase6ne direct-call-edges.csv; phase6mm canonicalization-call-sites.csv`
- SHA-256: `1105a7ac6fe5104222394fefe2576a96419dbab8fd85b416e77209c79209ba89`
- Caller: path operation presence does not prove attacker-controlled input or impact
- Gate: path operation presence does not prove attacker-controlled input or impact
- Identity/user scope: path operation presence does not prove attacker-controlled input or impact
- Sink: MakeFreeSpaceOnCache path operations
- Effect: readlink_chk at 0x417bf0 plus stat/directory/unlink/free-space edges are direct and symbol-resolved
- Confidence/status: **closure** / `closure`
- Scope: previous public Phase 9 corpus

## 6X4-OTA-005
- Phase/surface: `6X4` / `OTA indirect/update closure`
- Source: `phase6mk registration-dispatch.csv; phase6mm block-image-registration.csv; phase6mk summary.json`
- Evidence: `phase6mk registration-dispatch.csv; phase6mm block-image-registration.csv; phase6mk summary.json`
- SHA-256: `1105a7ac6fe5104222394fefe2576a96419dbab8fd85b416e77209c79209ba89`
- Caller: cell/address-only provenance is not caller authorization or bypass
- Gate: cell/address-only provenance is not caller authorization or bypass
- Identity/user scope: cell/address-only provenance is not caller authorization or bypass
- Sink: Indirect registry dispatch resolution
- Effect: 24 install cells and 5 block-image cells resolve to named symbols; RegisterFunction remains indirect
- Confidence/status: **closure** / `closure`
- Scope: previous public Phase 9 corpus

## 6X4-OTA-006
- Phase/surface: `6X4` / `OTA indirect/update closure`
- Source: `phase6mk updater-script-entrypoints.csv; phase6mm focus-disassembly.txt; phase6md path-write-call-edges.csv`
- Evidence: `phase6mk updater-script-entrypoints.csv; phase6mm focus-disassembly.txt; phase6md path-write-call-edges.csv`
- SHA-256: `1105a7ac6fe5104222394fefe2576a96419dbab8fd85b416e77209c79209ba89`
- Caller: signed recovery updater capability only; no arbitrary archive/partition selection
- Gate: signed recovery updater capability only; no arbitrary archive/partition selection
- Identity/user scope: signed recovery updater capability only; no arbitrary archive/partition selection
- Sink: Archive/transfer-list and writer argument chain
- Effect: fixed script archive names feed block-image handler; WriteToPartition target string reaches ota_open/ota_write/write
- Confidence/status: **closure** / `closure`
- Scope: previous public Phase 9 corpus

## 6X4-OTA-007
- Phase/surface: `6X4` / `OTA indirect/update closure`
- Source: `phase6mk canonicalization-context.csv; canonicalization-marker-strings.csv; phase6mm canonicalization-call-sites.csv; phase6md path-marker-strings.csv`
- Evidence: `phase6mk canonicalization-context.csv; canonicalization-marker-strings.csv; phase6mm canonicalization-call-sites.csv; phase6md path-marker-strings.csv`
- SHA-256: `1105a7ac6fe5104222394fefe2576a96419dbab8fd85b416e77209c79209ba89`
- Caller: bounded negative only; unselected/indirect edges remain unresolved
- Gate: bounded negative only; unselected/indirect edges remain unresolved
- Identity/user scope: bounded negative only; unselected/indirect edges remain unresolved
- Sink: No selected canonicalization-to-write direct edge
- Effect: markers and MakeFreeSpaceOnCache readlink_chk exist, but selected graph has no direct edge to WriteToPartition
- Confidence/status: **negative** / `negative`
- Scope: previous public Phase 9 corpus

## 6X4-OTA-008
- Phase/surface: `6X4` / `OTA indirect/update closure`
- Source: `phase6kt audit.json; phase6mk summary.json`
- Evidence: `phase6kt audit.json; phase6mk summary.json`
- SHA-256: `1105a7ac6fe5104222394fefe2576a96419dbab8fd85b416e77209c79209ba89`
- Caller: wrapper, capability, address-only target, or function-pointer cell is not bypass evidence
- Gate: wrapper, capability, address-only target, or function-pointer cell is not bypass evidence
- Identity/user scope: wrapper, capability, address-only target, or function-pointer cell is not bypass evidence
- Sink: AVB/rollback native handoff not closed and no bypass
- Effect: RecoverySystem verification precedes handoff, but exact native verifier/AVB/rollback provenance is absent
- Confidence/status: **negative** / `negative`
- Scope: previous public Phase 9 corpus

## P7-SOURCE-001
- Phase/surface: `7` / `7.3.3.1 source/installer scope`
- Source: `official source archive`
- Evidence: `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2`
- SHA-256: `ab88fcac93808e197dd97c2d1ecd21bfd33dbb8cbea1775ea243f53765d66f6d`
- Caller: firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2
- Gate: Official PS7331 source archive identity is preserved; size/hash match prior HTTP provenance.
- Identity/user scope: UNKNOWN
- Sink: source/build/installer provenance
- Effect: Official PS7331 source archive identity is preserved; size/hash match prior HTTP provenance.
- Confidence/status: **CONFIRMED** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## P7-SOURCE-002
- Phase/surface: `7` / `7.3.3.1 source/installer scope`
- Source: `source bundle scope`
- Evidence: `firmware/extracted/PS7331-SOURCE-20250617/platform.tar; fireos.tar`
- SHA-256: `b6376c25c36b315d640704c7e69c34c59ac42299db956035eabf3343986f076a`
- Caller: firmware/extracted/PS7331-SOURCE-20250617/platform.tar; fireos.tar
- Gate: Source scope includes system/core, MT8183 kernel/init/drivers, Amazon driver source, FireOS/userspace source and apps; remains source/build material.
- Identity/user scope: UNKNOWN
- Sink: source/build/installer provenance
- Effect: Source scope includes system/core, MT8183 kernel/init/drivers, Amazon driver source, FireOS/userspace source and apps; remains source/build material.
- Confidence/status: **CONFIRMED** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## P7-SOURCE-003
- Phase/surface: `7` / `7.3.3.1 source/installer scope`
- Source: `source bundle scope`
- Evidence: `firmware/extracted/PS7331-SOURCE-20250617/platform.tar; fireos.tar`
- SHA-256: `46a602a9c8830281f9345aa3ae597ea8728e7c0472f331d8f9702b9b9ddbfeae`
- Caller: firmware/extracted/PS7331-SOURCE-20250617/platform.tar; fireos.tar
- Gate: Bounded nested-tar audit found no OTA installer members update-binary/updater-script/payload.bin/.new.dat/otacert; recovery.c hits are source filenames only.
- Identity/user scope: UNKNOWN
- Sink: source/build/installer provenance
- Effect: Bounded nested-tar audit found no OTA installer members update-binary/updater-script/payload.bin/.new.dat/otacert; recovery.c hits are source filenames only.
- Confidence/status: **CONFIRMED_NEGATIVE** / `CONFIRMED_NEGATIVE`
- Scope: previous public Phase 9 corpus

## P7-SOURCE-004
- Phase/surface: `7` / `7.3.3.1 source/installer scope`
- Source: `signed OTA provenance`
- Evidence: `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin`
- SHA-256: `1f18be825bb2b250080cb05c42fc92c66631d7eb2d6493bc40e9d25526fed33b`
- Caller: firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin
- Gate: Official SignApk OTA is distinct from source bundle and contains update-binary, updater-script, block payloads, boot and boot-chain images.
- Identity/user scope: UNKNOWN
- Sink: source/build/installer provenance
- Effect: Official SignApk OTA is distinct from source bundle and contains update-binary, updater-script, block payloads, boot and boot-chain images.
- Confidence/status: **CONFIRMED** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## P7-SOURCE-005
- Phase/surface: `7` / `7.3.3.1 source/installer scope`
- Source: `installer gate/sink boundary`
- Evidence: `firmware/extracted/PS7331/META-INF/com/google/android/updater-script`
- SHA-256: `bd91a9c407c036373a8cf5957e3d7f00846dcd7cd25e24dbdca713fc96ae873a`
- Caller: firmware/extracted/PS7331/META-INF/com/google/android/updater-script
- Gate: Saved updater-script has trona/build-date assertions and static block/image writes; existing OTA evidence, not a new vulnerability claim.
- Identity/user scope: UNKNOWN
- Sink: source/build/installer provenance
- Effect: Saved updater-script has trona/build-date assertions and static block/image writes; existing OTA evidence, not a new vulnerability claim.
- Confidence/status: **DEDUP_EXISTING_PHASE6X4** / `DEDUP_EXISTING_PHASE6X4`
- Scope: previous public Phase 9 corpus

## P7-SOURCE-006
- Phase/surface: `7` / `7.3.3.1 source/installer scope`
- Source: `signed boot comparison`
- Evidence: `firmware/extracted/PS7331/boot.img; source rtmutex.c`
- SHA-256: `46a602a9c8830281f9345aa3ae597ea8728e7c0472f331d8f9702b9b9ddbfeae`
- Caller: firmware/extracted/PS7331/boot.img; source rtmutex.c
- Gate: OTA boot member equals saved extracted boot hash; PS7331 source rtmutex hash equals prior semantic evidence. Identity/semantic comparison only.
- Identity/user scope: UNKNOWN
- Sink: source/build/installer provenance
- Effect: OTA boot member equals saved extracted boot hash; PS7331 source rtmutex hash equals prior semantic evidence. Identity/semantic comparison only.
- Confidence/status: **CONFIRMED_VERSION_SCOPED** / `CONFIRMED_VERSION_SCOPED`
- Scope: previous public Phase 9 corpus

## P7-SOURCE-007
- Phase/surface: `7` / `7.3.3.1 source/installer scope`
- Source: `Amazon driver source`
- Evidence: `firmware/extracted/PS7331-SOURCE-20250617/platform/device/amazon/kernel/driver/amzn_drv_test.c`
- SHA-256: `6c2309f996cacafaab35cce3935bcb725a5259211751af89df88d3732797029e`
- Caller: firmware/extracted/PS7331-SOURCE-20250617/platform/device/amazon/kernel/driver/amzn_drv_test.c
- Gate: Driver test source contains OTA reboot/test labels, but source presence is not proof of production caller, UID/domain, SELinux gate, open/ioctl reachability or sink.
- Identity/user scope: UNKNOWN
- Sink: source/build/installer provenance
- Effect: Driver test source contains OTA reboot/test labels, but source presence is not proof of production caller, UID/domain, SELinux gate, open/ioctl reachability or sink.
- Confidence/status: **OPEN_BOUNDARY_NO_VULNERABILITY** / `OPEN_BOUNDARY_NO_VULNERABILITY`
- Scope: previous public Phase 9 corpus

## P7-SOURCE-008
- Phase/surface: `7` / `7.3.3.1 source/installer scope`
- Source: `version provenance`
- Evidence: `source archive and official PS7331 OTA`
- SHA-256: `phase5BT metadata; phase5 official-update source-map; OTA provenance README`
- Caller: source archive and official PS7331 OTA
- Gate: Current saved device baseline versus PS7331 source/OTA
- Identity/user scope: UNKNOWN
- Sink: source/build/installer provenance
- Effect: Current saved device baseline versus PS7331 source/OTA
- Confidence/status: **0a7eb0ac06352eb33b9ac5ce8416637b6819c67c1389bc52937ff893c836f6be** / `0a7eb0ac06352eb33b9ac5ce8416637b6819c67c1389bc52937ff893c836f6be`
- Scope: previous public Phase 9 corpus

## P7-IPC-001
- Phase/surface: `7` / `Amazon Framework/System Services IPC`
- Source: `decompiled fosservices 40453-40534; boot-fosframework 394721-395074; phase6up prewarm CSV`
- Evidence: `decompiled fosservices 40453-40534; boot-fosframework 394721-395074; phase6up prewarm CSV`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`
- Caller: caller not recovered; known caller is privileged Alexa-side code
- Gate: APP_PREWARM check; result consumption unresolved
- Identity/user scope: clearCallingIdentity before package/process work; original UID not shown at sink; explicit package plus integer user; User-0/User-10 validation unknown
- Sink: IPackageManager.getApplicationInfo -> PreWarmCacheHelper -> startProcessLocked reason prewarm
- Effect: static process/resource deputy; no HOME/PMS writer or saved dispatch
- Confidence/status: **unknown** / `unknown`
- Scope: previous public Phase 9 corpus

## P7-IPC-002
- Phase/surface: `7` / `Amazon Framework/System Services IPC`
- Source: `amazonactivitymanager_fosinit 8-23; service-context-matrix row 38; phase6up prewarm CSV`
- Evidence: `amazonactivitymanager_fosinit 8-23; service-context-matrix row 38; phase6up prewarm CSV`
- SHA-256: `5d212c94f047aee7abc85ef6dc99aa92ca61e3e3d9318bb69db3c10d9e0da411;5063f3de53710d009f2f80c68d5194d471c248f8564aaa05925faf94149f4aea;ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: system_server fosinit loader / ActivityManager manager fetcher
- Gate: service publication plus SELinux service label; method gate not recovered
- Identity/user scope: system_server service context; external caller identity not observed; service-global; prewarm carries explicit user only
- Sink: AmazonActivityManagerService BinderService / AmazonActivityManagerImpl
- Effect: registration real; saved shell lookup/transaction did not establish dispatch; no HOME/package-state effect
- Confidence/status: **duplicate** / `duplicate`
- Scope: previous public Phase 9 corpus

## P7-IPC-003
- Phase/surface: `7` / `Amazon Framework/System Services IPC`
- Source: `boot-fosframework 369180-370443; fosservices 54297-54478; phase6ub and phase6uf CSV`
- Evidence: `boot-fosframework 369180-370443; fosservices 54297-54478; phase6ub and phase6uf CSV`
- SHA-256: `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71;ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: createChildUser internal path plus onBootPhase upgrade path; external caller not joined
- Gate: Stub enforceInterface only; no tx3-specific MANAGE_USERS or checkCallingUid gate visible
- Identity/user scope: transacted caller UID not recovered; writer has no identity clear; UserInfo.id from createUser flags 0x8000; child/profile not proven User-0
- Sink: PackageManager component/app-state setters for Tahoe Fire Launcher3
- Effect: accepted external tx3 caller and cross-user admin gate remain unresolved
- Confidence/status: **unknown** / `unknown`
- Scope: previous public Phase 9 corpus

## P7-IPC-004
- Phase/surface: `7` / `Amazon Framework/System Services IPC`
- Source: `fosservices 54297-54325 and 55053-55119; phase6ub CSV; phase6x4 report`
- Evidence: `fosservices 54297-54325 and 55053-55119; phase6ub CSV; phase6x4 report`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: AmazonUserManagerService child/upgrade branches
- Gate: child predicate and lifecycle; no method-local gate in writer
- Identity/user scope: system_server/AmazonUserManager process; no identity transition; UserInfo.id only; no constant User-0 target
- Sink: Tahoe component enabled plus Fire/Launcher3 app state set for supplied user
- Effect: real child/profile writer; saved tests preserve User-0 Fire Launcher; no preferred-HOME setter joined
- Confidence/status: **bounded-negative** / `bounded-negative`
- Scope: previous public Phase 9 corpus

## P7-IPC-005
- Phase/surface: `7` / `Amazon Framework/System Services IPC`
- Source: `phase6ub CSV; phase6x reconcile CSV; phase6x4 baseline CSV`
- Evidence: `phase6ub CSV; phase6x reconcile CSV; phase6x4 baseline CSV`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;b6a3ad87a24e4fc185a29dc18c92c4144889ad19e6283ac9a17db762b10a52fc`
- Caller: no named production caller joined; historical resolver/package captures only
- Gate: existing PMS/HOME gates; no Fire-targeted restoration setter recovered
- Identity/user scope: caller and UID unknown; User-0 candidate only; KFT writer is child/profile supplied-user scoped
- Sink: no exact Fire setHomeActivity or replacePreferredActivity or User-0 writer
- Effect: Fire Launcher remains saved User-0 HOME; no new mutation
- Confidence/status: **bounded-negative** / `bounded-negative`
- Scope: previous public Phase 9 corpus

## P7-IPC-006
- Phase/surface: `7` / `Amazon Framework/System Services IPC`
- Source: `phase6qe caller closure; phase6x4 evidence index 2060-2071; phase6su CSV`
- Evidence: `phase6qe caller closure; phase6x4 evidence index 2060-2071; phase6su CSV`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: DPM owner/admin/profile scope from saved tests; ordinary app not established
- Gate: DPM owner/admin plus PMS package-state gates; downstream method check bounded
- Identity/user scope: system/root or trusted owner/admin; no clear identity to ordinary caller; profile/owner target user plus package
- Sink: PMS package/component state writer tx73
- Effect: trusted policy behavior bounded; no HOME selection or sustainable ordinary-app route
- Confidence/status: **duplicate** / `duplicate`
- Scope: previous public Phase 9 corpus

## P7-IPC-007
- Phase/surface: `7` / `Amazon Framework/System Services IPC`
- Source: `amazonpackagemanager_fosinit 8-28; service-context-matrix row 45; fosdebug inventory; phase6x4 evidence index`
- Evidence: `amazonpackagemanager_fosinit 8-28; service-context-matrix row 45; fosdebug inventory; phase6x4 evidence index`
- SHA-256: `eb53e50cf72174eddcde25fd3538e4736d2cd4cb7866bab4e5bc2b70fc514286;5063f3de53710d009f2f80c68d5194d471c248f8564aaa05925faf94149f4aea`
- Caller: system_server lifecycle plus PMS upgrade state
- Gate: boot/upgrade lifecycle and protected callback gates; ordinary broadcast relay not established
- Identity/user scope: system_server identity; no external Binder identity; system/default or callback-derived package scope
- Sink: package metadata and protected-package/cache callbacks
- Effect: no Fire HOME writer; no ordinary caller or observed package-state mutation
- Confidence/status: **bounded-negative** / `bounded-negative`
- Scope: previous public Phase 9 corpus

## P7-IPC-008
- Phase/surface: `7` / `Amazon Framework/System Services IPC`
- Source: `launcherhijackpreventer_fosinit 8-16; fosservices 136857-137040; phase6rt CSV`
- Evidence: `launcherhijackpreventer_fosinit 8-16; fosservices 136857-137040; phase6rt CSV`
- SHA-256: `026a1efce008ef99cc2afa32a9bc8913bf929e74256af67971f426a97c968eea;ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: AMS/ActivityTask in-process dispatcher
- Gate: Leanback plus seInfo see_home_task or Android signature fallback; no exported component gate
- Identity/user scope: system_server callback identity; caller package/UID is input; activity/task scope; no user mutation argument
- Sink: canSeeHomeTask and permission decision only
- Effect: HOME visibility/permission gate; not selector or package-state writer; no Binder relay
- Confidence/status: **bounded-negative** / `bounded-negative`
- Scope: previous public Phase 9 corpus

## P7-IPC-009
- Phase/surface: `7` / `Amazon Framework/System Services IPC`
- Source: `fosservices 168487-168535; boot-fosframework 391141-391186; phase6x IPC CSV`
- Evidence: `fosservices 168487-168535; boot-fosframework 391141-391186; phase6x IPC CSV`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71;5063f3de53710d009f2f80c68d5194d471c248f8564aaa05925faf94149f4aea`
- Caller: external Binder caller not recovered; service context unmapped
- Gate: CONTROL_KEYGUARD or Amazon keyguard permission via checkUidPermission
- Identity/user scope: Binder.getCallingUid retained; verified package forwarded; no clearCallingIdentity; no explicit user; PendingIntent/SystemUI target scope
- Sink: IAmazonKeyguardServiceSystemUI.dismissWithPendingIntent
- Effect: keyguard dismissal/PendingIntent handoff only; no runtime success or HOME/package mutation
- Confidence/status: **duplicate** / `duplicate`
- Scope: previous public Phase 9 corpus

## P7-IPC-010
- Phase/surface: `7` / `Amazon Framework/System Services IPC`
- Source: `fosservices 168690-168795; boot-fosframework 391292-391349; phase6x IPC CSV`
- Evidence: `fosservices 168690-168795; boot-fosframework 391292-391349; phase6x IPC CSV`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`
- Caller: external Binder caller not recovered
- Gate: CONTROL_KEYGUARD or Amazon keyguard permission
- Identity/user scope: calling UID/package retained and forwarded; no clear identity; user not explicit; global SystemUI presentation scope
- Sink: IAmazonKeyguardServiceSystemUI accessibility and foreground state
- Effect: keyguard presentation only; no HOME/package writer or runtime acceptance
- Confidence/status: **duplicate** / `duplicate`
- Scope: previous public Phase 9 corpus

## P7-IPC-011
- Phase/surface: `7` / `Amazon Framework/System Services IPC`
- Source: `tabletkeypolicymanager_fosinit 8-19; fosdebug inventory rows 182-183 and 273-299; phase6rt CSV`
- Evidence: `tabletkeypolicymanager_fosinit 8-19; fosdebug inventory rows 182-183 and 273-299; phase6rt CSV`
- SHA-256: `802a9b8e22ac485a07d5198bd22fd6aae18920f56af4f34a2ba35a0083a91ffe;20c0d022e7c71b431dc8b992077ad01b7cbefdae85ce3c59e169f49ffafea29a`
- Caller: PhoneWindowManager/system_server callback dispatcher
- Gate: callback registration plus input/window policy checks; no exported AIDL
- Identity/user scope: system_server identity; input event/window policy context; device/global key policy scope; no user argument
- Sink: PhoneWindowManager key interception and policy decision
- Effect: keyboard/navigation policy only; no launcher/package/settings writer
- Confidence/status: **bounded-negative** / `bounded-negative`
- Scope: previous public Phase 9 corpus

## P7-IPC-012
- Phase/surface: `7` / `Amazon Framework/System Services IPC`
- Source: `keypolicymanager_fosinit 8-16; fosdebug inventory rows 182-201; boot-fosframework 58936-58976; phase6rs CSV`
- Evidence: `keypolicymanager_fosinit 8-16; fosdebug inventory rows 182-201; boot-fosframework 58936-58976; phase6rs CSV`
- SHA-256: `802a9b8e22ac485a07d5198bd22fd6aae18920f56af4f34a2ba35a0083a91ffe;5063f3de53710d009f2f80c68d5194d471c248f8564aaa05925faf94149f4aea;fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`
- Caller: SettingsProvider callback construction
- Gate: provider API authorization remains authoritative
- Identity/user scope: provider/server process identity; no external Binder caller attached; settings provider cache/user context; per-user routing not recovered
- Sink: SettingsProvider callback setting initialization/update
- Effect: callback state only; no caller-controlled settings write or HOME/PMS edge
- Confidence/status: **bounded-negative** / `bounded-negative`
- Scope: previous public Phase 9 corpus

## P7-IPC-013
- Phase/surface: `7` / `Amazon Framework/System Services IPC`
- Source: `SettingsProvider 238-264 344-418 658-704 1229-1302; settings manifest; phase6rs CSV`
- Evidence: `SettingsProvider 238-264 344-418 658-704 1229-1302; settings manifest; phase6rs CSV`
- SHA-256: `a8fbe99c7f72432eec5af24d5640fb2df2795e112342cf427e6afb7a9c56021d`
- Caller: external ContentProvider caller not enumerated
- Gate: WRITE_SECURE_SETTINGS plus setting-specific restrictions plus cross-user enforcement
- Identity/user scope: ContentProvider retains Binder UID/package; no clearCallingIdentity; requesting user resolved through ActivityManager; global/secure per-user routing
- Sink: SettingsRegistry state plus persisted settings XML; no HOME/package-state sink
- Effect: real static writer but arbitrary caller and target key acceptance not closed; no saved mutation
- Confidence/status: **unknown** / `unknown`
- Scope: previous public Phase 9 corpus

## P7-IPC-014
- Phase/surface: `7` / `Amazon Framework/System Services IPC`
- Source: `amazonactivitymanager_fosinit 12-22; fosservices 180180-180210; phase6rt CSV`
- Evidence: `amazonactivitymanager_fosinit 12-22; fosservices 180180-180210; phase6rt CSV`
- SHA-256: `5d212c94f047aee7abc85ef6dc99aa92ca61e3e3d9318bb69db3c10d9e0da411;ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: AMS system_server lifecycle callback
- Gate: private in-process callback dispatch; no external transaction gate
- Identity/user scope: system_server identity; resumed ComponentName and user lifecycle; activity/user lifecycle scope
- Sink: ActivitySwitchHandler/observer notification
- Effect: activity event notification only; no PMS/HOME writer or saved effect
- Confidence/status: **bounded-negative** / `bounded-negative`
- Scope: previous public Phase 9 corpus

## P7-IPC-015
- Phase/surface: `7` / `Amazon Framework/System Services IPC`
- Source: `phase6x4 evidence index 2437-2456; fosdebug inventory rows 14-18`
- Evidence: `phase6x4 evidence index 2437-2456; fosdebug inventory rows 14-18`
- SHA-256: `5063f3de53710d009f2f80c68d5194d471c248f8564aaa05925faf94149f4aea;71ec62fe8eb8bd575da8b7d3bfd17dfd55d8488b9ebb2449ba720a4e2cd48c7e`
- Caller: internal DCPMS caller not recovered; local process binder
- Gate: Stub slice shows no calling UID/user check; external publication not established
- Identity/user scope: process identity retained; no clearCallingIdentity; singleUser and no explicit user argument in bounded AIDL
- Sink: DeviceExperienceModeDecisionManager and DCPMS policy state
- Effect: CDE/profile policy evaluation only; no SettingsProvider/PMS/HOME/OTA sink
- Confidence/status: **unknown** / `unknown`
- Scope: previous public Phase 9 corpus

## P7-KERNEL-001
- Phase/surface: `7` / `CMDQ/MDP`
- Source: `work/ps7331-kasan-source-20260810/drivers/misc/mediatek/cmdq/v3/cmdq_driver.c:660-700,864-898; mdp_ioctl_ex.c:332-405,602-729`
- Evidence: `work/ps7331-kasan-source-20260810/drivers/misc/mediatek/cmdq/v3/cmdq_driver.c:660-700,864-898; mdp_ioctl_ex.c:332-405,602-729`
- SHA-256: `b3a54d37b4e498ff969a2717cb02cefc923ae6f39da32f5fd8529fe3dce6e899`
- Caller: UNKNOWN: no exact shipped ELF open/ioctl callsite; library markers are insufficient
- Gate: UNKNOWN: no exact node label/mode file_contexts/TE allow tuple retained; CONFIG_MTK_CMDQ=y plus DT/platform match; final built-in/module/Image join UNKNOWN
- Identity/user scope: UNKNOWN: no exact shipped ELF open/ioctl callsite; library markers are insufficient; /dev/mtk_cmdq; /proc/mtk_cmdq_debug/*; sysfs attrs; ioctl CMDQ_IOCTL_ASYNC_EXEC/WAIT/READBACK
- Sink: cmdq_ioctl -> async job/readback -> MDP register/hardware path
- Effect: Potential display/engine/resource control; no framework/package sink shown
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P7-KERNEL-002
- Phase/surface: `7` / `M4U ioctl/proc`
- Source: `work/ps7331-kasan-source-20260810/drivers/misc/mediatek/m4u/2.4/m4u.c:1577-1809,2220-2270`
- Evidence: `work/ps7331-kasan-source-20260810/drivers/misc/mediatek/m4u/2.4/m4u.c:1577-1809,2220-2270`
- SHA-256: `6351de00903a282ba682427095a155794efd8221f253ff11a0f74ed7c5cb86c6`
- Caller: UNKNOWN: no shipped native caller or UID/domain
- Gate: UNKNOWN: proc mode 0 is source literal; exact label/allow absent; driver source/DT/config gate; active misc /dev/m4u branch is #if 0
- Identity/user scope: UNKNOWN: no shipped native caller or UID/domain; /proc/m4u; MTK_M4U_T_POWER_ON/OFF,ALLOC_MVA,CONFIG_PORT,MONITOR,CONFIG_TF
- Sink: DMA/IOMMU mapping port/power/monitor/TF controls
- Effect: Potential memory-isolation or device-state impact; no package/HOME/PMS sink
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P7-KERNEL-003
- Phase/surface: `7` / `ION generic`
- Source: `work/ps7331-kasan-source-20260810/drivers/staging/android/ion/ion.c:1502-1503,1657-1658,1906-1924`
- Evidence: `work/ps7331-kasan-source-20260810/drivers/staging/android/ion/ion.c:1502-1503,1657-1658,1906-1924`
- SHA-256: `abac518864faed94439d75d204e8c16ea75cf3a74c93ee50e128e0f6928a6d63`
- Caller: UNKNOWN: no exact gralloc/codec/native open/ioctl caller or UID/domain
- Gate: UNKNOWN: node mode/label and allow not joined; CONFIG_ION=y; CONFIG_ION_TEST absent; final heap enablement unknown
- Identity/user scope: UNKNOWN: no exact gralloc/codec/native open/ioctl caller or UID/domain; /dev/ion; alloc/free/map/share/import/sync/custom ioctl
- Sink: buffer allocation/import/custom ioctl -> DMA/buffer state
- Effect: Potential buffer/DMA exposure; no framework package-state sink proven
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P7-KERNEL-004
- Phase/surface: `7` / `ION MediaTek custom`
- Source: `work/ps7331-kasan-source-20260810/drivers/staging/android/ion/mtk/ion_drv.c:319-435,612,765`
- Evidence: `work/ps7331-kasan-source-20260810/drivers/staging/android/ion/mtk/ion_drv.c:319-435,612,765`
- SHA-256: `eb7fbf99acbc492d99d60c98fc62a67fe7350160c6e91dc033781d5bcd986411`
- Caller: UNKNOWN: no exact shipped custom ioctl caller or UID/domain
- Gate: UNKNOWN: node/type/allow absent; CONFIG_MTK_ION=y; heap and platform registration not fully joined
- Identity/user scope: UNKNOWN: no exact shipped custom ioctl caller or UID/domain; /dev/ion custom ioctl; ion_device_create; secure/physical-address paths
- Sink: custom system/physical-address/secure-memory controls
- Effect: Potential physical-address/secure-buffer state; no package/HOME effect shown
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P7-KERNEL-005
- Phase/surface: `7` / `MediaTek performance ioctl`
- Source: `work/ps7331-kasan-source-20260810/drivers/misc/mediatek/performance/perf_ioctl/perf_ioctl.c:69-203,231-232`
- Evidence: `work/ps7331-kasan-source-20260810/drivers/misc/mediatek/performance/perf_ioctl/perf_ioctl.c:69-203,231-232`
- SHA-256: `df846d7463d14af07fa98bb0a26d389c1a5e41a46b58763327c9d47a2aa3ff09`
- Caller: UNKNOWN: no exact shipped native writer or UID/domain
- Gate: UNKNOWN: source mode 0664 lacks final owner/label/TE allow; driver Kconfig and proc registration; product caller gate unknown
- Identity/user scope: UNKNOWN: no exact shipped native writer or UID/domain; /proc/perfmgr/perf_ioctl; FPSGO_* write/ioctl/compat_ioctl
- Sink: performance/governor/touch-boost scheduling controls
- Effect: Authorized writer could alter performance/resource state; no package sink
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P7-KERNEL-006
- Phase/surface: `7` / `AUXADC ioctl/sysfs`
- Source: `work/ps7331-kasan-source-20260810/drivers/misc/mediatek/auxadc/mtk_auxadc.c:553-667,1515-1651`
- Evidence: `work/ps7331-kasan-source-20260810/drivers/misc/mediatek/auxadc/mtk_auxadc.c:553-667,1515-1651`
- SHA-256: `5ffbce942417fc6aca773d90e4c6935f508087f9a80d96138a7ecc30561ed327`
- Caller: UNKNOWN: no exact shipped native open/ioctl or sysfs writer; UID/domain unknown
- Gate: UNKNOWN: exact sysfs/node label mode and TE allow absent; CONFIG_MTK_AUXADC_INTF=y plus selected platform driver
- Identity/user scope: UNKNOWN: no exact shipped native open/ioctl or sysfs writer; UID/domain unknown; AUXADC ioctl/compat_ioctl; writable dump/status/calibration attributes
- Sink: ADC/register diagnostic/calibration read/write paths
- Effect: Hardware/diagnostic state effect possible; no package/HOME effect
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P7-KERNEL-007
- Phase/surface: `7` / `PMIC debugfs/sysfs`
- Source: `work/ps7331-kasan-source-20260810/drivers/misc/mediatek/pmic/common/upmu_debugfs.c:323-351`
- Evidence: `work/ps7331-kasan-source-20260810/drivers/misc/mediatek/pmic/common/upmu_debugfs.c:323-351`
- SHA-256: `db8dfc551225586a717af6cc96057b8d810548cf123bd555cfb5d5698b5ec092`
- Caller: UNKNOWN: no shipped debugfs writer or UID/domain
- Gate: UNKNOWN: debugfs type/mode/mount and file_contexts/TE allow absent; PMIC debug feature/Kconfig gate unresolved
- Identity/user scope: UNKNOWN: no shipped debugfs writer or UID/domain; mtk_pmic debugfs/sysfs entries including dump_pmic_reg
- Sink: writable PMIC register dump/debug controls
- Effect: Potential PMIC register/debug state effect; no package/HOME sink
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P7-KERNEL-008
- Phase/surface: `7` / `uinput`
- Source: `work/ps7331-kasan-source-20260810/drivers/input/misc/uinput.c:909-933`
- Evidence: `work/ps7331-kasan-source-20260810/drivers/input/misc/uinput.c:909-933`
- SHA-256: `98b41492311d9b9fb9ccbfe269a2fddc0fb436f3048b7887e1f6e5482d36211a`
- Caller: UNKNOWN: no exact shipped ELF open/write/ioctl caller or UID/domain
- Gate: UNKNOWN: node mode/label and allow absent; CONFIG_INPUT_UINPUT=y; final node creation and caller gate unknown
- Identity/user scope: UNKNOWN: no exact shipped ELF open/write/ioctl caller or UID/domain; /dev/uinput; UI_DEV_CREATE/DESTROY; event writes; ioctl/compat_ioctl
- Sink: synthetic input device/event injection
- Effect: Input graph and downstream user-facing state may be affected; no package/HOME sink
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P7-KERNEL-009
- Phase/surface: `7` / `Amazon liquid-detection sysfs`
- Source: `work/ps7331-kasan-source-20260810/drivers/staging/amazon/amzn_ld.c:638-711,737-786`
- Evidence: `work/ps7331-kasan-source-20260810/drivers/staging/amazon/amzn_ld.c:638-711,737-786`
- SHA-256: `4ef656e1a4e54bce29c6f54d62478b5b68dd093abe2641b85ee15feb1f30d1bc`
- Caller: UNKNOWN: no exact shipped native sysfs writer or UID/domain
- Gate: UNKNOWN: exact sysfs label/allow and owner/group absent; CONFIG_AMAZON_LD=y plus DT compatible/driver registration; DT selection unknown
- Identity/user scope: UNKNOWN: no exact shipped native sysfs writer or UID/domain; conditional liquid-detection sysfs attrs/module parameters; writable 0664 source attrs
- Sink: stop/control/threshold/interval/ADC controls
- Effect: Potential liquid-detection/device behavior change; no framework/package sink shown
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P7-KERNEL-010
- Phase/surface: `7` / `Amazon driver test proc`
- Source: `firmware/extracted/PS7331-SOURCE-20250617/platform/device/amazon/kernel/driver/amzn_drv_test.c:747-812; phase6nb evidence`
- Evidence: `firmware/extracted/PS7331-SOURCE-20250617/platform/device/amazon/kernel/driver/amzn_drv_test.c:747-812; phase6nb evidence`
- SHA-256: `6c2309f996cacafaab35cce3935bcb725a5259211751af89df88d3732797029e`
- Caller: UNKNOWN: no exact open/write caller or UID/domain
- Gate: UNKNOWN: proc label/init import/TE allow absent; CONFIG_AMZN_DRV_TEST default n and dependency chain; conditional only
- Identity/user scope: UNKNOWN: no exact open/write caller or UID/domain; /proc/amzn_drvs/{sign_of_life,idme,logger}; proc_write decimal test_index
- Sink: test dispatcher can write factory-reset/RTC special-mode state if built
- Effect: High-impact factory state is source-capable but not shipped-confirmed; no low-privilege route proven
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P7-KERNEL-011
- Phase/surface: `7` / `Thermal writable sysfs`
- Source: `work/ps7331-kasan-source-20260810/drivers/thermal/thermal_core.c:1672-1753,1772-1909`
- Evidence: `work/ps7331-kasan-source-20260810/drivers/thermal/thermal_core.c:1672-1753,1772-1909`
- SHA-256: `3cb614b7c82c9f933e0dd436702b1f7e29d03307b3a1758d860b1b082897caf9`
- Caller: UNKNOWN: no exact shipped writer or UID/domain
- Gate: UNKNOWN: sysfs labels/allow and provider-specific mode absent; CONFIG_THERMAL_WRITABLE_TRIPS=y plus DT thermal zones/provider
- Identity/user scope: UNKNOWN: no exact shipped writer or UID/domain; /sys/class/thermal/thermal_zone*/{mode,trip_point_*_temp,emul_temp,policy}; writable trip/emulation attrs
- Sink: thermal trip/emulation/governor controls
- Effect: Potential thermal/power/availability effect; no package/HOME sink established
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P7-KERNEL-012
- Phase/surface: `7` / `Input evdev`
- Source: `work/ps7331-kasan-source-20260810/drivers/input/evdev.c:840-892,1329-1331`
- Evidence: `work/ps7331-kasan-source-20260810/drivers/input/evdev.c:840-892,1329-1331`
- SHA-256: `7664e11a712c24b906da6cbf3504c96e00a6b3ca7d64e5b286a345141ada2d28`
- Caller: UNKNOWN: no exact ordinary-app or native event caller and UID/domain
- Gate: UNKNOWN: node mode/file_contexts/TE allow absent; CONFIG_INPUT_EVDEV=y plus selected input devices
- Identity/user scope: UNKNOWN: no exact ordinary-app or native event caller and UID/domain; /dev/input/event*; evdev ioctl/read/write path
- Sink: Input events/state consumed by user-facing components
- Effect: Potential user-facing input-state effect; no direct package/HOME sink
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P7-KERNEL-013
- Phase/surface: `7` / `USB devio`
- Source: `work/ps7331-kasan-source-20260810/drivers/usb/core/devio.c:976-1112,1628-1650,2396-2398,2449`
- Evidence: `work/ps7331-kasan-source-20260810/drivers/usb/core/devio.c:976-1112,1628-1650,2396-2398,2449`
- SHA-256: `655a3f79b2230031e0f2dfef4fbb699d832db9054debf47fd5186acec0af2768`
- Caller: UNKNOWN: no preserved USB ioctl/URB caller or UID/domain
- Gate: UNKNOWN: usbfs device node label/allow absent; CONFIG_USB=y + selected host/controller drivers
- Identity/user scope: UNKNOWN: no preserved USB ioctl/URB caller or UID/domain; USB devio ioctl/URB submission/control-transfer entry
- Sink: USB/device hardware and control-transfer state
- Effect: Potential USB peripheral/hardware state effect; no framework/package sink shown
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P7-KERNEL-014
- Phase/surface: `7` / `RPMB char ABI`
- Source: `work/ps7331-kasan-source-20260810/drivers/char/rpmb/rpmb-mtk.c:2377-2401,2560-2582,2736-2776`
- Evidence: `work/ps7331-kasan-source-20260810/drivers/char/rpmb/rpmb-mtk.c:2377-2401,2560-2582,2736-2776`
- SHA-256: `a6b070190ad8b97173c129509e6d8f8ae8c9f0d383bc349be44d9c919387c8d5`
- Caller: UNKNOWN: rpmb_svc/name evidence does not identify exact shipped open+ioctl caller or UID/domain
- Gate: UNKNOWN: node mode/file_contexts/allow/capable tuple absent; RPMB/MMC configuration and registration; final object gate unknown
- Identity/user scope: UNKNOWN: rpmb_svc/name evidence does not identify exact shipped open+ioctl caller or UID/domain; RPMB char device; unlocked_ioctl; .read/.write NULL
- Sink: authenticated persistent-storage ioctl/state
- Effect: Potential authenticated storage mutation; low-privilege reachability and package/HOME effect unproven
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P7-KERNEL-015
- Phase/surface: `7` / `Amazon DSP debugfs`
- Source: `work/ps7331-kasan-source-20260810/drivers/staging/amazon/dspframework/src/adf_debug.c:245-261`
- Evidence: `work/ps7331-kasan-source-20260810/drivers/staging/amazon/dspframework/src/adf_debug.c:245-261`
- SHA-256: `5831c6e7920f76e8bea94179cf4b0812ceee8b37a59e0a6b420928d2a24331ca`
- Caller: UNKNOWN: no shipped debugfs writer or UID/domain
- Gate: UNKNOWN: debugfs mount/owner/type and SELinux allow absent; DSP framework Kconfig/module gate unresolved
- Identity/user scope: UNKNOWN: no shipped debugfs writer or UID/domain; debugfs /adf_dbg_fs/*; debugfs_create_file callbacks
- Sink: DSP debug/control file callbacks
- Effect: Potential DSP diagnostic/control state; no package/HOME/PMS sink
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P7-RUNTIME-001
- Phase/surface: `7` / `existing runtime/workaround reconciliation`
- Source: `output/tables/phase6di-home-priority-override.csv; findings/phase-6ij-user0-home-candidate-closure.md`
- Evidence: `output/tables/phase6di-home-priority-override.csv; findings/phase-6ij-user0-home-candidate-closure.md`
- SHA-256: `249ff92ad3ae913ed6821b17787e92165f62006894af9764456b00cc25232430`
- Caller: baseline HOME resolver
- Gate: none
- Identity/user scope: user0
- Sink: Fire Launcher priority 50; com.amazon.firelauncher/.Launcher isDefault=true; Fire package enabled=0
- Effect: persistent baseline; not required
- Confidence/status: **CONFIRMED** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## P7-RUNTIME-002
- Phase/surface: `7` / `existing runtime/workaround reconciliation`
- Source: `output/tables/phase6di-home-priority-override.csv; output/tables/phase6ex-preferred-force-stop-home.csv`
- Evidence: `output/tables/phase6di-home-priority-override.csv; output/tables/phase6ex-preferred-force-stop-home.csv`
- SHA-256: `249ff92ad3ae913ed6821b17787e92165f62006894af9764456b00cc25232430`
- Caller: public set-home-activity Microsoft
- Gate: cmd package set-home-activity Microsoft
- Identity/user scope: user0
- Sink: Preferred/mAlways record was written successfully, but resolver and foreground remained Fire priority 50
- Effect: record persisted across reboot; preferred rollback to Fire recorded
- Confidence/status: **CONFIRMED** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## P7-RUNTIME-003
- Phase/surface: `7` / `existing runtime/workaround reconciliation`
- Source: `output/tables/phase6ex-preferred-force-stop-home.csv`
- Evidence: `output/tables/phase6ex-preferred-force-stop-home.csv`
- SHA-256: `21edb5fb681987ef47b8e34a1955681bb85742d4e233a465a51961205f68f11f`
- Caller: set-home plus force-stop checkpoint
- Gate: set Microsoft preferred; force-stop Microsoft; HOME; restore Fire preferred
- Identity/user scope: user0
- Sink: "Fire won HOME; Microsoft stopped; Fire preferred and foreground restored"
- Effect: preferred state persistent; force-stop temporary; successful semantic rollback
- Confidence/status: **CONFIRMED** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## P7-RUNTIME-004
- Phase/surface: `7` / `existing runtime/workaround reconciliation`
- Source: `output/tables/phase6di-home-priority-override.csv; output/tables/phase6fg-pms-protected-package.csv`
- Evidence: `output/tables/phase6di-home-priority-override.csv; output/tables/phase6fg-pms-protected-package.csv`
- SHA-256: `249ff92ad3ae913ed6821b17787e92165f62006894af9764456b00cc25232430`
- Caller: protected package/component disable
- Gate: pm disable-user Fire package/component
- Identity/user scope: user0
- Sink: "SecurityException before state write; Fire package remained protected and HOME priority 50"
- Effect: unchanged; not required
- Confidence/status: **CONFIRMED_NEGATIVE** / `CONFIRMED_NEGATIVE`
- Scope: previous public Phase 9 corpus

## P7-RUNTIME-005
- Phase/surface: `7` / `existing runtime/workaround reconciliation`
- Source: `output/tables/phase6fo-gui-default-apps-home-boundary.csv; findings/phase-6fo-gui-default-apps-home-boundary.md`
- Evidence: `output/tables/phase6fo-gui-default-apps-home-boundary.csv; findings/phase-6fo-gui-default-apps-home-boundary.md`
- SHA-256: `5d8d637d86d32d6cc880f9af04406d1acd39271eddee00552ec317cb73bb9886`
- Caller: Settings GUI default HOME
- Gate: open HOME_SETTINGS / AdvancedAppsActivity
- Identity/user scope: user0
- Sink: "Settings exposed no usable Home-app picker; no GUI HOME replacement; Fire remained HOME"
- Effect: unchanged; not required
- Confidence/status: **CONFIRMED_NEGATIVE** / `CONFIRMED_NEGATIVE`
- Scope: previous public Phase 9 corpus

## P7-RUNTIME-006
- Phase/surface: `7` / `existing runtime/workaround reconciliation`
- Source: `output/tables/phase6dt-dpm-tx100-caller-gate.csv; output/tables/phase6cq-dpm-persistent-preferred-boundary.csv`
- Evidence: `output/tables/phase6dt-dpm-tx100-caller-gate.csv; output/tables/phase6cq-dpm-persistent-preferred-boundary.csv`
- SHA-256: `2447acb2b9dac6f27b2ca32cdc0133d7629deb406a3d6141dd0e769ccf7be657`
- Caller: DPM persistent preferred tx100
- Gate: fake admin/live owner caller attempt
- Identity/user scope: user0
- Sink: "Both caller cases rejected with security error; Fire remained HOME; no persistent preferred write"
- Effect: none; not required
- Confidence/status: **CONFIRMED_NEGATIVE** / `CONFIRMED_NEGATIVE`
- Scope: previous public Phase 9 corpus

## P7-RUNTIME-007
- Phase/surface: `7` / `existing runtime/workaround reconciliation`
- Source: `output/tables/phase6cp-backup-preferred-observation.csv; output/tables/phase6dw-backup-preferred-observation.csv`
- Evidence: `output/tables/phase6cp-backup-preferred-observation.csv; output/tables/phase6dw-backup-preferred-observation.csv`
- SHA-256: `2447acb2b9dac6f27b2ca32cdc0133d7629deb406a3d6141dd0e769ccf7be657`
- Caller: backup preferred restore
- Gate: none; read-only dumpsys backup and static restore path
- Identity/user scope: user0
- Sink: "Backup helper/tx81 exists statically; no restore running; shell writer rejected; Fire unchanged"
- Effect: not tested; not applicable
- Confidence/status: **UNTESTED_SAFE_ROUTE** / `UNTESTED_SAFE_ROUTE`
- Scope: previous public Phase 9 corpus

## P7-RUNTIME-008
- Phase/surface: `7` / `existing runtime/workaround reconciliation`
- Source: `output/tables/phase6cb-gui-child-profile-kft-lifecycle.csv; output/tables/phase6cc-adb-child-home-activation.csv; output/tables/phase6gr-gui-systemui-profile-switch.csv`
- Evidence: `output/tables/phase6cb-gui-child-profile-kft-lifecycle.csv; output/tables/phase6cc-adb-child-home-activation.csv; output/tables/phase6gr-gui-systemui-profile-switch.csv`
- SHA-256: `d3ce7a38f3d1e3df35571880b922aaa22377f5efaea8a349e5520f2ae2fc06ad`
- Caller: GUI child/KFT provisioning
- Gate: supported Settings child creation plus authorized user lifecycle
- Identity/user scope: user10/11/12
- Sink: "Tahoe FreeTimeLauncherActivity became child HOME priority 975; Fire disabled per child; User 0 Fire priority 50 stayed independent"
- Effect: child state persisted until stop/switchback; stop child/switch User 0 recorded
- Confidence/status: **CONFIRMED_CHILD_ONLY** / `CONFIRMED_CHILD_ONLY`
- Scope: previous public Phase 9 corpus

## P7-RUNTIME-009
- Phase/surface: `7` / `existing runtime/workaround reconciliation`
- Source: `output/tables/phase6ay-kft-child-user-matrix.csv; findings/phase-6ay-kft-child-user-experiment.md`
- Evidence: `output/tables/phase6ay-kft-child-user-matrix.csv; findings/phase-6ay-kft-child-user-experiment.md`
- SHA-256: `2447acb2b9dac6f27b2ca32cdc0133d7629deb406a3d6141dd0e769ccf7be657`
- Caller: shell restricted child create/remove
- Gate: pm create-user --profileOf 0 --restricted then remove-user
- Identity/user scope: user10
- Sink: "User 10 created stopped/unstarted; User 0 HOME unchanged; removal succeeded; no direct KFT call observed"
- Effect: temporary and reversible; remove-user plus post-rollback guard
- Confidence/status: **CONFIRMED_NEGATIVE** / `CONFIRMED_NEGATIVE`
- Scope: previous public Phase 9 corpus

## P7-RUNTIME-010
- Phase/surface: `7` / `existing runtime/workaround reconciliation`
- Source: `output/tables/phase6ck-child-third-party-home-boundary.csv; output/tables/phase6fy-kft-user10-third-party-home.csv`
- Evidence: `output/tables/phase6ck-child-third-party-home-boundary.csv; output/tables/phase6fy-kft-user10-third-party-home.csv`
- SHA-256: `8732d7a6f3f9a343c3768d0e040e569d5c2ba95971a48cc31b62d0f5ef2133b3`
- Caller: third-party HOME inside KFT child
- Gate: install-existing Microsoft; set-home-activity; switch child
- Identity/user scope: user10/12
- Sink: "Microsoft candidate priority 0 did not displace Tahoe priority 975; Tahoe remained foreground; parent User 0 Fire unchanged"
- Effect: per-user state during child run; uninstall/stop/switchback recorded
- Confidence/status: **CONFIRMED_NEGATIVE** / `CONFIRMED_NEGATIVE`
- Scope: previous public Phase 9 corpus

## P7-RUNTIME-011
- Phase/surface: `7` / `existing runtime/workaround reconciliation`
- Source: `output/tables/phase6gr-gui-systemui-profile-switch.csv; findings/phase-6ih-child-kft-evidence-closure.md`
- Evidence: `output/tables/phase6gr-gui-systemui-profile-switch.csv; findings/phase-6ih-child-kft-evidence-closure.md`
- SHA-256: `39b5e4ad80099d7ff037a832e044f814f5b38b526678c4790907beb8206dcd9c`
- Caller: SystemUI/profile switch
- Gate: supported SystemUI picker / public switch-user
- Identity/user scope: user0↔child
- Sink: "Switch to child selects Tahoe; return to owner selects Fire; no HOME writer observed"
- Effect: active-user dependent; stop child and return User 0 recorded
- Confidence/status: **CONFIRMED_CHILD_ONLY** / `CONFIRMED_CHILD_ONLY`
- Scope: previous public Phase 9 corpus

## P7-RUNTIME-012
- Phase/surface: `7` / `existing runtime/workaround reconciliation`
- Source: `output/tables/phase6cx-adb-accessibility-foreground-redirect.csv; output/tables/phase6cy-clean-reboot-home.csv; adb/phase6cy/PHASE6CY-MS-ACCESSIBILITY-20260806-15-CLEAN-REBOOT/metadata.json`
- Evidence: `output/tables/phase6cx-adb-accessibility-foreground-redirect.csv; output/tables/phase6cy-clean-reboot-home.csv; adb/phase6cy/PHASE6CY-MS-ACCESSIBILITY-20260806-15-CLEAN-REBOOT/metadata.json`
- SHA-256: `80afbf76e424ecbdb747ccff83464dfd30773df96b0adc94cb62631acee004fe`
- Caller: Accessibility explicit foreground redirect
- Gate: enabled research Accessibility service; explicit Fire event/launch handling
- Identity/user scope: user0
- Sink: "Microsoft/alias reached foreground after Fire launch events; HOME resolver stayed Fire priority 50; package/HOME state unchanged"
- Effect: reboot rebind confirmed for one variant; USB/ADB independence not proven; disable/remove research packages and restore Fire recorded
- Confidence/status: **CONFIRMED_WORKAROUND_WITH_SCOPE** / `CONFIRMED_WORKAROUND_WITH_SCOPE`
- Scope: previous public Phase 9 corpus

## P7-RUNTIME-013
- Phase/surface: `7` / `existing runtime/workaround reconciliation`
- Source: `findings/phase-6ig-accessibility-consume-home-closure.md; adb/phase6cy/PHASE6CY-CONSUME-HOME-20260807-02/metadata.json`
- Evidence: `findings/phase-6ig-accessibility-consume-home-closure.md; adb/phase6cy/PHASE6CY-CONSUME-HOME-20260807-02/metadata.json`
- SHA-256: `2447acb2b9dac6f27b2ca32cdc0133d7629deb406a3d6141dd0e769ccf7be657`
- Caller: Accessibility HOME consume attempt
- Gate: Accessibility service configured to consume HOME
- Identity/user scope: user0
- Sink: "0/3 Microsoft final foreground; Fire started 3/3; service did not intercept system HOME on this build"
- Effect: not applicable; rollback recorded
- Confidence/status: **CONFIRMED_NEGATIVE** / `CONFIRMED_NEGATIVE`
- Scope: previous public Phase 9 corpus

## P7-RUNTIME-014
- Phase/surface: `7` / `existing runtime/workaround reconciliation`
- Source: `findings/phase-6at-adb-home-monitor.md; adb/phase6at/PHASE6AT-ADB-HOME-MONITOR-PS7331-T02/`
- Evidence: `findings/phase-6at-adb-home-monitor.md; adb/phase6at/PHASE6AT-ADB-HOME-MONITOR-PS7331-T02/`
- SHA-256: `2447acb2b9dac6f27b2ca32cdc0133d7629deb406a3d6141dd0e769ccf7be657`
- Caller: ADB foreground monitor
- Gate: host monitor sends HOME then explicit research Activity
- Identity/user scope: user0
- Sink: "30/30 final foreground samples were research Activity after Fire HOME event; resolver remained Fire; requires active ADB monitor"
- Effect: not established after disconnect/process death/reboot; monitor stopped and normal HOME restore recorded
- Confidence/status: **CONFIRMED_TEMPORARY_WORKAROUND** / `CONFIRMED_TEMPORARY_WORKAROUND`
- Scope: previous public Phase 9 corpus

## P7-RUNTIME-015
- Phase/surface: `7` / `existing runtime/workaround reconciliation`
- Source: `output/tables/phase6ew-amazon-activity-foreground-spoof.csv; findings/phase-6ew-amazon-activity-foreground-spoof.md`
- Evidence: `output/tables/phase6ew-amazon-activity-foreground-spoof.csv; findings/phase-6ew-amazon-activity-foreground-spoof.md`
- SHA-256: `2447acb2b9dac6f27b2ca32cdc0133d7629deb406a3d6141dd0e769ccf7be657`
- Caller: Amazon activity foreground spoof
- Gate: accepted tx7 onActivityResume fake neutral component
- Identity/user scope: user0
- Sink: In-memory observer event accepted, but no HOME/PMS/KFT writer or launcher replacement observed; real Fire start restored
- Effect: temporary in-memory probe; APK removal and Fire start recorded
- Confidence/status: **CONFIRMED_NON_HOME_BOUNDARY** / `CONFIRMED_NON_HOME_BOUNDARY`
- Scope: previous public Phase 9 corpus

## P7-RUNTIME-016
- Phase/surface: `7` / `existing runtime/workaround reconciliation`
- Source: `output/tables/phase6ec-kft-tx3-reachability.csv; output/tables/phase6mv-runtime-summary-20260810-02.csv`
- Evidence: `output/tables/phase6ec-kft-tx3-reachability.csv; output/tables/phase6mv-runtime-summary-20260810-02.csv`
- SHA-256: `2447acb2b9dac6f27b2ca32cdc0133d7629deb406a3d6141dd0e769ccf7be657`
- Caller: private Amazon/KFT service reachability
- Gate: service list/check only; no transaction
- Identity/user scope: user0/child
- Sink: Names may appear in service list, but shell service check returned not found/SELinux find denial; no KFT tx3 dispatch
- Effect: not tested; not applicable
- Confidence/status: **CONFIRMED_SHELL_BLOCKED** / `CONFIRMED_SHELL_BLOCKED`
- Scope: previous public Phase 9 corpus

## P7-RUNTIME-017
- Phase/surface: `7` / `existing runtime/workaround reconciliation`
- Source: `output/tables/phase6gu-boot-after-system-ota.csv; output/tables/phase6m-oobe-control-surface.csv; output/tables/phase6r-oobe-authorization-matrix.csv`
- Evidence: `output/tables/phase6gu-boot-after-system-ota.csv; output/tables/phase6m-oobe-control-surface.csv; output/tables/phase6r-oobe-authorization-matrix.csv`
- SHA-256: `2447acb2b9dac6f27b2ca32cdc0133d7629deb406a3d6141dd0e769ccf7be657`
- Caller: OOBE post-system-OTA route
- Gate: none; static audit and read-only package state
- Identity/user scope: user0/child
- Sink: "boot phase 550/isUpgrade guarded broadcast can enable OobeHomeActivity and alter setup state; OOBE component disabled in captured runtime; no action replay"
- Effect: not tested; natural OTA only; not applicable
- Confidence/status: **UNTESTED_HIGH_IMPACT** / `UNTESTED_HIGH_IMPACT`
- Scope: previous public Phase 9 corpus

## P7-RUNTIME-018
- Phase/surface: `7` / `existing runtime/workaround reconciliation`
- Source: `output/tables/phase6n-ota-post-install-audit.csv; findings/phase-6z-boot-after-system-ota-follow-up.md`
- Evidence: `output/tables/phase6n-ota-post-install-audit.csv; findings/phase-6z-boot-after-system-ota-follow-up.md`
- SHA-256: `2447acb2b9dac6f27b2ca32cdc0133d7629deb406a3d6141dd0e769ccf7be657`
- Caller: OTA staging/post-install
- Gate: none; static source/control audit
- Identity/user scope: user0/child
- Sink: "Verification/staging/update handoff is high-impact lifecycle; no HOME setter or executed OTA evidence"
- Effect: not tested; not applicable
- Confidence/status: **UNTESTED_HIGH_IMPACT** / `UNTESTED_HIGH_IMPACT`
- Scope: previous public Phase 9 corpus

## P7-WATCHDOG-001
- Phase/surface: `7` / `Amazon package-state/HOME watchdog`
- Source: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:33627-33718 (class/method and setPackage Fire literal; 031350-0313b0 loops running users and broadcasts)`
- Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:33627-33718 (class/method and setPackage Fire literal; 031350-0313b0 loops running users and broadcasts)`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: MigrationService lifecycle caller; private method
- Gate: appsAvailable receives availability boolean; no shell/exported entry shown
- Identity/user scope: system_server/Amazon MigrationService; running user IDs returned by getRunningUserIds()
- Sink: com.amazon.firelauncher; IActivityManager.broadcastIntent
- Effect: package-scoped EXTERNAL_APPLICATIONS_AVAILABLE/UNAVAILABLE notification with changed package list; no package-state/HOME write
- Confidence/status: **static capability** / `static capability`
- Scope: previous public Phase 9 corpus

## P7-WATCHDOG-002
- Phase/surface: `7` / `Amazon package-state/HOME watchdog`
- Source: `artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv:5-6 and disassembly.log:54297-54434`
- Evidence: `artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv:5-6 and disassembly.log:54297-54434`
- SHA-256: `39ce24194ecead7109894d6bae3cfcf631118c9181ec446dc70a6dd3354f231a; ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: tryEnableKftLauncherComponent and child/profile lifecycle
- Gate: UserInfo.id is supplied; nearby flow requires KFT admin/profile-owner setup
- Identity/user scope: system_server AmazonUserManagerService; child/profile user only (UserInfo.id)
- Sink: com.amazon.firelauncher; AmazonPackageManager.setApplicationEnabledSetting
- Effect: Fire application state is enabled/disabled alongside Tahoe FreeTime launcher for KFT child user; no HOME preferred write
- Confidence/status: **duplicate** / `duplicate`
- Scope: previous public Phase 9 corpus

## P7-WATCHDOG-003
- Phase/surface: `7` / `Amazon package-state/HOME watchdog`
- Source: `artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv:4 and disassembly.log:54300-54312`
- Evidence: `artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv:4 and disassembly.log:54300-54312`
- SHA-256: `39ce24194ecead7109894d6bae3cfcf631118c9181ec446dc70a6dd3354f231a; ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: same KFT path
- Gate: child/profile lifecycle plus profile-owner/admin setup
- Identity/user scope: system_server AmazonUserManagerService; child/profile user only (UserInfo.id)
- Sink: com.amazon.tahoe.launcher.FreeTimeLauncherActivity; AmazonPackageManager.setComponentEnabledSetting
- Effect: Tahoe FreeTime component enabled for child user; paired with Fire package state but not a Fire HOME writer
- Confidence/status: **duplicate** / `duplicate`
- Scope: previous public Phase 9 corpus

## P7-WATCHDOG-004
- Phase/surface: `7` / `Amazon package-state/HOME watchdog`
- Source: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:136888-136954 (getPackagesForUid/getCallingUserId/getApplicationInfo and gates)`
- Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:136888-136954 (getPackagesForUid/getCallingUserId/getApplicationInfo and gates)`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: system-server callback invoked by ActivityStack path
- Gate: ApplicationInfo lookup by supplied UID; allow if SELinux amazon_policies:see_home_task or package signature matches android
- Identity/user scope: system_server callback context; caller UID/user implied by package lookup
- Sink: caller application (not Fire-specific); boolean callback return
- Effect: permits/denies visibility of HOME task only; no package state or preferred write
- Confidence/status: **static capability** / `static capability`
- Scope: previous public Phase 9 corpus

## P7-WATCHDOG-005
- Phase/surface: `7` / `Amazon package-state/HOME watchdog`
- Source: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:136954-137013`
- Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:136954-137013`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: system-server PackageManager callback
- Gate: tracked package/user pair and userId >= 0; only packages recorded by PermissionManager callback
- Identity/user scope: system_server callback; recorded package/user pairs
- Sink: tracked package; PackageManager.revokeRuntimePermission
- Effect: revokes READ_LOGS on shutdown; does not hide/suspend/disable Fire or write HOME state
- Confidence/status: **static capability** / `static capability`
- Scope: previous public Phase 9 corpus

## P7-WATCHDOG-006
- Phase/surface: `7` / `Amazon package-state/HOME watchdog`
- Source: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:97240-97345 and 97304-97330; artifacts/phase6ap/consumer-snippet-20260805-01/fosservices-denylist-consumer.snippet.txt`
- Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:97240-97345 and 97304-97330; artifacts/phase6ap/consumer-snippet-20260805-01/fosservices-denylist-consumer.snippet.txt`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c; 860e30444f8c23a5e990e1b0f5ed0ff0feb330436d9e2f222aa7ea49d2e0be78`
- Caller: DenyListArcusHelper constructor during trusted PM service setup
- Gate: first-run SharedPreferences absence causes resource JSON import; initialize requires non-empty persist.sys.denylist_arcusid resource/property value
- Identity/user scope: system_server Amazon PM service; device-protected shared preference/global property scope
- Sink: configured deny-list packages; SharedPreferences.Editor.putStringSet/commit and SystemProperties.get then ArcusFwkManager.register/syncId
- Effect: stores deny-list metadata and registers Arcus sync; no observed enable/disable/hidden/suspend/preferred/HOME write
- Confidence/status: **bounded negative** / `bounded negative`
- Scope: previous public Phase 9 corpus

## P7-WATCHDOG-007
- Phase/surface: `7` / `Amazon package-state/HOME watchdog`
- Source: `artifacts/phase6ap/denylist-resource-closure-20260805-01/res/raw/package_manager_deny_list.json and disassembly.log:97280-97302`
- Evidence: `artifacts/phase6ap/denylist-resource-closure-20260805-01/res/raw/package_manager_deny_list.json and disassembly.log:97280-97302`
- SHA-256: `16086fecbfce0a20c0b37535e25d690635d398b30d582fa6d231736dc9bdf710; ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: system-server PM helper initialization
- Gate: resource package_manager_deny_list JSON parsed from preserved resource; no caller-controlled file path
- Identity/user scope: system_server Amazon PM helper; device/resource scope
- Sink: packages_deny_list entries; resource InputStream read plus saveProtectedPackages
- Effect: build/config deny-list only; no HOME/package-state writer
- Confidence/status: **static capability** / `static capability`
- Scope: previous public Phase 9 corpus

## P7-WATCHDOG-008
- Phase/surface: `7` / `Amazon package-state/HOME watchdog`
- Source: `artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv:13-14 and findings/phase-6fw-framework-home-provenance-closure.md`
- Evidence: `artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv:13-14 and findings/phase-6fw-framework-home-provenance-closure.md`
- SHA-256: `39ce24194ecead7109894d6bae3cfcf631118c9181ec446dc70a6dd3354f231a`
- Caller: adb shell command path
- Gate: standard PMS caller/permission/protected-package gates; --user is caller-supplied but not bypass
- Identity/user scope: com.android.shell; explicit --user scope
- Sink: requested package/component; IPackageManager.setApplicationEnabledSetting/setComponentEnabledSetting/setHomeActivity
- Effect: standard shell-writable interface exists but protected PMS/HOME semantics remain; no new Fire-specific watchdog caller
- Confidence/status: **duplicate** / `duplicate`
- Scope: previous public Phase 9 corpus

## P8-PREWARM-001
- Phase/surface: `8` / `prewarm caller/user-scope closure`
- Source: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40534; decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:3642543-3642624; artifacts/phase6x/prewarm-authorization-20260805-05/com_amazon_permission_APP_PREWARM.block.txt:1-5`
- Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40534; decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:3642543-3642624; artifacts/phase6x/prewarm-authorization-20260805-05/com_amazon_permission_APP_PREWARM.block.txt:1-5`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;04d68d0bb562a14e9cbff3bdce63b66eb911ee4bb7e728ca77cd435a5b03c146;4a71d4d60cdb6c45233e270e3548f02c9ea77e9d3b3b4ed33a7aeb1e130bb798`
- Caller: Remote Binder entry; implementation-side caller UID is the incoming Binder identity; no caller package/UID read is shown before clear
- Gate: Context.checkCallingPermission(com.amazon.permission.APP_PREWARM); result is not moved/compared and no denial branch is present before clearCallingIdentity
- Identity/user scope: Incoming Binder identity exists at permission check; clearCallingIdentity at FOS 0x036f5c / OTA 0x037004; restoreCallingIdentity at FOS 0x03702a / OTA 0x0370d2
- Sink: IPackageManager.getApplicationInfo(package,1024,user) -> PreWarmCacheHelper.getKeepIfLargeValue -> ActivityManagerService.startProcessLocked(...,'prewarm',...)
- Effect: Process/resource prewarm only; no HOME selector, preferred-activity, package/component-state, settings, root, or privilege-grant sink
- Confidence/status: **confirmed-static; authorization-result defect candidate; not by itself a vulnerability claim** / `confirmed-static; authorization-result defect candidate; not by itself a vulnerability claim`
- Scope: previous public Phase 9 corpus

## P8-PREWARM-002
- Phase/surface: `8` / `prewarm caller/user-scope closure`
- Source: `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:553272-553277,553433-553440; decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:4464666-4464696; findings/phase-6er-amazon-prewarm-confused-deputy.md:38-47`
- Evidence: `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:553272-553277,553433-553440; decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:4464666-4464696; findings/phase-6er-amazon-prewarm-confused-deputy.md:38-47`
- SHA-256: `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71;04d68d0bb562a14e9cbff3bdce63b66eb911ee4bb7e728ca77cd435a5b03c146`
- Caller: AmazonActivityManagerImpl framework wrapper; Proxy writes String + int + int and calls IBinder.transact(code=1); no caller-side permission gate in proxy
- Gate: No proxy-side APP_PREWARM enforcement; server-side check is P8A-001
- Identity/user scope: Caller identity is carried unchanged over Binder to server until server clearCallingIdentity
- Sink: IBinder.transact(1) -> Stub.onTransact -> BinderService.preWarmApplicationForUser
- Effect: Exact bind/transaction contract recovered; publication does not imply arbitrary caller reachability
- Confidence/status: **confirmed-static; ordinary-app reachability requires separate runtime evidence** / `confirmed-static; ordinary-app reachability requires separate runtime evidence`
- Scope: previous public Phase 9 corpus

## P8-PREWARM-003
- Phase/surface: `8` / `prewarm caller/user-scope closure`
- Source: `artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/sources/amazon/speech/sim/router/intentrouter/ExplicitIntentAction.java:268-282; .../resources/AndroidManifest.xml:146-148; .../pm-path.stdout.txt:1`
- Evidence: `artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/sources/amazon/speech/sim/router/intentrouter/ExplicitIntentAction.java:268-282; .../resources/AndroidManifest.xml:146-148; .../pm-path.stdout.txt:1`
- SHA-256: `c1a8bcfc0952239a26b669f7bc227fcc01024ac5db26db7e6eed2ae5cb6a2dc2;cc0a7b0df71c627ce09849b573e44491db3c715d365b631e3325d28623638f0d;b26d2a7083c743893fc2dc382b2cf276c0dbe268517dac76039e3267d318d88b`
- Caller: com.amazon.alexa.multimodal.gemini; target non-null, manager non-null, self-package target excluded; only direct source caller found in retained JADX corpus
- Gate: Manifest requests com.amazon.permission.APP_PREWARM and amazon.speech.permission.SEND_DATA_TO_ALEXA; APP_PREWARM effective grant is not separately enumerated
- Identity/user scope: Alexa package identity is preserved through Proxy; server clears identity before package/process work
- Sink: Alexa wrapper -> AmazonActivityManagerImpl -> Proxy tx1 -> server prewarm sink
- Effect: trusted internal caller path statically exact; not evidence that all Amazon packages or ordinary apps hold permission
- Confidence/status: **confirmed-static-caller; grant/user edge incomplete** / `confirmed-static-caller; grant/user edge incomplete`
- Scope: previous public Phase 9 corpus

## P8-PREWARM-004
- Phase/surface: `8` / `prewarm caller/user-scope closure`
- Source: `artifacts/phase6x/prewarm-authorization-20260805-05/com_amazon_permission_APP_PREWARM.block.txt:1-5; artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/manifest.txt:146-148; work/luna_worker_prewarm_identity_closure_20260810.csv:1-3`
- Evidence: `artifacts/phase6x/prewarm-authorization-20260805-05/com_amazon_permission_APP_PREWARM.block.txt:1-5; artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/manifest.txt:146-148; work/luna_worker_prewarm_identity_closure_20260810.csv:1-3`
- SHA-256: `4a71d4d60cdb6c45233e270e3548f02c9ea77e9d3b3b4ed33a7aeb1e130bb798;cc0a7b0df71c627ce09849b573e44491db3c715d365b631e3325d28623638f0d;65ad3f10ed3fe2186d5a69e1fe67a2ff86ac9b41d9c39ea66cee05a9c5011b1e`
- Caller: Requester 1: Alexa manifest declares APP_PREWARM; requester 2: ordinary Phase6ER probe declares no permissions; no other exact requester found in retained source/manifest search
- Gate: com.amazon.permission.APP_PREWARM
- Identity/user scope: Permission is evaluated against incoming Binder caller before identity clear; no post-clear UID check
- Sink: Permission gate precedes the same process-prewarm sink; no permission consumer after the check is visible
- Effect: Ordinary caller can still reach the sink in the saved Phase6ER runtime evidence; this is the key distinction from treating an unconsumed result alone as a vulnerability
- Confidence/status: **partial-closure; holder positive, grant and full requester universe incomplete** / `partial-closure; holder positive, grant and full requester universe incomplete`
- Scope: previous public Phase 9 corpus

## P8-PREWARM-005
- Phase/surface: `8` / `prewarm caller/user-scope closure`
- Source: `adb/phase6er/PHASE6ER-UNTRUSTED-SERVICE-LOOKUP-20260806-134346/result.json; findings/phase-6er-amazon-prewarm-confused-deputy.md:15-35,98-109`
- Evidence: `adb/phase6er/PHASE6ER-UNTRUSTED-SERVICE-LOOKUP-20260806-134346/result.json; findings/phase-6er-amazon-prewarm-confused-deputy.md:15-35,98-109`
- SHA-256: `230a59769bfed7ede022259295c2f034c05a5f044a8da8115b2ac1caacda49ae;230a59769bfed7ede022259295c2f034c05a5f044a8da8115b2ac1caacda49ae`
- Caller: Ordinary APK, no declared permissions, UID 10198; saved result records handle=true and prewarm transact=true/result=0
- Gate: Probe had no APP_PREWARM declaration; no denial blocked tx1 in saved result
- Identity/user scope: Incoming ordinary Binder UID 10198 is visible to checkCallingPermission; server then clears identity and restores it
- Sink: Target process appeared after tx1; saved result records target PID and process record; HOME and Fire package state remained unchanged
- Effect: Confirmed ordinary-app process/resource prewarm confused deputy; no HOME/package/settings/root effect
- Confidence/status: **confirmed-ordinary-app-reachable; process-only effect** / `confirmed-ordinary-app-reachable; process-only effect`
- Scope: previous public Phase 9 corpus

## P8-PREWARM-006
- Phase/surface: `8` / `prewarm caller/user-scope closure`
- Source: `artifacts/phase6aq/public-summary-20260805-02/amazon-service-avc.txt:6-118; artifacts/phase6x/prewarm-authorization-20260805-05/prewarm-authorization-evidence.csv:10`
- Evidence: `artifacts/phase6aq/public-summary-20260805-02/amazon-service-avc.txt:6-118; artifacts/phase6x/prewarm-authorization-20260805-05/prewarm-authorization-evidence.csv:10`
- SHA-256: `d436542564947472c1b2481519312542d7d1053512b9cb47c68abbb981e0b0a4;53cbf5d5e873de56b7efee4918ba0b95f5968bf824e665842a5d1f4860ddb5cb`
- Caller: Shell UID 2000 / u:r:shell:s0; no service handle acquired in saved enforcing capture
- Gate: APP_PREWARM is not reached; service-manager find is denied before Binder method entry
- Identity/user scope: No Binder calling UID reaches the method because service lookup is denied
- Sink: No sink/effect; no shell dispatch evidence
- Effect: Shell route closed for the saved enforcing policy only; not universal across other domains/builds
- Confidence/status: **bounded-negative-shell; no exploit inference** / `bounded-negative-shell; no exploit inference`
- Scope: previous public Phase 9 corpus

## P8-PREWARM-007
- Phase/surface: `8` / `prewarm caller/user-scope closure`
- Source: `work/luna_worker_phase7b_ipc_residual_20260810.csv:P7B-001; findings/phase-6er-amazon-prewarm-confused-deputy.md:1-10; work/luna_worker_phase6_private_client_universe_20260810.md:89-91`
- Evidence: `work/luna_worker_phase7b_ipc_residual_20260810.csv:P7B-001; findings/phase-6er-amazon-prewarm-confused-deputy.md:1-10; work/luna_worker_phase6_private_client_universe_20260810.md:89-91`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;230a59769bfed7ede022259295c2f034c05a5f044a8da8115b2ac1caacda49ae;65ad3f10ed3fe2186d5a69e1fe67a2ff86ac9b41d9c39ea66cee05a9c5011b1e`
- Caller: P7B-001 caller was previously marked unknown; Phase6ER supplies an accepted ordinary caller, while Alexa remains the only direct retained JADX caller
- Gate: APP_PREWARM check-result defect is real in code; permission holder is known; effective caller grant and method-level denial semantics remain separate edges
- Identity/user scope: Pre-clear incoming UID is consumed only by checkCallingPermission; after clear, downstream calls run as system identity; restore exists on normal/exception paths
- Sink: Only downstream stateful sink is process start; no recovered HOME/PMS preferred/component writer
- Effect: Closure must distinguish confirmed ordinary-app process prewarm from unproven HOME/privilege escalation; ignored result alone is not the finding once runtime effect is independently evidenced
- Confidence/status: **reconciled-P7B-001; ordinary-app reachable; shell bounded-negative; HOME/root not established** / `reconciled-P7B-001; ordinary-app reachable; shell bounded-negative; HOME/root not established`
- Scope: previous public Phase 9 corpus

## P8-KFT-001
- Phase/surface: `8` / `KFT tx3 caller/user-scope closure`
- Source: `boot-fosframework/disassembly.log:369180-369243; 370398-370443`
- Evidence: `boot-fosframework/disassembly.log:369180-369243; 370398-370443`
- SHA-256: `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`
- Caller: AmazonUserManagerImpl.createChildUser(String)
- Gate: createUser(name;0x8000) returns child UserInfo; client package UID signature not recovered
- Identity/user scope: none at Proxy; caller identity carried into service
- Sink: optional UserInfo parcel; IBinder.transact(3) to enableKftLauncher
- Effect: boolean tx3 dispatch
- Confidence/status: **CONFIRMED** / `CONFIRMED`
- Scope: previous public Phase 9 corpus

## P8-KFT-002
- Phase/surface: `8` / `KFT tx3 caller/user-scope closure`
- Source: `boot-fosframework/disassembly.log:370674-370777; 371789-371861`
- Evidence: `boot-fosframework/disassembly.log:370674-370777; 371789-371861`
- SHA-256: `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`
- Caller: external transacted caller not recovered; internal client is createChildUser
- Gate: interface token only; no method-local UID MANAGE_USERS or cross-user check visible
- Identity/user scope: transacted Binder identity retained; no tx3 clearCallingIdentity
- Sink: dispatch to enableKftLauncher(UserInfo); nullable UserInfo unmarshaled and dispatched
- Effect: tx3 reaches service method
- Confidence/status: **CONFIRMED_STATIC_GATE_GAP** / `CONFIRMED_STATIC_GATE_GAP`
- Scope: previous public Phase 9 corpus

## P8-KFT-003
- Phase/surface: `8` / `KFT tx3 caller/user-scope closure`
- Source: `fosservices/disassembly.log:54415-54478; 54847-54895; work/luna_worker_phase6ub_kft_caller_scope_20260810.md; work/luna_worker_phase6uf_kft_gate_20260810.md`
- Evidence: `fosservices/disassembly.log:54415-54478; 54847-54895; work/luna_worker_phase6ub_kft_caller_scope_20260810.md; work/luna_worker_phase6uf_kft_gate_20260810.md`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;985baf87524b8c11746268ee861e430e9fc5ac26594268107cbc9f2dc4f858c4;04cb8f5c74966ad94c0dbdf9de3dc60b03f5c349632321a92e7e6b6f20d2075b`
- Caller: AmazonUserManagerImpl.createChildUser(String) via Proxy; onBootPhase is local not tx3
- Gate: tx3-local checkManageUsersPermission call not found; separate helper allows UID 0/1000 or MANAGE_USERS but tx3 edge unjoined
- Identity/user scope: no identity transition at bounded entry; later DPM branch clears/restores identity
- Sink: tryEnableKftLauncherComponent(UserInfo); KFT writer and downstream profile-owner/DPM work
- Effect: invokes KFT path and downstream profile-owner/DPM work
- Confidence/status: **PARTIALLY_CLOSED_AUTHZ** / `PARTIALLY_CLOSED_AUTHZ`
- Scope: previous public Phase 9 corpus

## P8-KFT-004
- Phase/surface: `8` / `KFT tx3 caller/user-scope closure`
- Source: `fosservices/disassembly.log:55053-55119; work/luna_worker_phase6uf_kft_gate_20260810.md`
- Evidence: `fosservices/disassembly.log:55053-55119; work/luna_worker_phase6uf_kft_gate_20260810.md`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;04cb8f5c74966ad94c0dbdf9de3dc60b03f5c349632321a92e7e6b6f20d2075b`
- Caller: AmazonUserManagerService system-server lifecycle
- Gate: phase 500 AND isUpgrade AND isChildUser(UserInfo); then local enableKftLauncher plus tx4
- Identity/user scope: not Binder; system-server local identity
- Sink: each genuine child/profile entry; local enableKftLauncher(UserInfo)
- Effect: upgrade-time KFT package/component state
- Confidence/status: **CONFIRMED_INTERNAL_CHILD_ONLY** / `CONFIRMED_INTERNAL_CHILD_ONLY`
- Scope: previous public Phase 9 corpus

## P8-KFT-005
- Phase/surface: `8` / `KFT tx3 caller/user-scope closure`
- Source: `fosservices/disassembly.log:54297-54312; artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv:4`
- Evidence: `fosservices/disassembly.log:54297-54312; artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv:4`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;6fe2fa8a27fd2e753fb34f7fd162f051ab9bae6d0667290d4f2af8fef40e1503`
- Caller: AmazonUserManagerService BinderService
- Gate: gate inherited; no local UID or cross-user check visible
- Identity/user scope: tx3 entry has no clearCallingIdentity; package calls are system-side
- Sink: com.amazon.tahoe/.launcher.FreeTimeLauncherActivity; AmazonPackageManager.setComponentEnabledSetting(...;userId)
- Effect: Tahoe FreeTime launcher enabled for supplied child/profile
- Confidence/status: **CONFIRMED_CHILD_PROFILE_WRITER** / `CONFIRMED_CHILD_PROFILE_WRITER`
- Scope: previous public Phase 9 corpus

## P8-KFT-006
- Phase/surface: `8` / `KFT tx3 caller/user-scope closure`
- Source: `fosservices/disassembly.log:54311-54318; artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv:5`
- Evidence: `fosservices/disassembly.log:54311-54318; artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv:5`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;6fe2fa8a27fd2e753fb34f7fd162f051ab9bae6d0667290d4f2af8fef40e1503`
- Caller: AmazonUserManagerService BinderService
- Gate: gate inherited; no local UID or cross-user check visible
- Identity/user scope: tx3 entry has no clearCallingIdentity; package calls are system-side
- Sink: com.amazon.firelauncher; AmazonPackageManager.setApplicationEnabledSetting(...;userId)
- Effect: Fire Launcher disabled for supplied child/profile
- Confidence/status: **CONFIRMED_CHILD_PROFILE_WRITER** / `CONFIRMED_CHILD_PROFILE_WRITER`
- Scope: previous public Phase 9 corpus

## P8-KFT-007
- Phase/surface: `8` / `KFT tx3 caller/user-scope closure`
- Source: `fosservices/disassembly.log:54319-54325; artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv:6`
- Evidence: `fosservices/disassembly.log:54319-54325; artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv:6`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;6fe2fa8a27fd2e753fb34f7fd162f051ab9bae6d0667290d4f2af8fef40e1503`
- Caller: AmazonUserManagerService BinderService
- Gate: gate inherited; no local UID or cross-user check visible
- Identity/user scope: tx3 entry has no clearCallingIdentity; package calls are system-side
- Sink: com.android.launcher3; AmazonPackageManager.setApplicationEnabledSetting(...;userId)
- Effect: Launcher3 disabled for supplied child/profile
- Confidence/status: **CONFIRMED_CHILD_PROFILE_WRITER** / `CONFIRMED_CHILD_PROFILE_WRITER`
- Scope: previous public Phase 9 corpus

## P8-KFT-008
- Phase/surface: `8` / `KFT tx3 caller/user-scope closure`
- Source: `fosservices/disassembly.log:54894-54899; 55106-55119; device/fireos-config/CONFIG-20260803-02/paths/find_init_xml__system_fireos_etc_init.txt:49; adb/phase6cz/PHASE6CZ-KFT-PROVENANCE-20260806-01/audit_logcat.stdout.txt:82`
- Evidence: `fosservices/disassembly.log:54894-54899; 55106-55119; device/fireos-config/CONFIG-20260803-02/paths/find_init_xml__system_fireos_etc_init.txt:49; adb/phase6cz/PHASE6CZ-KFT-PROVENANCE-20260806-01/audit_logcat.stdout.txt:82`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;bbb8b23472b52720dd4ad2cba0ce327f8c528af2c29ad60f78b0f8793de6ff7f`
- Caller: AmazonUserManagerService.onStart and BinderService
- Gate: private service publication; no recovered service declaration permission tied to tx3
- Identity/user scope: system_server publishes private Binder under Amazon service context
- Sink: amazonusermanagerservice; ServiceManager publication plus SELinux service_manager boundary
- Effect: private service trusted path; shell blocked before tx3
- Confidence/status: **SAVED_RUNTIME_BOUNDARY** / `SAVED_RUNTIME_BOUNDARY`
- Scope: previous public Phase 9 corpus

## P8-KFT-009
- Phase/surface: `8` / `KFT tx3 caller/user-scope closure`
- Source: `output/tables/phase7-control-surface.csv:259-263; adb/phase6gr/PHASE6GR-GUI-SYSTEMUI-SWITCH-20260807-02/sha256sums.txt; work/luna_worker_phase6ub_kft_caller_scope_20260810.md`
- Evidence: `output/tables/phase7-control-surface.csv:259-263; adb/phase6gr/PHASE6GR-GUI-SYSTEMUI-SWITCH-20260807-02/sha256sums.txt; work/luna_worker_phase6ub_kft_caller_scope_20260810.md`
- SHA-256: `1d10e729806a748b77b52ce88449a9c0fa20315faa84e55948e30be16fb1dda8;08c9737cb9c9d902d0b7ef5d25d4fa46f22c7017874555ef38ae28e7d67b6d3a;985baf87524b8c11746268ee861e430e9fc5ac26594268107cbc9f2dc4f858c4`
- Caller: N/A no transaction sent
- Gate: GUI/SystemUI child lifecycle; no private Binder replay
- Identity/user scope: child Tahoe HOME while parent User 0 Fire remains independent; no tx3 attribution
- Sink: child User 10/11/12 versus User 0 owner; child Tahoe HOME and parent Fire HOME
- Effect: existing capture only; no fresh tx3 claim
- Confidence/status: **CONFIRMED_SCOPE_SEPARATION** / `CONFIRMED_SCOPE_SEPARATION`
- Scope: previous public Phase 9 corpus

## P8-SETTINGS-001
- Phase/surface: `8` / `SettingsProvider/HOME-key closure`
- Source: `SettingsProvider.java:344-418; :658-704`
- Evidence: `SettingsProvider.java:344-418; :658-704`
- SHA-256: `4efc2aba8f7798fb4e026f13479f5b4929ef545deba5618b35d799555d78678b`
- Caller: external ContentProvider caller unknown
- Gate: android.permission.WRITE_SECURE_SETTINGS
- Identity/user scope: UserHandle.getCallingUserId and Binder.getCallingUid; no clearCallingIdentity before gate
- Sink: none to HOME; generic global settings only; SettingsRegistry insert/update/delete type=0 user=0
- Effect: global settings persistence
- Confidence/status: **static provider writer** / `static provider writer`
- Scope: previous public Phase 9 corpus

## P8-SETTINGS-002
- Phase/surface: `8` / `SettingsProvider/HOME-key closure`
- Source: `SettingsProvider.java:344-418; :718-777; :900-1015`
- Evidence: `SettingsProvider.java:344-418; :718-777; :900-1015`
- SHA-256: `4efc2aba8f7798fb4e026f13479f5b4929ef545deba5618b35d799555d78678b`
- Caller: external ContentProvider caller unknown
- Gate: android.permission.WRITE_SECURE_SETTINGS
- Identity/user scope: UserHandle.getCallingUserId and Binder.getCallingUid; identity retained through gate
- Sink: none to HOME; secure key mutation is not PMS mutation; SettingsRegistry insert/update/delete type=2 owningUserId
- Effect: per-user secure settings persistence
- Confidence/status: **static provider writer** / `static provider writer`
- Scope: previous public Phase 9 corpus

## P8-SETTINGS-003
- Phase/surface: `8` / `SettingsProvider/HOME-key closure`
- Source: `SettingsProvider.java:344-418; system mutation around :1015-1120`
- Evidence: `SettingsProvider.java:344-418; system mutation around :1015-1120`
- SHA-256: `4efc2aba8f7798fb4e026f13479f5b4929ef545deba5618b35d799555d78678b`
- Caller: external ContentProvider caller unknown
- Gate: WRITE_SETTINGS operation gate plus secure-settings fallback
- Identity/user scope: calling identity retained through authorization
- Sink: none to HOME; no preferred/component setter; SettingsRegistry insert/update/delete type=1 userId
- Effect: per-user system settings persistence
- Confidence/status: **bounded negative** / `bounded negative`
- Scope: previous public Phase 9 corpus

## P8-SETTINGS-004
- Phase/surface: `8` / `SettingsProvider/HOME-key closure`
- Source: `SettingsProvider.java:238-277; :658-676; getRequestingUserId`
- Evidence: `SettingsProvider.java:238-277; :658-676; getRequestingUserId`
- SHA-256: `4efc2aba8f7798fb4e026f13479f5b4929ef545deba5618b35d799555d78678b`
- Caller: framework/system caller unknown
- Gate: WRITE_SECURE_SETTINGS for global/secure; system operation gate
- Identity/user scope: Binder caller retained for permission and user checks
- Sink: none to HOME; call wraps provider mutation; SettingsProvider.call to insert/update helpers
- Effect: authorized settings mutation only; no PMS sink
- Confidence/status: **static provider writer** / `static provider writer`
- Scope: previous public Phase 9 corpus

## P8-SETTINGS-005
- Phase/surface: `8` / `SettingsProvider/HOME-key closure`
- Source: `phase6h ipc-findings.csv:14-15; FireOsSettingsStoreMapping.java`
- Evidence: `phase6h ipc-findings.csv:14-15; FireOsSettingsStoreMapping.java`
- SHA-256: `64c869e40c1919c8fdb27acac4e17c1f8e7291c3805188698f501fffe8ba6e00;0b464cd30a8d7f627261f809e1994e522c28c01a04399a8707a0426574ebf637`
- Caller: com.amazon.firelauncher mapping; exact downstream writer not fully joined
- Gate: WRITE_SECURE_SETTINGS in Fire Launcher manifest
- Identity/user scope: Fire Launcher package identity at writer; provider sees Binder caller
- Sink: HOME-adjacent card/rotation UI only; not HOME resolver; Settings.Global.CONTENT_URI
- Effect: changes home-card/rotation settings only
- Confidence/status: **static provider writer** / `static provider writer`
- Scope: previous public Phase 9 corpus

## P8-SETTINGS-006
- Phase/surface: `8` / `SettingsProvider/HOME-key closure`
- Source: `FireOsSettingsStoreMapping.java:38-39; Fire Launcher manifest:111-112`
- Evidence: `FireOsSettingsStoreMapping.java:38-39; Fire Launcher manifest:111-112`
- SHA-256: `64c869e40c1919c8fdb27acac4e17c1f8e7291c3805188698f501fffe8ba6e00;ba88dc674466a2c4561e7258586ca31f739e8527153d81dc6cd2a262a3f2fdab`
- Caller: com.amazon.firelauncher mapping
- Gate: WRITE_SECURE_SETTINGS
- Identity/user scope: Fire Launcher package identity; provider Binder identity
- Sink: HOME UI personalization only; not preferred HOME; Settings.Secure.CONTENT_URI
- Effect: launcher personalization settings only
- Confidence/status: **bounded negative** / `bounded negative`
- Scope: previous public Phase 9 corpus

## P8-SETTINGS-007
- Phase/surface: `8` / `SettingsProvider/HOME-key closure`
- Source: `settings resource followup; DefaultHomeShortcutPreferenceController.java:9`
- Evidence: `settings resource followup; DefaultHomeShortcutPreferenceController.java:9`
- SHA-256: `6d5e43ac80febad594ef8b8ee2bab7faceca2b17925a7cfe7032725d44601383`
- Caller: Settings DefaultHomeShortcutPreferenceController / DefaultHomePicker
- Gate: WRITE_SECURE_SETTINGS not established for provider route; picker uses PackageManager preferred API
- Identity/user scope: system Settings identity for PackageManager call
- Sink: HOME relevant but not a SettingsProvider key writer; PackageManager.replacePreferredActivity to PMS preferred XML
- Effect: preferred HOME record can persist; separate from SettingsProvider and may lose to Fire priority
- Confidence/status: **bounded negative** / `bounded negative`
- Scope: previous public Phase 9 corpus

## P8-SETTINGS-008
- Phase/surface: `8` / `SettingsProvider/HOME-key closure`
- Source: `settings-provider AndroidManifest.xml:25-32; SettingsProvider.java:238-418`
- Evidence: `settings-provider AndroidManifest.xml:25-32; SettingsProvider.java:238-418`
- SHA-256: `e4f2d9d47e7fa10be2aa2d26f6549b41184762d7ff5c77c19ffa7fc7560aac70;4efc2aba8f7798fb4e026f13479f5b4929ef545deba5618b35d799555d78678b`
- Caller: AMS/content-provider transport caller unknown
- Gate: provider exported=true; mutation authorization in provider
- Identity/user scope: AMS supplies Binder caller identity
- Sink: not HOME by itself; generic settings authority; SettingsProvider ContentProvider transport
- Effect: read/write/query/call surface subject to checks
- Confidence/status: **caller unknown** / `caller unknown`
- Scope: previous public Phase 9 corpus

## P8-SETTINGS-009
- Phase/surface: `8` / `SettingsProvider/HOME-key closure`
- Source: `phase6kv-pms-home-callers.csv:25; PMS.java:13120-13143; :13817-13838`
- Evidence: `phase6kv-pms-home-callers.csv:25; PMS.java:13120-13143; :13817-13838`
- SHA-256: `dc1a86ea85904e3775704944fa86364a9a89033f6146eed0dac8b324b7028382`
- Caller: framework callers enumerated separately; no SettingsProvider caller
- Gate: SET_PREFERRED_APPLICATIONS and cross-user permission in PMS
- Identity/user scope: PMS checks Binder.getCallingUid and cross-user permission
- Sink: direct preferred HOME sink; separate from SettingsProvider; PackageManagerService.setHomeActivity to replacePreferredActivity to preferred XML
- Effect: stored preferred HOME only; no provider bridge
- Confidence/status: **bounded negative** / `bounded negative`
- Scope: previous public Phase 9 corpus

## P8-SETTINGS-010
- Phase/surface: `8` / `SettingsProvider/HOME-key closure`
- Source: `phase6rs closure; settings home resource followup; phase6h ipc-findings.csv`
- Evidence: `phase6rs closure; settings home resource followup; phase6h ipc-findings.csv`
- SHA-256: `6d5e43ac80febad594ef8b8ee2bab7faceca2b17925a7cfe7032725d44601383;0b464cd30a8d7f627261f809e1994e522c28c01a04399a8707a0426574ebf637`
- Caller: unknown production caller set
- Gate: WRITE_SECURE_SETTINGS/WRITE_SETTINGS where applicable
- Identity/user scope: provider authorization preserves caller identity
- Sink: card/personalization/setup state found; no resolver key; SettingsState persistence only; PMS preferred state is separate XML
- Effect: no SettingsProvider HOME selection effect found
- Confidence/status: **bounded negative** / `bounded negative`
- Scope: previous public Phase 9 corpus

## P8-DRIVER-001
- Phase/surface: `8` / `driver final node/policy/caller closure`
- Source: `Phase7C row 7C-001; phase6SG /dev join; phase6VC caller/policy closure; cmdq static CSV`
- Evidence: `Phase7C row 7C-001; phase6SG /dev join; phase6VC caller/policy closure; cmdq static CSV`
- SHA-256: `b3a54d37b4e498ff969a2717cb02cefc923ae6f39da32f5fd8529fe3dce6e899;6cb000e68c9391a2b954966944a41facb31d9c6fed8372c07b8fb4ce07441111;8bb5edcc5b5e1cf0bfb8e45cd14c1e185ac873c4d307e67594c024ccd3b69ad0;8e59aec14eccd2afdf9179efbfea8b727c55d1776fdf68a88bbcf332d8afe1e6`
- Caller: UNKNOWN: no exact shipped native ELF open()+CMDQ ioctl callsite with UID/domain; phase6 inventories contain no closed caller relocation tuple
- Gate: 0644 system:system and mtk_cmdq_device are recorded for the char node; proc entries source 0440; exact merged file_contexts/TE tuple not fully retained; CONFIG_MTK_CMDQ=y; CONFIG_MTK_CMDQ_TAB=y; source platform match mediatek,gce; final Image/object/DTB join incomplete
- Identity/user scope: UNKNOWN: no exact shipped native ELF open()+CMDQ ioctl callsite with UID/domain; phase6 inventories contain no closed caller relocation tuple
- Sink: CMDQ async task/engine notification/readback and MDP register/display/DMA path
- Effect: Potential display/engine/resource control; no package/PMS/HOME sink proven
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P8-DRIVER-002
- Phase/surface: `8` / `driver final node/policy/caller closure`
- Source: `Phase7C row 7C-003; phase6VC /dev/ion policy/caller closure; phase6XG ion_generic source audit`
- Evidence: `Phase7C row 7C-003; phase6VC /dev/ion policy/caller closure; phase6XG ion_generic source audit`
- SHA-256: `abac518864faed94439d75d204e8c16ea75cf3a74c93ee50e128e0f6928a6d63;8bb5edcc5b5e1cf0bfb8e45cd14c1e185ac873c4d307e67594c024ccd3b69ad0;20a47a755613dcfd967624d9821060534e9cda38286a7bb2f8ee777ed9e9a225`
- Caller: UNKNOWN: libion.so symbols/ioctl markers are library capability, not a shipped process open/ioctl caller; UID/domain unresolved
- Gate: Saved metadata records 0666 system:graphics ion_device; final ueventd/file_contexts/TE and exact heap/object join are incomplete; CONFIG_ION=y; CONFIG_MTK_ION=y; CONFIG_ION_TEST absent; final heap enablement and DT/platform instance UNKNOWN
- Identity/user scope: UNKNOWN: libion.so symbols/ioctl markers are library capability, not a shipped process open/ioctl caller; UID/domain unresolved
- Sink: ION buffer allocation/import/share/map/sync and DMA buffer state
- Effect: Potential buffer/DMA exposure; no package/PMS/HOME sink proven
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P8-DRIVER-003
- Phase/surface: `8` / `driver final node/policy/caller closure`
- Source: `Phase7C row 7C-004; phase6VC MTK custom caller closure; phase6XG ion_mtk_custom source audit`
- Evidence: `Phase7C row 7C-004; phase6VC MTK custom caller closure; phase6XG ion_mtk_custom source audit`
- SHA-256: `eb7fbf99acbc492d99d60c98fc62a67fe7350160c6e91dc033781d5bcd986411;8bb5edcc5b5e1cf0bfb8e45cd14c1e185ac873c4d307e67594c024ccd3b69ad0;20a47a755613dcfd967624d9821060534e9cda38286a7bb2f8ee777ed9e9a225`
- Caller: UNKNOWN: libion_mtk.so custom ioctl markers do not identify the exact shipped process, UID, or SELinux domain
- Gate: Node metadata/policy is inherited only from generic /dev/ion evidence; exact custom ioctl allow and heap labels UNKNOWN; CONFIG_MTK_ION=y; ion_device_create/platform registration source present; built-in/module delivery and heap enablement UNKNOWN
- Identity/user scope: UNKNOWN: libion_mtk.so custom ioctl markers do not identify the exact shipped process, UID, or SELinux domain
- Sink: MTK custom system/physical-address/secure-memory and debug metadata controls
- Effect: Potential buffer/physical-address/secure-memory state; no package/PMS/HOME sink proven
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P8-DRIVER-004
- Phase/surface: `8` / `driver final node/policy/caller closure`
- Source: `Phase7C row 7C-002; phase6SG M4U node/policy join; phase6QE privilege-surface M4U row`
- Evidence: `Phase7C row 7C-002; phase6SG M4U node/policy join; phase6QE privilege-surface M4U row`
- SHA-256: `6351de00903a282ba682427095a155794efd8221f253ff11a0f74ed7c5cb86c6;6cb000e68c9391a2b954966944a41facb31d9c6fed8372c07b8fb4ce07441111;db5cd91b8d25170ad27809ace8cdbbd2a3f838ec72e2598a4f6b5a44953d322e`
- Caller: UNKNOWN: no exact shipped native proc open/ioctl caller or UID/domain; no operation performed
- Gate: init records system:media 0440 for the M4U surface; source proc mode 0 is not equivalent to world access; exact proc label/allow tuple is UNKNOWN; Source proc registration and M4U/DT/config correspondence; active misc char branch disabled (#if 0); final DT/object join UNKNOWN
- Identity/user scope: UNKNOWN: no exact shipped native proc open/ioctl caller or UID/domain; no operation performed
- Sink: DMA/IOMMU mapping, port configuration, power and monitor/TF control paths
- Effect: Potential DMA/IOMMU/device-state effect; no package/PMS/HOME sink proven
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P8-DRIVER-005
- Phase/surface: `8` / `driver final node/policy/caller closure`
- Source: `Phase7C row 7C-008; phase6XG uinput source and native/SELinux caller negative`
- Evidence: `Phase7C row 7C-008; phase6XG uinput source and native/SELinux caller negative`
- SHA-256: `98b41492311d9b9fb9ccbfe269a2fddc0fb436f3048b7887e1f6e5482d36211a;20a47a755613dcfd967624d9821060534e9cda38286a7bb2f8ee777ed9e9a225;9d1313d25cb45492d5656d03f05b7e60f5d037ccef15c20d9edec5e0fdbf17f9`
- Caller: UNKNOWN: native inventory/policy scan found no exact shipped ELF open/write/ioctl caller, package, UID, or domain
- Gate: Source fops and CONFIG_INPUT_UINPUT=y are confirmed; node mode/owner/type/allow are UNKNOWN; CONFIG_INPUT_UINPUT=y; inspected source has no local capable()/credential gate; final object/node creation unresolved
- Identity/user scope: UNKNOWN: native inventory/policy scan found no exact shipped ELF open/write/ioctl caller, package, UID, or domain
- Sink: Synthetic input device and event injection into the kernel input graph
- Effect: Potential downstream user-facing input-state effect; no package/PMS/HOME sink proven
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P8-DRIVER-006
- Phase/surface: `8` / `driver final node/policy/caller closure`
- Source: `Phase7C row 7C-006; phase6ME driver-control markers lines 188-194; source/config/Image final join`
- Evidence: `Phase7C row 7C-006; phase6ME driver-control markers lines 188-194; source/config/Image final join`
- SHA-256: `5ffbce942417fc6aca773d90e4c6935f508087f9a80d96138a7ecc30561ed327;077a7cff0d60ae2329986382ef91118819045c3540ec76d0d9eeffb2c67230e3`
- Caller: UNKNOWN: no exact shipped native open/ioctl or proc/sysfs writer with UID/domain; no write performed
- Gate: Source shows writable diagnostic/calibration registrations (proc S_IRUGO|S_IWUSR and device_create_file); final node names, mode/owner, genfscon/file_contexts and TE allow UNKNOWN; CONFIG_MTK_AUXADC_INTF=y; platform_driver_register and calibration cdev/device_create source present; final DT/object/selected instance UNKNOWN
- Identity/user scope: UNKNOWN: no exact shipped native open/ioctl or proc/sysfs writer with UID/domain; no write performed
- Sink: ADC/register diagnostic and calibration read/write paths
- Effect: Potential hardware/diagnostic/calibration state effect; no package/PMS/HOME sink proven
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P9-PREWARM-001
- Phase/surface: `9` / `prewarm caller/grant closure`
- Source: `artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/sources/amazon/speech/sim/router/intentrouter/ExplicitIntentAction.java:268-282`
- Evidence: `artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/sources/amazon/speech/sim/router/intentrouter/ExplicitIntentAction.java:268-282`
- SHA-256: `c1a8bcfc0952239a26b669f7bc227fcc01024ac5db26db7e6eed2ae5cb6a2dc2`
- Caller: com.amazon.alexa.multimodal.gemini / ExplicitIntentAction.prewarmApplicationProcess
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **CLOSED_STATIC** / `CLOSED_STATIC`
- Scope: previous public Phase 9 corpus

## P9-PREWARM-002
- Phase/surface: `9` / `prewarm caller/grant closure`
- Source: `saved APP_PREWARM package snapshot joins com.amazon.alexa.multimodal.gemini to UID 10044 and matching PackageSetting`
- Evidence: `saved APP_PREWARM package snapshot joins com.amazon.alexa.multimodal.gemini to UID 10044 and matching PackageSetting`
- SHA-256: `artifacts/phase6x/prewarm-authorization-20260805-05/com_amazon_permission_APP_PREWARM.block.txt:17-20;262-265`
- Caller: 10044
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **CONFIRMED_SNAPSHOT_LIMITED** / `CONFIRMED_SNAPSHOT_LIMITED`
- Scope: previous public Phase 9 corpus

## P9-PREWARM-003
- Phase/surface: `9` / `prewarm caller/grant closure`
- Source: `artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/manifest.txt:147`
- Evidence: `artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/manifest.txt:147`
- SHA-256: `016bb989d131b2d3f5da85d57962b19054dddbc67eb08d6a9d0812077eacb049`
- Caller: UNKNOWN
- Gate: com.amazon.permission.APP_PREWARM
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **CLOSED_STATIC** / `CLOSED_STATIC`
- Scope: previous public Phase 9 corpus

## P9-PREWARM-004
- Phase/surface: `9` / `prewarm caller/grant closure`
- Source: `artifacts/phase6x/prewarm-authorization-20260805-05/com_amazon_permission_APP_PREWARM.block.txt:1-4;12191;16899;19950`
- Evidence: `artifacts/phase6x/prewarm-authorization-20260805-05/com_amazon_permission_APP_PREWARM.block.txt:1-4;12191;16899;19950`
- SHA-256: `4a71d4d60cdb6c45233e270e3548f02c9ea77e9d3b3b4ed33a7aeb1e130bb798`
- Caller: UNKNOWN
- Gate: granted=true; protection=signature|amazon
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **POSITIVE_STATIC** / `POSITIVE_STATIC`
- Scope: previous public Phase 9 corpus

## P9-PREWARM-005
- Phase/surface: `9` / `prewarm caller/grant closure`
- Source: `artifacts/amazon-services/amazonactivitymanager_fosinit.xml:8-28`
- Evidence: `artifacts/amazon-services/amazonactivitymanager_fosinit.xml:8-28`
- SHA-256: `5d212c94f047aee7abc85ef6dc99aa92ca61e3e3d9318bb69db3c10d9e0da411`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **CLOSED_STATIC** / `CLOSED_STATIC`
- Scope: previous public Phase 9 corpus

## P9-PREWARM-006
- Phase/surface: `9` / `prewarm caller/grant closure`
- Source: `artifacts/phase6aq/public-summary-20260805-01/amazon-service-avc.txt:6`
- Evidence: `artifacts/phase6aq/public-summary-20260805-01/amazon-service-avc.txt:6`
- SHA-256: `d436542564947472c1b2481519312542d7d1053512b9cb47c68abbb981e0b0a4`
- Caller: UNKNOWN
- Gate: shell UID 2000 denied service_manager find; Alexa allow rule UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **PARTIAL_UNKNOWN** / `PARTIAL_UNKNOWN`
- Scope: previous public Phase 9 corpus

## P9-PREWARM-007
- Phase/surface: `9` / `prewarm caller/grant closure`
- Source: `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:394721-394739`
- Evidence: `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:394721-394739`
- SHA-256: `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **CLOSED_STATIC** / `CLOSED_STATIC`
- Scope: previous public Phase 9 corpus

## P9-PREWARM-008
- Phase/surface: `9` / `prewarm caller/grant closure`
- Source: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40534`
- Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40534`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: UNKNOWN
- Gate: checkCallingPermission(APP_PREWARM) then clearCallingIdentity without observed result consumption
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **ANOMALY_CANDIDATE** / `ANOMALY_CANDIDATE`
- Scope: previous public Phase 9 corpus

## P9-PREWARM-009
- Phase/surface: `9` / `prewarm caller/grant closure`
- Source: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40472-40503;40525-40534`
- Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40472-40503;40525-40534`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: incoming identity before check; clearCallingIdentity before PM/AM; restore on normal path
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **PARTIAL_UNKNOWN** / `PARTIAL_UNKNOWN`
- Scope: previous public Phase 9 corpus

## P9-PREWARM-010
- Phase/surface: `9` / `prewarm caller/grant closure`
- Source: `ExplicitIntentAction.java:274; fosservices/disassembly.log:40480-40489`
- Evidence: `ExplicitIntentAction.java:274; fosservices/disassembly.log:40480-40489`
- SHA-256: `c1a8bcfc0952239a26b669f7bc227fcc01024ac5db26db7e6eed2ae5cb6a2dc2;ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: explicit user -> getApplicationInfo(target,1024,user); caller supplies foregroundProfileId
- Sink: UNKNOWN
- Effect: UNKNOWN
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: previous public Phase 9 corpus

## P9-PREWARM-011
- Phase/surface: `9` / `prewarm caller/grant closure`
- Source: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40490-40503`
- Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40490-40503`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: PreWarmCacheHelper -> startProcessLocked(reason=prewarm)
- Effect: UNKNOWN
- Confidence/status: **CLOSED_STATIC** / `CLOSED_STATIC`
- Scope: previous public Phase 9 corpus

## P9-PREWARM-012
- Phase/surface: `9` / `prewarm caller/grant closure`
- Source: `Phase 6/7/8 ledgers`
- Evidence: `Phase 6/7/8 ledgers`
- SHA-256: `UNKNOWN`
- Caller: UNKNOWN
- Gate: UNKNOWN
- Identity/user scope: UNKNOWN
- Sink: UNKNOWN
- Effect: process/cache prewarm; no HOME/package-state/root sink
- Confidence/status: **CLOSED_BOUNDED** / `CLOSED_BOUNDED`
- Scope: previous public Phase 9 corpus

## P9-KFT-001
- Phase/surface: `9` / `KFT tx3 caller identity closure`
- Source: `boot-fosframework/disassembly.log:369180-369243,370378-370428; fosservices/disassembly.log:54415-54478`
- Evidence: `boot-fosframework/disassembly.log:369180-369243,370378-370428; fosservices/disassembly.log:54415-54478`
- SHA-256: `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71;ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: AmazonUserManagerImpl.createChildUser(String) -> IAmazonUserManager.Proxy.enableKftLauncher(UserInfo) -> Binder.transact(3)
- Gate: createUser(name,0x8000) child lifecycle confirmed; tx3 method-local UID/permission/cross-user gate not observed
- Identity/user scope: external APK package/UID not joined; Binder identity reaches service; no pre-setter clearCallingIdentity
- Sink: AmazonUserManagerService.BinderService.enableKftLauncher -> tryEnableKftLauncherComponent -> PMS setters
- Effect: KFT package/component writer for supplied child/profile; no fixed User 0
- Confidence/status: **CONFIRMED_SEMANTIC_CALLER_PARTIAL_IDENTITY** / `CONFIRMED_SEMANTIC_CALLER_PARTIAL_IDENTITY`
- Scope: previous public Phase 9 corpus

## P9-KFT-002
- Phase/surface: `9` / `KFT tx3 caller identity closure`
- Source: `manifest xmltree:2-28; package dump:10774-10809; privapp_permissions.xml:203-207`
- Evidence: `manifest xmltree:2-28; package dump:10774-10809; privapp_permissions.xml:203-207`
- SHA-256: `674c6aa94350761cf2a239f1ffd9099e8dcd3d1f9172a1480e6a5f8a6e2346bd;4a71d4d60cdb6c45233e270e3548f02c9ea77e9d3b3b4ed33a7aeb1e130bb798;643cf114ed7d7b82a642fea650ed7d2f53b5dab2291e4f043c272cbe577df732`
- Caller: Candidate com.amazon.frameworksettings
- Gate: manifest requests MANAGE_USERS and INTERACT_ACROSS_USERS; privapp grants positive; tx3 callsite absent
- Identity/user scope: UID 10112; privileged /system/priv-app; signature digest e627f73a in saved package dump
- Sink: same tx3 writer
- Effect: candidate package has relevant privileges, not proof it invokes tx3
- Confidence/status: **CANDIDATE_NOT_CONFIRMED_CALLER** / `CANDIDATE_NOT_CONFIRMED_CALLER`
- Scope: previous public Phase 9 corpus

## P9-KFT-003
- Phase/surface: `9` / `KFT tx3 caller identity closure`
- Source: `manifests/006_com.amazon.h2settingsfortablet.xmltree.txt; privapp_permissions.xml:213-217; phase6k preferred_activities package block`
- Evidence: `manifests/006_com.amazon.h2settingsfortablet.xmltree.txt; privapp_permissions.xml:213-217; phase6k preferred_activities package block`
- SHA-256: `6e1edce5feb0eb638e04d569f4df9752234ac3c5fd6f33b8169a56c30781ee0c;643cf114ed7d7b82a642fea650ed7d2f53b5dab2291e4f043c272cbe577df732`
- Caller: Candidate com.amazon.h2settingsfortablet
- Gate: manifest/privapp policy grants MANAGE_USERS and INTERACT_ACROSS_USERS; tx3 callsite absent
- Identity/user scope: UID 10130 from saved package artifacts; privileged /system/priv-app
- Sink: same tx3 writer
- Effect: same relevant privilege family, not proof of tx3 use
- Confidence/status: **CANDIDATE_NOT_CONFIRMED_CALLER** / `CANDIDATE_NOT_CONFIRMED_CALLER`
- Scope: previous public Phase 9 corpus

## P9-KFT-004
- Phase/surface: `9` / `KFT tx3 caller identity closure`
- Source: `fosservices/disassembly.log:55053-55105`
- Evidence: `fosservices/disassembly.log:55053-55105`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: AmazonUserManagerService.onBootPhase(500) -> mBinderService.enableKftLauncher(UserInfo)
- Gate: isUpgrade && isChildUser(UserInfo)
- Identity/user scope: system-server local lifecycle; no Binder caller, no tx3
- Sink: same BinderService KFT writer
- Effect: child/profile package/component state; not external Binder tx3
- Confidence/status: **CONFIRMED_LOCAL_NOT_TX3** / `CONFIRMED_LOCAL_NOT_TX3`
- Scope: previous public Phase 9 corpus

## P9-KFT-005
- Phase/surface: `9` / `KFT tx3 caller identity closure`
- Source: `boot-fosframework/disassembly.log:370637-370750`
- Evidence: `boot-fosframework/disassembly.log:370637-370750`
- SHA-256: `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`
- Caller: IAmazonUserManager.Stub.onTransact tx3
- Gate: enforceInterface(amazon.os.IAmazonUserManager); nullable UserInfo decode; no local permission marker
- Identity/user scope: incoming Binder identity preserved into implementation; no clear before writer in bounded slice
- Sink: dispatch to BinderService.enableKftLauncher
- Effect: method dispatch only; no effect without downstream gates
- Confidence/status: **CONFIRMED_DISPATCH_PARTIAL_AUTHZ** / `CONFIRMED_DISPATCH_PARTIAL_AUTHZ`
- Scope: previous public Phase 9 corpus

## P9-KFT-006
- Phase/surface: `9` / `KFT tx3 caller identity closure`
- Source: `fosservices/disassembly.log:55106-55119; artifacts/phase6jd-fosinit-20260808-01/system/fireos/etc/init/amazonusermanager_fosinit.xml`
- Evidence: `fosservices/disassembly.log:55106-55119; artifacts/phase6jd-fosinit-20260808-01/system/fireos/etc/init/amazonusermanager_fosinit.xml`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;14ccd432e6393ce1660ad51c10430c392a3562be3ef20ee2bdfe62a2240e8678`
- Caller: AmazonUserManagerService.onStart -> publishBinderService(amazonusermanagerservice)
- Gate: fosinit vendor-service declaration; service-manager/SELinux is domain-specific
- Identity/user scope: published by system-server; client-side identity not implied by publication
- Sink: IAmazonUserManager Binder service
- Effect: publication/reachability surface, not writer effect
- Confidence/status: **CONFIRMED_PUBLICATION_GATE_INCOMPLETE** / `CONFIRMED_PUBLICATION_GATE_INCOMPLETE`
- Scope: previous public Phase 9 corpus

## P9-KFT-007
- Phase/surface: `9` / `KFT tx3 caller identity closure`
- Source: `fosservices/disassembly.log:54297-54325`
- Evidence: `fosservices/disassembly.log:54297-54325`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: BinderService.enableKftLauncherComponent(UserInfo)
- Gate: tryEnableKftLauncherComponent KFT/TV/existence gate; downstream PMS authorization remains authoritative
- Identity/user scope: no hard-coded identity switch before three setters; later DPM path clear/restore is separate
- Sink: setComponentEnabledSetting Tahoe; setApplicationEnabledSetting Fire Launcher and Launcher3
- Effect: Tahoe enabled; Fire Launcher and Launcher3 state 2 for supplied user
- Confidence/status: **CONFIRMED_SUPPLIED_USER_WRITER** / `CONFIRMED_SUPPLIED_USER_WRITER`
- Scope: previous public Phase 9 corpus

## P9-KFT-008
- Phase/surface: `9` / `KFT tx3 caller identity closure`
- Source: `fosservices/disassembly.log:54847-54895`
- Evidence: `fosservices/disassembly.log:54847-54895`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: General AmazonUserManagerService.checkManageUsersPermission(String)
- Gate: UID 0/1000 or android.permission.MANAGE_USERS
- Identity/user scope: helper checks calling permission, but tx3 edge not recovered
- Sink: SecurityException gate only
- Effect: general user-management authorization; not proven tx3 gate
- Confidence/status: **CONFIRMED_HELPER_UNJOINED** / `CONFIRMED_HELPER_UNJOINED`
- Scope: previous public Phase 9 corpus

## P9-KFT-009
- Phase/surface: `9` / `KFT tx3 caller identity closure`
- Source: `findings/phase-6pr-kft-tx3-authorization-closure.md; work/luna_worker_phase6ub_kft_caller_scope_20260810.md`
- Evidence: `findings/phase-6pr-kft-tx3-authorization-closure.md; work/luna_worker_phase6ub_kft_caller_scope_20260810.md`
- SHA-256: `hashes of cited reports preserved in their own evidence tables`
- Caller: PMS setter downstream for supplied UserInfo.id
- Gate: existing downstream INTERACT_ACROSS_USERS/component-state/protected-package gates are referenced from prior evidence; not re-executed
- Identity/user scope: caller identity remains relevant before PMS gate; no static proof of system identity substitution
- Sink: PMS component/application enabled-state setters
- Effect: child/profile state only when accepted; no formal HOME writer
- Confidence/status: **PARTIAL_DOWNSTREAM_SCOPE** / `PARTIAL_DOWNSTREAM_SCOPE`
- Scope: previous public Phase 9 corpus

## P9-IPC-001
- Phase/surface: `9` / `residual IPC privilege-sink closure`
- Source: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/021_com.amazon.dcpms.fos.service.xmltree.txt:168-175; artifacts/phase6it-missing-priv-apps-20260807-01/jadx/sources/com/amazon/dcpms/fos/service/DCPMSService.java:onBind; artifacts/phase6it-missing-priv-apps-20260807-01/jadx/sources/com/amazon/dcpms/fos/service/ServiceBinder.java:getBinderInstance/getLastDeviceChildExperienceModeDecision; artifacts/phase6it-missing-priv-apps-20260807-01/jadx/sources/com/amazon/dcpmsaidl/IDeviceChildExperienceModeDecisionManager.java:onTransact`
- Evidence: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/021_com.amazon.dcpms.fos.service.xmltree.txt:168-175; artifacts/phase6it-missing-priv-apps-20260807-01/jadx/sources/com/amazon/dcpms/fos/service/DCPMSService.java:onBind; artifacts/phase6it-missing-priv-apps-20260807-01/jadx/sources/com/amazon/dcpms/fos/service/ServiceBinder.java:getBinderInstance/getLastDeviceChildExperienceModeDecision; artifacts/phase6it-missing-priv-apps-20260807-01/jadx/sources/com/amazon/dcpmsaidl/IDeviceChildExperienceModeDecisionManager.java:onTransact`
- SHA-256: `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4; eeb1591145fafc1f5d84e4e801fa5648bd2cfae54b99b1437aad75ff396f5602; 8329e98d58a91b34331d147eac86551b384126af0ec539a7841f8cdf716b520d; 1d02fba9cea813e9d20b1fbd6a515eeb152ff453e36c0ade56825aa685210c73`
- Caller: No client bindService/asInterface caller found in recovered APK/source corpus; DCPMSService itself is the only proven owner
- Gate: Manifest service permission com.amazon.dcpms.permission.GET_DEVICE_CDE_DECISION; exported=true, singleUser=true; AIDL onTransact only enforceInterface, no method-local UID/permission check
- Identity/user scope: Incoming Binder identity is not read, cleared, or replaced in DCPMS onBind/Stub/ServiceBinder; implementation executes as DCPMS process
- Sink: ServiceBinder.getLastDeviceChildExperienceModeDecision -> CDEAttributesPersistenceService.getDeviceChildExperienceModeDecision; null path clears decision and returns NOT_COMPUTED
- Effect: Read-only CDE decision retrieval; no SettingsProvider/PMS/preferred-activity/package-state/user mutation sink recovered
- Confidence/status: **UNKNOWN_BOUNDED** / `UNKNOWN_BOUNDED`
- Scope: previous public Phase 9 corpus

## P9-IPC-002
- Phase/surface: `9` / `residual IPC privilege-sink closure`
- Source: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/021_com.amazon.dcpms.fos.service.xmltree.txt:168-175; artifacts/phase6it-missing-priv-apps-20260807-01/jadx/sources/com/amazon/dcpms/fos/service/ServiceBinder.java:registerCallback/unregisterCallback/broadcastDecision; artifacts/phase6it-missing-priv-apps-20260807-01/jadx/sources/com/amazon/dcpmsaidl/IDeviceChildExperienceModeDecisionManager.java:onTransact cases 2-3; artifacts/phase6it-missing-priv-apps-20260807-01/jadx/sources/com/amazon/dcpmsaidl/callbacks/IDCPMSServiceCallback.java:onTransact`
- Evidence: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/021_com.amazon.dcpms.fos.service.xmltree.txt:168-175; artifacts/phase6it-missing-priv-apps-20260807-01/jadx/sources/com/amazon/dcpms/fos/service/ServiceBinder.java:registerCallback/unregisterCallback/broadcastDecision; artifacts/phase6it-missing-priv-apps-20260807-01/jadx/sources/com/amazon/dcpmsaidl/IDeviceChildExperienceModeDecisionManager.java:onTransact cases 2-3; artifacts/phase6it-missing-priv-apps-20260807-01/jadx/sources/com/amazon/dcpmsaidl/callbacks/IDCPMSServiceCallback.java:onTransact`
- SHA-256: `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4; 8329e98d58a91b34331d147eac86551b384126af0ec539a7841f8cdf716b520d; 1d02fba9cea813e9d20b1fbd6a515eeb152ff453e36c0ade56825aa685210c73; 0b705c458b7dcc34deb7b39c10470b5f4d020f04d254209058fac35de3ca6fa4`
- Caller: No callback-client caller or package identity found; only DCPMS internal broadcastDecision producer is recovered
- Gate: Same exported service permission and singleUser declaration; Stub enforces interface token only; callback registration accepts non-null binder plus non-empty caller-supplied string
- Identity/user scope: DCPMS stores supplied callback Binder in process map; no Binder.getCallingUid, clearCallingIdentity, callback ownership, or package-to-string binding check
- Sink: ServiceBinder.mCallbackClientsMap -> IDCPMSServiceCallback.handleDecisionChange; callback Stub also only enforces interface token
- Effect: Decision notification to registered callback; no direct settings/package/user/device-policy sink; untrusted caller could only be assessed after missing bind/permission/client join
- Confidence/status: **UNKNOWN_BOUNDED** / `UNKNOWN_BOUNDED`
- Scope: previous public Phase 9 corpus

## P9-BROAD-001
- Phase/surface: `9` / `broad non-Launcher privilege surfaces`
- Source: `output/tables/phase6qd-privilege-surface.csv:2; work/luna_worker_ipc_unclosed_sink_inventory_20260810.md:15`
- Evidence: `output/tables/phase6qd-privilege-surface.csv:2; work/luna_worker_ipc_unclosed_sink_inventory_20260810.md:15`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;d6c45b2eb54d4a4acd288ffc7ddd36c6d65be373d72e66bd2991354c3a0b5839`
- Caller: External Binder caller UNKNOWN; tx1/2/4/5 proxy contract only
- Gate: com.amazon.permission.ADD_RM_PKG_METADATA via checkCallingOrSelfPermission; exact accepted caller UNKNOWN
- Identity/user scope: Calling UID not resolved; no clearCallingIdentity/restoreCallingIdentity in bounded mutator block
- Sink: AmazonApplicationFlags persistence; first PackageManager/HOME/component consumer UNKNOWN
- Effect: Package/metadata state capability statically confirmed; caller and downstream effect UNKNOWN
- Confidence/status: **STATIC_SINK_CONFIRMED_CALLER_UNKNOWN; UNKNOWN is not a vulnerability** / `STATIC_SINK_CONFIRMED_CALLER_UNKNOWN; UNKNOWN is not a vulnerability`
- Scope: previous public Phase 9 corpus

## P9-BROAD-002
- Phase/surface: `9` / `broad non-Launcher privilege surfaces`
- Source: `output/tables/phase6qd-privilege-surface.csv:5; work/luna_worker_ipc_unclosed_sink_inventory_20260810.md:17`
- Evidence: `output/tables/phase6qd-privilege-surface.csv:5; work/luna_worker_ipc_unclosed_sink_inventory_20260810.md:17`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875dc5f937073ccc2faa020ca592c0515151c;d6c45b2eb54d4a4acd288ffc7ddd36c6d65be373d72e66bd2991354c3a0b5839`
- Caller: Device/Profile Owner or trusted policy caller expected; ordinary caller UNKNOWN
- Gate: Mapped restriction permission plus system/root-style Binder.getCallingUid allow branch; exact external caller UNKNOWN
- Identity/user scope: clearCallingIdentity around UserManager.setUserRestriction; restore path bounded
- Sink: UserManager.setUserRestriction/clear restriction persistence; no PM preferred/HOME/component sink in bounded path
- Effect: User/profile policy state can change only after unresolved policy/caller join; effect scope UNKNOWN
- Confidence/status: **STATIC_POLICY_SINK_CONFIRMED_CALLER_UNKNOWN; UNKNOWN is not a vulnerability** / `STATIC_POLICY_SINK_CONFIRMED_CALLER_UNKNOWN; UNKNOWN is not a vulnerability`
- Scope: previous public Phase 9 corpus

## P9-BROAD-003
- Phase/surface: `9` / `broad non-Launcher privilege surfaces`
- Source: `output/tables/phase6qd-privilege-surface.csv:6; work/luna_worker_ipc_unclosed_sink_inventory_20260810.md:18`
- Evidence: `output/tables/phase6qd-privilege-surface.csv:6; work/luna_worker_ipc_unclosed_sink_inventory_20260810.md:18`
- SHA-256: `caller registration, manifest/service binding, returned component and user arguments`
- Caller: AmazonProfileManager/framework client; external caller UNKNOWN
- Gate: PROFILE_INTERACTION enforced by enforceProfileInteractionPermissions
- Identity/user scope: No relevant clearCallingIdentity-to-PM writer shown
- Sink: Internal profile flow and component/activity handoff; no preferred-activity, HOME resolver, package or component setter found
- Effect: Permission-gated profile surface with caller and user mapping unresolved; no launcher sink proven
- Confidence/status: **PERMISSION_GATED_STATIC_PROFILE_SINK; ORDINARY_REACHABILITY_UNKNOWN; UNKNOWN is not a vulnerability** / `PERMISSION_GATED_STATIC_PROFILE_SINK; ORDINARY_REACHABILITY_UNKNOWN; UNKNOWN is not a vulnerability`
- Scope: previous public Phase 9 corpus

## P9-BROAD-004
- Phase/surface: `9` / `broad non-Launcher privilege surfaces`
- Source: `output/tables/phase6qd-privilege-surface.csv:7; work/luna_worker_ipc_unclosed_sink_inventory_20260810.md:18`
- Evidence: `output/tables/phase6qd-privilege-surface.csv:7; work/luna_worker_ipc_unclosed_sink_inventory_20260810.md:18`
- SHA-256: `manifest/service binding, method-local permission, caller identity and user argument provenance`
- Caller: External private-service caller UNKNOWN
- Gate: Method-local permission marker not resolved in bounded block; service publication present
- Identity/user scope: No clearCallingIdentity-to-PM writer shown
- Sink: Configured profile picker and startActivityAsUser; no explicit HOME/preferred/package mutation shown
- Effect: Exported/private UI relay capability; accepted caller, gate and downstream state effect UNKNOWN
- Confidence/status: **STATIC_UI_LAUNCH_SINK_CALLER_AND_GATE_UNKNOWN; UNKNOWN is not a vulnerability** / `STATIC_UI_LAUNCH_SINK_CALLER_AND_GATE_UNKNOWN; UNKNOWN is not a vulnerability`
- Scope: previous public Phase 9 corpus

## P9-BROAD-005
- Phase/surface: `9` / `broad non-Launcher privilege surfaces`
- Source: `output/tables/phase6qd-privilege-surface.csv:8; work/luna_worker_ipc_unclosed_sink_inventory_20260810.md:19`
- Evidence: `output/tables/phase6qd-privilege-surface.csv:8; work/luna_worker_ipc_unclosed_sink_inventory_20260810.md:19`
- SHA-256: `all observer registrations, callback implementations/consumers and any component/package-state join`
- Caller: Framework/system-server callback path; external Binder caller and observer registration UNKNOWN
- Gate: Observer registration permission/caller gate not closed in bounded slice
- Identity/user scope: No clearCallingIdentity-to-PM/HOME writer shown
- Sink: IAmazonActivitySwitchObserver callback with ComponentName; consumer and any HOME/package-state sink UNKNOWN
- Effect: Callback surface and component string are capability evidence only; caller-to-sink edge remains UNKNOWN
- Confidence/status: **CALLBACK_SURFACE_STATIC; CALLER_TO_HOME_SINK_UNKNOWN; UNKNOWN is not a vulnerability** / `CALLBACK_SURFACE_STATIC; CALLER_TO_HOME_SINK_UNKNOWN; UNKNOWN is not a vulnerability`
- Scope: previous public Phase 9 corpus

## P9-BROAD-006
- Phase/surface: `9` / `broad non-Launcher privilege surfaces`
- Source: `output/tables/phase6qd-privilege-surface.csv:9; work/luna_worker_ipc_unclosed_sink_inventory_20260810.md:20`
- Evidence: `output/tables/phase6qd-privilege-surface.csv:9; work/luna_worker_ipc_unclosed_sink_inventory_20260810.md:20`
- SHA-256: `method-local gates, service registration/SELinux mapping, caller UID and target user/display scope`
- Caller: External caller UNKNOWN; private service lookup boundary
- Gate: Per-method permission and Binder caller handling incomplete in bounded wrapper
- Identity/user scope: Identity handling unresolved; no clearCallingIdentity-to-PM writer shown
- Sink: WindowManagerService.setOverscan and PIP/status-bar control state
- Effect: High-impact window state sink is statically visible; no package/HOME sink or accepted caller established
- Confidence/status: **STATIC_WMS_SINK_CALLER_AND_GATE_UNKNOWN; UNKNOWN is not a vulnerability** / `STATIC_WMS_SINK_CALLER_AND_GATE_UNKNOWN; UNKNOWN is not a vulnerability`
- Scope: previous public Phase 9 corpus

## P9-BROAD-007
- Phase/surface: `9` / `broad non-Launcher privilege surfaces`
- Source: `output/tables/phase6qd-privilege-surface.csv:10; work/luna_worker_ipc_unclosed_sink_inventory_20260810.md:21`
- Evidence: `output/tables/phase6qd-privilege-surface.csv:10; work/luna_worker_ipc_unclosed_sink_inventory_20260810.md:21`
- SHA-256: `service declaration, caller package/signature, grant provenance and create-user user-scope data flow`
- Caller: H2 client/account workflow; exported-service caller not identified
- Gate: android.permission.BIND_SERVICE signature gate plus account/workflow checks
- Identity/user scope: No clearCallingIdentity edge established in recovered H2 path
- Sink: AmazonUserManager.createAdultUser/createChildUser and downstream profile lifecycle
- Effect: Signature-bound user/profile creation capability; ordinary reachability and exact caller/user scope UNKNOWN
- Confidence/status: **SIGNATURE_BOUND_TRUSTED_WORKFLOW; LOW_PRIVILEGE_CALLER_UNKNOWN; UNKNOWN is not a vulnerability** / `SIGNATURE_BOUND_TRUSTED_WORKFLOW; LOW_PRIVILEGE_CALLER_UNKNOWN; UNKNOWN is not a vulnerability`
- Scope: previous public Phase 9 corpus

## P9-BROAD-008
- Phase/surface: `9` / `broad non-Launcher privilege surfaces`
- Source: `output/tables/phase6qd-privilege-surface.csv:11; work/luna_worker_ipc_unclosed_sink_inventory_20260810.md:22`
- Evidence: `output/tables/phase6qd-privilege-surface.csv:11; work/luna_worker_ipc_unclosed_sink_inventory_20260810.md:22`
- SHA-256: `Context/ContentResolver/PackageManager user handle, protected receiver membership and sender provenance`
- Caller: Trusted system-server AmazonPackageManagerService.onBootPhase(550) sender; ordinary broadcast sender UNKNOWN
- Gate: boot phase 550 plus isUpgrade; protected BOOT_AFTER_SYSTEM_OTA/RECEIVE_BOOT_AFTER_SYSTEM_OTA provenance bounded to scanned set
- Identity/user scope: Receiver runs in trusted lifecycle context; no ordinary Binder calling identity
- Sink: PackageHelper.enableComponent(OobeHomeActivity) plus Settings/OOBE setup flags
- Effect: OTA/OOBE lifecycle writer statically confirmed; ordinary relay and exact user/component state effect UNKNOWN
- Confidence/status: **STATIC_LIFECYCLE_SINK_CONFIRMED_ORDINARY_RELAY_UNKNOWN; UNKNOWN is not a vulnerability** / `STATIC_LIFECYCLE_SINK_CONFIRMED_ORDINARY_RELAY_UNKNOWN; UNKNOWN is not a vulnerability`
- Scope: previous public Phase 9 corpus

## P9-BROAD-009
- Phase/surface: `9` / `broad non-Launcher privilege surfaces`
- Source: `output/tables/phase6qd-privilege-surface.csv:12; work/luna_worker_ipc_unclosed_sink_inventory_20260810.md:23`
- Evidence: `output/tables/phase6qd-privilege-surface.csv:12; work/luna_worker_ipc_unclosed_sink_inventory_20260810.md:23`
- SHA-256: `exact production caller, effective grant, target package/component and user input provenance`
- Caller: Play Store/data-app invoking component and input provenance UNKNOWN
- Gate: Captured grant/holder metadata; effective writer gate and calling UID not established
- Identity/user scope: No identity relay to a Fire target proven
- Sink: setApplicationEnabledSetting/setComponentEnabledSetting generic writers
- Effect: Holder/grant metadata plus generic writer capability only; Fire target and caller edge UNKNOWN
- Confidence/status: **HOLDER_METADATA_ONLY_WRITER_STATIC_CALLER_UNKNOWN; UNKNOWN is not a vulnerability** / `HOLDER_METADATA_ONLY_WRITER_STATIC_CALLER_UNKNOWN; UNKNOWN is not a vulnerability`
- Scope: previous public Phase 9 corpus

## P9-BROAD-010
- Phase/surface: `9` / `broad non-Launcher privilege surfaces`
- Source: `output/tables/phase6qd-privilege-surface.csv:13; work/luna_worker_ipc_unclosed_sink_inventory_20260810.md:24`
- Evidence: `output/tables/phase6qd-privilege-surface.csv:13; work/luna_worker_ipc_unclosed_sink_inventory_20260810.md:24`
- SHA-256: `registration/function-pointer provenance, accepted caller, signature grant and any framework/package-state relay`
- Caller: OTA controller/recovery lifecycle caller; ordinary app/shell caller UNKNOWN
- Gate: com.amazon.dcp.ota.permission.CONTROLLER signature|privileged; recovery/update identity boundary
- Identity/user scope: Trusted OTA/recovery identity; no ordinary clearCallingIdentity relay established
- Sink: Partition/block-image and post-install lifecycle capability; Framework HOME/package sink not connected
- Effect: OTA/update capability statically confirmed only; ordinary caller and Framework sink join UNKNOWN
- Confidence/status: **PRIVILEGED_CAPABILITY_ONLY_CALLER_UNKNOWN; UNKNOWN is not a vulnerability** / `PRIVILEGED_CAPABILITY_ONLY_CALLER_UNKNOWN; UNKNOWN is not a vulnerability`
- Scope: previous public Phase 9 corpus

## P10-APM-001
- Phase/surface: `10` / `AmazonPackageManager/package-state closure`
- Source: `fosservices/disassembly.log:95991-96008; phase6mu consumer-call-sites.csv:95531-95546; phase6mx caller inventory`
- Evidence: `fosservices/disassembly.log:95991-96008; phase6mu consumer-call-sites.csv:95531-95546; phase6mx caller inventory`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;0b86f79ce8ae336ed5de9f50ecf80d2bce2f01e3c11c121299aea2a46e111ebb;884b8636fd1baff3c1790cb4398e9cb83588dd68260643a4c660876c5269af82`
- Caller: production APK/native caller NOT_FOUND; generated IAmazonPackageManager Proxy/Stub excluded
- Gate: amazon.permission.ADD_RM_PKG_METADATA; declared signature|amazon; service publication is not authorization
- Identity/user scope: No clearCallingIdentity/restoreCallingIdentity in method slice; checkCallingOrSelfPermission is used; caller supplies userId; User 0 not established
- Sink: AmazonApplicationFlags.setAmazonFlagsForUser -> writeToFile
- Effect: persists Amazon application flags/metadata state; no HOME resolver edge
- Confidence/status: **STATIC_SINK_CONFIRMED_CALLER_UNKNOWN** / `STATIC_SINK_CONFIRMED_CALLER_UNKNOWN`
- Scope: Phase 10 worker row 10A-PM-001; missing_edge=Exact production caller package/UID/signing identity; exact service-manager and SELinux allow tuple; runtime caller-to-userId provenance

## P10-APM-002
- Phase/surface: `10` / `AmazonPackageManager/package-state closure`
- Source: `fosservices/disassembly.log:96009-96026; phase6mu consumer-call-sites.csv:95548-95554; phase6mu consumer closure`
- Evidence: `fosservices/disassembly.log:96009-96026; phase6mu consumer-call-sites.csv:95548-95554; phase6mu consumer closure`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;0b86f79ce8ae336ed5de9f50ecf80d2bce2f01e3c11c121299aea2a46e111ebb`
- Caller: production APK/native caller NOT_FOUND; generated IAmazonPackageManager Proxy/Stub excluded
- Gate: amazon.permission.ADD_RM_PKG_METADATA; declared signature|amazon; service publication is not authorization
- Identity/user scope: No clearCallingIdentity/restoreCallingIdentity in method slice; checkCallingOrSelfPermission is used; caller supplies userId; User 0 not established
- Sink: AmazonApplicationFlags.setAmazonMetadataForUser -> writeToFile
- Effect: persists per-package Amazon metadata; consumer scan finds flags/metadata consumers but no HOME selector
- Confidence/status: **STATIC_SINK_CONFIRMED_CALLER_UNKNOWN** / `STATIC_SINK_CONFIRMED_CALLER_UNKNOWN`
- Scope: Phase 10 worker row 10A-PM-002; missing_edge=Exact requester package/UID and grant/privapp join; exact service-manager/SELinux gate; whether any consumer changes HOME/package state

## P10-APM-003
- Phase/surface: `10` / `AmazonPackageManager/package-state closure`
- Source: `fosservices/disassembly.log:54297-54325,54371-54414; phase9b KFT closure; phase6ay method matrix`
- Evidence: `fosservices/disassembly.log:54297-54325,54371-54414; phase9b KFT closure; phase6ay method matrix`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;ed81a8c3d285c34531307ea16aac0093167890d59c8a93920d6f3d41194fc029;807fb78567609b170833b8855b350b2d996bd56a78683d9b919cb879cf921484`
- Caller: AmazonUserManagerService.BinderService.enableKftLauncher(UserInfo); external APK caller to AmazonUserManagerImpl.createChildUser is NOT_FOUND; framework candidate packages only
- Gate: KFT/TV/existence gates; outer private service visibility; tx3 method-local MANAGE_USERS edge not proven
- Identity/user scope: Binder identity remains relevant before PMS setters; later enableKftLauncher path has clear/restore around DPM/profile-owner work; UserInfo.id supplied; child/profile user; no constant User 0
- Sink: AmazonPackageManager.setComponentEnabledSetting(com.amazon.tahoe/.launcher.FreeTimeLauncherActivity,1,1,userId)
- Effect: enables Tahoe FreeTime launcher component for supplied child user
- Confidence/status: **KNOWN_CHILD_SCOPED_WRITER_EXTERNAL_CALLER_UNKNOWN** / `KNOWN_CHILD_SCOPED_WRITER_EXTERNAL_CALLER_UNKNOWN`
- Scope: Phase 10 worker row 10A-PM-003; missing_edge=Exact external APK/native callsite; tx3 authorization join; service-manager/SELinux client rule; proof of User 0 input

## P10-APM-004
- Phase/surface: `10` / `AmazonPackageManager/package-state closure`
- Source: `fosservices/disassembly.log:54314-54325; phase6mh writer ledger; phase6fz User-0 closure`
- Evidence: `fosservices/disassembly.log:54314-54325; phase6mh writer ledger; phase6fz User-0 closure`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;39ce24194ecead7109894d6bae3cfcf631118c9181ec446dc70a6dd3354f231a;a1b93d1d061b5a9df5a9799e8190b8f2d2271ae2b4ddda5e64ad590aab2b9e25`
- Caller: AmazonUserManagerService.BinderService.enableKftLauncher(UserInfo); external APK caller NOT_FOUND
- Gate: KFT/TV/existence gates; private service visibility; PMS protected-package gate applies downstream
- Identity/user scope: No identity clear before the three package-state setters in the inspected helper; later DPM branch clears/restores; UserInfo.id supplied; child/profile user; no constant User 0
- Sink: AmazonPackageManager.setApplicationEnabledSetting(com.amazon.firelauncher,2,0,userId) and com.android.launcher3
- Effect: disables Fire Launcher and Launcher3 for supplied KFT child user; not a general HOME replacement
- Confidence/status: **KNOWN_CHILD_SCOPED_WRITER_PROTECTED_DOWNSTREAM** / `KNOWN_CHILD_SCOPED_WRITER_PROTECTED_DOWNSTREAM`
- Scope: Phase 10 worker row 10A-PM-004; missing_edge=Exact external caller package/UID; child-user creation-to-tx3 edge; whether PMS accepts target for User 0; protected-package policy tuple

## P10-APM-005
- Phase/surface: `10` / `AmazonPackageManager/package-state closure`
- Source: `fosservices/disassembly.log:293701-293755; phase6mh writer ledger; phase6ep reachability`
- Evidence: `fosservices/disassembly.log:293701-293755; phase6mh writer ledger; phase6ep reachability`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;39ce24194ecead7109894d6bae3cfcf631118c9181ec446dc70a6dd3354f231a;`
- Caller: AmazonProductPolicyService local/in-process trusted system service; external trigger package/UID UNKNOWN
- Gate: policy-file/user-list driven; trusted system-service path; no public AmazonPackageManager endpoint
- Identity/user scope: No Binder caller in local callback; system_server/service identity inferred only from static class placement; explicit user list parameter; User 0 only if policy input names it
- Sink: AmazonPackageManager.setComponentEnabledSetting or setApplicationEnabledSetting
- Effect: enables/disables policy-selected package/component; ledger has no fixed Fire/HOME target
- Confidence/status: **STATIC_TRUSTED_LOCAL_WRITER_NO_USER0_HOME_EDGE** / `STATIC_TRUSTED_LOCAL_WRITER_NO_USER0_HOME_EDGE`
- Scope: Phase 10 worker row 10A-PM-005; missing_edge=Exact policy resource, trigger caller, UID/domain, and User-0 target provenance

## P10-APM-006
- Phase/surface: `10` / `AmazonPackageManager/package-state closure`
- Source: `boot-fosframework/disassembly.log:367356; PMS Java:12916-12962; phase6mw sink inventory`
- Evidence: `boot-fosframework/disassembly.log:367356; PMS Java:12916-12962; phase6mw sink inventory`
- SHA-256: `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71;f0efc633c75524540dd8a5703e5db528bb81ed80c9c49ad34e5cdf4d2078b074;84544d534c0c5addf6d10ff3d5cef6f8ec2a4a725da50ee1d18609fccfba0953`
- Caller: framework manager API caller NOT_FOUND in bounded production corpus; static API wrapper only
- Gate: PMS addPreferredActivity enforces cross-user permission and SET_PREFERRED_APPLICATIONS (or legacy targetSdk exception)
- Identity/user scope: PMS reads Binder.getCallingUid; no identity normalization established for external wrapper; explicit userId in PMS; User 0 possible only with authorized caller and supplied id
- Sink: PMS addPreferredActivityInternal -> preferred activity record
- Effect: writes preferred activity state; not itself proof of HOME selection or Fire replacement
- Confidence/status: **STATIC_API_AND_PMS_GATE_CALLER_UNKNOWN** / `STATIC_API_AND_PMS_GATE_CALLER_UNKNOWN`
- Scope: Phase 10 worker row 10A-PM-006; missing_edge=Exact APK/native caller; service-manager/SELinux path; candidate component and actual User-0 effect

## P10-APM-007
- Phase/surface: `10` / `AmazonPackageManager/package-state closure`
- Source: `PMS Java:12987-13062,13705-13706; Settings DefaultHomePicker.java:69-90; phase1 HOME evidence summarized in phase9/earlier reports`
- Evidence: `PMS Java:12987-13062,13705-13706; Settings DefaultHomePicker.java:69-90; phase1 HOME evidence summarized in phase9/earlier reports`
- SHA-256: `f0efc633c75524540dd8a5703e5db528bb81ed80c9c49ad34e5cdf4d2078b074;56e7319492ee910d53c89f1d9c09eb18bdc7cc304106c403ee2e1049ebe2b9a7;6bd54597763b4dc880cb0fa7539a29a78b840a610eab1a9ea7ae414181f9d17b`
- Caller: framework manager API caller NOT_FOUND in bounded production corpus; Settings DefaultHomePicker is a separate static caller
- Gate: PMS enforces cross-user permission and SET_PREFERRED_APPLICATIONS; HOME filter/component validation remains in PMS
- Identity/user scope: PMS uses Binder.getCallingUid; no clear/restore edge in inspected gate; explicit userId; User 0 possible only through authorized AsUser route
- Sink: PMS replacePreferredActivity -> preferred activity record
- Effect: can replace preferred record when authorized, but Fire priority-50 resolver evidence shows ordinary preferred record did not win
- Confidence/status: **STATIC_HOME_WRITER_GATE_CONFIRMED_CALLER_NOT_CLOSED** / `STATIC_HOME_WRITER_GATE_CONFIRMED_CALLER_NOT_CLOSED`
- Scope: Phase 10 worker row 10A-PM-007; missing_edge=Exact Settings/runtime UID and exported reachability; exact User-0 authorization; protected Fire/HOME resolver gate

## P10-APM-008
- Phase/surface: `10` / `AmazonPackageManager/package-state closure`
- Source: `services/disassembly.log:500744-500765; phase6mh writer ledger; phase6fz User-0 closure; saved phase1 package tests`
- Evidence: `services/disassembly.log:500744-500765; phase6mh writer ledger; phase6fz User-0 closure; saved phase1 package tests`
- SHA-256: `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53;a1b93d1d061b5a9df5a9799e8190b8f2d2271ae2b4ddda5e64ad590aab2b9e25`
- Caller: shell UID 2000 via standard pm/cmd package path
- Gate: standard shell command reaches PMS, then protected-package/PMS gate; existing saved attempts against Fire Launcher returned SecurityException and unchanged User 0 state
- Identity/user scope: Binder identity is shell UID 2000 at PMS entry; --user selects scope; tested existing evidence targets User 0
- Sink: PMS setApplicationEnabledSetting/setComponentEnabledSetting
- Effect: ordinary shell cannot disable protected Fire Launcher in saved evidence; no Amazon private-service reachability
- Confidence/status: **ORDINARY_SHELL_USER0_CHAIN_REJECTED_BY_PMS** / `ORDINARY_SHELL_USER0_CHAIN_REJECTED_BY_PMS`
- Scope: Phase 10 worker row 10A-PM-008; missing_edge=Exact SELinux/service-manager tuple for private Amazon service; whether any non-protected package target creates HOME effect

## P10-APM-009
- Phase/surface: `10` / `AmazonPackageManager/package-state closure`
- Source: `phase6mx caller inventory; phase9c residual IPC; phase6ip/phase6bd service boundary evidence`
- Evidence: `phase6mx caller inventory; phase9c residual IPC; phase6ip/phase6bd service boundary evidence`
- SHA-256: `884b8636fd1baff3c1790cb4398e9cb83588dd68260643a4c660876c5269af82;UNKNOWN;UNKNOWN`
- Caller: ordinary app package/UID NOT_FOUND as a successful caller; Phase6IP test app only exercised proxy receiver and was blocked
- Gate: private service_manager/SELinux gate is unresolved per-client; metadata mutators additionally require signature|amazon; tx6 requires FLAG_SYSTEM PendingIntent creator
- Identity/user scope: No successful Binder identity path; tx6/tx7 identity gates use creator UID/Binder.getCallingUid; User scope UNKNOWN; no evidence of User-0 writer
- Sink: UNKNOWN
- Effect: No package/HOME sink reached from bounded ordinary-app corpus
- Confidence/status: **NO_REACHABLE_ORDINARY_APP_USER0_HOME_CHAIN_FOUND** / `NO_REACHABLE_ORDINARY_APP_USER0_HOME_CHAIN_FOUND`
- Scope: Phase 10 worker row 10A-PM-009; missing_edge=Exact ordinary-app package/UID to service_manager allow; successful transaction and downstream PMS gate

## P10-APM-010
- Phase/surface: `10` / `AmazonPackageManager/package-state closure`
- Source: `phase1 rendered report HOME resolver and package tests; phase6fz closure; phase9 control-surface index`
- Evidence: `phase1 rendered report HOME resolver and package tests; phase6fz closure; phase9 control-surface index`
- SHA-256: `UNKNOWN;a1b93d1d061b5a9df5a9799e8190b8f2d2271ae2b4ddda5e64ad590aab2b9e25;6bd54597763b4dc880cb0fa7539a29a78b840a610eab1a9ea7ae414181f9d17b`
- Caller: Fire Launcher is standard HOME candidate; Settings picker is static caller; exact runtime external caller for selected HOME state UNKNOWN
- Gate: resolver ranking and PMS preferred-activity gates; Fire protected-package policy is separate downstream gate
- Identity/user scope: HOME launch path can be system_server or shell depending entry; no identity relay to Amazon PM established; existing saved User 0 HOME resolution; alternate users UNKNOWN
- Sink: PackageManager resolver -> com.amazon.firelauncher/.Launcher
- Effect: saved unlocked HOME path resolves Fire priority 50; normal preferred record did not outrank it
- Confidence/status: **HOME_EFFECT_CONFIRMED_FIRE_RESOLVER_NOT_AMAZON_PM_BYPASS** / `HOME_EFFECT_CONFIRMED_FIRE_RESOLVER_NOT_AMAZON_PM_BYPASS`
- Scope: Phase 10 worker row 10A-PM-010; missing_edge=Exact current-build resolver internal selection path and all alternate-user behavior

## P10-DPM-001
- Phase/surface: `10` / `DevicePolicy/Profile IPC closure`
- Source: `fosservices/disassembly.log:45935-46108; work/luna_worker_parent_profile_dpm_sink_closure_20260810.md; artifacts/amazon-services/amazondevicepolicymanager_fosinit.xml:9-27`
- Evidence: `fosservices/disassembly.log:45935-46108; work/luna_worker_parent_profile_dpm_sink_closure_20260810.md; artifacts/amazon-services/amazondevicepolicymanager_fosinit.xml:9-27`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;c16b54b82a42c7ec41d3e0a943e7352428100c4b23cad90e024202b51ac5ed96;6fe0df7450551fb940f4169977d97b46bebb43bebef8a604ac77e0c40f91acee`
- Caller: External APK/package/UID/signature: UNKNOWN; no exact production client joined in bounded Phase 8B/9B/10A corpus
- Gate: Amazon restriction keys require MANAGE_USERS; generic branch still reaches DPM active-admin/profile-owner and caller-ownership validation; service publication is not authorization
- Identity/user scope: Binder.getCallingUid() is read by caller check; custom branch then Binder.clearCallingIdentity()/restoreCallingIdentity() around UserManager/DPM write; caller-supplied userId; User 0 is a possible input in the API but no ordinary caller-to-User-0 edge is closed
- Sink: DevicePolicyManagerService.setUserRestrictionForUser or UserManager.setUserRestriction
- Effect: restriction/policy state only; no PMS package-state or HOME resolver sink
- Confidence/status: **STATIC_GATE_CONFIRMED_CALLER_UNKNOWN_NO_HOME_EDGE** / `STATIC_GATE_CONFIRMED_CALLER_UNKNOWN_NO_HOME_EDGE`
- Scope: Phase 10 worker row 10B-DPM-001; missing_edge=exact client package/UID/signature grant; per-domain service_manager/SELinux allow; runtime userId provenance

## P10-DPM-002
- Phase/surface: `10` / `DevicePolicy/Profile IPC closure`
- Source: `decompiled/jadx/systemui/sources/com/android/server/devicepolicy/DevicePolicyManagerService.java:6604-6621,8303-8321; work/luna_worker_parent_profile_dpm_sink_closure_20260810.csv`
- Evidence: `decompiled/jadx/systemui/sources/com/android/server/devicepolicy/DevicePolicyManagerService.java:6604-6621,8303-8321; work/luna_worker_parent_profile_dpm_sink_closure_20260810.csv`
- SHA-256: `f0efc633c75524540dd8a5703e5db528bb81ed80c9c49ad34e5cdf4d2078b074;c16b54b82a42c7ec41d3e0a943e7352428100c4b23cad90e024202b51ac5ed96`
- Caller: Active admin/profile owner is the semantic caller gate; exact external trigger package/UID for the tested owner path is UNKNOWN
- Gate: DPM active-admin/profile-owner and caller ownership; vendor callback requires LOCK_SCREEN_SERVICE; downstream PMS persistent-preferred transaction requires system UID 1000
- Identity/user scope: DPM clears calling identity before IPackageManager/PMS call; PMS then evaluates Binder.getCallingUid()==1000; DPM owner user context can be User 0, but target component/user acceptance and effective HOME replacement are not established
- Sink: persistent preferred activity record / PMS addPersistentPreferredActivityInternal
- Effect: potential preferred/HOME record only; saved closure found no ordinary write and no proof of Fire replacement
- Confidence/status: **DPM_OWNER_AND_PMS_UID1000_GATE_CONFIRMED** / `DPM_OWNER_AND_PMS_UID1000_GATE_CONFIRMED`
- Scope: Phase 10 worker row 10B-DPM-002; missing_edge=exact external caller package/UID/certificate; complete owner-to-target-user mapping; resolver ranking and Fire protection join

## P10-DPM-003
- Phase/surface: `10` / `DevicePolicy/Profile IPC closure`
- Source: `fosservices/disassembly.log:77222-77266; boot-fosframework/disassembly.log:378462-378525; findings/phase-6er-amazon-profile-metadata-tx41-boundary.md`
- Evidence: `fosservices/disassembly.log:77222-77266; boot-fosframework/disassembly.log:378462-378525; findings/phase-6er-amazon-profile-metadata-tx41-boundary.md`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71;UNKNOWN`
- Caller: Saved ordinary test caller: org.fireosresearch.phase6er.picker, UID 10219; production client universe/package/signature UNKNOWN
- Gate: Generated Stub interface token only for tx41; no method-local PROFILE_INTERACTION or UID check; downstream ActivityManager.getCurrentUser()/startActivityAsUser requires INTERACT_ACROSS_USERS
- Identity/user scope: No clearCallingIdentity()/restoreCallingIdentity() in tx41 slice; downstream sees ordinary Binder caller; explicit picker argument plus ActivityManager current-user lookup; no arbitrary user mapping proven
- Sink: mLaunchDataInfoMap lookup -> Intent.setClassName -> Context.startActivityAsUser
- Effect: ordinary APK reached Binder but was stopped before activity start; no HOME/PMS/package-state write
- Confidence/status: **ORDINARY_CALLER_REACHED_DOWNSTREAM_CROSS_USER_BLOCK** / `ORDINARY_CALLER_REACHED_DOWNSTREAM_CROSS_USER_BLOCK`
- Scope: Phase 10 worker row 10B-PROFILE-001; missing_edge=production caller package/UID/signature; service_manager/SELinux accepted edge; trusted caller-to-user mapping; any hidden tx41 consumer

## P10-DPM-004
- Phase/surface: `10` / `DevicePolicy/Profile IPC closure`
- Source: `fosservices/disassembly.log:73714-73812,78985-79006,79424-79464,80564; findings/phase-6er-amazon-profile-metadata-tx41-boundary.md`
- Evidence: `fosservices/disassembly.log:73714-73812,78985-79006,79424-79464,80564; findings/phase-6er-amazon-profile-metadata-tx41-boundary.md`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;UNKNOWN`
- Caller: Ordinary metadata provider can be any installed APK; probe package/UID is test-only; production provider/signature UNKNOWN
- Gate: Only target package ApplicationInfo.flags & SYSTEM_APP is checked; provider package, UID and signing certificate are not authenticated
- Identity/user scope: Local system-server Handler callback; no external Binder caller identity at map write; system-owned persistent map; no caller-selected Android user argument in this path
- Sink: mLaunchDataInfoMap and SharedPreferences launch_info_map_key
- Effect: ordinary metadata can seed a package/activity pair for a system-app target; downstream consumer and HOME/PMS effect are not proven
- Confidence/status: **PARTIAL_METADATA_INTEGRITY_ISSUE_CONSUMER_UNKNOWN** / `PARTIAL_METADATA_INTEGRITY_ISSUE_CONSUMER_UNKNOWN`
- Scope: Phase 10 worker row 10B-PROFILE-002; missing_edge=complete production metadata-provider inventory; exact map consumers; whether any consumer reaches HOME/PMS; persistent-map reset edge

## P10-DPM-005
- Phase/surface: `10` / `DevicePolicy/Profile IPC closure`
- Source: `boot-fosframework/disassembly.log:369180-369243,370637-370777; fosservices/disassembly.log:54297-54478,54847-54875; work/luna_worker_phase8b_kft_tx3_closure_20260810.md; work/luna_worker_phase9b_kft_client_identity_20260810.csv`
- Evidence: `boot-fosframework/disassembly.log:369180-369243,370637-370777; fosservices/disassembly.log:54297-54478,54847-54875; work/luna_worker_phase8b_kft_tx3_closure_20260810.md; work/luna_worker_phase9b_kft_client_identity_20260810.csv`
- SHA-256: `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71;ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;UNKNOWN;UNKNOWN`
- Caller: Semantic framework caller is AmazonUserManagerImpl.createChildUser(String); exact APK/native client package, UID and signing certificate UNKNOWN; framework candidates are not confirmed callers
- Gate: Stub enforces amazon.os.IAmazonUserManager interface token and decodes nullable UserInfo; no tx3-local UID/permission/MANAGE_USERS check shown; checkManageUsersPermission helper has no recovered tx3 edge
- Identity/user scope: Incoming Binder identity remains relevant before three package setters; later DPM empowerKftUser clear/restore is a separate branch and cannot be back-propagated; UserInfo.id supplied by child creation path; child/profile scope; no hard-coded User 0
- Sink: AmazonPackageManager setters: enable com.amazon.tahoe/.launcher.FreeTimeLauncherActivity; disable com.amazon.firelauncher and com.android.launcher3
- Effect: high-impact child/profile package-state writer; no formal HOME setter; ordinary User-0 route not proven
- Confidence/status: **STATIC_WRITER_CHILD_SCOPE_EXTERNAL_CALLER_UNKNOWN** / `STATIC_WRITER_CHILD_SCOPE_EXTERNAL_CALLER_UNKNOWN`
- Scope: Phase 10 worker row 10B-KFT-001; missing_edge=exact APK/native callsite and package/UID/signature; service-manager/SELinux client tuple; complete PMS cross-user/protected gate; proof of User 0 input

## P10-DPM-006
- Phase/surface: `10` / `DevicePolicy/Profile IPC closure`
- Source: `fosservices/disassembly.log:55053-55119; work/luna_worker_phase8b_kft_tx3_closure_20260810.md`
- Evidence: `fosservices/disassembly.log:55053-55119; work/luna_worker_phase8b_kft_tx3_closure_20260810.md`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;UNKNOWN`
- Caller: System-server local lifecycle call; no external package/UID/signature and no Binder transaction
- Gate: isUpgrade() plus AmazonUserManagerHelper.isChildUser(UserInfo) over UserManager.getUsers(); local trusted lifecycle predicate
- Identity/user scope: Local system-server context; no external Binder identity exists on this edge; each enumerated child UserInfo.id; child/profile only; no User 0 selector shown
- Sink: same KFT AmazonPackageManager component/application setters, followed by DPM/profile-owner empowerment branch
- Effect: trusted child-profile restoration/lifecycle behavior; not evidence of external tx3 authorization or ordinary User-0 control
- Confidence/status: **CONFIRMED_LOCAL_SYSTEM_SERVER_CHILD_SCOPE** / `CONFIRMED_LOCAL_SYSTEM_SERVER_CHILD_SCOPE`
- Scope: Phase 10 worker row 10B-KFT-002; missing_edge=exact boot lifecycle state and child predicate implementation join; downstream PMS acceptance per target user

## P10-DPM-007
- Phase/surface: `10` / `DevicePolicy/Profile IPC closure`
- Source: `fosservices/disassembly.log:54524-54566,370674-370777; work/luna_worker_parent_profile_dpm_sink_closure_20260810.csv`
- Evidence: `fosservices/disassembly.log:54524-54566,370674-370777; work/luna_worker_parent_profile_dpm_sink_closure_20260810.csv`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c;UNKNOWN`
- Caller: Saved ordinary APK reached tx4 in prior bounded test; exact production package/UID/signature UNKNOWN
- Gate: Stub interface token/parcel dispatch only in bounded slice; no tx4-local caller permission shown
- Identity/user scope: Binder.clearCallingIdentity() before Settings writes, then restore; sink executes with cleared/system identity; caller-supplied UserInfo.id; User 10 was the bounded observed scope; User 0 not established
- Sink: Settings.Secure.putIntForUser(user_setup_complete=1) and tv_user_setup_complete=1
- Effect: confirmed cross-user settings deputy in bounded evidence; no PMS/HOME/package-state sink
- Confidence/status: **CONFIRMED_SETTINGS_ONLY_DEPUTY_NO_HOME_EDGE** / `CONFIRMED_SETTINGS_ONLY_DEPUTY_NO_HOME_EDGE`
- Scope: Phase 10 worker row 10B-KFT-003; missing_edge=exact external caller package/UID/signature; service-manager/SELinux tuple; User-0 acceptance; any settings consumer leading to profile transition

## P10-DPM-008
- Phase/surface: `10` / `DevicePolicy/Profile IPC closure`
- Source: `artifacts/phase6ad/protected-broadcast-inventory-20260805-01/manifests/001_com.amazon.parentalcontrols__0_com.amazon.parentalcontrols.xmltree.txt:93-230; decompiled/jadx/parentalcontrols/sources/com/amazon/parentalcontrols/admin/ParentalAdminUtils.java:530-559; work/luna_worker_parent_profile_dpm_sink_closure_20260810.md`
- Evidence: `artifacts/phase6ad/protected-broadcast-inventory-20260805-01/manifests/001_com.amazon.parentalcontrols__0_com.amazon.parentalcontrols.xmltree.txt:93-230; decompiled/jadx/parentalcontrols/sources/com/amazon/parentalcontrols/admin/ParentalAdminUtils.java:530-559; work/luna_worker_parent_profile_dpm_sink_closure_20260810.md`
- SHA-256: `5ef89e517f53d6d3696df3a43df40502f651d57f0a27d62a445ddc518930c9db;UNKNOWN;c16b54b82a42c7ec41d3e0a943e7352428100c4b23cad90e024202b51ac5ed96`
- Caller: Package exact: com.amazon.parentalcontrols; runtime UID and signing certificate UNKNOWN in static manifest/privapp set; owner identity is existing User-0 Profile Owner
- Gate: isProfileOwnerApp/active-owner checks; exported UI does not establish arbitrary DPM relay; ParentalAdminUtils merges fixed parentalcontrols/SystemUI list
- Identity/user scope: Owner/DPM calls run in trusted owner/system-server context; no untrusted caller identity relay to a HOME writer shown; User 0 Profile Owner state; fixed package list; no arbitrary target-user/package input closed
- Sink: DPM policy persistence and AMS lock-task allowlist containing com.amazon.parentalcontrols and com.android.systemui
- Effect: real Profile Owner capability, but no arbitrary launcher package, Fire package-state, preferred-HOME, user creation or profile-transition sink shown
- Confidence/status: **PROFILE_OWNER_REAL_FIXED_INPUT_NO_ORDINARY_HOME_RELAY** / `PROFILE_OWNER_REAL_FIXED_INPUT_NO_ORDINARY_HOME_RELAY`
- Scope: Phase 10 worker row 10B-PARENT-001; missing_edge=runtime UID/signature and exact owner provisioning provenance; complete exported-component argument flow; any unindexed native/reflection caller

## P10-OTA-001
- Phase/surface: `10` / `OTA post-install/update closure`
- Source: `findings/phase-6my-ota-receiver-package-helper-closure.md; receiver source lines 27-61`
- Evidence: `findings/phase-6my-ota-receiver-package-helper-closure.md; receiver source lines 27-61`
- SHA-256: `c29b32bf6874b245859357d926773193c15771a6eb254f97edac57541ae5cb90`
- Caller: AmazonPackageManagerService.onBootPhase(550)
- Gate: PMS.isUpgrade plus protected action plus receiver permission filter
- Identity/user scope: system_server sender; receiver delivery UID unresolved; context-derived receiver/provider scope; numeric user UNKNOWN
- Sink: PackageHelper.enableComponent plus OOBEActivationHelper settings
- Effect: capability only; no runtime effect
- Confidence/status: **CONFIRMED_STATIC_BOUNDED** / `CONFIRMED_STATIC_BOUNDED`
- Scope: Phase 10 worker row 10C-001; missing_edge=complete runtime protected-broadcast union and exact delivery user

## P10-OTA-002
- Phase/surface: `10` / `OTA post-install/update closure`
- Source: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log lines 96087-96126`
- Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log lines 96087-96126`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Caller: system_server boot lifecycle
- Gate: phase 550 plus isUpgrade gate; not public app or shell entry
- Identity/user scope: system_server; no app or shell Binder identity; system-server context; exact delivery user UNKNOWN
- Sink: sendBroadcast BOOT_AFTER_SYSTEM_OTA
- Effect: post-OTA OOBE lifecycle event; not observed
- Confidence/status: **CONFIRMED_STATIC_BOUNDED** / `CONFIRMED_STATIC_BOUNDED`
- Scope: Phase 10 worker row 10C-002; missing_edge=exact runtime sender authorization and delivery sequencing

## P10-OTA-003
- Phase/surface: `10` / `OTA post-install/update closure`
- Source: `artifacts/phase6r/ota-ipc-static-audit-20260805-03/report.md; IOTAControlService lines 278-288`
- Evidence: `artifacts/phase6r/ota-ipc-static-audit-20260805-03/report.md; IOTAControlService lines 278-288`
- SHA-256: `a2e5280c773511f748a8553fe14d7145aa636071ec8bbf3596a4d423ca6583e5`
- Caller: OtaServiceConnectionManager.getService to ServiceBinder.bind to transaction 18
- Gate: exported true but CONTROLLER permission is signature|privileged
- Identity/user scope: service UID 10017; implementation caller identity unresolved; OTA service process scope; user scope UNKNOWN
- Sink: installSideload to SideloadInstaller to UpdateSystemWrapper.install
- Effect: privileged install capability behind bind gate; no transaction or install effect
- Confidence/status: **CONFIRMED_STATIC_BOUNDED** / `CONFIRMED_STATIC_BOUNDED`
- Scope: Phase 10 worker row 10C-003; missing_edge=implementation-side caller validation and native handoff

## P10-OTA-004
- Phase/surface: `10` / `OTA post-install/update closure`
- Source: `artifacts/phase6j/.../SideloadInstaller.java lines 65-85`
- Evidence: `artifacts/phase6j/.../SideloadInstaller.java lines 65-85`
- SHA-256: `98fe15a329e96ec793fc3f50172d945d9d409b734efce084af38bbef49248e4a`
- Caller: OTA service implementation internal call
- Gate: metadata and sanity checks plus device-state check
- Identity/user scope: caller marker unresolved; caller UID UNKNOWN; Sideload File from OTA app or service; user scope UNKNOWN
- Sink: UpdateSystemWrapper.install at SideloadInstaller line 44
- Effect: privileged install handoff capability; no OTA effect
- Confidence/status: **CONFIRMED_STATIC_BOUNDED** / `CONFIRMED_STATIC_BOUNDED`
- Scope: Phase 10 worker row 10C-004; missing_edge=exact implementation caller and recovery/native handoff

## P10-OTA-005
- Phase/surface: `10` / `OTA post-install/update closure`
- Source: `artifacts/phase6j/.../SideloadMover.java lines 31-44`
- Evidence: `artifacts/phase6j/.../SideloadMover.java lines 31-44`
- SHA-256: `59131cf032d8544cd44ea839ad63eb37993d2853b4925bf56d10ede721693f63`
- Caller: SideloadInstaller.installSideload line 74
- Gate: OTA data directory support plus sufficient external storage; basename concatenation and no canonicalPath or NOFOLLOW marker
- Identity/user scope: caller inherited from OTA app or service; UID UNKNOWN; external OTA data directory
- Sink: FileHelper.moveFile renameTo or copy/delete
- Effect: staging capability only; not executed
- Confidence/status: **CONFIRMED_STATIC_BOUNDED** / `CONFIRMED_STATIC_BOUNDED`
- Scope: Phase 10 worker row 10C-005; missing_edge=canonicalization symlink race atomicity SELinux label and caller identity

## P10-OTA-006
- Phase/surface: `10` / `OTA post-install/update closure`
- Source: `artifacts/phase6j/.../FileHelper.java lines 305-339`
- Evidence: `artifacts/phase6j/.../FileHelper.java lines 305-339`
- SHA-256: `55a7f44a70735626be7ebde25e96812346f336fddbec2c87de29ac0fb709b980`
- Caller: SideloadMover.maybeMoveSideloadFile line 41
- Gate: source exists and destination existence branch; no local Binder gate
- Identity/user scope: caller identity inherited and UNKNOWN; OTA external staging scope
- Sink: renameTo or FileOutputStream copy then source delete
- Effect: non-atomic fallback capability; no effect
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: Phase 10 worker row 10C-006; missing_edge=filesystem identity labels and no-follow semantics

## P10-OTA-007
- Phase/surface: `10` / `OTA post-install/update closure`
- Source: `artifacts/phase6j/.../SideloadVerifier.java lines 31-59; .../OSUpdateValidator.java lines 42-78`
- Evidence: `artifacts/phase6j/.../SideloadVerifier.java lines 31-59; .../OSUpdateValidator.java lines 42-78`
- SHA-256: `4ba31d323419575c4f9294d430bd6e758b38db68b7ff67405150a697cd549eea`
- Caller: SideloadVerifier line 42 and OSUpdateValidator lines 73-78
- Gate: metadata or sanity then android.os.RecoverySystem.verifyPackage; OSUpdateValidator also hash and update-property checks
- Identity/user scope: Java caller unresolved; downstream recovery identity UNKNOWN; package file path from Sideload or PendingUpdate
- Sink: RecoverySystem.verifyPackage
- Effect: verification capability; no verification executed
- Confidence/status: **CONFIRMED_STATIC_BOUNDED** / `CONFIRMED_STATIC_BOUNDED`
- Scope: Phase 10 worker row 10C-007; missing_edge=platform verifier certificate AVB rollback inputs

## P10-OTA-008
- Phase/surface: `10` / `OTA post-install/update closure`
- Source: `artifacts/phase6j/.../UpdateSystemWrapper.java lines 29-44`
- Evidence: `artifacts/phase6j/.../UpdateSystemWrapper.java lines 29-44`
- SHA-256: `c99f6884fa298546b18722a5addb46ae35aff4fa9c9f6003d8ad3ccaebe2edfdbd9`
- Caller: SideloadInstaller.installOSUpdate line 44
- Gate: external-to-media path replacement plus screen-state and install flags; controller gate upstream
- Identity/user scope: caller identity unresolved; context mContext and global update scope
- Sink: UpdateSystem.install(context path flags emptyMap)
- Effect: post-install or recovery handoff capability; no effect
- Confidence/status: **CONFIRMED_STATIC_BOUNDED** / `CONFIRMED_STATIC_BOUNDED`
- Scope: Phase 10 worker row 10C-008; missing_edge=authoritative UpdateSystem recovery caller SELinux and slot rollback handoff

## P10-OTA-009
- Phase/surface: `10` / `OTA post-install/update closure`
- Source: `artifacts/phase6mk-updater-dispatch-20260810-04/registration-dispatch.csv; updater-script-entrypoints.csv; artifacts/phase6md-native-updater-path-audit-20260810-02/path-write-call-edges.csv`
- Evidence: `artifacts/phase6mk-updater-dispatch-20260810-04/registration-dispatch.csv; updater-script-entrypoints.csv; artifacts/phase6md-native-updater-path-audit-20260810-02/path-write-call-edges.csv`
- SHA-256: `d88e35ec08d9ef0a55a3dbc17dc430b62d3b419810653542b6dd3077095cca24;4d0128ee85eec7b0c88716012858bef699f740907e46e854939c83a6c9e99077;7dc9e3ef08d9ef0a55a3dbc17dc430b62d3b419810653542b6dd3077095cca24`
- Caller: script parser to RegisterInstallFunctions and RegisterFunction
- Gate: saved script joins fixed block_image_update and package_extract_file entries; no external Binder caller proof
- Identity/user scope: updater or recovery identity UNKNOWN; fixed archive and by-name targets; user scope UNKNOWN
- Sink: WriteToPartition to ota_open and ota_write to open and write
- Effect: native partition-write capability only; not executed
- Confidence/status: **CONFIRMED_STATIC_BOUNDED** / `CONFIRMED_STATIC_BOUNDED`
- Scope: Phase 10 worker row 10C-009; missing_edge=unselected indirect dataflow recovery caller and authentication

## P10-OTA-010
- Phase/surface: `10` / `OTA post-install/update closure`
- Source: `artifacts/phase6ne-updater-cache-flow-20260810-03/direct-call-edges.csv`
- Evidence: `artifacts/phase6ne-updater-cache-flow-20260810-03/direct-call-edges.csv`
- SHA-256: `d653e4a84898509781a333c56502087a83981781fcf6612d7026bfd79602b477`
- Caller: PerformBlockImageUpdate at 0x409cb4 and 0x409cdc to CacheSizeCheck to MakeFreeSpaceOnCache
- Gate: sign-bit return gate; negative is error and nonnegative is success
- Identity/user scope: updater or recovery identity UNKNOWN; cache filesystem scope
- Sink: readlink_chk plus stat64 plus directory traversal plus unlink plus free-space helper
- Effect: cache cleanup capability only; no writer effect
- Confidence/status: **CONFIRMED_STATIC_BOUNDED** / `CONFIRMED_STATIC_BOUNDED`
- Scope: Phase 10 worker row 10C-010; missing_edge=returned path dataflow and relation to extraction or partition writer

## P10-OTA-011
- Phase/surface: `10` / `OTA post-install/update closure`
- Source: `work/luna_worker_phase6al_ota_indirect_closure_20260810.md; artifacts/phase6kt/recovery-verifier-audit-20260810-01/audit.json`
- Evidence: `work/luna_worker_phase6al_ota_indirect_closure_20260810.md; artifacts/phase6kt/recovery-verifier-audit-20260810-01/audit.json`
- SHA-256: `01e29ec3a2649d85d033ce7ce65034631ebb44ef00633e34a95b0eb063f317f9`
- Caller: UpdateSystem.install to RecoverySystem or native recovery boundary
- Gate: Java wrapper and static updater capability do not close verifier or rollback-index chain
- Identity/user scope: caller identity UNKNOWN; recovery and boot-control scope UNKNOWN
- Sink: AVB verification rollback index slot handoff UNKNOWN
- Effect: no effect and no bypass claim
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: Phase 10 worker row 10C-011; missing_edge=exact platform or native AVB descriptor rollback index and post-install executor

## P10-OTA-012
- Phase/surface: `10` / `OTA post-install/update closure`
- Source: `artifacts/phase6r/ota-ipc-static-audit-20260805-03/summary.json; work/luna_worker_ota_recovery_handoff_followup_20260810.md`
- Evidence: `artifacts/phase6r/ota-ipc-static-audit-20260805-03/summary.json; work/luna_worker_ota_recovery_handoff_followup_20260810.md`
- SHA-256: `UNKNOWN`
- Caller: no complete caller chain found from ordinary APK or UID 2000 to controller bind or install or recovery or update-binary or partition writer
- Gate: controller signature|privileged gate plus protected lifecycle gate plus fixed recovery script boundary
- Identity/user scope: ordinary app or shell identity does not cross preserved gates; user and partition scope unreachable from low privilege
- Sink: no sink established and Fire HOME is not an OTA sink
- Effect: no route or effect observed
- Confidence/status: **NEGATIVE_BOUNDARY_BOUNDED** / `NEGATIVE_BOUNDARY_BOUNDED`
- Scope: Phase 10 worker row 10C-012; missing_edge=complete exact-version caller SELinux and native provenance outside preserved corpus

## P10-DRV-001
- Phase/surface: `10` / `MTK/Amazon driver caller closure`
- Source: `Phase8D-001; Phase7C-001; init.mt8183.rc:302-303 and mtk_cmdq_device provenance`
- Evidence: `Phase8D-001; Phase7C-001; init.mt8183.rc:302-303 and mtk_cmdq_device provenance`
- SHA-256: `b3a54d37b4e498ff969a2717cb02cefc923ae6f39da32f5fd8529fe3dce6e899;6cb000e68c9391a2b954966944a41facb31d9c6fed8372c07b8fb4ce07441111;8bb5edcc5b5e1cf0bfb8e45cd14c1e185ac873c4d307e67594c024ccd3b69ad0`
- Caller: UNKNOWN: no exact shipped native ELF open()+CMDQ ioctl callsite; graphics/media/surfaceflinger/mediaserver policy references are not caller proof
- Gate: CONFIG_MTK_CMDQ=y; CONFIG_MTK_CMDQ_TAB=y; source OF match mediatek,gce; final Image/object/DTB join incomplete
- Identity/user scope: UNKNOWN: no Binder transaction or clearCallingIdentity chain reaches the node; UNKNOWN: no shipped UID/domain; policy references appdomain/graphics/media/surfaceflinger/mediaserver only
- Sink: cmdq ioctl -> async task/engine notification/readback -> MDP register/display/DMA path
- Effect: Potential display/engine/resource control; no package/PMS/HOME sink proven
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: Phase 10 worker row 10D2-001; missing_edge=compiled DTB/DT registration; final Image/module object; merged file_contexts+TE allow; native caller UID/domain and input-to-node edge

## P10-DRV-002
- Phase/surface: `10` / `MTK/Amazon driver caller closure`
- Source: `Phase8D-002/003; Phase7C-003/004; saved ion_device metadata and vendor_file_contexts`
- Evidence: `Phase8D-002/003; Phase7C-003/004; saved ion_device metadata and vendor_file_contexts`
- SHA-256: `abac518864faed94439d75d204e8c16ea75cf3a74c93ee50e128e0f6928a6d63;eb7fbf99acbc492d99d60c98fc62a67fe7350160c6e91dc033781d5bcd986411;8bb5edcc5b5e1cf0bfb8e45cd14c1e185ac873c4d307e67594c024ccd3b69ad0`
- Caller: UNKNOWN: libion.so/libion_mtk.so markers identify capability, not a shipped process or callsite
- Gate: CONFIG_ION=y; CONFIG_MTK_ION=y; CONFIG_ION_TEST absent; final heap/object/DT instance UNKNOWN
- Identity/user scope: UNKNOWN: no Binder caller-to-native ioctl chain or identity transition retained; UNKNOWN: saved metadata says system:graphics 0666, but shipped opener UID/domain is unresolved
- Sink: ION allocation/import/share/map/sync -> DMA buffer and heap state; MTK custom physical/secure paths
- Effect: Potential buffer/DMA or physical-address/secure-memory effect; no package/PMS/HOME sink proven
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: Phase 10 worker row 10D2-002; missing_edge=exact heap/object and DT/init registration; final node policy+allow; top-level native caller UID/domain; Binder-to-open boundary

## P10-DRV-003
- Phase/surface: `10` / `MTK/Amazon driver caller closure`
- Source: `Phase8D-004; Phase7C-002; init.mt8183.rc:295-296; source proc mode 0`
- Evidence: `Phase8D-004; Phase7C-002; init.mt8183.rc:295-296; source proc mode 0`
- SHA-256: `6351de00903a282ba682427095a155794efd8221f253ff11a0f74ed7c5cb86c6;6cb000e68c9391a2b954966944a41facb31d9c6fed8372c07b8fb4ce07441111;db5cd91b8d25170ad27809ace8cdbbd2a3f838ec72e2598a4f6b5a44953d322e`
- Caller: UNKNOWN: no exact shipped native proc opener or operation caller
- Gate: Source proc registration; active /dev/M4U_device misc branch is #if 0; final DT/object join UNKNOWN
- Identity/user scope: UNKNOWN: no Binder identity chain; init policy is not a caller chain; UNKNOWN: init record system:media 0440 does not establish actual domain or proc label
- Sink: proc control -> DMA/IOMMU mapping, port configuration, power and monitor/TF state
- Effect: Potential DMA/IOMMU/device-state effect; no package/PMS/HOME sink proven
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: Phase 10 worker row 10D2-003; missing_edge=compiled DTB/object delivery; exact proc genfscon+allow; native caller UID/domain and input boundary

## P10-DRV-004
- Phase/surface: `10` / `MTK/Amazon driver caller closure`
- Source: `Phase8D-005; Phase7C-008; uinput source and native/SELinux negative inventory`
- Evidence: `Phase8D-005; Phase7C-008; uinput source and native/SELinux negative inventory`
- SHA-256: `98b41492311d9b9fb9ccbfe269a2fddc0fb436f3048b7887e1f6e5482d36211a;20a47a755613dcfd967624d9821060534e9cda38286a7bb2f8ee777ed9e9a225;9d1313d25cb45492d5656d03f05b7e60f5d037ccef15c20d9edec5e0fdbf17f9`
- Caller: UNKNOWN: native inventory found no exact shipped ELF open/write/ioctl caller
- Gate: CONFIG_INPUT_UINPUT=y; final object/node creation unresolved; no local capable() gate in inspected source
- Identity/user scope: UNKNOWN: no Binder-to-uinput chain or identity-preserving native path; UNKNOWN: node mode/owner/type/SELinux allow and caller UID/domain absent
- Sink: uinput create/destroy/write -> synthetic input device and kernel input graph
- Effect: Potential downstream user-facing input-state effect; no package/PMS/HOME sink proven
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: Phase 10 worker row 10D2-004; missing_edge=final ueventd mode/owner; file_contexts+allow; shipped object; native caller UID/domain; input boundary

## P10-DRV-005
- Phase/surface: `10` / `MTK/Amazon driver caller closure`
- Source: `Phase8D-006; Phase7C-006; source registration and config/Image markers`
- Evidence: `Phase8D-006; Phase7C-006; source registration and config/Image markers`
- SHA-256: `5ffbce942417fc6aca773d90e4c6935f508087f9a80d96138a7ecc30561ed327;077a7cff0d60ae2329986382ef91118819045c3540ec76d0d9eeffb2c67230e3`
- Caller: UNKNOWN: no exact shipped native open/ioctl/proc/sysfs writer
- Gate: CONFIG_MTK_AUXADC_INTF=y; platform registration source present; final DT/object/selected instance UNKNOWN
- Identity/user scope: UNKNOWN: no Binder identity chain or caller transition; UNKNOWN: source writable bits do not establish final label, allow, UID, or domain
- Sink: ADC/register diagnostic and calibration read/write paths
- Effect: Potential hardware/diagnostic/calibration state effect; no package/PMS/HOME sink proven
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: Phase 10 worker row 10D2-005; missing_edge=compiled DT/DT registration and final object; exact proc/sysfs/device labels+modes+allow; native writer UID/domain

## P10-DRV-006
- Phase/surface: `10` / `MTK/Amazon driver caller closure`
- Source: `Phase7C-010; gpl driver surface inventory; trona_defconfig negative gate`
- Evidence: `Phase7C-010; gpl driver surface inventory; trona_defconfig negative gate`
- SHA-256: `6c2309f996cacafaab35cce3935bcb725a5259211751af89df88d3732797029e`
- Caller: UNKNOWN: no production open/write caller; test-only source path
- Gate: CONFIG_AMZN_DRV_TEST=y not found in trona_defconfig; source Kconfig default n; production delivery conditional
- Identity/user scope: UNKNOWN: no Binder chain; test dispatcher identity not established; UNKNOWN: proc label/init import/TE allow and any caller UID/domain absent
- Sink: conditional test dispatcher -> factory-reset or RTC special-mode state for selected indices
- Effect: High-impact factory/engineering effect is source-capable but not shipped-confirmed; no low-privilege route proven
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: Phase 10 worker row 10D2-006; missing_edge=product config/object/module; proc label+allow; production caller UID/domain; Binder/input boundary

## P10-DRV-007
- Phase/surface: `10` / `MTK/Amazon driver caller closure`
- Source: `Phase7C-009; Phase6UN Amazon-LD join; source attrs 0664 and platform registration`
- Evidence: `Phase7C-009; Phase6UN Amazon-LD join; source attrs 0664 and platform registration`
- SHA-256: `4ef656e1a4e54bce29c6f54d62478b5b68dd093abe2641b85ee15feb1f30d1bc`
- Caller: UNKNOWN: no shipped native sysfs writer or caller
- Gate: CONFIG_AMAZON_LD=y and CONFIG_AMAZON_LD_SWITCH=y; DT compatible amzn,ld/selected instance UNKNOWN
- Identity/user scope: UNKNOWN: no Binder identity chain or caller transition; UNKNOWN: sysfs owner/group, label, TE allow, UID/domain absent
- Sink: stop/control/threshold/interval/ADC controls -> liquid detection and device behavior
- Effect: Potential liquid/thermal/USB behavior change; no package/PMS/HOME sink proven
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: Phase 10 worker row 10D2-007; missing_edge=matching compiled DTB node; final object; sysfs label+allow; native writer UID/domain

## P10-DRV-008
- Phase/surface: `10` / `MTK/Amazon driver caller closure`
- Source: `Phase7C-011; thermal_core source/config provenance`
- Evidence: `Phase7C-011; thermal_core source/config provenance`
- SHA-256: `3cb614b7c82c9f933e0dd436702b1f7e29d03307b3a1758d860b1b082897caf9`
- Caller: UNKNOWN: no shipped thermal writer or native caller
- Gate: CONFIG_THERMAL=y and CONFIG_THERMAL_WRITABLE_TRIPS=y; final zones/providers/DT UNKNOWN
- Identity/user scope: UNKNOWN: no Binder-to-sysfs chain or identity transition; UNKNOWN: sysfs labels/allow and provider-specific mode absent
- Sink: thermal trip/emulation/governor writes -> thermal/power/availability state
- Effect: Potential thermal throttling, power, or availability effect; no package/PMS/HOME sink proven
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: Phase 10 worker row 10D2-008; missing_edge=compiled DTB zone/provider; sysfs policy; final native writer UID/domain

## P10-DRV-009
- Phase/surface: `10` / `MTK/Amazon driver caller closure`
- Source: `Phase7C-013; USB devio source/config provenance`
- Evidence: `Phase7C-013; USB devio source/config provenance`
- SHA-256: `655a3f79b2230031e0f2dfef4fbb699d832db9054debf47fd5186acec0af2768`
- Caller: UNKNOWN: no preserved USB ioctl/URB caller
- Gate: CONFIG_USB=y plus selected controller drivers; final USB node/policy not joined
- Identity/user scope: UNKNOWN: no Binder/native caller chain or identity transition; UNKNOWN: usbfs node label/allow and caller UID/domain absent
- Sink: USB control transfer/URB -> peripheral and hardware state
- Effect: Potential USB peripheral/control-transfer effect; no package/PMS/HOME sink proven
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: Phase 10 worker row 10D2-009; missing_edge=final usbfs node mode/owner; file_contexts+allow; controller DT/object; native caller UID/domain

## P10-DRV-010
- Phase/surface: `10` / `MTK/Amazon driver caller closure`
- Source: `Phase7C-014; rpmb-mtk source/config provenance`
- Evidence: `Phase7C-014; rpmb-mtk source/config provenance`
- SHA-256: `a6b070190ad8b97173c129509e6d8f8ae8c9f0d383bc349be44d9c919387c8d5`
- Caller: UNKNOWN: rpmb_svc/name markers do not identify exact shipped open+ioctl caller
- Gate: RPMB/MMC registration/config correspondence only; final object/module promotion UNKNOWN
- Identity/user scope: UNKNOWN: no Binder identity chain or clearCallingIdentity boundary; UNKNOWN: node mode/file_contexts/allow/capable tuple and caller UID/domain absent
- Sink: authenticated persistent-storage ioctl/state -> RPMB mutation or authenticated read
- Effect: Potential authenticated storage mutation; low-privilege reachability and package/HOME effect unproven
- Confidence/status: **UNKNOWN** / `UNKNOWN`
- Scope: Phase 10 worker row 10D2-010; missing_edge=final object; node mode/label+allow; capability gate; native/Binder caller UID/domain
