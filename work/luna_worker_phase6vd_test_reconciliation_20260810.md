# Phase 6VD：既有實機測試與結果去重稽核

日期：2026-08-10（Asia/Taipei）  
範圍：唯讀掃描 `adb/`、`findings/`、`output/`、`artifacts/` 中 Phase 3A–6UR 的既有證據；矩陣見 [CSV](./luna_worker_phase6vd_test_reconciliation_20260810.csv)。

本稽核沒有重新執行 adb、沒有連接或改動實機、沒有 reboot、沒有送出 Binder/driver/OTA/recovery/root/PI-futex 操作，也沒有提出未知 Binder code 或 exploit payload。CSV 的 `Original evidence paths` 保留原始路徑；`Original evidence SHA-256` 保留可核對的 finding／worker artifact SHA。資料夾路徑的 SHA 以其內既有 manifest 或列出的 canonical file 為準，不能解讀成整個資料夾的單一 hash。

## 去重後結論

- User-0 HOME 的 canonical 保存結果仍是 Fire Launcher；普通 preferred/set-home、package-state 與 force-stop 類路線沒有形成可持續的第三方 User-0 HOME。
- Child/Tahoe/KFT 是真實但嚴格限於 target child/profile 的狀態變化；switch-back/final guard 保留 User-0 Fire，不能升格為 User-0 writer。
- Accessibility/ADB monitor/Lock Task 只支持 bounded foreground 或 temporary workaround；沒有 formal HOME resolver writer，也沒有可持續性證據。
- DPM、Settings/overlay、private service/Binder、OTA/OOBE/updater、driver/ION、root/PI-futex 路線均未閉合 `caller → gate/identity → user scope → sensitive sink`。Static declaration、service visibility、ELF/policy edge、OTA writer graph 都不是 runtime reachability。
- 「已排除」包括重複、明確安全拒絕或在既有條件下未達成目標；拒絕／未執行不等於負向 runtime 結果，也不代表未知高權限 caller 不存在。

## 判讀與安全最小驗證

`Whether state truly changed` 僅描述保存的既有 run；read-only/static 是沒有裝置 mutation，historically 是有 before/after/rollback 或 profile 生命週期證據。沒有任何普通 app/shell 路線被標成可持續 User-0 replacement。

重複族以 build fingerprint、user/profile topology、candidate set、mutation condition、rollback/final guard 去重：HOME resolver、preferred/package guards、service visibility、child/KFT、Accessibility iterations 與 final guards 不因新檔名而成為新 writer 證據。

下一步僅限 host-side：path/schema/manifest/SHA-256 檢查、saved guard 比對、source/permission/caller/user/sink join、Settings resource/overlay diff、ION DT_NEEDED/relocation/policy join、OTA EOF/provenance review。不得重送 setter、切換 child、enable Accessibility、呼叫 private Binder、開 driver node/ioctl、送 OTA/OOBE、reboot、root 或 partition payload。

## 主要未閉合缺口

1. User-0 Fire restoration writer 的 production caller、identity、user scope 與 sink。
2. KFT 合法 caller/provenance，以及 child-scoped writer 之外是否存在 User-0 side effect。
3. H2 permission holder/grant/requester 與 Binder caller identity。
4. ION/native 實際 process/domain load、`/dev/ion` gate 與 effect。
5. OOBE/BootAfterSystemOTA 的 exact delivered user、native updater/fosinit handoff 與 partition caller chain。

