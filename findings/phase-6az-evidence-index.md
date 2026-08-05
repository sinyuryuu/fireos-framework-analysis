# Phase 6AZ evidence index

## 6AZ-KFT-001

- **Source:** PS7331 `fosservices` VDEX disassembly and Phase 6AY parser output
- **File/method:** `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54297-54325`, `AmazonUserManagerService.BinderService.enableKftLauncherComponent(UserInfo)`
- **Observed result:** Enables the FreeTime launcher component and calls `setApplicationEnabledSetting` with state `2` for `com.amazon.firelauncher` and `com.android.launcher3`.
- **Interpretation:** KFT has an explicit Fire Launcher disable path, but it is a private static path and was not invoked.
- **Confidence:** Confirmed
- **Related hypothesis:** KFT child-user lifecycle can alter launcher package state independently of ordinary HOME resolution.

## 6AZ-KFT-002

- **Source:** PS7331 `fosservices` VDEX
- **File/method:** `tryEnableKftLauncherComponent(UserInfo):54371-54414`; `enableKftLauncher(UserInfo):54415-54478`; `onBootPhase(int):55053-55105`
- **Observed result:** Eligibility checks, Device Policy/profile-owner operations, boot phase 500, upgrade state, and child-user selection precede the KFT path.
- **Interpretation:** This is not a general shell API or a normal user-0 HOME resolver branch.
- **Confidence:** Confirmed
- **Related hypothesis:** KFT is a special privileged lifecycle controller.

## 6AZ-PM-001

- **Source:** PS7331 `fosservices` and standard services VDEX
- **File/method:** `ControlProtectedPackagesCallback.shouldProtectPackage(int,String,Context):97034-97049`; `VendorProtectedPackagesCallback.callShouldProtectPackage:539225-539239`
- **Observed result:** Amazon callback checks system/privileged app status, deny-list membership, and caller UID 2000; the framework callback fan-in propagates a positive decision.
- **Interpretation:** The ordinary shell enabled-state rejection has a concrete Amazon protected-package gate.
- **Confidence:** Confirmed (static gate); live literal set is separately bounded below.
- **Related hypothesis:** Fire Launcher is protected by an Amazon callback rather than only by HOME priority.

## 6AZ-PM-002

- **Source:** PS7331 `system.img`, read-only debugfs extraction
- **Artifact:** `artifacts/phase6ap/denylist-resource-closure-20260805-01/`
- **Observed result:** Resource `0x7e05000a` maps to `amazon.fireos:raw/package_manager_deny_list`; its JSON explicitly contains `com.amazon.firelauncher`.
- **Interpretation:** Fire Launcher membership is present in the matched PS7331 resource seed.
- **Confidence:** Confirmed (host artifact)
- **Related hypothesis:** The callback’s deny-list membership condition explains shell rejection.

## 6AZ-PM-003

- **Source:** Amazon `fosinit` registration
- **File:** `artifacts/amazon-services/amazonpackagemanager_fosinit.xml:22`; SHA-256 `eb53e50cf72174eddcde25fd3538e4736d2cd4cb7866bab4e5bc2b70fc514286`
- **Observed result:** `ControlProtectedPackagesCallback` is registered as a system-server vendor callback.
- **Interpretation:** The Amazon callback is wired into the PackageManager protection fan-in.
- **Confidence:** Confirmed
- **Related hypothesis:** Shell cannot replace the callback through an ordinary user-level API.

## 6AZ-LIVE-001

- **Source:** Explicit-serial read-only capture
- **Test ID:** `PHASE6AZ-RO-20260805-04`
- **Public artifact:** `artifacts/phase6az/public-summary-20260805-02/`
- **Observed result:** PS7331/KFTRWI/API 28, verified boot green, SELinux enforcing, HOME resolves to `com.amazon.firelauncher/.Launcher` at priority 50, and the Amazon private service names are not visible to shell.
- **Interpretation:** The live device is consistent with the static resolver/protection model; this is observation, not a private-service invocation.
- **Confidence:** Strong evidence
- **Related hypothesis:** No ordinary shell route reaches the KFT or OTA private service.

## 6AZ-LIVE-002

- **Source:** Same read-only capture, explicit settings/package queries
- **Files:** `control-state-summary.txt`, derived from `tb_custom_launcher_value.stdout.txt` and `teslacoilsw_package.stdout.txt`
- **Observed result:** `tb_custom_launcher` points to `com.teslacoilsw.launcher`, but that package is not installed; no inspected artifact contains a HOME-specific reader/writer for this key.
- **Interpretation:** The key is stale/tool state, not an active Fire OS HOME selector in the inspected scope.
- **Confidence:** Strong evidence; scope-limited negative result
- **Related hypothesis:** A legacy launcher-control key remains as a useful historical clue but not a current control surface.

## 6AZ-SAFETY-001

- **Source:** `adb/phase6az/PHASE6AZ-RO-20260805-04/sha256sums.txt` and capture script
- **Observed result:** All raw capture hashes verify; `commands.txt` contains read-only queries only; no mutation was requested.
- **Interpretation:** Phase 6AZ did not alter package, settings, overlay, policy, boot, or partition state.
- **Confidence:** Confirmed
- **Related hypothesis:** The KFT path can be confirmed without executing it.
