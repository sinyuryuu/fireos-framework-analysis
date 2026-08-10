# Phase 20D — Phase 1–19 no-repeat / residual reconciliation

日期：2026-08-10（Asia/Taipei）  
範圍：只讀整理現有 Phase 1–19 的 `findings/`、`adb/`、`artifacts/`、`output/`、`tools/`、`work/`；本輪未連裝置、未執行 ADB、未重測、未送 Binder/broadcast、未操作 driver/OTA/root，也未修改既有檔案。

## 去重結論

Phase 19 已把以下九個大面向列入 no-repeat：HOME、KFT/child profile、private IPC、prewarm、DPM/profile、Accessibility/redirect、OTA/OOBE、CVE/GhostLock、driver/root。因此本報告不把「再看一次 resolver、KFT、service list、prewarm、DPM、Accessibility、OTA、CVE 或 driver」列成新候選。

掃描 Phase 1–19 的 work 索引後，真正仍有高價值且粒度不同的 residual 僅有四項：

1. 全量 `fosinit` callback/receiver/policy fan-out 到 method gate/sink 的完整性。
2. Play/Vending 已恢復但仍有 partial/duplicated branch 的下游語意，特別是 exported receiver 的 token/creator path 與 DSE `g()` 分支。
3. ION ELF caller 已知，但 top-level process → loader → `/dev/ion` → downstream effect 尚未閉合。
4. `PackageManagerDenyList` 的 host resource membership 與 live persisted membership 之間的證據界線；live file content 並未取得。

## 候選矩陣

| ID | 未覆蓋的窄候選 | 已有 test IDs / 已做 evidence | 實際既有命令或輸入 | Phase 20D 分類 | 可得到的價值 | 不可宣稱 / 缺 evidence |
|---|---|---|---|---|---|---|
| `P20D-FOSINIT-001` | 244 個 fosinit XML entry 中，`amazonservicespolicy`、`core`、`tabletkeypolicy`、`amazonappsettings`、auxiliary user、OTA callback、`receiverfilter/tabletbroadcastrelay` 的 registration → implementation → method gate → sink union | `P6-UQ`/`P6-UQ` completeness ledger；`P6-TM/6RS–6SQ` private contract closures；Phase 7–19 callback and broad-surface reports。尚無一個 Phase 1–19 test ID 完成全部 244-entry fan-out | 已保存 inputs：`artifacts/phase6jd-fosinit-20260808-01/extraction-manifest.tsv`、`artifacts/phase6h/.../fosinit-edges.csv`、`artifacts/phase6k/.../service-surface.csv`、`artifacts/phase6l/.../contract-methods.csv`、`artifacts/phase6mv-runtime-report-20260810-02/runtime-summary.csv`。本輪未執行 parser | `HOST_ONLY_RERUN` | 可補齊哪些 callback 只是 registration、哪些有 local gate、哪些真的接 package/component/HOME/settings/user/OTA sink，縮小「未審 entry」範圍 | 不能由 registration/runtime listing 推導 reachability；缺 callback-by-callback source join、sender identity、method-local gate、effect sink。不得呼叫任何 entry |
| `P20D-VENDING-002` | `LauncherConfigurationReceiver` 的 verificationToken/creator 分支與 DSE `g()` duplicated-block/branch equivalence；下游是 restore metadata、browser/search/secure-settings，不是 HOME writer | `P6PZ` Vending follow-up 已恢復主要 body，但明確保留 `g()` branch partial；既有 receiver test 只有 registration/read-only observation，沒有 broadcast/bind/injected PendingIntent test | `artifacts/phase6mb-vending-static-20260810-01/manifest-print.txt`、`artifacts/phase6ps-vending-receiver-20260810-01/LauncherConfigurationReceiver.java`、Vending JADX/DEX/smali；既有 registration input `artifacts/phase6k/readonly-device-20260805-01/preferred_activities.stdout.txt`。本輪未送 broadcast 或 bind | `HOST_ONLY_RERUN`；live trigger `RISK_REJECTED` | 可判定 exported/no-permission 是否仍被 token/creator/setup gate 完整約束，並界定 secure-settings/browser downstream 是否越出 Phase 19 HOME/private-IPC 邊界 | 不能稱為 HOME replacement、Fire writer 或 arbitrary broadcast sink；缺 duplicated `g()` exact branch equivalence、完整 creator/package authorization join。不得構造 PendingIntent、broadcast 或 DSE Binder call |
| `P20D-ION-003` | 已知 `gralloc`/`hwcomposer`/DRM/media ELF 對 ION library 的 imports，但 top-level process、dynamic loader/dlopen、service-to-HAL mapping、實際 `/dev/ion` consumer 尚未閉合 | Phase 5 library-only、Phase 6 driver policy、Phase 9 ELF inventory、`P6-TM-B` ION loader graph；沒有 Phase 19 專門的 process-provenance test ID | `work/luna_worker_phase6tn_ion_loader_graph_20260810.csv`、`work/luna_worker_phase6tk_ion_process_provenance_20260810.md`、Phase 9 ELF inputs、init/VINTF/SELinux artifacts。可用既有 `objdump`/`nm`/loader parser，未執行 device node 操作 | `HOST_ONLY_RERUN`；runtime node observation `RISK_REJECTED` | 可把 library capability 降級或升級為具名 process/domain/load path，並確認是否存在敏感 downstream effect | ELF DT_NEEDED、symbols、SELinux allow 不等於 invocation；缺完整 dlopen target、init/service ownership、runtime call/node evidence、effect join。不得 open/read/write/ioctl `/dev/ion` 或任何 driver node |
| `P20D-DENYLIST-004` | host-extracted PS7331 resource 的 `packages_deny_list` membership 與 `/data/system/PackageManagerDenyList` live persisted set 的差異 | `P6PW`/Phase 7E 已閉合 resource seed/provenance；Phase 1–19 只有 protected rejection 與 live file metadata，沒有 live content read | Host inputs：`artifacts/phase6ap/denylist-resource-closure-20260805-01/`、extracted `fireos-res.apk`/raw JSON、saved live metadata stdout/hash。沒有可用的 live content artifact；本輪未 ADB/pull/chmod/read | `SAFE_READONLY` 只限既有 host artifact/hash comparison；live privileged read `RISK_REJECTED` | 可精確維持三層 distinction：resource membership = observed、live persisted membership = unknown、protected rejection = observed runtime behavior | 缺 live `DenyListKeyPackages` content/privileged capture；不能把 resource seed 或 rejection 推成 live literal membership。不得讀取、改權限、refresh 或替換 system-owned deny-list |

