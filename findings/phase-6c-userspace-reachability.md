# Phase 6C userspace requeue-PI reachability audit

## Scope

This is a host-only scan of preserved PS7331 Fire/Amazon native ELF artifacts.
It uses `file`, `strings`, and dynamic-symbol metadata only; it does not execute
an ELF, disassemble an exploit, generate futex arguments, contact the tablet,
or access kernel memory.

Inputs:

- `artifacts/phase5/phase5cq-fire-native-20260804-01/`
- `artifacts/phase5/phase5cr-fire-native-20260804-02/`
- `artifacts/phase5/phase5cs-fire-amazon-native-20260804-01/`

## Results — Confirmed, bounded artifact scope

| Result | Count |
|---|---:|
| ELF files scanned | 16 |
| Named `REQUEUE_PI` marker | 0 |
| Ordinary futex/PI-helper markers only | 5 |
| Generic `syscall` boundary only | 1 |
| No named futex marker | 10 |

The one generic syscall boundary is `libcutils.so`; it does not identify an
operation. The ordinary markers include PI-lock helpers and ART's diagnostic
string `futex cmp requeue failed for`. That diagnostic is not evidence of the
`FUTEX_CMP_REQUEUE_PI` opcode or of a proxy waiter.

## Combined interpretation

### 已證實

- The exact PS7331 kernel source has the requeue-PI dispatch and proxy path.
- The preserved native scan has no named requeue-PI caller in these 16 ELF
  inputs.
- Phase 6A ordinary private PI lock/unlock succeeded from an ordinary app, but
  that operation is not requeue-PI.

### 高可信推論

The currently preserved Fire libc/ART/Amazon native surfaces do not provide a
direct, named userspace entry into the GhostLock proxy path. This makes a
stock trigger less established, but does not rule out stripped, inline,
numeric, indirect, unpulled, or generated callers.

### 待驗證

- Complete installed-image native coverage for every process that can issue a
  generic syscall.
- Whether seccomp or another policy allows the requeue-PI opcodes.
- Any indirect caller and actual stock runtime execution.

### 已排除／不支持

The following are not sufficient GhostLock caller evidence:

- ordinary `FUTEX_WAIT`/`FUTEX_WAKE` helpers;
- `FUTEX_LOCK_PI_PRIVATE`/`UNLOCK_PI_PRIVATE` helpers;
- ART's ordinary compare-requeue diagnostic;
- a generic `syscall` import;
- kernel selftest wrappers or documentation examples.

### 因風險拒絕測試

No device-side requeue-PI call, paired waiter, race, panic, memory operation,
or root payload was run. A single-thread label does not make the operation
read-only because the exact kernel dispatch can prepare PI state and enter the
proxy cleanup path.

## Reproduction

```sh
python3 tools/scripts/audit_phase5dd_native_futex_surface.py \
  --input-root artifacts/phase5/phase5cq-fire-native-20260804-01 \
  --input-root artifacts/phase5/phase5cr-fire-native-20260804-02 \
  --input-root artifacts/phase5/phase5cs-fire-amazon-native-20260804-01 \
  --output artifacts/phase6c/phase6c-userspace-native-scan-YYYYMMDD-NN
```

The output directory must be new. The generated manifest was verified for this
run at `artifacts/phase6c/phase6c-userspace-native-scan-20260804-01/`.
