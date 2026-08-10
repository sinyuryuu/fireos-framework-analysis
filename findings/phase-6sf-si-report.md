# Phase 6SF–SI — permission, driver, recovery and test-catalog closure

日期：2026-08-10（Asia/Taipei）
基準：公開 `1214e6f1564422cf411e57305b5acc727ababb66` 及 exact-device
readonly snapshot `6SE-DEVICE-READONLY-20260810-01`。
執行模式：host-only static/provenance review；未對設備新增變更。

## Executive summary

本輪將四條未閉合研究線整理成 66 筆可重產 ledger：

- **6SF — permission holder/provenance：已修正一項資料品質問題。**
  `amazon.permission.ADD_RM_PKG_METADATA` 在保存的 exact-build XML 中確實存在，
  raw protection level 是 `0x80000002`，即 Android 編碼慣例下的
  `signature|privileged`。目前仍沒有足夠證據證明誰取得 holder/grant、實際 production
  caller 是誰，或它能寫 HOME、preferred activity、component state。
- **6SG — sensitive driver join：未找到 POSITIVE join。**
  `/dev/mtk_cmdq`、`/dev/ion`、`/dev/gsensor`、`/proc/perfmgr/perf_ioctl`、
  `/proc/m4u`、RPMB、IDME 及 Amazon diagnostic/metrics/lifecycle 面都至少缺少
  exact native client 或完整 shipped policy join，因此全部保留 `UNKNOWN`。
- **6SH — OTA/recovery：高權限能力已確認，低權限入口未建立。**
  Java verifier、UpdateSystem handoff、staging/copy shape 及 protected post-OTA
  lifecycle 可定位；但没有 shell/ordinary app → verifier/install → recovery/updater
  → partition writer 的合法呼叫鏈。沒有執行 payload、recovery、OTA 或 updater。
- **6SI — existing-test catalog：降低重複與誤判。**
  20 個測試族群標出可保留、前提改變才可重開、證據不足、已拒絕及 bounded negative。
  KFT child writer 仍是 child-scoped；accessibility/foreground redirect 仍只是近似
  方案，不能改稱正式 HOME replacement。

結論：截至本輪，在目前保存 corpus 和 PS7331 runtime snapshot 中，仍沒有新的
ordinary app/shell → trusted identity → package/HOME state、driver sensitive effect、
OTA partition writer 或 root chain。這是 **Strong evidence 的 bounded negative**，不是
全系統漏洞不存在證明。

## 已證實

1. Exact-build permission XML 在
   `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt:1822`
   宣告 `amazon.permission.ADD_RM_PKG_METADATA`，owner 為 `android.amazon.perm`，
   raw `protectionLevel=0x80000002`（6SF-001/002，Confirmed）。
2. Amazon package-manager metadata method-level permission check 與
   `AmazonApplicationFlags` → `amazon_package_flags.xml` sink 已有靜態證據；它不是
   HOME resolver writer（6SF-010–020，Confirmed static sink / bounded bridge not found）。
3. 11 個 driver/storage/diagnostic target 沒有同時閉合 source/config、shipped node
   owner/mode、SELinux label/allow、exact native client 四段（6SG-001–011，UNKNOWN）。
4. `SideloadVerifier`、`SideloadMover`、`UpdateSystem.install` 的 Java handoff，以及
   `BOOT_AFTER_SYSTEM_OTA` protected lifecycle 可定位（6SH-001/002/007–010，Confirmed）。
5. exact-device readonly snapshot 沒有做 node/Binder/settings/package mutation、reboot、
   OTA/recovery 或 root/exploit；HOME 仍是 `com.amazon.firelauncher/.Launcher` priority
   50，User 0 preferred record 仍為 Fire、`mAlways=true`（6SE-DEVICE/HOME/PREFERRED）。

## 高可信推論

- `ADD_RM_PKG_METADATA` 目前最合理的解释是 Amazon package metadata persistence surface；
  沒有 `→ setApplicationEnabledSetting`、`→ setComponentEnabledSetting`、preferred
  activity 或 HOME selection 的 bounded static edge。
