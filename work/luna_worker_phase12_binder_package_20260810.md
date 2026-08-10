# Phase 12 — Amazon Framework/Binder/package-state writer closure

日期：2026-08-10。範圍：主機端既有 artifacts、decompiled、firmware source、findings 的只讀整理。未執行 adb、裝置變更、root、exploit、未知 service call 或未知 Binder transaction；未提出或執行 payload。

工作區確認：

- `pwd`: `/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire`
- Git HEAD：`aeb8709519ab4c4cb5b9fc3e835f5cf30a9f5568`
- 工作區原已有未提交變更；本 phase 僅新增本報告與同名 CSV。

## 結論

保存的兩份精確 disassembly 中，21 個 `setComponentEnabledSetting` / `setApplicationEnabledSetting` callsite 已由 Phase 6MH 索引。Amazon 相關 writer 可閉合為：KFT writer 是 supplied `UserInfo.id` 的 child/profile lifecycle sink；ProductPolicy 是 trusted policy-file/user-list sink，精確 PS7331 policy input 沒有 Fire Launcher；OOBE/Gemini/Espresso 只見固定或受 gate 的非-HOME 目標；AmazonPackageManager 私有 Binder 沒有 HOME、preferred-activity 或 enabled-state 方法，facade 會回到標準 PMS gate。

現有證據沒有形成「普通 app 或 shell → User 0 Fire package/component state → HOME/UID0」的閉合路徑。普通 app 可取得 `amazonusermanagerservice` descriptor/handle，但 tx3 的完整 caller authorization 與任意 `UserInfo` parcel edge 沒有在本 phase 重播；已知 runtime child writer 仍只歸因於 child user。DPM generic restriction branch 的下游 active-admin/owner gate 阻斷普通 app；ProxyReceiver 的 system-app creator gate 也阻斷普通 APK。這是 reachability/authorization closure，不是漏洞或 payload 結論。

## Closure 規則

每一列都按 `caller → permission_or_gate → binder_identity → user_scope → sink → observed_effect` 記錄。若保存材料未能證明其中一段，CSV 直接填 `UNKNOWN`，不以 service name、exported、interface descriptor 或 setter callsite 推導出權限、UID、user 0 或可達 sink。

逐條矩陣見 [CSV](./luna_worker_phase12_binder_package_20260810.csv)。重點如下：

| Surface | Caller / gate | User scope | Exact sink / observed effect | 判定 |
|---|---|---|---|---|
| KFT / `IAmazonUserManager` tx3 | trusted child lifecycle；private service boundary；完整 tx3 local check UNKNOWN | `UserInfo.id`；已觀測 child User 10 | Amazon facade → PMS tx90/tx92；Tahoe/Fire/Launcher3 child state | 非 User-0 closed route |
| `IAmazonPackageManager` tx1–11 | metadata writers require `amazon.permission.ADD_RM_PKG_METADATA`；private contract has no package/HOME setter | per-user metadata arguments；cross-user validation UNKNOWN | metadata/flags/proxy/query only | 非 HOME/package enabled sink |
| Amazon facade setters | trusted caller enters ordinary `IPackageManager` | KFT uses supplied child id；other callers UNKNOWN | PMS component/application setters | 受 PMS permission/protected/cross-user gate |
| ProductPolicy | system-server callback；trusted policy file + user list | policy-selected user list | `AmazonPackageManager` setters | exact PS7331 policy has no Fire target |
| OOBE/Gemini/Espresso | lifecycle/observer/metadata gates | several callsites UNKNOWN | fixed Registration, Gemini, BOOT receiver targets | no Fire/HOME target in bounded context |
| preferred/HOME | PMS standard permissions, resolver, DPM owner/admin checks | explicit `userId`/`AsUser` in some paths | `replacePreferredActivity`, persistent preferred, `setHomeActivity` | no ordinary-app User-0 writer proven |
| Amazon DPM | Amazon keys require `MANAGE_USERS`; generic branch reaches DPM active-admin/owner checks | parcel userId, downstream validation | `UserManager`/DPM restriction state | no package/HOME sink |
| ProxyReceiver | PendingIntent creator must be system app | creator/service context; cross-user UNKNOWN | internal receiver + PendingIntent send | ordinary APK returned false; no callback |
| LauncherHijackPreventer | system-server callback registration | package/user bookkeeping | visibility boolean, READ_LOGS policy, fdrw bookkeeping | not HOME selector |
| Fire Launcher | runtime exported HOME activity, priority 50 | User 0 runtime observation | resolver selects `com.amazon.firelauncher/.Launcher` | target state, not writer |

## Exported component / permission review

The bounded manifest and service registrations distinguish three things that must not be conflated:

