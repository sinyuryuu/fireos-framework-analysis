# Level 3 report：GhostLock on KFTRWI／trona／PS7330

## Operation

Attempt a temporary local-root trigger for CVE-2026-43499 (GhostLock) against
the exact Amazon Fire HD 10 11th generation target.

## Purpose

Determine whether the source-level `rtmutex` overlap can be reached on the
installed signed kernel and, only if successful, collect a controlled diagnostic
result. This is not authorization to execute the trigger.

## Why current ADB-level methods are insufficient

The target is shell UID 2000 with SELinux enforcing. Current evidence does not
include a shell-readable signed `boot.img`, `vmlinux`, kernel symbol table,
compiled `task_struct` offset, KASLR slide, or a target-specific Android payload.
The public source only proves the vulnerable-looking source path and does not
prove the installed binary or exploit reliability.

## Exact commands proposed

`NOT_PROPOSED FOR EXECUTION.` No live exploit command, futex race, native binary,
`LD_PRELOAD`, ION/CMDQ operation, or post-exploitation command is supplied until
an exact target artifact and an independently reviewable payload are available.

The only approved next commands are host-only source comparison and read-only
metadata collection documented in `phase-5u-android-cve-applicability.md`.

## Files or images to be written

None. No APK, native binary, shared object, boot image, kernel image, loader,
preloader, LK image, DA, seccfg or partition image is approved.

## Target and compatibility

| Field | Value |
|---|---|
| Model | `KFTRWI` |
| Product | `trona` |
| SoC | MediaTek MT8183 |
| Build | `PS7330.4104N/0030099376128` |
| Kernel | Linux `4.4.146+`, AArch64 |
| Android | 9 / API 28 |
| Verified boot | `green` |
| Flash locked | `1` |
| SELinux | Enforcing |

## Expected outcome

No expected live outcome is accepted at this stage. A safe result would require a
non-triggering compatibility check that terminates normally and leaves the
device unchanged. A kernel panic, hang, spontaneous reboot, filesystem error,
or partial privilege change is a failure, not a successful experiment.

## Known failure modes

- immediate `EINVAL`/`ENOSYS` or policy denial;
- process crash without privilege change;
- kernel oops/panic and reboot;
- ADB loss;
- corrupted userspace state or filesystem after a failed kernel write;
- incomplete SELinux/credential change leaving an inconsistent process state;
- a false negative caused by wrong offsets or wrong signed-kernel assumption.

## Risk assessment

- Soft-brick risk: medium to high if a kernel panic or persistent userspace
  corruption occurs.
- Hard-brick risk: low for a pure in-memory trigger, but non-zero if a payload
  continues into block/boot writes; those stages are explicitly prohibited.
- Data-loss risk: medium to high because panic or corrupted writes can damage
  userdata even when no partition is intentionally targeted.
- Rollback/anti-rollback risk: not applicable to the rejected no-write plan;
  any boot-chain or image write would require a separate report.

## Recovery method

No guaranteed recovery method exists that is safe without the device remaining
ADB-accessible. A reboot may recover a pure in-memory crash, but it is not a
guarantee. If userdata or boot state is damaged, recovery may require factory
reset, signed firmware or hardware servicing; therefore the operation is
rejected.

## Required backup

Before any future consideration: exact signed firmware, userdata backup, device
identity, boot-chain metadata, and a verified recovery path. Those prerequisites
are not currently available in this workspace.

## Evidence supporting compatibility

- Amazon public Fire source `rtmutex.c` matches stable v4.4.146 old semantics;
- exact defconfig contains `CONFIG_FUTEX=y` and `CONFIG_RT_MUTEXES=y`;
- public Android ports demonstrate target-specific offset requirements.

These are source/config clues only and do not satisfy live-execution approval.

## Alternative lower-risk method

Continue host-only analysis, obtain an exact PS7330 signed artifact through an
authorized source, and compare its code/layout before considering any trigger.
Do not reuse another device's target header or binary.

## Decision

**因風險拒絕測試。** This report records the candidate and its blockers; it does
not authorize execution.
