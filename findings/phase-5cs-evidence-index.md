# Phase 5CS evidence index

日期：2026-08-04

本輪只分析已由明確 serial、唯讀 ADB pull／listing 取得的 ELF 與檔名清單，
再由主機端執行 `file`、`strings`、`nm`、`objdump -t` 及限定範圍的
`objdump -d`。沒有在平板執行 ELF、futex、race、ioctl、device-node
操作、核心記憶體存取或 root payload。

| Evidence ID | Source | File / SHA-256 | Command or observation | Interpretation | Confidence |
|---|---|---|---|---|---|
| `P5CS-001` | PS7331 device identity | `artifacts/phase5/phase5cs-native-inventory-20260804-01/identity.txt` / `eff54128ec883e000ebc1efc10b90806aa2526bd280557ecffa83051125ab4a2` | `adb -s G001LT0511550CFT shell getprop` | Captured build is `PS7331.4463N/0031575863172`, device `trona`, arm64 | Confirmed, capture scope |
| `P5CS-002` | Native inventory | `system-lib64.txt` / `0fcd041aec74aed4c1c0b3eda6d4007d3e382d8bd72c15a54e05d683b9833b7c`; `vendor-glob.txt` / `11971e54842899dd3aa07c785fa23c56fb4fdcec4d6760dbd6385ab84ef3fb4e` | Read-only directory listing and glob listing | System and vendor native names were recorded; product/system_ext glob expansion was unavailable | Confirmed, inventory scope |
| `P5CS-003` | Fire ART | `/system/lib64/libart.so` / `3a0a7cdc0d8b3634c6b362e0b68d0f05225063eec098fdc7656988139bb9f658` | Host `strings`, `nm`, `objdump -t` | Contains `futex cmp requeue failed for`, `ThreadList::SuspendAllInternal`, and an imported `syscall` | Confirmed, binary scope |
| `P5CS-004` | Fire ART disassembly | Local generated `artifacts/phase5/phase5cs-native-analysis-20260804-02/libart-suspendall-disassembly.txt` / `35e60900cc5a86771ab00a198660bd812c7188d3a3ad70da7333119b3779faa4` | Host-only disassembly of the identified ART method | Method reaches the libc `syscall` PLT boundary; no syscall number or argument recipe is treated as evidence | Confirmed, method scope |
| `P5CS-005` | AOSP ART source reference | [AOSP ART `runtime/base/mutex.cc`](https://android.googlesource.com/platform/art/+/e8256e7773a230337c3d137cbf0365f737820405/runtime/base/mutex.cc) | `ConditionVariable::Broadcast` source history | The matching ART diagnostic is associated with ordinary `FUTEX_CMP_REQUEUE`, not PI requeue | Strong evidence, reference mapping |
| `P5CS-006` | Fire Android runtime | `/system/lib64/libandroid_runtime.so` / `73dd8b974989faeaed65d03d548f3a776fd31e65ddb29cdd583dcaeea623d837` | Host string scan | Contains pthread condition symbols and seccomp setup/source-label strings | Confirmed, binary scope |
| `P5CS-007` | Selected Amazon libraries | Hashes recorded in `output/tables/phase5cs-native-inventory.csv` | Host bounded `strings`/symbol scan | No named futex/requeue/rtmutex caller established in the selected Amazon libraries | Negative observation only |
| `P5CS-008` | Fire vendor inventory | `vendor-lib64.txt` / `166a69290007f44fb69f794d2046fe7bb67caad03a95a01dd86e9996a65ce4e7` | Read-only `/vendor/lib64` listing | FireOS HIDL and MediaTek libraries are present; no vendor ELF was executed or bypassed | Confirmed, inventory scope |
| `P5CS-009` | Restricted artifacts | `/system/bin/amazonfiled`, product/system_ext detailed listings | Pull/stat or glob access was denied or unavailable | These paths remain unanalysed; no permission bypass was attempted | Unknown |
| `P5CS-RUNTIME-001` | Stock PS7331 runtime | Prior Phase 5CP/5CK captures; no new trigger | No `waiter->task != current`, `remove_waiter()` execution, residue or later consumer observed | GhostLock dynamic validation has not begun | Unobserved |
| `P5CS-SAFETY-001` | Phase 5CS process | `tools/scripts/analyze_phase5cs_native_inventory.py` | `host_only=true`; no ADB, ELF execution, syscall, race, device-node, kernel-memory or payload operation | Device state unchanged | Confirmed safety scope |

## Confidence rule

`Confirmed` is limited to the captured artifact or host disassembly. The AOSP
source is a semantic reference, not a substitute for a Fire kernel/userspace
runtime trace. A bounded negative scan is never promoted to “no caller exists.”
