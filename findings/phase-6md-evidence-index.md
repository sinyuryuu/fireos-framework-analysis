# Phase 6MD evidence index

本索引只使用主機端、已保存且 hash-pinned 的 PS7331 OTA artifacts。沒有執行
updater、recovery、OTA、Binder 或裝置變更。

| Evidence ID | Source | Observation | Confidence |
|---|---|---|---|
| 6MD-OTA-001 | `firmware/extracted/PS7331/META-INF/com/google/android/update-binary` SHA `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b` | PS7331 AArch64 static updater input | Confirmed |
| 6MD-OTA-002 | `firmware/extracted/PS7331/META-INF/com/google/android/updater-script:6-23` SHA `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248` | `block_image_update`、`package_extract_file` 明確指向 system/vendor/boot chain 與 firmware partitions | Confirmed |
| 6MD-EDGE-001 | `artifacts/phase6md-native-updater-path-audit-20260810-02/path-write-call-edges.csv` | `PackageExtractFileFn` direct-calls `ota_open`, `ExtractToMemory`, `ExtractEntryToFile`; `ota_open` direct-calls open wrapper | Confirmed |
| 6MD-EDGE-002 | 同上；`PerformBlockImageUpdate` rows at `0x409340`, `0x409bdc`, `0x409d48`, `0x40a2e0`, `0x40a344`, `0x40a378`, `0x40a3a8` | block-image path reaches open/chown/rename sinks | Confirmed |
| 6MD-EDGE-003 | 同上；`WriteToPartition` rows at `0x413dcc`–`0x414164`; `ota_write` at `0x426e44` | partition write handler reaches `ota_open` and native write | Confirmed |
| 6MD-PATH-001 | `artifacts/phase6md-native-updater-path-audit-20260810-02/path-marker-strings.csv` | `symlink_realpath`/`readlink`/`readlinkat` markers exist; selected direct-BL graph has zero direct path-canonicalization edges | Strong evidence; bounded |
| 6MD-SAFETY-001 | `artifacts/phase6md-native-updater-path-audit-20260810-02/summary.json` | `device_contacted=false`, `updater_executed=false`, `partition_written=false` | Confirmed |
| 6MD-BOUNDARY-001 | `findings/phase-6md-native-updater-path-audit.md` | No Fire Launcher/HOME sink or low-privilege entry established by this OTA analysis | Strong evidence; bounded |

## Limitations

Direct-BL extraction does not resolve indirect calls, function pointers, data-driven
dispatch or all error paths. String presence is not proof of invocation. The index
therefore does not claim a path-traversal defect, arbitrary file overwrite, root, or
any runtime exploitability.
