# Phase 5BT evidence index

本索引只收錄 PS7331 主機端 source／boot provenance 證據。每筆資料都保留
原始檔案路徑、命令與 SHA-256；不存在 live exploit、root 或 partition evidence。

## P5BT-ARCHIVE-001

- Source: Official Amazon S3 PS7331 source archive
- File: `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2`
- SHA-256: `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea`
- Test ID: `P5BT-HOST-ARCHIVE-01`
- Timestamp: `2026-08-04`
- Command: `stat`, `md5 -q`, `shasum -a 256`; HTTP HEAD preserved in `artifacts/phase5/phase5bn-ghostlock-marker-recheck-20260804-01/source-http-headers.txt`
- Observed result: local size `2563328975`; MD5 equals ETag `88ff8aaa109325255b9a1caa76ab5da9`; Content-Length matches.
- Interpretation: Local file is byte-consistent with the official single-part S3 object metadata.
- Confidence: **Confirmed**
- Related hypothesis: PS7331 source identity is exact.

## P5BT-BUILD-001

- Source: Top-level build members from the same local archive
- File: `artifacts/phase5/ps7331-top-level-build-members-20260804-01/`
- SHA-256: metadata manifest `083d2c41ff0c03dd886a92d645a0f036b284206d553800192e0372368767d844`
- Test ID: `P5BT-HOST-BUILD-01`
- Timestamp: `2026-08-04T06:34:12Z`
- Command: `python3 -B tools/scripts/extract_phase5_ps7331_outer_members.py ...`
- Observed result: both build scripts present; no content was executed.
- Interpretation: The archive publishes the build-selected MT8183 path and product defconfig mapping.
- Confidence: **Confirmed**
- Related hypothesis: `mt8183/4.4` is the correct PS7331 source subtree.

## P5BT-BUILD-002

- Source: Static analyzer over the extracted build scripts
- File: `artifacts/phase5/phase5bt-build-script-controls-20260804-01.csv`
- SHA-256: `f3eff6635a68a11262f66cb88805ad697b711c9133372b28a747a20ab430c94e`
- Test ID: `P5BT-HOST-BUILD-02`
- Timestamp: `2026-08-04`
- Command: `python3 -B tools/scripts/analyze_phase5bp_build_scripts.py --scripts-dir ...`
- Observed result: `KERNEL_SUBPATH=kernel/mediatek/mt8183/4.4`, `DEFCONFIG_NAME=trona_defconfig`, `TARGET_ARCH=arm64`, zero visible non-comment suspicious patch/apply tokens.
- Interpretation: The visible scripts build and validate the kernel outputs but do not show a patch or signing stage.
- Confidence: **Strong evidence** for captured-script scope; release-CI scope remains unknown.
- Related hypothesis: Public build scripts do not visibly apply a GhostLock patch.

## P5BT-SOURCE-001

- Source: Build-selected PS7331 nested source member
- File: `artifacts/phase5/ps7331-full-source-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c`
- SHA-256: `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde`
- Test ID: `P5BT-HOST-SOURCE-01`
- Timestamp: `2026-08-04T06:25:22Z`
- Command: `python3 -B tools/scripts/check_phase5_ghostlock_source_semantics.py ...`
- Observed result: lines 1079–1129; `current_pi_blocked_on_cleanup=true`; `waiter_task_reference_in_remove_waiter=false`; proxy error call present.
- Interpretation: The selected PS7331 source retains the pre-fix cleanup pattern.
- Confidence: **Confirmed**
- Related hypothesis: PS7331 source does not contain the upstream `waiter->task` fix.

## P5BT-SOURCE-002

- Source: Build-selected PS7331 nested futex member
- File: `artifacts/phase5/ps7331-full-source-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/futex.c`
- SHA-256: `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96`
- Test ID: `P5BT-HOST-SOURCE-02`
- Timestamp: `2026-08-04`
- Command: `rg -n 'rt_mutex_start_proxy_lock|this->task' .../futex.c`
- Observed result: PI requeue path passes `this->rt_waiter` and `this->task` at lines 1958–1965.
- Interpretation: Source contains the relevant proxy-waiter wiring; this is not trigger or privilege-transition proof.
- Confidence: **Confirmed** for source wiring; **Hypothesis** for live reachability.
- Related hypothesis: GhostLock path may be present in the PS7331 source.

