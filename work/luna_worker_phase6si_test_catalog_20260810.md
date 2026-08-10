# Phase 6SI — Phase 5/6 test and result catalog

日期：2026-08-10（Asia/Taipei）  
範圍：只讀 `adb/`、`artifacts/`、`findings/`、`output/`、`work/`。未執行 adb，未修改裝置，未發送 Binder、driver、OTA、recovery 或 OOBE payload。逐列資料在同名 CSV。

## 結論

本 catalog 將同一測試族群的多個 run、before/after/rollback guard 與靜態 artifact 合併為一列；因此不把每個輸出檔誤算成獨立測試。涵蓋 Phase 5 的 low-level/CVE/OTA/accessibility/route/postcheck 類，以及 Phase 6 的 PI、KFT child、prewarm、PMS/HOME、driver policy、OTA/OOBE、accessibility redirect、ProductPolicy/package-state、updater 與重複 read-only guard 類。

最重要的狀態：

- KFT child：已閉合的是 trusted child/profile writer，且以 `UserInfo.id` 為 scope；不是 User 0 HOME writer。Shell/private service reachability 已被保存證據拒絕或限制。
- prewarm：`APP_PREWARM` gate、server flow、privileged Alexa caller 有強靜態證據；ordinary-app Binder route 未閉合。
- PMS/HOME：KFT 是目前唯一閉合的 launcher-specific Amazon writer，但 child-scoped；沒有確認低權限 User 0 Fire HOME writer。大量 HOME resolver/foreground runs 是重複 guard。
- driver policy：source ioctl、policy allow、factory `0666` 等只證明條件式 capability；retail active branch、client、node access 與 effect 尚未 join。
- OTA/OOBE：receiver/settings/updater sinks 與 authorization gates 有靜態證據；未送 broadcast/Binder/OTA，不能把 sink 當成 ordinary caller route。
- accessibility redirect：既有 isolation/monitor/rollback run 可作 bounded evidence；沒有證明 unrestricted durable redirect，不應重跑。

## 分類規則

`evidence sufficient` 表示本 catalog 針對該範圍已有足夠保存證據；`duplicate` 表示重複既有 run/guard；`evidence insufficient` 表示還缺 caller、user、retail branch、hash 或 reachability closure；`rejected` 表示明確未做或被邊界拒絕；`negative` 只代表保存測試未得到該路徑，不外推全系統不存在。

CSV 欄位固定為：`test id, scope, command class, device mutation, result, evidence path/hash, classification, next safe action`。

## 已公開、重複、前提變更與安全重複

- 已公開/已有完整索引：Phase 5 low-level/CVE/OTA/accessibility、Phase 6A PI、6AY KFT、6BB prewarm、6BG UI、6R OTA/OOBE、6U boot-after-OTA、6K/6KV/6MW PMS/HOME、6QE driver policy、6NE updater。
- 重複：HOME resolver/foreground、service visibility、user list、Fire package state、rollback/final guards；每個 build/state 保留一個 canonical run 即可。
- 前提已變：只有在 fingerprint/build、受測 user/profile、package/artifact corpus、policy/image marker 或 protected-broadcast inventory 改變時，相關 static/read-only review 才重新開 queue。既有 run 不因新檔案名稱自動變成新結果。
- 證據不足：driver retail branch/client join、Amazon PM/KFT 完整 caller/holder/user mapping、OOBE exact numeric user、native updater/archive EOF 與 ordinary caller closure。
- 可安全重複：host-only parser、CSV schema/hash verification、source-to-policy/caller/data-flow join、既有 artifact 的 EOF/provenance review。不可安全重複：private Binder transaction、driver ioctl/node write、package/PMS setter、child creation/switch/unlock、accessibility isolation replay、OTA/OOBE/recovery/updater payload。

## 交付檔

- [CSV catalog](luna_worker_phase6si_test_catalog_20260810.csv)
- 本檔只新增於 `work/`；未修改其他既有檔案。

