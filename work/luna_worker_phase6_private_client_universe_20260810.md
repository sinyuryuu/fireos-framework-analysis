# Phase 6 — Amazon private Binder client/caller universe

日期：2026-08-10。這是 host-only、bounded 的完整索引；「完整」指本次指定的 decompiled/jadx、baksmali、fosinit、既有 findings/output corpus，而不是對未取得的 APK/native code 作全域否定。未送 Binder transaction，未執行 service call、root、input injection、OTA、reboot、ioctl 或設備修改。

## 結論

在指定 corpus 中，Amazon private Binder 路徑可分為：

* system_server 發佈的 `amazonusermanagerservice`、`amazonprofileservice`、`amazonpackagemanager`、`amazonactivitymanager`、`amazonwindowmanager`、`amazonaccessibilitymanager`、`amazondevicepolicymanager`、`amazon_input`；以及 `fosdebug`。其中 User/Profile/Package/Activity/Window/Input/Accessibility/DPM 是 system_server service；`fosdebug` 是 FireOSDebugService 的 diagnostics Binder/local service。
* boot framework 內的 `ServiceManager.getService()` client 與 generated `Stub.asInterface()` proxy 已被定位。已知實際 client 包括 `AmazonUserManagerImpl`（child-user/KFT lifecycle）、`AmazonProfileManager`（profile operations）、`AmazonPackageManager`/`FtvSpecAssertionUtility`（package metadata/classification）、`AmazonAccessibilityService`、`AmazonActivityManagerImpl`、以及 system_server 內對 Amazon service 的 callbacks/helpers。
* ordinary APK 曾能取得 `amazonusermanagerservice` handle（`PHASE6FH-USERMANAGER-INTERFACE-20260807-01`、UID 10210）並在 bounded tests 送出特定 transaction；shell UID 2000 在保存的 SELinux capture 對 private service `find` 被拒絕。這兩者不可混為「ordinary APK 可任意呼叫」或「shell 可達」。
* 最接近 HOME/package-state 的邊界是：`IAmazonUserManager.enableKftLauncher(UserInfo)` 的 child/profile-scoped Fire/Tahoe/Launcher3 component-state 路徑，以及 `IAmazonProfileService` 的 profile picker/start-launcher helper。前者不是普通 HOME setter，後者不是 preferred-HOME/package-state writer。
* `IAmazonPackageManager` 四個 flags/metadata mutator 確實寫入 `AmazonApplicationFlags` 檔案；既有 closure 找不到其到 `setHomeActivity`、preferred、`setApplicationEnabledSetting` 或 `setComponentEnabledSetting` 的 downstream edge。這是 **Confirmed/Strong negative bounded result**，不是 permission 缺字串即可推論漏洞。
* 已確認的 ordinary-app confused-deputy 是 UserManager tx4 的 setup-state writer（Finding **F-108**），以及 ActivityManager tx1 prewarm 的 permission-result defect（`PHASE6ER`）；兩者均未到 HOME/package-state sink。未找到 ordinary APK 或 shell 能寫 User-0 Fire HOME 的完整鏈。

## Input SHA / evidence index

| corpus / artifact | SHA-256 / identity | 用途 |
|---|---|---|
| `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log` | `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71` | Stub/Proxy、ServiceManager client、Amazon manager implementations |
| `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` | `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` | publication、BinderService、local sinks |
| `output/tables/phase6mt-amazon-ipc-candidates-20260810-01.csv` | existing table；rows cover five core interfaces | method/gate/sink index |
| `output/tables/phase6mr-amazon-input-manager-20260810-01.csv` | `10a7ea5396f498e2c00fac94844519b3db6e5386e2d7901a49e973286a618ae3` | 26 `IAmazonInputManager` methods |
| `artifacts/phase6mr-amazon-input-manager-20260810-01/method-matrix.csv` | same phase artifact；summary `e5888be4f032cee8fe4ce546199893924898521f2c2183e68d4aaa714e016beb` | Input closure |
| `output/tables/phase6mu-amazon-application-flags-20260810-01.csv` | existing table | flags/metadata persistence and consumer scan |
| `output/tables/phase6kv-pms-home-callers.csv` | `dc1a86ea85904e3775704944fa86364a9a89033f6146eed0dac8b324b7028382` | standard PMS HOME caller negative comparison |
| `output/tables/phase6ak-launcher-user-service.csv` | existing table; source SHA above | UserManager publication/client/KFT sink |

