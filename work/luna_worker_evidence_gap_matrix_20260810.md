# Phase 6 證據缺口矩陣（2026-08-10）

## 盤點範圍與基線

本文件是 host-only、唯讀證據整理。只引用工作區既有的 Phase 6 findings、
ADB 原始 capture、artifacts 與 Git 狀態；本輪沒有執行 ADB、Binder／
`service call`、ioctl、Root/exploit、reboot、OTA/recovery/updater，也沒有
重做 priority、set-home、KFT replay 或 updater tests。未修改既有檔案、未
commit、未 push。

目前實際 Git HEAD（本輪讀取）：

```text
e8ce51c0afdbbccf8e81c6fc62ea5bdd3e965c0d
```

工作區有大量既有未提交／未追蹤內容；因此本文把檔案內容當作保存的證據，
不把各份較早 worker report 內的歷史 HEAD 當成目前 HEAD。

## 已有直接證據（不列為缺口）

| 已證實觀察 | 現有證據 |
|---|---|
| User 0 目前由 Fire HOME resolver 選中，priority 50；有 3 個 HOME candidates；User 0 與 User 10 狀態分開 | `findings/phase-6mv-runtime-readonly-report.md`；原始檔 `adb/phase6mv/PHASE6MV-READONLY-20260810-01/home_resolve.stdout.txt`、`home_candidates_cmd.stdout.txt`、`firelauncher_package_dump.stdout.txt`；同批 `sha256sums.txt` |
| 保存的 read-only service checks 顯示 Amazon private service 名稱雖在 service list，shell 查詢結果為 not found；這不是 shell 可用的 Binder relay | `adb/phase6mv/PHASE6MV-READONLY-20260810-01/service_list.stdout.txt`、各 `service_*_stdout.txt`；`adb/phase6bk/PHASE6BK-SERVICE-RO-20260810-01/`；`findings/phase-6mv-runtime-readonly-report.md` |
| 42-row caller→permission→identity→sink→user-scope ledger 沒有 selected untrusted caller 到 User-0 Fire HOME/package sink 的路徑 | `findings/phase-6mn-ipc-user-scope-closure.md`；`artifacts/phase6mn-ipc-user-scope-20260810-01/route-matrix.csv` |
| 已索引的 PMS/HOME/package-state sinks 沒有新的 Amazon User-0 HOME setter；KFT writer 是 supplied child/profile user scope | `findings/phase-6mw-home-state-sink-closure.md`；`findings/phase-6kv-pms-home-caller-closure.md`；`findings/phase-6mx-amazon-pm-caller-provenance.md` |
| AmazonApplicationFlags 的四個 mutator 有 permission→user-indexed persistence；保存的第一批 consumer 沒有直接 HOME writer | `findings/phase-6mu-amazon-application-flags-closure.md` |
| OTA/update-binary 有 extraction、block verification 與 named-partition write capability；沒有執行路徑或 shell/ordinary-app caller 證據 | `findings/phase-6nf-ipc-ota-evidence-synthesis.md`；`findings/phase-6md-native-updater-path-audit.md`；`findings/phase-6mk-updater-dispatch-closure.md`；`findings/phase-6mm-updater-blockimage-closure.md` |

上述證據支持「目前 Fire HOME、private service shell boundary、child-scoped
KFT、以及 privileged/static OTA capability」；它們都不是穩定、無 Root 的
替代 HOME 成功證明。

## 去重後 gap matrix

狀態定義：`直接缺口` 表示研究目標所需的 caller／user／sink／持久性鏈尚未
被現有檔案直接證明；`bounded negative` 表示選定 corpus 內沒有找到，但不
是全系統不存在證明。

