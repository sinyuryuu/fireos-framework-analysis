# Phase 3C overlay and runtime-resource analysis

The canonical cmd overlay list contained only internal cutout overlays and
com.android.systemui.theme.dark: adb/phase3c/PHASE3C-BASELINE-20260803-02/overlay/list.stdout.txt.
No mutable Fire Launcher, HOME resolver, or default-home overlay was observed.
No overlay was switched in Phase 3C.

已證實: no relevant enabled overlay was observed in the baseline.
高可信推論: overlay switching is not needed to explain p0's stored-but-unused
preferred record.
待驗證: an overlay in an unlisted partition or another firmware build.
因風險拒絕測試: changing core SystemUI/framework overlays.