Confidence labels in this report are **Confirmed**, **Strong evidence**, **Probable**, **Hypothesis**, **Disproved**, and **Unknown**. A static absence is always scope-limited.

## 1. Service publication and caller classes

| service | publication / owner | service class | known clients/callers | caller class | assessment |
|---|---|---|---|---|---|
| `amazonusermanagerservice` | `fosservices/disassembly.log:54894,55106`; `publishBinderService` at `55106` | `AmazonUserManagerService.BinderService` in system_server | `AmazonUserManagerImpl.createChildUser` (`boot-fosframework/disassembly.log:369203–369243`); ordinary probe handle | trusted framework; ordinary APK observed; shell denied by AVC | publication and trusted client **Confirmed**; ordinary reachability **Confirmed**; shell reachability **Disproved for saved capture** |
| `amazonprofileservice` | `fosservices/disassembly.log:80813–80823` | `AmazonProfileService.BinderService` in system_server | `AmazonProfileManager` (`boot-fosframework/disassembly.log:29462–29832`); profile callbacks/helpers | framework/privileged profile client; shell `find` denied | client and publication **Confirmed**; shell route **Disproved for saved capture** |
| `amazonpackagemanager` | `fosservices/disassembly.log:96056–96098` | `AmazonPackageManagerService.BinderService` in system_server | `FtvSpecAssertionUtility.getAmazonPackageManager` (`boot-fosframework/disassembly.log:5374–5377`); `AmazonPackageManager` facade | boot framework/system-side; ordinary caller not proven | service handle and proxy **Confirmed**; external caller **Unknown** |
| `amazonactivitymanager` | `fosservices/disassembly.log:40958`; service block begins around `39808` | `AmazonActivityManagerService.BinderService` in system_server | `AmazonActivityManagerImpl`; system_server callbacks; ordinary prewarm probe | framework/system; ordinary APK prewarm caller tested; shell service not found | static client and tx1 ordinary reachability **Confirmed**; HOME writer **Disproved in reviewed sink** |
| `amazonwindowmanager` | `fosservices/disassembly.log:56234–56244` | `AmazonWindowManagerService.BinderService` in system_server | framework/window helpers; no separate ordinary client established | system/framework; external caller unknown | publication/proxy **Confirmed**; caller **Unknown** |
| `amazon_input` | `fosservices/disassembly.log:21872–21880,22644–22670`; input service onStart around `160953–160961` | `AmazonInputManagerService.BinderService` in system_server | `AmazonInputManager`/input framework; callback clients | privileged/framework; transaction caller not established in static corpus | interface method map **Confirmed**; direct HOME sink **Disproved in bounded matrix** |
| `amazonaccessibilitymanager` | `fosservices/disassembly.log:032804–032808,35432` | `AmazonAccessibilityManagerService.BinderService` in system_server | `AmazonAccessibilityService` (`boot-fosframework/disassembly.log:07005a–0700f6`) | accessibility/framework | client and canvas sink **Confirmed**; HOME/package sink **Disproved in bounded slice** |
| `amazondevicepolicymanager` | `fosservices/disassembly.log:46146–46156` | `AmazonDevicePolicyManagerService.BinderService` in system_server | framework DPM facade; no low-privilege client proven | system/privileged | publication/proxy **Confirmed**; HOME/package sink **Disproved in bounded slice** |
| `fosdebug` | `fosservices/disassembly.log:412–576`; `core_fosinit.xml` / vendor registration | `FireOSDebugService`, diagnostics/local Binder | `IFireOSDebugManager` descriptor only; `dumpsys fosdebug` consumer | shell diagnostics subject to `DUMP`; no custom transaction found | read-only diagnostics **Strong evidence**; state writer **Disproved in inspected code** |

## 2. Generated Proxy / transaction index

### `IAmazonUserManager`

