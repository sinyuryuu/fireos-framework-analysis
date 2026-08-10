# Phase 6SB–SE — broad privilege-surface closure

日期：2026-08-10（Asia/Taipei）  
基準：公開 commit `59742fef3e839a495a941a7c114bd12eb1ded602`  
模式：host-only；既有設備證據只作引用，不重播高風險操作。

## Executive result

本輪把既有 6RY–SA 的 45 筆 ledger 與新 worker 的 39 筆資料合併成 84
筆 row-level control-surface ledger。結果沒有找到新的 ordinary app／shell
到 system UID、HOME/package-state writer、driver sensitive effect 或 OTA
partition writer 的可重現 caller chain。

這不是「所有漏洞都不存在」的證明；它是對目前保留 artifact、反編譯、policy、
source/config 與既有 runtime evidence 的 bounded closure。未閉合的 caller、
permission holder、native indirect dispatch、recovery provenance 仍標為
UNKNOWN，不能轉成 exploit。

## Fresh device snapshot

指定 serial `G001LT0511550CFT` 於 2026-08-10T03:50:39Z 做了 12 項唯讀採樣；
snapshot 內的 `sha256sums.txt` 在 snapshot directory 內驗證全部 OK。這次採樣
沒有開啟 device node、讀取 driver data、呼叫 Binder、修改 settings/package、
重開機或執行 OTA/recovery/root。

實測仍為：

- fingerprint `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`
- `KFTRWI` / `trona` / Android 9 API 28 / security patch `2024-08-01`
- HOME resolver：`com.amazon.firelauncher/.Launcher`, priority 50
- HOME candidates：Fire 50、Microsoft 0、Settings Fallback -1000
- User 0 preferred record：Fire Launcher，`mMatch=0x100000 mAlways=true`，
  selected set 包含 Fire、Microsoft、FallbackHome
- Fire Launcher package path `/system/priv-app/com.amazon.firelauncher`，
  User 0 `enabled=0`（default），User 10 的保存狀態為 `enabled=2`；本輪沒有
  修改任何一個狀態，User 10 值只作為現況證據，不推導其歷史來源。

原始輸出與 hash 位於
`adb/phase6se/PHASE6SE-DEVICE-READONLY-20260810-01/`。

## 分類結論

### 已證實

- `AmazonPackageManagerService` 的 metadata/flags mutator 會在權限檢查後寫入
  `AmazonApplicationFlags`／`amazon_package_flags.xml`；沒有保存的 HOME、preferred
  activity 或 package-state bridge。
- KFT tx3 是 child/profile-scoped 的 launcher component/package writer，使用
  `UserInfo.id`；既有 User 0/User 10 ordinary-app 測試在 PMS gate 被拒，沒有形成
  User-0 Fire Launcher mutation route。
- kernel/source 內存在 CMDQ、ION、M4U、RPMB、performance、factory/diagnostic
  等高影響能力或控制面，但 source/config/node metadata 本身不等於 caller
  reachability。
- 官方 OTA/update-binary 具有 recovery/high-privilege extraction、block-image
  與 partition-write capability；它不是 shell 或 ordinary-app caller 證據。
- outer source tar 已由 6SD worker 讀到 real EOF：35 members、0 symlink、0 hardlink；
  它不是 installable OTA。

### 高可信推論

- 在保存的 framework/VDEX、Amazon service、policy 與 caller inventory 內，沒有
  新的普通 App／shell → trusted identity → package/HOME sink。
- `preWarmApplicationForUser()` 的既有 confused-deputy 觀察是 process/resource
  effect，不是 HOME writer 或 root proof；本輪沒有重播 Binder transaction。
- OTA/OOBE 路徑屬 protected lifecycle／privileged capability；receiver exported
  metadata、缺少某個 Java marker 或 native write symbol 都不足以證明低權限可達。

### 待驗證

- `ADD_RM_PKG_METADATA` 的 exact declaration、protectionLevel、grant/holder 與
  production caller 不在目前保存的 exact-build permission census 中。
- CMDQ/ION/gsensor/perfmgr/RPMB 的完整 shipped ueventd + SELinux + native
  userspace caller join仍有缺口。
- recovery verifier/native caller、staging canonicalization、indirect updater
  CFG/dataflow 與 OOBE numeric user 尚未完全閉合。
- runtime-loaded native callbacks、service aliases、reflection/generated
  dispatch outside the bounded corpus 尚未全面證明不存在。

### 已排除（目前證據範圍）

