# Phase 5BQ evidence index

| Evidence ID | Source | File | Observation | Confidence |
|---|---|---|---|---|
| `P5BQ-DEVICE-001` | Serial-qualified read-only ADB postcheck | `adb/phase5/PHASE5BQ-DEVICE-POSTCHECK-20260804-01/` | PS7330.4104N, 2024-02-01 patch, ADB `device`, HOME Fire Launcher | Confirmed, runtime scope |
| `P5BQ-MTK-001` | Public repository HEAD/README review | `artifacts/phase5/phase5bq-public-route-review-20260804-01/source-heads.tsv` | mtk-easy-su is legacy mtk-su wrapper; no exact target in listed devices | Confirmed, public-source scope |
| `P5BQ-HIJACK-001` | Public source plus existing controlled run | `findings/phase-5ab-evidence-index.md`; `findings/phase-5bd-ota-and-redirect-followup.md` | LauncherHijack is foreground redirect reference; no new APK installed | Confirmed, source/runtime scope |
| `P5BQ-GHOSTLOCK-001` | NVD and Linux stable patch reference | `findings/phase-5bn-ghostlock-current-verdict.md` | Fix changes `current` cleanup/task to `waiter->task` | Confirmed, upstream scope |
| `P5BQ-PS7330-001` | Official exact source archive | `artifacts/phase5/ps7330-full-source-members-20260804-01/` | Build-selected mt8183 source remains pre-fix | Confirmed, source scope |
| `P5BQ-PS7331-001` | Official adjacent boot/source analysis | `artifacts/phase5/ps7331-source-binary-semantic-20260804-01/` | Inspected Image and source remain pre-fix-consistent | Confirmed, inspected-image scope |
| `P5BQ-OTA-001` | Official OTA metadata review | `findings/phase-5bd-ota-and-redirect-followup.md` | Full OTA updates boot plus other partitions/firmware | Confirmed, metadata scope |
| `P5BQ-SAFETY-001` | Phase 5BQ command ledger | `artifacts/phase5/phase5bq-public-route-review-20260804-01/commands.txt` | No exploit, reboot, bootchain, ioctl, or partition operation | Confirmed |

This index does not claim live exploitability, root, or safe upgradeability.
