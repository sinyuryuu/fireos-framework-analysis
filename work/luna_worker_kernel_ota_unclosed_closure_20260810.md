# PS7331 kernel / OTA / init unclosed-candidate closure

Date: 2026-08-10. Host-only static review of preserved source, disassembly, manifests, and artifacts. No ADB, device access, Binder/service call, ioctl, root/exploit testing, OTA/recovery/flash, or state change was performed.

## Executive disposition

The remaining candidates separate static capability from reachable privilege transition. Public-looking kernel nodes/ioctls and the native updater expose capability surfaces, but the corpus does not prove an untrusted or shell caller can cross the relevant SELinux/permission/recovery boundary into a privileged sink. OOBE and init are trusted lifecycle/policy machinery, not public selectors. No safe dynamic test is justified for dangerous routes; only host-side provenance analysis or read-only observation of a naturally occurring authorized lifecycle event remains appropriate.

## Candidate closure

### K-1 — CMDQ / ION / GED and related public driver surfaces

Static capability: confirmed. Anchors: `drivers/misc/mediatek/cmdq/v3/cmdq_driver.c:660-743,816-824,848-865,894-898`, `drivers/staging/android/ion/ion.c:1478-1617,1657-1658`, and `drivers/misc/mediatek/gpu/ged/src/ged_main.c:271-346,407-416`. The scan found 0 direct Framework/HOME/PMS literals in 1,671 selected files; summary SHA-256 `129bd9e929cad163652e6140a0c84248bcf16ef951ad6c2760ec0bf3e2da9669`; source-hash table SHA-256 `e08cce97c1779ff27be2c6f92687fa24a8a3ac48756c99c65b2fdb2c80d4da91`.

No untrusted/shell caller is proven for CMDQ, ION, M4U, CCU, GZ, SMI, input, power, USB, or char write paths. Existing GED evidence proves only a query/telemetry read path. Unix node mode, init registration, production SELinux label/domain, Kconfig, and downstream behavior remain separate gates. Exact sink is driver fops/user-copy into hardware, telemetry, DMA, or secure-world candidate state; no direct AMS/ATMS/PMS/HOME/Fire Launcher sink. Static capability only; no reachable low-privilege transition. Dynamic test: **not justified** for write/reset, DMA/readback, debugfs/sysfs/proc writes, or malformed ioctl.

### K-2 — Amazon staging driver nodes

Static capability: confirmed under `drivers/staging/amazon/` (not `drivers/amazon/`), including IDME, logger, sign-of-life, and lifecycle paths. Canonical source-manifest SHA-256 is `ada254be9c56572282704924eea66e2852889ec73c0a65be4558f36f77d8250a`.

No untrusted/shell write caller is proven. Existing review says IDME strips write bits and logger/lifecycle surfaces are read/poll/open/release or read-only; source mode is not runtime SELinux/node proof. Exact sink is telemetry/device state, not a package/component/HOME/system-server writer. Privilege transition not proven. Dynamic test: **not justified**; no node open/write, ioctl, sysfs/proc write, module load, or secure-world operation.

### O-1 — Native updater, block-image, extraction, and partition I/O

Static capability: confirmed. `RegisterBlockImageFunction` registers five handlers at `0x40d0fc, 0x40d144, 0x40d190, 0x40d1d8, 0x40d224`; update cell `0x5af678` resolves to `BlockImageUpdateFn 0x40b8b8`. Extraction edges are at `0x4021b4, 0x4022cc, 0x40238c`; block-image open/rename edges at `0x409340, 0x40a3a8, 0x40a2e0, 0x409d48, 0x40a378`; partition open/write edges at `0x413dcc, 0x413e98, 0x413ecc, 0x414164, 0x413e3c, 0x413edc, 0x413f08`, and libc `write` at `0x426e44`.

Inputs: `update-binary` SHA-256 `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b`; `updater-script` SHA-256 `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248`. Script lines 6, 10, 13, 15-23 name protected `/dev/block/platform/bootdevice/by-name/` targets. Selected call-edge SHA-256 `2e5074f461127445bfcb5633840aff16e2284545245292b5999581d672e10d65`.

No shell or ordinary-app caller to recovery/updater is proven. Java validation (`OSUpdateValidator.java:42-48,72-77`, `RecoverySystemWrapper.java:21-22`, `SideloadVerifier.java:55-58`) is a separate provenance boundary from `UpdateSystem.install` and native recovery. Exact sink is protected partition open/write and extraction/rename. High-privilege capability only; no reachable transition. Dynamic test: **rejected**—do not execute the ELF/script, enter recovery, sideload, fastboot, or write a partition.

### O-2 — Canonicalization / cache helper

`MakeFreeSpaceOnCache + 0x478` (`0x417bf0`) directly calls `__readlink_chk` (`0x4ce4e8`), with nearby `stat64`, `strncmp`, `unlink`, and cache bookkeeping. The selected graph has no direct canonicalization-to-write edge, but `CacheSizeCheck` is not fully selected. Summary SHA-256: `a0186bb7d053d23f002dc663b9ee3f312255410b35ed997a74e864fc8f9229a6`.