- KFT child writer 作為 broad User-0 HOME replacement。
- `ADD_RM_PKG_METADATA` metadata sink 作為 HOME/PMS/package-state relay。
- source 中的 `AMZN_DRV_TEST` factory-reset/RTC dispatcher 作為 shipped retail
  route；`trona_defconfig` 未啟用該 config，且保存 Image marker audit 沒有匹配證據。
- outer source tar 內含可直接安裝的 OTA/recovery/post-install/partition member。
- 「raw CSV malformed」作為目前 worker/source CSV 的一般性資料品質結論；本輪
  CSV 均通過標準 parser 與欄位寬度檢查。

### 因風險拒絕測試

- 未執行 root exploit、kernel race、private Binder transaction 或 caller spoofing。
- 未開啟 `/dev/mtk_cmdq`、`/dev/ion`、`/dev/gsensor`、`/proc/perfmgr/perf_ioctl`、
  `/proc/m4u` 或任何 driver/diagnostic node。
- 未執行 OTA/recovery/update-binary、crafted archive、symlink/traversal input、
  reboot、sideload、partition write、SELinux/remount 或 Fire Launcher mutation。

## 四條研究線結果

### 6SB — IPC / permission

`ADD_RM_PKG_METADATA` 的服務端 metadata mutators 與 XML persistence sink 已有
靜態證據，但 permission declaration/holder/actual production caller 尚未閉合。
KFT tx3 的 writer 已知且 child/profile-scoped；ordinary app 的既有測試進入
service 後由 PMS cross-user/component-state gate 擋下。私有 Binder 的 service
publication 不等於 shell handle；保存的 enforcing service-manager evidence
顯示 shell find 被拒。

### 6SC — kernel / driver

source → selected config → node/policy → exact userspace caller → effect 的鏈條
大多停在 caller。ION 的 shell allow、factory mode stanza、proc mode 或
`copy_from_user` 只作 capability/policy evidence，未升級成 live open/ioctl 或
memory-safety finding。IDME direct write path 有 bounded negative；RPMB caller
與 persist effect 仍 UNKNOWN。

### 6SD — OTA / install

`DeviceSoftwareOTA` 受 signature|privileged controller permission 與多重 metadata、
hash、device-state、recovery gate；`UpdateSystem.install` 與 update-binary 的
高權限 writer 是已知能力。Java staging 未見 canonicalPath/NOFOLLOW marker，
但 native/helper semantics 與 crafted-path 行為未知，故僅列 hardening hypothesis，
不列漏洞。`BOOT_AFTER_SYSTEM_OTA` 可進入 OOBE setup lifecycle，不是一般 HOME
selector，也沒有 ordinary sender 證據。

### 6SE — evidence quality

catalog 重新審核既有標籤，將「artifact authenticity」「static sink」「caller
reachability」「user scope」「archive completeness」分開。這避免把 `Confirmed`
static capability誤寫成可利用的低權限路徑。

## 可重產資料

主 ledger 由以下腳本產生：

```sh
python3 tools/scripts/build_phase6sb_se_surface.py --dry-run
python3 tools/scripts/build_phase6sb_se_surface.py \\
  --device-snapshot adb/phase6se/PHASE6SE-DEVICE-READONLY-20260810-01
python3 - <<'PY'
import hashlib, json
from pathlib import Path
m = json.loads(Path("output/tables/phase6sb-se-control-surface.csv.manifest.json").read_text())
got = hashlib.sha256(Path(m["output"]).read_bytes()).hexdigest()
assert got == m["output_sha256"], (got, m["output_sha256"])
print(got)
PY
```

輸入 worker CSV 與既有 6RY–SA matrix 的 hash、row count、輸出安全旗標均在
同名 manifest 與 [evidence index](phase-6sb-se-evidence-index.md) 記錄。腳本不
依賴 ADB 或任何 device-side binary。

## 最佳可行方向

若目標仍是正式關閉 Fire Launcher，目前最接近的非 root 方案仍是既有的使用者
明確授權 foreground/accessibility redirect；它不是 PackageManager HOME replacement，
也不會提供 system UID。若目標是繼續尋找任何高權限面，下一個最低風險工作應是
host-only 補齊 exact permission holder、ueventd/TE/client joins 與 recovery caller
provenance；不應以未知 Binder、driver ioctl、OTA payload 或 root exploit 補缺口。

## Evidence index

見 [phase-6sb-se-evidence-index.md](phase-6sb-se-evidence-index.md)。
