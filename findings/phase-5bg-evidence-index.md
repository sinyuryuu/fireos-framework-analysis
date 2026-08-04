# Phase 5BG evidence index

| Evidence ID | File | SHA-256 | Observation | Confidence |
|---|---|---|---|---|
| `P5BG-SOURCE-001` | `artifacts/phase5/ghostlock-source-semantics-20260804-01/mt8183.json` | `3a02f57d3aeb548948666d7feda4e9121cdc3dff67998f637db6257e67225ba2` | PS7331 build-selected source has pre-fix current-task cleanup and proxy call | Confirmed, source scope |
| `P5BG-IMAGE-001` | `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/instruction-patterns.csv` | `0ee3da7513051f2fa32b221918c6e671bc78b2a8e192fa0ab7ad65cc6e53475d` | Inspected PS7331 Image has current-task source/clear and proxy call patterns | Confirmed, inspected-function scope |
| `P5BG-FIX-001` | `artifacts/phase5/public-source-review/linux-rtmutex/linux-stable-v6.1.175.c` | `c307ed54156d1f16e82387df7b214445dddf27be8a880f31575f698ca07d880a` | Fixed reference uses `waiter->task` cleanup and no current cleanup in function | Confirmed, reference scope |
| `P5BG-MODEL-001` | `artifacts/phase5/ps7331-source-binary-semantic-20260804-01/semantic-comparison.json` | `c1b9e09cdc058f07776de2615491c38f4890cfbd5f2e526f02fd6a1a0d8156c3` | Machine verdict: PS7331 inspected Image is consistent with pre-fix source | Strong evidence, version-scoped |
| `P5BG-BOUNDARY-001` | `artifacts/phase5/ps7331-source-binary-semantic-20260804-01/semantic-comparison.json` | `c1b9e09cdc058f07776de2615491c38f4890cfbd5f2e526f02fd6a1a0d8156c3` | Exact PS7330 signed binary, runtime exploitability and privilege gain remain unproven | Confirmed boundary |

No device or boot state was changed.
