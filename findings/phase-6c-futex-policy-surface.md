# Phase 6C futex opcode and policy surface audit

## Scope

This is a host-only audit of the preserved PS7331 7.3.3.1 source/config and a
previously generated native-ELF summary. It did not contact ADB, execute an
ELF, compile code, invoke futex, enable tracing, access kernel memory, or
generate a payload.

Artifact:

`artifacts/phase6c/phase6c-futex-policy-surface-20260804-01/`

The analyzer scanned 7,135 text files outside paths containing `kernel`, read
the captured IKCONFIG, and imported the existing 16-ELF native scan summary.

## Results

| Surface | Result | Classification |
|---|---:|---|
| `CONFIG_FUTEX` | `y` | Confirmed config scope |
| `CONFIG_RT_MUTEXES` | `y` | Confirmed config scope |
| `CONFIG_SECCOMP` | `y` | Confirmed config scope |
| `CONFIG_SECCOMP_FILTER` | `y` | Confirmed config scope |
| `CONFIG_USERFAULTFD` | not set | Confirmed config scope |
| Non-kernel source `FUTEX_WAIT` hits | 4 | Bounded source observation |
| Non-kernel source `FUTEX_WAKE` hits | 4 | Bounded source observation |
| Non-kernel `FUTEX_*_REQUEUE_PI` hits | 0 | Bounded source observation |
| Non-kernel named seccomp hits | 0 | Coverage limitation |
| Policy-named files outside kernel paths | 0 | Coverage limitation |
| Native named requeue-PI files | 0 | Bounded artifact observation |

The four WAIT and four WAKE hits are the ordinary GLib synchronization calls
already identified in Phase 5DE. No non-kernel source hit for
`FUTEX_WAIT_REQUEUE_PI` or `FUTEX_CMP_REQUEUE_PI` was found in this tree.

## Interpretation

### 已證實

1. The captured PS7331 config enables futex, rtmutex, seccomp and seccomp
   filters, while explicitly disabling userfaultfd.
2. The preserved non-kernel source contains ordinary WAIT/WAKE calls but no
   named requeue-PI opcode.
3. The previously scanned 16 native ELF files contain no named requeue-PI
   file.

### 高可信推論

The available source and native artifacts do not identify a direct Fire
userspace requeue-PI caller. This strengthens the distinction between
ordinary PI capability and the GhostLock proxy path.

### 待驗證

- Fire's installed app/zygote seccomp policy, because the source archive did not
  contain a recognizable policy profile outside kernel paths.
- Stripped, inline, numeric, indirect, generated, vendor-only or unpulled
  callers.
- Actual opcode allow/deny behavior in an untrusted app. Measuring that with a
  requeue-PI call would enter the stateful path under investigation and is not
  treated as a safe probe.

### 已排除／不支持

- `CONFIG_SECCOMP=y` as proof that requeue-PI is blocked or allowed.
- ordinary WAIT/WAKE source as a proxy waiter caller.
- ordinary PI lock/unlock success from Phase 6A as requeue-PI evidence.
- absence of a source policy filename as proof that no runtime policy exists.

### 因風險拒絕測試

No direct requeue-PI syscall, paired waiter, race, panic, kernel memory
operation, unknown ioctl or root payload was executed on the tablet.

## Reproduction

```sh
python3 tools/scripts/audit_phase6c_futex_policy_surface.py \
  --source-root firmware/extracted/PS7331-SOURCE-20250617 \
  --config artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config \
  --native-summary artifacts/phase6c/phase6c-userspace-native-scan-20260804-01/summary.json \
  --output artifacts/phase6c/phase6c-futex-policy-surface-YYYYMMDD-NN
```

The script refuses to overwrite an existing output directory and supports
`--dry-run`.
