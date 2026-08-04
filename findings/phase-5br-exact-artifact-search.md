# Phase 5BR：PS7330 exact signed artifact bounded search

日期：2026-08-04

## 結果

### 已證實

- 針對 `PS7330.4104N`、`KFTRWI`、`trona`、`boot.img`、`vmlinux` 與
  `Fire_HD10` OTA 的 bounded public-web search 已保存於
  `artifacts/phase5/phase5br-exact-artifact-search-20260804-01/`。
- 搜尋結果包含裝置／build 文字提及與 Amazon 裝置識別資料，但沒有返回一個
  可驗證的 exact PS7330 signed boot、kernel Image 或 vmlinux 下載。
- 目前本機 exact-device 證據仍是 PS7330 source + denied boot read；本機
  boot artifact 是 PS7331，不能代替 PS7330。

### 高可信推論

- 在目前已檢索的公開結果範圍內，沒有新的 exact signed artifact 可以補上
  GhostLock 的 binary provenance 缺口。

### 待驗證

- Amazon 私有更新服務、授權維修管道或未被搜尋引擎索引的鏡像是否保存
  exact PS7330 signed artifact。

### 已排除／不採用

- 將一般 KFTRWI/trona build mention 當成 boot binary。
- 將 PS7331 official OTA／boot image 當成 PS7330 signed target。

### 因風險拒絕測試

沒有下載或執行未知 firmware、boot image、root payload 或 exploit；沒有
進行 OTA、fastboot、BROM/DA、boot write 或 partition write。

## Search scope

| Query | Scope | Result |
|---|---|---|
| `"PS7330.4104N" boot.img trona KFTRWI` | Public web | Device/build mentions only |
| `"Fire_HD10" "PS7330" OTA` | Public web | No exact signed artifact returned |
| `site:github.com trona PS7330.4104N boot` | GitHub-scoped | No exact target artifact returned |
| `site:amazon.com Fire HD 10 7.3.3.0 update` | Amazon-scoped | General device/update references only |

Amazon’s device specification identifies the Fire HD 10 (2021, 11th Gen) as
`KFTRWI`/`trona` on Android 9/API 28/Fire OS 7, but that page is device
metadata rather than a signed boot artifact:
[Amazon device specification](https://developer.amazon.com/docs/device-specs/ft-identify-tablet-devices.html).

## Decision

The exact signed PS7330 binary remains an evidence gap. The next responsible
step is to obtain it through an authorized, version-matched source or keep the
GhostLock conclusion at source/inspected-image scope. No mismatched image or
generic MTK loader should be used to fill this gap.
