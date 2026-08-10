# Phase 6QE — Amazon Framework/System Services IPC caller→sink closure

日期：2026-08-10。範圍限於工作區既有 VDEX/JADX/smali、manifest、fosinit 與 evidence；沒有執行裝置指令、Binder transaction、protected broadcast、settings/package mutation、Root、exploit、OTA、recovery 或 ioctl。只新增本報告與 companion CSV。

## 結論

CSV 整理 15 條 service publication → Stub/方法 → caller provenance → gate → identity → user scope → sink 鏈。結果沒有證明 ordinary app 或 shell 可到達 User-0 formal HOME、Fire package/component state、system/root、OTA/recovery 或 partition sink。

已閉合或 bounded 的重點：

- Amazon PM flags/metadata 的 static mutator sink 存在，但 production caller、第一個 PM/HOME consumer 與完整 user mapping 未閉合。
- ProxyReceiver tx6/tx7 的 service publication、PendingIntent creator/UID gate、map/receiver sink 已閉合；production caller 仍 unknown，保存的 ordinary self-created probe 被 gate 阻擋。
- KFT tx3 的唯一保存 caller 是 `AmazonUserManagerImpl.createChildUser`；writer 使用 supplied `UserInfo.id`，只寫 child/profile-scoped Tahoe/Fire/Launcher3 state，不是 formal HOME setter。tx3 method-local authorization 未由 bounded body 證明，不能將缺口升級為漏洞。
- tx4 確認是既有 cross-user setup-settings deputy，但沒有 PM/HOME sink；DPM restriction、DPM tx100→PMS tx73、Profile tx21/tx41 均受 role/permission/cross-user 或 downstream UID gate 限制。
- AMS observer、WMS overscan/PIP、Vending receiver/DSE 的 downstream 不是已證實的 Fire/HOME writer；缺少的 caller、注入 writer 或 skipped/partial code 保留 `UNKNOWN`。
- `BOOT_AFTER_SYSTEM_OTA` 是 system-server phase-550 + `isUpgrade()` 的 protected OTA/OOBE lifecycle；receiver 可啟用 OOBE Home 並寫 OOBE setup state，但沒有普通 caller delivery 證據。OtaService/recovery/write chain 只有 privileged capability，沒有 ordinary caller closure。

## 判定規則

`UNKNOWN` 僅表示 caller、gate、identity、numeric user scope 或 downstream consumer 的 evidence gap，不代表漏洞。`static sink confirmed` 不代表 caller 可達；manifest exported、service publication、receiver-permission argument 也不單獨證明 sender authorization。所有 user scope 只沿保存的 `UserInfo.id`、`UserHandle` 或 service Context evidence 描述，未把 child/profile 行為推廣為 User 0。

逐列 exact path、method、publication、caller、gate、identity、scope、sink、low-privilege status、classification、evidence 與安全下一步見 [CSV](luna_worker_phase6qe_ipc_caller_closure_20260810.csv)。主要 evidence 包括：`fosservices/disassembly.log`、`boot-fosframework/disassembly.log`、`artifacts/phase6mb/phase6ps/phase6jd`、OOBE/OTA source 與既有 Phase 6 findings。既有 evidence hash 依 CSV 保留；省略號只表示 companion worker 已保存的完整 hash 前綴，不是新的推測 hash。

## Residual safe closure

後續僅可做 exact-build host-only reference、alias、manifest/permission、Context/user propagation 與 skipped DEX/smali CFG 恢復。不得為補 caller provenance 而取得 private service handle、猜 parcel、重放 tx3/tx6/tx7/tx41/tx100、發送 OTA action、啟動 picker、修改 settings/package/component、執行 OTA/recovery/updater 或寫 partition。
