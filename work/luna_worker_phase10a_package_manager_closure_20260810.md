# Phase 10A — AmazonPackageManager / package-state caller closure

日期：2026-08-10。範圍限 host-only 檔案搜尋與既有結果整理；本輪未執行 adb、service call、Binder transaction、APK 安裝、package/settings mutation、driver open/ioctl、root 或 exploit。輸出 CSV：`work/luna_worker_phase10a_package_manager_closure_20260810.csv`。

## 結論

目前沒有證據把普通 app 或 shell 連成「可影響 User 0 package/HOME」的 AmazonPackageManager 鏈。最接近的兩類 static sink 都不能直接當漏洞：

- `setAmazonFlagsForUser` / `setAmazonMetadataForUser` 有明確 `amazon.permission.ADD_RM_PKG_METADATA`（既有 permission 證據為 `signature|amazon`）gate；bounded corpus 沒找到 production APK/native caller、package/UID join、service-manager/SELinux client tuple 或 User-0 effect。下游是 Amazon flags/metadata file state，不是 HOME resolver。
- KFT `enableKftLauncherComponent(UserInfo)` 確實呼叫 AmazonPackageManager 的 component/application setters，且含 `com.amazon.firelauncher` 與 `com.android.launcher3`；但輸入是 supplied `UserInfo.id`，由 KFT child/profile lifecycle gate 控制，沒有 User-0 常數。Phase 9 也只閉合到 framework `AmazonUserManagerImpl.createChildUser` semantic caller，沒有閉合到實際 APK package/UID。

## Caller → gate → identity → scope → sink → effect

| entry | caller / UID | gate | identity | scope | effect / disposition |
|---|---|---|---|---|---|
| `setAmazonFlagsForUser` | production caller UNKNOWN | `ADD_RM_PKG_METADATA` | no clear/restore in slice | caller-supplied userId | file-backed Amazon flags; no HOME edge |
| `setAmazonMetadataForUser` | production caller UNKNOWN | same signature|amazon permission | no clear/restore in slice | caller-supplied userId | file-backed metadata; no HOME edge |
| KFT component setter | `AmazonUserManagerService.BinderService`; external APK caller UNKNOWN | KFT/TV/existence + private service visibility | pre-PMS identity not normalized in helper | child `UserInfo.id` | enables Tahoe FreeTime component |
| KFT application setters | same | same + downstream PMS/protected-package gates | same | child `UserInfo.id` | disables Fire/Launcher3 for KFT child; not general User-0 HOME control |
| Product Policy setters | local trusted service; trigger package/UID UNKNOWN | policy-file/user-list | local/system context; no external Binder identity established | explicit policy user list | policy-selected package/component only; fixed Fire/HOME target not found |
| `replacePreferredActivity` / `addPreferredActivity` | Settings picker or framework wrapper; exact runtime caller unresolved | PMS cross-user + `SET_PREFERRED_APPLICATIONS` | PMS uses `Binder.getCallingUid` | explicit userId | preferred record only; Fire priority-50 candidate remained selected in saved unlocked evidence |
| shell enabled-setting route | shell UID 2000 | standard PMS + protected-package gate | shell UID 2000 | `--user`, existing test User 0 | saved Fire disable attempts rejected with SecurityException; state unchanged |

## Ordinary app / shell priority answer

The bounded evidence supports `NO_REACHABLE_ORDINARY_APP_USER0_HOME_CHAIN_FOUND`. A private service declaration or exported/generated AIDL contract is not sufficient: the metadata writers require a signature-level Amazon permission, the shell service lookup was denied in saved service-manager/SELinux evidence, and the standard shell PMS route hit the protected-package gate. The Phase 6IP ordinary-app probe is test-only and does not establish a production caller or a successful package writer.

The HOME path is separate. Settings retains a `DefaultHomePicker` call to `replacePreferredActivity`, but PMS requires cross-user authorization and `SET_PREFERRED_APPLICATIONS`; saved unlocked resolution still selected `com.amazon.firelauncher/.Launcher` at priority 50. This is resolver/PMS behavior, not proof that AmazonPackageManager exposes a reachable HOME bypass.

## Important non-joins retained as UNKNOWN

1. Exact production APK/native caller package, UID, signing certificate, and service-manager/SELinux allow tuple for metadata mutators.
2. Exact external APK callsite for `AmazonUserManagerImpl.createChildUser` → KFT tx3; `com.amazon.frameworksettings` and `com.amazon.h2settingsfortablet` remain candidates only.
3. Complete PMS protected-package gate and User-0 acceptance for the KFT application setters.
4. Exact runtime external caller and exported reachability for the retained Settings `DefaultHomePicker`.
5. Native/reflection/runtime-loaded callers outside the bounded JADX/smali/VDEX corpus.

All such fields are `UNKNOWN` or equivalent bounded status in the CSV; no inference was substituted.

## Evidence hashes

The CSV preserves per-row evidence paths and SHA-256 values. Primary hashes include: `fosservices/disassembly.log` `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`; `boot-fosframework/disassembly.log` `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`; PMS JADX `f0efc633c75524540dd8a5703e5db528bb81ed80c9c49ad34e5cdf4d2078b074`; Phase 6MH ledger `39ce24194ecead7109894d6bae3cfcf631118c9181ec446dc70a6dd3354f231a`; Phase 6MU consumer closure `0b86f79ce8ae336ed5de9f50ecf80d2bce2f01e3c11c121299aea2a46e111ebb`; Phase 9 control-surface index `6bd54597763b4dc880cb0fa7539a29a78b840a610eab1a9ea7ae414181f9d17b`.
