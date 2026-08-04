# Phase 5BI：MTK 公開路線與 PS7331 升級候選再檢查

日期：2026-08-04

## 結論先行

### 已證實

1. 目前設備仍是 `KFTRWI` / `trona` / MT8183、Android 9、PS7330.4104N；本輪
   沒有改變設備狀態。
2. `KoCleo/mtk-easy-su` 固定版本的 `mtk-su64` LFS SHA-256
   `328632e853ff6427af9f35cb83a91d9e960f35d01188ee66d46ae9c7ce7c7827`，與既有
   `MTK-SU-CMDQ-T03` 使用的 payload 相同。既有測試在 critical init step 3
   失敗，沒有觀察到 UID 0；因此不重跑相同路線。
3. 公開的 mtk-easy-su 是舊式 MediaTek bootless-root wrapper，不是針對
   `trona`/MT8183/PS7330 的新 Android implementation。公開 README 也明確提醒
   2020 年 3 月後的 firmware 可能阻擋該方法；本次固定版本的測試裝置清單沒有
   KFTRWI、trona 或 MT8183。[KoCleo/mtk-easy-su](https://github.com/KoCleo/mtk-easy-su)
4. 所檢視的 HackMD 公開資料包含多個 vendor-specific 的 MTK preloader／boot-chain
   案例，但沒有建立本機 `trona`、MT8183、Android 9 的 exact profile；因此不能
   把那些案例當成 Amazon 平板的可執行路線。[HackMD exploit survey](https://hackmd.io/@lokey0905/rk-hQSzibl)
5. GhostLock (`CVE-2026-43499`) 目前仍只有 source/config applicability candidate：
   PS7330 source/config 有 futex/rtmutex 家族重疊，PS7331 build-selected source
   與 inspected Image 的語意結果仍是 pre-fix pattern；這不等於 exact PS7330
   signed binary、runtime exploitability 或 root 已證明。
6. 7.3.3.1 的官方 OTA 與本地保存檔已完成 hash／HTTP metadata 對照，可列入
   一般安全更新的 A/B 候選；但它是 full-block OTA，更新範圍包含 system、vendor、
   boot 及額外 boot-chain／firmware 成員。單獨寫入 `boot.img` 不是等價升級，
   本輪不執行。

### 高可信推論

- PS7331 對研究有價值，主要是作為同型號、相鄰版本的離線比較基準；現有 source
  與 inspected Image 結果不支持「升級即可修補 GhostLock」的說法。
- 若目標是一般安全更新，完整官方 OTA 比 standalone boot image 更接近正確的
  A/B 研究對象；但這會是另一個需要完整備份、相容性與復原計畫的受控系統變更，
  不能由本次 host-only review 自動推導為可安全執行。
- 既有 mtk-su 失敗較可能反映 payload／目標 firmware 介面不匹配，而不是已證明
  的「只差一個 kernel offset」。這是解釋性假說，不是 compiled-driver proof。

### 已排除或不適用

- 不把同一個 `mtk-su64` payload 當作新測試。
- 不把 generic `mtkclient`、fenrir、lkpatcher 或其他 OEM 的 preloader／LK 路線
  當成 Amazon `trona` 相容方案。
- 不把 PS7331 的 inspected Image 語意直接套成 PS7330 signed-binary 結論。
- 不把 `CVE-2026-43503` 當 GhostLock；不把尚未確認的 `CVE-2026-3499` 當成可
  操作的漏洞識別碼。

### 因風險拒絕測試

本輪沒有執行 root exploit、futex race、kernel memory 操作、未知 ioctl、BROM/DA
handshake、preloader/LK patch、fastboot unlock/flash、OTA sideload、單獨 boot
寫入、remount 或任何分割區寫入。缺少 exact PS7330 signed boot-chain artifact
與可靠復原路徑時，這些操作無法提供可歸因的研究證據。

## PS7331 是否列入升級考量

| 目的 | 判定 |
|---|---|
| 驗證官方檔案與同型號版本 | 已完成；可用於 host-only A/B |
| 期待 GhostLock 修補 | 不支持；現有語意證據仍是 pre-fix |
| 一般安全更新 | 可列為獨立候選，但不是本輪自動執行項目 |
| 單獨寫入 boot.img | 拒絕；不是等價 OTA，可能破壞 boot-chain 相容性 |
| 目前設備狀態 | 維持 PS7330，無變更 |

官方 Amazon 更新頁列出 Fire HD 10（11th Generation）Fire OS 7.3.3.1，且
   下載 metadata 與本地保存 OTA 一致：[Amazon Fire Tablet Software Updates](https://digprjsurvey.amazon.co.uk/csad/help/node/G2JXLC4L34GX73TE?theme=light)。
   本地 OTA SHA-256 為
   `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`。

本地只讀 boot artifact 的 SHA-256 為：`boot.img`
`cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b`；解壓後
`kernel.Image` 為
`10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d`。這些 hash
只證明本地保存與分析輸入的身份，不授權寫入設備。

## 證據與可重現輸出

- [`findings/phase-5bi-evidence-index.md`](phase-5bi-evidence-index.md)
- [`artifacts/phase5/mtk-public-route-recheck-20260804-01/`](../artifacts/phase5/mtk-public-route-recheck-20260804-01/)
- [`findings/phase-5az-ghostlock-mtk-compatibility.md`](phase-5az-ghostlock-mtk-compatibility.md)
- [`findings/phase-5bh-ps7331-official-ota-source.md`](phase-5bh-ps7331-official-ota-source.md)
- [`findings/phase-5bg-ps7331-source-binary-semantic.md`](phase-5bg-ps7331-source-binary-semantic.md)

本輪 host-only 輸入與 decision matrix 位於 artifact 目錄；所有原始裝置證據仍
以既有 Phase 5 索引為準，沒有覆寫。

## 下一步邊界

仍有研究價值的安全下一步只有：取得合法且完全匹配 PS7330 的 signed kernel／
vendor artifact，或停止把 source overlap 擴張成 exploit claim。若研究目標改為
一般安全更新，應另立完整 OTA 風險報告，先核對資料備份、官方包、版本相容性、
復原可行性與回退限制；本報告不授權也不執行升級。
