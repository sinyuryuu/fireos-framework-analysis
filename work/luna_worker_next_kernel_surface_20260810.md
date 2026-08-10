# PS7331 7.3.3.1 kernel/source/driver 靜態資產盤點

日期：2026-08-10。範圍限主機端既有 workspace：
`firmware/extracted/PS7331-SOURCE-20250617`、既有 boot image/符號材料、以及 Phase 5/6/7/8/13 的保存 artifacts。未連接或修改裝置；未執行 driver open/ioctl、exploit、root、boot 或 partition 操作。

## 判讀規則

- 「存在的能力」與「已確認 caller/權限/sink」分開。source registration、Kconfig、DT match 或 symbol 僅證明 capability/build intent。
- `caller_or_entry`、`permission_or_gate`、`sink_or_effect` 若沒有 exact caller、UID/domain、node policy 或 effect provenance，CSV 直接寫明 UNKNOWN；不因缺少 caller 宣稱漏洞。
- Confidence 僅使用指定枚舉。`Confirmed` 表示該欄位的靜態存在或明確負向 gate 已被保存證據直接支持；不等同於低權限 runtime reachability。

## 總結

在 MT8183 4.4 source 中確認多組 Mediatek misc/graphics/memory/power/input/USB 與 Amazon surfaces：CMDQ、ION generic/MTK、M4U、uinput、AUXADC、perfmgr、USB PHY/TCPC debug、Amazon liquid-detection sysfs 及 Amazon metrics/sign-of-life/test catalogue。`mt8183.dts` 也保留 GCE/CMDQ、M4U、DevAPC、CQDMA、Amazon mdump 等 instantiation intent。

既有 Phase 5/6/7/8/13 artifacts 的共同 closure：沒有保存到足以閉合「普通 app/shell/native caller → exact node → permission/SELinux → ioctl/proc/sysfs write → sink」的完整鏈。`CONFIG_AMZN_DRV_TEST` 在 `trona_defconfig`/`kernel.config` 未啟用，故其 factory/engineering dispatcher 是 conditional source capability，不能當成 shipped runtime surface。部分 Amazon metrics/sign-of-life 與 CMDQ/ION config 則有啟用證據，但 final object/image、node mode/owner、merged policy 與 exact caller 仍未全部 join。

既有測試/觀測只作邊界證據：保存的 QEMU/KASAN observer、source/config audit、native caller inventory 與 SELinux/policy scans 均為 host-side 或既有 artifact review；本次沒有新增 runtime probe。沒有任何記錄可把上述 surface 證成可由低權限 caller 到達，也沒有執行寫入或 ioctl 以製造 effect。

## 已確認與未閉合的分界

| 類別 | 已確認 | 尚未確認 |
|---|---|---|
| source capability | fops/ioctl、procfs/sysfs/debugfs registration、platform/DT match、Kconfig symbols | final build 是否選入每個 object/module、DTB/DTBO variant 是否被 boot 選用 |
| caller/permission | init 的 node owner/mode 或 policy candidate（僅在保存資料出現時） | exact native/ framework caller、UID/domain、capability、merged SELinux allow、實際 node mode |
| sink/effect | handler 中可見的 buffer/DMA/register/power/input/diagnostic effect | caller input 到 sink 的完整 dataflow、低權限可達性、產品 runtime effect |

## QA / safe next step

QA：確認只新增本次指定的兩個檔案；CSV header 與固定欄位一致；confidence 值均在允許枚舉；所有 rows 都標示 static capability 與 caller/permission/sink 缺口；未執行裝置操作。可安全的後續工作是繼續 host-only 比對 exact shipped object/module、compiled DTB/DTBO、ueventd/file_contexts/merged TE allow 與既有 native ELF callsites；若仍缺任一 edge，維持 Unknown，不做 ioctl/open/replay。

詳細 row、source line、既有測試與缺口見同名 CSV。
