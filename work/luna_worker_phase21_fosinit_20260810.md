# Phase 21A — FOSINIT fan-out

日期：2026-08-10（Asia/Taipei）  
範圍：host-only 靜態 join；未執行 ADB、Binder/service call、broadcast、driver、OTA、root 或任何裝置操作。

## 結論

以 `P20D-FOSINIT-001` 為輸入，沿保存的 244-entry fosinit ledger，將尚未閉合的 registration → implementation → method gate → caller/identity → user scope → sink 做 bounded join。結果新增 13 個唯一 `P21A-*` rows，集中在 P20D 指定的 residual：settings、package/component、user/toddler/KFT auxiliary、OTA/recovery、CRL/cert-pin、core、receiver-filter 與 all-user relay。

這不是對 244 entries 的 reachability 或漏洞宣告：`UNKNOWN` 只表示現有 host evidence 沒有證明該邊；`UNRESOLVED_AUTHZ_BOUNDED` 表示註冊/實作或 sink 已見，但 caller/authz 尚未閉合。P19/P20 已閉合的 Amazon Profile picker、KFT tx3/H2、AmazonWindowManager、DCPMS、一般 HOME resolver 與既有 direct setter rows 不重複建立。

## Input / join method

- Primary residual ledger：`work/luna_worker_phase20_reconciliation_20260810.md/.csv`，`P20D-FOSINIT-001`。
- Registration inventory：`artifacts/phase6jd-fosinit-20260808-01/extraction-manifest.tsv`、`artifacts/phase6h/phase6h-framework-ipc-20260804-01/fosinit-edges.csv`；既有 completeness row 明確記錄 244 entries。
- Implementation/gate evidence：exact fosinit XML、`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`、`decompiled/jadx/ota-PS7331`、既有 `phase6va` residual CSV。
- Sink priority：package/component/PMS、HOME-adjacent resolution, Settings, user/profile, OTA/recovery. Registration alone was not treated as caller reachability.

每一列至少保留 registration、implementation、entry、caller、gate、identity、user_scope、sink、runtime、missing_edge；其中 runtime 明確標記為 host-only evidence，沒有 fresh device result。

## Row map

| ID | Residual join | Disposition |
|---|---|---|
| P21A-001 | Amazon app/TV settings callbacks → SettingsProvider | UNKNOWN settings key/permission/identity join |
| P21A-002 | PackageWhitelister → PMS package policy | BOUNDED_PARTIAL; package/user writer unresolved |
| P21A-003 | PackageRecency → delayed package-recency broadcast | BOUNDED_PARTIAL; explicit userId, downstream consumer unresolved |
| P21A-004 | FactoryResetWhitelist → recovery | UNKNOWN caller/gate/sink |
| P21A-005 | auxiliary Amazon user/profile callbacks → package/component writers | BOUNDED_PARTIAL; prior KFT tx3 excluded |
| P21A-006 | ToddlerMode callbacks → Secure settings/window policy | BOUNDED_PARTIAL; user -2 semantics unresolved |
| P21A-007 | KindleFreeTime activity/stack callbacks | BOUNDED_PARTIAL; child scope, exact propagation unresolved |
| P21A-008 | FireOSSystemOTA callback → OTA/recovery | UNKNOWN caller/path/sink |
| P21A-009 | CRLSetManager Binder/receiver → trust/update files | UNRESOLVED_AUTHZ_BOUNDED |
| P21A-010 | Amazon cert-pin receiver → update files | BOUNDED_PARTIAL caller/validation |
| P21A-011 | core bootstrap/debug service | UNKNOWN debug gate and side effects |
| P21A-012 | ReceiverFilter → PMS receiver/component filtering | BOUNDED_PARTIAL |
| P21A-013 | TabletBroadcastRelay → `UserHandle.ALL` relay | UNRESOLVED_AUTHZ_BOUNDED |

## No-repeat / safety boundary

The rows deliberately do not reopen Phase 19/20 closures. In particular, they do not re-audit the closed Profile picker, H2/KFT transaction, WindowManager PIP/overscan, DCPMS, direct User-0 HOME setter, or runtime service reachability. No callback, Binder method, receiver, settings writer, package writer, recovery/OTA path, or user lifecycle was invoked.

The next safe step is another host-only source join for the `missing_edge` in each row: recover method bodies, manifest permissions/exportedness, `getCallingUid`/`clearCallingIdentity` ordering, explicit UserHandle propagation, and concrete PMS/Settings/file/receiver sink. Do not convert an absent edge into a vulnerability claim.

See the machine-readable ledger: `work/luna_worker_phase21_fosinit_20260810.csv`.
