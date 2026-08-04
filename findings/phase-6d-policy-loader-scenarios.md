# Phase 6D：`/init` policy-loader 四情節判定

## 範圍

本報告把既有 PS7331 stripped `/init` 指令級 audit、AOSP Android 9
`system/core/init/selinux.cpp` anchor 與唯讀裝置 snapshot 合併。沒有執行
`/init`、改寫 boot property、選擇 alternate policy、繞過 AVB、讀寫 kernel
memory、觸發 crash 或執行 root payload。

Canonical scenario artifact：
`artifacts/phase6d/phase6d-policy-scenarios-20260804-01/`。

## 結果

| 情節 | 判定 | 信心 | 證據摘要 |
|---|---|---|---|
| S1 userspace 可控屬性 | **待驗證** | Hypothesis | 尚沒有 source-level 或 CFG 證據把 shell／untrusted-writable 的 `persist.*` 或 `/data` 標誌連到 rootable branch。 |
| S2 boot／kernel cmdline | **高可信推論** | Strong evidence | `/init` 有 `androidboot.selinux`／`permissive` parser candidate，並有 standard/rootable path-builder call sites；裝置為 locked、Enforcing，shell 不能讀 `/proc/cmdline`。 |
| S3 AVB／signature／fuse | **待驗證** | Hypothesis | `/init` 含 `FsManagerAvbHandle`、`avb_slot_verify`、BoringSSL 與 `SIGNATURE_MISMATCH` markers，但目前沒有 CFG edge 證明它們 guard rootable policy 或讀 eFuse。 |
| S4 dead code／編譯殘留 | **已排除（純字串殘留）／待驗證（runtime reachability）** | Strong evidence | rootable literals 有 ADRP/ADD code references，`0x41ae44` 設定 `w5=1`，並在 `0x41be48` 以 `tbnz` 分到 `0x41c30c`；不能再以 strings-only 解釋，但分支是否在 stock boot 被走仍未知。 |

## 重要限制

`rootable_*` 檔案存在、`/init` 引用它們、或 AVB 字串存在，都不能單獨推出
目前裝置會載入 rootable policy。`0x41ad00`、`0x41af80`、`0x41bd60`、
`0x41be00` 仍是 stripped binary 的人工標籤，不是可直接宣稱的原始函式名稱。

## 最小後續目標

只做主機端：完成 `0x41ad00–0x41bf30` 的 CFG、caller／callee 與資料流映射，
並將 AVB call sites 與 policy-loader window 對齊。若沒有 matching symbolized
`/init` 或 Amazon `system/core/init` source，應把 selector 保持為
**待驗證**，而不是猜測 `w5`、`persist.*` 或工程模式語意。

## 明確拒絕

Boot property／cmdline injection、alternate SELinux policy selection、AVB
verification bypass、remount、bootloader／fastboot、image write、futex race、
kernel panic、heap shaping、kernel memory operation 與 privilege-escalation
payload 均不在本階段執行範圍。

<!-- End of report -->