## 執行分類

### 可 host-only 重跑

- `P20D-FOSINIT-001`：只讀 XML、JADX/smali/disassembly、fosinit edges、contract tables、runtime summary，做 registration/class/gate/sink join。
- `P20D-VENDING-002`：只讀 manifest、DEX/smali/JADX，補 `g()` branch equivalence、creator/token/data-flow；不得觸發 receiver/service。
- `P20D-ION-003`：只讀 ELF `DT_NEEDED`、relocation、`nm`/`objdump`、init/VINTF、file-context/policy，補 process/loader graph。

### 可安全唯讀

- `P20D-DENYLIST-004` 的 host artifact/hash/schema/path comparison。
- 既有 saved runtime summary、service list、metadata、manifest 與 hash manifest 的交叉檢查。

這裡的「唯讀」不包含本次連裝置；本輪沒有 fresh state。

### 需風險拒絕

- 觸發任一未閉合 fosinit callback/receiver、Vending broadcast、DSE Binder 或 private service transaction。
- 開啟或操作 `/dev/ion`、CMDQ、M4U、gsensor 或其他 driver node。
- 讀取 live system-owned deny-list content 若需要繞過 ACL、改權限或 privileged Binder。
- OTA/recovery/updater、reboot、package/settings mutation、root/exploit、partition/bootloader 操作。

這些操作不會被當成 Phase 20D 的 negative runtime result；它們只是明確的安全拒絕。Phase 19 已將同類 runtime replay 列為 no-repeat。

## 排除清單（與 Phase 19 重複）

| 已排除面 | 原因 |
|---|---|
| HOME / User-0 restoration / deny-list 對 HOME 的一般推論 | 已在 `P19D-HOME-001` 收斂；本報告只保留 deny-list live membership 證據界線，不重做 HOME。 |
| KFT / child / DPM / profile | 已在 `P19D-KFT-002`、`P19D-DPM-005` 收斂；不建立 user、不切換、不送 tx。 |
| private IPC / H2 / prewarm | 已在 `P19D-IPC-003`、`P19D-PREWARM-004` 收斂；Vending 只保留其特有的 host-side branch gap。 |
| Accessibility / redirect | 已在 `P19D-ACCESS-006` 收斂；不再 enable secure setting、安裝 APK 或重播 redirect。 |
| OTA/OOBE、CVE/GhostLock、driver/root | 已在 `P19D-OTA-OOBE-007`、`P19D-CVE-GHOSTLOCK-008`、`P19D-DRIVER-ROOT-009` 收斂；本報告的 ION 候選只做 library/process provenance，拒絕 node/runtime。 |

## 最小安全下一步

若繼續，優先順序是 `P20D-FOSINIT-001` → `P20D-ION-003` → `P20D-VENDING-002` → `P20D-DENYLIST-004`。前三者可完全在 host corpus 上完成；第四者只能修正 evidence wording，不能在沒有既有 privileged artifact 的情況下補 live membership。

本報告不把「未找到」升格為「不存在」，不把拒絕操作升格為 negative result，也不宣稱 Phase 1–19 之外的 fresh device state。

## 來源

主去重索引：`work/luna_worker_phase19_reconciliation_20260810.md/.csv`。 residual evidence：`work/luna_worker_phase6uq_fosinit_completeness_20260810.md/.csv`、`work/luna_worker_vending_skipped_methods_followup_20260810.md/.csv`、`work/luna_worker_phase6tk_ion_process_provenance_20260810.md/.csv`、`work/luna_worker_phase6tn_ion_loader_graph_20260810.md/.csv`、`work/luna_worker_denylist_provenance_followup_20260810.md/.csv`、`findings/phase-19-evidence-index.md`。
