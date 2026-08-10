# Phase 6X-OTA — 7.3.3.1 host-only static audit

日期：2026-08-10；基準 HEAD：`687a236c0b81e44060b3ec6a5a53fdce74eabf3e`。

範圍只包含 7.3.3.1 OTA/安裝包、post-install/native updater、recovery/AVB/rollback、暫存檔、symlink/canonicalization。未構造或執行更新包，未 sideload、刷機、重啟、執行 recovery/update-binary、寫入分割區，也未接觸設備。

## 結論

去重 Phase 6WH、6SD、6SP、6TG、6VB 及既有 OTA reports 後，沒有新的 untrusted caller → gate → identity → writer 閉合，也沒有新的可報告 bypass。現有證據仍是：

`privileged OTA lifecycle → metadata/hash/recovery-verification gates → basename staging → UpdateSystem.install → recovery/update-binary → Edify/block-image/extraction → open/write`

其中 recovery/native writer capability 已確認，但 exact recovery caller、UID/SELinux identity、AVB rollback handoff、暫存 canonicalization/no-follow/atomicity、間接 dispatch/dataflow 仍為 `UNKNOWN`。OOBE post-install 的 protected `BOOT_AFTER_SYSTEM_OTA` 與 context-scoped component/settings sink 亦沒有 ordinary app/shell caller 或 exact numeric user 閉合。

## 本輪新增的排除／邊界

1. `firmware/manifests/OTA-20260803-01/README.md` 明確把保存包標為 `VERSION_MISMATCH`：裝置基線是 PS7330/7.3.3.0，保存 OTA 是 PS7331/7.3.3.1。故該包可作 7.3.3.1 adjacent static evidence，不能當作目前安裝版本的 runtime caller、post-install effect、AVB/rollback 結果。
2. `selected/` 與 `compiled-02/` extraction manifests 只列 host-side `debugfs` 衍生檔及 SHA-256；它們不是安裝、post-install 或 recovery execution log。由其中出現 framework/APK/VDEX 路徑，不能推導 caller identity 或 writer reachability。
3. 既有 native registry/block-image/cache/readlink、Java staging/handoff、OOBE helper、AVB/recovery 缺口均與 6WH/既有 reports 相同；本輪不重列為新 finding，只在 CSV 留下去重後的 disposition 與 UNKNOWN 邊界。

## Evidence / safety boundary

保存 OTA SHA-256：`9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`。`ota.prop` SHA-256：`f91b4c792339c605d81a2d6d5e819fee5d522a7514111daa1468717e07319ded`。本報告只引用可在 HEAD/工作區核對的 manifest、extraction manifest 與既有靜態 evidence；不把 raw adjacent OTA、derived extraction 或缺失的 `vbmeta`/recovery implementation 誤標為已驗證 runtime evidence。

CSV 欄位固定為 `evidence_id,surface,source,caller,gate,identity_scope,sink,observed_effect,confidence,evidence_file,evidence_sha256,status`。`UNKNOWN` 表示證據不足，不表示存在 bypass；`NONE` 表示沒有觀察到 effect。

