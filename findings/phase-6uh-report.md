# Phase 6UH — bounded permission, KFT and control-surface integration

This host-only bundle integrates the missing H2 candidate search, KFT transaction-3 authorization review, and exact-build Amazon permission-grant parser review. It broadens the sink question beyond Launcher: a system-level caller could affect package/component state, user-scoped policy, or other privileged state, but no accepted ordinary-app or shell path to such a sink is established here.

Generation HEAD: `131991c6ae5650f83836af84a13510e8343a2df4`.

## Safety boundary

No device operation was performed in this phase: no adb, Binder bind/call, `service call`, transaction construction, user creation/switch, package or permission mutation, Fire Launcher mutation, driver operation, OTA, reboot, Root/exploit attempt, or partition write.

## Inputs

- **6UA H2 grant/client:** `work/luna_worker_phase6ua_h2_grant_client_20260810.md` (76f847a4b3842874870e88d02f35b117ee075ed39608ce1c1e6e12d731e33ac9); `work/luna_worker_phase6ua_h2_grant_client_20260810.csv` (19ff5c49265689cb0d0e64324760c29c85e1e34c86134b349e7f89bd2a95d306); 12 row(s).
- **6UB KFT caller/scope:** `work/luna_worker_phase6ub_kft_caller_scope_20260810.md` (985baf87524b8c11746268ee861e430e9fc5ac26594268107cbc9f2dc4f858c4); `work/luna_worker_phase6ub_kft_caller_scope_20260810.csv` (03a5b7c38a1ab02f38a49e5d3c16e611e2ce72c1d056cc36a8de85b84d287f19); 7 row(s).
- **6UC Amazon permission semantics:** `work/luna_worker_phase6uc_amazon_perm_semantics_20260810.md` (f101c66f0d13e83ffadaa6cf0a718d23e084bb09016426263c5a38f2a05051a2); `work/luna_worker_phase6uc_amazon_perm_semantics_20260810.csv` (37dcc749b5fff557bc3612eab502b696ec044647ea88f914022d5c9974a84aba); 14 row(s).
- **6UE H2 missing candidates:** `work/luna_worker_phase6ue_h2_missing_candidates_20260810.md` (3088ca5ac2b0ca8682c40f3d9374933e1106169e5ac82f16e5fa1e715a838c48); `work/luna_worker_phase6ue_h2_missing_candidates_20260810.csv` (1df5c08e36c1c752c25a9388ace6d494828b8b946a01daa23b25a83c3c679423); 32 row(s).
- **6UF KFT tx3 gate:** `work/luna_worker_phase6uf_kft_gate_20260810.md` (04cb8f5c74966ad94c0dbdf9de3dc60b03f5c349632321a92e7e6b6f20d2075b); `work/luna_worker_phase6uf_kft_gate_20260810.csv` (9a14b249b8741918de259d186dbc22509c8862e39ab55aeab005c7fa5688b833); 12 row(s).
- **6UG permission parser:** `work/luna_worker_phase6ug_permission_parser_20260810.md` (86f9940ae703a03b1ee6fae76d33fc30d797777d4bc811a1fa026c1e64a93b85); `work/luna_worker_phase6ug_permission_parser_20260810.csv` (396f9990baadef8cebffaceca53cf8852cc88f556b942950757c2571bb4809d1); 13 row(s).

Context hashes: `findings/phase-6ud-report.md` (39c2c605ba946a7a5c773cb06bd0b8efa6fc44d671b1837889f7a60d270d7172); `findings/phase-6ud-evidence-index.md` (449fee8e61808f4f86078463da38f89907fa717d9702ac5e7ea4d99c53248938); `output/tables/phase6ud-control-surface.csv` (ad6b6e2bc527d9132d311ba794f878cf38d733eda7dc4971e7ace56e7c93e004); `findings/phase-6tz-report.md` (fb73aebc8abcbc14f3e8877387511bc74b29936f9f584aef548f716d2749aa5e); `findings/phase-6tv-report.md` (e766794a9683923e11a723e11d4e1b772512212745699f8e071e5ac0bb4cd31f)

## Findings

### 1. Amazon permission-grant hook — **已證實 / CONFIRMED**

The exact-build `fosservices` disassembly contains `com.android.server.pm.permission.AmazonPermissionsGranter.grantSignaturePermission` at `codeOff=0xd242a`. Its compiled branches inspect the `BasePermission.protectionLevel` vendor bit `0x80000000`, return the SELinux grant result for that branch, then inspect `0x40000000` and consult `FireOsSystemConfig.getAmzRestrictedPermissions(packageName)`. The neighboring `addAmazonPermissions` path at `codeOff=0xd24ca` checks the SELinux policy `amazon_policies/grant_amazon_permissions` before adding Amazon cross-user permission names. This is a confirmed Amazon-specific grant hook, not evidence of a shell bypass.

### 2. `android.amazon.perm` ownership — **已證實 / CONFIRMED**

The exact package artifact is a core/system-shared-UID package and owns the custom permission records. The observed `0x80000002` values are artifact-level evidence consistent with a signature base plus an Amazon vendor flag. The exact FireOS symbolic parser mapping and shell/ordinary-app eligibility remain `UNKNOWN`; do not treat the numeric value as a grant.

### 3. KFT child-state writer — **已證實 / STRONG_STATIC**

`IAmazonUserManager` transaction 3 is `enableKftLauncher(UserInfo)`. Its recovered Stub enforces the interface token and unmarshals `UserInfo`, then dispatches the method without a visible method-local UID, `MANAGE_USERS`, or cross-user check in the bounded slice. The sink uses `UserInfo.id` to enable Tahoe `FreeTimeLauncherActivity` and set Fire Launcher/Launcher3 application state to disabled for that same user. Confirmed internal callers are child creation and an upgrade boot phase guarded by `isUpgrade()` and `isChildUser()`. External caller access, service-manager policy and downstream PackageManager authorization remain `UNKNOWN`. This is an authorization review point, not a demonstrated confused deputy or exploit.

### 4. H2 client candidates — **待驗證 / UNKNOWN**

Ten candidate grant records remain, but the bounded corpus closes neither a candidate-specific `bindService` → `ServiceConnection` → `IH2ClientService` path nor a runtime client. Three preserved XML trees show requested permission names; seven candidate permission fields remain unavailable. AVOD's separate `PlaybackSdkService` bind and caller check is not H2 evidence.

## Control-surface interpretation

The strongest current model is: a privileged Amazon/system-server identity owns the relevant permission and user/package-state sinks; KFT's recovered writer is user-scoped and can change more than HOME when reached; the missing evidence is the caller and authorization boundary. No evidence presently justifies invoking a private Binder transaction, crafting a service payload, opening a driver, or claiming root. The remaining safe work is artifact-preserving static closure of candidate manifests/callers and exact runtime read-only correlation.

## Verdict

- **已證實:** Amazon permission-grant control flow and owner artifact; KFT child writer sink and two internal lifecycle callers.
- **高可信推論:** the relevant package/user-state effects require an Amazon/system identity or a caller accepted by additional service/SELinux/PackageManager gates.
- **待驗證:** H2 external client, KFT tx3 external authorization, full parser semantics, and downstream PMS outcome.
- **已排除:** no accepted ordinary-app/shell route has been shown in the bounded evidence; this does not prove universal absence.
- **因風險拒絕測試:** private Binder transaction replay, arbitrary `UserInfo` injection, package-state mutation, driver/ioctl probes, Root and boot/partition operations.

Integrated rows: `90`; parse warnings: `0`.

Warnings:
- None detected.
