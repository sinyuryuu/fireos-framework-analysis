# Phase 15 — Amazon private-service authorization and sink closure

Date: 2026-08-10
Device context: KFTRWI / trona / Android 9/API 28 / PS7331.4463N
Serial referenced by prior runtime evidence: G001LT0511550CFT
Scope: host-only static closure plus previously archived bounded runtime evidence.

## Executive result

已證實：an ordinary APK can obtain handles for several Amazon private services
under the FireOS app_api_service route. The earlier bounded tx1 test also
demonstrated a real process/resource effect: a no-permission APK requested
preWarmApplicationForUser and a temporary target process appeared. This is a
confused-deputy finding, not root and not a HOME replacement.

已證實：the exact PS7331 VDEX is mapped through the generated Proxy and Stub,
transaction 1, fosinit service declaration, and system-server callback
ServiceManager acquisition.

高可信推論：the prewarm anomaly is confined to a process-prewarm sink. The
reviewed method reaches getApplicationInfo and startProcessLocked("prewarm");
it contains no setHomeActivity, preferred-activity, package-enabled,
component-enabled, or Fire Launcher mutation sink.

已證實：the KFT path is the strongest Fire-specific package-state writer in
this corpus. It enables Tahoe and disables Fire Launcher/Launcher3 for a
supplied child/profile UserInfo.id. The evidence does not close an ordinary
caller or shell to accepted User 0 input.

未找到：a new low-privilege path that changes formal HOME, disables User 0 Fire
Launcher, writes persistent preferred HOME, or reaches an OTA/partition sink.
Phase 15 sent no Binder transaction and changed no device state.

## 1. Exact prewarm call chain

The exact PS7331 method begins at
decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:3642543:

    checkCallingPermission("com.amazon.permission.APP_PREWARM")
    Binder.clearCallingIdentity()
    package/user branches
    IPackageManager.getApplicationInfo(package, 1024, userId)
    PreWarmCacheHelper.getKeepIfLargeValue(package)
    ActivityManagerService.startProcessLocked(..., "prewarm", ...)
    Binder.restoreCallingIdentity()

The saved instruction stream has no visible move-result, comparison, denial
return, or SecurityException between the permission call and identity clear.
That is a Strong evidence authorization-review candidate, not evidence of
arbitrary code execution or root.

The Proxy at disassembly.log:4464650-4464710 serializes a String and two ints
and invokes Binder transact(1). The Stub at disassembly.log:4465050-4465105
enforces the interface token, reads the same values, dispatches to the server
method, and writes an integer result.

## 2. Publication and caller boundary

amazonactivitymanager_fosinit.xml:8-28 declares AmazonActivityManagerService
and the cached activity vendor manager. The exact system-server callback
initializes its interface with ServiceManager.getService("amazonactivitymanager")
at disassembly.log:3783142-3783161.

Saved runtime evidence separates two caller classes:

- shell UID 2000 is denied service-manager find under SELinux Enforcing;
- an ordinary APK previously obtained non-null handles to private services, so
  method-level authorization must be reviewed separately.

The preserved direct caller for prewarm is Amazon Alexa's
ExplicitIntentAction.java:268-282, and the package declares APP_PREWARM. This
supports the intended privileged-caller interpretation but does not erase the
confirmed tx1 behavior observed in the earlier bounded test.

## 3. Sink inventory beyond Launcher

| Surface | Evidence result | Meaning |
|---|---|---|
| ActivityManager prewarm | getApplicationInfo then startProcessLocked | Confirmed process/resource deputy; no formal HOME/package sink |
| Amazon Package Manager | flags/metadata/proxy-related methods | Capability exists; no closed ordinary-app enabled-state/HOME edge |
| Amazon User Manager/KFT | Tahoe/Fire/Launcher3 state changes | Confirmed child/profile writer; User 0 relay not closed |
| Profile service | profile interaction and cross-user gates | No persistent HOME writer in reviewed path |
| Input/keyevent | implicit MAIN + HOME path and input policy | No explicit Fire component or preferred mutation observed |
| Migration service | Fire Launcher refresh notification | Side effect, not package/HOME setter |
| OOBE/OTA | lifecycle/setup and update capability | Not a generic low-privilege control surface; replay rejected |

The normalized rows are in output/tables/phase15-private-service-boundary.csv.
Worker source rows remain under work/ and are included in the Phase 15 hash
manifest.

## 4. HOME and Fire Launcher conclusion

The prior User 0 baseline remains:

    priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
    com.amazon.firelauncher/.Launcher

Nothing in the prewarm chain writes that resolver state. The KFT writer is
scoped to a supplied child/profile UserInfo.id, and the ordinary-app handle
test left User 0 HOME and Fire package state unchanged after rollback.

Therefore:

- 已證實: process-prewarm confused deputy;
- 已證實: child/profile KFT state writer exists;
- 已排除（目前保存範圍）: prewarm as a Fire Launcher replacement or root path;
- 待驗證: remaining private methods whose caller/sink joins are incomplete;
- 因風險拒絕測試: guessed Binder parcels, forged UserInfo, private-service
  mutation, OOBE/OTA replay, Fire Launcher mutation, root, and partition work.

## 5. Next safe work

1. Recover missing fosinit/service-context declarations for user/profile/migration.
2. Map callers of package-state writers and prove user/caller validation.
3. Inspect AmazonPackageManager metadata/flag consumers for a real policy
   decision, without treating metadata capability as a package-state writer.
4. If no new caller-to-sink edge appears, formally close the result as:
   formal HOME replacement unavailable without protected/system capability;
   one confirmed process/resource deputy remains, with no root claim.

No additional device mutation is justified by the current evidence.

## Reproduction and QA

    python3 tools/scripts/build_phase15_static_closure.py --dry-run
    python3 tools/scripts/build_phase15_static_closure.py --force
    python3 -m py_compile tools/scripts/build_phase15_static_closure.py

Generated input/output hashes are in
firmware/manifests/PHASE15-HOST-ANALYSIS-20260810/sha256sums.txt.
Raw device captures and prior test APK artifacts are not rewritten by this phase.
