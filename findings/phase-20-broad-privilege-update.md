# Phase 20 — Broad privilege-surface closure

Date: 2026-08-10 (Asia/Taipei)

Phase 20 continues the search beyond Launcher. It evaluates any route that
could eventually obtain enough authority to change Fire package/component
state, HOME, user policy, OTA/recovery state, UID 0, or kernel-driver/memory
state. All work in this phase is host-only static analysis of preserved PS7331
artifacts and existing evidence.

## Executive result

**Confirmed:** 43 new residual rows were normalized from five independent
ledgers. None closes the complete chain:

```text
ordinary APK / ADB shell
  -> accepted permission + SELinux/service-manager gate
  -> trusted identity or User-0 authority
  -> Fire package state / HOME / UID 0 / partition / kernel-memory sink
```

**Strong evidence:** KFT transaction 3 now has a static upstream through
`H2ClientService` and `AndroidUserHelper.addAndroidUser`. The H2 service is
exported but protected by a `signature|amazon` bind permission. The KFT setter
path retains the incoming Binder identity while changing package state; its
later `clearCallingIdentity()` is scoped to later DPM/profile-owner work. This
is a real trusted-side child/profile writer, not evidence of an ordinary-app
identity relay. Evidence: `P20A-001`, `P20A-004`.

**Confirmed, bounded:** DCPMS and the Amazon window/PIP callbacks do not expose
a PackageManager, HOME, or package-state sink in the analyzed paths. The
profile picker is a current-user UI launch, not a HOME writer. Evidence:
`P20A-002`, `P20A-003`, `P20A-005`, `P20A-006`.

**Strong evidence:** `/vendor/bin/meta_tst` has shipped gsensor and USB sysfs
diagnostic edges with init identity and CIL permissions; `rpmb_svc` has a
shipped TEE/RPMB edge. These remain hardware/diagnostic sinks with missing
exact control-flow, selected DTB/object, mode, and authentication edges. No
row reaches PackageManager, HOME, UID 0, or kernel-memory control. Evidence:
`P20C-004`, `P20C-005`, `P20C-007`.

**Confirmed, bounded:** the OTA Java verification/install handoff and the
PS7331 `update_verifier` / `install-recovery.sh` capabilities are trusted
post-update sinks. The saved corpus does not establish shell/ordinary-app
reachability, recovery UID/SELinux transition, AVB key authority, or rollback
index enforcement. Evidence: `P20B-02`–`P20B-11`.

**No device mutation:** no Binder transaction, service call, driver open/ioctl,
OTA/recovery/sideload execution, reboot, package/settings mutation, Fire
Launcher mutation, root attempt, or partition write was performed.

## Phase 20 matrix

The normalized ledger is
[phase20-caller-gate-sink.csv](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/output/tables/phase20-caller-gate-sink.csv).
It contains 43 unique records:

| Workstream | Rows | Main result |
|---|---:|---|
| IPC | 6 | KFT/H2 caller and identity order narrowed; no ordinary User-0 sink |
| OTA/recovery | 11 | Java/native trusted capability mapped; low-privilege reachability unresolved |
| MTK/Amazon drivers | 10 | `meta_tst` and `rpmb_svc` partial static callers; no privilege sink |
| No-repeat reconciliation | 4 | Four residuals retained; live risky routes rejected |
| Provenance | 12 | PS7331 source/image/OTA scope and PS7330 pull provenance separated |

## Findings by surface

### A. Amazon IPC and system services

`H2ClientService` is an exported, single-user service protected by
`com.amazon.alta.h2clientservice.permission.BIND_SERVICE`, declared
`signature|amazon`. Its AIDL dispatch does not add a second visible caller-UID
check in the recovered slice, but the required signature-level bind gate and
unknown production caller set remain decisive. The child workflow can feed the
KFT lifecycle; it does not directly call a HOME or PackageManager setter.

`enableKftLauncher(UserInfo)` changes state for the returned child/profile
user. The incoming identity remains active through the package setters; the
later identity clear is not shown to launder that call into system identity.
The exact installed UID/signature grant and PMS acceptance are not present in
the saved host corpus, so this is not a safe candidate for `service call`.

`AmazonProfileService.startProfilePicker` launches configured UI as the current
system user and has no bounded HOME/package-state sink. The PIP/overscan path is
system-server callback context and ends in window/display policy. DCPMS is
signature-bound and its bounded service paths expose decision retrieval and
callbacks, not a sensitive platform writer.

### B. OTA, recovery and post-install

