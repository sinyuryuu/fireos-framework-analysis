# Phase 13 — KFT, exported components, policy/card and driver closure

## Executive result

Phase 13 broadened the analysis beyond the Launcher itself. It covered the
KFT `IAmazonUserManager` transaction 3 path, the Amazon package-manager
facade used by that path, exported Amazon components, parental/card policy
flows, and seven previously open driver surfaces. The work was host-only and
read-only. No Binder transaction was sent, no `UserInfo` parcel was forged, no
driver node or ioctl was opened, and no package, HOME, Fire Launcher, OTA,
recovery, partition, SELinux or system state was changed.

**Confirmed:** the saved code contains a real `IAmazonUserManager` tx3
Stub/Proxy pair. The Stub decodes a nullable `UserInfo` and dispatches to
`AmazonUserManagerService$BinderService.enableKftLauncher(UserInfo)`.

**Confirmed:** the only closed semantic caller in the preserved corpus is
`AmazonUserManagerImpl.createChildUser(String)`. It creates a child
user and passes the returned child `UserInfo` through tx3. This is not a
User-0 caller and is not a HOME setter.

**Strong evidence:** the KFT writer passes the supplied `UserInfo.id` to three
package/component state writers: enable Tahoe FreeTime Launcher, disable
`com.amazon.firelauncher`, and disable `com.android.launcher3`. The method has
no visible hard-coded nonzero user check in the bounded slice, but the actual
external tx3 caller, authorization, user scope and PMS downstream decision are
not closed.

**Strong evidence:** the KFT path's `AmazonPackageManagerImpl` delegates its
four-argument state calls to the standard `IPackageManager` Binder proxy. The
facade constructor obtains the standard `package` service after the private
`amazonpackagemanager` service. Because the KFT service implementation is in
the system-server service corpus and no `clearCallingIdentity()` precedes
these package calls, the static model is consistent with PMS seeing the
system-server caller for the internal call. This is a serious confused-deputy
candidate, not a proven external vulnerability: no external caller has been
joined, no tx3 authorization has been demonstrated, and no transaction was
sent.

**Unknown:** the exported components and all seven driver surfaces do not
close a new low-privilege route. Their missing caller, permission/SELinux,
user-scope, validation and sink edges remain in the machine-readable table.

## Baseline and safety

The Phase 12 serial-bound baseline remains the current device reference:
[`adb/phase12/PHASE12-BASELINE-20260810-01`](../adb/phase12/PHASE12-BASELINE-20260810-01).
Its post-host guard preserved the same PS7331 fingerprint, User 0 and formal
Fire HOME. Phase 13 performed no device operation, so there is no mutation
rollback to report.

| Item | Result | Status |
|---|---|---|
| Serial | `G001LT0511550CFT` | Confirmed from Phase 12 baseline |
| Fingerprint | `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys` | Confirmed from Phase 12 baseline |
| User 0 HOME | `com.amazon.firelauncher/.Launcher`, priority 50 | Confirmed from Phase 12 baseline |
| SELinux | Enforcing | Confirmed from Phase 12 baseline |
| Phase 13 mutation | None | Confirmed |

## 1. KFT tx3 call path

The bounded static path is:

```text
AmazonUserManagerImpl.createChildUser(String)
  -> createUser(name, 0x8000)
  -> IAmazonUserManager.Proxy.enableKftLauncher(UserInfo)
  -> Parcel(UserInfo) + transact(3)
  -> IAmazonUserManager.Stub.onTransact(3)
  -> BinderService.enableKftLauncher(UserInfo)
  -> tryEnableKftLauncherComponent(UserInfo)
  -> AmazonPackageManagerImpl
  -> IPackageManager Binder proxy
  -> PMS package/component state setters
```

Line/offset evidence:

- Proxy parcel and `transact(3)`: `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:370398-370443`.
- Stub descriptor enforcement, nullable parcel decode and tx3 dispatch:
  `.../boot-fosframework/disassembly.log:370674-370777`, tx3 at `370737-370745`.
