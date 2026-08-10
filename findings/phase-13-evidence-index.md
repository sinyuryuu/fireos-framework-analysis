# Phase 13 evidence index

Generated UTC: `2026-08-10T08:55:47.359238+00:00`

This is a host-only closure. It does not claim that an external caller
can invoke tx3, construct UserInfo for User 0, bypass PMS, open a driver,
or mutate Fire Launcher state. Unknown edges remain explicitly unknown.

## Evidence IDs

| ID | Finding | Source | Confidence | Missing edge |
|---|---|---|---|---|
| `P13-KFT-001` | tx3 Stub enforces descriptor, decodes nullable UserInfo and dispatches | `boot-fosframework/disassembly.log:370674-370777` | Confirmed | inherited/superclass authorization and full cross-user gate |
| `P13-KFT-002` | tx3 Proxy parcels UserInfo and calls transact(3) | `boot-fosframework/disassembly.log:370398-370443` | Confirmed | external APK/native caller and UID/signature |
| `P13-KFT-003` | BinderService tx3 implementation reaches supplied-user KFT path | `fosservices/disassembly.log:54415-54478` | Strong evidence | authorization and PMS downstream gates |
| `P13-KFT-004` | createChildUser is the closed semantic caller and passes returned child UserInfo | `boot-fosframework/disassembly.log:369180-369243` | Strong evidence | upstream runtime caller and caller authorization |
| `P13-ID-001` | AmazonPackageManagerImpl obtains standard package Binder after private service | `boot-fosframework/disassembly.log:366047-366081; fosservices/disassembly.log:55072-55076` | Strong evidence | runtime attribution/SELinux capture |
| `P13-ID-002` | 4-argument application-state facade calls IPackageManager with op package | `boot-fosframework/disassembly.log:368214-368229; fosservices/disassembly.log:54310-54324` | Strong evidence | runtime PMS trace, tx3 auth, User-0 invocation |
| `P13-ID-003` | 4-argument component-state facade calls IPackageManager | `boot-fosframework/disassembly.log:368254-368263; fosservices/disassembly.log:54300-54309` | Strong evidence | runtime PMS trace, tx3 auth, User-0 invocation |
| `P13-ID-004` | KFT writer uses supplied UserInfo.id for three package/component writers | `fosservices/disassembly.log:54297-54325,54415-54478` | Strong evidence | inherited auth, service permission, SELinux client allow, PMS gate |
| `P13-EXP` | Exported component inventory is not a route without permission, identity, user and sink closure | `work/luna_worker_phase13_exported_inventory_20260810.csv` | Probable | component-specific caller and sink closure |
| `P13-PC` | Parental/card paths close to UI/card/DPM workflows, not arbitrary HOME/package writers | `work/luna_worker_phase13_policy_card_closure_20260810.csv` | Strong evidence | runtime grants and complete policy call graph |
| `P13-DRV` | Seven driver surfaces retain missing caller/policy/identity/validation/effect edges | `work/luna_worker_phase13_driver_join_20260810.csv` | Unknown | compiled delivery, merged policy, native caller and effect |

## Worker CSV shape and hashes

| Input | Rows | Columns | Malformed rows | SHA-256 |
|---|---:|---:|---:|---|
| `kft` | 14 | 12 | 0 | `367bc9a672ca869692ce866db3814bf90e11f73d1b4399a701f4043b0d781faf` |
| `exported` | 23 | 15 | 0 | `65cc971f6b2415b4e9b20481f5ab87083b881eb1363ed0f9a5b5b77ba4f17db1` |
| `driver` | 7 | 15 | 0 | `1178429d2bbec4bf3dc980a09858ef9ce321580300fb15224284759f6924db7e` |
| `policy-card` | 8 | 13 | 0 | `43f3d763b4cfd516785b5ddd13d62355bb5a370a842a655b3ab50160cd3012aa` |

## Baseline and identity inputs

- Phase 12 baseline manifest: `dc8b8e551d63692885ec59990895d20d60bfe2319e886700803ff3028e1196e9`
- Phase 12 post-host guard manifest: `6ea5eca0828a747539937aea698eda91629f7bf1688a444804a0d034116ac040`
- Normalized Phase 13 table: `8d37326d55c6e93bbb83a888dc95ed6714467784f692f1539cd5d7b4895e9418`
- The manifest under `firmware/manifests/PHASE13-HOST-ANALYSIS-20260810/` records all preserved inputs used by the builder.

## Confidence semantics

`Confirmed` is reserved for a directly preserved code/data fact. `Strong evidence` is a bounded static inference whose listed missing edge prevents a reachability or exploit claim. `Unknown` means the corpus did not close the edge. `Disproved` applies only to the specific tested route, never to every possible implementation.
