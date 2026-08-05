# Phase 6AY — Launcher state services and OTA lifecycle gates

## Scope

This phase audits the PS7331 system-server VDEX disassembly for two previously
unclosed surfaces:

1. the Amazon user-management path that changes launcher package/component
   state for KFT (Kids/FreeTime) users; and
2. the Amazon package-manager post-system-OTA lifecycle path.

The work is host-only. It parses a saved VDEX disassembly and correlates it
with already-captured, enforcing-mode service-manager visibility evidence. It
does not contact ADB, obtain a Binder handle, send a Binder transaction,
invoke Device Policy Manager, change package/settings state, replay a broadcast,
reboot, or write a partition.

## Inputs and reproducibility

| Input | Evidence |
|---|---|
| VDEX disassembly | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` — SHA-256 `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` |
| Parser | `tools/scripts/audit_phase6ay_launcher_state_services.py` — SHA-256 `8a9bb2d033fca3fd7a3b2b2f72cd092908dacafea33043ee12102dd0f14ed710` |
| Corrected parser output | `artifacts/phase6ay/launcher-state-services-20260805-02/` |
| Parsed method count | 58 methods across four exact class regions |

Reproduction, without device access:

```sh
python3 -m py_compile tools/scripts/audit_phase6ay_launcher_state_services.py
python3 tools/scripts/audit_phase6ay_launcher_state_services.py --dry-run
python3 tools/scripts/audit_phase6ay_launcher_state_services.py \
  --output artifacts/phase6ay/launcher-state-services-YYYYMMDD-NN
```

The parser refuses to overwrite an existing output directory. The generated
`summary.json` records all safety flags as false:
`device_contacted`, `binder_invoked`, `dpm_or_profile_owner_invoked`,
`package_or_settings_state_changed`, `ota_broadcast_sent`, and
`partition_written`.

## Findings

### 1. KFT path contains an explicit launcher state mutation

**Status: Confirmed (static evidence; not a live invocation).**

`AmazonUserManagerService.BinderService.enableKftLauncherComponent(UserInfo)`
at VDEX disassembly lines 54297–54325 constructs
`com.amazon.tahoe.launcher.FreeTimeLauncherActivity`, enables it with
`AmazonPackageManager.setComponentEnabledSetting(..., 1, 1, userId)`, and then
calls `setApplicationEnabledSetting` with state `2` (disabled) for both:

* `com.amazon.firelauncher`; and
* `com.android.launcher3`.

This is a real Amazon package-state mutation path, but it is a private,
user-profile lifecycle helper. It is not evidence that ordinary shell can
invoke the mutation, and it is not the normal HOME resolver path.

### 2. KFT mutation has internal eligibility gates

**Status: Confirmed (static evidence; not a live invocation).**

`tryEnableKftLauncherComponent(UserInfo)` at lines 54371–54414 first handles
the user argument, returns early for the TV path, checks that the KFT launcher
activity exists, and only then calls the state-mutating helper. The caller
`enableKftLauncher(UserInfo)` at lines 54415–54478 also checks the Amazon
package-manager object and the multimodal-device condition. After the state
change it clears Binder calling identity and invokes the internal
`empowerKftUser` path, which checks/sets the KFT active admin and profile owner.

The presence of `clearCallingIdentity`, `setActiveAdmin`, and
`setProfileOwner` makes this an internal system-server lifecycle operation,
not a safe third-party or shell configuration API.

### 3. KFT boot lifecycle is upgrade- and child-user-scoped

**Status: Confirmed (static evidence; not a live invocation).**

`AmazonUserManagerService.onBootPhase(I)` at lines 55053–55105 requires boot
phase `500`, obtains User/Package/Device Policy services, checks
`AmazonPackageManager.isUpgrade()`, iterates users, and invokes the KFT path
only for users identified by `AmazonUserManagerHelper.isChildUser(UserInfo)`.
It then calls `setUserSetupComplete` for that child-user lifecycle.

Therefore this path does not explain a normal user-0 `HOME` resolution by
itself. It does show that Amazon has a separate, privileged path capable of
changing launcher package state for a special user profile.

### 4. AmazonUserManagerService publishes a private service

**Status: Confirmed in VDEX; runtime shell access denied in saved capture.**

`getSystemServiceName()` at lines 54894–54899 returns
`amazonusermanagerservice`. `onStart()` at lines 55106–55119 constructs the
BinderService, publishes it under that name, and publishes the local service.
The current artifact set does not contain a matching
`amazonusermanager_fosinit.xml`; that is an unresolved artifact-scope gap, not
evidence that the runtime service is absent.

The saved enforcing-mode live capture records `service check`/service-manager
visibility failure for `amazonusermanagerservice` and an AVC denial for shell
UID 2000. This supports the conclusion that ordinary shell cannot use this
private service through the normal service-manager lookup path.

### 5. Post-system-OTA broadcast is a system-server lifecycle gate

**Status: Confirmed (static evidence; not replayed).**

`AmazonPackageManagerService.onBootPhase(I)` at lines 96087–96127 initializes
at phase `500`; at phase `550` it checks the package-manager reference and
`PackageManagerService.isUpgrade()`. It then constructs
`amazon.intent.action.BOOT_AFTER_SYSTEM_OTA` and sends it with
`com.amazon.permission.RECEIVE_BOOT_AFTER_SYSTEM_OTA`.

The corresponding `fosinit` configuration records the service and the
system-server `ControlProtectedPackagesCallback` at
`artifacts/amazon-services/amazonpackagemanager_fosinit.xml:9–24`.
This establishes a post-OTA lifecycle sender and a protected package callback,
but it does not establish a shell-writable setting or a HOME selector.

The broadcast was not sent or replayed during this phase. Replaying it would
be an unsafe attempt to impersonate a boot/OTA lifecycle event and is outside
the permitted evidence boundary.

### 6. Amazon package metadata methods have an explicit permission gate

**Status: Confirmed (static evidence; not invoked).**

The Binder methods at lines 95955–96026 —
`removeAmazonFlagsForUser`, `removeAmazonMetadataForUser`,
`setAmazonFlagsForUser`, and `setAmazonMetadataForUser` — check
`amazon.permission.ADD_RM_PKG_METADATA` and log permission-denied branches.
These methods mutate Amazon package metadata, not HOME selection. No shell
call was attempted.

## Relation to HOME enforcement

The new evidence narrows the architecture:

```text
normal shell / HOME resolver
  -> existing PackageManager + ActivityTaskManager path
  -> Fire Launcher remains the observed HOME result

