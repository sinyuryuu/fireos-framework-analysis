# Phase 6MN — Amazon IPC/OOBE caller-to-user-scope closure

Date: 2026-08-10
Target: Fire HD 10 / KFTRWI / trona / Fire OS 7.3.3.1 (PS7331)
Mode: **host-only, preserved-evidence analysis**

## Executive result

This phase integrates the already preserved Amazon IPC, PackageManager, vendor
callback, and OOBE/helper evidence into one caller → permission → identity →
sink → user-scope ledger. It does not contact the tablet and does not replay a
Binder transaction.

The generated matrix contains 42 bounded routes:

- 7 previously curated caller/provenance rows;
- 25 exact PackageManager/package-state/preferred-state invoke sites;
- 2 registered vendor HOME callback implementations; and
- 8 grouped OOBE/helper signals.

The strongest new closure is:

> No route in the selected artifacts demonstrates an untrusted caller reaching
> a User-0 Fire Launcher/HOME state sink. The known low-privilege tx4 path is
> settings-only; the launcher-specific tx3 path is scoped by supplied child
> `UserInfo.id`; prewarm only starts a process; the OOBE path is a guarded
> system lifecycle; and the reviewed vendor HOME callback delegates to the
> standard PackageManager resolver without a Fire Launcher literal.

This is a **bounded negative / Strong evidence**, not a binary-wide proof of
absence. The full private Binder caller universe, exact OOBE `Context` user
mapping, and every runtime protected-broadcast source remain outside this
closure.

## Status vocabulary

| Status | Meaning in this report |
|---|---|
| **Confirmed** | Directly represented by preserved runtime evidence or an exact static row with the stated scope. |
| **Strong evidence** | Multiple preserved artifacts support the result, but the full runtime reachability or user mapping is not proven. |
| **Probable** | The bounded evidence supports the interpretation, with a material unresolved branch. |
| **待驗證** | A specific missing artifact or mapping is required before a stronger claim. |
| **已排除** | The selected evidence rules out the narrower claim as stated; it does not prove a broader absence. |
| **因風險拒絕測試** | The experiment would mutate lifecycle, user, package, OOBE, or privileged Binder state and was not run. |

## 1. Route-by-route conclusion

### 1.1 H2 household and child-user routes

**Strong evidence — child/profile lifecycle, not User-0 HOME.**

`H2ClientService` is exported but signature-bound by `BIND_SERVICE`. Its
`addUser()` chain reaches `AmazonUserManager.createChildUser()` through the
household/profile workflow. The preserved provenance records no Fire Launcher
or formal HOME writer in this bounded APK path. The child route therefore has
the following shape:

```text
H2ClientService
  -> IH2ClientService.addUser()
  -> HouseholdController.createUser()
  -> UserHelper / AndroidUserHelper
  -> AmazonUserManager.createChildUser()
  -> child/profile lifecycle state
```

No shell binding or transaction replay was performed. Binding the service,
creating a child user, or changing profile state is outside this host-only
closure and is **因風險拒絕測試**.

### 1.2 `IAmazonUserManager` transaction 3

**Strong evidence — child-scoped package-state writer, not a normal User-0
selector.**

The recovered `enableKftLauncherComponent(UserInfo)` method contains the
Fire/Launcher3/Tahoe package/component setters. Its input is a supplied
`UserInfo`; the relevant scope is `UserInfo.id` from the child lifecycle. The
static row does not establish an unconditional User-0 invocation or a formal
HOME preferred-activity write.

The route is represented by `CALLER-03` and the corresponding `PMS-*` rows in
the matrix. Sending tx3 was not allowed: it would invoke a private launcher
state mutator and would require a complete user/package rollback.

### 1.3 `IAmazonUserManager` transaction 4

**Confirmed — low-privilege settings confused deputy, with no HOME sink.**

The existing physical evidence shows an ordinary APK reaching
`setUserSetupComplete(UserInfo)` and causing the service to write setup-state
settings for the supplied user after clearing Binder identity. The preserved
call chain is:

```text
ordinary APK
  -> amazonusermanagerservice / tx4
  -> IAmazonUserManager.Stub.onTransact()
  -> BinderService.setUserSetupComplete(UserInfo)
  -> clearCallingIdentity()
  -> putIntForUser(user_setup_complete, userInfo.id)
  -> putIntForUser(tv_user_setup_complete, userInfo.id)
  -> restoreCallingIdentity()
```

