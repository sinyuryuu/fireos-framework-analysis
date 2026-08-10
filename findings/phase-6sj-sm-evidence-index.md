# Phase 6SJ–SM evidence index

## Device snapshot

| Evidence ID | File | SHA-256 | Result | Confidence |
|---|---|---|---|---|
| 6SJ-DEVICE-001 | `adb/phase6sj/PHASE6SJ-DEVICE-READONLY-20260810T040720Z/public-summary.md` | `6ab3386919b6652a10204f9b7670b8acfcdb706e3e2f1e17b750a850ec038b01` | redacted public summary of the read-only snapshot | Confirmed |
| 6SJ-DEVICE-002 | local-only `home_resolve.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` | Fire Launcher priority 50 | Confirmed |
| 6SJ-DEVICE-003 | local-only `home_candidates.stdout.txt` | `e85ea12c0b49b54392725c6f2f440f7c2b84ae4fdf47f604b9571c17427957e6` | Fire 50, Microsoft 0, FallbackHome -1000 | Confirmed |
| 6SJ-DEVICE-004 | local-only `preferred.stdout.txt` | `ab4c4d71d54faa5b5339dda54f4e3cc14c95a671e71ef1640627adf4c0e2e519` | `mAlways=true` Fire preferred record | Confirmed |
| 6SJ-DEVICE-005 | local-only `firelauncher_package.stdout.txt` | `73cf239df6f218c345fad253d707e852ba50cdbacdefe5a93a91a99456734db5` | User 0 enabled 0, User 10 enabled 2; privileged system package | Confirmed current state |
| 6SJ-DEVICE-006 | local-only `activity.stdout.txt` | `5b24f3f2afab0a937e5c2aaf22549e7a47a6cc73d9d327164a9300c749f44d0d` | resumed activity Fire Launcher | Confirmed |
| 6SJ-DEVICE-007 | local-only `window.stdout.txt` | `7e036609f999f353422eeb09e43d7c9d67cb84915ac6b898a0bba924c2515ad2` | current focus Fire Launcher | Confirmed |
| 6SJ-DEVICE-008 | local-only `sha256sums.txt` | `5891cff99f4a12a5064914c98d278c0dc13e7598351b041f464588ed4557f2bf` | all saved local snapshot files verify | Confirmed |

All 17 capture commands returned exit code 0. The command list is reproducible by
`tools/scripts/capture_phase6sj_readonly.sh`; it requires an explicit serial and supports
`--dry-run`.

The complete snapshot remains local-only because its secure-settings output contained an
Amazon account identifier. The public commit contains only `public-summary.md`.

The raw SJ worker CSV retains its original locator field. For `SJ-01`, direct verification
of the cited file/hash places the permission declaration at XML lines `1822-1824` (the raw
worker locator says `1936-1938`); the normalized finding uses the verified locator.

## Worker evidence

| Evidence IDs | Worker CSV | Rows | CSV SHA-256 | Narrative SHA-256 |
|---|---|---:|---|---|
| SJ-01–SJ-10 | `work/luna_worker_phase6sj_ipc_permission_20260810.csv` | 10 | `299047e59ad29c35392e9df1492138b323a9f242b27e7c19e98ecbcc154946c4` | `b20d4d9d8d27de550c569e8e92458ee3e7b46a887f03b7293693ecaa78639204` |
| 6SK-001–6SK-014 | `work/luna_worker_phase6sk_ota_recovery_20260810.csv` | 14 | `c72a6b61138d589ea9ec76ed99cdbff86d2bf2cb9049ece1a88d107feaa9af22` | `833f885ff68ebae52974fd381b5710c12bcd441227d12f019b9ccb83b4763abe` |
| 6SL-001–6SL-007 | `work/luna_worker_phase6sl_driver_callers_20260810.csv` | 7 | `748ec784a3e360a9c38d43f4d6ff248a099289ccc6018e1f6c04361d22a705d2` | `f1e25b4bbe4d9a4c4cc26ecd034d897306eb7af98386827d273f4060ff2e7e35` |
| P5-BASELINE…P6-REFUSED | `work/luna_worker_phase6sm_test_catalog_20260810.csv` | 19 | `199889eff3ecab08c8e901ff0b1c38f57bde4777d28e27da779f7bcb6a59c21e` | `a375bddb01c6ebe2f6d291a013f328c82c346c37d960bcfd83ad832e692ef34e` |

## Normalized output

`output/tables/phase6sj-sm-control-surface.csv` contains 50 rows and 14 columns.
Its SHA-256 is `eb48603b238d9c703f1d176d84dbf0f7631c65fc14bb3640effec68a08e95e3f`.
The fixed input manifest is `output/tables/phase6sj-sm-input-manifest.sha256`, SHA-256
`47ebd3bbe2871095b55ccc00772651e908c2224ced67b8469bda0b4266b15c06`.

## Safety classification

- `CONFIRMED`: preserved source/runtime fact only.
- `UNKNOWN`: bounded corpus does not close the relevant holder, caller, user scope or
  native dispatch.
- `OBSERVED-CAPABILITY`: static capability without live reachability.
- `NEGATIVE-BOUNDARY`: no route found in the bounded corpus; not universal absence.
- `REJECTED`: not executed because it could mutate the device, invoke privileged code or
  cause loss of recovery.
