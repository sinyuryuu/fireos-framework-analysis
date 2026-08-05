# Phase 6BI evidence index

本索引只列主機端靜態證據；沒有裝置 mutation、沒有 updater execution、沒有
recovery 或 partition write。時間以本輪分析主機時間（2026-08-05，Asia/Taipei）
記錄；精確產出時間亦保存在各 artifact `summary.json`。

## PH6BI-OTA-001

- Source: PS7331 extracted OTA
- File: `firmware/extracted/PS7331/META-INF/com/google/android/update-binary`
- SHA-256: `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b`
- Command: `shasum -a 256 <file>`
- Observed result: ELF64 AArch64 `update-binary` input preserved.
- Interpretation: 版本／檔案 provenance 已固定；不是 runtime evidence。
- Confidence: **Confirmed**
- Related hypothesis: OTA updater 是否含高權限 post-install write surface。

## PH6BI-OTA-002

- Source: `.gnu_debugdata` extractor
- File: `artifacts/phase6bi/update-binary-debugdata-20260805-01/{gnu_debugdata.elf,symbols.csv}`
- SHA-256: `gnu_debugdata.elf=a1918c31c48e4ee3a6f06d0bf85a87493d6f28b7b671bb019d8957c06073988d`; `symbols.csv=73990eeea6eaf9d5930f531132e37da04b201ba30e462a939f5fde7a6af3ddb9`
- Command: `python3 tools/scripts/audit_phase6p_gnu_debugdata.py ...`
- Observed result: mini-ELF 161008 bytes；symbols 2886；含 updater I/O／extraction symbol。
- Interpretation: 可以以符號地址導引完整 `.text` 反組譯。
- Confidence: **Confirmed**
- Related hypothesis: 函式級 CFG 可重現。

## PH6BI-OTA-003

- Source: symbol-guided direct-call audit
- File: `artifacts/phase6bi/write-boundary-20260805-01/{focus-functions.csv,direct-call-edges.csv,summary.json}`
- SHA-256: `focus-functions.csv=660e45075bda495dabf24f959fb89aa8e3521518eef3f2a6d750b2a25a9ddb7e`; `direct-call-edges.csv=f328389d5f5bdfef7c30259234d453cf8c24dadec7630bee668d1232e4ab7c0d`; `summary.json=4705917fbeb41b49fbfd9a7386f9816eb0b2ad49a6213739a08b090b50b8a75c`
- Command: `python3 tools/scripts/audit_phase6bi_ota_write_boundary.py ...`
- Observed result: 20 focus functions、851 direct BL call-sites、246 unique edges。
- Interpretation: direct call graph evidence；indirect dispatch 仍未解析。
- Confidence: **Confirmed**
- Related hypothesis: updater 能力是否為真實 code path 而非單純字串。

## PH6BI-OTA-004

- Source: AArch64 text disassembly
- File: `artifacts/phase6p/callback-ota-audit-20260805-02/native/text-disassembly.txt`
- SHA-256: `2cbce4c1329808d985058ebea9db35bd60ed0fa8cebcdeff2a960b1076e2ccbf`
- Location: `PackageExtractFileFn 0x401fb8–0x402788`; call-sites `0x402108`, `0x4021b4`, `0x40238c`, `0x40243c`, `0x40245c`。
- Observed result: `FindEntry → ota_open → ExtractEntryToFile → ota_fsync → ota_close` direct chain。
- Interpretation: package extraction has a concrete output-file write path。
- Confidence: **Confirmed**
- Related hypothesis: OTA package extraction 是否能改寫目標檔案。

## PH6BI-OTA-005

- Source: AArch64 text disassembly plus symbol table
- File: `artifacts/phase6s/ota-cfg-focus-20260805-01/focus-disassembly.txt`
- Location: `PackageExtractFileFn: 0x4021ac–0x4021b4`; `ota_open: 0x426338–0x426528`, `open: 0x4cc170`。
- Observed result: caller loads `w1=0x241`, `w2=0x180`; `ota_open` directly calls libc `open`。
- Interpretation: direct path-open flags are visible；未見本函式範圍內的 `O_NOFOLLOW`／`realpath` gate。
- Confidence: **Confirmed**（對 instruction）；**Hypothesis**（對整個 updater 的 path safety）。
- Related hypothesis: path canonicalization／symlink protection。

## PH6BI-OTA-006

- Source: AArch64 text disassembly plus direct-call output
- File: `artifacts/phase6bi/write-boundary-20260805-01/write-surface.csv`
- Location: `WriteToPartition 0x413c40–0x4142f0`; `MakeFreeSpaceOnCache 0x417778–0x417fc4`。
- Observed result: raw-write chain uses `ota_open`／`ota_write`／`ota_fsync`；cache helper separately calls `__readlink_chk` at `0x417bf0`。
- Interpretation: readlink path與 raw partition write path目前是分離的 direct-call branches。
- Confidence: **Confirmed**
- Related hypothesis: readlink 是否替 package extraction 做 canonicalization。

## PH6BI-OTA-007

- Source: focus call graph
- File: `artifacts/phase6bi/write-boundary-20260805-01/control-flow.mmd`
- SHA-256: `ac77e453db12b71669472e3cd416d2be6a9d842e1821755f45d9a457641ce33b`
- Observed result: `PackageExtractFileFn`／`ota_open` 沒有 direct edge 到 `readlink`；`MakeFreeSpaceOnCache` 才有 `__readlink_chk` edge。
- Interpretation: 不能把 readlink marker 擴張成 extraction canonicalization 結論。
- Confidence: **Strong evidence**
- Related hypothesis: updater path safety。

## PH6BI-OTA-008

- Source: audit script summary
- File: `artifacts/phase6bi/write-boundary-20260805-01/summary.json`
- Observed result: `device_contacted=false`, `updater_executed=false`, `recovery_executed=false`, `partition_written=false`。
- Interpretation: 本階段沒有真機或高風險操作。
- Confidence: **Confirmed**
- Related hypothesis: 所有結果均為 host-only 靜態證據。
