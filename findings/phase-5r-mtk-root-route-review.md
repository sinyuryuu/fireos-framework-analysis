# Phase 5R — MTK root 路徑重新核對：KoCleo fork、fenrir 與 LK patcher

## 結論摘要

本輪針對使用者提供的 `KoCleo/mtk-easy-su`、HackMD 清單，以及其中
MediaTek boot-chain 相關的 `fenrir`／`lkpatcher` 進行最新公開來源核對。
只讀取公開文字、GitHub API metadata、Git LFS pointer 與既有本機 artifact；
沒有下載、編譯或執行新的 root payload，也沒有進行 BROM/DA、fastboot write、
preloader/LK/boot 分割區操作。

目前沒有找到一個「新的、與 KFTRWI/trona/PS7330/MT8183 精確匹配」且足以
合理提交 live execution 的公開 root payload。

## 1. 裝置現況

本輪開始前的只讀核對：

| 欄位 | 值 |
|---|---|
| Serial | `G001LT0511550CFT` |
| Model / product | `KFTRWI` / `trona` |
| SoC | MT8183 / `mt8183` |
| Build | `Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys` |
| Kernel | Linux `4.4.146+`, arm64 |
| Verified boot | `green` |
| Flash lock | `ro.boot.flash.locked=1` |
| SELinux | `Enforcing` |
| HOME | `com.amazon.firelauncher/.Launcher` |
| ADB | `device`, shell UID 2000 |

這次只讀核對沒有改變裝置狀態。

## 2. KoCleo/mtk-easy-su 是否提供新的 payload

固定公開 commit：

`KoCleo/mtk-easy-su@8c6871ac7c15b8e98a47e25c35ab93b87e260475`

該 fork 的 `app/src/main/assets/mtk-su64` 不是新的 ELF，而是 Git LFS
pointer：

`oid sha256:328632e853ff6427af9f35cb83a91d9e960f35d01188ee66d46ae9c7ce7c7827`

本機既有、已經唯一執行過的 `MTK-SU-CMDQ-T03` binary SHA-256 同為：

`328632e853ff6427af9f35cb83a91d9e960f35d01188ee66d46ae9c7ce7c7827`

所以重新安裝或執行這個 fork 的 `mtk-su64` 不會改變測試前提；它會重複
先前 `Failed critical init step 3` 的同一 payload 路徑，沒有新的證據價值。

另外，fork 的 Android wrapper：

- 會把 `mtk-su`、Magisk init 與 `magisk-boot.sh` 從 assets 複製到 app 私有目錄；
- 會執行 shell command 與 Magisk boot script；
- manifest 宣告網路與開機完成接收權限；
- 以 `/sbin/su` 是否存在判斷成功；
- README 自己警告 2020-03 之後的 firmware 可能阻擋此方法。

這些是 wrapper 行為，不是對 PS7330 相容性的證明。既有實機測試已保存
UID 2000、SELinux enforcing、green verified boot 與 rollback 成功。

判定：

- **已證實：** KoCleo fork 的 `mtk-su64` 與先前已測 binary 相同。
- **已排除：** 把 KoCleo fork 當成新的 payload 再跑一次。
- **待驗證：** signed PS7330 kernel 是否存在其他未被該 payload 觸發的漏洞。

## 3. HackMD 清單中的 MTK boot-chain 路徑

HackMD 是研究索引，不是裝置相容性證明。其 MediaTek 相關項目主要包括：

| 公開項目 | 公開目標／操作層 | 與本裝置比較 | 判定 |
|---|---|---|---|
| `fenrir` | Preloader / `bl2_ext` / EL3 secure-boot chain | 公開支援清單沒有 `trona`；需要裝置特定 boot-chain 條件 | **因風險與相容性不足拒絕 live test** |
| `lkpatcher` | 讀取並修改 LK image、可輸出 patched image | exact PS7330 LK 無法由 shell 讀取；PS7331 LK 是 `VERSION_MISMATCH` | **僅 host-side review** |
| `oppo-mtk-fastboot-unlock` | 修改 factory preloader 並寫入 OPlus 裝置 | Amazon `trona`/PS7330 不是 OPlus target | **已排除作為直接路徑** |
| Dirty Pipe | Linux 5.8+ page-cache flaw | 本機 kernel 4.4.146+ | **已排除版本不符** |
| GhostLock | rtmutex/futex PI LPE | 已完成 source/Android port review；沒有 exact Fire payload | **待驗證但不執行 trigger** |

`fenrir` 的公開說明本身把它限制在特定 MediaTek boot chain，並警告錯誤
操作可能永久破壞裝置；`lkpatcher` 需要匹配的 LK image，且其功能本身
包括輸出 patched image。這兩者都不是可以從 Android shell 安全推導的
「測試命令」。

## 4. 為何本輪沒有提交新的 Level 3 live operation

目前沒有同時滿足下列條件的新候選：

1. exact `KFTRWI/trona/PS7330` target profile；
2. exact preloader/LK/DA/auth compatibility；
3. 明確的單一操作與成功／失敗訊號；
4. 可驗證的 recovery image／回復路徑；
5. 不把相鄰 PS7331 image、其他品牌 preloader 或 generic MT8183 alias 誤當成
   本機映像。

現有證據反而顯示：

- bootloader 讀取 `unlocked`/`secure`/`all` 已回覆 `locked hw`；
- shell 讀取 exact PS7330 LK 已被拒絕；
- workspace 只有 PS7331 的 boot-chain artifact，且已標示版本不匹配；
- Amazon source/config 與 runtime 已針對 CMDQ v3、futex、ION 等路徑做過
  host-only 或已核准的一次性邊界測試。

因此直接呼叫 `fenrir`、`mtkclient`、`lkpatcher`、preloader writer 或另一個
generic `mtk-su`，會把「未知相容性」直接轉成 boot-chain 寫入／brick 風險，
而不會形成可解釋的實驗結果。

## 5. 目前最佳下一步

在不新增 live exploit 的前提下，下一個最高價值工作是：

1. 繼續從官方 Fire source 與已保存的 Android property/boot-chain metadata
   交叉確認 `trona` 的 preloader/LK/DA 版本命名與安全檢查；
2. 尋找 exact PS7330 官方 package 或研究者合法取得的 matching boot/vmlinux
   artifact，並建立 hash/版本鏈；
3. 對 `fenrir`／`lkpatcher` 僅做 image-format、target profile 與控制流對照；
4. 只有當上述資料形成 exact target 與 recovery plan，才另寫一份新的、
   operation-specific Level 3 報告。

這不代表放棄低層研究；它把下一次 live 操作從「猜測性刷寫」提升到可解釋
的裝置特定實驗。

## 6. 證據與來源

- `artifacts/phase5/mtk-easy-su-current-review-20260804-01/`
- `adb/phase5/MTK-SU-CMDQ-T03/`
- `findings/phase-5-mtk-easy-su-root-followup.md`
- `findings/phase-5-mtk-compatibility-review.md`
- `findings/phase-5b-brom-identification-level3-report.md`
- `findings/phase-5-exact-ota-and-boot-chain-evidence.md`
- [KoCleo/mtk-easy-su pinned commit](https://github.com/KoCleo/mtk-easy-su/commit/8c6871ac7c15b8e98a47e25c35ab93b87e260475)
- [fenrir](https://github.com/R0rt1z2/fenrir)
- [lkpatcher](https://github.com/R0rt1z2/lkpatcher)
- [HackMD vulnerability index](https://hackmd.io/@lokey0905/rk-hQSzibl)
