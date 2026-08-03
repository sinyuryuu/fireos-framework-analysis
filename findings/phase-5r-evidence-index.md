# Phase 5R evidence index

| Evidence ID | Source | Observation | Interpretation | Confidence |
|---|---|---|---|---|
| `P5R-BASE-001` | read-only ADB check, 2026-08-04 | Device is `KFTRWI/trona`, MT8183, PS7330.4104N, green, `flash.locked=1`, SELinux enforcing, HOME Fire, ADB `device` | Current target remained unchanged | 已證實，snapshot-scoped |
| `P5R-MTKSU-001` | `artifacts/phase5/mtk-easy-su-current-review-20260804-01/repo-metadata.tsv` | KoCleo fork pinned at `8c6871ac...`; LFS `mtk-su64` OID is `328632e853ff...` | Public fork identity is reproducible | 已證實，public-source scope |
| `P5R-MTKSU-002` | `adb/phase5/MTK-SU-CMDQ-T03/host/mtk-su64` | Local executed binary SHA-256 is `328632e853ff...` | KoCleo current `mtk-su64` is the same payload already tested | 已證實，hash scope |
| `P5R-MTKSU-003` | KoCleo `ExploitHandler.kt` and manifest metadata | Wrapper extracts native assets, invokes Magisk boot script, runs shell commands, and checks `/sbin/su`; no exact KFTRWI target | Wrapper behavior is not device compatibility proof | 已證實，source scope |
| `P5R-FENRIR-001` | public `fenrir` README and existing source metadata | Supported list has no `trona/KFTRWI`; project targets MediaTek secure boot chain and warns of permanent damage | No exact target support for a live test | 已證實，public-source scope |
| `P5R-LK-001` | `findings/phase-5b-brom-identification-level3-report.md`; `P5-LK-005` | Exact PS7330 LK read denied; no matching recovery set | LK patch route lacks required input/recovery evidence | 已證實 |
| `P5R-LK-002` | `findings/phase-5-exact-ota-and-boot-chain-evidence.md` | Available boot-chain files are PS7331 and marked `VERSION_MISMATCH` | Adjacent image must not be used as PS7330 write input | 已證實 |
| `P5R-HACKMD-001` | user-provided HackMD, public-source review | List mixes Qualcomm, OPlus/MediaTek, modern kernel and boot-chain cases | It is a lead index, not exact-device authorization | 已證實，scope-scoped |
| `P5R-DECISION-001` | `findings/phase-5r-mtk-root-route-review.md` | No new exact target payload was identified; same mtk-su was not repeated | No new live Level 3 operation was justified in this turn | 已證實，decision scope |
