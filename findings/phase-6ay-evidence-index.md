# Phase 6AY evidence index

All evidence below is either host-only static analysis or a previously saved,
read-only device capture. No new device mutation was performed.

## 6AY-KFT-001

- **Source:** PS7331 VDEX disassembly
- **File:** `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`
- **SHA-256:** `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- **Test ID:** `PHASE6AY-STATIC-20260805-02`
- **Observed result:** Corrected parser identified 58 methods in four exact class regions: `AmazonUserManagerService`, its `BinderService`, `AmazonPackageManagerService`, and its `BinderService`.
- **Interpretation:** The service audit scope is reproducible and includes outer lifecycle methods that the first parser pass did not include.
- **Confidence:** Confirmed
- **Related hypothesis:** Amazon has a separate privileged lifecycle controller beyond the ordinary HOME resolver.

## 6AY-KFT-002

- **Source:** `AmazonUserManagerService.BinderService.enableKftLauncherComponent`
- **File/method:** VDEX lines 54297–54325; `artifacts/phase6ay/launcher-state-services-20260805-02/selected-method-snippets.txt`
- **Observed result:** Enables `com.amazon.tahoe.launcher.FreeTimeLauncherActivity`; sets `com.amazon.firelauncher` and `com.android.launcher3` application state to disabled for the supplied user.
- **Interpretation:** A real Amazon KFT package-state mutation path exists, but it is a private helper and was not invoked.
- **Confidence:** Confirmed
- **Related hypothesis:** KFT/child-user lifecycle can alter launcher state independently of ordinary HOME selection.

## 6AY-KFT-003

- **Source:** `tryEnableKftLauncherComponent` and `existsKftLauncher`
- **File/method:** VDEX lines 54326–54370 and 54371–54414
- **Observed result:** TV, device-feature, user, and FreeTime activity-existence checks precede the mutation.
- **Interpretation:** The launcher state write is conditional and not a general shell API.
- **Confidence:** Confirmed
- **Related hypothesis:** The KFT path is special-user/device lifecycle logic.

## 6AY-KFT-004

- **Source:** `enableKftLauncher` / `empowerKftUser`
- **File/method:** VDEX lines 54248–54296 and 54415–54478
- **Observed result:** The path uses Device Policy Manager, `clearCallingIdentity`, `setActiveAdmin`, and `setProfileOwner` for the FreeTime device-admin component.
- **Interpretation:** The path is privileged and high impact; it is not a safe ADB workaround.
- **Confidence:** Confirmed
- **Related hypothesis:** Device/profile policy participates in the KFT lifecycle.

## 6AY-KFT-005

- **Source:** `AmazonUserManagerService.onBootPhase`
- **File/method:** VDEX lines 55053–55105
- **Observed result:** Boot phase 500, `isUpgrade()`, child-user iteration, KFT enable flow, and setup completion update.
- **Interpretation:** KFT state changes are tied to an internal upgrade/child-user lifecycle.
- **Confidence:** Confirmed
- **Related hypothesis:** Amazon launcher behavior has a special-user path separate from normal user-0 HOME resolution.

## 6AY-KFT-006

- **Source:** `AmazonUserManagerService.getSystemServiceName` / `onStart`
- **File/method:** VDEX lines 54894–54899 and 55106–55119
- **Observed result:** Service name is `amazonusermanagerservice`; Binder and local services are published.
- **Interpretation:** The VDEX contains a private service publication. Matching `fosinit` registration was not found in the current artifact scope.
- **Confidence:** Confirmed for VDEX publication; unresolved for artifact mapping
- **Related hypothesis:** Ordinary shell may be unable to reach the KFT binder surface.

## 6AY-OTA-001

- **Source:** `AmazonPackageManagerService.onBootPhase`
- **File/method:** VDEX lines 96087–96127
- **Observed result:** At phase 550 and only when `PackageManagerService.isUpgrade()` is true, constructs `amazon.intent.action.BOOT_AFTER_SYSTEM_OTA` and sends it with `com.amazon.permission.RECEIVE_BOOT_AFTER_SYSTEM_OTA`.
- **Interpretation:** The sender is a system-server OTA lifecycle gate, not a shell-writable HOME control.
- **Confidence:** Confirmed
- **Related hypothesis:** OOBE/OTA can react to upgrade lifecycle events but is not an ordinary HOME setter.

## 6AY-OTA-002

- **Source:** Amazon `fosinit` configuration
- **File:** `artifacts/amazon-services/amazonpackagemanager_fosinit.xml:9–24`
- **SHA-256:** `eb53e50cf72174eddcde25fd3538e4736d2cd4cb7866bab4e5bc2b70fc514286`
- **Observed result:** Registers `AmazonPackageManagerService` and a system-server `ControlProtectedPackagesCallback` under `VendorProtectedPackagesCallback`.
- **Interpretation:** The package-manager protected-package extension is a concrete Amazon integration point.
- **Confidence:** Confirmed
- **Related hypothesis:** Fire Launcher protection may be introduced through the PackageManager protected-package callback.

## 6AY-PM-001

- **Source:** package metadata Binder methods
- **File/method:** VDEX lines 95955–96026
- **Observed result:** Four metadata mutation methods check `amazon.permission.ADD_RM_PKG_METADATA` and have permission-denied branches.
- **Interpretation:** These calls are protected metadata operations, not HOME selection operations.
- **Confidence:** Confirmed
- **Related hypothesis:** Amazon package metadata is not a shell-writable HOME control surface.

## 6AY-RUNTIME-001

- **Source:** saved enforcing-mode service visibility capture
- **Files:** `artifacts/phase6aq/public-summary-20260805-01/service-check-results.txt`, `amazon-service-avc.txt`
- **SHA-256:** service checks `242b8381d43970c6d25075d7434e9a8c6f26e0167bb4c8c31d910af1e0bb5aed`; AVC `d436542564947472c1b2481519312542d7d1053512b9cb47c68abbb981e0b0a4`
- **Observed result:** Shell UID 2000 could not find the Amazon private services; enforcing SELinux AVCs denied `{ find }` for the relevant service-manager labels.
- **Interpretation:** Ordinary shell cannot reach these services through normal service-manager lookup on the captured device.
- **Confidence:** Strong evidence
- **Related hypothesis:** No direct shell invocation of KFT/OTA private service methods.

## 6AY-SAFETY-001

- **Source:** generated parser summary
- **File:** `artifacts/phase6ay/launcher-state-services-20260805-02/summary.json`
- **SHA-256:** `ccf8cab249714f6265867e9ee6d8b522a073b5ed6aaa66d75c5f6fbfa8eaa642`
- **Observed result:** `device_contacted=false`, `binder_invoked=false`, `dpm_or_profile_owner_invoked=false`, `package_or_settings_state_changed=false`, `ota_broadcast_sent=false`, `partition_written=false`.
- **Interpretation:** The new artifact was produced without device mutation or high-impact invocation.
- **Confidence:** Confirmed
- **Related hypothesis:** Host-only analysis can close the current static boundary safely.