The interface descriptor is `amazon.os.IAmazonUserManager`; generated Stub/Proxy and `enableKftLauncher(UserInfo)` are at `boot-fosframework/disassembly.log:371513–371789`. Transaction 3 dispatches to `enableKftLauncher(UserInfo)`; transaction 4 is `setUserSetupComplete(UserInfo)`; transactions 5/6 cover active profile type. The generated dispatch enforces only the interface token in the bounded block; method-local authorization must be reviewed separately. **Confirmed static; authorization outside cited method blocks Unknown.**

* Trusted client: `AmazonUserManagerImpl.createChildUser` calls `enableKftLauncher`, then `setUserSetupComplete`; failures remove the new user (`boot-fosframework/disassembly.log:369203–369243`). **Confirmed; system/framework client.**
* tx3 server sink: `enableKftLauncherComponent(UserInfo)` at `fosservices/disassembly.log:54297–54325` uses supplied `UserInfo.id`, enables Tahoe launcher and disables `com.amazon.firelauncher` and Launcher3 through package/component setters. **Confirmed child/profile-scoped package-state sink; not a formal HOME setter.**
* tx4 server sink: `setUserSetupComplete(UserInfo)` writes setup settings with supplied `UserInfo.id` after `clearCallingIdentity` (`findings/phase-6gv-amazon-user-manager-tx4-settings-deputy.md`; OTA disassembly `3656667–3656709`). Ordinary APK UID 10223 reached UserInfo.id 0 in `PHASE6GV-USERMANAGER-TX4-20260807-02`; this is **Confirmed F-108**, a settings-state confused deputy, not a Fire/HOME writer.
* tx5: `setActiveProfileType` is guarded by `MANAGE_USERS` in `PHASE6GM-USERMANAGER-TX5-20260807-02`; ordinary APK read tx6 only. **Confirmed gate; no HOME sink.**
* shell: `amazonusermanagerservice` is listed, but shell UID 2000 `service_manager find` is denied in `PHASE6BS-AMAZON-USER-MANAGER-SELINUX-20260805-01`. **Disproved as current shell route.**

### `IAmazonProfileService`

`AmazonProfileManager` obtains `amazonprofileservice` (`boot-fosframework/disassembly.log:29462–29491`) and forwards profile methods, including `delistProfile`, `disableAppForProfile`, `enableAppForProfile`, `filterEvent`, `filterKeyEvent`, `getActiveProfileForApp`, `getAppListForProfile`, `initiateLauncher`, and `isAppEnabledForProfile` (`29491–29832`). This is the complete manager-to-interface forwarding family found in the boot disassembly; no generated method is interpreted as a HOME setter merely because it contains “launcher”.

* `initiateLauncher`: `fosservices/disassembly.log:76246–76256`, guarded by `enforceProfileInteractionPermissions` at `78949–78966`. **Confirmed permission-gated profile interaction; no HOME/preferred/package-state call.**
* `startProfilePicker` tx41: `fosservices/disassembly.log:77222–77280`; `PROFILE_INTERACTION` is signature|privileged and the bounded method starts the configured picker with `startActivityAsUser`. `PHASE6ER-PROFILE-METADATA-FIRE-TX41-20260807-03` foregrounded only the probe picker and preserved Fire HOME/package invariants. **Confirmed profile-picker start; HOME replacement Disproved.**
* Generic profile HOME helper: `fosservices/disassembly.log:74281–74312` creates MAIN/HOME intent for `UserHandle.CURRENT`; `80106–80114` posts `AmazonProfileService$20`; `80435–80450` calls `startLauncherActivity`. This is a **Confirmed static launcher-start path**, but `PHASE6GS-APS-HOME-TRIGGER-20260807-02` showed Fire Launcher, no preferred/package mutation, and absent profile-picker feature. It is not evidence of a third-party HOME selector.

### `IAmazonPackageManager`

Proxy range `boot-fosframework/disassembly.log:402917–403398`; service publication `fosservices/disassembly.log:96136`. The 11 methods and transaction codes are:

