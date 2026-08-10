# Phase 6PY evidence index

日期：2026-08-10
公開基準：`77c076b7624ce44f33a7107d7860db991ea57de1`

本輪證據以 host-side worker matrices、既有 exact-build artifacts 與 Phase 6PW
read-only comparator 為主。Phase 6PY 沒有新增可引用的 device mutation capture。

| Evidence ID | Source | File | SHA-256 | Test / timestamp | Observed result | Interpretation | Confidence |
|---|---|---|---|---|---|---|---|
| `PY-SERVICE-01` | Amazon service permission worker | `work/luna_worker_amazon_service_permission_followup_20260810.csv` | `9b6592de3a8d00e2ceab6bc8836a1814190cf6def35ba28ba0be468f8718318a` | host-only / 2026-08-10 | 11 rows covering ASP, SmartSuspend, thermal, fosdebug, Activity/Window/Input | Permission anomalies and sink boundaries are separated; no HOME/package/root sink closed | Strong evidence |
| `PY-SERVICE-02` | Amazon service permission report | `work/luna_worker_amazon_service_permission_followup_20260810.md` | `f6d3e93b537b1dbb11239a6d204bb025b5a08a5bd5573d5fa129d86236cf843d` | host-only / 2026-08-10 | ASP tablet allow branch and prewarm unconsumed check are static candidates; private-service lookup boundary remains denied | Static anomaly is not runtime exploitability | Strong evidence |
| `PY-STATE-01` | Fire package-state writer worker | `work/luna_worker_fire_state_writer_followup_20260810.csv` | `28e8d27989c88aa411513344177e8dffdd6bf54c180b152fd16b6c85dbb6e8c6` | host-only / 2026-08-10 | 16 deduplicated writers; KFT Fire/Tahoe writer uses supplied child/profile `UserInfo.id` | Child-scoped static writer, not User-0 shell bypass | Confirmed static |
| `PY-STATE-02` | Fire package-state writer report | `work/luna_worker_fire_state_writer_followup_20260810.md` | `3b403e6af5e9961f5b1b6561e9dc4f7527beee356cd8dfbc2e241be41ac44226` | host-only / 2026-08-10 | PMS protected callback is pre-write gate; Arcus resource seed and live-set limitation kept separate | Package protection is not a HOME writer | Strong evidence |
| `PY-FOS-01` | fosinit/exported sink worker | `work/luna_worker_fosinit_exported_sink_followup_20260810.csv` | `1e1a9023dfd002f9c28ab7d27577b346049bba285c24fee90f4452727aa76976` | host-only / 2026-08-10 | 11 deduplicated rows covering 123 fosinit XMLs and exported candidates | No new ordinary/shell path to User-0 HOME/preferred/package/settings/DPM sink | Strong evidence |
| `PY-FOS-02` | fosinit/exported sink report | `work/luna_worker_fosinit_exported_sink_followup_20260810.md` | `9b9ca43e93d8417d068edfb248d01772bbd5a6ab47f9dad9af8acb430021f3aa` | host-only / 2026-08-10 | Only retained high-impact edge is protected `BOOT_AFTER_SYSTEM_OTA` lifecycle; no public HOME writer | OTA/OOBE edge is lifecycle-bound | Strong evidence |
| `PY-NORM-01` | Phase 6PY normalizer output | `output/tables/phase6py-service-state-exported-closure.csv` | `cf26ff1c72c0a6eefaa66aa26ce7675ec24b452f8e8844c347b3be358d358a6b` | generated / 2026-08-10 | 38 rows: 11 service + 16 state + 11 fosinit/exported | Reproducible caller→gate→identity→sink closure matrix | Confirmed |
| `PY-NORM-02` | Phase 6PY normalizer manifest | `output/tables/phase6py-service-state-exported-closure.csv.manifest.json` | `99da85f41a64fd6d4248064eb36cadac5332d468773d7f96b2b342cde8285cb8` | generated / 2026-08-10 | Records input hashes, row counts, output hash and no-device/no-mutation flags | Reproduction and provenance metadata | Confirmed |
| `PY-SCRIPT-01` | Phase 6PY normalizer | `tools/scripts/build_phase6py_service_state_closure.py` | `695c8a38a10851ab60ed3c205788d05854380f7303555fe30e20e2498cc433e7` | `py_compile` + dry-run / 2026-08-10 | Dry-run reports no device contact, mutation, Binder transaction or root/exploit | Safe regeneration path | Confirmed |
| `PY-LIVE-01` | inherited Phase 6PW read-only comparator | `adb/phase6pw/PHASE6PW-READONLY-20260810-01/home_resolve.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` | PHASE6PW-READONLY-20260810-01 | User 0 HOME resolves to Fire Launcher priority 50 | Current runtime comparator; not new Phase 6PY mutation evidence | Confirmed |
| `PY-DENY-01` | inherited Phase 6PX resource provenance | `work/luna_worker_denylist_provenance_followup_20260810.csv` | `3c24274403383899e74dc78eb08670217a795698b00ad36aa89f60c1aa07721f` | Phase6PX / 2026-08-10 | Extracted deny-list resource directly lists `com.amazon.firelauncher` | Static seed membership is direct; live persisted set remains unknown | Confirmed static |

## Safety statement

Worker reports and the normalizer were host-only. No unknown Binder transaction,
`service call`, ioctl, package/settings mutation, protected broadcast, user
provisioning, reboot, OTA/recovery, Root, exploit or partition operation was
performed as part of Phase 6PY.
