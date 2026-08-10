# Phase 14 — broad privilege-surface and asset reconciliation

## Executive result

Phase 14 widened the review beyond the Launcher to the PS7331 source/boot/OTA
assets, Amazon private IPC, KFT child/profile writers, OOBE/OTA lifecycle,
Settings/DPM surfaces, and preserved native/driver candidates. The work was
host-only plus one bounded read-only device capture. No Binder transaction,
driver/ioctl, root/exploit, updater/recovery execution, package/settings/user
mutation, Fire Launcher mutation, reboot, remount, or partition write was
performed.

**Confirmed:** the exact PS7331 source archive, OTA `.bin`, extracted boot and
selected framework/Amazon artifacts are present with preserved hashes and can
support offline analysis. The asset inventory is in
`work/luna_worker_cont_asset_inventory_20260810.csv`.

**Confirmed:** the read-only device capture still resolves User 0 HOME to
`com.amazon.firelauncher/.Launcher` with `priority=50`, `isDefault=true`, and
the saved ordinary preferred XML points to the same component. Recent Activity
Manager records show HOME starts to that component.

**Confirmed:** the service list contains Amazon private service names, but the
saved shell `dumpsys` attempts for `amazonactivitymanager`,
`amazonwindowmanager`, `amazonusermanagerservice`, and `amazonprofileservice`
all returned `Can't find service`. This closes the saved shell lookup route,
not every possible privileged caller.

**Strong evidence:** the KFT path is a real package/component-state writer,
but its closed semantic caller is child/profile lifecycle and the supplied
`UserInfo.id` remains the target. The corpus does not close an ordinary
app/shell → accepted tx3 → system-server identity → User 0 → Fire Launcher
state/HOME sink chain.

**Strong evidence, not a vulnerability finding:**
`preWarmApplicationForUser()` contains a static pattern in which
`checkCallingPermission(com.amazon.permission.APP_PREWARM)` is not visibly
consumed before `clearCallingIdentity()`, followed by ApplicationInfo lookup
and `startProcessLocked`. The saved legitimate caller is privileged Amazon
Alexa; the private service is not reachable through the saved shell route, and
no HOME/package-state sink or privilege transition was observed.

**Not established:** a low-privilege path that disables User 0 Fire Launcher,
changes formal HOME, or reaches an OTA/partition sink. The current highest-value
next step is host-only completion of caller, Stub, permission, SELinux service
context, input validation, and downstream-consumer joins for the prewarm and
remaining private services. Guessing Binder transactions or replaying OOBE/OTA
actions is not justified by this evidence.

## Device and asset guard

| Item | Observation | Status |
|---|---|---|
| Build | `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys` | Confirmed |
| User 0 HOME | `com.amazon.firelauncher/.Launcher`, priority 50 | Confirmed |
| Preferred XML | Fire Launcher MAIN + HOME + DEFAULT record | Confirmed |
| Private-service shell lookup | Four selected `dumpsys` calls: `Can't find service` | Confirmed |
| Device mutation in this phase | `false` in capture metadata | Confirmed |
| PS7331 source tar | 2,563,328,975 bytes; SHA-256 recorded in worker inventory | Confirmed |
| PS7331 OTA `.bin` | 1,301,005,356 bytes; SHA-256 recorded in worker inventory | Confirmed |
| Boot image | Present in extracted PS7331 tree; hash recorded in worker inventory | Confirmed |

The full input hash list is
`firmware/manifests/PHASE14-HOST-ANALYSIS-20260810/sha256sums.txt`.

## 1. Broad control-surface result

The normalized machine-readable table is
`output/tables/phase14-control-surface.csv`. Each row separates caller, gate, Binder
identity, user scope, sink/effect, and the missing edge. The important
distinction is:

```text
capability or static writer
        ≠ accepted low-privilege caller
        ≠ identity handoff
        ≠ User 0 target
        ≠ observed HOME/package-state effect
```

### KFT and package-state writers

