# Phase 5 — Level 3 operation and risk approval report

## Current status

The explicitly approved Candidate A transition and Candidate B read-only
fastboot queries have now been executed. The device is currently enumerated in
fastboot as `G001LT0511550CFT`. No unlock, exploit, OEM, erase, format,
upload/download, set-active, remount, partition write, or flash operation has
been executed. The raw records and manifests are in:

`adb/phase5/PHASE5-BOOTLOADER-TRANSITION-20260803-01/`

`adb/phase5/PHASE5-FASTBOOT-GETVAR-20260803-01/`

A broad instruction to continue or accept a brick is not treated as approval
for a specific low-level operation. Each operation below needs its own explicit
approval after its risks and recovery limitations are understood.

## Candidate A — enter bootloader, read-only inspection only

**Operation:** `adb -s G001LT0511550CFT reboot bootloader`

**Purpose:** transition the tablet from Android to its bootloader so that
read-only fastboot identity/lock queries may be attempted.

**Why current ADB-level methods are insufficient:** Android shell cannot expose
the exact bootloader product, unlock state, secure flag, or fastboot variables.

**Exact commands proposed (not executed):**

```text
adb -s G001LT0511550CFT reboot bootloader
fastboot devices
fastboot -s <observed-fastboot-serial> getvar product
fastboot -s <observed-fastboot-serial> getvar unlocked
fastboot -s <observed-fastboot-serial> getvar secure
fastboot -s <observed-fastboot-serial> getvar all
```

The `<observed-fastboot-serial>` value must be obtained after the transition;
it must not be guessed. `getvar all` output may contain device identifiers and
must be stored as restricted research evidence if executed.

**Files/images written:** none.

**Target partitions:** none.

**Compatibility:** the current device is a locked MT8183 Amazon production
build. Fastboot availability is unknown; host fastboot currently sees no
device in Android mode.

**Expected outcome:** either a fastboot device appears and read-only variables
are returned, or the bootloader is not exposed / rejects the interface.

**Known failure modes:** no fastboot enumeration; device remains in bootloader;
ADB does not return until a normal reboot; cable/driver transport failure;
vendor bootloader requires a different USB mode.

**Soft-brick risk:** low but non-zero because the device may remain in a mode
where normal Android and ADB are unavailable until a hardware/power recovery.

**Hard-brick risk:** no partition write is proposed, so materially lower than a
write operation; vendor-specific bootloader behavior is not fully known.

**Data-loss risk:** no data deletion is proposed, but an unexpected bootloader
operation or forced recovery could make data temporarily inaccessible.

**Rollback/recovery:** wait for an identified normal reboot path; if the
bootloader has no documented exit, stop and do not issue unlock/flash commands.
The current workspace does not contain a device-specific recovery guarantee.

**Required backup:** preserve the existing ADB baseline, build identifiers, and
all current user data. No backup has been claimed sufficient for factory or
partition recovery.

**Approval required:** Candidate A has been approved and executed. Any future
transition must use a new test ID.

## Candidate B — read-only fastboot variables after an approved transition

**Operation:** the `fastboot getvar` commands above, with no `flash`, `erase`,
`format`, `unlock`, `oem`, `set_active`, or download/upload command.

**Purpose:** identify whether fastboot exposes a product/secure/lock state.

**Why current ADB-level methods are insufficient:** the Android properties are
not a substitute for bootloader-reported state.

**Files/images written:** none.

**Target partitions:** none.

**Risks:** identifier exposure and the possibility that a malformed/unsupported
query is rejected. No command should be sent if the device is not clearly
enumerated by fastboot.

**Stop conditions:** any prompt or output asking to unlock, authenticate,
download, erase, or write; any request to use an unknown OEM command; loss of
the device with no documented recovery; or any ambiguity about the serial.

**Approval required:** Candidate A must be approved first, and Candidate B must
be approved as a read-only follow-on. No write command is included in this
approval request.

## Candidate C — MTK BROM/Preloader protocol probe

**Operation:** connect to a MediaTek BROM/Preloader USB mode and issue a
read-only identification/protocol probe using a vetted, source-audited tool.

**Purpose:** learn the BROM hardware identifier and security/authentication
state that Android cannot expose.

**Why current ADB-level methods are insufficient:** `/proc/cmdline`,
`/proc/partitions`, preloader revision, and DA/auth state are protected or
unavailable from shell.

**Exact commands proposed:** none at this time. No tool, loader, payload, or
protocol transaction has been selected because the current device-specific
compatibility evidence is incomplete.

**Files/images written:** unknown; a generic tool may attempt a DA upload or
other handshake. That uncertainty is itself a rejection criterion.

**Target partitions:** potentially boot media/preloader-adjacent state; exact
target unknown.

**Known failure modes:** wrong USB mode; watchdog reset; secure-auth rejection;
invalid DA; protocol mismatch; accidental write path; loss of normal boot.

**Soft-brick risk:** material. **Hard-brick risk:** material if a wrong loader
or write path is used. **Data-loss risk:** material if userdata or metadata is
altered. **Rollback/anti-rollback risk:** unknown because RPMB is enabled and
the exact rollback policy is not exposed.

**Recovery method:** not established for the exact PS7330 build. The PS7331
preloader/LK files in the repository are version-mismatched and cannot be
declared recovery images.

**Approval status:** rejected for now. It requires a new exact compatibility
package, a vetted tool review, and a device-specific recovery plan before any
approval can be meaningful. The fastboot `locked hw` responses do not establish
that a BROM exploit or loader is compatible.

## Candidate D — unlock, exploit, DA upload, or partition write

This includes bootloader unlock, `fastboot flashing unlock`, MTK exploit
payloads, seccfg changes, DA upload that is not demonstrably read-only, and any
write to preloader, LK, boot, recovery, vbmeta, system, vendor, product,
super, userdata, NVRAM/NVDATA, or related partitions.

**Status:** `因風險拒絕測試`.

The current evidence lacks an exact PS7330 image set, verified recovery path,
compatible loader, and confirmed rollback procedure. No command, payload, or
image will be executed in this phase.

## Lower-risk alternatives

1. Continue offline analysis of the existing Fire OS VDEX/ODEX, FOS init XML,
   and PS7331 mismatch artifacts.
2. Acquire an official, exact PS7330 package and its published checksums, but
   do not flash it.
3. If the researcher explicitly wants bootloader metadata, approve Candidate A
   and B only, separately and read-only.

## Decision request

The next actionable approval, if desired, is:

> I explicitly approve Candidate A (`adb -s G001LT0511550CFT reboot bootloader`)
> followed only by Candidate B's read-only `fastboot getvar` queries, with no
> unlock, OEM, erase, format, upload, download, set-active, or flash command.

Without that exact approval, the project remains in the read-only state
documented by the Phase 5 baseline.
