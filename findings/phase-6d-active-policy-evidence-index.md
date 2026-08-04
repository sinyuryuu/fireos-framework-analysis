# Phase 6D active-policy read-only evidence index

## Evidence INIT-RO-01

- Source: PS7331 device read-only capture
- File: `adb/phase6d/PHASE6D-ACTIVE-POLICY-RO-20260804-03/getprop.stdout.txt`
- SHA-256: `eff54128ec883e000ebc1efc10b90806aa2526bd280557ecffa83051125ab4a2`
- Timestamp: `2026-08-04T14:55:08Z`
- Command: `adb -s G001LT0511550CFT shell getprop`
- Observed result: PS7331.4463N, Fire OS 7.3.3.1, KFTRWI, mt8183, API 28, green/locked
- Interpretation: captured device/build identity matches the PS7331 analysis target
- Confidence: **Confirmed**

## Evidence INIT-RO-02

- File: `adb/phase6d/PHASE6D-ACTIVE-POLICY-RO-20260804-03/policy_hashes.stdout.txt`
- SHA-256: `7803bbc21ba9b3862cd04ba8d5491973208d9e6b386a691018b433ccf014284d`
- Command: read-only `sha256sum`／`cat` over visible SELinux policy files
- Observed result: standard precompiled policy and standard/rootable CIL files are visible;
  `/sys/fs/selinux/policy` read denied
- Interpretation: file provenance is available, live policy identity is not shell-readable
- Confidence: **Confirmed**

## Evidence INIT-RO-03

- File: `adb/phase6d/PHASE6D-ACTIVE-POLICY-RO-20260804-03/selinux_mode.stdout.txt`
- Command: `adb -s G001LT0511550CFT shell getenforce`
- Observed result: `Enforcing`
- Interpretation: SELinux mode at capture time
- Confidence: **Confirmed (snapshot)**

## Evidence INIT-RO-04

- Files: `proc_cmdline.stderr.txt`, `kernel_visibility.stdout.txt`,
  `slab_visibility.stdout.txt`, `kallsyms_visibility.stdout.txt`
- Observed result: shell access denied or metadata-only for protected kernel interfaces
- Interpretation: runtime identity mismatch, SLUB residue, kernel memory effect and root
  cannot be inferred from these captures
- Confidence: **Confirmed (visibility boundary)**
