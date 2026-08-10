# Phase 6QD-A：未閉合 Amazon Framework/System Services IPC caller-to-sink inventory

日期：2026-08-10。只讀既有 workspace artifacts、decompiled、findings、output/tables；未接觸裝置，未送 service call/Binder/broadcast，不猜 parcel，未執行 Root/exploit、OTA、reboot、recovery 或 partition 操作。未重做 priority、set-home、disable、KFT、prewarm、tx4 或 InputManager 已閉合路徑。

## 結論

本輪保留 12 個尚未閉合的 caller→accepted gate→identity→sink 候選。可確認的是靜態 wrapper、權限/角色邊界或 privileged lifecycle sink；沒有任何 row 證明低權限 caller 能到達 User-0 HOME、preferred activity、Fire package/component state、credential、SELinux 或 OTA write sink。`UNKNOWN` 僅表示 caller、gate、identity、user scope 或 downstream sink 證據缺口，不是漏洞判定。

已排除既有閉合結果：ordinary prewarm 只到 process/resource；tx4 只到 setup settings；KFT tx3 已限定 child/profile user scope 且下游 gate 已拒絕未授權 User-0/User-10 mutation；InputManager、標準 PMS HOME setter、priority/set-home/disable tests 不重做。

## Row disposition

| ID | 未閉合鏈與目前可證實邊界 | status | 下一個安全步驟 |
|---|---|---|---|
| IPC-U01 | Amazon PM flags/metadata mutators：`ADD_RM_PKG_METADATA` → explicit user → `AmazonApplicationFlags`; first PM/HOME/component consumer未閉合 | `STATIC_SINK_CONFIRMED_CALLER_UNKNOWN` | 靜態追 flags persistence/consumers；不呼叫 private Binder |
| IPC-U02/U03 | Proxy receiver register/deregister：PendingIntent creator/system-app 與 caller-UID ownership gate；production caller 與 downstream sink UNKNOWN | `STATIC_IMPLEMENTATION_CONFIRMED_PRODUCTION_CALLER_UNKNOWN` | 只查 offline system-created PendingIntent provenance |
| IPC-U04 | Amazon DPM restriction：policy permission/UID branch → clearCallingIdentity → UserManager restriction；非 HOME/package sink | `STATIC_POLICY_SINK_CONFIRMED_CALLER_UNKNOWN` | 靜態補齊 role/permission branches |
| IPC-U05/U06 | Amazon Profile Service：permission-gated launcher/profile picker → internal flow/startActivityAsUser；沒有已證實 PM/HOME writer | `ORDINARY_REACHABILITY_UNKNOWN` | 靜態追 registration、user/component args |
| IPC-U07 | AMS activity observer callback：ComponentName callback；consumer/registration與 HOME sink UNKNOWN | `CALLER_TO_HOME_SINK_UNKNOWN` | 靜態追 observer consumers |
| IPC-U08 | WMS overscan/PIP/status-bar wrappers；caller/permission/identity closure incomplete，未見 PM/HOME sink | `CALLER_AND_GATE_UNKNOWN` | 靜態補 method-local gate |
| IPC-U09 | H2 exported service：signature `BIND_SERVICE` + workflow → createAdult/ChildUser；無 Fire/HOME writer | `LOW_PRIVILEGE_CALLER_UNKNOWN` | 靜態對齊 manifest、caller signature、user flow |
| IPC-U10 | system-server boot phase 550 + upgrade → protected BOOT_AFTER_SYSTEM_OTA → OOBE component/settings sinks；Context/user mapping未閉合 | `ORDINARY_RELAY_UNKNOWN` | 靜態追 Context/user handle；不 replay |
| IPC-U11 | Vending holder/grant metadata → generic enabled-state writers；exact caller/input/Fire target UNKNOWN | `HOLDER_METADATA_ONLY_WRITER_STATIC_CALLER_UNKNOWN` | 只查保存 APK/JADX caller provenance |
| IPC-U12 | OTA controller/recovery privileged capability → partition/block-image/post-install；ordinary caller與 Framework sink未建立 | `PRIVILEGED_CAPABILITY_ONLY_CALLER_UNKNOWN` | 靜態查 registration/function-pointer provenance；不執行 OTA |

## Evidence rule

CSV 保留每 row 的 exact file/class/method/offset、caller、permission/calling UID、identity、sink、status、next safe step 與 evidence hash。Hashes 是既有 disassembly/finding evidence 的 SHA-256；本輪新輸出 hash 於交付時另計。任何「service published」、「permission holder」、「static setter」、「clearCallingIdentity」或「generic writer」都不單獨等同 caller reachability、accepted gate 或成功 sink。
