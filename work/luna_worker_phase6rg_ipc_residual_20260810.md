# Phase 6RG — host-only Amazon Framework/System Services IPC residual search

日期：2026-08-10。範圍限定為既有 `decompiled/baksmali`、`decompiled/jadx`、`artifacts`、`firmware/extracted/PS7331-SOURCE-20250617` 與既有 findings。未執行 adb、service call、Binder transaction、broadcast、settings/package mutation、OTA/recovery、root/exploit、driver node/ioctl 或任何裝置操作；亦未執行 PS7331 boot_unpacked/src 下程式。

## 結果

伴隨 CSV 共 14 rows。每列都按 `registration → caller → sender/input → gate → identity → user scope → sink → reachability` 展開，並將「service/exported/Stub/source capability」與「實際 caller reachability」分開。`UNKNOWN` 是證據缺口，不是低權限可達或漏洞判定。

| row | surface | residual disposition |
|---|---|---|
| 6RG-01–03 | Amazon PM metadata/proxy receiver | Stub/service 與 method-local gate 靜態確認；production caller 或跨 user 可達性未閉合。 |
| 6RG-04–05 | Amazon User Manager/KFT | trusted child-user caller、component/package 與 Settings sink 可見；ordinary caller/完整 method gate 仍 UNKNOWN。 |
| 6RG-06–07 | Amazon Profile Service | PROFILE_INTERACTION 或 downstream `INTERACT_ACROSS_USERS` gate 可見；profile/picker caller 與 user provenance 部分未閉合。 |
| 6RG-08 | Amazon DPM | restriction sink 與 identity transition 可見；active-admin/owner 之外的 caller reachability 未證實。 |
| 6RG-09 | Amazon Activity Manager/SystemUI-adjacent observer | permission-gated observer registration 與 callback sink 可見；consumer、user attribution、HOME sink UNKNOWN。 |
| 6RG-10 | SettingsProvider | generic ContentProvider write path 有 secure/cross-user/AppOps gates；Amazon/SystemUI/OOBE 的實際 caller provenance UNKNOWN。 |
| 6RG-11 | SystemUI | system/secondary-user service arrays 與 lifecycle startup 可見；每個 configured service 的 downstream IPC 尚未閉合。 |
| 6RG-12–13 | OOBE/OTA | protected boot lifecycle 與 privileged OTA capability 可見；ordinary relay/OTA caller reachability 未證實。 |
| 6RG-14 | Vending receiver/DSE | exported metadata/service surface 與內部 qualification/UID authorization 可見；accepted external sender/client UNKNOWN。 |

## 判定規則與安全後續

- service publication、manifest exported、Stub method、permission holder 或 `clearCallingIdentity` 僅記為 capability/gate evidence，不單獨升級為 caller reachability。
- 靜態存在的 sink（例如 KFT component state、SettingsProvider state、OOBE setup flags、OTA partition capability）與 `reachability` 分欄；對 caller、gate、identity、user 或 downstream consumer 缺證的列保留 UNKNOWN。
- 下一步全部限於 host-only：補 registration alias、resource/manifest、Stub dispatch、permission/UID 分支、caller provenance、user-argument flow 與 first consumer。不得 replay Binder/broadcast、建立 PendingIntent、寫 settings/package、啟動 OTA/recovery 或觸碰裝置。

CSV schema 固定為：`row_id,scope,registration,caller,sender_or_input,gate,identity,user_scope,sink,reachability,confidence,evidence,next_safe_step`。
