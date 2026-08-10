# OTA / post-install reconciliation — PS7331 / Fire OS 7.3.3.1

日期：2026-08-10。範圍是目前 workspace 主機端唯讀 evidence reconciliation：exact OTA、已解包 `META-INF`/Edify、OOBE/BootAfterSystemOTA、otadexopt/native helper，以及既有 Phase 5/6/10/12 結果。沒有構造或修改封包，沒有執行 `update-binary`、recovery、sideload、flash、ADB、Binder、broadcast replay、symlink/traversal、reboot 或設備/partition 修改。

## 判定

目前沒有證據閉合「低權限 caller → OTA/recovery/partition sink」的完整鏈。已閉合的是 shipped PS7331 updater 的高權限 capability，以及 system-server 合法 upgrade lifecycle 的 OOBE state writer；兩者都沒有被證明可由 shell/ordinary app 取得或觸發。故本次結論是：**未發現已閉合的低權限 caller 能進入高權限 OTA/partition sink。** 這是 bounded negative，不是對所有未保存 recovery/native code 的 universal absence 宣告。

## 已觀察的 capability 與邊界

- `firmware/extracted/PS7331/META-INF/com/google/android/updater-script:1-24` 有 build-date/product abort、`block_image_update` 到固定 `system`/`vendor` by-name target、以及 `package_extract_file` 到 `boot`、`preloader`、`lk`、TEE/firmware targets 與 `/cache/recovery/last_blocklist`。這證明 recovery/updater capability，不證明 execution 或 caller reachability。
- `update-binary` (`SHA-256 02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b`) 的靜態 native graph 可到 Edify registry、extraction/block-image、`open`/`rename`/`chown`/`write`；`WriteToPartition` 與 named targets 的 sink capability 已確認。command dispatch 是 indirect，未執行。
- Java-side `OSUpdateValidator`/`SideloadVerifier` → `RecoverySystem.verifyPackage` → staging/`UpdateSystem.install` 的 provenance 已保留；但 native recovery verifier、AVB/rollback decision、final exec/domain/UID 與 Java-to-native caller 沒有在保存 corpus 中閉合。updater-script 的 date/product gate 不是 rollback-index proof。
- `MakeFreeSpaceOnCache → __readlink_chk` 與 `CacheSizeCheck` callers/return branches 已有 host-only evidence；selected graph 沒有 direct canonicalization→partition-write edge，但 indirect dispatch、argument provenance、完整 cache/path dataflow 尚未閉合。因此不推論 traversal/no-follow flaw。
- known package audit（Phase 6I/6FE）沒有另外找到 A/B `postinstall` executable 或 top-level post-install helper；保留 package-scoped negative。外層 `Fire_HD10-7.3.3.1-20250617.tar.bz2` listing 曾未到 verified EOF，不能把 negative 擴大到未列出的 outer-tail members。
- `AmazonPackageManagerService.onBootPhase(550)` 僅在 `isUpgrade()` 條件下送受 permission 保護的 `BOOT_AFTER_SYSTEM_OTA`。`BootAfterSystemOTAReceiver` 可 enable `OobeHomeActivity` 並寫 OOBE/setup state；這是 trusted lifecycle writer，不是普通 HOME replacement。receiver 的 numeric user scope 是 context-derived/未閉合。
- `OtaDexoptService` 的既有 capture 只到 shell-visible precondition path/error；未執行 mutating `prepare/next/cleanup/step`，也沒有 partition/HOME sink。
- HOME/PMS 既有 Phase 6/10/12 evidence 沒有閉合 User-0 Fire Launcher preferred-HOME writer。PMS/Settings 的 preferred writers、KFT launcher component writer 與 DPM/profile paths 各有更高權限或 child/profile/user/caller 缺口；既有結果不能把 OOBE component state mutation 當作 Fire Launcher HOME replacement。

## Phase 5/6/10/12 reconciliation

Phase 5 的 PS7331 upgrade/image/config evidence 支持 package/version/image provenance、verified/locked baseline 與 source/config scope，但不是低權限 OTA caller 證據。Phase 6 已分別保存 OTA verifier gap、native updater capability、BootAfter/OOBE scope、otadexopt boundary、SELinux/service visibility 與 HOME/PMS closure；本次只整合，不重做禁止的 runtime tests。Phase 10 的 OTA/post-install row 保留 `signature|privileged` controller boundary、無普通 APK/shell→privileged OTA chain 的 negative，以及無 post-OTA runtime effect。Phase 12 的 existing-evidence reconciliation 保留 AVB/rollback/native handoff、exact production caller/UID、SELinux tuple、numeric user scope 與 persistence/reboot gaps。

## 缺少的 closure edge

1. verifier → AVB/rollback-index → recovery accepted package → exact `update-binary` exec/domain/UID 的完整 provenance。
2. production OTA controller caller package/UID/signature、service-manager/SELinux allow tuple，以及 caller identity 是否被清除/切換。
3. native registry/function-pointer dispatch、`CacheSizeCheck`/`MakeFreeSpaceOnCache` 全 callers、archive argument 到 target 的 dataflow與 error/continuation 對 writer 的關係。
4. exact recovery/updater SELinux domain、file/partition labels/allow rules 與 init callback implementation；現有 Fire OS init XML 只保存 callback registration。
5. BootAfterSystemOTA receiver 的 numeric user/context provenance、OOBE state persistence/consumer，以及是否能影響實際 HOME resolver 的證據。
6. rollback/persistence across reboot/build、自然授權 OTA 後的唯讀 state/log/package/HOME observation。不得用 downgrade、replay、reboot 或 OTA execution 補洞。

## 非破壞性 HOME 狀態寫入結論

唯一明確看到的開機後 writer 是 OOBE receiver 對 `OobeHomeActivity` component enabled state 與 setup/OOBE settings 的寫入；其合法前提是 system-server phase 550 + `isUpgrade()` + protected action/lifecycle。保存 evidence 沒有 Fire Launcher literal、`setHomeActivity`、`addPreferredActivity` 或 `replacePreferredActivity` 在該 chain 中，也沒有證明 numeric User 0 或 durable HOME resolver mutation。故不能猜測它會影響 HOME；目前只能標記為 OOBE-adjacent state writer，HOME effect 未觀察/未證明。

## Safe next step

只做 host-only：若取得新的 exact signed package，重新 hash/member/manifest audit；完成未 EOF 的 outer tar listing；擴大既有 native disassembly 的 indirect pointer、caller、argument/return tracing；或在自然發生且已授權的 OTA 後收集 read-only build、AVB/rollback、OOBE、package/component、HOME 與 log evidence。不得執行 updater/recovery、構造 OTA、測 symlink/traversal、replay protected broadcast、呼叫 private Binder 或寫 partition。

逐列索引見同名 CSV；每列的 `confidence` 只代表目前主機端 evidence 對該列敘述的信心，不把 capability 升級成 reachability。
