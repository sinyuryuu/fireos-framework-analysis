# Phase 6UR evidence index

## 6UN native node join

Report SHA-256: `2136d316bd27fc33ef876204ae76148a0af44bc1c867dcc3060a6a2fccf52e34`

CSV SHA-256: `bceef4c32150d91e9b006a251d6cee85931947ad818aaee32d6c18c188d024f0`

Sources: `work/luna_worker_phase6un_native_node_join_20260810.md`, `work/luna_worker_phase6un_native_node_join_20260810.csv`

## 6UO OTA verifier/handoff

Report SHA-256: `ab72c4a8c4afaa643d73ac2f26ee0bd60c8078e7067500a58d37e34c34d70c31`

CSV SHA-256: `555957894258c019fbd30b69385818db507f4d3aae5679ef48d02f696ebcccb2`

Sources: `work/luna_worker_phase6uo_ota_verifier_handoff_20260810.md`, `work/luna_worker_phase6uo_ota_verifier_handoff_20260810.csv`

## 6UP ASP/prewarm closure

Report SHA-256: `1fc7d71c3232bd6122907394ea68665163bae3e3881ee218bcf7804c04479016`

CSV SHA-256: `0f33c86e23ce6c92f5e79c1adef2135736ef90de9a17cd7f4a0dab5192c39c1b`

Sources: `work/luna_worker_phase6up_asp_prewarm_closure_20260810.md`, `work/luna_worker_phase6up_asp_prewarm_closure_20260810.csv`

## 6UQ fosinit completeness

Report SHA-256: `e024c57757729622e0f968f70338a2d453e7a96707577eaa9494947b56cb67ce`

CSV SHA-256: `41a7dd25af6dca212867c7ccf7203d0257bacf406697a7cb8b4bc85deb7a1b04`

Sources: `work/luna_worker_phase6uq_fosinit_completeness_20260810.md`, `work/luna_worker_phase6uq_fosinit_completeness_20260810.csv`

## Acceptance rules

- Capability, registration, or missing method-local checks do not prove external reachability.
- Runtime service listing is not a valid Binder handle or caller authorization.
- `UNKNOWN` is bounded missing evidence, not universal absence.
- No row authorizes live Binder, driver, OTA/recovery or exploit execution.
