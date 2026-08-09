# Phase 6N evidence index

| Evidence ID | Source | SHA-256 / identity | Observation | Confidence |
|---|---|---|---|---|
| 6N-SRC-001 | `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea` | Amazon PS7331 GPL source archive used as input | Confirmed |
| 6N-SRC-002 | `firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4` | build-selected MT8183 4.4 tree | Exact kernel source scope selected; alternate generic/emc copies excluded | Confirmed |
| 6N-SCAN-001 | `tools/scripts/index_phase6n_kernel_user_surfaces.py` | `84a4b9785ce4bd20af334f36ffa1bef8350d322c5073b84e305d8b8b021f57f4` | Host-only scanner supports `--dry-run` and reads source text only | Confirmed |
| 6N-SCAN-002 | `output/tables/phase6n-kernel-user-surfaces.csv` | `67769dad8aceee106331acdeff299c89af60771b540f8bcda5b1bcd6ef1b0448` | 4,278 markers across 343 files | Confirmed |
| 6N-CMDQ-001 | `.../drivers/misc/mediatek/cmdq/v3/cmdq_driver.c:660-741` | source line references | ioctl/compat ioctl and device registration exist; no source-level caller gate observed | Confirmed source observation |
| 6N-ION-001 | `.../drivers/staging/android/ion/ion.c:1478-1658` | source line references | ION ioctl and user-copy paths exist; no source-level caller gate observed | Confirmed source observation |
| 6N-GED-001 | `.../drivers/misc/mediatek/gpu/ged/src/ged_main.c:271-411` | source line references | GED ioctl/proc query surface exists | Confirmed source observation |
| 6N-AMZ-001 | `platform/device/amazon/kernel/driver/amzn_idme.c:316-347` | source line references | IDME write bits are stripped and secure entry is restricted | Confirmed source observation |
| 6N-LIVE-001 | `findings/phase-6ga-p5-vendor-driver-closure.md` | report SHA `fb161723e3e39a7e2997236e36cb4deaab3b658e26789b3c3aa641eef053ed2e` | Existing live review found no driver-to-AMS/ATMS/PMS/HOME edge | Strong evidence |
| 6N-LIVE-002 | `findings/phase-6ha-p5-driver-reaudit-ged-cmdq-boundary.md` | report SHA `681f0da9560779628d1de53cb0cf1416e6737b1634b156f7877304c1ae66bd41` | GED query-only evidence; CMDQ malformed path not executed | Confirmed |
| 6N-LIVE-003 | `findings/phase-6br-amazon-kernel-user-surfaces.md` | existing Phase 6BR evidence | Amazon lifecycle/IDME/logger/liquid/debug boundaries restrict shell access | Strong evidence |

| 6N-LIVE-004 | `adb/phase6n/PHASE6N-KERNEL-RO-20260810-01/` | `sha256sums.txt` SHA-256 `eb9c347abddd4edc603b6d70fd71b5ce9c73393d92dd4d3475369f05bb50a078` | Fresh read-only capture: enforcing/green/4.4.146+, Fire HOME priority 50 | Confirmed |

All interpretations are limited to the stated source scope and saved runtime
evidence. No entry in this index is an exploit claim.
