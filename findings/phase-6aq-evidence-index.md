# Phase 6AQ／6AR Evidence Index

本索引只納入本階段新增或直接引用的證據。原始裝置 dump 保留在本機
`adb/phase6aq/`；公開摘要、輸入雜湊與 bounded matrix 位於
`artifacts/phase6aq/public-summary-20260805-05/` 與
`artifacts/phase6aq/service-context-audit-20260805-06/`。

| Evidence ID | Source | File／位置 | SHA-256／識別 | 結論 | Confidence |
|---|---|---|---|---|---|
| `6AQ-SCOPE-001` | Read-only capture metadata | `adb/phase6aq/PHASE6AQ-SERVICE-RO-20260805-01/metadata.json` | input hash in `artifacts/phase6aq/public-summary-20260805-05/input-sha256.json` | 19 queries；explicit serial；no mutation／broadcast／Binder transaction | Confirmed |
| `6AQ-SVC-001` | Amazon `fosinit` registration | `artifacts/amazon-services/amazonactivitymanager_fosinit.xml:10-25`; `amazondevicepolicymanager_fosinit.xml:10-26`; `amazonpackagemanager_fosinit.xml:10-30`; `amazonwindowmanager_fosinit.xml:10-29` | individual source hashes recorded in prior Phase 6Q inventory | Amazon service/callback wiring exists | Confirmed |
| `6AQ-SVC-002` | Amazon `fosinit` callback wiring | `launcherhijackpreventer_fosinit.xml:10-19`; `tabletlauncherhijackpreventer_fosinit.xml:10-18`; `tabletkeypolicymanager_fosinit.xml:10-20`; `core_fosinit.xml:7-15` | source files | task visibility, package callback, Home-key interceptor and debug service boundaries exist | Confirmed |
| `6AQ-SVC-003` | Runtime service inventory | `adb/phase6aq/PHASE6AQ-SERVICE-RO-20260805-01/service_list.stdout.txt:30-60,155`; `dumpsys_fosdebug.stdout.txt:1-100` | `service-context-key-rows.csv` hash `95a796b8e032a9ff05ada3a75deb24aa835fc871d88b2e9a24e00f026d0ec950` | services/inventory are loaded; `fosdebug`/`otadexopt` are shell-visible by standard dump/check | Confirmed |
| `6AQ-SVC-004` | Shell service lookup | `adb/phase6aq/PHASE6AQ-SERVICE-RO-20260805-01/service_check_*.stdout.txt` | `service-check-results.txt` hash `242b8381d43970c6d25075d7434e9a8c6f26e0167bb4c8c31d910af1e0bb5aed` | eight Amazon private service checks return `not found` for shell | Confirmed |
| `6AQ-SVC-005` | SELinux AVC | `artifacts/phase6aq/public-summary-20260805-05/amazon-service-avc.txt` | `d436542564947472c1b2481519312542d7d1053512b9cb47c68abbb981e0b0a4` | shell UID 2000 `service_manager find` denied, enforcing policy | Confirmed |
| `6AQ-SVC-006` | Context join | `artifacts/phase6aq/service-context-audit-20260805-06/service-context-matrix.csv` | `44526ce659cea48931be2b5d9b1b981f905a086f30a64acd78576dac27ee6397` | key private names map to Amazon service contexts and prior AVC rows | Strong evidence |
| `6AQ-HOME-001` | Home-key implementation | `decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:3744886-3744901` | VDEX input hash `04d68d0bb562a14e9cbff3bdce63b66eb911ee4bb7e728ca77cd435a5b03c146` | `launchHomeFromHotKey` uses implicit MAIN+HOME and `startActivityAsUser` | Confirmed |
| `6AQ-HOME-002` | Task visibility callback | `decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:3739892-3739925` | same VDEX input | SELinux/signature gate controls Home task visibility, not proven candidate rewrite | Confirmed / scope-limited |
| `6AQ-HOME-003` | Custom Home event | `decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:3744254-3744301` | same VDEX input | foreground custom broadcast requires Amazon permission; not normal HOME selection | Confirmed |
| `6AQ-HOME-004` | Permission provenance | `artifacts/phase6ad/protected-broadcast-inventory-20260805-01/manifests/017_android.amazon.perm.xmltree.txt:512-514`; `artifacts/phase6x/prewarm-authorization-20260805-05/com_amazon_permission_APP_PREWARM.block.txt:151-155` | manifest hash `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed` | `RECEIVE_CUSTOM_HOME` is `signature|amazon`, source UID 1000 | Confirmed |
| `6AQ-HOME-005` | Fresh resolver baseline | `artifacts/phase6aq/public-summary-20260805-05/home-and-build-state.txt`; raw `home_resolve.stdout.txt` | `01867d17a0084571870ff5cc698d738b109a2d2abcf709d56ed8d6d8ce307563` | current HOME resolves Fire Launcher priority 50; preferred XML empty; role service absent | Confirmed |
| `6AQ-AM-001` | AM state query | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40336-40373` | VDEX input hash `ecbe62fe8eb8bd575da8a2b73a155875df937073ccc2faa020ca592c0515151c` | `isOnHomeStack` queries focused stack/activity type; no HOME mutation in bounded method | Confirmed |
| `6AQ-AM-002` | Activity observer | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40374-40400` | same VDEX input | `notifyActivitySwitch` broadcasts observer notification; no Fire Launcher selection in bounded method | Confirmed |
| `6AQ-PW-001` | Prewarm method candidate | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40540` | same VDEX input | permission check followed by identity clear without visible denial branch; no runtime caller evidence | Hypothesis |
| `6AQ-OTA-001` | OTA staging closure | `findings/phase-6y-ota-staging-boundary.md` and referenced `artifacts/phase6y/ota-staging-audit-20260805-01/` | prior Phase 6Y hashes | verification/staging precedes high-impact `UpdateSystem.install` boundary | Confirmed |
| `6AQ-OTA-002` | Post-OTA OOBE closure | `findings/phase-6z-boot-after-system-ota-follow-up.md` | prior Phase 6Z evidence IDs `6U-OOBE-*`, `6U-OTA-*`, `6W-*` | receiver is natural post-OTA OOBE lifecycle, not shell HOME selector | Strong evidence |
| `6AQ-NEG-001` | Safety boundary | `artifacts/phase6aq/public-summary-20260805-05/scope.txt` | `a89d03f85418754cb8d33b51b04a5359204eeb863ee6b3e25935e8adfa5b8836` | no OTA/OOBE replay, unknown Binder transaction, mutation or partition write | Confirmed |

## Confidence rules

- `Confirmed`：原始指令輸出或 instruction-level evidence 直接支持。
- `Strong evidence`：多個獨立輸入一致，但仍有明確 scope boundary。
- `Hypothesis`：靜態候選或缺少 runtime invocation；不能用作漏洞／提權結論。
- 本階段沒有把任何 Amazon private service 缺少 method-local marker 解讀成授權
  缺陷，也沒有宣稱找到 root 或 launcher replacement。
