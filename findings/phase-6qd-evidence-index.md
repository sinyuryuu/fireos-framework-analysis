# Phase 6QD evidence index

日期：2026-08-10
公開基準：`0511bc0ab7a769a91ab5c1f506a3a2c3237593ae`

本索引保留三份 worker 原始 evidence、Phase 6QD read-only device capture、
以及主 Agent 的 source-level cross-check。`UNKNOWN` 表示證據鏈仍缺 caller、
permission、user scope、final image mapping 或 data-flow；不等於漏洞。

## Worker inventories

### QD-IPC-01

- Files: `work/luna_worker_ipc_unclosed_sink_inventory_20260810.md/.csv`
- SHA-256: MD `1d2bab0d6526850669a4d6858be5c7eb73d8c521d51eaed6d451438135b9180c`；CSV `c14abe7dfec800f1108be6492064f7e0474d43ea056799dc38eb27d168d93756`
- Rows: 12
- Result: PM flags/metadata、ProxyReceiver、DPM restriction、Profile、WMS、H2、OOBE、Vending、OTA residuals；沒有低權限→敏感 sink 閉合。
- Confidence: Strong evidence for bounded inventory; Unknown retained for missing callers.

### QD-DRV-01

- Files: `work/luna_worker_gpl_driver_surface_inventory_20260810.md/.csv`
- SHA-256: MD `ca908896398a6d106e3393baca30589f3297b4ea53efd808be8d75e1b88dd1a0`；CSV `e5705d76c1aaff3b76c0e4ad173717d2fee37e4d614d3d56d95edfbc12ff542f`
- Rows: 9
- Result: CMDQ/MDP、M4U、perf ioctl、sensor factory、conditional Amazon driver test、IDME/lifecycle/debugfs。
- Confidence: Confirmed source capability and source modes; low-privilege reachability remains Unknown where final image policy is absent.

### QD-GAP-01

- File: `work/luna_worker_residual_high_impact_gap_audit_20260810.md/.csv`
- SHA-256: MD `3be92ea31ad2127a2b6fc61d256d62956f1eb741840225d75c1218551e5f7644`；CSV `5352325eeb71b965e27e6a35a4071afd9cf87744a992eda0f77fbdef20aa87f9`
- Rows: 12 = 7 sensitive + 5 non-sensitive
- Result: Sensitive rows are trusted OTA/recovery, canonicalization markers, OOBE writers and SELinux/AVB boundaries; no low-privilege route established.
- Confidence: Strong evidence for row classification, not global absence proof.

## Main-agent source cross-checks

### QD-SRC-01 — trona defconfig

- File: `firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig`
- Observed: `CONFIG_MTK_CMDQ=y` and `CONFIG_MTK_CMDQ_TAB=y` at lines 139–140; `CONFIG_ION=y`/`CONFIG_MTK_ION=y` at 463–464; Amazon sign-of-life/IDME options at 524–528.
- Important negative: `CONFIG_AMZN_DRV_TEST=y` was not found.
- Confidence: Confirmed source observation; final built-kernel configuration still requires image evidence.

### QD-SRC-02 — M4U active branch

- File: `.../drivers/misc/mediatek/m4u/2.4/m4u.c`
- Observed: `#define __M4U_USE_PROC_NODE` precedes `MTK_M4U_Init`; `misc_register` is inside `#ifndef __M4U_USE_PROC_NODE`; active path calls `proc_create("m4u", 0, NULL, &m4u_fops)`.
- Interpretation: `/dev/m4u` is not established as active for this source configuration; `/proc/m4u` permission/SELinux remains unresolved.
- Confidence: Confirmed source control flow.

### QD-SRC-03 — conditional Amazon driver test

- Files: `platform/device/amazon/kernel/driver/Makefile` and `amzn_drv_test.c`
- Observed: `obj-$(CONFIG_AMZN_DRV_TEST) += amzn_drv_test.o`; test index 21 is factory-reset special mode and index 23 writes RTC special-mode bits; proc creation uses `S_IRUGO|S_IWUSR`.
- Interpretation: high-impact engineering source is conditional; no production enablement in trona defconfig, and no device test is permitted.
- Confidence: Confirmed source capability; shipped reachability Low/Medium at most.

### QD-SRC-04 — source/final-image policy gap

- Search scope: `firmware/extracted/PS7331-SOURCE-20250617` and available `firmware/extracted/PS7331` trees.
- Observed: no matching final `ueventd*.rc`, `file_contexts`, `service_contexts`, or TE allow corpus was found for the reviewed nodes in the available extracted paths.
- Interpretation: node owner/group, SELinux domain and shipped client mapping cannot be inferred from C source alone.
- Confidence: Confirmed artifact gap; not a negative permission proof.

## Phase 6QD runtime evidence

### QD-RT-01

- Directory: `adb/phase6qd/PHASE6QD-READONLY-20260810-01/`
- `metadata.json` SHA-256: `e2aacb3ac241db3dcc85cfa7d2e979ede9b823a66b0227e24b9adc4aa4f4cc70`
- `sha256sums.txt` SHA-256: `25ff097434ea7bd6c138c3adc49178d24ae5c69cc316bb54e124f86d64fb9b04`
- Build fingerprint: `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`
- Commands: 31 read-only queries/dumps; no Binder transaction, intent/broadcast, settings/package mutation, logcat clear or reboot.
- Confidence: Confirmed runtime capture.

### QD-RT-02

- Files: `home_resolve.stdout.txt`, `home_candidates_cmd.stdout.txt`, `firelauncher_package_dump.stdout.txt`, `target_selinux.stdout.txt`
- SHA-256: `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6`; `e85ea12c0b49b54392725c6f2f440f7c2b84ae4fdf47f604b9571c17427957e6`; `73cf239df6f218c345fad253d707e852ba50cdbacdefe5a93a91a99456734db5`; `4fefafd0dcddf54b31a0fef448083e7b77576d86a9ec97c14bfd92479c404290`
- Comparison: all four SHA-256 values exactly match the corresponding Phase 6QB baseline files.
- Interpretation: current HOME/package/SELinux state did not drift during Phase 6QD.
- Confidence: Confirmed runtime comparison.

## Normalized matrix

- File: `output/tables/phase6qd-privilege-surface.csv`
- SHA-256: `51c436c703c15ee6e495d5f90b00cb570c8345e301569fdc66f9501764ba3787`
- Manifest: `output/tables/phase6qd-privilege-surface.csv.manifest.json`
- Manifest SHA-256: `5483109b0e5c2d37f2aacf16efbac46425e22cb01f386859d0078ea70f59b705`
- Rows: 33 = 12 IPC + 9 GPL driver + 12 residual.
- Generator: `tools/scripts/build_phase6qd_privilege_surface.py`; dry-run and CSV validation passed.
