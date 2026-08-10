# Phase 16 — broad capability-to-sink reconciliation

Date: 2026-08-10
Device context: Amazon Fire HD 10 (KFTRWI / trona), Fire OS 7.3.3.1 / PS7331, Android 9/API 28.
Scope: host-only integration of four disjoint static/test-reconciliation inventories plus previously archived runtime evidence.

## Executive result

**已證實：**本階段沒有新增裝置操作，也沒有找到一條由普通 app 或 shell 到
User 0 Fire Launcher package/component state、正式 HOME、OTA partition、UID 0
的完整 caller→gate→sink 鏈。worker 證據總共整理 79 筆：
kernel/driver 12、Amazon IPC
19、OTA/post-install
18、Phase 1–15 reconciliation
30。

**已證實：**既有 Phase 6ER/15 runtime 已觀察到 ordinary no-permission APK
透過已保存的 prewarm 路徑造成暫時 process/resource effect；這是 process
confused-deputy finding，不是 root、HOME replacement 或 package-state writer。

**已證實：**KFT 的 package-state writer 可對 supplied `UserInfo.id` 的
child/profile lifecycle 啟用 Tahoe、停用 Fire Launcher/Launcher3；目前保存
證據沒有把普通 caller 或 shell 閉合到 User 0 的該 writer。

**高可信推論：**若目標是「取得任意足以停用官方 Launcher 的權限」，目前最接近
的研究面仍是受保護的 system-service caller/identity boundary，而不是再做
priority、`set-home-activity`、猜測 Binder parcel、driver ioctl 或 OTA replay。
本輪沒有證據足以把任何一個候選升級成可利用權限提升。

## 1. Capability versus accepted caller

Evidence discipline: the normalized table preserves each worker row's raw
evidence citation. The Phase 16 manifest hashes the worker files and every
generated output. Legacy shorthand citations that are not standalone paths are
not silently resolved or promoted; they remain part of the row's missing-edge
review.

| Surface | Static capability / sink | Accepted low-privilege caller | Current verdict |
|---|---|---|---|
| Kernel / MTK drivers | CMDQ, ION, M4U, uinput, AUXADC, power/USB/debug surfaces | Exact native caller, node mode, merged SELinux allow and shipped object are not all joined | **待驗證**；不得由 symbol/config 推論可利用 |
| Amazon private IPC | User/KFT, profile, input, PMS-facing metadata, OOBE/OTA contracts | Service visibility and method-specific gates vary; no closed ordinary User-0 package/HOME caller | **已證實能力存在；低權限 sink 未閉合** |
| Prewarm | `preWarmApplicationForUser` → `startProcessLocked` | Prior bounded ordinary-app observation exists | **已證實 process/resource effect；不等於 root/HOME** |
| KFT child/profile | enabled-state calls using supplied `UserInfo.id` | Child/profile lifecycle scope is shown; ordinary User-0 relay is missing | **已證實 child-scoped writer；User 0 路徑未證實** |
| OTA/recovery | signed block/full OTA, updater write handlers, boot-chain targets | Recovery/update verification and system context required; ordinary caller not closed | **高權限能力；非低權限入口** |
| User-0 Fire package/HOME | PMS protected gate; ordinary disable/component tests | Existing shell tests were rejected before state mutation | **已排除既有 shell route** |

## 2. Amazon IPC and package-state sinks

The strongest static package-state sink is:

```text
AmazonUserManagerService.BinderService.enableKftLauncher(UserInfo)
  -> enableKftLauncherComponent(UserInfo)
  -> enabled-state setters for supplied UserInfo.id
  -> Tahoe enabled; Fire Launcher and Launcher3 disabled
```

Evidence rows `LUNA-B-002`–`LUNA-B-005` and the prior KFT closure support the
sink and its child/profile scope. The precise external caller authorization for
`enableKftLauncher` remains an **待驗證** edge; the method's existence is not
permission to invoke it, and no transaction was sent in Phase 16.

The bounded Amazon profile/input/OOBE/OTA review found no proven direct
`setHomeActivity`, `addPreferredActivity`, or `replacePreferredActivity` writer.
`BootAfterSystemOTAReceiver` remains a protected lifecycle sink, not a broadcast
that may be replayed by shell. Treat these as bounded negatives, not a claim that
every Amazon class has been exhaustively decompiled.

