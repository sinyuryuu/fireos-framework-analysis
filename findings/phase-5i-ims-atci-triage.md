# Phase 5I — MT8183 IMS / ATCI read-only triage

## Scope and safety boundary

This phase was a read-only applicability review of the MediaTek IMS/ATCI
surface on the exact attached device. It did not set a property, start or stop
an init service, open an ATCI socket, send an AT command, invoke an unknown
Binder transaction, change package state, reboot, or execute an exploit.

The exact device was `G001LT0511550CFT`:

| Field | Observed value |
|---|---|
| Build fingerprint | `Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys` |
| Android base | Android 9 / API 28 |
| Overall security patch | 2024-02-01 |
| Runtime platform | MT8183 |
| SELinux | Enforcing |
| Verified boot | green |
| ADB state after collection | `device` |
| HOME after collection | `com.amazon.firelauncher/.Launcher` |

The raw captures are immutable evidence and each complete collection has its
own `sha256sums.txt`:

- `adb/phase5/PHASE5I-IMS-TRIAGE-20260803-01/`
- `adb/phase5/PHASE5I-IMS-TRIAGE-FOLLOWUP-20260803-01/`
- `adb/phase5/PHASE5I-IMS-TRIAGE-FOLLOWUP-20260803-02/`
- `adb/phase5/PHASE5I-IMS-TRIAGE-FOLLOWUP-20260803-04/`

The reproducible read-only collector is
`tools/scripts/capture_phase5i_ims_triage.sh`. It requires an explicit serial,
refuses an existing output directory, has a `--dry-run`, and records stdout,
stderr, exit code, commands, metadata, and SHA-256 values. The host-only
follow-up `PHASE5I-IMS-TRIAGE-FOLLOWUP-20260803-03` is retained as raw evidence
but has an incomplete manifest because a host zsh loop variable overwrote
`PATH`; its later `adb` failures are not device observations.

## Official vulnerability-scope evidence

MediaTek's [March 2022 Product Security Bulletin](https://corp.mediatek.com/product-security-bulletin/March-2022)
lists two separate IMS findings:

- CVE-2022-20053: missing authorization in the IMS service, with possible
  elevation of privilege; the bulletin lists MT8183 and Android 9.0/10/11/12
  affected software families.
- CVE-2022-20054: missing authorization in the IMS service, with possible AT
  command injection; the bulletin likewise lists MT8183 and Android
  9.0/10/11/12 affected software families.

This is chipset/software-family scope evidence only. It is not proof that the
PS7330 vendor binaries are vulnerable, that the device exposes an active IMS
service, or that a shell caller can reach ATCI.

## Runtime observations

### Package, service, and process enumeration

The primary capture's filtered package list found only
`com.android.providers.telephony` for the relevant package pattern. It did not
find a package named `com.mediatek.ims`, `imsservice`, or an equivalent IMS
implementation. The service list contained `imms` (the Android MMS Binder
service) and `telephony.registry`; it did not contain an `ims` or `atcid`
service. The process filter likewise did not show an IMS or ATCI process.

These are observations of the normal runtime snapshot, not a claim that no
vendor binary exists on the read-protected filesystem.

### Vendor init definitions

The shell-readable init configuration records two conditional, disabled
services:

```text
service atcid-daemon-u /vendor/bin/atcid
    interface vendor.mediatek.hardware.atci@1.0::IAtcid default
    socket adb_atci_socket stream 660 radio system
    user system wifi
    group radio system media bluetooth wifi
    disabled
    oneshot

on property:persist.vendor.service.atci.autostart=1
start atcid-daemon-u

on property:persist.vendor.service.atci.atm_mode=1
start atcid-daemon-u
```

`/vendor/etc/init/audiocmdservice_atci.rc` similarly defines a disabled,
oneshot `audio-daemon` using `/vendor/bin/audiocmdservice_atci` and an
`atci-audio` socket. The modem init files define one-shot CCCI setup helpers;
they do not establish an active IMS Binder service in the captured service
list.

