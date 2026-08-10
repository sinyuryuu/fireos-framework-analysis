# Phase 6RG evidence index

日期：2026-08-10
公開基準：`1aa7b4ae0ac6733f6e1f5835679f74fadbb88769`

本輪的證據分為 host-only static、既有 runtime、以及一個新的 serial-bound
metadata-only snapshot。沒有執行提權、未知 Binder、driver ioctl 或破壞性操作。

## RG-IPC-01 — residual Amazon IPC ledger

- File: `work/luna_worker_phase6rg_ipc_residual_20260810.md/.csv`
- SHA-256: MD `b37a17e943184c9ad0fe248e42593cbca1b72b62620303defb2c86818f55df55`;
  CSV `6e5a079d28428be5bbd3705b7c4ac96350990a14e6c638eefb40a6b29ff950e9`
- Rows: 14
- Observation: registration → caller → sender/input → gate → identity → user → sink
  was mapped. Caller reachability gaps remain explicit `UNKNOWN`.
- Classification: 高可信推論，bounded static closure；不是漏洞證明。

## RG-SOURCE-01 — source/package/policy ledger

- File: `work/luna_worker_phase6rh_source_package_20260810.md/.csv`
- SHA-256: MD `f39857e0fb6c523ee8ec620f4df8c287776e54c736ceb7a7ea5608161ef9843c`;
  CSV `7eb2d75fae40b392b7cd45324e2156ec6c888dee000fac6f85ecb4e9bf6c4a0d`
- Rows: 12
- Observation: source registration/config/image/policy/client/sink are separated;
  `CONFIG_AMZN_DRV_TEST` omission and missing init source are recorded.
- Classification: 已證實 source/package provenance；client/reachability gaps remain UNKNOWN。

## RG-EXISTING-01 — prior-test reconciliation

- File: `work/luna_worker_phase6ri_existing_results_20260810.md/.csv`
- SHA-256: MD `88a8dd8a9aee8a252d792f9c6d70082cda919eb4f1c9f1244e182ae5073a7a55`;
  CSV `cae44932caefe8d206888f5309b2f3860e3524667129cf3056b23013b33d4936`
- Rows: 10
- Observation: prior package gate, KFT/profile, DPM/Profile, Accessibility, OOBE/OTA,
  service visibility, driver metadata and settings routes are de-duplicated.
- Classification: existing evidence only；no tests were repeated。

## RG-DEVICE-01 — exact-device read-only capture

- Directory: `adb/phase6rg/PHASE6RG-DEVICE-READONLY-20260810-01/`
- Script: `tools/scripts/capture_phase6qe_device_readonly.py`
- Metadata SHA-256: `9e111a842ff4ae9a20feae960e11cafe4a42240d69eb59d1ee7247d39c3ef3e3`
- Manifest SHA-256: `8b511989fa23e1cf5602beefbef2f24fff54ea18889377c1efdd15cba937d44d`
- Test ID: `PHASE6RG-DEVICE-READONLY-20260810-01`
- Serial: `G001LT0511550CFT`
- Observation: PS7331.4463N, Fire HOME priority 50, selected node metadata; no node
  opened, driver data read, Binder transaction, mutation, reboot, OTA/recovery, root or exploit。
- Classification: 已證實 read-only observation。

## RG-ASSET-01 — official/local provenance boundary

- File: `work/phase6rg_asset_scope_20260810.md`
- SHA-256: `0ad656767bf243f2049a3cd854d06e2ff198565a1441f3b080046765170fc2c2`
- Observation: official image/source scope is separated from locally copied
  `boot_unpacked/src/exploit_main.c` and `root.c`; local files were not executed。
- Classification: 已證實 provenance boundary。

## RG-MATRIX-01 — normalized matrix

- File: `output/tables/phase6rg-privilege-surface.csv`
- SHA-256: `32efda6b6dd751d612caae14d6e1bbb66d8d94f8c7adc5254d73d1d96ebbcb35`
- Manifest: `output/tables/phase6rg-privilege-surface.csv.manifest.json`
  SHA-256 `c781e58fed3e063a3240c5ca7e6ca1f1ca34f36764c75e30611472f1e4c25711`
- Rows: 38
- Classification: confirmed deterministic host-only transformation。

## RG-SAFETY-01 — operations rejected by risk

- No unknown/private Binder transaction or payload。
- No private/protected broadcast or OTA/recovery replay。
- No device-node open/read/write/ioctl。
- No Root/kernel exploit, remount, SELinux mutation, bootloader or partition write。
- No Fire Launcher disable/hide/suspend/uninstall/force-stop/clear or data deletion。

These are **因風險拒絕測試**，not runtime negative results。

## Confidence vocabulary

- **已證實 / Confirmed**：directly observed or hash-verified fact。
- **高可信推論 / Strong evidence**：multiple artifacts agree but an edge remains。
- **Probable**：bounded inference with an explicit gap。
- **Hypothesis**：requires future safe analysis/test。
- **Disproved**：contradicted within the stated build/test scope。
- **因風險拒絕測試 / Risk-rejected**：not executed because rollback/safety is insufficient。
