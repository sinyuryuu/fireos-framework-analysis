# Phase 6KT — PS7331 recovery/updater provenance audit

Date: 2026-08-10
Scope: host-only, read-only analysis of preserved PS7331 artifacts
Device mutation: none
Classification: **Strong evidence; no low-privilege OTA entry demonstrated**

## Executive result

The PS7331 OTA material contains a high-privilege native updater capable of
extracting files and writing named partitions. The preserved Java OTA path
does not, by itself, establish that a shell UID or ordinary application can
invoke that updater. The recovery verification call and the native updater
handoff remain separate provenance boundaries.

This phase therefore does not produce a root path, a launcher replacement, or
an OTA exploit. It closes the safe question that can be answered from the
available artifacts: the update path has strong verification and staging
markers before the privileged handoff, while the final recovery/native caller
provenance is not present in the analyzed Java artifacts.

## Evidence inputs

The reproducible audit is:

```text
tools/scripts/audit_phase6kt_recovery_provenance.py
artifacts/phase6kt/recovery-verifier-audit-20260810-01/audit.json
artifacts/phase6kt/recovery-verifier-audit-20260810-01/sha256sums.txt
```

The principal input hashes are recorded in `audit.json` and include:

| Input | SHA-256 | Classification |
|---|---|---|
| `firmware/extracted/PS7331/META-INF/com/google/android/update-binary` | `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b` | Native updater artifact |
| `firmware/extracted/PS7331/META-INF/com/google/android/updater-script` | `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248` | Edify command input |
| `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/otacert.pem` | `5d52405362dcc9e755a4d972074ac7f886a5450e18fb6a6c2c2dad2b55730fe1` | Preserved OTA certificate |
| `RecoverySystemWrapper.java` | `5cea16a23aadebf9c043791fffb80c4e3a78ca629e8f7c64c82a366983790287` | Java verification wrapper |

The first row is also independently recorded in the Phase 6P native updater
evidence. The repeated hash is a provenance check, not a new artifact.

## Java verification and installation paths

### Validation path

The PS7331 OTA APK contains:

```text
OSUpdateValidator.validateOSUpdate()
  -> UpdateValidator.Helper.assertHash()
  -> RecoverySystemWrapper.verifyPackage()
  -> RecoverySystem.verifyPackage()
  -> OSUpdatePropertiesValidator.assertUpdatePropertiesValid()
```

Locations in the preserved JADX output:

- `OSUpdateValidator.java:42-48` calls the recovery wrapper and maps IO or
  security failures to validation failures.
- `OSUpdateValidator.java:72-77` performs the pending-update hash, recovery
  verification, and update-property checks in that order.
- `RecoverySystemWrapper.java:21-22` is a thin delegation to the Android
  `RecoverySystem.verifyPackage` API; it does not implement the cryptographic
  verifier itself.
- `SideloadVerifier.java:55-58` runs metadata/sanity checks, then the package
  verification wrapper, in the recovery-check path.

These locations prove the Java-side call relationship. They do not prove the
implementation details of the platform recovery verifier because that native
or recovery-side artifact was not executed or recovered in this phase.

### Installation handoff

The separate installation path is:

```text
SideloadInstaller.installSideload()
  -> SideloadVerifier.verifySideloadWithoutRecoveryCheck()
  -> SideloadMover.maybeMoveSideloadFile()
  -> SideloadInstaller.installOSUpdate()
  -> UpdateSystemWrapper.install()
  -> UpdateSystem.install()
```

The relevant preserved source locations are:

- `SideloadInstaller.java:65-74` performs the staging and installation call.
- `SideloadMover.java:29-43` derives a destination from the input basename and
  calls `FileHelper.moveFile`.
- `UpdateSystemWrapper.java:32-43` maps the external-storage prefix, records
  `persist.sys.ota.isScreenOffBeforeOTA`, and calls the framework
  `UpdateSystem.install` API.

