# Phase 5AC evidence index

| Evidence ID | File / source | Observation | Classification |
|---|---|---|---|
| P5AC-DEVICE-001 | findings/phase-5r-mtk-root-route-review.md | Exact device is KFTRWI/trona/MT8183/PS7330, flash locked | 已證實 |
| P5AC-MTK-001 | artifacts/phase5/mtkclient-android-route-review-20260804-01/brom-config-excerpt.txt | Public mtkclient shared profile names MT8183 but uses dacode=0x6771 | 已證實，source-scoped |
| P5AC-MTK-002 | same excerpt | No independent 0x8183 key | 已證實，source-scoped |
| P5AC-MTK-003 | findings/phase-5r-mtk-root-route-review.md, findings/phase-5f-exact-cmdq-source-followup.md | No exact Amazon loader/auth bundle; PS7331 boot artifacts are version mismatch | 已證實 |
| P5AC-MTK-004 | fixed public mtkclient README | Public tool documents BROM/root/read/write/erase operations | 已證實，scope only |
| P5AC-APK-001 | adb/phase5/PHASE5AB-PENDINGINTENT-T01/metadata.tsv | Self-built redirect APK SHA-256 and alias APK SHA-256 recorded | 已證實 |
| P5AC-APK-002 | adb/phase5/PHASE5AB-PENDINGINTENT-T01/accessibility_after_install.stdout.txt | Accessibility services remained empty after install | 已證實 |
| P5AC-APK-003 | adb/phase5/PHASE5AB-PENDINGINTENT-T01/before/package/home_resolve.stdout.txt | HOME resolver remained Fire Launcher | 已證實 |
| P5AC-APK-004 | tools/phase4-accessibility/dist/20260804-pendingintent-jdk17-01/ | APK v3 signature verified with OpenJDK 17 toolchain | 已證實，host-scoped |
| P5AC-RISK-001 | artifacts/phase5/mtkclient-android-route-review-20260804-01/commands.txt | BROM/DA/flash/ioctl operations explicitly not run | 已證實 |
