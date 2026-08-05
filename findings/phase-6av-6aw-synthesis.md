# Phase 6AV/6AW：最新研究結果與下一步判定

## 目前最好的新結果

### 已證實

- 最接近 Home-key 控制的 Amazon `registerKeyEventInterceptor()` 不是裸露的
  callback：它要求 Amazon `GET_KEYEVENTS`、calling UID 對應 package、package
  whitelist，並在必要時檢查前景 package。
- Amazon private service 的 service-manager SELinux `find` 邊界在 shell UID 2000
  上仍成立；沒有因 `service list` 的名稱出現而取得可用 Binder handle。
- KFT child-user 路徑確實包含 Fire Launcher disabled-state 寫入，但這是明確的
  高風險 lifecycle path，不能當成一般 User 0 workaround；本機未執行。
- 官方 PS7331 OTA 是完整高影響寫入契約，包含 system/vendor block image 及
  boot-chain／firmware targets；本機未執行。

### 高可信推論

目前可採用的無 Root結果仍只有「暫時 foreground redirect」類方案，而非正式
HOME replacement。正式 HOME 仍由 Fire Launcher 的 privileged candidate／標準
resolver 路徑主導；Amazon input/profile service 形成額外控制邊界，但本階段沒有
找到普通 shell 可使用的 HOME setter。

### 待驗證

- `setInputFilter()` 的 synthetic helper 完整授權 body。
- 所有 private Binder method 的完整 caller inventory。
- recovery native layer 的完整 path／signature control flow。

### 已排除

- private service 名稱本身可作為 shell bypass。
- profile `initiateLauncher()` 是正式 HOME 選擇器。
- 官方 OTA package 可視為低風險 ADB 實驗入口。

### 因風險拒絕測試

未知 Binder transaction、KFT launcher state mutation、OTA／recovery／OOBE replay、
任何 Fire Launcher 停用／隱藏／suspend／清除資料、partition write、root 或
bootloader 操作。

## 建議的最小後續工作

只做 host-only：補齊 `access$600` 的 DEX method mapping，並將其 caller／權限與
`registerKeyEventInterceptor` 做同版 source 對照。如果仍沒有 shell-visible
合法 caller，IPC 路線即可正式結案；不需要再猜 transaction code。
