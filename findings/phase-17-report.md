# Phase 17 — residual privilege-surface closure

Date: 2026-08-10 (Asia/Taipei)
Device corpus: Amazon Fire HD 10 (KFTRWI / trona), Fire OS 7.3.3.1 / PS7331, Android 9/API 28.
Scope: any path that could obtain enough authority to change package state, HOME, user policy, OTA/recovery state, kernel/driver state, or UID.

## Executive result

**已證實：**本階段沒有找到普通 APK 或 ADB shell 能取得 UID 0、system identity、User 0 Fire Launcher package-state writer、正式 HOME writer、OTA partition writer 或 driver memory primitive 的完整 caller-to-gate-to-sink 鏈。

**已證實：**KFT IAmazonUserManager transaction 3 的 implementation 會把 supplied UserInfo.id 傳到 Tahoe/Fire/Launcher3 state writers；既有 PHASE6FK 已以 ordinary APK UID 10213 實機送達 tx3，PMS 在 setComponentEnabledSetting() 前拒絕，Fire state 與 HOME 未變。PHASE6FJ 對 User 10 在跨使用者檢查拒絕。這兩次既有測試不重跑。

**高可信推論：**KFT tx3 是目前最接近「若取得受信任 system caller 就能改變 Fire state」的靜態控制面，但 Stub 缺少可見 caller check 本身不是漏洞證明；stock SELinux service-manager 邊界、下游 PMS caller gate 與 user-scope gate 尚未被繞過。

**已證實：**AmazonPackageManager facade 的 enabled-state setter 沒有清除 Binder identity；它委派標準 PackageManager/IPackageManager，不是把 ordinary caller 變成 system UID 的代理。

**已證實（bounded）：**driver、OTA/recovery、OOBE、Amazon flags、input/profile service 具備不同層級的能力或 sink，但現有 corpus 沒有把 ordinary caller 接到可持久提權、Fire state、HOME、partition 或 kernel memory sink。

## 1. Scope and no-repeat policy

本階段擴大到 launcher 以外的權限面：KFT/user management、Amazon IPC、PMS/DPM、driver/device node、OOBE/OTA/recovery、profile/input、Amazon package metadata 與既有 runtime deputy。沒有重跑 Phase 3A–16 已完成的 priority matrix、set-home persistence、Fire disable/component tests、child KFT tx3 probes、private Binder parcel probes、driver ioctl、GhostLock/root、OTA/recovery 或 partition 操作。

Worker raw input counts: kft: 10 raw / 10 unique / malformed=['KFT-10'], ipc: 12 raw / 12 unique / malformed=['P17-011', 'P17-012'], driver: 6 raw / 6 unique / malformed=none, ota: 10 raw / 10 unique / malformed=none。並行 worker 輸出的 CSV/Markdown 不一致或 malformed row 只作 QA 記錄；raw 檔案與 hash 保留，不被當作額外證據。

## 2. Caller to gate to identity/user scope to sink matrix

Derived rows: 40. Classification counts: Confirmed=4, Hypothesis=6, Probable=5, Strong evidence=25.

| Branch | Rows |
|---|---:|
| AOSP-shaped PMS gate | 1 |
| Amazon Framework / IPC | 10 |
| Amazon Framework / identity preservation | 1 |
| Amazon KFT / user-manager | 9 |
| Existing runtime boundary | 3 |
| MTK / Amazon driver surface | 6 |
| OTA / OOBE / recovery | 10 |

The machine-readable table is output/tables/phase17-residual-privilege-surface.csv. Static capability, accepted caller, and runtime effect remain separate.

## 3. KFT and PackageManager identity boundary

Static path:

AmazonUserManagerImpl.createChildUser(UserInfo)
  -> IAmazonUserManager.Proxy.transact(3)
  -> IAmazonUserManager.Stub.onTransact()
  -> BinderService.enableKftLauncher(UserInfo)
  -> tryEnableKftLauncherComponent(UserInfo)
  -> enable Tahoe FreeTimeLauncherActivity
  -> set Fire Launcher disabled for UserInfo.id
  -> set Launcher3 disabled for UserInfo.id
  -> clearCallingIdentity() only before later DPM/profile-owner work

The bounded Stub slice shows interface-descriptor enforcement and optional UserInfo unmarshalling. No getCallingUid, checkCallingPermission, or current-user equality check is visible in tx3. Classification: 待驗證 / high-impact static edge, not a vulnerability, because the accepted external caller set is not closed and the service-manager boundary blocks shell.

PHASE6FK records service=amazonusermanagerservice handle=true from an ordinary APK, then uid=10213 in PMS and SecurityException: Attempt to change component state at PackageManagerService.setEnabledSetting / setComponentEnabledSetting. Result=false, Tahoe was not enabled, Fire HOME remained priority 50, and the APK was removed.

PHASE6FJ records the analogous User 10 attempt failing with INTERACT_ACROSS_USERS for ordinary UID 10212. The supplied user ID is not an unrestricted cross-user relay in the observed stock path.

