# Phase 6TD：未整合高價值結果 inventory

日期：2026-08-10  
範圍：只盤點共享工作區既有 `work/` reports/CSVs，並以公開提交
`3d68f0046` 的 tracked tree、`findings/` 與 `output/tables/` 做引用比對。
沒有重新測試、沒有連裝置，也沒有執行 Binder、driver、OTA、recovery、root
或任何裝置狀態變更。未修改其他既有檔案。

## 判定方式

- `absent from 3d68f0046` 表示該候選檔案本身不在該提交的 tree；不表示其內容必然完全未被公開 synthesis 使用。
- `public_finding_citation` 區分「沒有 exact work-path citation」與「結果已被 public finding/table thematic/directly 吸收」。因此不把已公開的同一 bounded conclusion 再標成新 finding。
- `report_sha256` 是目前工作區候選檔案本身的 SHA-256，作為 inventory identity；`source_anchor_hashes` 保留報告內可直接取得的來源/輸入 hash。省略號表示原報告本身只保存 abbreviated hash，未在此輪補算。
- 所有候選均可安全以 host-only 的既有檔案重讀、hash check、靜態 source-to-caller-to-sink join 重現；「可重現」不包含重新執行 runtime、Binder、driver、OTA、root 或 OOBE。

## 結果摘要

真正不在 `3d68f0046` 的高價值主題報告是 5 份：driver/root boundary 1 份、Amazon PM/DCPMS/HOME/PMS writer 2 份、OTA/native/root boundary 1 份、OOBE/HOME/PMS user-scope 1 份。另有 2 份 rtmutex QA 檔案不在提交中。優先主題的其餘近期 work reports/CSVs（例如 Amazon PM caller/proxy、DCPMS/exported surface、HOME/PMS writer、OTA/native、driver caller）已存在於公開提交的 input tables，故不列為未整合檔案。

| 候選 | 公開狀態 | 結果是否已被公開內容吸收 | 安全重現性 |
|---|---|---|---|
| `luna_worker_kernel_driver_privilege_inventory_20260810.md` | 檔案缺席 | 是，主題結果已在 GED/CMDQ/ION/SELinux driver closure 與 privilege-route table 出現；無 exact work-path citation | host-only reread/hash |
| `luna_worker_next_ipc_ota_inventory_20260810.md` | 檔案缺席 | 是，Amazon PM、KFT/OOBE、updater/native 結論分散於相應 public findings | host-only reread/hash |
| `luna_worker_ota_init_privilege_inventory_20260810.md` | 檔案缺席 | 是，OTA/recovery/init/SELinux boundaries 已由 public findings 吸收；無 exact work-path citation | host-only static review |
| `luna_worker_phase6mo_inventory_20260810.md` | 檔案缺席 | 是，直接對應 public `findings/phase-6mo-oobe-context-user-scope.md` 與 Phase 6MN closure | host-only reread/hash |
| `luna_worker_privilege_ipc_inventory_20260810.md` | 檔案缺席 | 是，KFT/PMS/DPM/OOBE/DCPMS 邊界已在 public control-surface tables/related findings 表示 | host-only source join |
| `qa-source-verification-20260806-01/comparison.csv` | 檔案缺席 | 是，結果已在 Phase 5BJ/5BG source-semantic findings 表示；無 exact QA-path citation | host-only marker comparison |
| `qa-source-verification-20260806-01/result.md` | 檔案缺席 | 是，同一 rtmutex pre-fix 結論已公開；無 exact QA-path citation | host-only reread/hash |

完整欄位、候選檔案 hash、來源 anchor hash、結果與重現限制見同名 CSV。

## 不應升格的結果

- PS7331 futex/rtmutex：只有 source-level pre-fix cleanup identity candidate；沒有同一次 stock runtime mismatch、residue、memory effect 或 privilege transition。
- GED/CMDQ/ION：既有 evidence 分別支持 shell query、source/config surface 或 policy/node metadata；不支持 ordinary app 可達的 higher-impact operation 或 LPE。
- Amazon PM/DCPMS/HOME/PMS：KFT writer 是 supplied child/profile `UserInfo.id` scope；PMS/DPM gates 仍在；沒有已證實的低權限 User-0 Fire/HOME package-state writer。
- OTA/native/init：recovery/updater partition-write capability 與 OOBE lifecycle 是 privileged/static boundaries；沒有普通 shell/APK caller、OTA replay、root loader 或 SELinux bypass 證據。

以上是未整合檔案的 inventory，不是新增公開 finding，也不授權任何後續裝置或高風險測試。
