# Phase 6BD evidence index

所有結論都限定在下列保存輸入與測試範圍內。設備原始 service capture 含識別資料，未納入公開 commit；其 `sha256sums.txt` 的 hash 已記錄在 host-only audit output。

| Evidence ID | Source / file | Test ID | Observation | Classification | Confidence |
|---|---|---|---|---|---|
| 6BD-RO-001 | `adb/phase6bd/PHASE6BD-SERVICE-RO-20260805-01/sha256sums.txt`（本機原始 capture） | `PHASE6BD-SERVICE-RO-20260805-01` | 八個選定 Amazon private services 對 shell 為 `not found`；`fosdebug`、`otadexopt` 為 `found`；capture metadata 明確標示 no Binder transaction / no package change | 已證實唯讀邊界 | Confirmed |
| 6BD-INPUT-001 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:20112-20122,21687-21692,22437-22448`；VDEX SHA-256 `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` | `PHASE6BD-HOST-20260805-01` | `setInputFilter → access$600 → validateInputFilterAccessPermission`; system/updated-system app check，否則 permission enforcement | shell input filter path is protected | Confirmed |
| 6BD-PERM-001 | `artifacts/phase6ac/protected-broadcast-source-audit-20260805-02/manifest-aapt.xmltree.txt:1431-1433`; `artifacts/phase6k/readonly-device-20260805-01/preferred_activities.stdout.txt:9897-9901` | `PHASE6BD-HOST-20260805-01` | `FILTER_INPUT_EVENTS` 的 declared/device protection 為 `signature|amazon` | non-system shell cannot assume permission | Confirmed |
| 6BD-KFT-001 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54297-54325`；VDEX SHA-256 `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` | `PHASE6BD-HOST-20260805-01` | 指定 UserInfo 上 enable FreeTime、request Fire Launcher state 2、request Launcher3 state 2 | KFT static capability | Confirmed |
| 6BD-KFT-RO-001 | `findings/phase-6ay-kft-runtime-preflight.md` 及本機 `adb/phase6ay/KFT-PREFLIGHT-20260805-01/` | `KFT-PREFLIGHT-20260805-01` | 只有 User 0、無 child/KFT user、private service not found、KFT mutation 未呼叫、HOME 未變更 | device mutation not executed | Confirmed |
| 6BD-DEBUG-001 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:196-387`；本機 `dumpsys_fosdebug.stdout.txt` | `PHASE6BD-SERVICE-RO-20260805-01` | DUMP gate 後輸出 vendor inventory；沒有 bounded HOME/package setter | diagnostic-only evidence | Strong evidence |
| 6BD-OTA-001 | `findings/phase-6bc-provenance-and-fallback.md`；本機 `dumpsys_otadexopt.stdout.txt` | `PHASE6BD-SERVICE-RO-20260805-01` | service visibility 不等於 OTA control contract；未執行 OTA command、staging 或 recovery | no safe control surface established | Strong evidence |
| 6BD-AUDIT-001 | `tools/scripts/audit_phase6bd_ipc_service_closure.py`; `artifacts/phase6bd/ipc-service-closure-20260805-01/summary.json` | `PHASE6BD-HOST-20260805-01` | audit 是 host-only，`device_contacted=false`、`binder_invoked=false`、`package_state_changed=false`、`kft_device_invoked=false` | reproducibility metadata | Confirmed |

## Input hashes

由 `audit_phase6bd_ipc_service_closure.py` 產生的輸入 hash：

| Input | SHA-256 |
|---|---|
| `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` | `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` |
| `artifacts/phase6ac/protected-broadcast-source-audit-20260805-02/manifest-aapt.xmltree.txt` | `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed` |
| `artifacts/phase6k/readonly-device-20260805-01/preferred_activities.stdout.txt` | `6f2754f4e9655567524de00c5b044326cbd992d6a9022b87397369fb5b905909` |
| `adb/phase6bd/PHASE6BD-SERVICE-RO-20260805-01/sha256sums.txt` | `6319a9d7f99027d26ffdaba486bb9aa96b84637aed8a81fafe6d683629e80f8b` |

## Limitations

- `service check` 只說明本次 shell service-manager lookup 的結果；不等於服務不存在，也不等於其他 privileged caller 的授權結果。
- VDEX instruction evidence 證明靜態 control flow；沒有把 KFT 或 input filter 路徑在設備上執行。
- `dumpsys fosdebug` 的 callback inventory 不提供 callback implementation 的完整安全語意；未進行 callback replay。
- 這些證據不能推導 root、kernel exploit、正式 HOME replacement 或可利用的 Binder bypass。