The physical run left PackageManager state, the Fire package, and HOME
unchanged. This is a real settings-state authorization finding, but it does
not provide a launcher replacement or a route to `setHomeActivity`.

### 1.4 Amazon Activity Manager prewarm

**Strong evidence — process-prewarm confused deputy, no launcher sink.**

The preserved PS7331 method checks `APP_PREWARM`, discards the result in the
reviewed disassembly, clears identity, and reaches a process-start sink. The
physical test observed only the temporary target process. No call to
`setHomeActivity`, preferred-activity APIs, component state APIs, or Fire
Launcher restoration was observed.

This remains a secondary process/resource finding. It is not evidence of root,
HOME control, or a safe relay for package-state mutation.

### 1.5 Post-system-OTA OOBE sender and helper

**Strong evidence — guarded system lifecycle; exact Context/user mapping
待驗證.**

The system-server path is:

```text
AmazonPackageManagerService.onBootPhase(550)
  -> isUpgrade()
  -> protected BOOT_AFTER_SYSTEM_OTA broadcast
  -> BootAfterSystemOTAReceiver
  -> enable OobeHomeActivity
  -> OOBEActivationHelper
  -> setup/provisioning settings
```

The helper source uses `Settings.Secure.put*` and `Settings.Global.put*` with a
`ContentResolver`, and `PackageHelper` uses the context-derived
`PackageManager` for component state. No `ForUser` overload or explicit user ID
is visible at those helper call sites. Therefore the evidence proves
**context-bound scope**, not User 0. The `FG` method suffix is not accepted as
proof of foreground-user identity.

The helper sources contain no ordinary `setHomeActivity`,
`replacePreferredActivity`, or Fire Launcher write. OOBE lifecycle state is
not treated as a normal HOME-selection API. Manual broadcast, OOBE activation,
provisioning-key writes, and component enablement were **因風險拒絕測試**.

### 1.6 PackageManager/HOME call-site inventory

**Confirmed within the indexed disassembly — no new Amazon User-0 HOME setter
was found.**

The 25 exact rows include:

- the known child-scoped `enableKftLauncherComponent(UserInfo)` writer;
- fixed OOBE/Gemini/Espresso/ProductPolicy state writers;
- `PackageManagerShellCommand.runSetEnabledSetting()` as the shell front end;
- the standard internal `PackageManagerService.setHomeActivity()` →
  `replacePreferredActivity()` path;
- DevicePolicy and other system-service writers.

The inventory did not find a new Amazon `fosservices` implementation that
invokes `setHomeActivity`, `replacePreferredActivity`,
`addPersistentPreferredActivity`, or an equivalent Fire User-0 HOME restore
method. This is a static invoke-site result, not proof that every Amazon
binary path has been recovered.

### 1.7 Vendor HOME callbacks

**Confirmed in the selected callback artifacts — no Fire-specific final
selection override.**

`AppCompatActivityStackSupervisorCallback` delegates to
`IPackageManager.resolveIntent` and applies an `isUninstalledApp` filter. It
does not contain a hardcoded Fire Launcher literal. `EveActivityStackSupervisorCallback`
has no concrete `resolveIntent` override in the selected artifact and inherits
the base behavior. The callbacks therefore do not supply evidence that Amazon
rewrites a third-party resolver result to Fire Launcher.

## 2. Evidence matrix and reproducibility

The analyzer is:

```text
tools/scripts/audit_phase6mn_ipc_user_scope_closure.py
```

It was run in two modes:

```sh
python3 -m py_compile tools/scripts/audit_phase6mn_ipc_user_scope_closure.py
python3 tools/scripts/audit_phase6mn_ipc_user_scope_closure.py --dry-run
python3 tools/scripts/audit_phase6mn_ipc_user_scope_closure.py
```

The dry-run reported the same ten input paths and 42 route rows without
writing. The actual run wrote only new Phase 6MN outputs. It refuses to
overwrite an existing artifact directory, table, or graph.

Primary outputs:

| Output | Purpose | SHA-256 |
|---|---|---|
| `artifacts/phase6mn-ipc-user-scope-20260810-01/route-matrix.csv` | write-once 42-row route ledger | `a156538f89cff05e098a01fce169fda4e88f65b86fe4b06054d740cbd615e56b` |
| `artifacts/phase6mn-ipc-user-scope-20260810-01/summary.json` | run mode, counts, safety flags, bounded conclusion | `36e2c71079b4482fbb64e4672a57a00d9a2d9e5b233395e3cce3fa4089dbe669` |
| `artifacts/phase6mn-ipc-user-scope-20260810-01/input-manifest.csv` | input path/size/hash manifest | `afe09b2b8985e245d9835a53b58d5c9ec3fe8033bd69633b8cc8068c49d11760` |
| `artifacts/phase6mn-ipc-user-scope-20260810-01/route-flow.mmd` | host-only provenance graph | `a4c3ee80a19fd3d02423451318aa583bc3dba4eee26ec1d4bf40d7fdc0dc653a` |
| `output/tables/phase6mn-ipc-user-scope-20260810-01.csv` | review copy of route ledger | `a156538f89cff05e098a01fce169fda4e88f65b86fe4b06054d740cbd615e56b` |
| `output/call-graphs/phase6mn-ipc-user-scope-20260810-01.mmd` | review copy of graph | `a4c3ee80a19fd3d02423451318aa583bc3dba4eee26ec1d4bf40d7fdc0dc653a` |

The artifact directory also contains `sha256sums.txt`. The complete input
hash list is in `artifacts/phase6mn-ipc-user-scope-20260810-01/input-manifest.csv`
and is summarized in `findings/phase-6mn-evidence-index.md`.

## 3. Answer to the launcher question

The integrated evidence does **not** identify a new shell-accessible Amazon
route that can change the formal User-0 HOME result without touching Fire
Launcher. Specifically:

| Candidate control surface | Phase 6MN result |
|---|---|
| Ordinary `set-home-activity` / preferred state | Existing Phase 3 evidence remains authoritative: record can persist while Fire wins; no new low-privilege writer found here. |
| KFT launcher state writer | Exists, but child-scoped by `UserInfo.id`; no User-0 selector proven. |
| `IAmazonUserManager` tx4 | Ordinary-app reachable in prior test, but writes setup settings only. |
| Amazon Activity Manager prewarm | Process-start sink only. |
| OOBE/OTA receiver | Guarded lifecycle path; setup/OOBE side effects; manual trigger rejected. |
| Vendor HOME callback | Standard resolver delegation/filter; no Fire hardcode in selected implementations. |
| DevicePolicy/PMS internal writers | Trusted/internal paths; no ordinary shell capability established. |

Thus the current Phase 6MN result is **not a new viable HOME workaround**. It
does, however, close the most relevant static provenance gap without
introducing a risky device experiment.

## 4. Remaining questions

1. **OOBE Context → user mapping — 待驗證.** Trace the exact Context creation
   and ContentResolver user handle using preserved framework sources/artifacts.
   Do not activate OOBE or write setup state on the tablet.
2. **Full protected-broadcast source set — 待驗證.** Extend the host-only
   manifest inventory to all preserved system package manifests; do not send
   `BOOT_AFTER_SYSTEM_OTA` manually.
3. **Complete private Binder caller universe — 待驗證.** Expand only from
   preserved AIDL/Stub/registration artifacts; do not guess transaction codes
   or replay mutators.
4. **PMS resolver equivalence — 待驗證.** A method-level AOSP-vs-PS7331
   comparison remains the smallest route to distinguish standard resolver
   ordering from an unobserved Amazon branch.

## 5. Explicitly rejected or out-of-scope operations

The phase did not and will not infer authorization from a service name. It did
not perform:

- unknown `service call`, private Binder replay, or transaction fuzzing;
- H2 bind/create-child or KFT tx3 invocation;
- manual `BOOT_AFTER_SYSTEM_OTA` broadcast or OOBE component enablement;
- Fire Launcher disable/hide/suspend/uninstall/force-stop/data clear;
- settings/provisioning mutation, OTA/recovery, reboot, partition write,
  remount, Root, exploit, or driver ioctl.

The tablet unlock credential supplied in conversation was not used, stored, or
included in the analysis.

## Final disposition

**Strong evidence:** the selected PS7331 IPC/OOBE and HOME callback artifacts do
not expose a demonstrated untrusted-to-User-0 Fire Launcher/HOME state route.

**Confirmed secondary findings:** tx4 setup-state confused deputy and prewarm
process/resource confused deputy remain real but are not launcher controls.

**No new workaround:** Phase 6MN does not change the current assessment that a
formal, persistent, reversible, no-Root User-0 HOME replacement has not been
demonstrated.

The next low-risk research value is host-only completion of OOBE context-user
semantics or PMS AOSP/Fire method comparison. Live Binder replay, OOBE
activation, and package-state mutation are not justified by this evidence.
