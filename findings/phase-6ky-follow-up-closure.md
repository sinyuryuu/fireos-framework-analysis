# Phase 6KY — delegated follow-up closure

## Scope and safety disposition

This addendum integrates three bounded, host-only worker reviews with the main
agent's VDEX and HOME-callback audit. It does not repeat the priority matrix,
`set-home-activity` persistence experiment, or the previously closed User-0
writer searches. No Root method, unknown Binder transaction, native driver
command, OTA/recovery action, package mutation, or device state change was
performed in this follow-up.

The device unlock credential supplied during the session was not used or
written to project files.

Baseline public commit before this addendum: `0df74615721bad13fe1bf46d8361e759f4e4d454`.

## Integrated results

### 已證實：沒有新增可達的 User-0 formal HOME writer

The delegated inventory found no new Amazon caller that writes User-0
`setHomeActivity`, ordinary/persistent preferred activities, or a Fire
package/component state. The known standard sink remains
`PackageManagerService.setHomeActivity()` → `replacePreferredActivity()`.
The only launcher-specific Amazon state writer found in the selected VDEX is
`AmazonUserManagerService.BinderService.enableKftLauncherComponent(UserInfo)`;
its use of `UserInfo.id` makes it a child/profile-scoped lifecycle path, not an
unconditional User-0 route.

Evidence:

- `fosservices/disassembly.log:54310-54324`
- `artifacts/phase6av/ipc-method-closure-20260805-05/ipc-method-closure.csv`
  (SHA-256 `0d4afce1aee4acd54baf1bce90e009dc7ea94b2a47aa86db0266ec24c157c447`)
- `findings/phase-6kv-pms-home-caller-closure.md`
  (SHA-256 `a3c3d90315895c8295c8cee73f889f020b96f31cded80fa9e1672dc9ae598ef1`)

### 已證實：vendor HOME callbacks remain AOSP-shaped in the collected artifacts

The AppCompat callback delegates to `IPackageManager.resolveIntent()` and
applies the observed uninstalled-app filter. The Eve callback has no concrete
`resolveIntent()` override and inherits the base null result. The dispatcher
then falls back to `PackageManagerInternal.resolveIntent()` when callbacks
return null. Neither collected callback contains a Fire Launcher package
literal or a preferred/package-state write.

Evidence:

- `artifacts/phase6kw-vendor-home-callbacks/vendor-home-callbacks.csv`
  (SHA-256 `638c1a8ae1bae66cb24ebede74a8afcb48e26fd09f0028d87a8d2fef6ac3bc3d`)
- `artifacts/phase6kw-vendor-home-callbacks/result.md`
  (SHA-256 `2a2fd9187b81f0f036354e30ee424370e4bea5ee1ca998978dac803f1bee136d`)
- `services/disassembly.log:222435-222489,796458-796504`

### 已證實：OTA/OOBE is a setup-only state machine, not a normal HOME bypass

`BootAfterSystemOTAReceiver` and `OOBEActivationHelper` can activate the
protected OOBE component and write setup-state values under their lifecycle
conditions. The collected `OobeHomeActivity` is permission protected and its
baseline component state is disabled. No evidence shows that this path writes
the normal User-0 preferred HOME record or disables Fire Launcher. It was not
triggered.

Evidence:

- `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java`
  (source SHA-256 `c29b32bf6874b245859357d926773193c15771a6eb254f97edac57541ae5cb90`)
- `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/OOBEActivationHelper.java`
  (source SHA-256 `6ebcb7eef7a03459a76b9c21cd59b61a30947f2b00a5624a4646825b8e3223d`)
- `findings/phase-6ku-low-privilege-boundary.md`

### 高可信推論：selected Amazon IPC APIs do not control HOME

The bounded `AmazonActivityManagerService.BinderService` review shows:

- `isOnHomeStack()` reads focused-stack state only.
- `onActivityResume()` stores the foreground component and notifies registered
  observers.
- `registerActivitySwitchObserver()` and its unregister counterpart enforce
  `com.amazon.permission.ACTIVITY_SWITCH_WATCHER`.
- `preWarmApplicationForUser()` checks `com.amazon.permission.APP_PREWARM`,
  then clears calling identity and follows a process-prewarm path ending in
  `startProcessLocked`; the check result is not consumed in the bounded body.

The last item is an authorization-review candidate, not a HOME writer or a
root result. The saved enforcing-policy service lookup did not provide a shell
handle, and no transaction or process-start probe was sent.

