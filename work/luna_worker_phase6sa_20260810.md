# Phase 6SA — Fire OS 7.3.3.1 install-package / OTA provenance audit

Date: 2026-08-10. Scope: host-only, read-only review of the preserved official
Fire HD 10 PS7331 / Fire OS 7.3.3.1 package, extracted OTA metadata, updater
binary/script, OTA APK source, post-install/OOBE chain, staging, and existing
bounded audit artifacts. Only this report and its CSV ledger were created.

## Deterministic result

The corpus establishes a privileged update capability and its principal gates,
but does not establish an ordinary-app or shell caller route. The bounded flow
is:

```text
official signed OTA
  -> metadata/device/product/version/PVT checks
  -> RecoverySystem verification boundary
  -> privileged SideloadMover staging
  -> UpdateSystem.install hand-off
  -> recovery update-binary / Edify registry
  -> fixed system/vendor extraction or block-image update
  -> fixed partition write sinks
  -> guarded system-server BOOT_AFTER_SYSTEM_OTA
  -> OOBE component/settings sinks
```

High-privilege sinks confirmed statically are OTA package extraction, block-image
updates, fixed partition writes, update-file staging/cleanup, OOBE component
enablement, and OOBE setup-state writes. The package script uses fixed members
and fixed named block targets. The updater registers 24 handlers, including
extraction, `run_program`, mount, staging, reboot, and block-image handlers.
Registration and selected native call edges are static evidence only; no
updater, recovery, OTA, package, broadcast, Binder, partition, or reboot action
was performed.

## Provenance and hash boundary

| Class | Artifact | SHA-256 / status |
|---|---|---|
| Official artifact | `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea`; preserved outer archive; 2,563,328,975 bytes |
| Official artifact | `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` | `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`; 27 ZIP members |
| Official extracted member | `META-INF/com/google/android/updater-script` | `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248` |
| Official extracted member | `META-INF/com/google/android/update-binary` | `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b` |
| Official extracted member | `ota.prop` / selected metadata | `f91b4c792339c605d81a2d6d5e819fee5d522a7514111daa1468717e07319ded` (metadata-inspection copy) |
| Official extracted member | `target.blocklist` | `f0a3f810d0dab5486a59cc22b9fc9390e9668760ab5a2b1229580a27fb05d83c` (metadata-inspection JSON copy) |
| Official extracted member | `target.system.devicepath` | `7ea3d84d793c6514f273496ace96a4bdc6af8c17135f63eb37f02232fae637b5` |
| Local research file | Phase 6MD/6MK/6MM/6NE/6MY/6NI/6Y summaries and source reconstructions | Not package provenance; hashes and paths are retained in the CSV |

The outer archive is a large bzip2 file. Available host enumeration did not
produce a verified member listing/EOF in bounded time; therefore outer-tail
coverage is **OPEN**, not negative. The extracted signed OTA and the 27-member
ZIP metadata audit are separately bounded official-artifact evidence.

## Caller and permission gates

* The saved Java OTA path is the privileged/controller lifecycle: sideload
  discovery -> metadata/sanity/device-state checks -> optional move ->
  `UpdateSystem.install`. `SideloadMetadataChecker` covers build/version,
  signature transition, product/device, and PVT-style policy gates.
* `SideloadVerifier` invokes the `RecoverySystemWrapper.verifyPackage` path
  where applicable. The cryptographic implementation is outside the saved
  Java source; this is a hand-off boundary, not a claim that Java source alone
  proves the verifier.
* `UpdateSystemWrapper` remaps the external-storage path, writes OTA screen
  state, and calls `UpdateSystem.install`; the reviewed caller is a privileged
  system-update path. No shell/ordinary-app caller was connected to it.
* The update binary is a recovery/updater identity. `main` registers install and
  block-image functions; dispatch is indirect after registration. The updater
  has capability to call extraction, `run_program`, mount, staging, reboot, and
  block-image handlers, but execution was not performed.
* The system-server sender is the guarded upgrade lifecycle (`onBootPhase(550)`
  plus `PMS.isUpgrade()`), sending protected `BOOT_AFTER_SYSTEM_OTA` with the
  receiver permission gate. Protected-broadcast declaration and lifecycle gate
  do not imply ordinary caller reachability.
* `BootAfterSystemOTAReceiver` is the OOBE consumer. Static sinks are enabling
  `OobeHomeActivity` and writing OOBE setup state. The bounded chain did not
  show a Fire Launcher preferred/HOME writer; exact delivered numeric user is
  unresolved.

## Path, temporary, and verification sensitivity

`SideloadMover` constructs a destination from a basename and `FileHelper` has
rename/copy/delete fallback behavior. The reviewed Java source has no visible
`canonicalPath`, `realpath`, or `NOFOLLOW` marker. This is **static sensitivity
only**: no crafted name, collision, symlink, traversal, temporary-path, or
cleanup test was run, and no vulnerability conclusion is made.

The native updater contains path markers (`symlink_realpath`, `readlinkat`, and
`readlink`) and selected open/chown/rename/write edges. One selected
`MakeFreeSpaceOnCache` readlink-family call site has no direct selected edge to
extraction, block-image, or partition write. Indirect dispatch, unselected CFG,
all callers, and complete return-value dataflow remain open. This does not
prove hardening or weakness.

## Status and next safe host-only step

Overall status: **BOUNDED_PRIVILEGED_CAPABILITY / NO_UNTRUSTED_CALLER_PROOF**.

Safe next step: complete offline outer-archive member enumeration to verified
EOF; hash/re-audit any newly supplied exact signed package; expand native
indirect/canonicalization dataflow; and, only after a naturally occurring
authorized OTA, collect read-only build, package/component, OOBE, HOME, and log
state. Do not execute or replay the update chain, alter package/partition
content, or test symlink/traversal/temp-path behavior.

See `luna_worker_phase6sa_20260810.csv` for the deterministic evidence ledger.
