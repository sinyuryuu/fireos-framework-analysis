# Phase 6PZ evidence index

日期：2026-08-10
公開基準：`79955c534ec852563caf52d388587bccf12a231d`

| Evidence ID | Source | File | SHA-256 | Result | Confidence |
|---|---|---|---|---|---|
| `PZ-KERN-01` | kernel driver worker report | `work/luna_worker_kernel_driver_surface_followup2_20260810.md` | `0b850dd9bf2920a49675c042702eae67aee3485fcc6ff70bb1d175cc8d8a623b` | 13 source/user-surface rows; no direct driver→PMS/HOME edge; no device operation | Strong evidence |
| `PZ-KERN-02` | kernel driver worker matrix | `work/luna_worker_kernel_driver_surface_followup2_20260810.csv` | `3cffccae3348bbb606da02f1787f7dfc187ab630cd8e693eb45cba865bb3738b` | 13 rows, required 9-column schema | Confirmed artifact |
| `PZ-IPC-01` | IPC/OTA worker report | `work/luna_worker_ipc_ota_unclosed_followup_20260810.md` | `c590e8cc96fcaeac0f6635d33829ecca7576354b6005f424f7b8f651c8af3bb5` | 6 bounded unknowns; no low-privilege high-privilege sink closed | Strong evidence |
| `PZ-IPC-02` | IPC/OTA worker matrix | `work/luna_worker_ipc_ota_unclosed_followup_20260810.csv` | `ee307900e547452b89bf27a8b94b65b758922a2c9d8b9c6420a0645adc0c7d20` | 6 rows, 9-column schema | Confirmed artifact |
| `PZ-WA-01` | workaround gap report | `work/luna_worker_workaround_gap_followup_20260810.md` | `62abcd2bb2c6d4a3c9466dabfb01a1dd308d13084cc22824bb8941c2d0df6972` | 4 minimal host-only gaps, 5 risk-rejected rows | Strong evidence |
| `PZ-WA-02` | workaround matrix | `work/luna_worker_workaround_gap_followup_20260810.csv` | `39b0ace3cb3ce4a2d4d0c713d1e97be610cb7a1dcfc0f2d1de6b76d3dc8f6eef` | 22 rows; true HOME, per-user HOME, redirect and risk classes separated | Confirmed artifact |
| `PZ-MI-01` | Phase 6MI source archive EOF closure | `findings/phase-6mi-source-tar-eof.md` | `0b3d01e8264010320a2b504bceb249f7459bbe96072426e91fe1a42dc56f596f` | 35 outer members; EOF reached; no outer updater/post-install member | Confirmed static |
| `PZ-ME-01` | Phase 6ME driver control closure | `findings/phase-6me-driver-control-closure.md` | `5c9bd9bdc2fedf00502cdd50b638e1606771d6bcf1c4b7a3821438b988f4d7de` | 1,671 selected source files; no direct framework/HOME source edge | Strong evidence |
| `PZ-MN-01` | Phase 6MN IPC user-scope closure | `findings/phase-6mn-ipc-user-scope-closure.md` | `2adc3dd733dbc310da2706a14e9e7f12759198c09f37a63970f35c97855f383e` | 42 bounded routes; no untrusted User-0 Fire/HOME sink | Strong evidence |
| `PZ-NORM-01` | normalized Phase 6PZ matrix | `output/tables/phase6pz-broad-surface-closure.csv` | `4d551e0a1c7f3a8e33e70b19d5c345a1cc264fc3e3d06312aed3098468392102` | 41 rows: 13 kernel + 6 IPC/OTA + 22 workaround | Confirmed |
| `PZ-NORM-02` | normalization manifest | `output/tables/phase6pz-broad-surface-closure.csv.manifest.json` | `bb02def5015ebd98e580b04e7234f0cea55d8ee886387b3d635a5b907fae9236` | input hashes, row counts, output hash, no-device/no-mutation flags | Confirmed |
| `PZ-SCRIPT-01` | Phase 6PZ generator | `tools/scripts/build_phase6pz_broad_surface_closure.py` | `d5bf3b394f36c4ee7189516bcec72d661f799b2afc45717c446b556eaf7155dc` | `py_compile`, dry-run, and write-once generation passed | Confirmed |
