# Phase 6UD evidence index

## 6UA H2 grant/client

Report SHA-256: `76f847a4b3842874870e88d02f35b117ee075ed39608ce1c1e6e12d731e33ac9`

CSV SHA-256: `19ff5c49265689cb0d0e64324760c29c85e1e34c86134b349e7f89bd2a95d306`

Sources: `work/luna_worker_phase6ua_h2_grant_client_20260810.md`, `work/luna_worker_phase6ua_h2_grant_client_20260810.csv`

## 6UB KFT caller/scope

Report SHA-256: `985baf87524b8c11746268ee861e430e9fc5ac26594268107cbc9f2dc4f858c4`

CSV SHA-256: `03a5b7c38a1ab02f38a49e5d3c16e611e2ce72c1d056cc36a8de85b84d287f19`

Sources: `work/luna_worker_phase6ub_kft_caller_scope_20260810.md`, `work/luna_worker_phase6ub_kft_caller_scope_20260810.csv`

## 6UC Amazon permission semantics

Report SHA-256: `f101c66f0d13e83ffadaa6cf0a718d23e084bb09016426263c5a38f2a05051a2`

CSV SHA-256: `37dcc749b5fff557bc3612eab502b696ec044647ea88f914022d5c9974a84aba`

Sources: `work/luna_worker_phase6uc_amazon_perm_semantics_20260810.md`, `work/luna_worker_phase6uc_amazon_perm_semantics_20260810.csv`

## Context

- `findings/phase-6tz-report.md`: `fb73aebc8abcbc14f3e8877387511bc74b29936f9f584aef548f716d2749aa5e`
- `findings/phase-6tz-evidence-index.md`: `4cd86a7b6c63fd5491e21efec0fbb1cb787aa00278f983675e118ecda32173ad`
- `output/tables/phase6tz-control-surface.csv`: `a06b6616b63659ef53883aae21d62d867787005bdf6159255f2cfbc9550c9361`
- `findings/phase-6tv-report.md`: `e766794a9683923e11a723e11d4e1b772512212745699f8e071e5ac0bb4cd31f`

## Labels

- `CONFIRMED`: exact static declaration, owner record or caller/scope edge is shown.
- `STRONG_STATIC`: bounded grant/writer edge is shown, with a missing external/runtime edge.
- `UNKNOWN`: bind client, parser semantics, permission eligibility or cross-user gate is missing.
- `NEGATIVE_BOUNDED`: no edge in the preserved corpus; not a universal absence proof.
