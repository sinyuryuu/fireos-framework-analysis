# Phase 5AT：PS7330 exact artifact follow-up

## 結論先行

### 已證實

1. 目前裝置仍是 `KFTRWI/trona/PS7330.4104N`；既有 Phase 5T metadata 同時
   保存了 preloader/LK descriptor `d1a4a4b-20231011_072631` /
   `79172a1-20231008_072039`。
2. Amazon 官方 11 代更新入口目前標示 Fire OS 7.3.3.1，且其下載 endpoint
   重導向到 `update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin`，
   不是 PS7330。
3. FTVDB 的公開 11 代 firmware history 列出 PS7331、PS7329 及更早版本，
   沒有 PS7330 record；這與既有 workspace inventory 一致，但只是公開資料
   的 bounded absence。
   FTVDB 公開的 raw `com.amazon.trona.android.os.json` 也只含 PS7319、
   PS7321–PS7329 與 PS7331；其 snapshot SHA-256 為
   `7d80beaf572ee585449da48121b190b30cee7f92b1a69d3011b61d2668e6632a`。
4. 使用者提供的 source-notice 備份頁列出 11 代的
   `Fire_HD10-7.3.3.0-20240730.tar.bz2`，因此 7.3.3.0 source 是目前裝置的
   exact source family；它不是 signed boot image 或 loader。

### 高可信推論

- 在目前可驗證的公開來源中，沒有足以支撐 PS7330 signed-kernel offset、
  preloader/LK/DA 相容性或 recovery 的低層 artifact。
- PS7331 boot/Image 的 compiled GhostLock pattern 不能自動轉成 PS7330
  signed-binary 結論；目前最強的 PS7330 證據仍是 exact source/config。

### 待驗證

- Amazon 是否曾經透過歷史、區域或受控 endpoint 分發過完整 PS7330 package。
- descriptors 對應的 exact preloader/LK binary 是否能由研究者合法取得。
- PS7330 signed Image 的 `remove_waiter()` 是否與 7.3.3.0 public source 一致。

### 已排除

- 把官方目前的 PS7331 download redirect 當成 PS7330 artifact。
- 把 PS7331 preloader/LK/boot 當成目前裝置的 recovery 或 exploit input。
- 把 FTVDB 沒有 PS7330 record 解讀成「PS7330 絕對不存在」。

### 因風險拒絕測試

- 任何 BROM/DA loader upload、preloader/LK read/write、`seccfg`/RPMB 操作、
  fastboot unlock/flash、sideload、分割區讀寫或把 PS7331 寫入 PS7330。
- GhostLock futex race、kernel memory write、root payload 或 crash reproducer。

## Evidence and files

詳細來源與 HTTP metadata：
[`artifacts/phase5/ps7330-artifact-followup-20260804-01/metadata.md`](../artifacts/phase5/ps7330-artifact-followup-20260804-01/metadata.md)

FTVDB raw database：[com.amazon.trona.android.os.json](https://raw.githubusercontent.com/FTVDB/FTVDB/main/database/firmware/com.amazon.trona.android.os.json)

本結果與既有資料互相補強：

- [`phase-5t-ota-metadata-review.md`](phase-5t-ota-metadata-review.md)
- [`phase-5ai-exact-ps7330-artifact-search.md`](phase-5ai-exact-ps7330-artifact-search.md)
- [`phase-5ar-ps7331-compiled-rtmutex-review.md`](phase-5ar-ps7331-compiled-rtmutex-review.md)
- [`phase-5n-exact-source-ghostlock-review.md`](phase-5n-exact-source-ghostlock-review.md)

## Next highest-value step

繼續做 host-only 的 exact-source/build-input 對照，或取得合法且可驗證的
PS7330 signed boot/Image。沒有其中一項之前，執行 generic MTK loader 或
GhostLock payload 只會把版本未知轉成不可解釋的 boot/資料損壞結果，不能
有效回答「PS7330 是否可取得 temporary root」。
