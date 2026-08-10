# Phase 6QF evidence index — broad privilege-surface closure

日期：2026-08-10
公開基準：`aca16f12daa7807e435fcbc259e5af067cab6b12`
裝置：`G001LT0511550CFT` / `KFTRWI` / `trona` / PS7331

本輪只對既有 host corpus 做靜態交叉驗收，並整合 Phase 6QE 的 exact-device
metadata-only snapshot；沒有新增裝置狀態變更。

## Evidence entries

### QF-IPC-01 — Amazon IPC residual caller/provenance ledger

- Source: host-only worker audit
- File: `work/luna_worker_phase6qf_ipc_provenance_20260810.md/.csv`
- SHA-256: MD `7b993902f3081d9d3ad6f80848bd26357c70c4e8125b29707c7339bf313c1868`;
  CSV `2bbcebdd9dc1beaec690210a4e14f4754baae8a15c61a7036162eb8b643f1ae2`
- Test ID: `PHASE6QF-HOST-IPC-20260810`
- Timestamp: 2026-08-10
- Command: host-side CSV/DEX/JADX/baksmali review; no device command
- Observed result: 12 rows covering registration, Stub/onTransact or facade,
  caller/sender, gate, identity, user propagation and first sink. Several sinks
  are confirmed, but no ordinary app/shell → accepted trusted identity → User-0
  sensitive sink chain is closed.
- Interpretation: UNKNOWN caller, permission holder, numeric user, or first
  consumer remains an evidence gap, not a vulnerability.
- Confidence: Strong evidence for the bounded corpus
- Related hypothesis: any Amazon private service can be used by shell/ordinary app

### QF-POL-01 — PS7331 exact-image policy/client mapping

- Source: host-only source/config/image-policy review
- File: `work/luna_worker_phase6qf_exact_policy_client_20260810.md/.csv`
- SHA-256: MD `64849d6a46ccc91a1e959574f057da89fa9ff28509c009a4e5bf2b94c35e3907`;
  CSV `a44bbee4cb3336d228e2c55a46e0d71d31b1372c1b4e391a8d0ba4be715863`
- Test ID: `PHASE6QF-HOST-POLICY-20260810`
- Timestamp: 2026-08-10
- Command: host-side source, defconfig, init, file_contexts and CIL review; no device command
- Observed result: 7 rows covering CMDQ/MDP, M4U, perfmgr, gsensor, IDME/lifecycle
  and `amzn_drv_test`. Source registration and selected image policy markers are
  present; exact shipped client/domain/allow closure is incomplete on several rows.
- Interpretation: source capability, a node name, or a generic SELinux type does
  not establish runtime reachability or a privilege transition.
- Confidence: Confirmed for cited source/image markers; bounded Unknown for missing clients
- Related hypothesis: a driver or procfs surface provides a low-privilege control path

### QF-RT-01 — existing runtime and ADB evidence audit

- Source: prior exact-device evidence, no retest
- File: `work/luna_worker_phase6qf_existing_runtime_audit_20260810.md/.csv`
- SHA-256: MD `c3e861f58b37d57293448319a8131936fb4b57e7573df1b8a11630475c149782`;
  CSV `cdbf5f5f0bfec5f9f8a743bed82b6654aa29a7ed484a408e16acaa194b8a0dcb`
- Test ID: `PHASE6QF-EXISTING-RUNTIME-AUDIT-20260810`
- Timestamp: 2026-08-10
- Command: read-only inspection of saved `adb/`, `artifacts/`, `findings/` and scripts
- Observed result: 7 rows reconcile package gate, KFT/profile, DPM/Profile,
  Accessibility fallback, service visibility, OOBE/OTA and driver metadata.
- Interpretation: prior denials and current HOME state are directly reusable; no
  new writer, lifecycle or private-service behavior is implied.
- Confidence: Confirmed where raw hashes are cited; remaining caller provenance Unknown
- Related hypothesis: a previously observed service or lifecycle path can be replayed safely

### QF-RT-02 — exact-device metadata anchor reused from Phase 6QE

- Source: exact-device metadata-only snapshot
- File: `adb/phase6qe/PHASE6QE-DEVICE-READONLY-20260810-02/`
- SHA-256: `metadata.json` `5afaf05e9d2bec715d9142250f053441b31383ffe9624cb3d80f03cff6e16a0d`;
  `sha256sums.txt` `355dd168ad1061f5f017fb24f0d5b6e102d0d17e58cf38710d777cd39c5facee`
- Test ID: `PHASE6QE-DEVICE-READONLY-20260810-02`
- Timestamp: `2026-08-10T02:42:40Z`
- Command: 12 read-only ADB commands, recorded by
  `tools/scripts/capture_phase6qe_device_readonly.py`
- Observed result: HOME remains `com.amazon.firelauncher/.Launcher` priority 50;
  `/dev/mtk_cmdq` is `0644 system:system`, `/dev/gsensor` is `0660 radio:system`,
  `/proc/perfmgr/perf_ioctl` is root-owned, and shell metadata access to selected
  proc nodes is denied. No node was opened.
- Interpretation: direct runtime metadata anchor only; unopened-driver behavior is
  not inferred.
- Confidence: Confirmed
- Related hypothesis: exact device exposes a shell-reachable high-impact control node

### QF-MATRIX-01 — normalized 26-row matrix

- Source: deterministic host-only generator
- File: `output/tables/phase6qf-privilege-surface.csv`
- SHA-256: `c2b994c47a1bb90dc181e5377e78f5f0758478656eeda6aa495c931811fddd20`
- Manifest: `output/tables/phase6qf-privilege-surface.csv.manifest.json`
  SHA-256 `e263d06dd8331da5f678e65394deecd8e8233c7b2421dcddd2565763537e07a6`
- Test ID: `PHASE6QF-HOST-MATRIX-20260810`
- Timestamp: 2026-08-10
- Command: `python3 tools/scripts/build_phase6qf_privilege_surface.py`
- Observed result: 26 rows = 12 IPC + 7 exact-image policy/client + 7 existing runtime.
- Interpretation: normalized comparison surface; not an exploit result.
- Confidence: Confirmed reproducible transformation
- Related hypothesis: cross-domain evidence closes a low-privilege privilege chain

### QF-SAFETY-01 — operations deliberately not executed

- Source: Phase 6QF safety boundary
- File: `findings/phase-6qf-report.md`
- SHA-256: recorded after finalization
- Test ID: `PHASE6QF-SAFETY-20260810`
- Timestamp: 2026-08-10
- Command: none
- Observed result: no unknown Binder transaction, private broadcast, driver node
  open/ioctl, OTA/recovery/updater, Root/exploit, remount, SELinux mutation,
  Fire Launcher disable/hide/suspend/uninstall/force-stop/clear, reboot or partition write.
- Interpretation: risk-rejected, not a negative runtime result.
- Confidence: Confirmed by worker scope and generator metadata
- Related hypothesis: a destructive or exploit test is required before any conclusion

## Confidence vocabulary

- **已證實 / Confirmed**：直接觀察或 hash-verifiable 的來源、映像或保存 runtime 事實。
- **高可信推論 / Strong evidence**：多個獨立 artifact 一致，但仍有明確未閉合 edge。
- **Probable**：有界推論，不能當作已證實權限。
- **Hypothesis**：需要下一個安全分析或測試。
- **Disproved**：在指定 build/caller/test scope 內被反證。
- **因風險拒絕測試 / Risk-rejected**：刻意未執行，不能解讀為 runtime negative。
