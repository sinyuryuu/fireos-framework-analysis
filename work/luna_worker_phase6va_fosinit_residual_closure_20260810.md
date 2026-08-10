# Phase 6VA — fosinit residual closure（主機端靜態分析）

日期：2026-08-10。範圍限定為檔案、雜湊、XML fosinit、baksmali disassembly 與 JADX 輸出；未呼叫 Binder、未發送 broadcast、未修改裝置或套件/設定狀態。

## 結論

本輪完成 residual group 的靜態入口盤點與 `caller → gate → identity/user scope → sink` 判定，但不能把所有 group 宣告為安全閉合。CSV 是逐 group 的機器可讀結果；`PARTIAL` 表示入口與至少一段 gate/sink 已定位但仍有未解析 caller 或 scope，`UNKNOWN` 表示現有輸入不足以證明鏈路，`UNRESOLVED_AUTHZ` 表示 sink/註冊行為可見而授權邊界仍未閉合。

最強的主機端證據如下：

* launcher hijack 的 `canSeeHomeTask` 取 `UserHandle.getCallingUserId()`，並同時使用 SELinux access 與 package signature 檢查；其 permission-manager 路徑把 `READ_LOGS` revoke 明確帶入 `UserHandle`。這可閉合 gate/identity 的一段，但不等於所有 caller 路徑均已證明。
* package recency 的 callback 將 `userId` 帶入 `sendBroadcastWithDelay`，且先呼叫 `PackageRecencyUtils.shouldSendBroadcast`；因此 filter gate 與 user scope 可定位，broadcast receiver 的最終受眾仍需 caller/manifest 拓撲才能完全閉合。
* CRL service 發布 `crlsetmanager` Binder，`dump` 有 `android.permission.DUMP` 檢查；但 `checkTrusted` 的可見 Binder method 直接進入 trust manager，現有片段沒有同等 caller permission gate，故保留 `UNRESOLVED_AUTHZ`。
* Tablet broadcast relay 在 system service `onStart` 建立 receiver，註冊 `USER_BACKGROUND`/`USER_FOREGROUND` 並使用 `UserHandle.ALL`；這是明確 all-user scope，但 receiver 的轉發 sink 與授權仍未閉合。
* ToddlerMode 的 JADX 顯示 `isScreenPinningActive && TODDLER_MODE_USER_SELECTION` gate，以及 Secure settings observer/user `-2`；這支持 child/toddler scope 判定，但不替代 system-server callback 的 caller/authz 證據。

## Residual group 覆蓋

已覆蓋：`keypolicy/launcherhijack`、`appsettings`、`packagewhitelister`、`factoryresetwhitelist`、`packagerecency`、`user`、`toddler/freetime`、`fireossystemota`、`crlsetmanager/amazoncertpininstall`、`core`、`receiverfilter/tabletbroadcastrelay`。`amazon-services` 既有同名 fosinit（較早輸出）與 Phase 6JD 路徑均作為註冊拓撲交叉比對。

Phase 6UR 沒有以可搜尋的獨立檔名出現在 workspace；因此本報告把使用者明列的 residual group 作為工作清單，並將不能由本地輸入證明的項目保留 UNKNOWN/未閉合，而沒有猜測 Phase 6UR 未提供的額外條目。

## 重要證據索引

* Phase 6JD fosinit manifest：`artifacts/phase6jd-fosinit-20260808-01/extraction-manifest.tsv`；其輸入 manifest SHA：`artifacts/phase6jd-fosinit-20260808-01/manifest.sha256`。
* fosservices 主要反編譯：`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`。
* JADX 使用者/幼兒模式：`decompiled/jadx/ota-PS7331/systemui/sources/com/amazon/systemui/utils/ToddlerModeManager.java`。
* 既有交叉輸出：`artifacts/phase6h/phase6h-framework-ipc-20260804-01/`、`artifacts/phase6k/`、`artifacts/phase6l/`、`artifacts/phase6kw-vendor-home-callbacks/`。
* 既有 user package-state writer 證據：`artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv`。

## 輸入 SHA（aggregate 定義）

以下 aggregate 是對各目錄內相對檔案路徑排序後，逐檔 SHA-256 清單再做 SHA-256；不是裝置執行期 hash。檔案數/bytes 用於偵測輸入變動。

| input | files | bytes | aggregate SHA-256 |
|---|---:|---:|---|
| `artifacts/phase6jd-fosinit-20260808-01` | 125 | 143012 | `85c9b129d52e81aa77f0b7ef2d594b748f02362762332795ef54a76c1851380e` |
| `artifacts/amazon-services` | 14 | 19549 | `70d3db44f744fbf8fe54daeeae286d931f9a99136e1a2ff3fc44a380ecb9a78d` |
| `decompiled/baksmali/vdexExtractor` | 18 | 592704965 | `b426afd2f2fa5342f819dd142c67a643f9019a99f3fef50f6920ed35545d6c26` |
| `decompiled/jadx/ota-PS7331` | 29173 | — | `638dafcd94a6cb71c428626e6d1b28aae3da4c4cc95e78235a21cd667e620478` |
| `artifacts/phase6h` | 7 | — | `0e71b4d3e956b8891e4855b043a6de053002805695bce227abf70d21f1f0419e` |
| `artifacts/phase6k` | 84 | — | `6123fad7346dd06e9521c2b13759d503b13520a52e28ed99de91d415e0ba7faa` |
| `artifacts/phase6l` | 8 | — | `c058f65d86302817b5b7bbbea91250f09a0dea79dd892ddb3fb6e58adea1fbd4` |
| `artifacts/phase6kw-vendor-home-callbacks` | 5 | — | `1c7afb7a5777ff0e2bafe59a9c633b0eb8ea50973bdde00f701e9edd26826808` |

## 限制與未閉合證據

反編譯輸出可能缺失 parent callback、Binder stub、manifest permission、SELinux 或 framework side gate；marker 不證明 caller 可達。尤其 `appsettings`、`factoryresetwhitelist`、`fireossystemota`、`core` 的可見 fosinit 只提供 callback registration，沒有足夠方法體證據。`crlsetmanager`、`tabletbroadcastrelay` 的 receiver/Binder surface 已定位，但 caller authorization 仍是 residual。這些項目在 CSV 中刻意沒有標成 CLOSED。
