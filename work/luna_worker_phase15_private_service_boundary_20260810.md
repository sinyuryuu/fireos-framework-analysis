# Phase 15 — Amazon private service boundary inventory

Scope is host-only static analysis of the exact PS7331 artifacts, fosinit XML,
SELinux/service-context evidence, VDEX AIDL-like Stub/Proxy mappings, and saved
manifest/permission/privapp evidence. No Binder transaction was sent, no
transaction code was guessed, and no device command was run for this phase.

## Executive result

The saved PS7331 service list contains `amazonactivitymanager`,
`amazonwindowmanager`, `amazonpackagemanager`, `amazonprofileservice`,
`amazonusermanagerservice`, `migrationservice`, `amazon_input`, and
`amazon_keyevent`. The Phase 6AQ service-context join maps the private services
to SELinux service types and the saved AVC capture records `service_manager
find` denial for shell UID 2000. Thus service-manager visibility is a first
boundary; a listed name does not establish a shell Binder handle.

The exact fosinit declarations publish system-server vendor services for
`AmazonActivityManagerService`, `AmazonWindowManagerService`, and
`AmazonPackageManagerService`. `amazon_input` and `amazon_keyevent` are
published by `AmazonInputManagerService` in the VDEX disassembly. The saved
source inventory identifies `amazonusermanagerservice`, `amazonprofileservice`,
and `migrationservice` as published runtime names, but the corresponding
fosinit declaration was not recovered in the scoped XML set; those publication
edges are therefore kept separate from the exact fosinit-confirmed rows.

## Access boundaries

- `amazonactivitymanager`: context `amazonactivitymanager_service`; shell
  `find` denied. The AIDL-like contract is `IAmazonActivityManager`, with
  Stub/Proxy mappings in the Phase 6L contract inventory. The bounded method
  inventory identifies permission/control markers for selected operations;
  `preWarmApplicationForUser` contains an `APP_PREWARM` check and then a
  `clearCallingIdentity` in the saved instruction stream. That is a static
  authorization anomaly candidate, not evidence of a reachable shell route.
- `amazonwindowmanager`: context `amazonwindowmanager_service`; shell `find`
  denied. The exact fosinit service and `IAmazonWindowManager` contract are
  present. The reviewed methods are PIP, overscan, lock, and window-state
  controls; `CONTROL_PIP_WINDOW` is enforced on the bounded PIP mutator. No
  HOME candidate or package-state writer was found.
- `amazonpackagemanager`: context `amazon_package_manager_service`; shell
  `find` denied. The exact fosinit service and `IAmazonPackageManager`
  Stub/Proxy inventory are present. Metadata flag/metadata setters are gated by
  `com.amazon.permission.ADD_RM_PKG_METADATA` (`signature|amazon`) in the
  permission evidence. The proxy-receiver path additionally checks the
  `PendingIntent` creator as a system app before forwarding. No private HOME
  setter was found. Its exact package-state sink is a facade used by trusted
  system-server paths, notably the KFT child-user launcher path below.
- `amazonusermanagerservice`: context `amazonusermanager_service`; shell
  `find` denied. The `IAmazonUserManager` Stub/Proxy inventory identifies the
  KFT launcher method. Its exact downstream sink calls Amazon Package Manager
  component/application enabled-state setters for a supplied `UserInfo.id`:
  Tahoe FreeTime launcher is enabled and Fire Launcher/Launcher3 are disabled.
  This is a child/profile lifecycle path, not evidence of an ordinary User 0
  HOME selector. The exact external caller permission check remains an open
  edge; publication/SELinux reachability and downstream effect are separate.
- `amazonprofileservice`: context `amazon_profile_service`; shell `find`
  denied. The saved method inventory records `getCallingUid`, permission/
  signature markers, and `clearCallingIdentity`. `initiateLauncher` enforces
  `com.amazon.device.permission.PROFILE_INTERACTION`; the reviewed tx41
  metadata path reaches `startActivityAsUser` only after the separate
  cross-user gate. No package-state or persistent HOME writer was found.
- `migrationservice`: the saved list contains the name and the recovered
  `MigrationService` contract has `migrateData`, `getSharedStorageUuid`, and
  `getMigrateDataInfo`. `migrateData`/`getMigrateDataInfo` use
  `MOUNT_UNMOUNT_FILESYSTEMS`; the shared-storage query has no method-local
  permission check in the recovered slice. `appsAvailable()` sends a fixed
  application-availability notification to Fire Launcher. This is a
  migration/refresh side effect, not a package state or HOME selection sink.
  Service-context publication and exact external caller provenance remain
  unresolved in the extracted text join.
- `amazon_input` and `amazon_keyevent`: both map to
  `amazon_input_service`; shell `find` is denied. `AmazonInputManagerService`
  publishes both names. The method inventory contains permission, UID, and
  signature markers; key-event state includes protected input-locking and
  partner-app APIs. The HOME-key path is a local callback that creates an
  implicit `MAIN` + `HOME` intent for `UserHandle.CURRENT`; it does not show an
  explicit Fire Launcher component write or a preferred-activity mutation.

## HOME/package sink conclusion

The exact package/HOME-affecting sink in the requested private-service set is
`AmazonUserManagerService.BinderService.enableKftLauncherComponent(UserInfo)`
and its Amazon Package Manager enabled-state calls. The observed scope is the
supplied child `UserInfo.id`, with Tahoe/FreeTime enabled and Fire Launcher plus
Launcher3 disabled. No inspected private service method writes a persistent
User-0 preferred HOME. `AmazonActivityManagerService.isOnHomeStack` is a query;
the input key path launches an implicit HOME intent; migration notifies Fire
Launcher; profile service launches a profile-related activity subject to a
cross-user gate.

## Evidence and residuals

Primary evidence is recorded in the CSV companion. The main joins are:

- `artifacts/phase6aq/service-context-audit-20260805-06/service-context-matrix.csv`
- `findings/phase-6aq-service-context-closure.md`
- `artifacts/amazon-services/amazonactivitymanager_fosinit.xml`
- `artifacts/amazon-services/amazonwindowmanager_fosinit.xml`
- `artifacts/amazon-services/amazonpackagemanager_fosinit.xml`
- `artifacts/phase6l/binder-contract-audit-20260805-02/contract-methods.csv`
- `artifacts/phase6ax/activity-manager-home-surface-20260805-01/activity-manager-binder-methods.csv`
- `artifacts/phase6aj/input-home-boundary-20260805-04/input-home-boundary.csv`
- `artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv`
- `device/baseline/BASELINE-20260803-05/service_list.txt`

Remaining safe work is host-only: recover the missing exact publication XML or
service-context source for `amazonusermanagerservice`, `amazonprofileservice`,
and `migrationservice`; complete method-local permission and caller joins for
their contracts; and identify production callers plus cross-user validation.
No service invocation is required or authorized for those gaps.
