# Phase 12D — host-only static driver caller closure

日期：2026-08-10（Asia/Taipei）  
目標：KFTRWI / trona / MT8183 / PS7331.4463N / Android 9 / Linux 4.4.146+

## 結論

本輪只讀取主機端資料，沒有使用 ADB、開啟 `/dev`、執行 read/write/ioctl、root、exploit、kernel build/run、QEMU exploit，也沒有編寫或執行 PoC。盤點 7.3.3.1 GPL source、trona boot/config、vendor init、ueventd/file_contexts/SELinux artifacts、native ELF inventories、decompiled/findings。

12 個優先 surface 均維持 `UNKNOWN`；沒有任何一列滿足「shipped userspace caller + node policy + gate + sensitive sink」四項閉合，因此沒有 `Strong evidence`。`UNKNOWN` 代表本次保存的靜態 corpus 沒有完成該 edge，不代表 edge 不可能存在。

## 覆蓋範圍與方法

來源根目錄：

`firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4`

盤點目錄包括 `drivers/misc`、`drivers/soc/mediatek`、`drivers/input`、`drivers/power`、`drivers/usb`、`drivers/char`，以及 Amazon/vendor/MediaTek 自訂實作。目錄檔案計數為：drivers/misc 1887、drivers/soc/mediatek 1、drivers/input 112、drivers/power 44、drivers/usb 160、drivers/char 19（含 C/H/Kconfig/Makefile）。`drivers/soc/mediatek` 在此 source root 僅有 Kconfig，沒有可歸屬的實作 caller 或 node sink。

判定規則是逐列追蹤：

`source entry → built/shipped artifact → node or proc/sysfs/debugfs policy → shipped userspace caller UID/domain → config/DT/service gate → input validation and ioctl/API → sensitive sink`

任何一段缺失即 `UNKNOWN`。Kconfig `y`、source mode、`libion/libm4u/libged` marker、SELinux type 單獨都不是 caller closure；init 的 `chmod/chown` 也不等於 merged TE allow 或 native caller identity。

## 主要觀察

- `/dev/mtk_cmdq` 的 init provenance 與 `mtk_cmdq_device` file-context type 存在，但 exact shipped `open()+CMDQ ioctl` ELF caller、UID/domain、merged allow 與完整 DT/object delivery 未閉合。
- `/dev/ion` 有 `ion_device` file-context 與 `CONFIG_ION=y/CONFIG_MTK_ION=y`，但 heap/object、exact gralloc/codec caller、Binder-to-open edge 與 final allow 未閉合。
- `/proc/m4u` 有 init 的 `0440 system:media` 記錄；source 的 `/dev/M4U_device` misc 分支為 `#if 0`，proc label/allow 與實際 native opener 未閉合。
- `/dev/uinput` 有 init owner/group 與 `uinput_device`/`uhid_device` type，但沒有 exact shipped ELF `open/write/ioctl` caller，也沒有 downstream HOME/PMS sink。
- `drivers/misc/mediatek/performance` 確有 init boot/perfmgr writes；這只證明 init writer context，沒有完成 service/native caller、proc TE allow 與效果鏈。
- Amazon driver-test 在 trona defconfig 沒有 `CONFIG_AMZN_DRV_TEST=y/m`，source Kconfig default 亦為 `n`；列為 conditional source capability，不列 shipped reachability。
- `rpmb_svc` 有 init service 與 vendor file-context labels，但 service UID/domain、exact native RPMB caller、API validation 與 device allow 不完整。
- `drivers/soc/mediatek` 在指定 GPL tree 只有 Kconfig，不能由相鄰 `drivers/misc/mediatek` 實作代推 caller 或 sink。

## 權限、驗證與 sink 邊界

保存的 init/file-context evidence 能指向部分 node/type/mode，例如 `/dev/mtk_cmdq`、`/dev/ion`、`/dev/uinput`、`/dev/rpmb0`、`/proc/m4u` 與 PMIC/perfmgr 路徑；但 exact merged policy allow、domain transition、UID、DT instance、built object 與 native callsite 尚未同時存在。source 中看到 `copy_from_user`、ioctl dispatch、attribute parser 或 `unlocked_ioctl`，只代表 API surface，不能證明低權限可達或可影響 package/HOME。

所有 sensitive sink 都只記錄 source-visible effect：DMA/IOMMU、buffer/secure memory、synthetic input、thermal/PMIC、USB transfer、RPMB persistent storage、conditional factory/RTC state 或 performance state。未發現本輪列出的 driver source 有直接 PMS/AMS/ATMS/HOME/Fire Launcher sink；這個 negative result 仍不替代完整 userspace event/property/file provenance。

## 證據與輸出

- 本輪逐列結果：[luna_worker_phase12d_driver_20260810.csv](luna_worker_phase12d_driver_20260810.csv)
- canonical source manifest：`kernel/source-manifest.json`
- shipped config：`artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config`
- trona defconfig：`work/ps7331-kasan-source-20260810/arch/arm64/configs/trona_defconfig`
- init/policy extraction：`artifacts/phase6c/phase6c-image-policy-extract-20260804-02/`
- 交叉參考：`work/luna_worker_phase10d_driver_caller_closure_20260810.csv`、`work/luna_worker_phase7c_kernel_driver_closure_20260810.csv`、`findings/phase-6is-selinux-driver-route-closure.md`

## 安全界線與剩餘缺口

本輪沒有測試任何 driver node、沒有 mutation、沒有 kernel/QEMU/exploit。若要把任一列從 `UNKNOWN` 提升，仍需同一 exact build/variant 的 compiled DTB/object/module provenance、merged ueventd/file_contexts/TE allow、native relocation-level caller（含 UID/domain）、完整 input validation/API contract，以及 sink effect evidence。未完成前不可把任何列標為 Strong evidence。
