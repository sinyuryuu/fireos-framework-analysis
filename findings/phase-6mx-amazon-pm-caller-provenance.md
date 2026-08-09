# Phase 6MX：IAmazonPackageManager service-handle / caller provenance

## Scope

本產出是 PS7331 保存 artifacts 的主機端靜態索引。掃描 `boot-fosframework`
與 `fosservices` disassembly，以及 `amazonpackagemanager_fosinit.xml` 的服務註冊資料。
沒有執行 ADB、Binder transaction、`service call`、未知介面呼叫、裝置節點操作或任何裝置狀態修改。

## 已證實

- 精確的 system-server 實作是 `com.amazon.android.service.pm.AmazonPackageManagerService`，其
  `getSystemServiceName()` 回傳 `amazonpackagemanager`，並在 `onStart()` 以
  `publishBinderService()` 發布 `AmazonPackageManagerService$BinderService`。
- 私有介面 `IAmazonPackageManager` 在保存 disassembly 中有 11 個方法：
  `deregisterProxyReceiver, getAmazonFlagsForUser, getConfigurationHelper, isFtvSpecApp, isPreInstalledAppWithFtvSpec, registerProxyReceiver, removeAmazonFlagsForUser, removeAmazonMetadataForUser, setAmazonFlagsForUser, setAmazonMetadataForUser, shouldAllowMicAccess`。
- 掃描到 2 個 `ServiceManager.getService` service-handle row、
  1 個 publication row、30 個介面相關呼叫 row（含 generated Stub dispatch）。
- 這個介面沒有 `setHomeActivity`、preferred-activity setter、component/application enabled-state
  setter、hide 或 suspend setter；因此本掃描沒有發現可由該介面直接改寫 User 0 HOME 的方法。

## 高可信推論

- `amazon/content/pm/AmazonPackageManagerImpl` 是 fosinit 宣告的 `PackageManager` vendor instance，
  其保存的 constructor 先取得 `amazonpackagemanager`，再取得標準 `package` Binder；其介面呼叫集中在
  Amazon flags、metadata、mic policy 與 package-data callback 等功能。這更符合 framework facade，
  不等於 shell 可直接取得可改 HOME 的代理。
- `FtvSpecAssertionUtility` 取得同一 service 後只呼叫 FtvSpec／configuration read methods。這是
  classification/configuration read path，不是 HOME selection writer。

## 待驗證

- 完整的 `AmazonPackageManagerImpl` 實例化者、reflection/generated caller 與 native caller 尚未由
  此 bounded disassembly sweep 完整閉合；它們不能靠本索引推論為不存在。
- Binder method 的 runtime caller UID／permission enforcement 仍以既有 Phase 6IA/6HP 證據為準；本階段
  不重播 transaction，也不猜測 transaction code。

## 已排除（本範圍）

- 將 `amazonpackagemanager` service 名稱本身視為可用的 HOME 控制入口：未發現對應 interface method。
- 將 service handle、proxy/stub 或 framework facade 的存在誤稱為已取得 system UID 或 root：本掃描沒有
  改變 caller identity，也沒有執行任何提權測試。

## 統計

- rows: 48
- categories: {'binder_contract': 11, 'binder_interface': 12, 'framework_facade': 9, 'framework_read_classifier': 14, 'system_server_publisher': 1, 'system_server_service': 1}
- kinds: {'interface_callsite': 30, 'interface_declaration': 1, 'interface_method_definition': 11, 'service_handle': 2, 'service_name_literal': 3, 'service_publication': 1}
- interface calls: {'deregisterProxyReceiver': 1, 'getAmazonFlagsForUser': 2, 'getConfigurationHelper': 11, 'isFtvSpecApp': 2, 'isPreInstalledAppWithFtvSpec': 2, 'registerProxyReceiver': 1, 'removeAmazonFlagsForUser': 2, 'removeAmazonMetadataForUser': 2, 'setAmazonFlagsForUser': 2, 'setAmazonMetadataForUser': 2, 'shouldAllowMicAccess': 3}
- device_mutation: false

## 證據位置

完整逐行索引見 `caller-calls.csv`；輸入雜湊見 `input-manifest.csv`。