- driver source/config/policy 行為顯示 capability surface，但缺 exact native caller，不能
  推導 ordinary app 或 shell 可達，更不能推導 kernel control 或提權。
- OTA/recovery 是受保護的高權限寫入面；`update-binary` 的 partition-write symbol、
  exported metadata 或 Java staging marker 都不等於低權限可利用路徑。
- 目前最佳的無 Root 近似方案仍是使用者明確授權的 foreground/accessibility redirect；
  它不會改變正式 HOME resolver、不能提供 system UID，也可能有延遲/閃爍/背景限制。

## 待驗證

1. `ADD_RM_PKG_METADATA` 在完整 exact-build package permission state 中的 holder、grant
   與 production caller；最小安全目標是擴大既有 artifact 的離線 caller/holder census，
   不呼叫 Binder。
2. driver targets 的 exact native userspace caller、完整 ueventd owner/mode 與 TE join；
   只做主機端 source/config/policy/inventory matching，不開節點。
3. recovery verifier 的 platform/native caller 與 staging canonicalization semantics；
   不提交 malformed OTA、symlink/traversal 或 recovery payload。
4. Amazon callback 的 indirect/reflection/generated caller completeness；以既有反編譯和
   method-index 擴充為限，不猜 transaction code。

## 已排除（目前證據範圍）

- KFT child/profile writer 作為 broad User-0 HOME replacement。
- `ADD_RM_PKG_METADATA` metadata sink 作為 HOME/PMS/package-state relay。
- 只憑 source symbol、SELinux allow、0666 node metadata、HAL presence 或 updater write
  capability 宣稱低權限可達。
- 把 `mAlways=true` ordinary preferred record 存在本身宣稱為有效 HOME replacement。
- 把 accessibility redirect 宣稱為正式 HOME replacement。

## 因風險拒絕測試

- 私有 Binder `service call`、未知 transaction、caller spoofing、driver `open/ioctl` 或
  proc write。
- OTA/recovery/update-binary、crafted archive、symlink/traversal payload、sideload、
  reboot、partition write、remount、SELinux 修改。
- 停用、hide、suspend、uninstall、force-stop 或清除 Fire Launcher；任何可能失去桌面
  或需要 factory reset 的測試。

## 可重產性

```sh
python3 tools/scripts/build_phase6sf_si_surface.py --dry-run
python3 tools/scripts/build_phase6sf_si_surface.py
python3 - <<'PY'
import csv
from pathlib import Path
p = Path("output/tables/phase6sf-si-control-surface.csv")
with p.open(newline="", encoding="utf-8") as f:
    rows = list(csv.reader(f))
assert len(rows) == 67 and all(len(r) == 14 for r in rows)
print("CSV schema OK", len(rows) - 1, "rows")
PY
sha256sum work/luna_worker_phase6sf_permission_20260810.csv \
  work/luna_worker_phase6sg_driver_join_20260810.csv \
  work/luna_worker_phase6sh_recovery_20260810.csv \
  work/luna_worker_phase6si_test_catalog_20260810.csv \
  output/tables/phase6sf-si-control-surface.csv \
  output/tables/phase6sf-si-input-manifest.sha256
```

腳本只讀 worker CSV、正規化欄位並寫 host-side output；不需要 ADB，不會接觸裝置。
66-row output 的 SHA-256 是 `8575401e2d1e02dc3b44893cad2b3e20f3e3bcf6689ac2db24b8a2eb96c2fdaf`；
固定內容的 input manifest SHA-256 由腳本每次重產並寫入同名檔案，避免把執行時間納入雜湊。

## 下一個最小安全目標

若繼續研究，優先順序是：

1. 離線補齊 exact permission holder/grant/caller 的 class/package join；
2. 離線補齊 driver 的 exact native client 與 shipped policy join；
3. 離線補齊 recovery native verifier/staging provenance。

若這三條仍無法閉合低權限 caller，正式 HOME replacement 研究可合理結案為：
Fire Launcher 受到 privileged/system package 與 resolver state 共同保護；目前沒有可
證明、可持久、可還原、無 Root 的正式 HOME replacement，只有需明確使用者授權的近似
foreground/accessibility redirect。
