# Phase 6UH evidence index

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

## 6UE H2 missing candidates

Report SHA-256: `3088ca5ac2b0ca8682c40f3d9374933e1106169e5ac82f16e5fa1e715a838c48`

CSV SHA-256: `1df5c08e36c1c752c25a9388ace6d494828b8b946a01daa23b25a83c3c679423`

Sources: `work/luna_worker_phase6ue_h2_missing_candidates_20260810.md`, `work/luna_worker_phase6ue_h2_missing_candidates_20260810.csv`

## 6UF KFT tx3 gate

Report SHA-256: `04cb8f5c74966ad94c0dbdf9de3dc60b03f5c349632321a92e7e6b6f20d2075b`

CSV SHA-256: `9a14b249b8741918de259d186dbc22509c8862e39ab55aeab005c7fa5688b833`

Sources: `work/luna_worker_phase6uf_kft_gate_20260810.md`, `work/luna_worker_phase6uf_kft_gate_20260810.csv`

## 6UG permission parser

Report SHA-256: `86f9940ae703a03b1ee6fae76d33fc30d797777d4bc811a1fa026c1e64a93b85`

CSV SHA-256: `396f9990baadef8cebffaceca53cf8852cc88f556b942950757c2571bb4809d1`

Sources: `work/luna_worker_phase6ug_permission_parser_20260810.md`, `work/luna_worker_phase6ug_permission_parser_20260810.csv`

## Integrated evidence rules

- `CONFIRMED`: exact-build declaration, owner artifact, or bounded compiled branch is shown.
- `STRONG_STATIC`: a caller/sink or grant edge is shown but an external/runtime edge is missing.
- `UNKNOWN`: the bounded corpus lacks the required caller, service-manager, parser, or downstream edge.
- `NEGATIVE_BOUNDED`: no edge was found in preserved artifacts; it is not a universal absence proof.
- No row authorizes a live private Binder call, state mutation, driver operation, or exploit.