**結論：Confirmed boundary, not privilege escalation.** The static KFT writer is real, but no ordinary-app or shell route to a User 0 Fire mutation is proven.

## 4. AmazonPackageManager and other IPC surfaces

- AmazonPackageManagerImpl — Strong evidence: enabled-state methods delegate to standard PackageManager/IPackageManager and do not call clearCallingIdentity.
- AmazonApplicationFlags — Confirmed, bounded: mutators require amazon.permission.ADD_RM_PKG_METADATA (signature|amazon) and persist /data/system/amazon_package_flags.xml; bounded consumers cover recency, game-mode, and AppCompat, not HOME or Fire state.
- Profile/input services — Strong evidence / Probable: profile picker and input injection are protected or unresolved private surfaces; no direct preferred/HOME/package-state writer is proven.
- Prewarm — Confirmed limited deputy: an ordinary APK previously caused a temporary process/resource effect through a private service; no package, HOME, UID 0, or persistence effect occurred.

## 5. Driver, OTA, and OOBE surfaces

CMDQ, ION, M4U, uinput, AUXADC and Amazon diagnostic markers establish source/configuration capability, not a usable caller. Exact shipped object/module, selected DTB/DTBO, merged policy, native opener, UID/domain and input-to-effect path are not jointly closed. No device node, proc/sysfs/debugfs, ioctl, module load or memory operation was performed.

The OTA controller and deferred/check paths are signature|privileged protected. BootAfterSystemOTAReceiver and its OOBE helper can enable OobeHomeActivity and write setup settings in a trusted post-OTA lifecycle, but no ordinary broadcast replay or shell-to-recovery handoff is proven. The updater has write capability only in recovery/update context behind verification and boot-chain gates.

**分類：** Strong evidence for capability; low-privilege reachability remains Hypothesis/Unknown.

## 6. What is required to disable Fire Launcher

1. A caller accepted by PMS protected-package and user-scope checks, or a trusted internal lifecycle caller that invokes the setter after legitimate elevation.
2. A User 0-scoped package/component state write, not merely a preferred record or foreground redirect.
3. A path not blocked by shell SELinux service discovery, signature permissions, INTERACT_ACROSS_USERS, DevicePolicy/provisioning state, or recovery/AVB verification.

No current evidence demonstrates all three for a normal app, shell, settings key, AppOp, overlay, profile picker, OTA receiver, or driver node.

## 7. Classification summary

- 已證實: PMS rejects the existing ordinary User 0 KFT tx3 route before mutation; cross-user tx3 is rejected; KFT child-scoped writer exists; Amazon facade preserves caller identity; Amazon flags are signature-gated; ordinary prewarm caused only process/resource effect.
- 高可信推論: KFT tx3 authorization and trusted-service caller inventory are the highest-value remaining host-side questions; a successful route would require a materially different trusted caller or changed build/policy boundary.
- 待驗證: complete KFT external caller set; exact Amazon profile/input accepted caller; final driver object/DTB/policy/native joins; OTA native handoff; natural prewarm observation.
- 已排除（bounded scope）: ordinary shell/component disable; ordinary User 0 KFT tx3; User 10 cross-user tx3; preferred record as sufficient HOME replacement; prewarm as package/HOME/root sink; treating source/Kconfig/OTA strings as caller reachability.
- 因風險拒絕測試: guessed Binder transaction/parcel, forged UserInfo, Fire Launcher mutation, driver open/ioctl, Root/GhostLock trigger, OTA/recovery execution, sideload/flash, partition writes, SELinux/service-manager changes and broadcast replay.

## 8. Recommended next research value

Only host-only joins remain justified: (a) complete the exact-build trusted caller/reference graph for KFT tx3 and profile/input services; (b) join shipped native ELF, DTB/DTBO, merged policy and node ownership for driver surfaces; and (c) if a natural system prewarm event occurs, passively capture it without manufacturing a private Binder call. A new live mutation is not justified by the present evidence. If the caller/gate/user/sink join remains open, formally close the broad privilege-surface investigation as no ordinary-app/shell privilege path demonstrated.

## 9. Reproduction

python3 tools/scripts/build_phase17_residual_closure.py --dry-run
python3 tools/scripts/build_phase17_residual_closure.py --force
python3 -m py_compile tools/scripts/build_phase17_residual_closure.py
sha256sum -c firmware/manifests/PHASE17-HOST-ANALYSIS-20260810/sha256sums.txt

All commands above are host-only. No rollback is required because this phase performed no device mutation.

## 10. Outputs

- findings/phase-17-evidence-index.md
- output/tables/phase17-residual-privilege-surface.csv
- output/call-graphs/phase17-kft-pms-identity-flow.mmd and .md
- firmware/manifests/PHASE17-HOST-ANALYSIS-20260810/sha256sums.txt
- tools/scripts/build_phase17_residual_closure.py