The runtime properties included `ro.vendor.md_auto_setup_ims=1`,
`vendor.mtk.atci.boot_completed=1`, `ro.vendor.mtk_ril_mode=c6m_1rild`,
`ro.vendor.vilte_support=0`, `ro.vendor.viwifi_support=0`,
`ro.baseband=unknown`, and `ro.telephony.sim.count=0`. The values show that
the image contains modem-related configuration; they do not show that an IMS
endpoint is active or shell-reachable.

`dumpsys telephony.registry` reported Phone 0 as voice/data
`OUT_OF_SERVICE`, voice/data radio technology `Unknown`, and
`mVoLteServiceState=2147483647` at capture time. That is consistent with the
absence of a usable telephony subscription in this snapshot, but is not a
patch-level determination.

### Vendor binary visibility boundary

The shell could see init references to `/vendor/bin/atcid` and
`/vendor/bin/audiocmdservice_atci`, but the direct read/hash/string attempts
were denied:

```text
adb: error: failed to stat remote object '/vendor/bin/atcid': Permission denied
adb: error: failed to stat remote object '/vendor/bin/audiocmdservice_atci': Permission denied
```

The same follow-up recorded `Permission denied` for `ccci_fsd` and `ccci_rpcd`
and `No such file or directory` for `permission_check` and `ccci_mdinit` at
the tested paths. These results describe the shell's visibility and path
resolution only; they do not prove that the binaries are absent or patched.

## Evidence-indexed verdicts

| Finding | Status | Evidence |
|---|---|---|
| The official bulletin places CVE-2022-20053 and CVE-2022-20054 in a scope that includes MT8183 and Android 9 software families. | High-confidence external scope evidence | `P5I-WEB-001` |
| No active `ims`/`atcid` Binder service was present in the captured normal runtime. | Confirmed, snapshot-scoped | `P5I-IMS-001`, `P5I-IMS-002` |
| No IMS/ATCI package or process was found by the captured package/process filters. | Confirmed, enumeration-scoped | `P5I-IMS-001` |
| The ATCI init definitions are disabled/oneshot and require an explicit property condition to start `atcid-daemon-u`. | Confirmed, file-scoped | `P5I-IMS-002` |
| The normal shell could not pull or hash the vendor ATCI binaries. | Confirmed, shell-visibility-scoped | `P5I-IMS-003` |
| A normal ADB shell can directly exercise the bulletin's IMS/AT-command-injection surface on this snapshot. | Disproved for the observed normal runtime; not a vulnerability verdict | `P5I-IMS-001`, `P5I-IMS-003` |
| The vendor binaries are patched or unpatched for CVE-2022-20053/20054. | Unknown | No readable exact binary or matching exact OTA artifact |
| The ATCI property triggers or sockets should be enabled for further testing. | Risk-rejected | No property write, service start, socket use, or AT command was authorized |

## Decision and next safe step

The current evidence does not establish a new ADB-to-Root path. It does
narrow the route: normal shell enumeration finds no active IMS/ATCI endpoint,
while the potentially relevant vendor executables are protected from shell
read/pull. The strongest safe next step is offline acquisition and analysis of
an exact PS7330.4104N vendor/OTA artifact, if an authorized copy is available.
That analysis should inspect the ATCI implementation, HIDL interface, init
conditions, permissions, and patch level without running the binary.

The following actions were deliberately not performed and remain outside this
read-only result:

- writing `persist.vendor.service.atci.autostart` or
  `persist.vendor.service.atci.atm_mode`;
- starting `atcid-daemon-u` or `audio-daemon`;
- opening `adb_atci_socket` or `atci-audio`;
- sending an AT command or invoking the vendor ATCI Binder interface;
- pulling through a privilege boundary;
- trying an IMS/ATCI exploit or changing kernel/boot-chain state.

Any future action that starts a vendor daemon, sends an AT command, invokes a
potentially privileged Binder interface, or tests a vulnerability requires a
new exact risk report and authorization. The bounded CMDQ approval
`CMDQ-IOCTL-V3-COMPAT-T01` is consumed and does not authorize any of those
operations.
