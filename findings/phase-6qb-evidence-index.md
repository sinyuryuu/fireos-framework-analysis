# Phase 6QB evidence index

日期：2026-08-10
公開基準：`c8ece719f7577b7815c8379265c54efd04dbefb2`

| Evidence ID | Source | File | SHA-256 | Result | Confidence |
|---|---|---|---|---|---|
| `QB-PM-01` | tx6/tx7 caller inventory | `work/luna_worker_amazonpm_caller_inventory_20260810.md` | `6776c3ddca75b7cb1ded1fec50e175f389a38795213735400fcae0f0117a1863` | No production caller/system-token provenance in bounded exact-build corpus | Strong evidence |
| `QB-PM-02` | tx6/tx7 matrix | `work/luna_worker_amazonpm_caller_inventory_20260810.csv` | `7ea3f7cc3194084a5b9c75c14e2bce56c1096cf99f21bc5b62951ff37fcd2d74` | 2 rows; implementation/gates and NOT_FOUND caller status | Confirmed artifact |
| `QB-VEND-01` | Vending downstream report | `work/luna_worker_vending_downstream_closure_20260810.md` | `2029962c917e1d5481ba999c5545611542b795c9400748b8c8d8463c8b9404d6` | Restore/browser/search/secure-settings/install sinks; no Fire/HOME/root sink | Strong evidence |
| `QB-VEND-02` | Vending downstream matrix | `work/luna_worker_vending_downstream_closure_20260810.csv` | `e468aebac3cf204a23c69206ccddbbf1b2c180b5ca362e5dcdb3ae17f22f6f77` | 9 rows; schema validated | Confirmed artifact |
| `QB-WR-01` | PS7331 residual writer report | `work/luna_worker_ps7331_residual_writer_inventory_20260810.md` | `43ea9e03e59c1ff677fc1f87cbc514e6d30a62325dfba6abca7d6aafb7e68c80` | 7 bounded OOBE/OTA/fosinit residuals; no low-privilege sink closed | Strong evidence |
| `QB-WR-02` | PS7331 residual writer matrix | `work/luna_worker_ps7331_residual_writer_inventory_20260810.csv` | `967b23450726a54e0fba2bb00e587e2d16d3451f365b7503c2c0d4e62bbbbba5` | 7 rows, 11 columns | Confirmed artifact |
| `QB-RT-01` | canonical read-only baseline | `adb/phase6qb/PHASE6QB-READONLY-20260810-01/metadata.json` | `9c8db228ac716492ee230e5e93e59eb5cb8ef082b15a0077b66acba1523c2f79` | 31 read-only commands; no mutation/Binder/reboot/OTA | Confirmed runtime capture |
| `QB-RT-02` | HOME resolution | `adb/phase6qb/PHASE6QB-READONLY-20260810-01/home_resolve.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` | Fire Launcher priority 50 remains resolver winner | Confirmed runtime |
| `QB-RT-03` | HOME candidates | `adb/phase6qb/PHASE6QB-READONLY-20260810-01/home_candidates_cmd.stdout.txt` | `e85ea12c0b49b54392725c6f2f440f7c2b84ae4fdf47f604b9571c17427957e6` | Fire 50, Microsoft 0, FallbackHome -1000 | Confirmed runtime |
| `QB-RT-04` | Fire package state | `adb/phase6qb/PHASE6QB-READONLY-20260810-01/firelauncher_package_dump.stdout.txt` | `73cf239df6f218c345fad253d707e852ba50cdbacdefe5a93a91a99456734db5` | System/priv-app path; User 0 installed/visible/not suspended; no mutation | Confirmed runtime |
| `QB-RT-05` | service-manager policy | `adb/phase6qb/PHASE6QB-READONLY-20260810-01/logcat_all_dump.stdout.txt` | `dcef2a733776de2832c99dfe2239f25a619ab222a0bfbc44f60b17b354ddf451` | shell UID 2000 `find` denied for Amazon private services | Confirmed runtime |
| `QB-NORM-01` | normalized residual matrix | `output/tables/phase6qb-residual-inventory.csv` | `9c3ba480da85b6a79952d10d597f07a9caf558425c56f0308bfd0ae6b9182f37` | 18 rows: 2 PM + 9 Vending + 7 writers | Confirmed artifact |
| `QB-NORM-02` | normalization manifest | `output/tables/phase6qb-residual-inventory.csv.manifest.json` | `3577416d727d24bea7d40ec40d99cc279721f96a9328f659b60bdb2a4bf9386f` | Inputs/output hashes and no-device flags match | Confirmed artifact |
| `QB-SCRIPT-01` | host-only generator | `tools/scripts/build_phase6qb_residual_inventory.py` | `4f153032c21ebef26b7e90defe357da27b1a9a945e5425840bad19eb72b93f0d` | py_compile, dry-run, write-once generation passed | Confirmed artifact |

## Confidence rule

`UNKNOWN`/`NOT_FOUND` means the saved corpus did not establish the item. It is
not converted into a negative proof or a vulnerability claim. Any device test
would require a new concrete caller plus a reversible, low-risk sink.
