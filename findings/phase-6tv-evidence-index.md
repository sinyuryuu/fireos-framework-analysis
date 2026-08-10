# Phase 6TV evidence index

## 6TO IPC sink audit

Report SHA-256: `2e7d1e0b8c091e8c69573abf136368fae3b700407ba3c074d1b2c513228148a6`

CSV SHA-256: `43b7c270de32105680b12969b1a8dbd5a84d37a82a06d5ae24d08d0185e469a5`

Sources: `work/luna_worker_phase6to_ipc_sink_audit_20260810.md`, `work/luna_worker_phase6to_ipc_sink_audit_20260810.csv`

## 6TP OTA writer audit

Report SHA-256: `1f2b859aa5113cd9c51fa325314017929910a8400458256119326c6cbcbdf7b5`

CSV SHA-256: `949dd5515b55d0e4061c495156bc983f7c55a7193a33cabaa2d558b642d32440`

Sources: `work/luna_worker_phase6tp_ota_writer_audit_20260810.md`, `work/luna_worker_phase6tp_ota_writer_audit_20260810.csv`

## 6TQ driver inventory

Report SHA-256: `d6cd5da0ff28632e1bca65f0e7c0255b4f6783b717a86a7a8662df1d93edba43`

CSV SHA-256: `289dde4546aacc33aaacec0f715d2f5dbd2ddcd0cde9f415f90c7ac14c0567b5`

Sources: `work/luna_worker_phase6tq_driver_inventory_20260810.md`, `work/luna_worker_phase6tq_driver_inventory_20260810.csv`

## 6TR test reconciliation

Report SHA-256: `1d1c267a88bb3d2e96f1a5e0d0d7d46368f136c81f591c6a6b17964b5b7a4b30`

CSV SHA-256: `04c49baf1fd96f32a5497022d43486b6651f4f1a0656c46ab52f4786cf728cd3`

Sources: `work/luna_worker_phase6tr_test_reconciliation_20260810.md`, `work/luna_worker_phase6tr_test_reconciliation_20260810.csv`

## Context

- `findings/phase-6tm-report.md`: `73ea2ed41c91f96958172fe3b5e034e75324ebbd249341a6db37e74bffc48d89`
- `findings/phase-6tm-evidence-index.md`: `90917fa9eace7d49435cd1114cbda1b34fdd7950967db77b85941e8ef06aac56`
- `output/tables/phase6tm-control-surface.csv`: `e207284a5701448da27ac5fa0dbf844190e94c534876a0540e92a16affdd1444`
- `findings/phase-6tu-readonly-snapshot.md`: `e83a3529a63a05c5a1fa1f2c86c18eed764d8027f444dcd2eed10b7e8ae0fae0`
- `output/tables/phase6tu-readonly-state.csv`: `83cb7258da8177858bfd827a2cdda0dfaf0b960dd9ab2785b7800ec023b3dee2`

## Labels

- `CONFIRMED`: exact static declaration or read-only observation is directly supported.
- `STRONG_STATIC`: bounded caller/gate/sink edge, with at least one missing external/runtime edge.
- `UNKNOWN`: caller, loader, identity, policy, user scope or downstream effect is missing.
- `NOT_A_SINK`/`ABSENT`/`LOCAL_ONLY`: scope classifications, not exploit conclusions.
