# Phase 6MN evidence index

All Phase 6MN evidence below is host-only and read-only. No device command,
Binder transaction, ioctl, package mutation, settings write, reboot, OTA,
recovery, or partition operation was used in this phase.

| Evidence ID | Source / file | SHA-256 | Test ID | Observation | Interpretation | Confidence |
|---|---|---|---|---|---|---|
| `6MN-001` | `artifacts/phase6mc-caller-provenance-20260810-01/caller-provenance.csv` | `fbb4f21dad1c3948bb3748fe7bcf652b6b136a6fb07e62cb4e7d7e6d51e1b11d` | `PHASE6MN-HOST-01` | Seven curated caller/entry routes with permission, identity, sink, and scope fields | Existing caller provenance is the primary input for route normalization | Strong evidence |
| `6MN-002` | `artifacts/phase6kv/pms-home-caller-closure-20260810-01/pms-home-callers.csv` | `dc1a86ea85904e3775704944fa86364a9a89033f6146eed0dac8b324b7028382` | `PHASE6MN-HOST-01` | 25 exact package/preferred/component state invoke sites | Separates KFT child writer, shell front end, internal HOME writer, and other system writers | Strong evidence |
| `6MN-003` | `artifacts/phase6kw-vendor-home-callbacks/vendor-home-callbacks.csv` | `638c1a8ae1bae66cb24ebede74a8afcb48e26fd09f0028d87a8d2fef6ac3bc3d` | `PHASE6MN-HOST-01` | AppCompat delegates to IPackageManager; Eve has no concrete resolver override; no Fire literal | No Fire-specific final selection override in selected callbacks | Confirmed |
| `6MN-004` | `artifacts/phase6mg-oobe-helper-scope-20260810-01/helper-scope.csv` | `0c144bb1b79b359bc00cb52daca41faa23cb3a61f763491c11655df3010d457d` | `PHASE6MN-HOST-01` | 29 helper signals; no explicit `ForUser` call at helper sites; settings/component calls are Context-bound | OOBE user mapping remains unresolved; helper is not a normal HOME writer | Strong evidence |
| `6MN-005` | `artifacts/phase6bk/ipc-ota-closure-20260810-02/method-map.csv` | `b487531c8ae8dbf55812feb463f666810eb63acca98d3ce57dbffddf37567acf` | `PHASE6MN-HOST-01` | Preserved Amazon service method inventory used as cross-artifact support | Supports the selected IPC/service boundary mapping; not a live reachability proof | Probable |
| `6MN-006` | `findings/phase-6gv-amazon-user-manager-tx4-settings-deputy.md` | `2c6c5ab757dab503fb6a295bbb823e446cb41d69a4378abb5f91a8c10664b8cf` | `PHASE6GV-USERMANAGER-TX4-20260807-02` | Ordinary APK tx4 wrote setup settings under cleared identity; Fire package/HOME unchanged and rollback succeeded | Confirms a settings-only confused deputy, not a HOME route | Confirmed |
| `6MN-007` | `findings/phase-6er-amazon-prewarm-confused-deputy.md` | `e3f940fa236a80865d505a3c852ab5030c3265dafa8126d59f58727d949fd548` | `PHASE6ER-UNTRUSTED-SERVICE-LOOKUP-20260806-134346` | Ordinary APK reached process-prewarm sink; no package/HOME sink | Confirms secondary process/resource effect only | Confirmed |
| `6MN-008` | `findings/phase-6r-bootafter-system-ota-authorization.md` | `4c2edb6e43b39bfbe615fd8779f49026f3694cad884ebab50103f0cfbd701fbc` | `PHASE6R-HOST-01` | OTA/OOBE sender is guarded system lifecycle; manual broadcast has side effects and was rejected | OOBE is high-impact lifecycle surface, not a safe shell HOME selector | Strong evidence |
| `6MN-009` | `artifacts/phase6mn-ipc-user-scope-20260810-01/route-matrix.csv` | `a156538f89cff05e098a01fce169fda4e88f65b86fe4b06054d740cbd615e56b` | `PHASE6MN-HOST-01` | 42 normalized route rows | Unified caller→permission→identity→sink→user-scope ledger | Strong evidence |
| `6MN-010` | `artifacts/phase6mn-ipc-user-scope-20260810-01/summary.json` | `36e2c71079b4482fbb64e4672a57a00d9a2d9e5b233395e3cce3fa4089dbe669` | `PHASE6MN-HOST-01` | `device_contacted=false`, `binder_or_service_call=false`, `ioctl=false`, `mutation=false` | Safety and bounded-negative metadata for this run | Confirmed |
| `6MN-011` | `output/tables/phase6mn-ipc-user-scope-20260810-01.csv` | `a156538f89cff05e098a01fce169fda4e88f65b86fe4b06054d740cbd615e56b` | `PHASE6MN-HOST-01` | Review copy of the write-once route ledger | Reproducible table for downstream review | Strong evidence |

## Input manifest

The complete input path/size/hash manifest is:

```text
artifacts/phase6mn-ipc-user-scope-20260810-01/input-manifest.csv
```

Its SHA-256 is:

```text
afe09b2b8985e245d9835a53b58d5c9ec3fe8033bd69633b8cc8068c49d11760
```

The generated artifact directory also contains `sha256sums.txt`. All outputs
were new paths; the script refuses to overwrite an existing output.

## Reproduction

From the repository root:

```sh
python3 -m py_compile tools/scripts/audit_phase6mn_ipc_user_scope_closure.py
python3 tools/scripts/audit_phase6mn_ipc_user_scope_closure.py --dry-run
python3 tools/scripts/audit_phase6mn_ipc_user_scope_closure.py
```

The script uses only preserved host files and explicitly performs no ADB,
network, Binder, ioctl, reboot, mutation, or exploit operation.