The KFT writer remains the closest Fire-specific state sink: it can enable
the Tahoe FreeTime launcher and disable Fire Launcher/Launcher3 for a supplied
child/profile `UserInfo.id`. The preserved closed caller is child creation or
child lifecycle. The missing external caller, service-manager/SELinux client
tuple, tx3 authorization, and User 0 parcel provenance prevent an exploit or
User-0 relay claim. This phase did not replay tx3 and did not construct a
forged `UserInfo`.

### Private ActivityManager prewarm candidate

The exact saved disassembly is
`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40535`.
It contains the following bounded sequence:

```text
checkCallingPermission(APP_PREWARM)
clearCallingIdentity()
getApplicationInfo(package, 1024, user)
PreWarmCacheHelper...
startProcessLocked(..., "prewarm", ...)
```

This is a static authorization-review candidate. The saved Alexa source calls
it only after endpoint/package filtering and the package holds the Amazon
signature permission. The service lookup barrier and missing input/consumer
edges mean the correct status is **Strong evidence / Unknown**, not “root
primitive”.

### OTA and post-install

The updater script and native `update-binary` show fixed-target write
capabilities in recovery/updater context. The evidence does not close a
low-privilege caller, accepted-package verifier chain, AVB/rollback decision,
SELinux domain, or actual execution. No update or recovery path was run.

### OOBE, DPM, SettingsProvider, native and driver surfaces

These remain bounded static writers/capabilities with missing publication,
caller/UID/domain, user attribution, validation, or final HOME/package sink
edges. `BootAfterSystemOTAReceiver` is an OTA-gated OOBE lifecycle writer, not
a generic third-party HOME API. DCPMS and SettingsProvider evidence does not
close to Fire Launcher state. Driver nodes and native symbols are not treated
as reachable merely because an init rule, config, or symbol exists.

## 2. Evidence categories

See `findings/phase-14-evidence-index.md` for the complete row-level index.

- **已證實 / Confirmed:** asset hashes, package/HOME dumps, service-list and
  read-only shell errors, preserved method/manifest structure.
- **高可信推論 / Strong evidence:** KFT child-scoped state-writer semantics;
  prewarm permission-return anomaly candidate; privileged caller boundary;
  OTA capability with missing reachability edges.
- **待驗證 / Unknown:** external private-service caller universe, SELinux
  client tuple, exact DEX register semantics of the prewarm check, arbitrary
  input validation, downstream HOME/package consumer, and driver/native
  reachability.
- **已排除 / Disproved:** the saved shell route directly finding the four
  selected private services; a closed ordinary app/shell → User 0 Fire state
  writer in the preserved corpus; any claim that OTA capability alone is an
  exploit.
- **因風險拒絕測試:** unknown `service call`, Binder parcel forgery, driver
  open/ioctl, root/exploit, OOBE/OTA broadcast replay, updater/recovery,
  sideload/flash, remount, SELinux or Fire Launcher state mutation.

## 3. Next minimal safe research target

1. Build a host-only parent Stub/callee map for `IAmazonActivityManager` and
   the four private services.
2. Join the service registration/init context, manifest declarations,
   permission definitions, `service_contexts`, and saved SELinux allow rules.
3. Enumerate all preserved callers of `preWarmApplicationForUser()` and
   prove target package/profile input validation and consumer scope.
4. Scan the exact PS7331 corpus for an exported wrapper or documented read-only
   API that reaches a package/HOME writer; if no closed edge appears, close the
   candidate as inaccessible rather than replaying it.
5. Keep the existing Fire Launcher baseline as a guard; do not repeat the
   disproved component-disable or priority matrices.

## Reproduction and QA

```sh
python3 tools/scripts/build_phase14_report.py --force
python3 - <<'PY'
import csv
from pathlib import Path
p = Path('output/tables/phase14-control-surface.csv')
rows = list(csv.DictReader(p.open()))
allowed = {'Confirmed','Strong evidence','Probable','Hypothesis','Disproved','Unknown'}
assert rows and all(r['confidence'] in allowed for r in rows)
assert all(len(r) == len(rows[0]) for r in csv.reader(p.open()))
print('rows=', len(rows), 'confidence=', sorted({r['confidence'] for r in rows}))
PY
git diff --check
```

Input manifest SHA-256 is generated by the builder; the report and graph are
derived outputs and can be regenerated without a device connection.
