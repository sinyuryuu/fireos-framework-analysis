# Phase 6TF — Amazon Framework/System Services IPC host-only residual search

日期：2026-08-10（Asia/Taipei）

## Scope and safety

本輪只讀取既有 JADX source、既有 Phase 6TA–TD/6RG/6SU/6QE/6QF reports，沒有接觸設備，沒有呼叫 Binder、`service call`、broadcast、driver、ioctl、OTA/recovery、root 或 exploit。已關閉的 Amazon PM proxy、DCPMS CDE、KFT/PMS/HOME writer、既有 native surfaces 不重列。

## Result

找到一組未在上述 residual ledgers 中整合的 exact-build Amazon Alta/H2ClientService chain。`H2ClientService.onBind()` 回傳 `IH2ClientService.Stub`，其 mutating API 可進入 household/user workflow；可見 sink 包含 Amazon user creation/removal、跨 profile Settings relay，以及 Amazon user sort-order state。這些是 production code path 的靜態正證據，但外部 accepted caller、manifest/service declaration、`BIND_SERVICE` holder/grant 與低權限可達性仍未由 bounded corpus 閉合，因此不把它判定為 ordinary app/shell route。

| row | chain | result | production caller | residual meaning |
|---|---|---|---|---|
| 6TF-01 | `IH2ClientService.addUser` → `AddUserAPICall` → `HouseholdController.createUser` → `CreateAndroidUserCommand` → Amazon user manager | POSITIVE | Yes; external sender UNKNOWN | User creation sink exact; bind authorization and caller provenance unresolved. |
| 6TF-02 | `IH2ClientService.removeUserFromDevice` → `RemoveUserFromDeviceAPICall` → `HouseholdController.removeUserFromDevice` → `RemoveAndroidUserCommand` | POSITIVE | Yes; external sender UNKNOWN | User 0 rejection and removal sink exact; bind authorization unresolved. |
| 6TF-03 | production persistence → `ConfigHelper` → `MultipleProfileHelper.putStringForProfile` | POSITIVE | Yes | Per-profile Settings relay exact; upstream Binder caller gate unresolved. |
| 6TF-04 | `SortOrderManager` → `AndroidUserHelper.setSortedAndroidIds` → Amazon user manager | POSITIVE | Yes | Profile ordering state exact; no HOME/package sink found. |

`POSITIVE` means the production caller→internal validation→sink edge is statically joined. It does not mean ordinary-app reachability or a vulnerability. External Binder caller/permission-holder reachability is `UNKNOWN` for all rows.

## Exact evidence

- `artifacts/phase6mc-alta-jadx-20260810-01/sources/com/amazon/alta/h2clientservice/H2ClientService.java:104-126` publishes the Binder Stub and routes `addUser`; `:226-236` routes `removeUserFromDevice`; `:270-276` initializes production controllers.
- `.../apicall/AddUserAPICall.java:10-14,29-33` calls `HouseholdController.createUser`; device-removal routing is in `H2ClientService.java:227-236`.
- `.../controllers/HouseholdController.java:323-373` contains `createUser`; `:635-652` removes a device user; `:593-605` removes an Android account.
- `.../workflow/commands/CreateAndroidUserCommand.java:20-37` reaches Android user creation; `.../helpers/AndroidUserHelper.java:148-176` shows nonzero-user removal and sorted-user writes.
- `.../controllers/PersistenceController.java:36-43,74-99` calls per-user role/state/KFT/experience setters. `.../helpers/ConfigHelper.java:94-124` maps them to Global/Secure or `MultipleProfileHelper.putStringForProfile` writes.
- `.../controllers/SortOrderManager.java:19-24,49-70` derives ordered Android IDs and calls the helper sink.
- `.../Manifest.java:6-9` declares symbolic `com.amazon.alta.h2clientservice.permission.BIND_SERVICE`, but no matching manifest XML/service declaration or holder/grant is present in this bounded source package; effective bind gate remains UNKNOWN.

No H2 edge to formal preferred HOME, `setComponentEnabledSetting`, `setApplicationEnabledSetting`, or Fire Launcher selection was found. Next safe verification is host-only recovery of the exact-build H2 manifest/service declaration and enumeration of non-generated `IH2ClientService` clients. Do not obtain a service handle, construct a parcel, bind/call the service, or mutate user/settings/package state.