| tx | method | bounded server range / sink | result |
|---:|---|---|---|
| 1 | `setAmazonFlagsForUser(List,int,int)` | `95991–96008`; `AmazonApplicationFlags.setApplicationInfoForUserLocked` → `writeToFile` (`95531–95547`) | metadata/flags writer **Confirmed**, permission `amazon.permission.ADD_RM_PKG_METADATA` consumed |
| 2 | `removeAmazonFlagsForUser(List,int,int)` | `95955–95972`; `removeApplicationInfoForUserLocked` → `writeToFile` (`95473–95488`) | metadata/flags writer **Confirmed**, same permission |
| 3 | `getAmazonFlagsForUser(String,int)` | `95889–95895` | read wrapper **Confirmed** |
| 4 | `setAmazonMetadataForUser(String,List,List,int)` | `96009–96025`; `setAmazonMetadataForUserLocked` → `writeToFile` (`95548–95555`) | metadata writer **Confirmed**, same permission |
| 5 | `removeAmazonMetadataForUser(String,List,int)` | `95973–95990`; `removeAmazonMetadataForUserLocked` → `writeToFile` (`95489–95496`) | metadata writer **Confirmed**, same permission |
| 6/7 | `registerProxyReceiver(Intent,PendingIntent)` / `deregisterProxyReceiver(Intent)` | `95943–95954` / `95877–95888` | broadcast/proxy surface **Strong evidence**; effective external authorization **Unknown** |
| 9/10 | `isFtvSpecApp(String)` / `isPreInstalledAppWithFtvSpec(String)` | `95929–95942` | classification/read **Confirmed** |
| 8 | `shouldAllowMicAccess(String)` | `96027–96036`; delegates to `AudioRecordPermissionEnforcer.shouldAllowMicAccess` | policy/read helper **Confirmed static**; downstream consumer not HOME |
| 11 | `getConfigurationHelper()` | `95896–95928` | configuration/read helper **Confirmed** |

`AmazonApplicationFlags.init/readFromFile/writeToFile` are bounded at `fosservices/disassembly.log:95327–95642`; `phase6mu` found file persistence and a package-recency broadcast consumer (`17467–17540`), but no call to `setHomeActivity`, `replacePreferredActivity`, `addPersistentPreferredActivity`, `setApplicationEnabledSetting`, or `setComponentEnabledSetting`. Therefore the strongest defensible result is **Strong evidence: metadata-only with no demonstrated HOME/package-state consumer**. Do not infer a vulnerability from any missing permission string; the four mutators explicitly consume `ADD_RM_PKG_METADATA`.

### `IAmazonActivityManager`

Proxy range `boot-fosframework/disassembly.log:394353–394885`; server methods are in `fosservices/disassembly.log:39808–40680`. The complete method family in `phase6mt` is:

`preWarmApplicationForUser` tx1; `packageLifetimeHint` tx2; `checkKillAppGoingIntoBg` tx3; `getRecentCrashes` tx4; `registerActivitySwitchObserver` tx5; `unregisterActivitySwitchObserver` tx6; `onActivityResume` tx7; `getCpuLoad` tx8; `isOnHomeStack` tx9; `requestCpuBoost` tx10; `dismissMultiWindow` tx11; `dismissPipWindow` tx12; `disablePipWindows` tx13; `enablePipWindows` tx14.

`preWarmApplicationForUser` checks `APP_PREWARM` at `40472–40474`, then clears identity and reaches `startProcessLocked` at `40480–40503`; the check result is not consumed in the bounded block. `PHASE6ER-UNTRUSTED-SERVICE-LOOKUP-20260806-134346` confirmed ordinary-app transaction 1/process effect. This is **Confirmed permission-result defect / Strong evidence confused deputy**, but process start only; HOME and Fire package state were unchanged. `onActivityResume`, `isOnHomeStack`, and observer methods are **Strong evidence HOME-adjacent callbacks**, not selectors.

### `IAmazonWindowManager`

Proxy `boot-fosframework/disassembly.log:400006–400264`; publication `fosservices/disassembly.log:56244`; server block `56070–56179`. Methods: `lockNow` tx1, `setOverscan` tx2, `getLidState` tx3, `isPipActive` tx4, `setPipVisibility` tx5, `stopAppPinningMode` tx6. WMS/status-bar/PIP sinks are **Confirmed**; no HOME/preferred/component/package-state sink is present in the bounded implementation. Caller permissions are partly downstream/unknown; do not treat missing local permission text as a vulnerability. Classification: **Confirmed static mapping; HOME sink Disproved in bounded slice; external caller Unknown.**

### `IAmazonInputManager`

