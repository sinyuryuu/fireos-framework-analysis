# Phase 6X — broad privilege/control-surface continuation

Generation HEAD: `687a236c0b81e44060b3ec6a5a53fdce74eabf3e`
Generated UTC: `2026-08-10T06:56:10.172620+00:00`

## Scope and safety

This phase expands the research beyond Launcher-only behavior. It joins the
existing Phase 6WL corpus with new Framework IPC, 7.3.3.1 OTA, GPL/MediaTek
driver, and prior-test reconciliation evidence. The live observations use the
exact serial `G001LT0511550CFT` and only read-only ADB commands. No unknown
Binder transaction, driver node/ioctl, OTA/recovery execution, exploit payload,
Root attempt, Fire Launcher mutation, reboot, or partition write was executed.

## Current device observation

**已證實：** the device remains PS7331 (`Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`), SELinux Enforcing, and User 0 resolves HOME to `com.amazon.firelauncher/.Launcher` at effective priority 50. User 0 candidates include Microsoft Launcher at 0 and FallbackHome at -1000.

**已證實：** an existing User 10 has a different scope: the saved package
dump reports Fire Launcher `enabled=2`, and the User 10 query returns
FallbackHome. Existing Phase 6NC/6FY evidence shows this is a child/profile
boundary involving Tahoe/Profile Owner, not a User 0 package-state writer.

## Cross-surface result

The ledger contains **78** control observations: 48 prior
  Phase 6WL rows, 3 new IPC rows, 4 OTA rows, 5 GPL/native rows, 4 permission
  rows, 8 exported/OOBE component rows, and 6 live read-only rows. The separate
  reconciliation matrix contains **15**
deduplicated route families.

### 已證實：privileged capability exists, but capability is not reachability

The source and disassembly contain sinks for keyguard/SystemUI state, OTA and
recovery writers, uinput/power-supply/RPMB operations, package/user/settings
state, and child/profile lifecycle. The required proof standard remains:

`caller → permission/identity gate → user scope → exact sink → observed effect`

No new row closes that chain from an ordinary app or shell to User 0 package,
formal HOME, root identity, or partition effect.

### 已證實：new IPC delta is permission-gated SystemUI surface

`IAmazonKeyguardService.dismissWithPendingIntent`, `setAccessibilityInfo`,
and `setForegroundColor` verify `Binder.getCallingUid()` through
`CONTROL_KEYGUARD` or `com.amazon.permission.AMAZON_CONTROL_KEYGUARD` before
forwarding verified caller identity/package to SystemUI. Transaction number,
publication, protection level, SELinux rule, and runtime caller remain
**待驗證**. These methods are not HOME/PMS/package-state sinks.

### 已證實：OTA evidence does not provide a safe or current-build bypass

The retained OTA is preserved 7.3.3.1 evidence and its provenance README
explicitly records the historical PS7330→PS7331 version boundary. The current
live fingerprint is PS7331.4463N, but the package was not executed in this
phase. Native
updater/recovery writers and staging paths remain statically capable, but
caller identity, AVB/rollback handoff, canonicalization/no-follow behavior,
and runtime effect are unresolved. No package was constructed or executed.

### 已證實：GPL/native driver surfaces do not close a privilege route

The 7.3.3.1 source confirms generic uinput fops, provider-gated power-supply
sysfs writes, and RPMB ioctl-only persistence operations. No exact shipped
caller/package/UID/domain was joined to a package/HOME/root sink. The archive
also has no `vendor/mediatek` path; that is only a provenance negative, not a
claim that every vendor artifact is absent.

### 已證實：permission declarations alone do not form a deputy

The residual permission scan found two `USE_SDK` declarations at `0x0` and one
`PLUGIN` declaration at `0x1`, plus one bounded declaration without a safely
decoded protection level. No requester, granted holder, exported consumer,
method-local caller gate, or sensitive sink was joined to these declarations.
They remain static candidates, not an elevation path.

### 已證實：OOBE/DCPMS surfaces remain lifecycle- or policy-scoped

`BootAfterSystemOTAReceiver` and its activation helper have protected OTA/OOBE
guards and setup-state sinks; DCPMS exported receivers update profile/CDE
policy; ProductPolicy registration is in-process. The bounded source contains
no new Fire Launcher HOME setter. Numeric user, producer permission/identity,
and external caller edges remain **待驗證**.

### Source package scope

The unpacked 7.3.3.1 source contains `platform/kernel/mediatek/4.4`,
`platform/device/amazon/kernel/driver`, and a bounded `platform/system/core`
scope centered on libcutils. The exact source audit did not find
`system/core/init/selinux.cpp` or a complete init policy-loader tree in this
package. Therefore the GPL package supports kernel/driver provenance and
differential analysis, while `/init` policy-loader conclusions still require
the saved binary/AOSP anchor. The absence of a `vendor/mediatek` member is
recorded only as a path-level negative.

### 已排除：replaying equivalent known routes is not productive

The 15-row reconciliation matrix marks ordinary preferred/set-home, Fire
package-state gates, KFT child scope, DPM, service visibility, OTA/driver/root,
and Accessibility foreground paths as completed, static-gap, or closed-no-
retest. Repeating denied component-disable, guessing Binder codes, opening
driver nodes, or executing OTA/recovery would not add the missing caller and
identity evidence and would violate the experiment boundary.

## Candidate assessment

| Candidate | Classification | Reason |
|---|---|---|
| User 10 Tahoe/profile HOME | **已證實但非 User 0 replacement** | Child/profile-scoped lifecycle; no cross-user User 0 effect. |
| Keyguard Binder methods | **待驗證 / not a launcher route** | Explicit permission gate; SystemUI presentation sink only. |
| uinput/power/RPMB source surfaces | **高可信推論：capability only** | No shipped low-privileged caller/domain/sink join. |
| OTA staging/recovery | **因風險拒絕測試** | Requires package/recovery/partition execution; current build/provenance gaps remain. |
| Accessibility/foreground redirect | **已排除為正式 HOME** | Historical bounded runs did not establish durable resolver replacement. |

## Remaining minimum host-only work

1. Resolve exact 7.3.3.1 artifact provenance and any missing `product_policy`
   or recovery mapping without executing it.
2. Join any remaining Amazon Binder publication to declared permission,
   SELinux/service-manager policy, caller identity, and user-scoped sink.
3. Finish exact native ELF load/caller joins for only those nodes with a
   confirmed policy allow; do not open the nodes.

If those joins remain open, the defensible conclusion is that no safe,
reproducible ADB-only privilege path has been demonstrated; the closest
observed alternate desktop behavior is child/profile-scoped Tahoe, not a
User-0 replacement or Root acquisition.

## Reproduction commands

The device captures were produced with the existing serial-bound read-only
scripts (use a new output directory for every capture):

```sh
tools/scripts/capture_phase6mv_runtime_readonly.sh   --serial G001LT0511550CFT   --output adb/phase6x/PHASE6X-DEVICE-READONLY-YYYYMMDD-NN

python3 tools/scripts/capture_phase6ee_current_baseline.py   --serial G001LT0511550CFT   --output adb/phase6x/PHASE6X-CURRENT-SCOPE-READONLY-YYYYMMDD-NN

python3 tools/scripts/build_phase6x_surface.py --dry-run
python3 tools/scripts/build_phase6x_surface.py --force
```

The first two commands are read-only; the last two are host-only. The scripts
do not call private Binder transactions, open driver nodes, mutate settings or
package state, reboot, or execute OTA/recovery code.
