# Phase 5Q — Android CMDQ implementation 與 Fire runtime 對照

## 範圍與安全界線

本輪只回答「Android 實作如何使用 MediaTek CMDQ」以及它與目前 Fire HD 10
保存證據的 ABI 對照。分析在主機端完成，讀取已保存的 exact source excerpt
與既有一次性 runtime 結果；沒有下載、編譯、安裝或執行 exploit/PoC，也沒有
新增 ioctl、device-node、kernel、bootloader 或分割區操作。

裝置基線仍為 `KFTRWI / trona / MT8183 / PS7330.4104N`、Android 9、Linux
`4.4.146+`、SELinux enforcing。原始 runtime 結果不是本輪重跑。

## 1. Android 公開實作是什麼

官方 AOSP 的 CVE-2020-0069 實作位於 CTS security bulletin test，形式是
native `cc_test`／`poc.c`，不是可以直接安裝的普通 APK。AOSP 的 CTS commit
記錄了 `CVE-2020-0069/Android.bp` 與 `poc.c`，並以 CTS host test 啟動它：

`cts-tradefed run cts -m CtsSecurityBulletinHostTestCases -t android.security.cts.Poc20_03#testPocCVE_2020_0069`

其重要特徵（只做介面層摘要，不在本專案重現 payload）是：

- 嘗試多個歷史節點名稱，例如 `/dev/mtk_cmdq`、`/proc/mtk_cmdq`、
  `/dev/mtk_mdp`；
- 使用歷史 CMDQ v2 request contract：write-address #7、free #8，以及
  command execution #3；
- 以 userspace 結構、DMA buffer 與 command buffer 驗證 driver 是否接受
  該歷史介面；
- 這是漏洞測試／kernel-memory 風險路徑，不是安全的版本偵測 API。

NVD 將 CVE-2020-0069 描述為 MediaTek CMDQ ioctl 輸入驗證不足造成的
out-of-bounds write，並列為 Android kernel 的本地提權問題。Quarkslab 的
技術分析則說明歷史漏洞利用的是 CMDQ ioctl、DMA 與實體記憶體路徑。這些
來源說明實作原理，但不證明目前 PS7330 binary 仍 vulnerable。

## 2. 與 Fire exact source 的對照

| 對照項 | Fire v2 source excerpt | Fire v3 source excerpt | 判定 |
|---|---|---|---|
| `CMDQ_IOCTL_ALLOC_WRITE_ADDRESS` | `cmdq_driver.c:709–752` 有 case | `cmdq_driver.c:663–706` dispatcher 沒有 case | 已證實，source scope |
| request #7 處理 | `copy_from_user`、`cmdqCoreAllocWriteAddress`、`copy_to_user` | 未列入 dispatcher | 已證實，source scope |
| unknown ioctl | 未使用本段作為結論 | `cmdq_driver.c:700–703` 回 `-ENOIOCTLCMD` | 已證實，source scope |
| MT8183 build selection | 不在 v2 allow-list | exact Makefile 對 MT8183 選 v3 | 已證實，source/config scope |
| 已保存 runtime | 不適用 | `open_ret=3`、`ioctl_ret=-25`（`-ENOTTY`） | 已證實，runtime scope |

因此，既有 `MTK-SU-CMDQ-T03` 以舊 v2 contract 初始化，以及後續
`CMDQ-IOCTL-V3-COMPAT-T01` 對 request #7 的 bounded 結果，與 exact source
形成一致的「v2 payload 對 v3 dispatcher」解釋。這是對已完成測試的靜態
對照，不是對 v3 其他 ioctl 的安全保證。

## 3. 可重現的主機端分析

分析器不連接裝置，拒絕覆寫既有輸出：

