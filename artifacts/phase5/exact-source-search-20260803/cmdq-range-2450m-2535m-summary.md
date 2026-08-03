# Exact Fire source CMDQ range — retained metadata

The compressed range itself remains local-only because it is a large source
capture. This compact record preserves the inputs needed to identify and
reproduce the source-scoped evidence.

- Source URL: https://fireos-tablet-src.s3.amazonaws.com/7OU0BzzYt2YlM3MKwchLwgyUHM/Fire_HD10-7.3.3.0-20240730.tar.bz2
- Requested byte range: `2450000000-2535000000`
- Requested/received bytes: `85000001 / 85000001`
- Range SHA-256: `d0ae31742da1fff49a5e5a26248b78b52d75b248acbf6939f93092d0ae3041b9`
- Scan timestamp: `2026-08-03T14:11:00Z`
- curl exit code: `0`
- Independently recovered bzip2 blocks: `580`
- Reconstructed tar-slice SHA-256: `3eface62137af812ac497ff440b5042cdb3e447b80d83a61fc02f355bf75a6bd`
- Extractor output: `artifacts/phase5/exact-source-search-20260803/cmdq-source-members-20260803-v5/`

The range was downloaded and decompressed on the host only. No ADB,
fastboot, BROM, DA, loader, payload, ioctl, or partition operation ran during
this source scan. The range is not a complete archive and is not evidence
that a particular source path was compiled into the installed kernel.

Reproduction command (host-only; output directory must be new):

```sh
tools/scripts/scan_phase5_exact_source_cmdq.sh \
  --url https://fireos-tablet-src.s3.amazonaws.com/7OU0BzzYt2YlM3MKwchLwgyUHM/Fire_HD10-7.3.3.0-20240730.tar.bz2 \
  --range-start 2450000000 \
  --range-end 2535000000 \
  --output artifacts/phase5/exact-source-search-20260803/cmdq-range-2450m-2535m
```
