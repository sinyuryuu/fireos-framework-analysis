# High-permission holder closure: KOR, ManagedProvisioning, H2

Date: 2026-08-10. Scope: host-only static analysis of saved PS7331 artifacts. No
ADB/device action, Binder/service call, broadcast, provider write, install/start,
profile creation, DPM provisioning, root, OTA/recovery/flash, payload, or state
mutation was performed. This closes the three requested holder families; it does
not repeat Fire Launcher/KFT tx3 coverage.

## Executive disposition

* `com.amazon.kor.demo`: **closed for an ordinary app/shell caller** at the
  framework receiver/provider gates. A trusted DCP cloud-message caller can
  statically reach package deletion; a trusted retail-demo lifecycle can reach
  KOR component state writers. Those trusted gates, and the exact final PMS
  authorization outcome for an already-authorized KOR UID, are not ordinary
  caller proofs.
* `com.android.managedprovisioning`: **closed as a holder-only/lifecycle
  candidate, not as a complete APK sink audit**. The saved corpus proves a
  privileged grant and provisioning component registrations, but does not retain
  ManagedProvisioning JADX/VDEX source sufficient to prove an exact caller-to-
  mutator chain. Component/package/settings sink reachability is therefore
  **UNKNOWN**, and no ordinary caller is proven.
* `com.amazon.alta.h2clientservice`: **closed for ordinary app/shell access**.
  Its exported, direct-boot-aware, single-user service is protected by the
  signature-level `BIND_SERVICE` permission. Authorized H2 clients can statically
  reach Amazon child/adult profile creation and household/profile/settings state;
  no direct HOME writer is present in the bounded APK source scan. H2's caller
  identity is logged only; no `clearCallingIdentity()` was found in the H2
  service path. This does not make the service shell-reachable because binding is
  the gate.

## Route closure

### KOR retail/demo

`ordinary app/shell -> AMS BroadcastQueue -> ServerMessageReceiver` is stopped by
`com.amazon.dcp.messaging.permission.INITIATE_HANDLE_DEVICE_MESSAGE` at
`artifacts/phase6ad/protected-broadcast-inventory-20260805-01/manifests/020_com_amazon_kor_demo.xmltree.txt:267-270`.
The Phase 6DL saved evidence records shell UID 2000 denial. The receiver source
has no local `getCallingUid()`, `clearCallingIdentity()`, or
`restoreCallingIdentity()`; the framework broadcast permission is the effective
gate. With a trusted DCP sender and valid message envelope, the static route is:

`ServerMessageReceiver -> ServerMessageHandler -> MessageFactory ->
RemoveContentMessageHandler -> DemoPackageUtility.uninstallPackages() ->
PackageManagerUtility.uninstallApps() -> DemoPackageManager.deletePackage(...,
DELETE_ALL_USERS)`.

This is a package-deletion sink, not a proven HOME writer. The provider is
`exported=true` but requires separate `READ_PROVIDER`/`WRITE_PROVIDER` permissions
at manifest `:213-218`; saved shell query evidence was denied before the generic
SQL-backed handlers. `DemoStateService` reaches KOR's component-state API only
after `DemoManager.isDemo()` and kiosk-state logic. `KioskHome` and
`DOOBEInitiationActivity` are exported but manifest `enabled=false` at `:295-313`.
That is a trusted retail-demo lifecycle gate, not an ordinary caller route.

### ManagedProvisioning

The Phase 6PS/6MC inventory records UID 10091,
`/system/priv-app/ManagedProvisioning`, and granted
`CHANGE_COMPONENT_ENABLED_STATE`, `DELETE_PACKAGES`, `INSTALL_PACKAGES`,
`MANAGE_USERS`, and `WRITE_SECURE_SETTINGS`. The platform privapp allowlist is
at `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/system/etc/permissions/privapp-permissions-platform.xml:88-104`.
Saved read-only resolver output lists `SilentDeviceOwnerProvisioningReceiver`,
`ManagedUserCreationListener`, cross-profile restriction handling, OTA pre-boot
listeners, and provisioning activities at
`artifacts/phase6k/readonly-device-20260805-01/preferred_activities.stdout.txt:2058-2059,4689-4715,5642,5697`.

The path audit proves APK/odex/vdex presence at
`artifacts/phase6bp/ota-path-audit-20260805-02/ota-path-audit.json:1022,15377,19490`,
but no corresponding ManagedProvisioning JADX source or decoded manifest with
per-component permission/exported details is retained in the searched corpus.
Therefore the exact exported/lifecycle gate, `clearCallingIdentity()` behavior,
exact component/package/settings sink, and explicit user/profile argument are
**UNKNOWN**. The safe conclusion is lifecycle-only: provisioning, device-owner/
profile-owner, managed-user, boot/OTA and cross-profile callbacks are trusted
system/DPM flows. A holder row is not an ordinary caller proof.

