# Phase 6AD：保存 APK 的 protected-broadcast source inventory

## 範圍

本階段對 28 個已保存、明確列入 scope 的 Amazon／system／Settings／SystemUI／
OOBE／OTA APK 使用本機 `aapt dump xmltree` 解析 binary manifest。排除了
MTK Root 測試 APK、Phase 6A 測試 APK 與未明確列入的第三方輸入。

這是 host-only provenance audit：沒有 ADB、沒有 broadcast、沒有 Binder
transaction、沒有 package/settings mutation、沒有 OTA/recovery、沒有重啟，
也沒有寫入分割區。輸入 APK 沒有被修改。

## 結果

- 輸入 APK：28
- AAPT failures：0
- 找到 `amazon.intent.action.BOOT_AFTER_SYSTEM_OTA` 的來源 APK：1
- 唯一來源：`android.amazon.perm.apk`
- 來源 package：`android.amazon.perm`
- 來源 APK SHA-256：
  `5b72bdfcfb91b28d2c751e548f60d406de5c3cbb235e47e232014abdebcdc058`
- 該 manifest 的 protected-broadcast declarations：158

### 判定

| 問題 | 結果 | 信心 |
|---|---|---|
| `BOOT_AFTER_SYSTEM_OTA` 是否在已保存 system/Amazon APK 中出現？ | 是 | 已證實 |
| 是否在多個已保存 APK 中重複宣告？ | 否；scope 內只有 `android.amazon.perm` | 已證實 |
| 是否可由這個 inventory 證明完整 runtime `mProtectedBroadcasts`？ | 否 | 待驗證 |
| 是否因此證明 shell 可以發送 action？ | 否 | 已排除該推論 |
| 是否提供 Launcher replacement 或 root route？ | 否 | 已排除 |

## 證據解讀

Phase 6AC 已確認 `android.amazon.perm` manifest 的 exact declaration；Phase
6AD 的第二個、較寬的保存 APK scope 沒有找到其他 declaration。兩者合併後，
目前最合理的模型是：

```text
android.amazon.perm manifest
  -> PackageParser.Package.protectedBroadcasts
  -> PackageManagerService.mProtectedBroadcasts
  -> isProtectedBroadcast(BOOT_AFTER_SYSTEM_OTA)
  -> ActivityManagerService caller authorization
  -> guarded system_server post-OTA sender
  -> BootAfterSystemOTAReceiver
```

這個結果不會把 `BootAfterSystemOTAReceiver` 變成可採用入口。Receiver 仍會
啟用 OOBE Home、修改 setup state，並可能觸發其他 Alexa consumers；因此人工
`am broadcast`、OOBE activation、OTA Binder 或 updater/recovery 測試仍拒絕。

## Scope limitation

Inventory 只覆蓋明確提供給腳本的保存 APK，不包含：

- 尚未保存的 system/vendor/product/system_ext APK；
- 可能由 SystemConfig、runtime injection 或其他 parser path 加入的 action；
- 裝置中不可讀取的 system-owned runtime state；
- 任何自然 OTA 事件之外的 runtime caller observation。

因此不能把「其他 27 個保存 APK 沒有 declaration」寫成「Fire OS runtime
只有一個來源」；只能寫成「在目前保存 artifact scope 中，唯一觀察到的來源
是 `android.amazon.perm`」。

## 可重現命令

```sh
python3 -m py_compile \
  tools/scripts/audit_phase6ac_protected_broadcast_inventory.py

python3 tools/scripts/audit_phase6ac_protected_broadcast_inventory.py \
  --root artifacts/amazon-services \
  --root artifacts/launcher \
  --root artifacts/phase3b-amazon-settings \
  --root artifacts/phase3b-device-policy \
  --root artifacts/phase3b-framework-settings \
  --root artifacts/phase3b-launcher \
  --root artifacts/phase3b-ota \
  --root artifacts/phase3b-package-management \
  --root artifacts/phase3b-provisioning \
  --root artifacts/phase3b-settings-provider \
  --root artifacts/phase3b-settings \
  --root artifacts/phase3b-systemui \
  --root artifacts/phase6ac/android-amazon-perm-device-20260805-01 \
  --root artifacts/phase6j \
  --output artifacts/phase6ad/protected-broadcast-inventory-20260805-01

(cd artifacts/phase6ad/protected-broadcast-inventory-20260805-01 \
  && sha256sum -c sha256sums.txt)
```

Canonical output：

`artifacts/phase6ad/protected-broadcast-inventory-20260805-01/`
