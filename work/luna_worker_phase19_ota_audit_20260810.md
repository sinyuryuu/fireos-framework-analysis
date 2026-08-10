# Phase 19B — PS7331 host-side OTA/update/post-install/recovery boundary audit

日期：2026-08-10。僅讀檢查 `firmware/original`、`firmware/extracted/PS7331`、既有 `artifacts`/findings 與 Phase 18 報告；未修改或重放 OTA，未執行 `update-binary`、recovery、sideload、reboot、partition write、malformed package 或 symlink/traversal 測試。

## 結論

本輪沒有發現可把既有 privileged updater capability 升格為 shell/ordinary-app reachability 的新證據。Phase 18 已確認的 package identity、fixed block targets、Java verification/install handoff、BOOT_AFTER_SYSTEM_OTA lifecycle 與 bounded negative 不重做；本輪只記錄仍未閉合的 host-side boundary。

原始 `update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` 是可讀驗證的 SignApk-signed ZIP/JAR，`unzip -t` 無錯，archive 有 27 entries。`metadata`/`ota.prop` 給出 `ota-type=BLOCK`、`pre-device=trona`、PS7331.4463N、release-keys 與 `post-timestamp=1746234888`；`updater-script` 以固定 system/vendor block-image 及 boot-chain `/dev/block/platform/bootdevice/by-name/*` 目標更新，並寫 `/cache/recovery/last_blocklist`。這些是 recovery/updater capability，不是未授權 caller 證明。

既有 host artifacts 進一步確認：`RegisterInstallFunctions` 的 24 個 function-pointer registrations 已解析，但 dispatch 仍是 indirect；`MakeFreeSpaceOnCache`/`CacheSizeCheck` 的分支關係已知，selected graph 沒有 canonicalization 到 extraction/write 的 direct edge。Java `RecoverySystem.verifyPackage` 與 staging/install 呼叫已存在，但 platform verifier 的 native executor、recovery UID/SELinux domain、AVB authority/rollback-index enforcement 未由保存 corpus 閉合。`SideloadMover` 的 basename/rename-or-copy path 也沒有 Java-level canonical/no-follow 或 race-proof evidence；不據此宣稱 symlink、TOCTOU、traversal 或 verifier bypass。

## Residual closure matrix

CSV 為本報告的逐列 evidence index；每一列均明確列出 caller、gate、sink、missing edge、classification 與 evidence。分類只表示保存證據的狀態：`CONFIRMED_STATIC` 是靜態 capability/metadata，`BOUNDED_UNKNOWN` 是尚未閉合的 edge，`BOUNDED_NEGATIVE` 是本輪 corpus 內未觀察到但非 binary-wide absence。

### 1. Archive / metadata / updater boundary

- Archive integrity 與 member inventory 已在原始 package 層確認：27 entries、所有 ZIP entries CRC/test OK，`zipinfo` 未見 symlink mode；這只覆蓋 package container，不覆蓋 block-image semantics 或 recovery execution。
- `metadata`、`ota.prop` 與 `otacert` 建立 release-key/full-BLOCK package identity；Java verifier handoff 仍只到 platform API boundary，不能推導 native verifier acceptance 或 rollback behavior。
- `updater-script` 只提供固定 gate 與固定 sink。`update-binary` 註冊的 `run_program`、`reboot_now` 等 handler 是 recovery-side command capability；沒有保存 caller/UID edge 把它們連到 ordinary app 或 shell。

### 2. Path / symlink / TOCTOU boundary

- `target.system.file_map`/blocklist 的既有 path scan 對 archive member path、duplicate 與 fixed targets 為 bounded clean result；不等同 staging destination 或 native cache helper 的 no-follow guarantee。
- `SideloadMover`/`FileHelper` 的 basename、`renameTo`/copy-delete flow 缺少 canonical path、openat/no-follow、directory-fd 或 same-object revalidation evidence。這是 missing edge，不是已證實漏洞。
- Native `readlink`/`readlinkat`/realpath markers 與 `MakeFreeSpaceOnCache` callsite 存在，但 indirect/unselected CFG、input provenance、return/error branch 到 write guard 尚未全部閉合；未做 crafted path、symlink 或 race replay。

### 3. AVB / rollback / recovery SELinux-UID handoff

- 保存 PS7331 extracted tree 沒有 `vbmeta.img` 或 AVB metadata member；既有 verifier audit 只證明 Java `RecoverySystem.verifyPackage` handoff 與 updater capability，沒有 recovery/native AVB authority 或 rollback-index implementation。
- recovery/updater 執行身份、SELinux domain transition、UID handoff 與 `update-binary` actual caller 未恢復。baseline 的 enforcing 狀態只能支持 boundary context，不能補出 allow rule 或低權限路徑。
- package-scoped inventory 沒有獨立 A/B `payload.bin` 或 post-install executable；`last_blocklist` 是 recovery metadata sink。outer source tar 的完整 corpus EOF 仍是既有未閉合限制，因此只作 package-scoped bounded negative。

## 判定與安全界線

總判定：`privileged recovery/updater capability confirmed; untrusted caller, canonicalization/TOCTOU, native verifier/AVB rollback, and recovery SELinux/UID handoff remain bounded-unresolved`。沒有新 evidence 支持 signature bypass、AVB rollback bypass、symlink/TOCTOU exploit、SELinux bypass、shell/ordinary-app OTA reachability 或 post-install code execution。

本輪未執行也不建議用來補缺口的操作：修改/構造/malformed/downgrade OTA、sideload、recovery 或 `update-binary` execution、replay OTA/broadcast/Binder、symlink/traversal/race test、reboot、flash 或任何 partition write。安全後續僅限 host-side 恢復 verifier/AVB/rollback source provenance、完整 native indirect dataflow、或在自然且已授權 OTA 後收集只讀 runtime evidence。