This interface is already closed by `PHASE6MR-STATIC-20260810-01` and is included here to avoid a false gap. Proxy/transaction matrix is `artifacts/phase6mr-amazon-input-manager-20260810-01/method-matrix.csv`; service `amazon_input`; 26 remote methods. `inject`/`injectSequence` carry Binder pid/uid to native sinks, while listener/filter methods carry `GET_KEYEVENTS` or event-register gates. The matrix contains no direct resolver/preferred/component writer. Classification: **Confirmed static method universe; Strong evidence indirect input path; direct HOME sink Disproved; caller reachability Unknown.** No injection was performed.

### `IAmazonAccessibilityManager`, `IAmazonDevicePolicyManager`, `IFireOSDebugManager`

* Accessibility proxy `394117–394266`, tx1/2/3 `magnificationCanvasAddLine`, `magnificationCanvasAddRect`, `magnificationCanvasClear`; server `35298–35344`; `DRAW_MAGNIFICATION_RECT` gate around `032760–0328e4`. **Confirmed canvas surface; HOME/package sink Disproved in bounded slice.**
* DPM proxy `397105–397282`, tx1 `setRestrictionForUser`, tx2 `clearRestrictionForUser`, tx3 `getBackedUpPoliciesFile`; publication `46156`; implementation `45935–46108`. Restriction writes use explicit user IDs and `clearCallingIdentity` around `UserManager.setUserRestriction`; `MANAGE_USERS` protects backup read. **Confirmed policy-state sink; HOME/package sink Disproved in bounded slice; non-system caller Unknown.**
* `IFireOSDebugManager` has no custom method surface in the inspected interface block; `fosdebug` is a dump/diagnostics endpoint with `DUMP` checks. **Strong evidence read-only; custom mutation Disproved in inspected code.**

## 3. HOME / preferred / package-state sink cross-index

| sink | Amazon path reviewed | status |
|---|---|---|
| `setHomeActivity` / `replacePreferredActivity` / persistent preferred | `phase6kv` 25-row standard PMS caller table; Amazon private interfaces and `phase6mt` scan | **Confirmed negative in bounded Amazon corpus**; no additional Amazon caller found |
| `setApplicationEnabledSetting` / `setComponentEnabledSetting` | UserManager KFT child path at `54297–54325`; OOBE helper `phase6MY`; standard PMS gate `services/disassembly.log:500744–500765` | KFT/OOBE writers **Confirmed**, but KFT is child/profile-scoped and OOBE is lifecycle/context-scoped; ordinary User-0 Fire workaround **Disproved** |
| Fire literal | `enableKftLauncherComponent`: Tahoe, Fire, Launcher3 literals (`54297–54325`); Fire Launcher HOME runtime evidence in `HOME-T01/T02`, `HOME-PREF-T17`, `HOME-T18/T19` | Fire literal in KFT path **Confirmed**; User-0 HOME replacement **Disproved by existing tests** |
| `startHome` / explicit HOME start | Profile generic runner `74281–74312`; launcher wrapper `80106–80114`; branch `80435–80450`; ordinary HOME resolver evidence `HOME-T01/T02` | **Confirmed static start paths**; they resolve/start Fire in saved tests, not a third-party selector |
| package flags/metadata | `AmazonApplicationFlags` `95327–95642`; mutator server methods `95866–96037` | **Confirmed persistence; Strong evidence no HOME/package-state consumer** |

The ordinary PMS path remains separately protected: `setHomeActivity` calls `replacePreferredActivity` and standard package/component setters enter known permission/protected-package gates. Existing `PACKAGE-T01/T03/T05`, `HOME-PREF-T17`, `HOME-T18/T19`, and `PHASE6KV-HOST-CALLER-INDEX-20260810-01` are evidence, not new tests.

## 4. Caller universe by trust domain

