# Phase 6MK evidence index

本索引只收錄本輪新增的 host-only 證據及其直接前置證據。所有「沒有觀察到」
的結果都限定在明確列出的 selected graph；不把 bounded negative 升格為 binary-
wide absence。

## 6MK-REG-001

Evidence ID: `6MK-REG-001`
Source: PS7331 `update-binary` symbolized disassembly
File: `artifacts/phase6s/ota-cfg-focus-20260805-01/focus-disassembly.txt:8215-8335`
SHA-256: `0e780e51ced6f7b000bf0a821ffe6cfe81bc0108e6073174b7fa0cb0b94abdcd`
Test ID: `PHASE6MK-HOST-20260810-04`
Timestamp: 2026-08-10
Command: `python3 tools/scripts/audit_phase6mk_updater_dispatch_closure.py`
Observed result: `RegisterInstallFunctions` contains repeated calls to `0x41d528`; command-name SSO objects and data-cell loads are visible.
Interpretation: install-script command dispatch is implemented through a shared registration routine.
Confidence: **Confirmed**
Related hypothesis: native updater command registry is an indirect boundary.

## 6MK-REG-002

Evidence ID: `6MK-REG-002`
Source: generated registration table
File: `artifacts/phase6mk-updater-dispatch-20260810-04/registration-dispatch.csv`
SHA-256: `d88e35ec08d9ef0a55a3dbc17dc430b62d3b419810653542b6dd3077095cca24`
Test ID: `PHASE6MK-HOST-20260810-04`
Timestamp: 2026-08-10
Command: host-only parser with existing ELF/symbol inputs
Observed result: 24/24 registration pointer cells resolve to known function symbols; recovered names include `package_extract_file`, `apply_patch`, `wipe_block_device`, `run_program`, and `reboot_now`.
Interpretation: the install command registry is concretely mapped, but no command was executed.
Confidence: **Strong evidence**
Related hypothesis: updater parser/handler mapping can be closed without device execution.

## 6MK-ENTRY-001

Evidence ID: `6MK-ENTRY-001`
Source: generated summary and prior direct-edge corpus
File: `artifacts/phase6mk-updater-dispatch-20260810-04/summary.json`
SHA-256: `4cf463ec498b74e6460fb598f7ce5e5756418aaa5c2ac5767009c22e9c29b9fe`
Test ID: `PHASE6MK-HOST-20260810-04`
Timestamp: 2026-08-10
Command: host-only parser
Observed result: `main` calls both install and block-image registration; `PackageExtractFileFn` has a direct edge to `ota_open`.
Interpretation: extraction is reachable from the registered updater command in the static model; this is not runtime reachability on the tablet.
Confidence: **Confirmed**
Related hypothesis: updater extraction/write chain is separate from HOME selection.

## 6MK-CANON-001

Evidence ID: `6MK-CANON-001`
Source: generated canonicalization context table
File: `artifacts/phase6mk-updater-dispatch-20260810-04/canonicalization-context.csv`
SHA-256: `44f61840637e65d7a263b4912d340d834aba1b41b7a84dc7d20382e45fd1a726`
Test ID: `PHASE6MK-HOST-20260810-04`
Timestamp: 2026-08-10
Command: host-only edge correlation
Observed result: no direct caller edge to `readlink`, `readlinkat`, `__readlink_chk`, `realpath`, or `symlink_realpath` appears in the selected graph; `readlink` and `readlinkat` wrappers are selected symbols.
Interpretation: bounded negative only. It does not establish that no unselected/indirect canonicalization exists.
Confidence: **Probable**
Related hypothesis: canonicalization guard is not yet mapped to extraction/write sinks.

## 6MK-MARK-001

Evidence ID: `6MK-MARK-001`
Source: native strings match corpus
File: `artifacts/phase6mk-updater-dispatch-20260810-04/canonicalization-marker-strings.csv`
SHA-256: `8bd1b735dc64fb71cc10fa297d14c01b5b46b52b8e64571043e1bf545090829a`
Test ID: `PHASE6MK-HOST-20260810-04`
Timestamp: 2026-08-10
Command: host-only marker extraction
Observed result: `readlink`, `readlinkat`, `realpath`, `symlink_realpath`, and canonicalization-related marker lines are present in the supplied strings corpus.
Interpretation: marker presence is not a proof of call-site semantics or a security flaw.
Confidence: **Confirmed**
Related hypothesis: path-handling code exists somewhere in the updater binary.

## 6MK-SCRIPT-001

Evidence ID: `6MK-SCRIPT-001`
Source: official PS7331 updater script
File: `firmware/extracted/PS7331/META-INF/com/google/android/updater-script`
SHA-256: `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248`
Test ID: `PHASE6MK-HOST-20260810-04`
Timestamp: 2026-08-10
Command: read-only script parser
Observed result: 13 `package_extract_file`／`block_image_update`／`run_program` entrypoint lines; prior Phase 6MD maps protected block-device targets.
Interpretation: the route is a privileged update/recovery path and is outside a reversible ADB HOME workaround.
Confidence: **Confirmed**
Related hypothesis: native updater is not a shell-level Launcher selector.

## 6MK-SAFETY-001

Evidence ID: `6MK-SAFETY-001`
Source: generated summary
File: `artifacts/phase6mk-updater-dispatch-20260810-04/summary.json`
SHA-256: `4cf463ec498b74e6460fb598f7ce5e5756418aaa5c2ac5767009c22e9c29b9fe`
Test ID: `PHASE6MK-HOST-20260810-04`
Timestamp: 2026-08-10
Command: host-only parser
Observed result: `device_contacted=false`, `updater_executed=false`, `recovery_executed=false`, `partition_written=false`.
Interpretation: no device state changed in this phase.
Confidence: **Confirmed**
Related hypothesis: Phase 6MK can be reproduced without risky operations.

## 6MJ-RESIDUAL-001

Evidence ID: `6MJ-RESIDUAL-001`
Source: bounded repository inventory
File: `work/luna_worker_phase6mj_residual_inventory_20260810.md`
SHA-256: `4552646901eaf74372927a28e8a37ee0e951b6e961177c964efc85a92aaa4847`
Test ID: `PHASE6MJ-INVENTORY-20260810`
Timestamp: 2026-08-10
Command: read-only file/evidence inventory
Observed result: remaining gaps are OOBE user-scope mapping, Amazon private Binder caller inventory, protected broadcast membership, and native updater indirect/canonicalization closure.
Interpretation: Phase 6MK closes only the updater registration portion; the other gaps remain separate.
Confidence: **Strong evidence**
Related hypothesis: next work must not repeat closed HOME/package-state tests.
