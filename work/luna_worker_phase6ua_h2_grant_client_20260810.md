# Phase 6UA — host-only exact-build H2 grant-candidate client closure

日期：2026-08-10（Asia/Taipei）

## Bounded result

只讀檢查目前已保存的 Phase6TW/UB package-permission、APK XML-tree、JADX 與 manifest/package artifacts。十個 explicit grant 均為 **POSITIVE grant candidate**，但 grant 不單獨等於 client。實際 `bindService`、`ServiceConnection`、`IH2ClientService` caller package/class 對十個 package 均未閉合；缺少對應 APK/JADX/manifest 的欄位保留 **UNKNOWN**。

三個保存 XML-tree 有 requested-permission 證據：`com.amazon.tahoe` line 70、`com.amazon.kindle.otter.oobe` line 85、`com.amazon.parentalcontrols` line 106。其餘七個 package 的 per-package requested-permission artifact 在本 bounded scope 未保存，標 `UNKNOWN`。即使 requested-permission 為 POSITIVE，也不能升級為實際 bind client。

Owner/service boundary：保存 PackageManager record 顯示 custom permission owner `sourcePackage=android.amazon.perm`, owner UID `1000`，SHA-256 `4a71d4d60cdb6c45233e270e3548f02c9ea77e9d3b3b4ed33a7aeb1e130bb798`，lines 3329–3334；H2 service resolution at line 21051 references the same permission. H2 UID/signing digest and ten grant rows are not caller identity proof.

## Static client scan

Bounded JADX contains generated `IH2ClientService` contract and H2 implementation only (`IH2ClientService.java:4–710`; `H2ClientService.java:104–267`). No external package-specific `bindService`/`ServiceConnection`/`IH2ClientService` callsite was recovered in this scope. Result is `NO_EXTERNAL_CLIENT_CLOSED` for the bounded corpus, not a universal absence claim.

## Safety boundary

No adb, device access, bind, service call, Binder replay, transaction construction, or mutation was used. No further scan expansion was performed after the bounded artifact set. Full row ledger with SHA-256, path, line, class, and classification is [the companion CSV](luna_worker_phase6ua_h2_grant_client_20260810.csv).