Evidence:

- `fosservices/disassembly.log:40374-40416,40453-40534,40535-40564`
- `artifacts/phase6ax/activity-manager-home-surface-20260805-01/activity-manager-binder-methods.csv`
  (SHA-256 `9ce611abaebb5dae3796b48cced862a9a3730abdd9fdfcf546dbad5968576879`)
- `artifacts/phase6av/ipc-method-closure-20260805-05/result.md`
  (SHA-256 `61b772a525f5bd04ea599e2331e01a47d83e6b58b377f2d25e529cfd7cc73b78`)

### 已證實、但與 HOME 無關：ASP tablet permission branch

`AmazonAspService.BinderService.hasCallerGotPermission()` returns true for a
device type equal to `tablet` before checking
`com.amazon.permission.ASP_PERMISSION`. `command(I,[B,[B)I` calls this helper
and otherwise returns `-EACCES`. This is a sensitive audio/native command
boundary, but the bounded body has no PackageManager, ActivityTaskManager,
preferred-activity, or Fire Launcher sink. No ASP transaction or native command
was sent.

Evidence: `fosservices/disassembly.log:82014-82077`.

### 已證實、但與 HOME 無關：kernel/Amazon driver surfaces

The PS7331 GPL source review found sensitive CMDQ, GED, `/proc/lk_env`, IDME,
lifecycle, and telemetry surfaces. The audited source scope contains no
`PackageManagerService`, `ActivityManagerService`, HOME resolver, Binder
transaction, or package-state writer edge. Existing GED work was read-only
telemetry; CMDQ, sysenv writes, and other hardware-affecting operations were
not executed.

Evidence:

- `findings/phase-6bq-ged-readonly-ioctl.md`
  (SHA-256 `bdb0c190aa2feb8285f637228a50738ee8120137c804eaf70455d74cdb2e91b4`)
- `findings/phase-6br-amazon-kernel-user-surfaces.md`
  (SHA-256 `6996f2f77e7e5847c99d252b7df9969eb597c4c662dfa0a52ff7127f844a66f6`)
- `findings/phase-6fs-p5-driver-source-audit.md`
  (SHA-256 `e3eb853972388b25ca2e034a003c84cfbdf99182be93e3311404011253396bf4`)

## Decision table

The machine-readable classification is
`output/tables/phase6ky-route-classification.csv`. The host-only checker
`tools/scripts/audit_phase6ky_amazon_ipc_boundaries.py` generates a checked
copy under `output/tables/phase6ky-validation/` and intentionally uses
conservative dispositions.

| Route | Result | Confidence | Safe disposition |
|---|---|---|---|
| Standard PMS HOME setter | Known formal sink; already tested | Confirmed | Do not repeat without a changed premise |
| KFT launcher component writer | Child/profile-scoped state writer; no shell route | Confirmed | Static only; no private transaction |
| AppCompat/Eve resolver callbacks | Delegation/null fallback; no Fire override | Strong evidence | Host-only closure |
| OTA/OOBE receiver | Setup-only component/state path | Confirmed | Do not trigger |
| AMS prewarm | Static authorization anomaly candidate; process prewarm only | Strong evidence | No transaction or exploit probe |
| ASP tablet branch | Sensitive non-HOME command boundary | Confirmed | No native command |
| CMDQ/GED/sysenv/IDME/lifecycle | Sensitive driver surfaces; no HOME edge | Strong evidence | Read-only/source-only |

## Remaining unknowns

1. Runtime-loaded native `fosinit` callbacks outside the preserved XML/VDEX
   scope are not universally proven absent. The next safe step would be a
   completeness/hash cross-check only.
2. The helper body reached by AMS prewarm is not a HOME path in the bounded
   artifact, but every upstream caller contract is not reconstructed. Any
   future review must remain host-only and must not send the Binder call.
3. A formal HOME replacement would still require a changed resolver candidate
   set, privileged/system identity, or an authorized user-facing redirect.
   Existing accessibility redirect evidence is a foreground fallback, not a
   PackageManager HOME replacement.

## Reproduction

```sh
python3 tools/scripts/audit_phase6ky_amazon_ipc_boundaries.py \
  --output-dir output/tables/phase6ky-validation
python3 -m py_compile tools/scripts/audit_phase6ky_amazon_ipc_boundaries.py
```

Both commands are host-only. The script records source/artifact hashes and
route anchors; it does not invoke `adb`, `service call`, `ioctl`, `am`, `pm`,
or any native executable.
