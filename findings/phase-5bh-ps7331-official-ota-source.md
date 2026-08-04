# Phase 5BH：PS7331 official OTA source mapping

日期：2026-08-04

## 已證實

- Amazon 官方 Fire Tablet Software Updates 頁面列出 Fire HD 10（11th
  Generation）與 Fire OS 7.3.3.1；頁面：[Amazon Fire Tablet Software
  Updates](https://digprjsurvey.amazon.co.uk/csad/help/node/G2JXLC4L34GX73TE?theme=light)。
- 官方下載路徑 `https://www.amazon.com/update_Fire_HD10_11th_Gen` 導向
  `fireos-tablet-src.s3.us-west-2.amazonaws.com` 的 PS7331 archive。
- 官方 HTTP metadata 的 `Content-Length=1301005356` 與本機保存 OTA 的大小一致。
- 本機保存檔案為：
  `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin`
- 本機 OTA SHA-256：
  `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`

## 高可信推論

PS7331 是本裝置型號可對應的官方版本，因此可以列為一般安全更新 A/B
研究候選；但這只確認來源與版本，不表示它修補 GhostLock。Phase 5BG 的
三方語意比對仍顯示 PS7331 inspected Image 與 pre-fix source 一致。

## OTA 風險邊界

既有 updater-script metadata 顯示此 OTA 不只更新 `boot`，也更新 system、
vendor、preloader、LK、TEE、SPMFW、SSPM 與 camera VPU 相關成員。故：

- 不能把 extracted `boot.img` 視為完整升級。
- 不能把單獨 boot image 寫入 PS7330 當作可逆 A/B。
- 本階段未安裝、未 sideload、未 flash、未 reboot、未修改裝置。

## 決策

| 目的 | 決定 |
|---|---|
| GhostLock remediation | 不採用 PS7331 作為已證明修補版 |
| 一般安全更新比較 | 可列入候選，但需另行完成完整 OTA 操作風險評估 |
| 單獨寫入 `boot.img` | 拒絕，非等價更新且可能破壞 boot-chain 相容性 |
| 本階段裝置狀態 | 維持 PS7330，無變更 |

## 證據

原始 HTTP headers、URL mapping 與 SHA-256 位於：
`artifacts/phase5/ps7331-official-update-source-20260804-01/`。

本檢查只使用 HTTP HEAD metadata；沒有保存或執行新的 OTA body。
