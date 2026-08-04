# Phase 6D：`/init` policy branch extended window

## 新增靜態證據

對保存的 PS7331 `/init` 以 host `objdump` 擴大 `0x41ad00–0x41d5c0` 視窗，沒有
執行 ELF，也沒有接觸裝置。

- **已證實：** rootable path-builder candidate 在 `0x41ae44` 將 `w5=1` 設定後，
  在 `0x41ae5c` 傳給
  `0x41be00`。
- **已證實：** standard path-builder candidate 在 `0x41af78` 將 `w5=0` 傳給同一
  helper candidate。
- **已證實：** `0x41be48` 有 `tbnz w5,#0,0x41c30c`，因此兩個 call-site 並非
  只使用不同的無效參數；helper 內存在 instruction-level control-flow split。
- **高可信推論：** `w5` 是一個會改變 policy-loader helper 執行區段的模式／
  路徑旗標。
- **待驗證：** `w5=1` 是否等同 rootable policy、`0x41c30c` 是否載入 alternate
  policy、以及 stock boot 是否曾到達該分支。這些不能由 stripped code 的單一
  branch 命名推導。

## 與四情節的關係

這項證據進一步削弱 S4「純字串死碼」解釋，並提高 S2/S3 的價值；但它沒有
證明任何 userspace 可控 root switch，也沒有證明 AVB／signature check 與這個
branch 有資料或控制依賴。

Canonical artifact：
`artifacts/phase6d/phase6d-init-branch-window-20260804-02/`。

## 安全界線

不執行 boot-property injection、alternate policy selection、AVB bypass、
remount、bootloader／fastboot、image write、kernel race/panic、kernel memory
operation 或 root payload。
