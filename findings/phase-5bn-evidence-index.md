# Phase 5BN evidence index

| Evidence ID | Source | File | Observation | Confidence |
|---|---|---|---|---|
| `P5BN-MARKER-001` | independent host-only rerun | `artifacts/phase5/phase5bn-ghostlock-marker-recheck-20260804-01/summary.json` | PS7330 and PS7331 source markers are pre-fix; fixed reference is waiter-task | Confirmed, source scope |
| `P5BN-MARKER-002` | independent host-only rerun | `artifacts/phase5/phase5bn-ghostlock-marker-recheck-20260804-01/comparison.csv` | Function lines and marker booleans are machine-readable | Confirmed, analyzer scope |
| `P5BN-SOURCE-001` | Amazon official source provenance | `artifacts/phase5/exact-kernel-source-review-20260804-02/metadata.tsv` | Exact PS7330 source member and archive metadata | Confirmed, source scope |
| `P5BN-BINARY-001` | preserved PS7331 image inspection | `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/summary.json` | PS7331 Image shows current-task source and proxy call observations | Confirmed, inspected Image scope |
| `P5BN-URL-001` | read-only HTTP HEAD | `artifacts/phase5/phase5bn-ghostlock-marker-recheck-20260804-01/source-http-headers.txt` | Official PS7330/PS7331 source endpoints returned HTTP 200 | Confirmed, availability scope |
| `P5BN-BOOT-001` | exact-device read-only probe | `adb/phase5/PHASE5AN-BOOT-READONLY-20260804-02/boot_pull.stderr.txt` | Installed PS7330 boot pull returned Permission denied | Confirmed, access scope |
| `P5BN-CVE-001` | NVD and Linux stable patch | `https://nvd.nist.gov/vuln/detail/CVE-2026-43499` | Root cause and remediation semantics are waiter-task cleanup | Confirmed, public reference scope |

No row in this index proves live exploitability, root, runtime offsets, or
successful upgrade.