1. `com.amazon.firelauncher/.Launcher` is an exported-by-runtime Android 9 HOME activity with `MAIN`, `HOME`, `DEFAULT`, priority 50. This establishes the resolver candidate and observed User-0 selection, not a write capability.
2. `amazonpackagemanager`, `amazonusermanagerservice`, and `amazondevicepolicymanager` are system-server/private Binder publications. Ordinary app handle reachability is separately observed for some services; shell `service check` denial does not imply ordinary-app denial, and interface reachability does not imply method authorization.
3. `LauncherHijackPreventer` is registered at system-server callback boundaries, not shown as an exported app service/receiver/provider. Its bounded code handles visibility and permission/package bookkeeping and contains no direct HOME selector.

The full exported service/receiver/provider inventory is not complete in the preserved corpus. Therefore the final inventory row explicitly records `UNKNOWN` for the unresolved component list, per-component permission, Binder identity, user scope, and sink. No missing component is promoted to a route.

## Sink-specific findings

### Component/application enabled state

The 21-callsite Phase 6MH inventory is the authoritative host-side setter index. High-value Amazon rows are:

- `AmazonUserManagerService$BinderService.enableKftLauncherComponent(UserInfo)` at `fosservices/disassembly.log:54297-54325`: Fire/Tahoe/Launcher3 literals, but user id comes from `UserInfo.id` and existing evidence attributes the effect to child lifecycle.
- `EnableDisableComponentAction.enableDisableComponent` at `fosservices/disassembly.log:293661-293770`: policy-file/user-list driven; exact policy audit has no `com.amazon.firelauncher` entry.
- `AppAdapterHandler.goToRegistration` at `:26038-26066`: fixed `com.amazon.tv.oobe/.RegistrationActivity`.
- `GeminiHandler.disableGeminiIfRequired` at `:30322-30355`: fixed Gemini package.
- `EspressoShotCallback` at `:191872-191892` and `:192056-192160`: gated BOOT receiver map.
- ordinary shell path `PackageManagerShellCommand.runSetEnabledSetting` at `services/disassembly.log:500744-500765`: standard PMS protected-package boundary.

### Preferred activity / HOME

`AmazonPackageManagerImpl.replacePreferredActivity` delegates to ordinary PMS. Standard PMS preferred methods show `SET_PREFERRED_APPLICATIONS` checks and user markers; DPM persistent-preferred methods require active-admin/owner context. `setHomeActivity` is a standard PMS sink (tx89), not an Amazon private Binder method. The bounded corpus does not close a normal app or shell caller through these gates to a User-0 Fire/HOME mutation.

### KFTUserManager / ChildUserManager

`IAmazonUserManager` ordinary-app service-handle reachability is real, but only descriptor/lookup evidence was used here. The state-changing tx3 is not replayed. Existing child/profile findings show the known writer consuming `UserInfo.id`, with child User 10 effect. The exact tx3 Stub caller check and whether an arbitrary caller can construct a valid lifecycle `UserInfo` remain `UNKNOWN`; this missing edge prevents claiming either exploitability or a User-0 path.

### AmazonPackageManager / DPM / proxy

The private package interface has metadata, flags, FTV/configuration, mic policy, and proxy receiver methods. Its metadata writers have `ADD_RM_PKG_METADATA`; it has no formal package enabled/HOME setter. The facade's setters use standard PMS. DPM tx1/tx2 reaches downstream active-admin/owner validation for generic restrictions, while Amazon restriction keys require `MANAGE_USERS`; neither branch reaches package/HOME state. Proxy tx6/tx7 checks `PendingIntent` creator system-app status; the ordinary APK test returned false and no callback.

## Final reachability decision

**No closed ordinary-app/shell path to User-0 Fire state, HOME, or UID 0 was found in the bounded evidence.** The strongest residual unknowns are completeness of the exported component inventory, exact tx3 authorization/parcel edge, exact OOBE numeric user mapping, and unpreserved native/overlay/reflection edges. Those are recorded as missing edges, not silently resolved. No device test or mutation is justified by the present host-side evidence.

## Evidence inputs

- `findings/phase-6mh-package-state-writer-closure.md`
- `artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv`
- `findings/phase-6ia-amazon-package-manager-closure.md`
- `findings/phase-6ep-amazon-writer-reachability.md`
- `findings/phase-6fh-amazon-user-manager-interface-boundary.md`
- `findings/phase-6bk-kft-component-state-boundary.md`
- `findings/phase-6ce-product-policy-firelauncher-boundary.md`
- `findings/phase-6et-amazon-dpm-restriction-gate.md`
- `findings/phase-6ip-amazon-proxy-receiver-gate.md`
- `findings/phase-6am-launcher-hijack-preventer.md`
- `findings/firelauncher-manifest-analysis.md`
- `artifacts/phase6mw-home-state-sinks-20260810-01/phase6mw-home-state-sinks.md`

