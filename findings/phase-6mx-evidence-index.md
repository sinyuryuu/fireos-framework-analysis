# Phase 6MX evidence index

- **6MX-E01** — Static service publication and handle inventory; see `artifacts/phase6mx-amazon-pm-callers-20260810-01/caller-calls.csv` and its input manifest. Confidence: **Strong evidence**.
- **6MX-E02** — IAmazonPackageManager method set contains no HOME/preferred/enabled-state setter. Source: `boot-fosframework/disassembly.log`, interface declaration and method rows. Confidence: **Confirmed static**.
- **6MX-E03** — No ADB, Binder transaction, device mutation, root, or exploit action was performed. Source: script and artifact summary. Confidence: **Confirmed**.