- Service implementation: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54415-54478`.
- State writer: `.../fosservices/disassembly.log:54297-54325`.
- Closed child semantic caller: `.../boot-fosframework/disassembly.log:369180-369243`.

The method-local slice does not show `Binder.getCallingUid`, a permission
check, or an explicit cross-user check before `tryEnableKftLauncherComponent`.
That observation is **Strong evidence**, not proof of missing authorization:
superclass/inherited checks, service declaration permission, SELinux service
manager rules, and PMS's own checks remain open.

## 2. Package-manager identity handoff

`AmazonPackageManagerImpl.<init>(PackageManager, Context)` obtains
`amazonpackagemanager`, then obtains `ServiceManager.getService("package")`
and converts it to `IPackageManager`. The four-argument
`setApplicationEnabledSetting` and `setComponentEnabledSetting` methods call
that `mPM` proxy and pass the context op-package name. They do not call
`clearCallingIdentity()` in the bounded method body.

This closes the static *internal* handoff to standard PMS, but not an external
caller-to-tx3 path. The relevant distinction is:

| Question | Status |
|---|---|
| Does the facade use the standard package Binder? | Confirmed |
| Does KFT use the four-argument facade state methods? | Confirmed |
| Would an internal system-server call carry its process Binder identity to PMS? | Strong evidence from Binder call structure |
| Can shell or an ordinary app invoke tx3? | Not established; saved shell lookup route is denied, ordinary app only performed descriptor tests |
| Can an external caller supply `UserInfo.id == 0` and pass all gates? | Unknown |

## 3. What is and is not a Fire Launcher sink

The KFT writer does contain a Fire Launcher package-state target, but its
target is a supplied user and the writer is reached through a child-profile
lifecycle in the only closed caller chain. It does **not** call
`setHomeActivity`, `replacePreferredActivity`, or a formal HOME resolver API.
Therefore it cannot, from this evidence alone, explain User-0 HOME selection.

The exact protected-package gate observed in earlier phases remains relevant
when PMS receives a direct state mutation. A system-server internal caller may
be authorized for a child-user operation; that does not establish that an
ordinary caller can turn the same code into a User-0 Fire disable.

## 4. Exported component inventory

The inventory contains Fire Launcher activities/receivers/providers,
Parental Controls, Settings and SystemUI entries. Exported status or a named
permission is not treated as an exploit. The current bounded findings are:

- Fire Launcher `Launcher` is an exported HOME activity; no new state writer
  was recovered from that entry.
- `StartEditModeReceiver` is permission-gated and starts edit mode; its source
  does not close to PackageManager or HOME default mutation.
- Card provider/agent routes close to card database, blacklist and card-read
  state. They do not close to package enabled state or HOME selection.
- Parental restriction provider/service routes close to auth/dialog flow.
  Fixed policy-map entries can reach DPM hidden/restriction APIs, but the
  supplied provider package name is not connected to that map in the saved
  corpus.
- SystemUI keyguard and Settings entries have unresolved method-level gates;
  no new Fire Launcher writer was proven.

## 5. Driver and native surface join

CMDQ/MDP, ION, M4U, uinput, perfmgr, Amazon driver-test and RPMB remain
`Unknown`. Source handlers, Kconfig, init node metadata, file contexts or
library symbols are capabilities, not reachability. Each row is missing at
least one of final object/DT delivery, merged SELinux allow, native caller and
UID/domain, input validation, or effect closure. No `/dev` node was opened and
no ioctl was attempted.

## 6. Overall decision

**No new reproducible low-privilege route to disable User-0 Fire Launcher or
replace formal HOME was established.** The highest-value remaining static
question is the authorization boundary around tx3: service declaration
permission, inherited Stub/service checks, SELinux service-manager access for
candidate domains, and the exact upstream caller. That work must remain
host-only unless a natural, user-driven child-profile lifecycle supplies an
observable call. Forging tx3, guessing a `service call` parcel, or trying a
User-0 `UserInfo` is not justified and is not part of this phase.

## Status vocabulary

- **已證實 / Confirmed:** directly preserved code, manifest, baseline or
  transaction structure.
- **高可信推論 / Strong evidence:** bounded static inference with explicit
  missing edges.
- **待驗證 / Unknown:** a required edge is not present in the corpus.
- **已排除 / Disproved:** only a specifically tested route, such as the saved
  shell service lookup, not every possible implementation.
- **因風險拒絕測試:** unknown Binder parcels, driver opens/ioctls, OTA or
  recovery execution, root, partition writes and Fire Launcher mutations.

## Reproduction

```sh
python3 tools/scripts/build_phase13_report.py --force
python3 - <<'PY'
import csv
from pathlib import Path
p = Path('output/tables/phase13-control-surface.csv')
rows = list(csv.DictReader(p.open()))
allowed = {'Confirmed','Strong evidence','Probable','Hypothesis','Disproved','Unknown'}
assert rows and all(r['confidence'] in allowed for r in rows)
print(f'rows={len(rows)} confidence={sorted(set(r["confidence"] for r in rows))}')
PY
sha256sum firmware/manifests/PHASE13-HOST-ANALYSIS-20260810/sha256sums.txt
```

The normalized evidence table is
[`output/tables/phase13-control-surface.csv`](../output/tables/phase13-control-surface.csv),
and the detailed index is
[`findings/phase-13-evidence-index.md`](phase-13-evidence-index.md).
