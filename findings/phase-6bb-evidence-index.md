# Phase 6BB Evidence Index

本索引只收錄可重現的 host-only 證據。所有路徑均為相對 repository root 的路徑；
未收錄裝置序號，也沒有新的裝置狀態變更。

| Evidence ID | Source | File / location | SHA-256 | Observation | Classification |
|---|---|---|---|---|---|
| 6BB-STATIC-001 | Fire services VDEX | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40534` | `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` | server method checks `APP_PREWARM`, does not show a consumed result before `clearCallingIdentity`, then reaches `startProcessLocked(...,"prewarm",...)` | 高可信靜態異常候選；非漏洞證明 |
| 6BB-STATIC-002 | PS7331 OTA VDEX | `decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:3642543-3642624` | `04d68d0bb562a14e9cbff3bdce63b66eb911ee4bb7e728ca77cd435a5b03c146` | OTA-matched server method preserves the same prewarm control-flow markers | 已證實靜態 |
| 6BB-BINDER-001 | Framework VDEX proxy | `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:394721-394751` | `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71` | descriptor is `com.amazon.android.server.am.IAmazonActivityManager`; proxy transaction is `1`; writes String + 2 ints | 已證實靜態 |
| 6BB-BINDER-002 | PS7331 OTA proxy | `decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:4464666-4464696` | `04d68d0bb562a14e9cbff3bdce63b66eb911ee4bb7e728ca77cd435a5b03c146` | OTA proxy matches transaction `1` and return-int path | 已證實靜態 |
| 6BB-BINDER-003 | Framework wrapper | `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:553272-553277,553433-553446` | `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71` | manager obtains `amazonactivitymanager` and delegates to the Binder interface | 已證實靜態 |
| 6BB-REG-001 | Amazon service registration | `artifacts/amazon-services/amazonactivitymanager_fosinit.xml:8-28` | `5d212c94f047aee7abc85ef6dc99aa92ca61e3e3d9318bb69db3c10d9e0da411` | registers `AmazonActivityManagerService` and the `activity` manager implementation | 已證實 |
| 6BB-CALLER-001 | Saved Alexa JADX | `artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/sources/amazon/speech/sim/router/intentrouter/ExplicitIntentAction.java:268-282` | `c1a8bcfc0952239a26b669f7bc227fcc01024ac5db26db7e6eed2ae5cb6a2dc2` | one direct caller in the supplied source scope; it passes target package and foreground profile | 高可信；scope-limited |
| 6BB-CALLER-002 | Alexa manifest and device package dump | `artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/manifest.txt:143-150`; `artifacts/phase6j/phase6j-ota-controller-holders-20260805-01/dumpsys_package_all.stdout.txt:24201-24216,24450-24456` | `016bb989d131b2d3f5da85d57962b19054dddbc67eb08d6a9d0812077eacb049`; `6f2754f4e9655567524de00c5b044326cbd992d6a9022b87397369fb5b905909` | Alexa is `/system/priv-app`, `PRIVILEGED`, requests and receives `APP_PREWARM` | Strong evidence |
| 6BB-ROUTE-001 | Existing Phase 6K live capture | `artifacts/phase6j/phase6j-service-visibility-20260805-01/filtered_avc.matches.txt:4403,4412,4420`; `service_check_amazonactivitymanager.stdout.txt` | `53cbf5d5e873de56b7efee4918ba0b95f5968bf824e665842a5d1f4860ddb5cb`; `fb64966bad778f1a3ebd748027b77455f07dfbddaf3ceac69995e3be7e6f5c31` | saved enforcing capture records shell service-manager `find` denied and service check not found | 已證實 live boundary |
| 6BB-TOOL-001 | Reproducible host parser | `tools/scripts/audit_phase6bb_prewarm_caller_mapping.py`; `artifacts/phase6bb/prewarm-caller-closure-20260805-04/summary.json` | see artifact `sha256sums.txt` | parser records `device_contacted=false`, `binder_invoked=false`, `mutation_performed=false`, `root_attempted=false`, 10 method blocks and 2 source occurrences | 已證實分析邊界 |

## Reproduction

```sh
python3 -m py_compile tools/scripts/audit_phase6bb_prewarm_caller_mapping.py
python3 tools/scripts/audit_phase6bb_prewarm_caller_mapping.py --dry-run \
  --output artifacts/phase6bb/prewarm-caller-closure-DRYRUN
python3 tools/scripts/audit_phase6bb_prewarm_caller_mapping.py \
  --output artifacts/phase6bb/prewarm-caller-closure-<new-id>
```

The parser refuses to overwrite an existing output directory. Verify a generated run
from its own directory with `sha256sum -c sha256sums.txt`.
