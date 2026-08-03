# Phase 5E — `MTK-SU-CMDQ-T03` direct control-test result

## Classification

- Direct kernel-memory root-exploit invocation: **已依精確核准執行**
- Functional root obtained: **已排除（本次 payload／本次 build）**
- CVE-2020-0069 absence from the kernel: **待驗證**
- Device damage or persistent state change: **未觀察到**
- Further exploit variants: **因風險拒絕／需新的精確核准**

## Scope and identity

This was the one-shot operation approved as `MTK-SU-CMDQ-T03`. The device was
`G001LT0511550CFT`, model `KFTRWI`, product `trona`, build
`Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys`,
security patch `2024-02-01`, kernel `4.4.146+`, and SELinux `Enforcing`.

The payload came from the already archived APK
`artifacts/phase5/mtk-easy-su-audit-20260803/mtk-easy-su-v2.2.1-KoModed2.apk`,
asset `assets/mtk-su64`. The extracted AArch64 payload SHA-256 was:

```text
328632e853ff6427af9f35cb83a91d9e960f35d01188ee66d46ae9c7ce7c7827
```

No other binary, Magisk component, root manager, DA, bootloader command,
partition command, or post-exploitation command was used.

## Exact execution

The repeatable wrapper is:

```sh
tools/scripts/run_mtk_su_cmdq_t03.sh \
  --serial G001LT0511550CFT \
  --output adb/phase5/MTK-SU-CMDQ-T03
```

The wrapper saved a before snapshot, cleared the logcat buffer, created only
`/data/local/tmp/MTK-SU-CMDQ-T03`, pushed the verified payload, set its mode to
`0700`, and ran it once. Its only stdin was:

```text
id
getenforce
cat /proc/version
exit
```

## Observed result

| Observation | Evidence | Classification |
|---|---|---|
| Payload hash matched the archived expected value | `adb/phase5/MTK-SU-CMDQ-T03/host/extracted_payload_sha256.stdout.txt`, `sha256sums.txt` | 已證實 |
| Direct runner exit code was `1` | `adb/phase5/MTK-SU-CMDQ-T03/exec/exit_code.txt` | 已證實 |
| Direct payload stderr was `Failed critical init step 3`; stdout was empty | `adb/phase5/MTK-SU-CMDQ-T03/exec/mtk-su64.stderr.txt`, `mtk-su64.stdout.txt` | 已證實 |
| No UID-0 marker was produced by the exploit run | direct stdout/stderr above; `result.md` | 已證實（未取得 root） |
| Independent after-execution shell remained `uid=2000(shell)` and SELinux remained `Enforcing` | `after-exec/id.stdout.txt`, `after-exec/selinux.stdout.txt` | 已證實 |
| HOME resolver remained `com.amazon.firelauncher/.Launcher` | `before/home_resolver.stdout.txt`, `after-rollback/home_resolver.stdout.txt` | 已證實 |
| ADB remained in `device` state | `after-exec/adb_state.stdout.txt`, `after-rollback/adb_state.stdout.txt` | 已證實 |

The `after-exec/id` file is a separate normal `adb shell id` observation; it is
not being presented as output from the exploit's child shell. The exploit
itself terminated during critical initialization and emitted no diagnostic
stdout.

## Rollback and state comparison

The exact cleanup command was:

```text
adb -s G001LT0511550CFT shell rm -rf /data/local/tmp/MTK-SU-CMDQ-T03
```

It returned exit code `0`; a following `ls -ld` reported that the directory no
longer existed. No reboot was needed. The comparison summary is
`adb/phase5/MTK-SU-CMDQ-T03/comparison/summary.tsv`.

The following before/after-rollback artifacts were byte-identical:

- full `getprop`
- SELinux mode and shell context
- kernel version
- boot-state properties
- HOME resolver and candidate output
- preferred XML
- Fire Launcher path and package dump
- window dump
- CMDQ device-node listing

The activity dump had only normal elapsed-time counters changed; it retained
the same Fire Launcher home task and no crash/reboot signal. All raw files and
derived comparisons are covered by the evidence directory SHA-256 manifest.

## Interpretation

The result is **strong evidence** that this archived `mtk-su64` payload is not
a working root path for the exact PS7330.4104N build. The failure occurs in the
payload's own critical initialization before any root marker is observed. It
does **not** prove that the historical CMDQ vulnerability is absent, because
this test did not independently inspect the kernel driver or issue a separate
CMDQ ioctl diagnostic.

Following the repository's public-scope rule, the executable payload itself is
kept local-only. The public copy retains its expected SHA-256, static metadata,
command records, raw exploit stdout/stderr, state snapshots, rollback records,
and `sha256sums-public.txt`; the local `sha256sums.txt` also covers the omitted
payload.

The earlier APK wrapper failure and this direct one-shot failure are now
consistent, but they are still evidence about this payload and build—not a
general proof about every MTK exploit. Repeating this binary with alternate
flags, feeding additional commands, or trying another kernel-memory primitive
would be a new Level 3 operation requiring a separate exact approval.

## Host-only static follow-up

The direct error was subsequently mapped without another device operation. The
reproducible script is `tools/scripts/analyze_mtk_su64_init_failure.py`, and
the derived evidence is under
`artifacts/phase5/mtk-su64-static-init-analysis-20260803/`.

The wrapper calls `0x3300` at `0x17d8`; the `-3` branch at `0x34c8` is reached
when the helper at `0x2f80` returns zero after an `ioctl` using request
`0x40087807`. That request encoding matches the public MediaTek
`CMDQ_IOCTL_ALLOC_WRITE_ADDRESS` definition. The cleanup path uses request
`0x40087808`, the corresponding free operation. This is **Strong evidence**
that `Failed critical init step 3` means the archived payload's CMDQ
write-address/DMA allocation initialization failed. The exact driver errno and
the presence or absence of CVE-2020-0069 remain **Unknown**.
