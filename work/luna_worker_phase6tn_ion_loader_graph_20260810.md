# Phase 6TM-B — host-only ION service/HAL loader graph

日期：2026-08-10。範圍限 host-side Phase 9 ELF artifacts、Phase 6C init rc/SELinux、Phase 5 HAL manifests 與 Phase6TK。未接觸設備；未執行 open/ioctl、Binder、root/exploit、reboot 或 mutation。

## 結論

Phase 9 證實 gralloc、hwcomposer、UREE DRM 與 libstagefright 的 DT_NEEDED/relocation/library-call edges；init rc 證實 allocator/composer/camerahalserver/media/camera processes 及 UID；file_contexts/CIL 證實 executable/library/device labels 與 policy surface。但 service executable 的 DT_NEEDED 不直接包含 gralloc.mt8183.so 或 hwcomposer.mt8183.so，host artifact 也沒有足夠的 service source/loader trace/完整 implementation mapping 證明 exact service → implementation load。

判定：`gralloc.mt8183.so` → ION 為 `POSITIVE_ELF_LIBRARY_CALLER`，且 ELF 有 exact `dlopen`/`dlsym` symbols，target string `gralloc.mt6771.so`，故 `POSITIVE_ELF_EXACT_DLOPEN_TARGET`；target SONAME 不同於 shipped filename，不能推導成功載入。`hwcomposer.mt8183.so` → ION 為 `POSITIVE_ELF_LIBRARY_CALLER`，但 service-to-library edge `UNKNOWN`。UREE DRM 有 `dlopen`，但 KM target/owner process 未完整解析。`libstagefright.so` → `libion.so` 是 `POSITIVE_TRANSITIVE_ELF_EDGE`，但 mediaserver → libstagefright 仍 `UNKNOWN_RUNTIME_LOAD`。完整 `process → loaded implementation → ION callsite → /dev/ion → downstream effect` chain 維持 `UNKNOWN`。

## Loader graph

```text
init rc
  ├─ vendor.gralloc-2-0 (system, hal_graphics_allocator_default)
  │    └─ service NEEDED allocator interface
  │         └─ implementation load → gralloc.mt8183.so : UNKNOWN
  │              ├─ NEEDED libion.so + libion_mtk.so
  │              └─ dlopen/dlsym → gralloc.mt6771.so : ELF-exact, success UNKNOWN
  ├─ vendor.hwcomposer-2-1 (system, hal_graphics_composer_default)
  │    └─ implementation load → hwcomposer.mt8183.so : UNKNOWN
  │         └─ NEEDED libion.so + libion_mtk.so
  ├─ camerahalserver (cameraserver, mtk_hal_camera) : ION chain UNKNOWN
  ├─ mediaserver (media, mediaserver)
  │    └─ libmediaplayerservice → libstagefright → libion : runtime load UNKNOWN
  └─ surfaceflinger (system, surfaceflinger) : allocator implementation/ION load UNKNOWN
```

## Evidence matrix

| edge / node | UID / domain | offset/line and method | result / effect |
|---|---|---|---|
| gralloc → ION | system / hal_graphics_allocator_default candidate | `0x1fe10, 0x1fe48, 0x1fe50, 0x1fe68, 0x1fe70, 0x1ffe8`; DT_NEEDED + relocation + nm/objdump | POSITIVE ELF caller; alloc/sync/import/free/custom only |
| gralloc internal loader | same candidate | `dlopen 0x127b`, `dlsym 0x12cb`, target `gralloc.mt6771.so 0xcb6`; strings + symbol inspection | POSITIVE exact ELF edge; success/process UNKNOWN |
| hwcomposer → ION | system / hal_graphics_composer_default candidate | `IONDevice 0xae010`, relocations `0xafe80–0xafea8`; DT_NEEDED + relocation + nm/objdump | POSITIVE ELF caller; map/import/share/free only |
| allocator service → gralloc | system / hal_graphics_allocator_default | rc line 1; service NEEDED only allocator interface; VINTF vendor manifest lines 92–100 | UNKNOWN service load |
| composer service → hwcomposer | system / hal_graphics_composer_default | rc line 1; service NEEDED only composer interface; VINTF vendor manifest lines 102–109 | UNKNOWN service load |
| camerahalserver | cameraserver / mtk_hal_camera | rc lines 1–6; vendor contexts line 59; no expected Phase9 camerahalserver ELF | Process identity positive; ION chain UNKNOWN |
| mediaserver → libstagefright → ION | media / mediaserver | rc lines 1–6; mediaserver NEEDED `libmediaplayerservice`; libstagefright NEEDED `libion`; DT_NEEDED closure | Transitive possibility only; runtime load UNKNOWN |
| camera/media/surfaceflinger consumers | cameraserver, mediaex, system domains | rc lines 1–4; plat contexts lines 360,367,386,388; ELF NEEDED inspection | Candidate consumers, not invocation proof |
| hwservicemanager | system / hwservicemanager | rc lines 1–10; HIDL/VINTF symbols; no gralloc/hwcomposer NEEDED | Manager/registration role only |
| `/dev/ion` and library labels | platform/vendor domains | plat contexts line 226; vendor contexts lines 198,277,280,293; CIL search | Authorization/label surface only |

## Interpretation and boundary

DT_NEEDED proves a link-time dependency; relocation proves an imported slot; neither proves top-level service execution. `dlopen` plus a target string proves an ELF-contained loader intent/edge, not target resolution, constructor execution, caller process or ION ioctl. SELinux allow rules and VINTF registration prove authorization/contract potential, not invocation. No device contact, Binder, open/ioctl, root/exploit, reboot, write, install, policy change or other mutation was performed. Keep process-level and downstream result `UNKNOWN`.

## Input SHA-256 / provenance

The companion CSV contains one row per selected input/edge with SHA256, offsets/lines and method. It covers Phase6TK MD/CSV; Phase 9 ELF binaries; Phase 6C init rc, plat/vendor file_contexts and CIL; and Phase 5 vendor/system HAL manifests. A future conclusion requires authorized complete host loader/source mapping plus separately captured read-only runtime maps/call evidence.
