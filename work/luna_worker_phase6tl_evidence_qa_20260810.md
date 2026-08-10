# Phase 6TL — host-only cross-evidence QA

日期：2026-08-10（Asia/Taipei）  
基準：公開 commit `56ac917a048cd876db03065bffee4bdb9a33355a`。  
範圍：只讀 Phase6TE–TI outputs、PS7331 source/OTA/boot artifact manifests，以及既有 Phase6TF–TH 與其 raw/input manifest；未接觸設備，未執行 OTA、recovery、sideload、flash、reboot、Binder、driver、root 或 exploit。未修改既有報告或檔案。

## 結論

TE–TH 的 input manifest `output/tables/phase6te-th-input-manifest.sha256` 可重算，10/10 筆均與 commit 內容一致。Phase6TI 的兩個 redacted summary 檔也在 commit，且其 snapshot manifest hash 及 raw path 是有界定的：raw `adb/phase6ti/PHASE6TI-DEVICE-READONLY-20260810-01` 不在公開 commit，因此公開引用應落在 `findings/phase-6ti-readonly-snapshot.md` 與 `output/tables/phase6ti-readonly-state.csv`，不可把 raw 檔案當成 public-commit 可直接核驗的 citation。

主要可修正問題集中在 Phase6TG 的 OTA matrix：

- TG-01、TG-03、TG-04 引用的 `firmware/original/...`、`firmware/extracted/PS7331/...` 與 `META-INF/...` 路徑不在 `56ac917a` tree；這些只能標成 local/uncommitted provenance，或改引 commit 內的 Phase 5/6 artifact manifest。
- TG-05 matrix/CSV 指向 `phase6mk-updater-dispatch-20260810-01`，但公開 commit 的實際 artifact 是 `phase6mk-updater-dispatch-20260810-04`；CSV 所列 hash `443c...` 也不是該 `registration-dispatch.csv` 的 hash，正確 commit 內容 hash 是 `d88e35...`。
- TG-06 把 `selected-functions.csv` 的 row source 寫成 summary hash `1cb21f...`；該 hash 實際對應 `summary.json`，而 `selected-functions.csv` 的 commit hash 是 `113caf...`。應拆成 source hash 與 summary hash。
- TG-07、TG-14 的路徑與 hash 可在 commit 內核驗；TG-02 的 `members.json` 也可核驗，但其 `path` 欄位是被檢查的 extracted output location，不是 commit tree 中的 raw extracted directory，應標成 derived/output path。

## capability 與 caller 分類

整體分類方向正確：TG-03/TG-04 的 partition/block-image writer 是 capability/static writer，不是 shell caller；TG-08/10/11 也沒有把 reachability 或 receiver metadata 升格成 ordinary caller。TH 對 `POSITIVE_LIBRARY_ONLY`、`UNKNOWN_RESIDUAL`、`CONDITIONAL_NOT_SHIPPED_ESTABLISHED` 和 OTA adjacent boundary 的區分一致，未發現把 source capability 誤寫成 production caller 的明確錯誤。

唯一值得改善的欄位語意是 Phase6TF CSV 的 `production_caller=YES`：四列描述的是 artifact 內部 production caller/edge，但同列 `external_reachability=UNKNOWN`。為避免下游讀者把 YES 解讀成外部可呼叫 caller，建議後續改欄名為 `internal_production_edge`，並保留 `external_reachability=UNKNOWN`；不需改變目前結論。

## 高價值、尚未整合但可安全引用的文件

1. `artifacts/phase6mk-updater-dispatch-20260810-04/registration-dispatch.csv`：24 個 install callback registry 的 host-only 靜態 join；可補強 TG-05，但不能寫成 public API 或 shell caller。
2. `artifacts/phase6ne-updater-cache-flow-20260810-03/selected-functions.csv`、`direct-call-edges.csv`：CacheSizeCheck/canonicalization bounded flow；可補強 TG-06，但 full dataflow 仍 Unknown。
3. `artifacts/phase6kt/recovery-verifier-audit-20260810-01/audit.json` 與 `findings/phase-6kt-recovery-verifier-provenance.md`：verifier/staging → privileged handoff；可安全引用為 provenance，不能補成 native recovery caller。
4. `artifacts/phase6nb-amzn-drv-test-source-closure-20260810-04/phase6nb-amzn-drv-test-source.csv`：Amazon diagnostic source capability；可補強 TG-14/TH，但 selected config、shipped node、SELinux caller 仍未閉合。
5. Phase6TF 的 H2ClientService chain：是高價值 exact-build static residual，可引用為 internal production edge；bind permission holder、exported/service declaration、external client 仍 UNKNOWN，不能升格 ordinary-app reachability。
6. Phase6TI redacted state table：可作 exact-build runtime snapshot anchor；raw ADB directory 只在 local provenance 中存在，不是公開 commit citation。

## 可修正事項與最小下一步

可修正事項詳見 companion CSV。最小且安全的下一個 host-only action 是：建立一份 canonical citation map，將 TG-05 改為 `phase6mk...-04`、TG-06 分離 selected-functions/direct-call-edges/summary 三個 hash，並將 TG-01/03/04 明確標成 local-only 或替換為 commit 內的 OTA/boot manifest；同時把 Phase6TF 的 YES 欄位改成 internal-edge 語意。這只涉及公開檔案的 path/hash/label 修正，不需設備或任何 runtime action。

本 QA 不新增漏洞、root、低權限可達性、OTA 執行或 caller proof 結論。

