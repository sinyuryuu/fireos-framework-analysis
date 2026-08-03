# Phase 5AD evidence index

| Evidence ID | Source | Observation | Classification |
|---|---|---|---|
| P5AD-SOURCE-001 | o3note historical Fire tutorial | 2017/Fire OS 5.6.4.0 is the demonstrated target; 2019/7.3.1.0 is explicitly untested | 已證實，source-scoped |
| P5AD-SOURCE-002 | KoCleo fixed README/source | Later firmware may block mtk-su; no KFTRWI/trona tested device | 已證實，source-scoped |
| P5AD-DEVICE-001 | adb/phase5/MTK-SU-CMDQ-T03 and Phase 5E report | Exact PS7330 payload failed at critical init step 3, no UID 0 | 已證實 |
| P5AD-MTK-001 | Phase 5AC mtkclient excerpt | Shared MT8183 profile uses dacode 0x6771; no independent 0x8183 key | 已證實，source-scoped |
| P5AD-RISK-001 | artifact commands.txt | No new payload, BROM, DA, flash, device-node or boot-chain operation | 已證實 |
