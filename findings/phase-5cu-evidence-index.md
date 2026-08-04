# Phase 5CU evidence index

日期：2026-08-04。全部為明確 serial `G001LT0511550CFT` 的唯讀查詢或 APK／
policy pull；沒有修改裝置、執行 futex、觸發 race、開 device node、讀寫
核心記憶體或執行 root payload。

| Evidence ID | Source | File / SHA-256 | Observation | Confidence |
|---|---|---|---|---|
| `P5CU-001` | system_server process | `adb/phase5/PHASE5CT-SECCOMP-20260804-01/device-status.txt` / `310c6760f3e241eddca75166875bdaac4ef7d4afb18104fb921e6a3988882a02` | UID 1000, `Seccomp: 2` | Confirmed, process snapshot |
| `P5CU-002` | Microsoft Launcher process | same raw file | UID 10178, `Seccomp: 2` | Confirmed, process snapshot |
| `P5CU-003` | research APK processes | same raw file | redirect／alias processes UID 10189／10190, `Seccomp: 2` | Confirmed, process snapshot |
| `P5CU-004` | adbd | same raw file | UID 2000, `Seccomp: 0`, no capabilities | Confirmed, process snapshot |
| `P5CU-005` | system seccomp policies | `system-mediacodec.policy` / `ee90974989c392ad6e3e343802bca4769dca4d7ba82ecdf04e0f6ada2806ef7e`; `system-mediaextractor.policy` / `fcb93275617f3d683826d0c941c6d6787defa12653ee704f2b7e6d802c4972d3` | Both contain `futex: 1` | Confirmed, service policy scope |
| `P5CU-006` | vendor configstore policy | `vendor-configstore@1.1.policy` / `3525a280a99e6c9f8c191f231cb56709080bcef0bfd35e6c33f368c45f7b3ade` | Contains `futex: 1` | Confirmed, service policy scope |
| `P5CU-007` | policy inventory | `policy-list.txt` / `d37388e86361430684f033b6128c853306fd3c867af0360c9c0d7c7f36648ed3` | Visible policy directory contains service policies; no ordinary app policy file recovered | Unknown app-policy scope |
| `P5CU-008` | Fire runtime | `findings/phase-5cs-fire-art-futex-analysis.md` and `libandroid_runtime.so` evidence | Runtime contains seccomp setup references | Confirmed binary scope; operation policy unknown |
| `P5CU-SAFETY-001` | capture procedure | `commands.txt` / `6dfc0b1649168b02a7859ca4ad53bd363d98b2795d560005eae23273efe1f869` | Only getprop, listing, `/proc` status and read-only pulls | Confirmed safety scope |