privileged child-user upgrade lifecycle
  -> AmazonUserManagerService.onBootPhase(500)
  -> KFT eligibility checks
  -> enable KFT launcher
  -> disable Fire Launcher and Launcher3 for that special user
  -> profile-owner/admin lifecycle

system-server upgrade lifecycle
  -> AmazonPackageManagerService.onBootPhase(550)
  -> protected BOOT_AFTER_SYSTEM_OTA broadcast
```

The KFT path is evidence of a distinct special-user package-state controller,
not proof of a normal-user HOME override. The OTA path is an authorization and
lifecycle boundary, not a safe ADB trigger.

## Runtime boundary

Saved read-only device evidence under
`artifacts/phase6aq/public-summary-20260805-01/` shows:

* ordinary shell UID 2000 could not find the private Amazon service names; and
* SELinux enforcing AVC records denied `{ find }` for
  `amazonpackagemanager`, `amazonusermanagerservice`,
  `amazonactivitymanager`, `amazonwindowmanager`, and related services.

This is strong evidence against a direct shell route to the newly identified
KFT or OTA lifecycle methods. It does not prove that a privileged Amazon
caller cannot reach them.

## Safety decisions

The following were deliberately rejected as unsafe or out of scope:

* private Binder transaction or transaction-code probing;
* calling `enableKftLauncher` or any profile-owner/admin method;
* replaying `BOOT_AFTER_SYSTEM_OTA`;
* changing `user_setup_complete` or other setup state;
* disabling, hiding, suspending, uninstalling, force-stopping, or clearing
  Fire Launcher;
* invoking OTA/recovery/update execution;
* changing partitions, SELinux policy, boot images, or bootloader state.

## Verdict

* **Confirmed:** Amazon contains a KFT-specific, privileged package-state path
  that can enable the FreeTime launcher and disable Fire Launcher/Launcher3
  for an eligible child user.
* **Confirmed:** Amazon emits a protected post-system-OTA broadcast from a
  system-server upgrade lifecycle path.
* **Strong evidence:** ordinary shell is blocked from finding the relevant
  private services by enforcing SELinux service-manager policy.
* **Not established:** that either path is the normal user-0 HOME resolver,
  that it can be invoked by ADB, or that it provides a safe launcher
  replacement.
* **No new workaround:** this phase found no safe, reversible ADB launcher
  replacement and no root path.

The next useful static target is the exact `ControlProtectedPackagesCallback`
implementation and its call sites inside the standard PackageManager protected
package flow. Any attempt to invoke the KFT or OTA lifecycle surfaces on the
retail device remains rejected.
