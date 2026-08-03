# Phase 5AM：Android Bluetooth CVE 實作邊界與 method-index 校正

日期：2026-08-04
裝置：Amazon Fire HD 10 2021 / `KFTRWI` / `trona` / MT8183
Build：`PS7330.4104N/0030099376128`，Android 9/API 28，security patch
`2024-02-01`

## 目的與安全範圍

本輪只解析先前從 exact Bluetooth VDEX 擷取的 host-side text artifacts，將 Android
Java/Binder、Amazon GATT extension、BTPM native declaration 與公開 CVE scope 分開。
沒有啟用 Bluetooth、發送 HCI/L2CAP/ATT/GATT 輸入、呼叫未知 Binder、載入 native
library、執行 PoC、觸碰 device node 或改變裝置狀態。

## 結論先行

### 已證實

1. `com.android.bluetooth` 的 exact VDEX 具有 AOSP-shaped `GattService` GATT
   entry points。`clientConnect`、`clientDisconnect`、`readCharacteristic`、
   `readDescriptor`、`registerClient` 等方法位於 Bluetooth app process 的 Binder
   service boundary；部分路徑會呼叫 `permissionCheck` 或 admin/privileged helper。
2. Amazon 增加了 `FosGattService`。其 constructor 建立
   `FosBluetoothGattBinder`，並將 extended binder 寫入 inherited `GattService`
   欄位；`clientConnect`／`clientDisconnect`／`registerClient` 等方法先要求
   `android.permission.BLUETOOTH`，再呼叫 superclass。
3. Amazon `AmazonBtPolicyManagerAdapter` 宣告一組 private native BTPM methods，
   並將 BTPM callback 轉送至 `FosGattService.onBtpm*Callback`。這確認了
   `com.android.bluetooth` 與 Amazon BTPM/native boundary 的實作連接，但不是
   shell-to-root primitive。
4. VDEX 中的 `method #20025`、`#20027`、`#20043` 等是 DEX method-pool index，
   不是 `CVE-2022-20025`、`CVE-2022-20027`、`CVE-2022-20043` 的漏洞實作。新的
   parser 將兩種識別明確分離，避免把 method index 誤報成 CVE。
5. MediaTek/Android 公告的 CVE scope 只能把歷史受影響 chipset/software family
   與本機 Android implementation 邊界連起來；它們不能單獨證明 exact PS7330
   vendor binary 未修補。

### 高可信推論

- `CVE-2022-20025`～`20028`、`20041`～`20046` 的公告描述與 patch ID 指向
  MediaTek Bluetooth stack 的 lower native/vendor implementation；目前取得的
  Java/VDEX 證據只能確認可達的 Android service boundary，不能把任何一個
  `GattService` method 認定為 vulnerable function。
- 以目前 security patch `2024-02-01` 相對 Android `2022-02-05` bulletin level 的
  日期關係看，這些歷史 issue 很可能已由 OEM backport 或後續更新處理；Amazon
  exact PS7330 的 patch mapping 未公開，故仍不是 binary-level confirmed。

### 待驗證

- `/vendor` Bluetooth HAL、controller firmware、BTPM implementation 是否包含
  `ALPS06126832`／`ALPS06126827`／`ALPS06126826`／`ALPS06198663` 對應修補。
- private BTPM native methods 的 JNI registration、symbol map 與 vendor source
  對應點；shell 不應以猜測 transaction 或 crafted input 取代這個缺口。

### 已排除／不採用

- `method #20025` 等於 `CVE-2022-20025`。
- `FosGattService` 或 `AmazonBtPolicyManagerAdapter` 的存在本身就是 root exploit。
- 一般 Android Bluetooth PoC、其他 MTK 型號 offset、BlueZ/Linux PoC 可以直接套用
  到 `KFTRWI/trona/PS7330`。

### 因風險拒絕測試

未執行 Bluetooth activation、crafted HCI/L2CAP/ATT/GATT、未知
`IFosBluetoothGatt`/BTPM Binder、vendor native library、kernel Bluetooth trigger、
root payload、BROM/DA、fastboot 或分割區操作。

## Exact Android implementation map

```text
Bluetooth client / system caller
        │ Binder + Android permission checks
        ▼
com.android.bluetooth (UID 1002, android.uid.bluetooth)
        ├─ GattService / BluetoothGattBinder
        │      └─ BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_PRIVILEGED checks
        └─ Amazon FosGattService
               ├─ FosBluetoothGattBinder (extended binder)
               ├─ permission-guarded overrides → GattService superclass
               └─ AmazonBtPolicyManagerAdapter
                       ├─ private Java policy methods
                       ├─ private native btpmLe* methods
                       └─ BTPM/JNI/vendor Bluetooth boundary
```

## 可重現 method evidence