### H2 household/profile service

`H2ClientService` is `exported=true`, `singleUser=true`, `directBootAware=true`,
with signature-level `com.amazon.alta.h2clientservice.permission.BIND_SERVICE` at
`artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/017_com.amazon.h2clientservice.xmltree.txt:102-107`.
The same manifest shows the MAP provider (`:111-114`), protected MAP receiver
(`:116-123`), non-exported SyncReceiver (`:124-126`), and DCP-protected receiver
(`:132-134`).

Static route: `authorized H2 client -> H2ClientService.onBind() ->
IH2ClientService.Stub tx1..30 -> AddUserAPICall -> HouseholdController ->
CreateAndroidUserCommand -> UserHelper/AndroidUserHelper ->
AmazonUserManager.createChildUser() or createAdultUser()`.
Offsets: `H2ClientService.java:105-107,124-127`; `IH2ClientService.java:26-59,581-710`;
`HouseholdController.java:323-372`; `CreateAndroidUserCommand.java:21-32`;
`UserHelper.java:22-29`; `AndroidUserHelper.java:78-83,99-111`.
Scope is household/profile and Android-user lifecycle, with per-profile
household/KFT/settings state in `PersistenceController.java:50-117`. The bounded
H2 scan found no HOME/preferred writer, Fire Launcher literal, or direct
component/application-state setter.

`AbstractAPICall.java:28-44` logs `Binder.getCallingUid()` and asserts the H2
process is user 0; it is not caller authorization. No
`clearCallingIdentity()`/`restoreCallingIdentity()` was found in the H2 service
implementation. Binding permission remains decisive: shell/app binding and any
transaction are unproven and were not attempted.

## Trusted gates, unknowns, and non-repeat list

Trusted gates are: KOR DCP messaging plus valid cloud envelope; KOR
`DemoManager.isDemo()` retail-demo lifecycle; ManagedProvisioning provisioning,
device/profile-owner, boot/OTA and cross-profile lifecycle; and H2's signature
`BIND_SERVICE` plus Amazon household/profile client lifecycle. Unknowns retained:
ManagedProvisioning per-component manifest gates and exact sinks; KOR final PMS
protected-component acceptance for an authorized KOR UID; H2 complete client
universe and framework implementation after `AmazonUserManager`; and
native/resource/failed-JADX paths. None is converted to a finding.

Do not repeat KOR Phase 6DL shell broadcast/provider/HOME probes; KOR demo
activation/reset or payload delivery; H2 bind/service-call, addUser/createChildUser,
reset/remove/switch, child-profile creation/deletion, or transaction replay;
DCPMS tx1-3/callback replay; DCPMS/OOBE/OTA lifecycle triggering; Fire
Launcher/KFT tx3 and child-user/Tahoe launcher-state tests; backup/restore, RDM,
package/component mutation, or DPM provisioning. These are already closed by
Phase 6DL, 6IT, 6MC and 6PS.

## Evidence hashes

| Path | SHA-256 |
|---|---|
| `artifacts/phase6ad/protected-broadcast-inventory-20260805-01/manifests/020_com_amazon_kor_demo.xmltree.txt` | `ac6c98e250f82949188ef2cd8eea0e85767bda808c00f9f8dccd384a1adc314e` |
| `artifacts/phase6j/ota-additional-holders-device-20260805-01/com_amazon_kor_demo.apk` | `975cad513f5830c35310577170da3f3c08f5514826c8e9e16b11ca3abf6b5542` |
| `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/017_com.amazon.h2clientservice.xmltree.txt` | `f14670a78cdbddf4c46375d78e1607fe491c33fd4d807de57abfe5e2b5300242` |
| `artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/H2ClientService.java` | `f30c3b42ce45c1e7ef717b2deb5b0402dbc01fc70cb5a86480d8b4a54e7fa9e5` |
| `artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2shared/aidl/IH2ClientService.java` | `3c3c46e60bc6d63be9c7074fa148767e41b51b734d84ceb920719b352ce7cb4b` |
| `artifacts/phase6it-missing-system-apps-20260807-01-files/jadx/sources/com/amazon/alta/h2clientservice/apicall/AbstractAPICall.java` | `9d843f825ae30e06e2e6d7598f8b49f90904bdd66c88660e18ce1f03d02421da` |
| `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/system/etc/permissions/privapp-permissions-platform.xml` | `0b30c1624ffdab6c5454746737a060157276da5d2bd43addc74cd3919ae4aad1` |