## P5BT-PATH-001

- Source: Local nested `platform.tar` path inventory
- File: `artifacts/phase5/ps7331-local-nested-build-index-20260804-02/`
- SHA-256: metadata `c59ac6ae55766fa70987fdced2e4f578ecea69577364200eb47fba580884cfb7`; patch subset `14f27eed487b1cd1900772a42d9361dabbe4eb6628eefe2cadc48141c394563d`
- Test ID: `P5BT-HOST-PATHS-01`
- Timestamp: `2026-08-04T06:21:22Z`
- Command: `tools/scripts/index_phase5_ps7331_local_nested_build_inputs.sh --archive ...`
- Observed result: `outer_tar=0`, `nested_tar=0`, `filter=0`; named patch subset contains four Mali hrtimer paths and no GhostLock-named path.
- Interpretation: No clearly named public rtmutex/futex patch was observed in the path inventory.
- Confidence: **Strong evidence** for path-name scope; not a proof against release-CI transforms.
- Related hypothesis: No named source patch hides the fix.

## P5BT-IMAGE-001

- Source: Official PS7331 OTA-derived boot image and preserved boot metadata
- File: `firmware/extracted/PS7331/boot.img`
- SHA-256: `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b`
- Test ID: `P5BT-HOST-IMAGE-01`
- Timestamp: `2026-08-04`
- Command: Existing address-sanitized static review and `tools/scripts/verify_phase5bs_ps7331_ghostlock_evidence.py`
- Observed result: `image_has_current_task_source=true`, `image_has_current_task_cleanup=true`, `image_proxy_calls_remove_waiter=true`.
- Interpretation: The inspected Image is consistent with the pre-fix source semantic pattern.
- Confidence: **Strong evidence** for the inspected Image scope.
- Related hypothesis: PS7331 production boot Image is not shown to include the fix.

## P5BT-VERIFY-001

- Source: Host-only evidence verifier
- File: `artifacts/phase5/phase5bs-ps7331-evidence-verification-20260804-01/verification.json`
- SHA-256: `f329d293221abd38ad45cf0ebee86e6358ea27bcc7fed0aa69204c1925a2ecff`
- Test ID: `P5BT-HOST-VERIFY-01`
- Timestamp: `2026-08-04`
- Command: `python3 -B tools/scripts/verify_phase5bs_ps7331_ghostlock_evidence.py ...`
- Observed result: all source/Image consistency checks pass; `runtime_exploitability_proven=false`; `root_or_privilege_gain_proven=false`; no payload or address output.
- Interpretation: Static evidence is internally consistent and deliberately bounded.
- Confidence: **Confirmed**
- Related hypothesis: Static pre-fix evidence is not a live PoC.

## P5BT-SAFETY-001

- Source: Phase 5BT command manifests and artifact metadata
- File: `artifacts/phase5/phase5bt-ps7331-source-archive-validation-20260804-01/metadata.tsv`
- SHA-256: recorded by the directory manifest
- Test ID: `P5BT-SAFETY-01`
- Timestamp: `2026-08-04`
- Command: Host-only `tar`, `md5`, `shasum`, Python text/hash tools
- Observed result: no ADB, fastboot, OTA, exploit, kernel execution, image write, or partition write.
- Interpretation: Device state was not changed by this phase.
- Confidence: **Confirmed**
- Related hypothesis: None; safety boundary.

## Consolidated verdict

| Question | Verdict |
|---|---|
| PS7331 archive identity | **Confirmed** |
| Build-selected PS7331 kernel source | **Confirmed** |
| `waiter->task` GhostLock fix in selected PS7331 source | **Confirmed absent** |
| Fix absent from inspected PS7331 Image markers | **Strong evidence** |
| Live PS7331 trigger | **Hypothesis / not tested** |
| Live root or privilege gain | **Not proven** |
| Upgrade to PS7331 as GhostLock remediation | **Disproved for the inspected evidence** |
| Exploit/flash/root execution | **Rejected for risk** |
