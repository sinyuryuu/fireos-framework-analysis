# Phase 6C runtime boundary: PS7331 read-only snapshot

## Scope

Capture ID: `PHASE6C-BOUNDARY-RO-20260804-05`
Device serial: `G001LT0511550CFT`
Capture window: `2026-08-04T13:03:53Z`–`2026-08-04T13:03:55Z`

This was a bounded, read-only ADB capture. It did not clear logcat, start an
activity, send a key event, change settings or package state, enable tracing,
open a device node, read kernel memory, reboot, or invoke any futex operation.
The raw command output is retained under
`adb/phase6c/PHASE6C-BOUNDARY-RO-20260804-05/` and is self-verifiable with its
`sha256sums.txt`.

## Observed facts

### Device and security boundary — Confirmed

- Build fingerprint: `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`.
- Model/device: `KFTRWI` / `trona`; Android release 9; security patch
  `2024-08-01`.
- Kernel: Linux `4.4.146+`, AArch64, build timestamp `Sat May 3 01:24:02 UTC
  2025`.
- `ro.boot.verifiedbootstate=green` and `ro.debuggable=0`.
- ADB shell is UID 2000 under SELinux `Enforcing`.

Evidence: `P6C-RO-001`, `P6C-RO-002`, `P6C-RO-003`, `P6C-RO-004`.

### Kernel observation visibility — Confirmed

The shell could not read `/proc/kallsyms` or
`/proc/sys/kernel/randomize_va_space`; `/proc/slabinfo` was not present in the
shell-visible namespace. These are permission/visibility results, not proof
that KASLR or a particular allocator state is absent.

Evidence: `P6C-RO-005`, `P6C-RO-006`, `P6C-RO-007`.

### Current HOME context — Confirmed

At capture time:

- `settings get secure user_setup_complete` returned `0`.
- `settings get global device_provisioned` returned `1`.
- `cmd package resolve-activity --brief -a MAIN -c HOME` returned
  `com.amazon.kindle.otter.oobe/.OobeHomeActivity` with priority `100`.
- The candidate dump still contained Fire Launcher at priority `50`,
  Microsoft Launcher at effective priority `0`, and other test/candidate
  activities.
- `dumpsys activity activities` reported the Microsoft Launcher as the resumed
  activity while a Fire Launcher task remained present.
- `dumpsys window windows` reported the Microsoft Launcher as `mCurrentFocus`
  and also retained Fire Launcher and test-launcher windows.

Evidence: `P6C-RO-008`, `P6C-RO-009`, `P6C-RO-010`, `P6C-RO-011`.

This is not a clean post-rollback HOME baseline: `user_setup_complete=0` and
research/test launcher packages are still visible. The resolver result and
current foreground therefore must not be used as a fresh ordinary-Home-key
comparison without first establishing a separate, explicitly approved test
state.

### Fire Launcher package — Confirmed

`pm path com.amazon.firelauncher` returned:

`/system/priv-app/com.amazon.firelauncher/com.amazon.firelauncher.apk`

The package dump identifies it as a privileged system package, with UID
`10120`, version name `1.3.239105.0_89024510`, and the launcher activity
`com.amazon.firelauncher/.Launcher`. The package was not disabled or modified
by this capture.

Evidence: `P6C-RO-012`.

## GhostLock runtime conclusion

No `FUTEX_CMP_REQUEUE_PI`, `FUTEX_WAIT_REQUEUE_PI`, proxy waiter, race,
cleanup residue, memory effect, kernel panic, or privilege transition was
attempted or observed in this phase. The Phase 6A result remains ordinary
private PI lock/unlock capability only; it is not evidence that the requeue-PI
proxy path is reachable in a useful state.

Status: **待驗證** for runtime identity mismatch and any consequence.
Status: **無法取得證據** for a stock-device `waiter->task != current` event,
because no trigger or kernel instrumentation was run.
Status: **因風險拒絕測試** for a real-device requeue-PI race, heap spray, ION or
pipe placement, kernel panic, memory read/write, or root payload.

The host-only source/model evidence remains the appropriate evidence for the
current step. In particular, `findings/phase-6-step4-source-safety-analysis.md`
documents why a single requeue-PI call is not a harmless syscall probe, and
`findings/phase-6b-host-layout-model.md` records the static layout assumptions
without claiming runtime exploitability.

## Safe next step

1. Keep all runtime-trigger work in a separate `LAB_ONLY` environment.
2. Treat the current OOBE/setup state as a context change, not as a new HOME
   resolver finding.
3. Do not write `user_setup_complete`, disable packages, or launch a HOME
   activity merely to normalize the snapshot; those are separate state-mutating
   experiments requiring their own backup and rollback record.
4. If a KASAN/debug-symbol lab is pursued, first satisfy the Phase 6C readiness
   gates. The current readiness audit is `NOT_READY` because QEMU AArch64 is
   unavailable and the stock config lacks both KASAN and debug info.

## Reproduction

```sh
tools/scripts/capture_phase6c_runtime_boundary.sh \
  --serial G001LT0511550CFT \
  --output adb/phase6c/PHASE6C-BOUNDARY-RO-20260804-05

(cd adb/phase6c/PHASE6C-BOUNDARY-RO-20260804-05 && \
  shasum -a 256 -c sha256sums.txt)
```

The output directory must be new; the script refuses to overwrite it.
