# Phase 5AR：PS7331 compiled `rtmutex` review

日期：2026-08-04

## 結論先行

### 已證實

1. The PS7331 decompressed ARM64 `Image` contains kallsyms entries for
   `remove_waiter`, `rt_mutex_start_proxy_lock`, `rt_mutex_finish_proxy_lock`
   and `futex_requeue`.
2. In the reconstructed PS7331 code, `remove_waiter` reads the AArch64
   current-task source (`SP_EL0`) and then clears a field through that same
   current-task register. When mapped against the exact 4.4 source, this is the
   old `current->pi_blocked_on = NULL` behavior, not the fixed waiter-task
   behavior.
3. `rt_mutex_start_proxy_lock` contains a call to `remove_waiter` on its error
   path. This is the proxy-lock relationship required to identify the
   GhostLock root-cause pattern.

### 高可信推論

- PS7331's signed kernel binary does not contain the upstream semantic fix in
  the inspected `remove_waiter` path. This is stronger than the earlier
  build-date/config inference.
- The current PS7330 remains a high-confidence source/config candidate because
  its exact 7.3.3.0 source has the old pattern and its live config enables
  futex/rtmutex. It is not a signed-PS7330-binary confirmation: shell cannot
  read the installed boot block, and PS7330's exact compiled `remove_waiter`
  was not recovered in this pass.

### 待驗證

- Whether Android/SELinux policy and the exact PS7330 binary permit a reliable
  futex PI trigger from an ordinary app or shell process.
- Whether Amazon changed any other part of the PS7331/PS7330 futex or credential
  path independently of `remove_waiter`.
- Whether a successful privilege transition is possible. No exploit was run.

### 已排除

- The claim that PS7331's lack of a fix is supported only by its 2025 build date
  or by matching config. The compiled instruction pattern now provides direct
  code-level evidence for the inspected function.
- The claim that the archived source-notice page contains a 7.3.3.1 11th-gen
  source archive. It contains the exact 7.3.3.0 archive instead.

### 因風險拒絕測試

No futex race, native root payload, ION/CMDQ ioctl, kernel memory access,
bootloader command, image write or partition operation was performed.

This boundary is recorded as `P5AR-008`.

## Evidence method

The evidence identifiers for this review are `P5AR-001` through `P5AR-008` in
[`phase-5ar-evidence-index.md`](phase-5ar-evidence-index.md).

The PS7331 boot artifact was decompressed offline. The public
`vmlinux-to-elf` 1.3.6 parser reconstructed an analysis ELF from the embedded
kallsyms table. The project analyzer then invoked host `nm`/`objdump` and
emitted only address-sanitized symbol/pattern records:

| Pattern | Observation | Confidence |
|---|---|---|
| `remove_waiter` current-task source | `mrs <reg>, SP_EL0` | 已證實（`P5AR-003`） |
| `remove_waiter` current-task clear | `str xzr, [current_task_reg, <field-immediate>]` | 已證實（`P5AR-003`; binary pattern; source mapping） |
| proxy error path | `bl remove_waiter` in `rt_mutex_start_proxy_lock` | 已證實（`P5AR-004`） |

The upstream vulnerability description identifies the defect as using `current`
instead of `waiter->task` in this proxy rollback path:
[NVD CVE-2026-43499](https://nvd.nist.gov/vuln/detail/CVE-2026-43499).

## Version boundary

| Build | Evidence | Result |
|---|---|---|
| PS7330 installed | exact 7.3.3.0 source + live config (`P5AR-006`) | source-level old pattern; binary still pending (`P5AR-007`) |
| PS7331 OTA | reconstructed signed-kernel Image (`P5AR-001`–`P5AR-005`) | old pattern directly observed in compiled code |

The 7.3.3.0 source archive supplied by Amazon is the exact current-device
source family:
[Fire_HD10-7.3.3.0-20240730.tar.bz2](https://fireos-tablet-src.s3.amazonaws.com/7OU0BzzYt2YlM3MKwchLwgyUHM/Fire_HD10-7.3.3.0-20240730.tar.bz2).
The backup page supplied for review lists that archive for the 11th-generation
device, but not a 7.3.3.1 source archive (`P5AS-001`, `P5AS-002`).

## Safety boundary

This result is a static patch-status finding, not a root result. The analysis
does not disclose absolute kernel addresses, KASLR values, gadget locations or
an executable payload. It cannot establish exploit reliability, SELinux bypass,
credential overwrite or data safety.

## Reproduction

1. Obtain the authorized PS7331 `boot.img` and extract its kernel `Image` using
   the existing `inspect_android_boot_image.py` workflow.
2. Run the pinned host-only `vmlinux-to-elf` parser to reconstruct an ELF.
3. Run:

   ```sh
   python3 tools/scripts/analyze_phase5ar_ps7331_rtmutex_binary.py \
     --elf reconstructed-kernel.elf \
     --output artifacts/phase5/ps7331-rtmutex-static-review-YYYYMMDD-NN
   ```

No device command is part of this reproduction.
