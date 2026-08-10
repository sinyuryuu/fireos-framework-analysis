# Broad surface triage after Phase 13

日期：2026-08-10。這是主機端唯讀盤點；未執行 adb、Binder/service call、root/exploit、driver/ioctl、OTA/recovery、grant/revoke 或任何設備/套件狀態修改。Launcher surface 排除；已在 Phase 10–13 關閉的 HOME/KFT/parental-owner 路徑只作去重引用。

## 結論

盤點得到 14 個非 Launcher surface：OOBE component/settings 與 OTA lifecycle、Amazon 私有 component-policy writers、DCPMS exported policy receivers、SettingsProvider、DPM hidden/suspend，以及 4 個 Phase 13 native nodes。只有 BS-001/002/004/005/006/009/010/011–014 是明確 sink 或 ioctl/driver sink；其中 BS-001/002/004/005/006/009/010 的 caller、UID/domain、user attribution 或 policy provenance 尚未形成完整可達鏈。DCPMS receivers 目前只到 policy persistence/evaluator，沒有 package/HOME sink。四個 native rows 仍是 Phase 13 的 UNKNOWN，不能由 config、node mode、library symbol 或 init ownership 推導出 caller reachability。

## 去重邊界

AmazonUserManager KFT tx3 的 Fire/Tahoe/Launcher3 component writer、Amazon DPM persistent-preferred 路徑、Parental Controls profile-owner 與 HOME resolver ranking 已由 `work/luna_worker_parent_profile_dpm_sink_closure_20260810.md`、`work/luna_worker_phase12_existing_evidence_20260810.csv` 和 Phase 13 driver join 覆蓋；本次不將它們列為新的 User-0 relay。SettingsProvider 與 DPM rows 保留是為了 exact sink 對照，不代表新增成功 caller。

## 主要缺口與安全下一步

最有價值的下一步是取得同一 PS7331 build 的新 host artifact，補齊 OOBE/EnableDisableComponentAction 的實際 caller、manifest/action publication、explicit user propagation，以及 driver 的 shipped object/DTB、ueventd/file_contexts、merged allow、native opener。不得以 broadcast、Binder、service call、ioctl 或設備測試補洞。

完整逐列證據、confidence、missing edge 與 next safe step 見 [CSV](luna_worker_cont_broad_surface_20260810.csv)。
