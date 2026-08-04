# Phase 6D：`/init` Policy Loader 四情節複核

## 範圍與安全界線

本報告只合併已保存的 PS7331 `/init`、AOSP Android 9 原始碼、唯讀裝置
snapshot、Framework 靜態稽核與 OTA metadata。沒有執行 `/init`，沒有改寫
boot property、SELinux policy、AVB 驗證、分割區或 kernel memory，也沒有執行
root payload。

主要輸入：

- `/init`：`artifacts/phase6c/phase6c-image-policy-extract-20260804-06/root/init`
  （SHA-256：`e72ed4e90d73b88be341985ebd624725b67d67967d04157317456233e15f31fd`）。
- CFG：`artifacts/phase6d/phase6d-init-cfg-20260804-03/`。
- 四情節機器判定：`artifacts/phase6d/phase6d-policy-scenarios-20260804-01/`。
- AOSP anchors：`artifacts/phase6d/phase6d-init-pipeline-diff-20260804-01/pipeline.json`。
- 裝置唯讀 snapshot：`adb/phase6d/PHASE6D-ACTIVE-POLICY-RO-20260804-03/`。

## 最新判定

| 情節 | 判定 | 信心 | 可由現有證據說明的最窄結論 |
|---|---|---|---|
| S1：userspace 可控屬性或 `/data` 標誌 | **待驗證** | Hypothesis | 尚無資料流證據把 shell／untrusted-writable 狀態連到 rootable branch；不可把 `persist.*` 或 `/data/` 字串當成控制條件。 |
| S2：Boot／kernel cmdline | **高可信推論** | Strong evidence | `/init` 有 `androidboot.selinux`／`permissive` 的 parser candidate，並有 standard/rootable 兩組 path-builder call site；精確 selector 與 caller 仍未還原。 |
| S3：AVB／簽章／eFuse | **待驗證** | Hypothesis | AVB、BoringSSL、`SIGNATURE_MISMATCH`、`efuse` markers 存在，但尚未以 CFG 或資料流證明它們 guard rootable policy。 |
| S4：死碼／編譯殘留 | **已排除（純字串版本）／待驗證（stock runtime reachability）** | Strong evidence | rootable literal 有 ADRP/ADD code references；`w5=1` 進 common helper，且 `0x41be48` 存在明確分支。這排除「只有無引用字串」，但不證明量產開機會走該路徑。 |

## 指令級證據

`callsite-markers.csv` 記錄：

- `0x41ae44`：`orr w5, wzr, #0x1`。
- `0x41ae5c`：呼叫 `0x41be00`，標為 rootable candidate/common helper candidate。
- `0x41af78`：`mov w5, wzr`。
- `0x41af80`：呼叫同一個 `0x41be00`，標為 standard candidate/common helper candidate。
- `0x41be48`：`tbnz w5, #0x0, 0x41c30c`。

保守 CFG 顯示 block `B41bdf4` 的 terminator 位於 `0x41be48`，有兩條邊：

```text
B41bdf4 --branch-->    0x41c30c
B41bdf4 --fallthrough--> 0x41be4c
```

這是「存在 mode/path 分支」的證據，不是「rootable policy 已載入」的證據。
stripped binary 的間接 branch、原始 symbol、函式邊界與 runtime caller 尚未完全
解析，因此 `0x41ad00`、`0x41af80`、`0x41bd60`、`0x41be00` 都應繼續視為
保守人工標籤。

## AOSP 對照

官方 Android 9 r1/r61 `init/selinux.cpp` 的 anchors 在兩個 tag 中具有相同
SHA-256：`b2bb7d74d8cb8863d04b2172eedc22d0074129cab16c3335285fc9c2f9e69fa1`。
已確認的 AOSP 範圍包括 `StatusFromCmdline`、`IsEnforcing`、
`FindPrecompiledSplitPolicy`、`LoadSplitPolicy`、`LoadMonolithicPolicy`、
`LoadPolicy` 與 `SelinuxInitialize`。這證明可用 AOSP loader 作為 anchor，
但不構成 Amazon `/init` 的 source-level diff：官方 GPL source package 沒有
`system/core/init/selinux.cpp`。

## 裝置現況的限制性證據

`PHASE6D-ACTIVE-POLICY-RO-20260804-03/metadata.txt` 記錄：

- serial：`G001LT0511550CFT`。
- `device_mutation=false`、`policy_selected=false`、`boot_property_changed=false`。
- `fastboot_invoked=false`、`futex_triggered=false`。

該 snapshot 的 `getprop.stdout.txt`、`selinux_mode.stdout.txt`、
`proc_cmdline.stdout.txt` 等原始輸出及雜湊均保留。shell 對 cmdline、live
policy 與部分 kernel 狀態的讀取受 SELinux 限制；「讀不到」不能改寫成
「沒有該條件」。

## 對四種情節的下一個最小安全工作

1. 在主機端繼續還原 `0x41ad00–0x41bf30` 的 caller、callee 與暫存器資料流，
   尤其是 `w5` 的所有定義點和 `0x41bd60` parser candidate 的返回值去向。
2. 將 `FsManagerAvbHandle`／`avb_slot_verify` markers 的 call site 與上述
   policy-loader window 做控制流和資料依賴對齊。
3. 對照 AOSP `LoadPolicy` 的檔案路徑、錯誤分支與 selector 形狀；若沒有
   symbolized `/init` 或 Amazon `system/core/init` source，維持 UNKNOWN。
4. 檢查已解包的 policy 檔案、init rc 與 properties 的靜態關係，但不注入
   property、不替換 policy、不執行 `/init`。

## Root 結論

目前沒有安全、可重現的 temporary-root 路徑。S1 尚未證實，S2 只顯示可能
存在 bootloader-controlled selector，S3 尚未連到 rootable branch，S4 只排除
「純字串死碼」而沒有證明可達。任何為了取得 root 而進行 boot-property 注入、
alternate policy selection、AVB bypass、kernel race、panic、heap shaping、
未知 Binder 或分割區寫入，都超出本階段且被拒絕。

## 再現

```text
python3 tools/scripts/recover_phase6d_init_cfg.py --help
python3 tools/scripts/classify_phase6d_policy_loader_scenarios.py --help
python3 tools/scripts/audit_phase6c5_gpl_source_scope.py --help
```

上述工具只分析已保存檔案，並拒絕覆寫既有輸出；完整命令、輸入與雜湊見
各 canonical artifact 的 `result.md` 與 `sha256sums.txt`。