No untrusted/shell caller or attacker-controlled path is proven. Exact sink is the readlink check and cache file management; no proven connection to `WriteToPartition`. No transition established. Dynamic test: **rejected** for symlink/traversal or crafted OTA; only host-side tracing of `CacheSizeCheck`, all callers, and return/data flow is justified.

### O-3 — Postinstall / outer OTA archive

Bounded negative: top-level and 18 known nested archives show no `postinstall`, `run_program`, `update-binary`, recovery, system/vendor writer, or HOME/PMS helper member. The outer `Fire_HD10-7.3.3.1-20250617.tar.bz2` listing did not reach EOF, so an unlisted tail cannot be excluded. No untrusted/shell caller is proven; any execution would be signed recovery/system context. No sink observed in the bounded listing. Dynamic test: **rejected** extraction/execution of unknown members or crafted OTA; EOF-complete host listing only. Finding SHA-256: `1de3ecc97b520f45981a906f09800d646c4f60d02fb58bcdf3a900a282526d23`.

### O-4 — BootAfterSystemOTA / OOBE

Trusted lifecycle flow confirmed. `fosservices/disassembly.log:96087-96126` shows `AmazonPackageManagerService.onBootPhase(550)` plus `isUpgrade()` before send; `BootAfterSystemOTAReceiver.java:27-80` reaches `PackageHelper.java:11-22` and `OOBEActivationHelper.java:53-56`. Exact sinks: `setComponentEnabledSetting(state=1)` for OobeHomeActivity and `Settings.Secure.putInt` via `SettingsDBUtils.java:51-64`. Context/user anchors: `boot-framework-disassembly.log:435176-435236,449212-449298,452691-452721`.

No untrusted/shell caller is proven. Protected-broadcast membership is not sender authentication; sender is system_server, and exact post-OTA user remains unresolved. OOBE has a priority-100 HOME candidate, but reviewed code has no Fire Launcher/preferred-HOME writer. This is trusted lifecycle mutation, not a low-privilege transition. Dynamic test: **rejected**—no manual broadcast/replay or OOBE/component/settings mutation. Only host-side user provenance or natural authorized OTA observation is justified. Artifact SHA-256: `e9c0aa2d1a35371a96a7564a33696f14b3b9ef7cb0734fbe5267d94cdc70f6d5` (bootafter scope summary); `c219719bbaca7c772a76721d55ad1a0ed0592771f90a6490c7b54403a6194708` (context/user summary).

### I-1 — /init policy loader and permissive parser

Code-level references are confirmed in `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/root/init`: rootable/standard builders at `0x41ad80-0x41ae54` and `0x41aea8-0x41af44`, common-helper calls at `0x41ae5c` (`w5=1`) and `0x41af80` (`w5=0`), branch `0x41be48`, and `androidboot.selinux=permissive` candidate `0x41bd60`. Init SHA-256 `e72ed4e90d73b88be341985ebd624725b67d67967d04157317456233e15f31fd`; policy audit SHA-256 `37d77ceed1004aa76e3804fd365c286eade2abca112c89e0e5f7898e51e5235`.

No shell/untrusted caller is proven; /init is boot-chain authority. Exact sink is policy path selection/helper state and a zero store in the stripped parser; field meaning and selected variant remain unresolved. No root/permissive transition established. Dynamic test: **rejected**—no boot-property mutation, alternate policy injection, remount, AVB bypass, reboot, or boot-image modification. Host-only CFG/data-flow and policy-hash provenance only.

### S-1 — OTA/system-service entry points

`OtaService` is exported with `com.amazon.dcp.ota.permission.CONTROLLER`; package protection is `signature|privileged`, and `IOTAControlService` has install/sideload-like methods. `AmazonPackageManagerService.onBootPhase` is an internal lifecycle entry, not a public caller API. No shell/ordinary-app caller or Binder transaction is proven. Boundaries are service permission, system_server identity, protected broadcast checks, and recovery handoff. Exact sinks are OTA install/recovery transition or O-4 OOBE sinks, not a direct HOME selector. Capability behind privileged boundaries only; no reachable transition. Dynamic test: **rejected**—no Binder lookup/replay, guessed transaction, OTA install, or service mutation. Evidence SHA-256: Phase 6R `4c2edb6e43b39bfbe615fd8779f49026f3694cad884ebab50103f0cfbd701fbc`; Phase 6Q `270dc8c36671e5fbc264361b99b0b0b2932edeb1172a895546c35ac4685624a8`; Phase 6KT `484273958f44898c6b94a208da4e144936df09a191e03efe6316c18d167fe732`.

## Final safety conclusion

No candidate closes an untrusted-caller-to-privileged-sink chain. Dangerous routes remain analysis-only or rejected: ioctl writes, DMA/readback, updater or recovery execution, crafted/symlink OTA, protected-broadcast replay, Binder transactions, init-property/policy mutation, partition writes, and reboot.
