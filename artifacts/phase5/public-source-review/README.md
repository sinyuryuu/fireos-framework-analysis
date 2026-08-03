# Phase 5K public-source review provenance

This directory contains provenance metadata only. Third-party exploit source,
the full offset-calculator implementation, and the local upstream C snapshots
are intentionally not part of the public repository; the reports cite their
immutable upstream URLs and record local hashes where needed.

## Sources reviewed

| Source | Pinned revision | Purpose |
|---|---|---|
| [NebuSec/CyberMeowfia](https://github.com/NebuSec/CyberMeowfia) | `2c83bfb0c9230dc063e1bbfc3e06228d45dd938f` | GhostLock public source target/profile review; no device execution |
| [ctn-Qvo/auto_extract_offsets](https://github.com/ctn-Qvo/auto_extract_offsets) | `eabf28bb83e5101f93d17d830cbc8ea8a2f66223` | Offset-calculator compatibility review; not run for KFTRWI |
| [Linux stable v4.4.146 `rtmutex.c`](https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/tree/kernel/locking/rtmutex.c?h=v4.4.146) | tag `v4.4.146` | Upstream source comparison |
| [Linux stable v6.12.86 `rtmutex.c`](https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/tree/kernel/locking/rtmutex.c?h=v6.12.86) | tag `v6.12.86` | Fixed-source comparison |
| [Amazon Fire HD 10 7.3.3.0 source archive](https://fireos-tablet-src.s3.amazonaws.com/7OU0BzzYt2YlM3MKwchLwgyUHM/Fire_HD10-7.3.3.0-20240730.tar.bz2) | Last-Modified 2024-07-30 | Exact-marketing-version source/build context; not a signed boot artifact |

## Local snapshot hashes

The local review used these SHA-256 values:

```text
linux-stable-v4.4.146.c  c4ddac5fe820c7f07670bc332425be05b0df0400ae334a147b483f0ee9b07345
linux-stable-v6.1.175.c  c307ed54156d1f16e82387df7b214445dddf27be8a880f31575f698ca07d880a
linux-stable-v6.12.86.c aee270b96a626ec014809b93586be1de907e15fe7b1d04974b84033d0cdcfd27
```

The complete review and confidence classification are in
`findings/phase-5k-public-kernel-cve-offset-review.md`.
