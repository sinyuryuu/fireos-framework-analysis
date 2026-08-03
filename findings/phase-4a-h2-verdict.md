# Phase 4A H2 verdict

## 判定：高可信推論（核心 chooser）；待驗證（Amazon callback/filter return）

在已比對的 `PackageManagerService` chooser、preferred lookup 與 priority
normalization 內，Fire OS 與 AOSP Android 9 的可見控制流等價；沒有找到
`com.amazon.firelauncher` 硬編碼，也沒有看到 callback 回傳 Fire component。
這支持「主結果可由 AOSP-shaped resolver 加上 privileged Fire priority 50
解釋」的 H2 核心部分。

H2 不能被標成完整已證實，因 Fire OS 新增了兩個尚未以回傳值封閉的控制面：

* `VendorActivityStackSupervisorCallback.callResolveIntent()` 可在 PM 前
  回傳非 null 結果；現有證據沒有證明它在本 HOME 請求中如此做。
* `VendorPackageManagerCallback.callFilterComponentIntent()` 可在 resolver
  建索引時排除 filter；現有證據沒有證明它排除了哪個 HOME filter。

因此「沒有任何 Amazon 核心介入」是已排除過強的表述；「核心 chooser 的
Fire 勝出不需要 package-name 特判即可重現」則是高可信推論。

Evidence: `P4A-METHOD-001`–`P4A-METHOD-008`, `P3C-CALLBACK-001`,
`P3C-PREF-001`.
