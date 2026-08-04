# Phase 5BK：PS7330／PS7331 安全版本差異

日期：2026-08-04

## 結論

### 已證實

- 目前設備 PS7330 的保存 properties 顯示 security patch level 為
  `2024-02-01`。
- 官方 PS7331 OTA 的 `system-build.prop` 顯示 security patch level 為
  `2024-08-01`，build fingerprint 為
  `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`。
- 兩者 product device 都是 `trona`，但 build、incremental 與 security patch
  不同；因此 PS7331 是同產品的相鄰一般安全更新候選。
- Phase 5BJ 的 source/Image 比對仍顯示 PS7331 `remove_waiter()` 是 pre-fix，
  所以「安全修補級別提高」與「GhostLock 已修補」必須分開。

### 高可信推論

PS7331 對一般安全更新有實際研究價值；但是否值得在研究設備上安裝，仍取決於
完整 OTA 的 recovery／回退條件。它不是可由 standalone `boot.img` 完成的等價 A/B
測試。

### 待驗證

- PS7331 相對 PS7330 的完整 security patch 清單與 Amazon backport 差異。
- 完整 OTA 安裝後的實機行為與可回退性。

### 因風險拒絕測試

本輪沒有安裝 OTA、重啟、寫入 boot/system/vendor、修改 boot-chain 或改變裝置狀態。

## 可重現輸出

腳本：[`tools/scripts/compare_phase5bk_security_delta.py`](../tools/scripts/compare_phase5bk_security_delta.py)

結果：[`artifacts/phase5/phase5bk-security-delta-20260804-02/`](../artifacts/phase5/phase5bk-security-delta-20260804-02/)

矩陣：[`output/tables/phase5bk-security-delta.csv`](../output/tables/phase5bk-security-delta.csv)

官方更新頁列出 Fire HD 10 11th Generation 的 Fire OS 7.3.3.1：[Amazon Fire Tablet Software Updates](https://digprjsurvey.amazon.co.uk/csad/help/node/G2JXLC4L34GX73TE?theme=light)。

## 升級決策

| 目標 | 判定 |
|---|---|
| 一般安全更新 | 可列入候選 |
| GhostLock 修補 | 目前不支持 |
| standalone boot.img | 不採用 |
| 完整 OTA | 需另立風險／復原評估，尚未執行 |
