# Phase 6MI evidence index

| Evidence ID | Source | SHA-256 | Observation | Confidence |
|---|---|---|---|---|
| 6MI-SOURCE-001 | `artifacts/phase6mi-source-tar-eof-20260810-03/summary.json` | `409ed81ede46db87a0ef8a05cc33b99df2b66e068d1edc1ac481a42e0606169b` | Official PS7331 source tar input hash, 2,563,328,975 bytes, 35 members, real EOF, no errors. | **Confirmed** |
| 6MI-SOURCE-002 | `artifacts/phase6mi-source-tar-eof-20260810-03/source-tar-summary.csv` | `8b577855f3ef674380231c89b65c86d233309d59984ef07fb38601408e9061d9` | 23 regular files, 12 directories, zero symlink/hardlink members; no extraction/execution/device mutation. | **Confirmed** |
| 6MI-OTA-001 | `artifacts/phase6mi-source-tar-eof-20260810-03/sensitive-member-hits.tsv` | `bbaacc3dfa337cfca20953ee3386ee037e84174b8d580203247a4194e8201867` | Two hits are only `apps/com.amazon.firelauncher` and its dependency path; zero OTA/update/post-install/file-mutation hits. | **Confirmed** |
| 6MI-GRAPH-001 | `output/call-graphs/phase6mi-source-tar-flow-20260810-03.mmd` | `46021cbad481ec3fdabd10f0164494e65027df08cb802450cba4bdca13719714` | Outer archive → nested source payload graph; no executable update branch. | **Confirmed** |
| 6MI-FIRE-001 | `artifacts/phase6ap/denylist-resource-closure-20260805-01/res/raw/package_manager_deny_list.json:6` | `16086fecbfce0a20c0b37535e25d690635d398b30d582fa6d231736dc9bdf710` | Static PS7331 deny-list resource contains `com.amazon.firelauncher`; this supersedes the earlier membership-pending wording. | **Confirmed** |
| 6MI-BOUNDARY-001 | `findings/phase-6bp-ota-post-install-path-audit.md` and `findings/phase-6fe-ota-top-level-postinstall-boundary.md` | See referenced artifact manifests | Signed PS7331 installation BIN remains a fixed image/partition update path; source tar is not a safe post-install route. | **Strong evidence** |

## Safety record

`adb_used=false`, `ota_executed=false`, `recovery_used=false`,
`binder_transaction_sent=false`, `extracted=false`, `executed=false`, and
`device_mutation=false` for this phase.
