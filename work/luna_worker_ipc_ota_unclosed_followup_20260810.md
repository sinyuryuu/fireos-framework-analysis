# Phase 6J–6PY IPC / OTA / OOBE 未閉合 follow-up

日期：2026-08-10。範圍限於工作區內既有 PS7331 7.3.3.1 install/OTA artifacts、VDEX/decompile/source、manifest 與已保存 Phase 6J–6PY evidence 的 host-only 稽核。未執行 adb、service call、Binder transaction/replay、broadcast、OTA/recovery、mutation、root、reboot 或分割區操作。

## 結論

沒有新的證據能閉合「低權限 caller → 未受保護 gate → system/root identity → User-0 package state、HOME/preferred state 或 root/partition sink」鏈，也沒有證據支持 vulnerability。以下 6 條是仍需保留的 bounded unknown，因為至少一個 caller、permission/gate、identity boundary、downstream sink 或 exact user mapping 尚未在保存 corpus 中完整閉合；它們不等同於漏洞。

1. `IAmazonPackageManager` tx6/tx7 proxy receiver register/deregister：interface 與 proxy/broadcast sink 已見，但 effective external authorization、caller universe、identity relay、下游 receiver effect 未閉合。
2. Play Store exported `LauncherConfigurationReceiver`：manifest exported boundary 已見，JADX 明確跳過 723 instruction-unit body；package/component target dataflow 不能作 bounded negative。
3. Play Store exported `DseService`：permission-gated exported service 與 DSE bookkeeping 已見，但 skipped/未完整復原的 target flow 尚不能排除 package/install side effect；沒有 Fire Launcher/HOME writer 證據。
4. OTA verifier/staging → `UpdateSystem.install` → recovery/native updater：Java 驗證與 handoff 已閉合到 privileged boundary，但 exact native/recovery caller provenance、indirect dispatch 與 path-policy relation 未閉合；未證明 shell/ordinary-app caller。
5. `BOOT_AFTER_SYSTEM_OTA` → OOBE receiver：system_server phase-550 + `isUpgrade` sender、protected action、OOBE component/settings sinks 已閉合；receiver 的 exact delivered numeric user 與 post-OTA resolver timeline 未閉合。這是 trusted lifecycle candidate，不是 ordinary broadcast route。
6. 7.3.3.1 outer source archive tail：既有 listing 未到 EOF，故不能對未列出的 post-install/recovery member 作完整 negative；目前沒有 untrusted caller 或 package/HOME sink 證據。

## 已排除或已閉合的相鄰路徑

既有 evidence 已將 KFT tx3 限定為 child/profile-scoped writer 並由 User-10/User-0 downstream gates 阻斷；ordinary prewarm 只有 process/resource effect；tx4 是固定 setup settings deputy、沒有 package/HOME sink；Amazon flags/metadata 是 metadata persistence、未見 preferred/component/HOME setter；InputManager、profile helper、window/PIP、DPM restriction、fosdebug 與 local `fosinit` callbacks 沒有已證實 requested sink。Fire Launcher User-0 read-only baseline 仍為 resolver comparator。這些不在本 follow-up 重做。

另外，manifest 的 `uses-permission`、interface token check 或「bounded method 沒看到 permission marker」本身都不被記錄為漏洞；只有保存 evidence 直接顯示的 gate、caller、identity、sink 與缺口被列出。

## 證據索引與安全下一步

逐列資料見 companion CSV。主要依據為：`work/luna_worker_binder_sink_closure_20260810.csv`、`work/luna_worker_bootafter_ota_provenance_followup_20260810.csv`、`work/luna_worker_ota_postinstall_followup_20260810.csv`、`work/luna_worker_vending_unclosed_surface_20260810.csv`、`artifacts/phase6ps-vending-receiver-20260810-01/LauncherConfigurationReceiver.java`、`artifacts/phase6mx-amazon-pm-callers-20260810-01/caller-calls.csv` 及既有 `findings/phase-6kt-recovery-verifier-provenance.md`。

安全下一步只限 host-only：補齊 proxy receiver 的所有 static callers/manifest ownership 與 receiver downstream；取得相同 APK 的 smali/disassembly 以復原 skipped exported methods；補 native/recovery handoff 的 indirect call/dataflow；完成 source archive EOF listing；或在自然、已授權 OTA 後做 read-only package/settings/resolver observation。不得以 replay、crafted OTA、recovery、mutation 或 service invocation 取代缺失證據。

因此，本輪狀態是：**未閉合候選存在，但沒有已證實低權限高權限漏洞路徑；尚不能宣稱全部已閉合。**
