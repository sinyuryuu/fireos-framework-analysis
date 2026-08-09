# Luna worker follow-up 2 — bounded host-only inventory

日期：2026-08-10（Asia/Taipei）
範圍：公開 HEAD `0e74afbfc7d96253373b2e65427ea4a66a93e561` 之後的工作樹、Phase 6/Launcher、Amazon IPC、OTA、KFT、核心/韌體與既有 captures/artifacts；只讀本機檔案。

## 執行界線與工作樹狀態

- HEAD：`0e74afbfc7d96253373b2e65427ea4a66a93e561`，subject `Add Phase 6MC permission and H2 caller audit`。
- 初始工作樹已有其他人的修改：9 個 tracked paths modified、約 1,625 個 untracked paths；未做 reset、clean、checkout、刪除或提交。
- 本報告建立前，`work/luna_worker_followup2_20260810.md` 不存在；本次只新增此檔案。
- 沒有執行 ADB、安裝、broadcast、activity、settings/package mutation、reboot/fastboot、未知 Binder/service call、ioctl、OTA/recovery、partition write、網路下載或 root/exploit。

## 查閱路徑與 hash anchors

主要查閱路徑：

- `PROJECT_STATUS.md`, `README.md`, `findings/evidence-index.md`, `PROJECT_INVENTORY.md`, `work/luna_worker_inventory.md`。
- `findings/phase-6bk-{report,evidence-index,followup-20260810,followup-evidence-index-20260810}.md`、`phase-6mb-vending-permission-and-state-writer-audit.md`、`phase-6mc-permission-and-h2-audit.md`、`phase-6ma-denylist-fosinit-and-kft-closure.md`。
- `findings/phase-6{j,k,n,o,q,r,s,t,u,y,z}-*.md` 及 `output/tables/phase6{j,k,n,o}*.csv`。
- `adb/phase6bk/`, `adb/phase6mb-vending-20260810-01/`, `adb/phase6mc-*`, `adb/phase6kft/`, `adb/phase6jd-fosinit-20260808-01/`, `adb/phase6je-native-overlay-20260808-01/`，以及既有 `adb/phase5/`, `adb/phase6*/` captures。
- `artifacts/phase6bk/`, `artifacts/phase6j/`, `artifacts/phase6n/`, `artifacts/phase6mb-*`, `artifacts/phase6mc-*`, `artifacts/phase5/`。
- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`, `.../boot-fosframework/disassembly.log`, `.../ota-PS7331/vdex-extractor/disassembly.log`；`firmware/original/`, `firmware/extracted/PS7331/`；`kernel/`；`tools/scripts/` 与 `tools/test-launcher-phase4/`。

可重用 hash：

| Artifact | SHA-256 |
|---|---|
| `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` | `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` |
| `artifacts/phase6mb-vending-static-20260810-01/base.apk` | `a5f456832018bbf571f915e949ea9dcd707ad514c269899e916b9b25d5297a50` |
| `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea` |
| `firmware/extracted/PS7331/boot.img` | `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` |
| `artifacts/phase6bk/ipc-ota-closure-20260810-02/summary.json` | `410dcbbdfe562198f00c214ed9efe7b14494f902f2957bd6f3c9a96d318e4b6d` |
| `artifacts/phase6bk/protected-broadcast-union-20260810-02/summary.json` | `4e44e4e1bb85a5067a2c26ab4a4539736b294e19b2164581691cad088b408abc` |
| `artifacts/phase6n/oobe-ipc-ota-audit-20260804-191216/summary.json` | `b3acfd9f3603e022277b41807e68989ad4295ae480d2416683e11f13ee1a2ee5` |
| `artifacts/phase6mc-caller-provenance-20260810-01/sha256sums.txt` | `fbb4f21dad1c3948bb3748fe7bcf652b6b136a6fb07e62cb4e7d7e6d51e1b11d` for `caller-provenance.csv`; manifest records input hashes |

## 去重後的研究結論

### 已完成／可關閉

- **Fire Launcher / User 0 邊界：** Phase 6BN/6EA/6KQ 等既有 evidence 已證實 shell 的 disable、component state、uninstall 路線在 PMS/Amazon protected-package gate 前拒絕；HOME 仍 Fire priority 50。Phase 6MB 的 Play Store bounded scan 也沒有 `com.amazon.firelauncher` literal、HOME writer 或 preferred-activity writer。
- **KFT：** `fosservices/disassembly.log` 的 Phase 6BK static chain（約 lines 54297–54325、54415–54478、55092–55118）確認 child-user-scoped Tahoe enable 與 Fire/Launcher3 state writer；`adb/phase6bk/PHASE6BK-SERVICE-RO-20260810-01/` 顯示私有 Amazon service 名稱可見不等於 shell handle，service check 為 not found。Phase 6EC 已閉合 shell tx3 reachability，不能把 static writer 稱為 untrusted caller exploit。
- **H2/child profile：** Phase 6MC 的 `com.amazon.alta.h2clientservice` exported service 有 signature-level `BIND_SERVICE`；static chain 是 H2 client → `CreateAndroidUserCommand` → `AmazonUserManager.createChildUser()`，未找到 Fire/HOME writer。這是合法 household/profile capability，不是 User-0 replacement。
- **OTA/post-install：** Phase 6J/N/O/Q/R/S/T/U/Y 等已整理 OOBE、`BOOT_AFTER_SYSTEM_OTA`、sideload path、otadexopt、block-image/write surface 與 permission/registration。Phase 6BK closure 明確為 `binder_invoked=false`, `ota_executed=false`, `recovery_executed=false`, `partition_written=false`, `root_attempted=false`。45 個保存 APK 的 protected-broadcast union 只在指定集合內命中 `BOOT_AFTER_SYSTEM_OTA` 一次，來源為 `android.amazon.perm`（APK hash `5b72bdfcfb91b28d2c751e548f60d406de5c3cbb235e47e232014abdebcdc058`）；不能外推為完整 runtime inventory。
- **核心/韌體/source：** PS7331 source、boot、OTA metadata、MT8183/trona kernel/source index 已有 hash 與 scope；source/Image 的 pre-fix correspondence 是 static/版本鄰近證據，不是 PS7330 exact installed image、runtime exploitability 或 root 證明。既有 PS7330/PS7331 資產不得交叉標成 exact-match。

### 重複或不應再做

- 再做 Fire disable/uninstall/component mutation、preferred HOME、child-user creation、KFT tx3/tx4 replay、未知 Amazon Binder transaction、service bind、protected broadcast replay、OTA/recovery、package install 或 launcher state mutation，均與既有 boundary/closure 重複或超出本任務限制。
- 再掃 Phase 6MB 的 Play Store Fire/HOME literal 與 generic setter 結果是重複；僅剩 permission provenance，不能以 granted permission 推導 protected-package bypass。
- 再將 `service list` 的 Amazon 名稱、static Binder Stub、或 `$20`/prewarm/OOBE identity-clear 直接寫成 low-privilege exploit，證據不足且已被既有 closure 限定為 caller/SELinux/permission boundary。

### 證據不足／尚未整理

- `artifacts/phase6mc-caller-provenance-20260810-01/caller-provenance.csv` 已有 7-row matrix，唯一標成 `low_privilege_caller_found` 的是 IAmazonUserManager tx4；該結果只證實 settings confused-deputy sink，沒有 Fire/HOME sink。需把 tx4、KFT tx3、H2 addUser、prewarm、post-OTA OOBE sender 的 caller identity、gate、identity clear、sink、user scope 與 dynamic-test prohibition 以 source line/hash 對齊。
- `/data/app` Play Store grants 與 extracted privapp XML 的版本/簽章 provenance 尚未完全閉合；Phase 6MB 已明確指出這是 metadata/history 問題，不是可安全實測的 writer。
- H2 `onBind`/`addUser` 的 signature gate 與 system-server `createChildUser` 後續 package-state callback 已有主要 source chain，但尚未完成同一 hash-pinned source index 的 caller-to-sink completeness；不可宣稱 shell relay 或成功 child creation。
- OTA post-install 的 source paths 已有大量 rows，但「sender identity → protected permission → receiver state predicates → first write sink」仍可做 offline normalization；不可執行 crafted OTA、broadcast 或 recovery。

## 下一個最小安全研究包（建議主 Agent 執行）

優先採用**離線 caller→sink provenance normalization**，不接觸裝置：

1. 以既有 `artifacts/phase6mc-caller-provenance-20260810-01/input-manifest.csv` 與 `sha256sums.txt` 為固定輸入，核對 H2 source、`fosservices/disassembly.log`、Phase 6BK/6ER/6Q/6R findings 的 hash 和行號。
2. 建立一份 host-only table（可由主 Agent 決定輸出位置）欄位：entry/caller、registration、permission/SELinux gate、Binder identity handling、sink、user scope、observed result、evidence class、reason not runnable。
3. 優先核對三條非重複邊：
   - H2 signature-bound `addUser` → `createChildUser` → child-only KFT writer；
   - ordinary APK reachable tx4 → `setUserSetupComplete` settings-only sink（明確標註非 HOME）；
   - system-server `onBootPhase(550)` → protected `BOOT_AFTER_SYSTEM_OTA` → OOBE settings/component sink，並與 OTA package write chain 分離。
4. 只用 `rg`, `sed`, `sha256sum`, CSV/JSON parsing 等 host read-only 操作；不執行任何 service call、broadcast、activity、settings/package command、ADB、reboot、OTA、install、ioctl 或 network。

預期最小輸出：一張 3–5 row provenance matrix，加上「confirmed static / confirmed runtime boundary / strong but bounded / unknown」分類；不新增 vulnerability ID，除非主 Agent 找到既有證據未涵蓋的 caller-to-sink fact。

## 驗證與限制

- 本次只做本機檔案盤點、既有結果閱讀、Git identity/status 與 hash 核對；沒有重跑會觸碰裝置或建立其他輸出的研究腳本。
- `git diff --check` 可作本檔建立後的 host-only formatting check；不得將既有 modified/untracked paths 視為本次產物。
- decompiler/JADX 輸出是近似 source；critical method semantics 應回看 smali/disassembly。保存 APK/source 與 live package 若非同一 immutable snapshot，permission/provenance 結論須標 version-scoped。
- `adb/` 下的 raw captures 是既有證據，不代表本次執行 ADB；任何 capture 內出現的 historical mutation 都必須按其 finding 的 rollback/safety classification 解讀。
- 報告未證實 root、runtime exploitability、未知 Binder service 安全性、PS7330 exact image correspondence、完整 runtime protected-broadcast inventory 或 low-privilege Fire/HOME writer。