```sh
python3 tools/scripts/analyze_phase5q_android_cmdq_implementation.py \
  --dry-run \
  --v2-excerpt artifacts/phase5/exact-source-search-20260803/cmdq-source-members-20260803-v6/v2_driver-excerpt.txt \
  --v3-excerpt artifacts/phase5/exact-source-search-20260803/cmdq-source-members-20260803-v6/v3_driver-excerpt.txt \
  --runtime-result adb/phase5/CMDQ-IOCTL-V3-COMPAT-T01-20260803-01/probe.stdout.txt \
  --output artifacts/phase5/android-cmdq-implementation-review-20260804-01

python3 tools/scripts/analyze_phase5q_android_cmdq_implementation.py \
  --v2-excerpt artifacts/phase5/exact-source-search-20260803/cmdq-source-members-20260803-v6/v2_driver-excerpt.txt \
  --v3-excerpt artifacts/phase5/exact-source-search-20260803/cmdq-source-members-20260803-v6/v3_driver-excerpt.txt \
  --runtime-result adb/phase5/CMDQ-IOCTL-V3-COMPAT-T01-20260803-01/probe.stdout.txt \
  --output artifacts/phase5/android-cmdq-implementation-review-20260804-01
```

Generated JSON/TSV is host-derived evidence only. The input runtime file is the
already archived output of `CMDQ-IOCTL-V3-COMPAT-T01`; the analyzer never calls
`adb`, opens `/dev/mtk_cmdq`, or interprets a returned address.

## 4. 結論分級

### 已證實

- AOSP 的公開 CVE-2020-0069 Android implementation 是 CTS native test，使用
  歷史 CMDQ v2 contract。
- Fire exact source 的 MT8183 build selection 對應 v3；v3 dispatcher 的
  unknown-request branch 回 `-ENOIOCTLCMD`。
- 已保存的單次 request #7 runtime 結果為 raw `-ENOTTY`，沒有取得 root、
  沒有改變 Android 狀態，也沒有重試。

### 高可信推論

- 已測的 `mtk-su`／AOSP v2 CMDQ implementation 失敗，主要原因是 request
  contract 與目前 MT8183 v3 dispatcher 不匹配。
- 「把其他 Android 裝置的 mtk-su 或 CMDQ PoC 改名後直接執行」不是有效的
  Fire target adaptation。

### 待驗證

- signed PS7330 kernel 是否在 v3 的其他路徑存在私有 backport、另一個漏洞或
  不同的 permission/validation 行為。
- exact signed binary 是否與公開 Fire source 的每個 CMDQ member 完全一致。

### 已排除／不採用

- 把 AOSP CTS PoC 當成可安全安裝的 APK。
- 把已保存的 `-ENOTTY` 寫成「所有 CMDQ 都安全」或「CVE-2020-0069 已被
  binary-level 證明不存在」。
- 重跑相同 request #7、嘗試 v2/v3 其他非零參數，或用 DMA/實體位址資料
  進行探測；這些不屬於本輪主機端分析。

### 因風險拒絕測試

- 任何 command buffer、DMA allocation、physical-address read/write、
  malformed ioctl、alternate v3 ioctl、kernel panic/root trigger。
- 任何透過 BROM/DA、fastboot、recovery、boot image 或分割區取得 exact
  signed kernel artifact 的操作。

## 5. 下一步邊界

目前 Android implementation 的研究價值已完成到「介面與版本適配」：可以
作為 source-level 對照，不能作為本機 root payload。若要再往 live kernel
驗證，必須另立針對 `KFTRWI/PS7330/MT8183` 的 operation-specific Level 3
報告，列出精確 binary hash、單一操作、預期 panic/reboot、資料損失、恢復
方法與替代的 host-only 分析；本報告不授權該操作。

## 來源與原始證據

- AOSP CTS CVE-2020-0069 commit：
  `https://android.googlesource.com/platform/cts/+/41603998db75f63a00581e359eca408ff30a3da1/`
- NVD CVE-2020-0069：`https://nvd.nist.gov/vuln/detail/CVE-2020-0069`
- Quarkslab 技術分析：
  `https://blog.quarkslab.com/cve-2020-0069-autopsy-of-the-most-stable-mediatek-rootkit.html`
- Fire v2/v3 recovered excerpts：
  `artifacts/phase5/exact-source-search-20260803/cmdq-source-members-20260803-v6/`
- 已保存 runtime：
  `adb/phase5/CMDQ-IOCTL-V3-COMPAT-T01-20260803-01/`
