# Phase 6VF evidence index

## Worker evidence

- **6VA fosinit residual closure:** `work/luna_worker_phase6va_fosinit_residual_closure_20260810.md` (b9b039d34a6d80e4483ce55bb71c16f3547d09339e9f40e6a2749ab70680fb55); `work/luna_worker_phase6va_fosinit_residual_closure_20260810.csv` (834676c20c53cb7910f2ed56f382fd4d90e0f04c56aaba23433a4b770c3eab2c); 15 row(s).
- **6VB OTA post-install closure:** `work/luna_worker_phase6vb_ota_postinstall_closure_20260810.md` (3489ce7b51e225ac05fa2439df5b2652100aa78a9becd68f719f777f5eb5873b); `work/luna_worker_phase6vb_ota_postinstall_closure_20260810.csv` (4eaeb6302d1fde0752bc052cd9c67b0b5ee1d3bac7f93935352dced1c36d3fd5); 13 row(s).
- **6VC native driver caller/policy closure:** `work/luna_worker_phase6vc_driver_caller_policy_20260810.md` (dda3425e4d6fca88aab7957689cc94209c0a31c919e455cdfa72379693122433); `work/luna_worker_phase6vc_driver_caller_policy_20260810.csv` (8bb5edcc5b5e1cf0bfb8e45cd14c1e185ac873c4d307e67594c024ccd3b69ad0); 7 row(s).
- **6VD existing-test reconciliation:** `work/luna_worker_phase6vd_test_reconciliation_20260810.md` (b129bdc5a15be77c1430a4a9585d0009d645822e2db9ee37ca5655ef1b85ab9e); `work/luna_worker_phase6vd_test_reconciliation_20260810.csv` (78462b8645a0c05bb134a0bae89a62cf154d0126c4aae24a93afe03d3be8a95e); 19 row(s).
- **6VE Framework IPC sink inventory:** `work/luna_worker_phase6ve_framework_sink_inventory_20260810.md` (9905f33d8cdc858a4bf59cfec8ef24f8d7a763db49f9cc0b33215de94eebae8a); `work/luna_worker_phase6ve_framework_sink_inventory_20260810.csv` (42d609d5d427fb691031e54caf9d25ee62718f9be64f7bf32fbc53d7eb88ab6a); 32 row(s).

## Acceptance rules

- Static capability, registration, package visibility, or a missing local check is not external reachability.
- `UNKNOWN` is bounded missing evidence, not proof of absence.
- A row with a writer must name its identity/user scope before it can support a User-0 conclusion.
- No evidence row authorizes live Binder, driver, OTA/recovery, root, or partition execution.
