# Phase 5AD：歷史 mtk-su 目標版本篩選

## 目的

本輪只篩選公開歷史 Android/Fire root 實作的裝置與 Fire OS 版本，不執行
新的 payload，也不把舊教學轉成目前設備的操作指令。

## 公開來源的實際目標

歷史 Fire HD 10 教學頁把目標分開描述：

| 公開目標 | 頁面描述 | 與 exact device 關係 |
|---|---|---|
| Fire HD 10 2017 | Fire OS 5.6.4.0；文章主要以此機型操作 | 不是 KFTRWI |
| Fire HD 10 2019 | Fire OS 7.3.1.0；頁面明確寫明作者未驗證 | 不是 KFTRWI，且 build 不同 |
| Fire HD 10 2021 | 沒有列出 | 沒有公開 target evidence |
| KFTRWI / trona / PS7330.4104N | 沒有列出 | exact target 缺失 |

頁面也明確提醒後續內容主要是 2017 機型，2019 機型可能無法正常處理。

**已證實（source scope）：** 該歷史教學不能作為 2021 KFTRWI 的 root
相容性證明。

來源：[Fire HD 10 歷史 root 教學](https://o3note.blogspot.com/2019/07/fire-hd-10-root.html)。

## KoCleo mtk-easy-su 對照

固定 KoCleo revision 的 Android wrapper 與 payload 已在 Phase 5AA/5R
分析。其公開 README 提醒 2020-03 後的 firmware 可能阻擋 mtk-su；測試裝置
清單沒有 KFTRWI/trona。更重要的是，同一 payload 已在 exact PS7330
MTK-SU-CMDQ-T03 執行失敗：

- exit code 1；
- stderr Failed critical init step 3；
- 沒有 UID 0；
- rollback 後 ADB、HOME、SELinux 與 package state 正常。

**已證實：** 重裝或重跑同一 KoCleo payload 不會改變測試前提。

## mtkclient 對照

目前公開 mtkclient source 把 MT8183 放在共享 MT6771/MT8385/MT8183/MT8666
profile，使用 dacode 0x6771；沒有獨立 0x8183 key。這只能說明某種
bootrom-family config 可能存在，不能證明 Amazon preloader、DA、SLA/DAA、
SBC、rollback 或 seccfg chain。

## 結論分級

- **已證實：** 公開歷史 mtk-su 材料沒有 exact 2021 KFTRWI/PS7330 target。
- **已證實：** 固定 mtk-su payload 在 exact PS7330 已失敗，不重跑等價 binary。
- **高可信推論：** 2017/2019 Fire 的 root route 不應直接移植到 2021/PS7330。
- **待驗證：** 是否存在未公開且 exact PS7330 的 Android/kernel root implementation。
- **因風險拒絕測試：** 用歷史 payload、shared mtkclient profile 或未知 preloader
  進行 live root/BROM/flash。

## 下一步

目前仍可安全進行的裝置工作是已準備好的 PendingIntent foreground
measurement；它與 root/bootloader 無關。低層路線若沒有 exact signed
PS7330 preloader/LK/DA/auth/recovery chain，就不增加可解釋性，只增加
不可逆損壞風險。

## Source

- [歷史 Fire root 教學](https://o3note.blogspot.com/2019/07/fire-hd-10-root.html)
- [KoCleo/mtk-easy-su](https://github.com/KoCleo/mtk-easy-su/tree/8c6871ac7c15b8e98a47e25c35ab93b87e260475)
- [bkerler/mtkclient](https://github.com/bkerler/mtkclient/tree/0542a8729993000661e2325e838217ee754d1632)
