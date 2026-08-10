# Binder caller→permission→identity→sink closure map

Date: 2026-08-10. Scope is host-only static analysis of the saved PS7331
decompilation, `fosinit` registrations, manifests, and prior Phase 6 evidence.
No Binder transaction was sent, no service was invoked, and no device state was
changed. “Proven” below means that the saved evidence closes the ordinary-app
caller and the sink; static method presence or a missing permission string is
not proof of low-privileged reachability.

## Result

The remaining private/exported surfaces reduce to three classes:

* Confirmed bounded ordinary-app deputies: ActivityManager tx1 reaches a
  system-identity process-start sink; UserManager tx4 reaches setup settings.
  Neither is a package/component/HOME/system-UID writer.
* High-impact static writers whose low-privileged reachability is not proven or
  is blocked downstream: UserManager tx3/KFT, DPM restriction, OOBE lifecycle,
  and metadata/proxy receiver paths.
* Protected, query-only, resource-only, or indirect input/window/callback
  surfaces. These are recorded to close false leads, not classified as
  privilege escalation.

No candidate in this map proves a low-privileged caller can mutate User-0 HOME,
preferred activities, arbitrary package/component enabled state, role state,
device-owner/profile-owner state, credentials, or system UID/root identity.

## Closure table

The machine-readable version is
`work/luna_worker_binder_sink_closure_20260810.csv`. Ranges are offsets in the
named disassembly log, not source line numbers.

| ID | Service / entry | Caller → permission | Identity boundary | Sink and disposition |
|---|---|---|---|---|
| A1 | `amazonactivitymanager`; `IAmazonActivityManager` tx1 `preWarmApplicationForUser` | Ordinary APK was observed reaching tx1 (UID 10198); `APP_PREWARM` check at `fosservices:40472-40474`, result not consumed | `clearCallingIdentity` before application lookup/process start (`fosservices:40480-40503`) | `startProcessLocked(...,"prewarm",...)`; confirmed process/resource deputy only. No package/component/HOME sink. **Proven bounded effect; not LPE.** |
| U3 | `amazonusermanagerservice`; `IAmazonUserManager` tx3 `enableKftLauncher(UserInfo)` | Stub dispatch has interface-token enforcement; method-local caller gate is not shown in bounded block. Trusted child/KFT client at `boot-fosframework:369203-369243`; ordinary tx3 reached service but PMS later gates | No caller-identity clear established before the relevant PMS calls | `enableKftLauncherComponent(UserInfo)` at `fosservices:54297-54325` enables Tahoe and disables Fire/Launcher3 using supplied user ID. User 10 cross-user and User 0 component gates rejected in Phase 6FJ/6FK. **Strong static writer; low-privileged mutation disproven on saved build.** |
| U4 | `amazonusermanagerservice`; tx4 `setUserSetupComplete(UserInfo)` | Ordinary APK UID 10223 reached supplied UserInfo.id 0 in Phase 6GV; no effective method-local authorization in the bounded path | Clears identity before settings writes (`fosservices:3656666-3656709`; also summarized in Phase 6GV) | `Settings.Secure.putIntForUser` / setup-state writes. **Confirmed settings-state deputy; fixed setup flags only, no package/HOME sink.** |
| P1 | `amazonprofileservice`; `IAmazonProfileService.initiateLauncher` | `com.amazon.device.permission.PROFILE_INTERACTION`, enforced by `enforceProfileInteractionPermissions` (`fosservices:78949-78966`) | No relevant caller-identity relay shown | Internal profile flow, method body `fosservices:76246-76256`; no preferred/HOME/package setter. **Permission-gated; ordinary reachability unknown.** |
| P2 | `amazonprofileservice`; `startProfilePicker` tx41 | Method-local marker/permission is not observed in bounded block; service is private and shell `find` was denied | No relevant clear-identity-to-PMS writer shown | Explicit configured picker + `startActivityAsUser` (`fosservices:77222-77280`). **Profile UI launch, not HOME resolver mutation; ordinary reachability unknown.** |
| P3 | `amazonprofileservice`; generic launcher helper | Framework/profile client (`AmazonProfileManager`, `boot-fosframework:29462-29832`); external caller unknown | No low-privileged relay established | MAIN/HOME intent and `startLauncherActivity` (`fosservices:74281-74312`, `80106-80114`, `80435-80450`). Saved runtime resolves Fire HOME; no preferred/package write. **Static launcher-start false lead.** |
| M1 | `amazonpackagemanager`; tx1/2/4/5 metadata/flags mutators | `ADD_RM_PKG_METADATA` is consumed by mutators; ordinary caller not proven | No relevant clear-identity-to-PMS writer | `AmazonApplicationFlags` file persistence (`fosservices:95327-95642`, tx methods `95866-96037`). Consumers are flags/recency/game-mode/AppCompat; no HOME, preferred, enabled-state, or component setter. **Metadata sink; not escalation.** |
| M2 | `amazonpackagemanager`; tx6/7 proxy receiver register/deregister | Effective external authorization and caller universe unknown; service-manager shell lookup denied | Identity handling not closed | Proxy receiver/broadcast path (`fosservices:95943-95954`), downstream sink not closed. **Unknown; do not infer escalation from missing local check.** |
| D1 | `amazondevicepolicymanager`; tx1 restriction setter | Device-policy/system caller path; low-privileged caller not proven | Identity cleared around `UserManager.setUserRestriction` (`fosservices:46101-46107`) | User restriction state only (`fosservices:45935-46108`). No role, owner, package/component, or HOME writer. **Trusted policy sink; ordinary relay unknown.** |
| I1 | `amazon_input`; `IAmazonInputManager.inject` / `injectSequence` tx1/2 | Java Binder block records caller PID/UID; helper `checkInjectEventsPermission` exists but callsite/enforcement is not closed (`fosservices:19508-19714`) | Caller PID/UID passed to native sink; no clear-identity boundary shown | `nativeInject`/`nativeInjectSequence`; indirect input could affect UI, but no resolver/preferred/component writer. **Authorization unknown; no proven security mutation.** |
| I2 | `amazon_input`; key interceptor/listener/filter family | `GET_KEYEVENTS`, `ACCESS_EVENT_REGISTER`, `FILTER_INPUT_EVENTS`/signature-or-Amazon gates appear in reviewed methods (`fosservices:19777-20547`, `19829-19999`) | Calling UID used for interceptor checks; no relevant clear-identity relay | Callback/input-filter state. Potential Home-key influence is indirect and no HOME selector sink is present. `setInputFilter` local authorization is incomplete in bounded excerpt. **Protected/unknown, not LPE.** |
| W1 | `amazonwindowmanager`; lock/overscan/PIP methods | Published private service; external caller unknown; shell `find` denied | Identity/permission closure incomplete | Window/PIP/overscan/status-bar operations (`fosservices:56070-56179`, publication `56234-56244`). No package/component/HOME sink. **Static boundary; false lead for requested sink class.** |
| O1 | `BootAfterSystemOTAReceiver` / OOBE `enableIncrementalFlow` | Delivery requires `RECEIVE_BOOT_AFTER_SYSTEM_OTA` signature|amazon; sender requires boot phase 550 and upgrade state | Lifecycle receiver runs in trusted OOBE context; no ordinary relay proven | May enable `OobeHomeActivity`; evidence `findings/phase-6q-binder-service-and-oobe-audit.md`, Phase 6P/6KT. **High-impact lifecycle candidate, reachability unknown; trigger intentionally not replayed.** |
| O2 | DeviceSoftwareOTA controller/update boundary | `com.amazon.dcp.ota.permission.CONTROLLER` signature|privileged | Recovery/update identity boundary; no ordinary caller | Partition/block-image and post-install lifecycle sink. **Static capability only; OTA execution prohibited and no low-privileged chain proven.** |
| F1 | `fosinit` local callback registrations (`Vendor*Callback`, AppCompat/Eve, LauncherHijackPreventer) | In-process system_server registrations from `*_fosinit.xml`, not exported Binder methods; no ordinary caller | No Binder calling identity at callback dispatch | Resolver filtering/visibility/policy callbacks (`services:222435-222489`; AppCompat `fosservices:41093-41147`; registrations Phase 6JD). No preferred/HOME/package writer. **False lead; local trusted surface.** |
| F2 | `fosdebug` / `IFireOSDebugManager` dump | `DUMP` on diagnostic path; shell read-only dump observed | No mutation identity boundary | Diagnostic output only (`fosservices:412-576`). **Query-only; no escalation.** |