| ID | 研究目標對應 | 現有證據已到哪裡 | 尚未有的直接證據 | 狀態／避免重複 | 最小安全分析 |
|---|---|---|---|---|---|
| G1 | 無 Root、穩定替代 User-0 HOME | read-only runtime 仍是 Fire priority 50；既有 preferred-state 寫入不改變有效 resolver；private service shell lookup 不可用；既有 workaround 不是 permanent HOME replacement | 沒有任何現有檔案直接證明第三方／普通 app 能持久成為 User-0 HOME，或能讓 Fire priority/protected gate 失效 | **核心未閉合**；不重跑 priority、set-home、component disable、KFT replay 或 foreground workaround | 只整理既有 HOME state、resolver、持久性與 reboot 邊界，將「foreground redirect」與「formal HOME replacement」分開；不新增裝置測試 |
| G2 | 可證明的 IPC 路徑 | 6MN 以 bounded ledger 排除了 selected untrusted→User-0 Fire sink；6MX 確認 `IAmazonPackageManager` 沒有 formal HOME setter；其他 Amazon interfaces 有 proxy/publication 或部分 sink | 完整 Amazon caller universe、每個 interface 的 permission／Binder identity／target user／HOME/package sink 尚未閉合；尤其不能由 service name、proxy 或單一 invoke site 推出可達 relay | **直接缺口**；6MN/6MX 已做的 inventory 不應重做 | 從保存 disassembly 的一個未閉合 interface 做 host-only caller→permission→identity→user→sink 表；遇到 native/reflection 即標 unresolved，不發 transaction |
| G3 | OOBE/OTA lifecycle 是否可成為穩定 HOME 路徑 | `BootAfterSystemOTAReceiver`、protected broadcast、OOBE helper 的 component/setup side effects 已靜態證實；6MO 已把 Context-derived user boundary 接上 | exact numeric post-OTA user 與 `Context`→`ContentResolver`／PackageManager 的最終 user handle 仍未直接證明；也沒有證據顯示它寫 preferred HOME 或 Fire User-0 state | **直接缺口，但較像排除性 closure**；不 replay broadcast、不執行 OTA/OOBE | 對保存的 OOBE source、framework client 與 receiver registration 做一次 data-flow closure：只回答 user handle、component/settings sink、是否有 HOME/preferred/Fire literal |
| G4 | Amazon IPC 是否能繞過 HOME/package gate | `IAmazonUserManager` tx3 已是 child/profile-scoped writer；tx4 是 settings-only；prewarm 是 process/resource sink；DPM/input/window/accessibility slices 不是已證實 HOME sink | 尚未有完整證據把未索引 Amazon methods 接到 ordinary caller 且最終寫入 User-0 HOME、preferred activity 或 Fire component state | **bounded negative 尚未升格 global negative**；不重做已閉合 tx3/tx4、prewarm、InputManager 或 service lookup | 只補未索引 methods 的靜態 method/permission/user/sink provenance；任何只到 process、PIP、settings、profile picker 的結果均標「非 HOME」 |
| G5 | 可證明的無 Root OTA/更新路徑 | PS7331 updater registry、script entrypoints、`package_extract_file`→`ota_open`、block-image handlers 與 write capability 已有保存 closure；官方 OTA/source/boot/system/vendor files 可 hash | verifier→recovery→updater 的完整 handoff、canonicalization/readlink marker 到 extraction/write 的實際 data-flow、以及 ordinary shell/app caller 均未直接證明；更沒有「OTA 後替代 HOME」結果 | **直接缺口，但不是安全的 live route 候選**；不執行 updater、recovery、crafted/symlink OTA 或 partition write | 使用既有 native `.text`/debugdata/CFG 與 Java staging artifact，輸出 `direct edge / indirect-unresolved / not in selected graph` 三態鏈；不把 capability 當 reachability |
| G6 | 由 Amazon flags/metadata 或未索引 consumer 間接影響 HOME | 四個 mutator 的 persistence、package/user record schema、已見 consumer（recency/game-mode/compatibility）已閉合到「無直接 HOME writer」 | 是否有 corpus 外、reflection/generated/native 或後續 consumer 將 flags/metadata 轉成 launcher/HOME/package-state 決策，仍未完全證明 | **低優先間接缺口**；不重做 6MU/6MX persistence 與 caller scan | 只沿既有 `AmazonApplicationFlags` readers 到第一個外部 consumer；若沒有 package/component/preferred sink 即結束為 bounded negative |

## 判斷

目前沒有現有檔案直接證明研究目標中的「穩定、無 Root、不可修改分割區的
替代 HOME」。最強的現有結論是 bounded negative：保存的 runtime capture
仍選 Fire，selected IPC ledger 沒有 untrusted→User-0 HOME/package sink，
而 OTA 只證明 privileged/static write capability。`G1` 是目標本身的未閉合
結論，不應把 G2–G6 的靜態候選誤寫成 workaround。

## 建議下一個最小安全分析

優先做 **G3：`BootAfterSystemOTAReceiver` → Context →
`ContentResolver`／PackageManager 的 host-only user-scope data-flow closure**。
這是目前最窄、最直接、且不重疊於已完成 priority、set-home、KFT replay、
6MN ledger 或 updater dispatch 的分析。輸出只需一張小表，欄位為：

```text
receiver/registration → guard → Context construction → user handle/API
→ component/settings sink → HOME/preferred/Fire literal → unresolved boundary
```

成功條件不是找到 workaround，而是直接證明其中一項：

1. sink 只作用於 setup/OOBE component/settings，且沒有 User-0 HOME/preferred
   writer；或
2. 存在具體 User-0 HOME/package sink，並能以保存 source/disassembly 指出
   permission、identity 與 user mapping。

若 G3 只得到 setup-only 或 unresolved，下一個才考慮 G2 的單一未索引
Amazon interface 靜態 caller closure；G5 保留作為獨立 OTA provenance 分支，
不應用 OTA 執行來補證據。

## 來源索引與安全界線

主要 findings：

- `findings/phase-6mv-runtime-readonly-report.md`
- `findings/phase-6mn-ipc-user-scope-closure.md`
- `findings/phase-6mw-home-state-sink-closure.md`
- `findings/phase-6mx-amazon-pm-caller-provenance.md`
- `findings/phase-6mu-amazon-application-flags-closure.md`
- `findings/phase-6my-ota-receiver-package-helper-closure.md`
- `findings/phase-6md-native-updater-path-audit.md`
- `findings/phase-6mk-updater-dispatch-closure.md`
- `findings/phase-6mm-updater-blockimage-closure.md`
- `findings/phase-6nf-ipc-ota-evidence-synthesis.md`

主要 raw capture：`adb/phase6mv/PHASE6MV-READONLY-20260810-01/`、
`adb/phase6bk/PHASE6BK-SERVICE-RO-20260810-01/`、
`adb/phase6bk/PHASE6BK-STATE-RO-20260810-01/`、
`adb/phase6mx/PHASE6MX-SERVICE-HANDLE-LOOKUP-20260810-01/`。

本文件只新增於 `work/`；沒有 commit 或 push。