## 3. Kernel and driver surface

The PS7331 source and saved boot/image artifacts contain capability markers for
CMDQ/GCE, ION, M4U, uinput, AUXADC, perf/power, USB PHY/TCPC and Amazon
diagnostic surfaces. The worker correctly separates:

1. registration/Kconfig/DT capability;
2. final shipped object/DTB and node ownership;
3. caller UID/domain, merged SELinux allow and ioctl/proc/sysfs dataflow; and
4. observable security effect.

The saved corpus does not close all four layers for a low-privilege caller.
`CONFIG_AMZN_DRV_TEST` is not enabled in the cited trona configuration, so its
factory/engineering dispatcher is not a shipped runtime claim. No open/ioctl,
memory read/write, exploit, or root test was performed in this phase.

## 4. OTA and post-install surface

The PS7331 package is a signed full/block OTA. The script/native updater artifacts
show fixed high-privilege capabilities including system/vendor and boot-chain
targets, but the relevant caller is recovery/updater context behind package,
version, signature, AVB/rollback and boot-control gates. The missing edges listed
in `C-001`–`C-018` prevent a low-privilege conclusion.

`BootAfterSystemOTAReceiver` and OOBE helpers can participate in protected
post-upgrade lifecycle and settings/setup changes. No broadcast replay, updater
execution, sideload, recovery, reboot, partition write or malformed OTA test was
performed. Capability is not reachability.

## 5. Historical runtime reconciliation and no-repeat policy

The reconciliation confirms that priority APK matrices, ordinary
`set-home-activity`, Fire package/component disable, child/KFT variants, DPM,
Accessibility foreground redirect, guessed private Binder parcels, root/GhostLock
probes, and OTA/driver mutation paths already have negative, bounded, or
risk-rejected results. They are not repeated merely because a static sink exists.

The only new runtime candidate identified by the reconciliation is a **passive
observation of a naturally occurring Alexa prewarm event**, with no APK, no
Binder transaction, no guessed parcel, no child/user mutation and no state write.
It is a validation candidate, not an exploit path. If no natural event occurs,
the correct result is `未觀察到`, not synthetic injection.

## 6. Verdict classification

- **已證實:** process/resource prewarm deputy; KFT child/profile package-state
  writer; Amazon/OTA/kernel capabilities exist at their respective static layers;
  existing User-0 Fire disable/component routes are protected/rejected.
- **高可信推論:** a new privilege path, if one exists, must close a protected
  caller/identity/user-scope edge; broad capability inventory alone is insufficient.
- **待驗證:** exact external authorization and accepted `UserInfo` validation
  for KFT; final shipped driver node/policy/caller joins; OTA native indirect
  handoff; a naturally occurring prewarm observation.
- **已排除（bounded scope）:** prewarm as HOME/package/root writer; existing
  ordinary shell HOME/disable route; child-scoped KFT evidence as a User-0 relay;
  treating OTA/driver symbols as an ordinary-app exploit.
- **因風險拒絕測試:** guessed private Binder transactions, forged user records,
  Fire Launcher mutation, driver open/ioctl, Root/GhostLock attempts, OTA/recovery
  execution, sideload/flash, partition writes, malformed OTA and broadcast replay.

## 7. Safe next action

No new state-changing device action is justified by the current matrix. The next
minimal step, if a new live-session observation is explicitly desired, is a
read-only passive capture around a naturally occurring Alexa prewarm event while
checking HOME, Fire package/component state, current user, settings and SELinux
invariants. Do not manufacture the event through private Binder calls. Otherwise
continue host-only joins of exact shipped driver objects/DTB/policy and the KFT
caller authorization path.

## 8. Reproduction and generated outputs

```sh
python3 tools/scripts/build_phase16_control_surface.py --dry-run
python3 tools/scripts/build_phase16_control_surface.py --force
python3 -m py_compile tools/scripts/build_phase16_control_surface.py
```

The normalized matrix, evidence index, Mermaid/text graph and input/output hashes
are generated without touching the device. Worker source files are retained under
`work/` and are hashed by the Phase 16 manifest.
