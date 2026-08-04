# Phase 5BI evidence index

| Evidence ID | Source | File / URL | Observation | Confidence |
|---|---|---|---|---|
| `P5BI-PUBLIC-001` | KoCleo public source review | `artifacts/phase5/mtk-easy-su-current-review-20260804-01/repo-metadata.tsv` | Pinned wrapper is legacy mtk-su/Magisk route; no exact KFTRWI/trona/MT8183 profile in reviewed scope | Confirmed, public-source scope |
| `P5BI-PUBLIC-002` | KoCleo payload identity | `artifacts/phase5/mtk-easy-su-current-review-20260804-01/repo-metadata.tsv` | Public `mtk-su64` LFS object matches the previously executed payload SHA-256 | Confirmed |
| `P5BI-PUBLIC-003` | Public exploit survey | `https://hackmd.io/@lokey0905/rk-hQSzibl` | Reviewed MTK examples are vendor-specific; no exact Amazon trona profile established | Strong evidence, review scope |
| `P5BI-DEVICE-001` | Exact device baseline | `findings/phase-5az-evidence-index.md` and `adb/phase5/PHASE5X-ROUTE-SURFACE-20260804-03/` | Device is KFTRWI/trona/MT8183, Android 9, PS7330.4104N | Confirmed |
| `P5BI-MTK-001` | Existing exact-device test | `findings/phase-5az-ghostlock-mtk-compatibility.md` and prior `MTK-SU-CMDQ-T03` evidence | Same mtk-su payload failed at critical init step 3; no UID 0; rollback succeeded | Confirmed |
| `P5BI-GHOSTLOCK-001` | Source/config review | `findings/phase-5az-ghostlock-mtk-compatibility.md` | PS7330 source/config overlap is a candidate, not signed-binary or runtime proof | Strong evidence, bounded |
| `P5BI-PS7331-001` | Official OTA mapping | `findings/phase-5bh-ps7331-official-ota-source.md` and `artifacts/phase5/ps7331-official-update-source-20260804-01/` | Official PS7331 package matches local archive and is a full-block OTA | Confirmed |
| `P5BI-PS7331-002` | Source-to-inspected-Image semantics | `artifacts/phase5/ps7331-source-binary-semantic-20260804-01/semantic-comparison.json` | Inspected PS7331 Image is consistent with pre-fix source pattern; exact PS7330 signed binary not proven | Strong evidence, version-scoped |
| `P5BI-DECISION-001` | Upgrade decision | `findings/phase-5bi-mtk-public-route-recheck.md` | PS7331 may be a general security A/B candidate, but standalone boot is not an equivalent update and GhostLock remediation is not demonstrated | Confirmed package identity; Strong evidence for bounded decision |

## Artifact integrity

The derived artifact manifest is:

`artifacts/phase5/mtk-public-route-recheck-20260804-01/sha256sums.txt`

No device state was changed in Phase 5BI.