| domain | callers / entry points | what is established |
|---|---|---|
| system_server / local | `AmazonUserManagerService`, `AmazonProfileService`, `AmazonPackageManagerService`, `AmazonActivityManagerService`, WMS/AMS callbacks, `FireOSDebugService` | publication, local sinks, identity transitions and lifecycle branches are **Confirmed** where cited |
| boot framework / trusted client | `AmazonUserManagerImpl`, `AmazonProfileManager`, `AmazonPackageManager`, `FtvSpecAssertionUtility`, `AmazonAccessibilityService`, `AmazonActivityManagerImpl` | ServiceManager handle → Stub/interface → method forwarding is **Confirmed** at cited offsets |
| priv-app / privileged | profile/OOBE/launcher helpers and Amazon Settings wrappers in existing tables | context/profile lifecycle and component helpers are **Confirmed**; no proof of ordinary User-0 Fire HOME writer |
| ordinary APK | UID 10210 handle/descriptor probe; UID 10223 tx4; UID 10221 tx5/6; `PHASE6ER` tx1 prewarm; profile tx41 probe | selected methods are reachable in saved tests; effects are setup-state/process/profile-picker only. No arbitrary private-service/HOME conclusion is justified |
| shell UID 2000 | private service `find` denied for User/Profile and candidate Amazon writer handles not found in `PHASE6EP-AMAZON-WRITER-REACHABILITY-20260809-191243` | **Confirmed current boundary; shell private Binder route Disproved for saved capture** |

## 5. Findings / test IDs and final disposition

* **F-108 / `PHASE6GV-USERMANAGER-TX4-20260807-02` — Confirmed:** ordinary APK supplied `UserInfo.id=0` to setup-state writer; cleanup restored captured settings and Fire HOME remained unchanged. This is a real bounded confused deputy, not a launcher takeover.
* **`PHASE6ER-UNTRUSTED-SERVICE-LOOKUP-20260806-134346` — Confirmed / Strong evidence:** ordinary APK reached ActivityManager prewarm tx1; ignored `APP_PREWARM` result plus cleared identity reached `startProcessLocked`. Process-only effect; no HOME/package sink.
* **`PHASE6FH-USERMANAGER-INTERFACE-20260807-01` — Confirmed:** ordinary APK obtained UserManager handle, pinged Binder, and queried descriptor. It did not establish arbitrary tx3 authorization.
* **`PHASE6GM-USERMANAGER-TX5-20260807-02` — Confirmed:** `setActiveProfileType` is MANAGE_USERS-gated; read tx6 returned active profile type only.
* **`PHASE6GS-APS-HOME-TRIGGER-20260807-02` — Confirmed:** profile generic HOME trigger started Fire Launcher and preserved HOME/package invariants.
* **`PHASE6ER-PROFILE-METADATA-FIRE-TX41-20260807-03` — Confirmed:** tx41 started the profile picker under profile interaction boundary; no preferred/package mutation.
* **`PHASE6MR-STATIC-20260810-01` — Confirmed:** `amazon_input` 26-method matrix; no direct HOME/package writer.
* **`PHASE6KV-HOST-CALLER-INDEX-20260810-01` / `PHASE6KV-DEVICE-REACHABILITY-20260809-191243` — Confirmed:** standard HOME/PMS caller inventory and current private-service reachability boundary; no additional Amazon preferred-HOME writer.
* **`HOME-T01/T02/T17/T18/T19`, `PACKAGE-T01/T03/T05` — Confirmed existing controls:** tested unlocked HOME resolves to `com.amazon.firelauncher/.Launcher`; normal preferred record and shell package/component disable attempts do not replace/disable Fire.

### Overall classification

**Confirmed:** service publication, generated Proxy/Stub mappings, known trusted clients, KFT/profile/package metadata sinks, selected ordinary-app boundaries, and saved shell SELinux boundaries.

**Strong evidence:** `AmazonApplicationFlags` persistence without a demonstrated HOME/package-state consumer; prewarm permission-result defect; HOME-adjacent profile/Activity callbacks.

**Probable:** none claimed as a vulnerability. A private interface being reachable, or a local permission literal being absent from a truncated method block, is insufficient.

**Hypothesis:** an unindexed APK/native client or an unreviewed callback could add a path outside this corpus; no such path is asserted.

**Disproved:** current shell route to private services; ordinary private Binder path as a demonstrated User-0 Fire HOME replacement; direct HOME/preferred sink in Input/Window/Accessibility/DPM/Package metadata slices.

**Unknown:** complete authorization of every bounded wrapper where the permission helper is external; unindexed APK/native callers; runtime behavior of private services on builds not represented by the saved captures.

No device or repository file other than this report was modified.
