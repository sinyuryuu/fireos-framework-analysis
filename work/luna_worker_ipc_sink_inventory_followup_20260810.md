# Host-only IPC sink inventory follow-up — 2026-08-10

Scope: saved decompiled APK/JAR/VDEX, Binder contract tables, and existing
Phase 6 reports only. No Binder transaction, service call, broadcast, provider
write, package setter, or private API was invoked for this follow-up.

## Reading rule

`Holder metadata` means a manifest/package/permission or published-service fact
only. It does not establish that the holder can reach a caller-controlled
method, pass its gate, or drive the listed sink. `Caller reachability` is listed
separately and requires a saved ordinary-caller result, a bounded static caller
edge, or is explicitly marked unresolved. Confidence labels are evidence
confidence, not exploitability claims.

## Inventory

| ID | Caller → manifest/service gate → user/profile scope | clearCallingIdentity | Sink | Saved runtime result | Reachability / confidence |
|---|---|---|---|---|---|
| IPC-01 | Ordinary APK UID 10198 → `amazonactivitymanager`; method checks `com.amazon.permission.APP_PREWARM`, but saved path discards the result → caller supplies package, flags, and user ID (tested User 0) | Yes; identity cleared before PackageManager lookup/process start and restored on normal path | `IPackageManager.getApplicationInfo` → `ActivityManagerService.startProcessLocked(..., "prewarm", ...)` | `service=amazonactivitymanager handle=true`; tx1 returned `0`; target PID appeared; temporary packages removed; User-0 HOME, preferred state, Fire package state, and users unchanged | **Caller reachability confirmed** for process/resource effect. No HOME/package/user sink in the bounded method. Strong/confirmed runtime evidence. Evidence: `findings/phase-6er-amazon-prewarm-confused-deputy.md`; `adb/phase6er/PHASE6ER-UNTRUSTED-SERVICE-LOOKUP-20260806-134346/`; `decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log:3642543-3642622` |
| IPC-02 | Ordinary APK UID 10223 → `amazonusermanagerservice`, Binder tx4/interface token; no method-local UID/permission gate visible → caller supplies `UserInfo.id=0` | Yes; before both settings writes; restored on success/exception paths | `AmazonUserManagerHelper.putIntForUser`: `user_setup_complete=1`, `tv_user_setup_complete=1` | `service handle=true`; tx4 returned true; User 0 values became `1/1`; exact rollback succeeded; HOME/package state unchanged | **Caller reachability confirmed** for User-0 settings sink. No HOME/package setter. Confirmed. Evidence: `findings/phase-6gv-amazon-user-manager-tx4-settings-deputy.md`; `adb/phase6gv/PHASE6GV-USERMANAGER-TX4-20260807-02/`; `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54524-54566` |
| IPC-03 | Ordinary APK UID 10227 → same `amazonusermanagerservice` tx4 contract; no method-local UID/permission gate visible → caller supplies `UserInfo.id=10` (stopped child profile) | Yes; same tx4 implementation clears identity around writes | Same two `putIntForUser` setup-state writes, scoped by caller-supplied UserInfo ID | `service handle=true`; tx4 returned true; armed User 10 `0/0` became `1/1`; exact rollback true; User-0 HOME/setup/package state unchanged | **Cross-user caller reachability confirmed** for bounded settings deputy. No package/HOME sink. Confirmed. Evidence: `findings/phase-6gi-amazon-user-manager-tx4-user10-deputy.md`; `adb/phase6gv/PHASE6GV-AMAZON-USER-MANAGER-TX4-USER10-20260807-02/`; `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54524-54566` |
| IPC-04 | Amazon child/profile lifecycle → `amazonusermanagerservice` / IAmazonUserManager tx3; private service-manager + SELinux boundary and child/KFT predicate; `UserInfo.id` comes from child lifecycle | No clear-identity edge established in the bounded tx3 writer | `AmazonPackageManager.setComponentEnabledSetting`, `setApplicationEnabledSetting`, and Tahoe/Fire/Launcher3 component-state updates for supplied child user | Prior controlled evidence: User 10 cross-user gate and User-0 protected-component gate rejected before mutation; no private tx3 replay in this phase | **Static sink confirmed; ordinary caller reachability not established.** Child/profile-scoped, not formal User-0 HOME selector. Strong evidence. Evidence: `findings/phase-6fi-fk-amazon-user-manager-tx-boundary.md`; `findings/phase-6pr-kft-tx3-authorization-closure.md`; `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54297-54325,54415-54478`; `output/tables/phase6mn-ipc-user-scope-20260810-01.csv:4,11-13` |
| IPC-05 | H2 household service `IH2ClientService` → exported service is `BIND_SERVICE` signature-bound; workflow/account checks → adult/child user ID is created by trusted workflow | Not observed in recovered H2 Stub/helper path; helper reaches Amazon user manager through trusted workflow | `AmazonUserManager.createAdultUser/createChildUser` and downstream profile lifecycle | No shell route; no low-privilege caller found; no dynamic test allowed. Saved evidence describes profile creation/removal only | **Service/profile route statically present, ordinary reachability not established.** No User-0 HOME writer in bounded APK evidence. Strong evidence. Evidence: `output/tables/phase6mn-ipc-user-scope-20260810-01.csv:2-3`; `artifacts/phase6mc-alta-static-20260810-01-manifest.txt:144-154`; `H2ClientService.java:105-107`; `AndroidUserHelper.java:78-81` |
| IPC-06 | `AmazonPackageManagerService.onBootPhase(550)` → system-server boot phase + `PackageManagerService.isUpgrade()`; broadcast action is protected-broadcast metadata and receiver has no `android:permission` claim in reviewed manifest → receiver context/user scope, exact ID unresolved from callsite | No ordinary caller identity; trusted system-server lifecycle sender | `PackageHelper.enableComponent(OobeHomeActivity)` → `OOBEActivationHelper.activateOOBEIF` → `Settings.Secure` setup/OOBE flags | Static/live saved state: OobeHomeActivity is User-0 disabled, HOME priority 100; manual broadcast/OTA/OOBE trigger rejected; no runtime mutation performed | **Lifecycle sender and sinks confirmed; ordinary caller relay unproven and risk-rejected.** Not a shell HOME selector. Confirmed static, strong authorization boundary. Evidence: `findings/phase-6q-bootafter-system-ota.md`; `findings/phase-6r-bootafter-system-ota-authorization.md`; `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96107-96126`; `output/tables/phase6mo-oobe-context-user-scope-20260810-01.csv:2-6` |
| IPC-07 | Play Store holder metadata → data-app internal verifier/enterprise-policy paths; captured package-state grants, but exact invoking component/input and any relay are unknown → internally derived package/component target | No identity relay to a Fire target proven in bounded audit | Generic `setApplicationEnabledSetting` / `setComponentEnabledSetting` writers; no preferred HOME writer or Fire literal in bounded scan | No writer was invoked; Fire-target mutation was not attempted; framework protected-package rejection remains saved evidence | **Holder metadata confirmed; caller reachability and Fire-target path unresolved.** Do not infer bypass from grant. Probable static evidence. Evidence: `findings/phase-6mb-vending-permission-and-state-writer-audit.md`; `output/tables/phase6mn-ipc-user-scope-20260810-01.csv:8`; `output/tables/phase6ps-privilege-route-closure.csv:2-3` |
| IPC-08 | Amazon DPM restriction / preferred-state surfaces → trusted Device Owner/Profile Owner or policy-admin gate; ordinary caller not proven → policy user scope | Saved candidate path clears identity around restriction helper; exact method-local identity handling varies by method | User restriction and trusted persistent-preferred/package policy sinks | No ordinary caller result; saved route matrix classifies DPM preferred writer as trusted path and no ordinary effect | **Trusted holder/role metadata and static sink only; ordinary caller reachability unclosed but not demonstrated.** No transaction or Device Owner creation. Strong evidence. Evidence: `output/tables/phase6pr-privilege-route-matrix.csv:5`; `output/tables/phase6mt-amazon-ipc-candidates-20260810-01.csv` (DPM rows); `output/call-graphs/phase6et-amazon-dpm-restriction-gate-class.mmd` |

## Closure notes

The private Amazon contracts are published and their Proxy/Stub mappings are
confirmed, but saved service-manager checks show the shell cannot find the
selected private services. Therefore publication, interface descriptors,
transaction codes, and permission-holder metadata are not equivalent to
ordinary-app reachability. The two confirmed ordinary-app routes in this
inventory are the tx1 process-prewarm sink and tx4 settings sink (including the
saved cross-user User 10 result); neither writes HOME or Fire package state.

The package/component-state candidates remain split: tx3 has a real static
child-scoped writer but saved framework gates reject the tested User-0/User-10
mutation; OOBE and ProductPolicy writers are lifecycle/in-process paths; Play
Store grants are holder metadata plus generic internal writers, not proof of a
Fire-targeted caller path. Existing route-closure results therefore leave no
saved low-privilege HOME replacement route.

## Evidence and safety boundary

All evidence paths above are repository-relative except where a referenced
table itself records an absolute decompilation path. This follow-up performed
host-only reads and wrote only the paired inventory files named by the task.