The static Java chain reaches hash validation, `RecoverySystem.verifyPackage`,
device/update-property validation, staging and `UpdateSystem.install`. This
proves a privileged OTA lifecycle, not a shell caller.

The PS7331 `update_verifier` contains block/caremap and slot-outcome capability;
`install-recovery.sh` contains recovery repair/signature write capability.
Neither proves AVB key authority or rollback-index comparison. Native cache
analysis found a regular-file check, `readlink_chk`, length/string checks and
cleanup, but no complete no-follow/same-object/race proof or final write
authorization edge. No symlink, traversal, race, malformed OTA, downgrade or
recovery replay was performed.

### C. MTK/Amazon driver surfaces

The new static caller evidence is limited:

- `meta_tst` runs from `meta_init.rc` with `radio system wifi` users and has
  gsensor imports plus CIL access to `gsensor_device`.
- `meta_tst` has Android USB sysfs path and write/open references with matching
  CIL permissions.
- `rpmb_svc` contains RPMB authenticated API/device/ioctl references and runs
  through the TEE domain with CIL access to the RPMB block device.

These are diagnostic, sensor, USB-control and authenticated-storage surfaces.
They are not a PackageManager, HOME, UID-0 or arbitrary kernel-memory sink. The
remaining CMDQ, M4U, uinput/evdev, USBDEVFS/URB, performance and liquid
detection rows remain unresolved rather than being treated as vulnerabilities.

### D. Provenance correction

PS7331 source, OTA and extracted boot artifacts are exact PS7331 inputs. Some
`artifacts/framework` and `artifacts/services` files came from the saved
2026-08-03 device pull and must remain classified by pull provenance; equal JAR
hashes do not make VDEX/ODEX or the whole build identical. The PS7331
`system/build.prop` hash is now recorded as:

`068b257362514773113671a7be67ff1288c484382ee43694872a19dbcb93e15e`

The saved PS7330 and PS7331 runtime slices remain separate.

## Required classifications

### 已證實

- KFT/H2 has a real child/profile-scoped static writer and a signature-bound
  upstream workflow, with no proof of ordinary caller reachability.
- DCPMS/profile picker/window callback paths reviewed here do not terminate in
  HOME or package-state sinks.
- `meta_tst` and `rpmb_svc` provide partial static driver caller evidence.
- PS7331 OTA/update_verifier/recovery capabilities and exact provenance are
  present in the saved artifacts.

### 高可信推論

- No safe ADB/API route currently closes ordinary caller → accepted trusted
  authority → Fire Launcher/package-state or UID-0 sink.
- The strongest remaining work is host-only provenance/policy/dataflow
  closure, not guessed private Binder payloads or driver operations.

### 待驗證

- Exact installed H2 caller UID/signature and PMS cross-user/protected-package
  acceptance for the legitimate KFT workflow.
- Selected DTB/object and exact native control flow for `meta_tst`/`rpmb_svc`.
- Recovery UID/domain transition, AVB authority and rollback-index comparison.
- Complete fosinit/Vending/deny-list edges listed by `P20D-*`.

### 已排除（有界）

- DCPMS/profile-picker/window callback as a direct HOME/package-state writer.
- `meta_tst` or `rpmb_svc` as an already-proven privilege-escalation path.
- PS7331 OTA metadata or `update_verifier` strings as shell OTA reachability.
- Replaying Phase 1–19 equivalent launcher, accessibility, KFT, Binder, OTA,
  driver or root tests.

### 因風險拒絕測試

- Unknown Binder transactions, H2 binding or child-user creation.
- Any `/dev` open/ioctl, including ION, CMDQ, M4U, gsensor, RPMB or USB.
- OTA/recovery/sideload/reboot, malformed input, symlink/race or partition
  tests.
- Root/GhostLock/BROM/bootloader attempts and Fire Launcher state mutation.

## Next safe work

The only justified next steps are host-only joins for `P20D-FOSINIT-001`,
`P20D-ION-003`, `P20D-VENDING-002` and `P20D-DENYLIST-004`, plus exact
provenance of the remaining OTA/driver edges. There is no Phase 20 evidence
that justifies a new device POC. A real-device experiment becomes justified
only if a documented, public, reversible API path reaches a concrete sink and
has a complete rollback plan.

## Reproduction

```sh
python3 tools/scripts/build_phase20_privilege_closure.py --root . --verify-only
python3 tools/scripts/build_phase20_privilege_closure.py --root .
```

Both commands are host-only and do not connect to the device.
