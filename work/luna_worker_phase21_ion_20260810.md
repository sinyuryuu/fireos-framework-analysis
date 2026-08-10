# Phase 21C — ION loader provenance

日期：2026-08-10（Asia/Taipei）

輸入是 `P20D-ION-003`。本輪只讀 preserved PS7331 ELF、DT_NEEDED、relocation、`nm`/`objdump`/string-based `dlopen` evidence、init/VINTF、file_contexts/CIL 與既有 display/media graph。禁止且未執行任何 `/dev` open/read/write/ioctl、proc/sysfs/debugfs 操作、module、root、Binder 或實機操作。

## 結論

ION 的可重現 host-side graph 現在可分成三層：

1. `gralloc.mt8183.so`、`hwcomposer.mt8183.so`、`lib_uree_mtk_modular_drm.so` 與 `libstagefright.so` 的 ION dependency/relocation/library edges 已確認。
2. allocator/composer/media/camera/surfaceflinger 的 init ownership、UID/group 與 VINTF HAL contracts 已接上；但 service executable 不直接 NEEDED 對應 implementation，故 service→implementation load 仍 UNKNOWN。
3. gralloc 內部存在 `dlopen`/`dlsym`，target string 是 `gralloc.mt6771.so`，而 shipped file 的 SONAME 是 `gralloc.mt6771.so`、檔名是 `gralloc.mt8183.so`；這證明 loader intent，不證明 target resolution、constructor 或 runtime ION consumer。

因此 P20D-ION-003 仍不能提升為完整 `process → loader → ION → downstream effect` closure。最強分類是 `POSITIVE_ELF_LIBRARY_EDGE`、`POSITIVE_DLOPEN_INTENT_ONLY`、`UNKNOWN_SERVICE_LOAD`、`UNKNOWN_RUNTIME_LOAD` 與 `UNKNOWN_PROCESS_CHAIN`；ION node/policy row 保留 `BOUNDED_STATIC_POLICY_ONLY`。沒有任何 row 指向 PackageManager、ActivityManager、SettingsProvider、Fire Launcher、HOME 或 privilege transition。

## Graph

```text
init/VINTF
  ├─ vendor.gralloc-2-0 (system; hal_graphics_allocator_default)
  │    └─ implementation load → gralloc.mt8183.so : UNKNOWN
  │         ├─ NEEDED libion.so + libion_mtk.so : POSITIVE ELF EDGE
  │         └─ dlopen/dlsym gralloc.mt6771.so : INTENT ONLY
  ├─ vendor.hwcomposer-2-1 (system; hal_graphics_composer_default)
  │    └─ implementation load → hwcomposer.mt8183.so : UNKNOWN
  │         └─ NEEDED libion.so + libion_mtk.so : POSITIVE ELF EDGE
  ├─ media (media; mediaserver)
  │    └─ mediaserver → libmediaplayerservice → libstagefright → libion : runtime UNKNOWN
  ├─ cameraserver (cameraserver; mtk_hal_camera candidate) : process chain UNKNOWN
  └─ surfaceflinger (system) : display consumer candidate, loader chain UNKNOWN
```

## Ownership and policy

- Allocator service: `/vendor/bin/hw/android.hardware.graphics.allocator@2.0-service`, `user system`, groups `graphics drmrpc`, capability `SYS_NICE`; VINTF allocator contract is present.
- Composer service: `/vendor/bin/hw/android.hardware.graphics.composer@2.1-service`, same system/graphics/drmrpc ownership and `SYS_NICE`; VINTF composer contract is present.
- Media: `/system/bin/mediaserver`, user `media`; camera: `/system/bin/cameraserver`, user `cameraserver`; surfaceflinger: `/system/bin/surfaceflinger`, user `system`.
- `/dev/ion` file_contexts maps to `ion_device`; merged CIL allows several graphics/MTK domains. These are authorization edges only. No selected trona DTB/DTBO or complete built-in/module/heap manifest was found, so source registration and config are not promoted to delivery.

## Downstream sink boundary

The static downstream effects are restricted to graphics buffers, display composition, media/DRM shared memory, camera buffers and DMA/heap state. The corpus does not join any of these to a package-state writer, HOME resolver, launcher replacement, or privilege transition. DT_NEEDED and relocation prove link-time edges; `dlopen` plus a target string proves loader intent; init/VINTF and CIL prove ownership/contract/policy potential, not invocation.

## Evidence anchors

- Input reconciliation: `work/luna_worker_phase20_reconciliation_20260810.md` (`P20D-ION-003`).
- Canonical prior loader graph: `work/luna_worker_phase6tn_ion_loader_graph_20260810.{md,csv}`.
- ELF set: `artifacts/phase9/ps7331-runtime-binary-audit-20260806-01/{vendor-lib64/lib64/hw/gralloc.mt8183.so,vendor-lib64/lib64/hw/hwcomposer.mt8183.so,vendor-lib64/lib64/lib_uree_mtk_modular_drm.so,system-lib64/lib64/libstagefright.so,system-bin/bin/mediaserver}`.
- Init/VINTF/policy: Phase 6C allocator/composer/media/camera/surfaceflinger rc files, Phase 5 compatibility vendor manifest, and Phase 6C plat/vendor file_contexts/CIL.

CSV contains 9 unique `P21C-*` rows. It does not repeat the already-closed ION generic/MTK library-to-node rows; it records only loader, ownership, policy, downstream and remaining provenance edges.
