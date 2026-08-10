# Phase 6SE broad privilege-surface evidence catalog

日期：2026-08-10（Asia/Taipei）

範圍僅限既有 repo 的 `findings/`、`output/`、`adb/`、`artifacts/`、`work/`。未執行裝置命令、未接觸 device node、未發送 Binder/broadcast、未執行 OTA/recovery/updater、未修改裝置、未做 exploit。這是一份供主 Agent 審核的候選清單，不是新的漏洞結論。

## 方法與總結

- 以既有 Phase 6K–6SA 報告、CSV、manifest 與相關 artifact 交叉比對：`registration → caller → gate → identity/user → sink → reachability`。
- 對 scoped CSV 使用 Ruby 標準 `CSV` parser 做語法/欄位數檢查；未發現無法解析或資料列欄位數不一致的 raw CSV。因此「raw CSV malformed」本身列為 **Disproved**，但語義欄位不足、hash/source 不完整仍列為候選缺口。
- `Confirmed` 只保留給 exact sink/gate/artifact 本身已被直接保存的事實；caller reachability、retail branch、User-0 scope 或完整 dataflow 未閉合時降級為 `Strong evidence`、`Probable`、`Hypothesis` 或 `Unknown`。

共 12 個候選項目：Confirmed 0、Strong evidence 1、Probable 1、Hypothesis 2、Disproved 3、Unknown 5。逐列 evidence path 與 SHA-256 見同名 CSV。

## 主要審核注意事項

1. 6SA 的 official artifact 身分與 updater sink 可以 Confirmed，但 outer archive 未達 verified EOF，不應把 archive completeness 一併標成 Confirmed。
2. 6SA staging/native path rows 的 sink 或 marker 是 static evidence；缺少 canonicalization、indirect CFG、return-value 與 caller closure 時，不應升級成 vulnerability 或 low-privilege route。
3. OOBE receiver 的 component/settings sink 靜態存在，但 exact numeric user 與 ordinary sender route 未閉合；「receiver-local permission omission」不等於可達。
4. Driver source `no capable()`、factory `0666` stanza、SELinux allow 或 appdomain allow 只證明 policy/source capability，不能單獨證明 retail ordinary-app reachability。
5. Amazon PM metadata/flags 與 KFT rows 仍有 production caller/holder/user-scope 缺口；KFT 已閉合的是 child/profile writer，不是 broad User-0 HOME writer。

所有後續動作均應維持 host-only；不得以本 catalog 作為執行 private transaction、driver ioctl、OTA 或 crafted input 的授權。
