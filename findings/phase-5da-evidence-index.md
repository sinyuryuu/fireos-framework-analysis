# Phase 5DA evidence index

All evidence below is host-side and read-only. No device command was issued
by this phase.

## P5DA-E01

- Source: official source archive preserved locally
- File: `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2`
- SHA-256: `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea`
- Command: `shasum -a 256 ...`
- Observed: 2,563,328,975-byte archive; hash matches the retained provenance.
- Interpretation: input archive identity is fixed.
- Confidence: **Confirmed**

## P5DA-E02

- Source: outer archive extraction
- File: `firmware/extracted/PS7331-SOURCE-20250617/`
- Command: `tar -xjf ... -C firmware/extracted/PS7331-SOURCE-20250617`
- Observed: exit code 0; 23 files and 13 directories; `platform.tar` and
  `fireos.tar` are present.
- Interpretation: outer archive was fully extracted without overwriting the
  original.
- Confidence: **Confirmed**

## P5DA-E03

- Source: nested source archives
- Files: `firmware/extracted/PS7331-SOURCE-20250617/platform.tar` and
  `fireos.tar`
- SHA-256: `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd`
  and `bb7030296545dd45edcfec47d3e742043e7813852844f4b0fbbe8d223899b369`
- Command: `shasum -a 256 platform.tar fireos.tar`
- Observed: both primary archives extracted successfully to distinct
  directories.
- Interpretation: primary build source is available for offline indexing.
- Confidence: **Confirmed**

## P5DA-E04

- Source: Amazon build recipe
- Files: `build_kernel.sh:130-140` and `build_kernel_config.sh:9-18`
- Observed: kernel path `kernel/mediatek/mt8183/4.4`, defconfig
  `trona_defconfig`, architecture `arm64`, and trona image outputs.
- Interpretation: the supplied build recipe explicitly targets the trona
  MT8183 device family.
- Confidence: **Confirmed**

## P5DA-E05

- Source: device configuration and DT sources
- Files: `platform/kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig`
  and `arch/arm64/boot/dts/mediatek/trona_*.dts`
- SHA-256: defconfig
  `09ca8dfc3b3b5e139482e3dd9976dae79547077fb750a4cbc778814f85ecaaac`;
  per-file hashes are in the local focus index.
- Observed: MT8183, trona project, randomized base, and four trona DTBs are
  selected.
- Interpretation: board-level source matches the intended device target.
- Confidence: **Strong evidence**

## P5DA-E06

- Source: exact MT8183 futex/rtmutex source
- Files: `platform/kernel/mediatek/mt8183/4.4/kernel/futex.c` and
  `kernel/locking/rtmutex.c`
- SHA-256: `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96`
  and `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde`
- Observed: proxy requeue path and pre-fix cleanup markers at the previously
  recorded source lines.
- Interpretation: source corroborates the existing Phase 5 static analysis;
  it does not establish runtime exploitability.
- Confidence: **Confirmed** for source semantics; **Hypothesis** for runtime
  impact.

## P5DA-E07

- Source: reproducible index
- File: `artifacts/phase5/phase5da-ps7331-source-tree-index-20260804-01/metadata.json`
- SHA-256: `b6376c25c36b315d640704c7e69c34c59ac42299db956035eabf3343986f076a`
- Observed: 173,535 files indexed, 1,094 focus files hashed; ctags and clangd
  paths recorded; `source_executed=false`, `device_touched=false`.
- Interpretation: indexing is reproducible and bounded to offline analysis.
- Confidence: **Confirmed**

## P5DA-E08

- Source: supplied source layout
- Files: `apps/com.amazon.firelauncher/` and `fireos/`
- Observed: Launcher directory contains only a third-party dependency archive;
  no `frameworks/` tree or matching system-server/Settings/SystemUI source
  paths were found in the extracted FireOS tree.
- Interpretation: the official source package is incomplete for proprietary
  Launcher/framework implementation analysis; APK/JAR artifacts remain needed.
- Confidence: **Confirmed**

## P5DA-E09

- Source: command log and script metadata
- Files: `tools/scripts/index_phase5da_source_tree.py` and local index metadata
- Observed: no ADB, fastboot, compiler, selftest, source execution, payload,
  or partition command was run.
- Interpretation: this phase changed only local extraction/index outputs.
- Confidence: **Confirmed**
