# Phase 6AY：KFT 實機 runtime preflight

## Test identity

- Test ID：`KFT-PREFLIGHT-20260805-01`
- Scope：read-only ADB precondition capture
- Raw capture：`adb/phase6ay/KFT-PREFLIGHT-20260805-01/`（本機保存，含裝置識別資料，未公開推送）
- Script：`tools/scripts/capture_kft_preflight.py`
- Binder transaction：未呼叫
- KFT mutation：未呼叫

## 實機觀察

| 項目 | 結果 | 判定 |
|---|---|---|
| Android／Fire OS | PS7331.4463N，Android 9/API 28 | 已證實 |
| 使用者 | `UserInfo{0:sinyu:13}`，只有 User 0，running | 已證實 |
| Child/KFT user | 未出現 | 已證實於本次 capture |
| Device owner | `-10000`，無 device owner | 已證實 |
| User 0 profile owner | Amazon parental-controls admin 存在 | 已證實 |
| `amazonusermanagerservice` | shell `service check` 回報 `not found` | 已證實 runtime boundary |
| HOME resolver | `com.amazon.firelauncher/.Launcher`, priority 50 | 已證實 |
| Fire Launcher User 0 | installed，`enabled=0`，沒有被本次測試改變 | 已證實 |
| Tahoe User 0 | package `enabled=3`，`lastDisabledCaller: shell:1000` | 已證實既有狀態；本次未修改 |
| Tahoe FreeTime activity | manifest/resolver table 存在，priority 975；沒有因此被啟用 | 已證實靜態/狀態分離 |

## 為什麼沒有進入 KFT mutation

PS7331 靜態鏈是：

```text
AmazonUserManagerService.onBootPhase / trusted child-user client
  → enableKftLauncher(UserInfo)
  → tryEnableKftLauncherComponent(UserInfo)
  → enableKftLauncherComponent(UserInfo.id)
  → enable Tahoe FreeTimeLauncherActivity
  → disable Fire Launcher and Launcher3 for that user
```

此鏈需要特殊 `UserInfo`／child-user lifecycle。實機沒有 child user，且 private
service 對 shell 不可取得。因此：

- 直接對 User 0 嘗試會偏離 KFT 的實際條件，可能把主桌面切掉；
- `service call` 即使使用已知 transaction，也沒有可驗證的 `UserInfo` parcel 或
  isolated rollback；
- 建立 child/profile owner 再觸發會改變 user、DPM/profile-owner 與 package state，
  不是單一可逆 launcher 實驗。

所以本次的「實機測試嘗試」只到達 precondition capture，沒有把靜態 KFT helper
誤當成已在真機執行。

## 結果分類

- **已證實：** KFT code 可對指定 user 變更 launcher package/component state。
- **已證實：** 本機目前只有 User 0，KFT private Binder 不可由 shell 取得。
- **高可信推論：** 目前沒有合法、隔離、可完全回復的 ADB 入口可以在本機重現該鏈。
- **待驗證：** Amazon 正常 UI 的 child-profile provisioning 是否會建立符合
  `isChildUser(UserInfo)` 的 user；這需要真正的家長／帳戶流程，不應由研究腳本模擬。
- **因風險拒絕：** 建立 profile/child user、直接 `service call`、重播 OTA/boot lifecycle、
  或讓 User 0 進入 KFT package-state mutation。

## Recovery status

本次沒有任何需要 rollback 的變更。HOME、Fire Launcher state、user list、DPM、
settings、overlay 與 ADB 連線均未由本次 capture 改變。

## Evidence hashes

以下是本機 raw capture 的關鍵檔案 SHA-256；完整清單在 capture 目錄的
`sha256sums.txt`：

| Evidence | SHA-256 |
|---|---|
| `metadata.json` | `48dffc952fc660b5be34ff490c97a1632706997a4270efc0c3207af2e5bf2e26` |
| `users_list.stdout.txt` | `4c915d71b79462e0a3ea4996f5882c5293afe47a963fca1a41856a47cb4c7b83` |
| `users_dump.stdout.txt` | `6336e0534d9dc5d6c6a3545596eb4c628c845bb5648f456cb2506b1b06ce946b` |
| `amazon_user_manager_check.stdout.txt` | `8902751dde38ba27b52dbd74d314ef5c39b341c0dfcde9bda6e1de5ecd67dcd1` |
| `home_resolve.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` |
| `firelauncher_package.stdout.txt` | `3c836dccf0d66b0eb273ed020b42f0b29e9b3ac172d378accd91f67edaf64479` |
| `tahoe_package.stdout.txt` | `3fe1e239012ec643fea4e10d0ad2e0bee104dde143267a48ec77dffdb1b84243` |
