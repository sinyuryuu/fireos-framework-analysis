# Phase 5BS evidence index

| Evidence ID | Source | File | Observation | Confidence |
|---|---|---|---|---|
| `P5BS-SOURCE-001` | PS7331 exact build-selected source | `artifacts/phase5/phase5bs-ps7331-source-semantic-recheck-20260804-01/ps7331.json` | `current->pi_blocked_on`, no `waiter->task`, pre-fix classification | Confirmed, source scope |
| `P5BS-FIXED-001` | Fixed reference source | `artifacts/phase5/phase5bs-ps7331-source-semantic-recheck-20260804-01/fixed-reference.json` | `waiter->task` reference and no current cleanup | Confirmed, reference scope |
| `P5BS-BOOT-001` | Official PS7331 boot image | `firmware/extracted/PS7331/boot.img`; `artifacts/phase5/ps7331-boot-image-inspection-20260804-01/input.sha256` | Boot image hash `cf12e561…` | Confirmed, artifact identity |
| `P5BS-IMAGE-001` | Address-sanitized PS7331 Image analysis | `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/instruction-patterns.csv` | Current-task source/cleanup and proxy call markers | Confirmed, inspected-image scope |
| `P5BS-COMPARE-001` | Source-to-Image semantic comparison | `artifacts/phase5/ps7331-source-binary-semantic-20260804-01/semantic-comparison.json` | PS7331 inspected Image consistent with pre-fix source | Confirmed, inspected-image scope |
| `P5BS-VERIFY-001` | Host-only verifier | `artifacts/phase5/phase5bs-ps7331-evidence-verification-20260804-01/verification.json` | All identity/marker/safety checks passed | Confirmed, verification scope |
| `P5BS-SAFETY-001` | Phase 5BS command ledger | `artifacts/phase5/phase5bs-ps7331-evidence-verification-20260804-01/commands.txt` | No code execution, device I/O, exploit or payload | Confirmed |

The index does not prove runtime exploitability, privilege gain, or a working
root PoC.