The Java `SideloadMover` scan did not find a `canonicalPath` or `NOFOLLOW`
marker. This is **strong evidence of an unobserved Java check**, not proof of
a symlink vulnerability: `FileHelper`, framework/native code, and the actual
recovery staging environment remain outside this bounded observation.

## Native updater capability

The preserved AArch64 `update-binary` is static and stripped, with embedded
mini-debug data recovered in Phase 6P. The existing symbol/CFG audit identifies:

- `PackageExtractFileFn`: `0x401fb8–0x402788`; output open uses flags `0x241`
  and mode `0600`, followed by extraction, `fsync`, and close.
- `WriteToPartition`: `0x413c40–0x4142f0`; opens a target read/write and calls
  the updater write/sync helpers.
- `ota_open`: `0x426338–0x426528`; direct libc `open` at `0x426354`.
- `LoadSrcTgtVersion3` calls `VerifyBlocks` at the preserved call sites;
  the CFG contains block verification and mismatch branches.

The script contains the following fixed named targets. This table is generated
from the preserved updater script; the same records are retained in
`audit.json`.

| Line | Target |
|---:|---|
| 6 | `/dev/block/platform/bootdevice/by-name/system` |
| 10 | `/dev/block/platform/bootdevice/by-name/vendor` |
| 13 | `/dev/block/platform/bootdevice/by-name/boot` |
| 15 | `/dev/block/platform/bootdevice/by-name/preloader` |
| 16 | `/dev/block/platform/bootdevice/by-name/lk` |
| 17 | `/dev/block/platform/bootdevice/by-name/tee1` |
| 18 | `/dev/block/platform/bootdevice/by-name/tee2` |
| 19 | `/dev/block/platform/bootdevice/by-name/spmfw` |
| 20 | `/dev/block/platform/bootdevice/by-name/sspm_1` |
| 21 | `/dev/block/platform/bootdevice/by-name/cam_vpu1` |
| 22 | `/dev/block/platform/bootdevice/by-name/cam_vpu2` |
| 23 | `/dev/block/platform/bootdevice/by-name/cam_vpu3` |

The exact line mapping is generated from the original preserved updater
script, not inferred from the binary marker scan.

This confirms capability, not reachability. No updater binary was executed and
no archive, function table, transaction, or partition input was supplied to
it.

## Security and launcher impact

| Question | Result | Confidence |
|---|---|---|
| Can the native updater write named partitions? | Yes, statically confirmed from the binary and script. | Confirmed |
| Is recovery/package verification present before the normal validation handoff? | Yes, the Java path calls the platform verification API. | Confirmed |
| Is the platform verifier implementation fully identified? | No; the wrapper delegates outside the preserved Java source. | Hypothesis |
| Is a shell/ordinary-app caller to the updater established? | No. | Strong evidence |
| Is there a safe OTA route to disable Fire Launcher? | No evidence. | Disproved for the analyzed low-privilege path |
| Did this phase alter the device? | No. | Confirmed |

The OTA path is therefore not a justified ADB launcher workaround. Pursuing
the unresolved verifier boundary would require recovery/updater execution or
crafted OTA input, which is outside the current safe scope and is not needed
to continue the Framework/HOME analysis.

## Reproduction

Host-only reproduction:

```sh
python3 tools/scripts/audit_phase6kt_recovery_provenance.py \
  --root . \
  --output artifacts/phase6kt/recovery-verifier-audit-20260810-01
```

Expected output is a JSON summary containing nine input hashes. Verify the
generated result with:

```sh
sha256sum -c artifacts/phase6kt/recovery-verifier-audit-20260810-01/sha256sums.txt
```

No ADB command is required.

## Next research value

The remaining useful static task is to recover or identify the exact platform
recovery verifier artifact and correlate its certificate/AVB handoff with the
native updater entry. It should remain host-only. The current evidence does
not justify executing an OTA, sending private Binder transactions, writing a
partition, or switching to a root exploit.
