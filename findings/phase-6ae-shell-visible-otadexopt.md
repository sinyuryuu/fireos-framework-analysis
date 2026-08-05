# Phase 6AE：shell-visible `otadexopt` contract audit

## 目的與界線

Phase 6AC／6AD 已把 `BootAfterSystemOTAReceiver` 納入高風險、非可直接採用
的 OTA/OOBE 研究面。本階段不觸發該 receiver，也不把 OTA lifecycle 當成
可用入口；只對既有 PS7331 保存證據中的 `otadexopt` 服務做 host-only
介面還原。

禁止並且未執行：`service call`、手寫 Binder transaction、OTA／recovery、
`prepare`／`dexoptNextPackage`／`cleanup`、未知 read transaction、廣播、
OOBE state mutation、Root、重啟及分割區操作。

## Phase 6AF correction

本文件的原始版本把 concrete implementation 標成「尚未定位」。該狀態已由
Phase 6AF 更正：保存的 PS7331 services VDEX 確實包含
`com.android.server.pm.OtaDexoptService`、`main()` 的 `otadexopt` 註冊、
`onShellCommand()` 及所有對應實作。原始 Phase 6AE artifact 保留作歷史介面
審計，不再作為「implementation 不存在」的證據；請以
`findings/phase-6af-otadexopt-implementation-closure.md` 與
`artifacts/phase6af/otadexopt-implementation-closure-20260805-03/` 為實作層
權威結果。

## 已證實

1. 保存的 shell-side `service list` 包含：

   ```text
   otadexopt: [android.content.pm.IOtaDexopt]
   ```

   來源：`adb/phase6t/PHASE6T-IPC-RO-20260805-01/service_list.stdout.txt:153`。

2. 保存的 `dumpsys otadexopt` 返回成功但沒有文字輸出。這只說明 ordinary
   dump 沒有提供可用診斷資料，不表示 private Binder method 可用。

3. PS7331 boot-framework VDEX 的 `IOtaDexopt` interface 有六個無參數方法：

   | Transaction | 方法 | 靜態分類 | 本階段是否呼叫 |
   |---:|---|---|---|
   | 1 | `prepare()` | 可能建立／準備 dexopt 狀態 | 否 |
   | 2 | `cleanup()` | 可能清理 dexopt 狀態 | 否 |
   | 3 | `isDone()` | read-like status | 否 |
   | 4 | `getProgress()` | read-like status | 否 |
   | 5 | `dexoptNextPackage()` | 可能執行 dexopt 工作 | 否 |
   | 6 | `nextDexoptCommand()` | read-like 但可能暴露敏感命令／狀態 | 否 |

   Proxy transaction constants 位於
   `decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log:928324-928548`；
   Stub dispatch 位於 `:928549-928628`。

4. Stub 在保存的 disassembly 中可見 `enforceInterface()`，之後直接呼叫
   interface method；該 Stub 本身沒有可見的 method-local permission check。
   Phase 6AF 進一步確認 concrete service 的 class 與 publisher，但沒有把
   「class 內未找到 method-local permission marker」誤判為 authorization
   bypass；Binder、SELinux、service publication 與 caller policy 仍是獨立邊界。

5. `cmd otadexopt done` 與 `cmd otadexopt progress` 的既有唯讀 capture 已
   連到實際 service：`done` 在 `OtaDexoptService.isDone()` 以
   `done() called before prepare()` 拋出 stack，`progress` 返回 `1.00`。

## Phase 6AF 已閉合的實作事實

- `OtaDexoptService.main()` 位於
  `decompiled/baksmali/vdexExtractor/services/disassembly.log:482249-482263`，
  以 `ServiceManager.addService("otadexopt", ...)` 發布服務。
- `SystemServer` 在同一份 VDEX 的 `:107990-108045` 依
  `mOnlyCore` 與 `config.disable_otadexopt` 條件啟動它；相同形狀也存在於
  保存的相鄰 PS7331 VDEX。
- `prepare()` 會建構 dexopt command list，並在低空間分支呼叫
  `deleteOatArtifactsOfPackage()`；`nextDexoptCommand()` 會移除 command，
  `cleanup()` 會清除 `mDexoptCommands`。這些命令均未執行。
- `dexoptNextPackage()` 在此 artifact 直接建立並拋出
  `UnsupportedOperationException`；仍未在設備上呼叫。

## 尚未確認

- implementation 是否檢查 `DUMP`、`INTERACT_ACROSS_USERS`、system UID、OTA
  agent 或其他權限。
- `nextDexoptCommand()` 是否實際回傳命令字串，及其是否只限 system caller。
- 服務是否與 Amazon OTA package、PackageManager dexopt scheduler 或開機後
  post-install 流程相連。

## 判定

目前沒有證據把 `otadexopt` 連到 HOME resolver、Fire Launcher、Home key、
privilege transition 或 Root。它是標準 Android dexopt／OTA adjacent service
的靜態控制面候選，而不是 workaround。

`prepare`、`dexoptNextPackage`、`cleanup` 具有明顯的狀態變更風險；即使
`isDone`、`getProgress`、`nextDexoptCommand` 名義上偏 read-like，呼叫它們仍
需要未知的 private Binder transaction，且 implementation authorization 未知。
因此全部列為「因風險拒絕測試」。

## 下一個安全分析目標

只在 host 端從 exact PS7331 `services.jar`／VDEX 或權威、匹配的 Android 9
source tree 追查 authorization branch。具體 implementation 與 publisher 已
閉合；剩餘問題是 runtime caller policy，不需要也不允許透過 private
transaction 逼出答案。

## 可重現命令

```sh
python3 -m py_compile tools/scripts/audit_phase6ae_otadexopt_contract.py

python3 tools/scripts/audit_phase6ae_otadexopt_contract.py --dry-run \
  --disassembly decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log \
  --service-list adb/phase6t/PHASE6T-IPC-RO-20260805-01/service_list.stdout.txt \
  --metadata adb/phase6t/PHASE6T-DEBUG-SURFACE-20260805-02/metadata.json \
  --output artifacts/phase6ae/otadexopt-contract-20260805-01

python3 tools/scripts/audit_phase6ae_otadexopt_contract.py \
  --disassembly decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log \
  --service-list adb/phase6t/PHASE6T-IPC-RO-20260805-01/service_list.stdout.txt \
  --metadata adb/phase6t/PHASE6T-DEBUG-SURFACE-20260805-02/metadata.json \
  --output artifacts/phase6ae/otadexopt-contract-20260805-01

(cd artifacts/phase6ae/otadexopt-contract-20260805-01 \
  && sha256sum -c sha256sums.txt)
```

## 結論信心分級

| 結論 | 分級 |
|---|---|
| saved PS7331 service list contains `otadexopt` | 已證實 |
| six-method interface and transaction mapping | 已證實 |
| Stub has no visible local permission check | 已證實（僅限 Stub） |
| concrete implementation has no authorization | 待驗證；VDEX 只支持「未觀察到 method-local marker」，不可推論可繞過 |
| service changes HOME or enables Root | 已排除目前證據支持 |
| private transaction is safe to invoke | 因風險拒絕測試 |