## Explicit unknowns and exclusions

* A generated Stub that checks only the interface token does not establish an
  absent permission vulnerability; method-local and downstream checks must be
  closed separately.
* `clearCallingIdentity` is material only when the subsequent sink consumes
  caller-controlled package, component, user, role, or policy data. The map
  therefore does not elevate DPM/settings/lifecycle identity clears by
  themselves.
* Input injection, key callbacks, launcher-start helpers, and metadata files
  are not labeled privilege escalation because no security-relevant requested
  mutation is proven downstream.
* The Phase 6PR conclusions and confirmed A1/U4 evidence are retained as
  closure anchors; no transaction is repeated.

## Evidence integrity

Primary disassembly hashes:

* `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` —
  `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
* `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log` —
  `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`
* `decompiled/baksmali/vdexExtractor/services/disassembly.log` —
  `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53`

Reviewed summaries/tables: `findings/phase-6pr-privilege-surface-synthesis.md`
(SHA-256 `06ec5c0091005424580a635b7c03c674f43812bad30a283a8ed4d89de5f12a82`),
`findings/phase-6fl-amazon-caller-identity-relay-audit.md` (SHA-256
`2bb3adb6e30eaf51d78e9202fd5bf72cf6d61f572e495b6f85480e167e8b30d9`), and
`artifacts/phase6mh-package-state-writers-20260810-01/summary.json` (SHA-256
`c8bcd0cda741aa21534a5aebc7995c7daa007f669a14b1ec7b913b6bbf055cc4`).

