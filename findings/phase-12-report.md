# Phase 12 — broad privilege-surface closure

## Executive result

This phase broadened the review beyond Launcher-only logic across four
independent surfaces: existing test evidence, Amazon Binder/package-state
writers, OTA/post-install paths, and MTK/Amazon driver callers. The review was
host-only except for one new serial-bound read-only baseline. No root exploit,
unknown Binder transaction, driver open/ioctl, OTA/recovery execution, reboot,
partition write, Fire Launcher state mutation, or Fire Launcher data deletion
was performed.

**Confirmed:** the current device remains User 0 with SELinux Enforcing and
formal HOME `com.amazon.firelauncher/.Launcher` at priority 50.

**Strong evidence:** the bounded Framework/Binder corpus does not close an
ordinary-app or shell path to User-0 Fire package/component state, HOME state,
UID 0, or a protected partition.

**Confirmed static capability, not runtime access:** the signed OTA script
contains recovery-time partition sinks; its caller, verifier, AVB/SELinux
handoff and runtime execution were not established.

**Unknown:** all twelve driver surfaces remain missing at least one of the
shipped caller, node policy, identity/domain, validation, or effect edges.

## Current baseline

The serial-bound capture is
[`adb/phase12/PHASE12-BASELINE-20260810-01`](../adb/phase12/PHASE12-BASELINE-20260810-01)
and its summary is
[`findings/phase-12-readonly-baseline.md`](phase-12-readonly-baseline.md).

| Field | Observation | Status |
|---|---|---|
| Serial | `G001LT0511550CFT` | Confirmed |
| Fingerprint | `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys` | Confirmed |
| Current user | `0` | Confirmed |
| SELinux | `Enforcing` | Confirmed |
| User 0 HOME | `com.amazon.firelauncher/.Launcher`, priority `50` | Confirmed |
| User 10 HOME | `com.android.settings/.FallbackHome`, priority `-1000` | Confirmed |

The post-host guard
[`adb/phase12/PHASE12-POST-HOST-GUARD-20260810-01`](../adb/phase12/PHASE12-POST-HOST-GUARD-20260810-01)
repeated only `get-state`, fingerprint, current-user, User-0 HOME resolution,
and the Fire package dump. It matched the baseline: User 0, the same PS7331
fingerprint, and Fire Launcher HOME priority 50. Its SHA-256 manifest passed.

## Control-surface findings

### Amazon Binder and package state

The worker closure identifies the known KFT writer as child/profile-scoped:
the sink consumes a supplied `UserInfo.id`, and the observed effect is on the
child user. It does not prove a User-0 route. AmazonPackageManager metadata
writers retain the `ADD_RM_PKG_METADATA` gate and the private interface has no
formal HOME or enabled-state setter. Its facade delegates enabled-state and
preferred operations to ordinary PMS checks.

`IAmazonUserManager` service-handle reachability is not method authorization.
The exact tx3 authorization and arbitrary `UserInfo` construction edge remain
`UNKNOWN`; no unknown transaction was sent. DPM generic restrictions still
flow through active-admin/owner checks. ProxyReceiver requires a system-app
PendingIntent creator; the saved ordinary-app result was negative.

### OTA and post-install

The PS7331 `updater-script` statically names system/vendor/boot and several
boot-chain partition sinks. This is a recovery/update-binary capability
contract, not evidence that an app or shell can invoke it. Sideload validation,
release metadata, device/version checks, signature/PVT checks, and recovery
handoff remain gates. The post-OTA OOBE sender uses the protected
`RECEIVE_BOOT_AFTER_SYSTEM_OTA` path; delivery, user handoff, and native
verifier behavior were not replayed.

No malformed package, symlink/traversal input, update-binary invocation,
recovery/sideload, or partition operation was performed. These remain
**因風險拒絕測試**.

### MTK/Amazon drivers

The driver review covers CMDQ, ION, M4U, uinput, AUXADC, performance,
Amazon liquid detection, Amazon driver-test, thermal/PMIC, USB, RPMB, and the
MediaTek SoC directory. All remain `UNKNOWN`: source/Kconfig, init mode, a
file-context label, or an ioctl handler alone does not establish a retail
caller, SELinux allow, UID/domain, validation, or a package/HOME/credential
effect. No device node was opened. The raw driver CSV has a 14-column header
but 13-field data rows; the normalized table therefore forces all driver
confidence values to `UNKNOWN` and treats the worker narrative as the
authoritative summary until the raw CSV is repaired.

### Existing runtime evidence

The prior child-profile, DPM, package-state, HOME, OTA and Accessibility
captures were indexed without replay. The Phase 11 Accessibility T01/T02
results remain foreground-observation-only: formal HOME stayed Fire and the
current APK did not produce a reliable redirect. This does not prove that every
future Accessibility implementation is ineffective, but it is not a stable
replacement result.

## Overall decision

**No new reproducible low-privilege route was established.** The formal HOME
replacement and Fire Launcher disable objectives remain unachieved without
Root/system privilege or an as-yet unproven control-surface flaw. The present
evidence supports closing the broad static sweep as a bounded negative result,
not declaring that every private API or driver is mathematically impossible.

The safest next research targets are host-only completion of the remaining
exact tx3 Stub/caller and compiled policy/DT joins, followed by a natural,
non-mutating lifecycle observation if a concrete caller is identified. Sending
unknown Binder parcels, invoking update-binary/recovery, opening driver nodes,
or mutating Fire Launcher state is not justified by the current evidence.

## Reproduction

```sh
python3 tools/scripts/capture_phase6ee_current_baseline.py \
  --serial G001LT0511550CFT \
  --output adb/phase12/PHASE12-BASELINE-20260810-01
python3 tools/scripts/build_phase12_report.py --force
```

The normalized matrix is
[`output/tables/phase12-control-surface.csv`](../output/tables/phase12-control-surface.csv),
the evidence index is
[`findings/phase-12-evidence-index.md`](phase-12-evidence-index.md),
and the call graph is
[`output/call-graphs/phase12-control-surfaces.mmd`](../output/call-graphs/phase12-control-surfaces.mmd).
