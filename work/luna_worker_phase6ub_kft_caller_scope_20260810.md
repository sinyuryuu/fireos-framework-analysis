# Phase 6UB：AmazonUserManager/KFT child writer caller provenance

日期：2026-08-10（Asia/Taipei）。本報告只做 host-only exact-build static correlation；未呼叫 Binder transaction、未建立/切換 user、未做 setter replay、未 reboot。

## 結論

`enableKftLauncherComponent(UserInfo)` 的 production writer 位於
`AmazonUserManagerService$BinderService`，其唯一保存的外部 Binder caller 是
`AmazonUserManagerImpl.createChildUser(String)`：建立 child user（`createUser(name,
0x8000)`）後，將同一個 `UserInfo` 傳給 `IAmazonUserManager.enableKftLauncher`。
generated proxy/stub table 對應 **transaction code 3**。

另有一條非-Binder、system-server 內部 lifecycle caller：
`AmazonUserManagerService.onBootPhase(500)` 在 `AmazonPackageManager.isUpgrade()` 且
`AmazonUserManagerHelper.isChildUser(UserInfo)` 為真時，直接呼叫本地
`BinderService.enableKftLauncher(UserInfo)`。這不是 tx3，也不是 User-0 restore path。

writer 的 user scope 是完全由傳入 `UserInfo.id` 導入：

* `com.amazon.tahoe/.launcher.FreeTimeLauncherActivity`：enabled，flags 1；
* `com.amazon.firelauncher`：application state 2（disabled），flags 0；
* `com.android.launcher3`：application state 2（disabled），flags 0。

因此這是 child/profile-scoped KFT package/component writer。現有 bounded tx3
method body 沒有 `getCallingUid`、permission check 或 `clearCallingIdentity`；雖然
service 另有 `checkManageUsersPermission`（UID 0/1000 或 `MANAGE_USERS`），但沒有
證據證明該 helper 套用到 `enableKftLauncher`。caller permission/UID 與 tx3 的
完整 cross-user/admin authorization 保持 **UNKNOWN**，不可升格成「無 gate」或
「任意 caller 可達」。

## Evidence map

| edge | exact evidence | finding |
|---|---|---|
| child production caller | `boot-fosframework/disassembly.log:370295-370301, 369203-369243` | `createChildUser` creates with `0x8000`, obtains `mService`, calls `enableKftLauncher(UserInfo)`; same object then goes to setup completion |
| proxy contract | `boot-fosframework/disassembly.log:370378-370428`（Phase 6AK proxy table） | nullable `UserInfo` parcel; `IBinder.transact(3,...)`; boolean reply |
| stub dispatch | `boot-fosframework/disassembly.log:371789-371861` | interface token enforced, nullable `UserInfo` unmarshaled, dispatch to `enableKftLauncher`; **tx=3** |
| internal upgrade caller | `fosservices/disassembly.log:55057-55105` / codeOff `0x043942` | boot phase 500; `isUpgrade`; iterate `UserManager.getUsers`; `isChildUser`; direct local call to `mBinderService.enableKftLauncher(UserInfo)` |
| service entry | `fosservices/disassembly.log:54415-54440` | package-manager availability and MM-device branch; then `tryEnableKftLauncherComponent(UserInfo)`; no bounded caller UID/permission check |
| writer | `fosservices/disassembly.log:54297-54325` / codeOff `0x0431e2` | all three setters use `UserInfo.id`; no hard-coded user 0 |
| separate helper | `fosservices/disassembly.log:54847-54895` | `checkManageUsersPermission(String)` allows UID 0/1000 or `android.permission.MANAGE_USERS`; invocation from tx3 not proven |
| publication/access boundary | `fosservices/disassembly.log:55106-55118`; Phase 6AK `launcher-user-service.csv` row 6AK-UM-001 | published as `amazonusermanagerservice`; saved shell find was denied; no transaction sent |

## Caller / gate / user-scope disposition

| path | production caller | tx code | permission/helper | UserInfo.id source | cross-user/admin gate | disposition |
|---|---|---:|---|---|---|---|
| child provisioning | `AmazonUserManagerImpl.createChildUser(String)` | 3 | tx3 local permission/UID check: **UNKNOWN**; separate `checkManageUsersPermission`: present but not joined | `createUser(name, 0x8000)` return object, then parcelled `UserInfo` | child creation flag and child lifecycle are confirmed; exact caller authorization: **UNKNOWN** | CONFIRMED caller→tx3→child writer |
| upgrade lifecycle | `AmazonUserManagerService.onBootPhase(500)` | N/A (direct local call) | system-server lifecycle; no Binder caller; exact admin permission gate: **UNKNOWN** | each `UserManager.getUsers()` entry, passed if `isChildUser` | `isUpgrade && isChildUser` confirmed; exact user-id/cross-user enforcement: **UNKNOWN** | CONFIRMED internal child/profile caller |
| writer body | `BinderService.enableKftLauncher` → `enableKftLauncherComponent` | inherited from caller | no bounded local UID/permission/identity check | `UserInfo.id` at each setter | no hard-coded User 0; child/profile attribution is static | CONFIRMED child/profile writer |

## User-0 separation

No KFT writer call in the exact disassembly uses constant user 0 or a formal
`setHomeActivity`/`replacePreferredActivity`/preferred-HOME sink. The three package-state
calls are parameterized by the supplied `UserInfo.id`; the child caller supplies a newly
created child object and the upgrade caller filters with `isChildUser`. Phase 6TY's
User-0 restoration row remains `UNKNOWN`: a resolver result or generic PMS HOME API is
not caller provenance for a Fire restoration writer.

The saved KFT/child artifacts and Phase 6TY rows therefore support:

`createChildUser / upgrade-child lifecycle -> (tx3 or local call) -> UserInfo.id -> Tahoe enabled + Fire/Launcher3 disabled`

but do not support:

`production caller -> authorized cross-user/admin gate -> User 0 -> Fire HOME restoration`.

Missing caller, permission, inherited authorization, or runtime-loaded private-client
evidence is retained as **UNKNOWN**.
