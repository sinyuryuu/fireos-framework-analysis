# Amazon parent/profile/DPM sink closure — PS7331 host-only review

Date: 2026-08-10. Scope was limited to saved PS7331 fosservices, boot-fosframework and boot-framework disassembly, JADX sources, manifests, package/DPM evidence, KFT reports, and prior caller-closure work. No ADB/device, Binder/service call, user creation, PIN, DPM provisioning, root/exploit, OTA/recovery/flash, or state mutation was used. Only this Markdown and its companion CSV were created.

## Result

No ordinary-app or shell route is proven that reaches a User-0 Fire HOME/package-state writer. The strongest static candidate is `IAmazonUserManager` tx3 `enableKftLauncher(UserInfo)`: its bounded Stub/implementation slice shows interface-token enforcement but no method-local caller check, and it writes Tahoe/Fire/Launcher3 state using caller-supplied `UserInfo.id`. Existing ordinary-app tests nevertheless show the User-10 cross-user gate and the User-0 protected-component gate reject before state change. Treat the method as a static high-impact review point, not an exploit.

The only confirmed ordinary-app confused deputy in this surface is tx4 `setUserSetupComplete(UserInfo)`, which writes two setup settings for User 10 after `clearCallingIdentity`; it has no observed HOME/PMS edge. AmazonProfileService tx41 can accept ordinary metadata and an ordinary caller can reach its Binder, but the downstream current-user/cross-user check stops execution. Amazon DPM restriction tx1/tx2 and DPM tx100 persistent-preferred paths are stopped by active-admin/profile-owner/caller gates; PMS tx73 additionally requires system UID. Parental Controls is an existing User-0 Profile Owner, but its exported surface does not show an arbitrary package/HOME relay.

Static absence of a method-local check, exported component, or consumer is not treated as proof of safety. Rows P-009, P-010, P-013, and P-014 retain bounded unknowns where the saved corpus does not establish the full downstream consumer/caller universe.

## Caller → permission → scope → identity → sink summary

See the companion CSV for one row per route and exact evidence locations. The important boundaries are:

- KFT tx3: intended `AmazonUserManagerImpl.createChildUser` and system boot-phase child loop; sink is child/profile-scoped by `UserInfo.id`. Existing FJ/FK ordinary tests are closed and must not be repeated.
- KFT tx4: ordinary APK reached tx4 for User 10; identity was cleared before settings writes; this is settings-only and already closed as a secondary finding.
- Profile tx41: ordinary metadata seeding is confirmed, but ordinary execution stops at `INTERACT_ACROSS_USERS` before `startActivityAsUser`; tx21/tx20 use the protected `PROFILE_INTERACTION` family.
- DPM tx1/tx2: Amazon restriction keys require `MANAGE_USERS`; generic restrictions still hit DPM active-admin/owner validation. No launcher sink exists in this path.
- DPM tx100: active admin/profile owner and caller ownership are required; the downstream PMS persistent-preferred writer requires UID 1000 after identity clearing. Existing fake-admin/live-owner tests are closed.
- Parental Controls: exported UI/provider entries were reviewed; policy service is non-exported and lifecycle receivers are protected. Profile-owner DPM capability is real but no arbitrary HOME/package relay is shown.
- PMS writers: formal enabled-setting, component-setting, and preferred-activity sinks remain framework-gated. The saved Play Store permission-holder anomaly is provenance-unknown, not a proven caller path.

## Exported component and package evidence

The saved parental-controls manifest records exported activities including `ParentalPasswordAuthentication` and `SearchEntryActivity` (manifest lines 152–190), while the policy service and selected lifecycle components are non-exported or protected in the same manifest slice (lines 188–230 and the related receiver/provider entries). It declares powerful permissions including `MANAGE_USERS`, `MANAGE_PROFILE_AND_DEVICE_OWNERS`, and cross-user permissions (lines 93–136), but declaration does not prove an ordinary caller can use them. SHA-256: `artifacts/phase6ad/protected-broadcast-inventory-20260805-01/manifests/001_com.amazon.parentalcontrols__0_com.amazon.parentalcontrols.xmltree.txt` = `5ef89e517f53d6d3696df3a43df40502f651d57f0a27d62a445ddc518930c9db`.

The saved Tahoe manifest records privileged/signature-sensitive capabilities including `MANAGE_DEVICE_ADMINS`, `WRITE_SECURE_SETTINGS`, `LOCK_SCREEN_SERVICE`, and `PARENTAL_ACCESS` (lines 7–153). This is package capability evidence, not an exported ordinary relay. SHA-256: `artifacts/phase6ad/protected-broadcast-inventory-20260805-01/manifests/021_com_amazon_tahoe.xmltree.txt` = `12055fed1f6cf5f012725aa044e215dcc8c8cdaa233ffac6f044c59198c36ae1`.

## Exact disassembly inputs

- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` — SHA-256 `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`. Relevant windows: Amazon DPM `45935–46108`; profile HOME/helper and tx41 `74281–74312`, `76246–76256`, `77028–77266`, `78949–79132`; KFT writer/implementation `54297–54566`; manager permission helper `54847–54906`; child boot loop and publication `55053–55119`.
- `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log` — SHA-256 `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`. Relevant windows: child caller `369180–369243`; Amazon user-manager Proxy/Stub `370398–370777`; profile tx41 Stub `378462–378525`.
- `decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log` — SHA-256 `5ef6a8c6edea903e3bf7e5298be02041dc46be06881438457e79cbf8501b76df`. Relevant window: `UserInfo.writeToParcel` `562771–562801`; DPM/PMS transaction evidence is cited in the CSV.

## Existing tests closed — do not repeat

Do not repeat KFT tx3 User-10 or User-0 probes (Phase 6EC/6FJ/6FK and Phase 6PR), tx4 User-10 settings test (Phase 6GI/6GV), profile tx41/tx21 tests (Phase 6ER/6MQ), DPM restriction tx1/tx2 (Phase 6ET), DPM tx100 fake-admin/live-owner tests (Phase 6DT), parental-owner HOME/reachability probes (Phase 6GA/6BU/6JG), component-state Fire/Tahoe disable tests (Phase 6KQ/6LZ), or service-manager/SELinux reachability tests (Phase 6BS). These tests either mutated and restored state under their own controls or were read-only negative boundaries; this closure only reuses their saved evidence.

## Safe/rejected next steps

Safe: host-only search for additional aliases, native/runtime-loaded callers, missing manifest component records, and consumers of `launch_info_map_key`; provenance comparison of the saved Play Store `CHANGE_COMPONENT_ENABLED_STATE` grant; static diff against a materially different PS7331 artifact.

Rejected: any Binder/service invocation, ADB/device action, child-user creation, PIN or owner/profile-owner provisioning, package/component or preferred-activity mutation, permission grant/revoke, reboot, OTA/recovery/flash, root/exploit, or repeating a closed test without new evidence.

Disposition: no low-privilege User-0 HOME/package-state relay is proven in the bounded saved corpus. Unknowns remain explicitly bounded in the CSV.