| 層 | 證據位置 | 觀察 | 判定 |
|---|---|---|---|
| AOSP-shaped GATT | `.../GattService.txt:433651` | `clientConnect`; `BLUETOOTH` permission path | 已證實 |
| AOSP-shaped permission helper | `.../GattService.txt:434403-434420` | `enforceAdminPermission` / `enforcePrivilegedPermission` | 已證實 |
| GATT privileged check | `.../GattService.txt:437804-437910` | `permissionCheck(II)` 與 UUID overload 參照 `BLUETOOTH_PRIVILEGED` | 已證實 |
| GATT operation boundary | `.../GattService.txt:437918-439404` | read/write/register/scan methods與permission helper | 已證實，slice-scoped |
| Amazon subclass/extension | `.../FosGattService.txt:507658-507692` | constructor calls `GattService.<init>`, creates `FosBluetoothGattBinder`, links `mExtendedBinder` and policy adapter fields | 已證實 |
| Amazon guarded override | `.../FosGattService.txt:507712-507747` | `clientConnect` / `clientDisconnect` enforce `BLUETOOTH`, then call superclass | 已證實 |
| Amazon BTPM native declaration | `.../AmazonBtPolicyManagerAdapter.txt:160880-160924` | private native `btpmLe*`, `classBtpmInitNative`, `cleanupNative` | 已證實 |
| Amazon callback bridge | `.../AmazonBtPolicyManagerAdapter.txt:161010-161362` | BTPM callbacks call `FosGattService.onBtpm*Callback` | 已證實 |

完整、由腳本產生的 62-row table：
`output/tables/phase5am-bluetooth-boundaries.csv`。不可覆寫的 derived artifact 與
input manifest 位於：
`artifacts/phase5/phase5am-bluetooth-implementation-20260804-02/`。

本輪 derived hashes：script `b0f263ee032ad87735d42321fb15c3d586df537b5abc1e7a9dac858c1ccb2dee`；
public table `e91a2f22b599c78bf23cba35252aa2b5dbb0b2724078a46098c2e560cda8c4ff`；同一份
CSV 的 artifact copy hash 亦為 `e91a2f22b599c78bf23cba35252aa2b5dbb0b2724078a46098c2e560cda8c4ff`。

## CVE name 與 Android implementation 的界線

| 公開識別 | 公告／公開描述 | 可以由 exact Android artifact 證明的層 | 目前判定 |
|---|---|---|---|
| `CVE-2022-20025..20028` | MediaTek Bluetooth stack 的 bounds-check 類問題，公告列 MT8183/Android 9；Android bulletin 給 MediaTek patch IDs | Java GATT service 是上層可達邊界；vulnerable/fixed code 未出現在目前可讀的 Java slice | 高可信 scope；exact binary 待驗證 |
| `CVE-2022-20041` | MediaTek Bluetooth issue，公告列 MT8183 | 目前沒有 CVE-to-method map；不能使用 DEX index `#20041` 代替 map | 外部 scope only |
| `CVE-2022-20043..20046` | MediaTek Bluetooth information disclosure/UAF/permission/lifetime 類 issue，公告列相關 Android/MT8183 rows | 目前只能確認 Android GATT/BTPM boundary；沒有 exact vulnerable symbol | 外部 scope only |

## AOSP 對照的限制

AOSP `GattService` 可用來確認 Android Bluetooth app/service 的一般 permission 與
Binder 分層；Amazon exact VDEX 顯示其在該分層上增加 `FosGattService`、extended
Binder 與 BTPM adapter。這仍不足以判定 MediaTek proprietary native patch 狀態，因為
vendor HAL/controller firmware 並未以可驗證的 vulnerable/fixed pair 取得。

## 安全下一步

若要提高 exactness，下一個合理工作是取得合法且版本完全匹配的 vendor Bluetooth
binary/source patch mapping，做 host-only hash/symbol/diff。只有找到 exact vulnerable
branch、可文件化入口與 recovery plan 後，才可另行評估 active testing；目前不應執行
crafted Bluetooth input 或未知 Binder。

## Reproduction

```sh
python3 tools/scripts/analyze_phase5am_bluetooth_boundaries.py --dry-run \
  --gatt artifacts/phase5/phase5j-bluetooth-static-analysis-20260803/focus-classes/com_android_bluetooth_gatt_GattService.txt \
  --fos-gatt artifacts/phase5/phase5j-bluetooth-static-analysis-20260803/focus-classes/com_android_bluetooth_gatt_FosGattService.txt \
  --btpm artifacts/phase5/phase5j-bluetooth-static-analysis-20260803/focus-classes/com_android_bluetooth_amznbtpolicymgr_AmazonBtPolicyManagerAdapter.txt \
  --output /tmp/phase5am-boundaries.csv
```

實際輸出使用同一 command、但輸出至新的空目錄；script 會拒絕覆寫既有 output。
