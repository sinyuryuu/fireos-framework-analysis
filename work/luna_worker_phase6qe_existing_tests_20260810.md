# Phase 6QE：既有測試與高影響權限缺口整理

日期：2026-08-10  
範圍：只讀既有 `adb/`、`artifacts/`、`findings/`、`tools/scripts/`；沒有重跑已排除的 priority APK 矩陣或 set-home 組合，沒有修改裝置，也沒有執行未知 Binder、driver、OTA、recovery、root 或 partition 操作。

## 結論

目前沒有由普通 shell／第三方 APK 導向 User-0 Fire Launcher disable、正式 HOME replacement、system/root identity 或 partition sink 的已閉合鏈。

已實測且有 raw evidence/hash 的高影響邊界：

- Fire 的 package/component disable、force-stop 保護在狀態變更前拒絕。
- Tahoe package enable 不足以形成 HOME；FreeTime component enable 被 shell gate 拒絕。
- KFT writer 確認存在，但只對 child/profile 的 target user 寫入 launcher state；User-0 restoration writer 仍未確認。
- 已安裝 Microsoft Accessibility service 能 bind 但 callback 為空；另有明確標界的 user-consented Accessibility／ADB-connected foreground fallback，但不是 HOME replacement。
- DPM/Profile Owner persistent-preferred 路徑有 owner/admin/UID gate；Backup passive capture 沒有 active restore writer。
- OOBE/OTA receiver 與 priority-100 OOBE HOME 受 protected broadcast、system-server OTA lifecycle、OOBE/demo/shared-pref gate 約束；沒有做人工觸發。
- Amazon private service 名稱可出現在 `service list`，但 shell UID 2000 的 `service check/find` 被 SELinux 擋下；名稱可見不等於 handle 或 transaction 可用。
- Phase 6QA/6QB/6PZ 的 residual host-only closure 未找到新的低權限 caller → system identity → PMS/HOME/Fire/root 鏈。

完整逐項矩陣見 [luna_worker_phase6qe_existing_tests_20260810.csv](./luna_worker_phase6qe_existing_tests_20260810.csv)。

## 證據分級

### 已確認、且有 raw evidence/hash

1. **Package/component disable gate**：6BK/6BL 的 Tahoe package-vs-component 實測；6FA 的 Fire force-stop protected-package rejection。  
2. **KFT/child user**：既有 managed child 的 Tahoe HOME、Fire per-user state、switch-back User-0 Fire，以及 focused log 沒有 User-0 restoration writer。  
3. **Accessibility**：6DE 的 installed Microsoft service bind-but-no-redirect；6IQ/F-118 的 foreground fallback 行為與限制。6PD 的 PendingIntent APK update 失敗亦有 raw rejection/hash，但其 runtime 行為未測。  
4. **PM/DPM/Profile**：DPM tx100 → PMS tx73 的 static trusted path、Profile Owner/passive lifecycle capture、Backup disabled/no active restore。  
5. **OOBE/OTA**：6Q read-only baseline、BootAfterSystemOTAReceiver 靜態控制流、固定 partition updater script 與 post-install closure。  
6. **Service visibility**：Amazon private service inventory 與 AVC/service-check denial capture。

各來源的 SHA-256 由原始目錄的 `sha256sums.txt`、既有 evidence index 或 finding 明列；本報告不把靜態 hash 當成 runtime exploitability 證明。

### UNKNOWN／不可由現有結果推出

- User-0 正常 Fire restoration writer 的完整 production caller provenance。
- KFT tx3 在合法、自然 child/profile lifecycle 以外的 caller 可達性；不得以 raw parcel 試探。
- PendingIntent Accessibility 變體的 runtime redirect 行為（更新在簽章不相容時已先被拒絕）。
- DPM/Profile Owner 是否存在尚未保存的合法 relay；不得建立、移除或重配 owner。
- 官方 OTA 後 native updater/fosinit handoff 的自然 runtime 行為；不得 replay OTA 或 recovery。
- 未保存的 fosinit registration、native CFG/decompiler branch、Vending grant provenance、以及完整 production caller universe。
- `service list` 中已列出但 shell 不可取得 handle 的 private service method-level behavior。
- Accessibility fallback 是否在其他未測 exact-build／GUI 狀態下具有不同持久性；現有結果不支持把它稱為 formal HOME。

UNKNOWN 只表示保存的 corpus 沒有建立結論，不是漏洞或全域不存在的證明。

## 高影響缺口與最小下一步

| 缺口 | 最小、不改狀態的下一步 |
|---|---|
| User-0 Fire restoration writer | 只做 exact-build host-side caller/source correlation；或等待自然、合法 profile/OTA lifecycle 後讀取既有 resolver/package/log evidence。 |
| KFT child provenance | 只比較既有 child/profile capture 與 static `UserInfo.id`/caller gate；不送 tx3、不建立/刪除 user。 |
| DPM/Profile relay | 只掃描已保存的 exported component、manifest、caller graph；不 provision/remove Profile Owner、不送 tx100/tx73。 |
| OOBE/OTA | 只補齊已取得檔案的 fosinit/native source-to-service map；只有合法官方 OTA 後做 read-only post-state capture。 |
| Private service visibility | 只做 host-side class-to-registration mapping；不呼叫未知 Binder transaction，不把 `service list` 當成權限。 |
| Anomalous permission grant | 只比較已保存的 Vending manifest/signature/privapp metadata；不 grant/revoke、不啟動 production component 進行猜測。 |
| Accessibility | 保留既有 user-consented foreground fallback邊界；不為了驗證而重裝、卸載、切換未知 package 或變更 secure setting。 |

## 明確不再執行

- priority APK 矩陣、普通 `set-home-activity`、preferred/force-stop 組合的重測。
- Fire Launcher 或核心服務的 disable、hide、suspend、uninstall、clear、force-stop 重測。
- 未知 Amazon Binder transaction（含 KFT tx3、DPM/PM/Backup raw transaction）。
- 手動 OOBE/OTA broadcast、updater/recovery、OTA replay、partition write。
- driver ioctl、kernel exploit、root、remount、system-server injection。
- 為繞過 6PD 簽章拒絕而 uninstall/reinstall 既有研究 APK。

## 交付

- [Markdown 報告](./luna_worker_phase6qe_existing_tests_20260810.md)
- [CSV 矩陣](./luna_worker_phase6qe_existing_tests_20260810.csv)

兩個檔案均為本次新建；既有檔案未修改。
