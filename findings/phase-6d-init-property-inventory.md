# Phase 6D：PS7331 `/init` boot-property／cmdline 靜態 inventory

## 範圍

本輪對保存的 PS7331 7.3.3.1 `/init` AArch64 stripped ELF 做主機端 literal
inventory 與 ADRP/ADD 位址映射。`/init` 沒有被執行，沒有讀取裝置，沒有修改
boot property、cmdline、SELinux policy、bootloader 或分割區。

分析器：`tools/scripts/inventory_phase6d_init_properties.py`

Canonical artifact：
`artifacts/phase6d/phase6d-init-property-inventory-20260804-01/`

## 輸入

| Input | SHA-256 |
|---|---|
| preserved `/init` | `e72ed4e90d73b88be341985ebd624725b67d67967d04157317456233e15f31fd` |

## 結果

分析器找到：

- 162 個 literal marker occurrence；
- 111 個可映射到 marker 的 AArch64 ADRP/ADD 參照。

分類計數（literal / mapped reference）：

| Class | Literal | ADRP/ADD |
|---|---:|---:|
| boot property | 36 | 31 |
| cmdline source | 4 | 9 |
| SELinux policy/mode | 67 | 15 |
| policy path/variant | 39 | 41 |
| boot/recovery control | 9 | 9 |
| security property | 2 | 5 |
| boot integrity/lock state | 5 | 1 |

計數包含重疊 marker（例如 `selinux`、`androidboot.` 與完整字串），因此是
inventory 數量，不是去重後的設定鍵數量。

### 已證實

`/init` 內含下列靜態 surfaces：

- `/proc/cmdline` 與 `proc/%d/cmdline`；
- `androidboot.*`、`ro.boot.*`、`ro.debuggable`、`ro.secure`；
- verified-boot／locked-state markers；
- recovery markers 與 `/proc/idme/`；
- standard／`rootable_*` SELinux policy path；
- `androidboot.selinux` 與 `permissive` 的可定位字串參照。

既有反組譯窗口顯示：

- `0x41bd60`：比較 `androidboot.selinux` 與 `permissive` 的 candidate helper；
- `0x41ad00`：rootable policy path-builder candidate，呼叫 common helper 時
  `w5=1`；
- `0x41af80`：standard policy path-builder candidate，呼叫 common helper 時
  `w5=0`；
- `0x41be48`：common helper 依 `w5` 分支，但 stripped binary 無法直接命名其
  高階語意。

### 高可信推論

這些結果支持「`/init` 有 boot-time property／policy-loader decision surface」；
它不是單純因為檔名含有 `rootable` 而出現的資料。可是這仍是 static control-flow
證據，不能說明目前 stock boot 選了哪一組 policy。

### 待驗證

- 哪些 caller 在目前 boot 分支實際執行；
- `w5` 的準確資料流與語意；
- `androidboot.selinux/permissive` 比較成功後 zero store 對應的欄位；
- active policy blob／hash 與 standard 或 rootable path 的對應；
- 是否存在任何可由 Android shell 寫入且在 `/init` 早期啟動前生效的合法入口。

### 已排除

- `rootable_*` 字串存在不等於 rootable policy active；
- `permissive` 字串比較存在不等於 shell 能設定 SELinux permissive；
- 本輪沒有取得 temporary root，也沒有證明 bootloader／recovery 可選擇 alternate
  policy。

### 因風險拒絕測試

不執行 cmdline/property injection、bootloader／fastboot 選擇、policy replacement、
remount、image write、SELinux mutation、factory reset，以及任何 kernel race、
panic、memory access 或 privilege payload。這些都不是單純的讀取驗證。

## 重現

```sh
python3 tools/scripts/inventory_phase6d_init_properties.py --dry-run \
  --init artifacts/phase6c/phase6c-image-policy-extract-20260804-06/root/init \
  --output artifacts/phase6d/phase6d-init-property-inventory-YYYYMMDD-NN

python3 tools/scripts/inventory_phase6d_init_properties.py \
  --init artifacts/phase6c/phase6c-image-policy-extract-20260804-06/root/init \
  --output artifacts/phase6d/phase6d-init-property-inventory-YYYYMMDD-NN
```

原始 JSON、CSV、分析摘要與 SHA-256 manifest 均保留在 canonical artifact。
