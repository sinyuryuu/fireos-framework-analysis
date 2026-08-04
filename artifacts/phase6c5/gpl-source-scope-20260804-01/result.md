# PS7331 GPL source scope verification

Host-only coverage audit. No source was built or executed and no device was contacted.

Source root: firmware/extracted/PS7331-SOURCE-20250617

## Result

- platform/system/core/init present: **False**
- kernel futex.c present: **True**
- kernel rtmutex.c present: **True**

**已證實：** this tarball contains the selected MT8183 4.4 kernel source and Amazon device/kernel support, but the expected Android system/core/init directory and selinux.cpp are absent. The named-match table records any remaining SELinux/rootable filenames without treating them as init source.

**高可信推論：** the GPL package cannot directly provide Amazon's /init policy-loader source diff; the stripped /init and AOSP anchor remain necessary for that pipeline.

**待驗證：** whether Amazon's private build overlay or an unreleased source component supplied the /init changes. This archive alone cannot answer it.

**已排除：** the absence of system/core/init in this archive is not evidence that /init has no Amazon modification.

## Reproduction

python3 tools/scripts/audit_phase6c5_gpl_source_scope.py --dry-run --source-root firmware/extracted/PS7331-SOURCE-20250617 --output artifacts/phase6c5/gpl-source-scope-YYYYMMDD-NN

python3 tools/scripts/audit_phase6c5_gpl_source_scope.py --source-root firmware/extracted/PS7331-SOURCE-20250617 --output artifacts/phase6c5/gpl-source-scope-YYYYMMDD-NN
