# Phase 6MV — Read-only runtime and GPL/OTA provenance closure

Generated: 2026-08-09T22:22:27.376830+00:00
Schema: phase6mv-runtime-readonly-report-v1

## Scope and safety

The runtime capture used only read-only ADB queries and dumps. No Binder
transaction, service call, package/settings mutation, input event, reboot,
OTA/recovery operation, Root/exploit, or Fire Launcher disable/force-stop was
performed. The GPL/OTA inventory was delegated to luna_worker and is included
as a hashed input.

## Results

### 已證實

- Device: [KFTRWI] / [trona] / [Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys]; security patch [2024-08-01];
  incremental [0031575863172].
- User 0 HOME resolver returned priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
com.amazon.firelauncher/.Launcher.
- Candidate query reported 3 activities found:.
- Fire package dump contains separate User 0 and User 10 state records; the
  child-user record does not alter User 0.
- Amazon private names are present in service list, but every selected service
  check returned not found for shell.
- The GPL/official-package inventory found kernel/source and official OTA
  artifacts, but no complete Amazon framework or init source tree.

### 高可信推論

The current runtime evidence is consistent with the existing boundary: User 0
remains controlled by the standard PackageManager HOME resolver, with Fire's
privileged manifest candidate winning. Child-user state is separate. The
visible private service names do not constitute an ADB-accessible Binder relay.

### 待驗證

- Indirect/native consumers not represented in the preserved disassembly.
- Exact runtime provenance of the deny-list resource package.
- Full updater canonicalization dataflow; static updater write capability is
  not evidence of an ADB or shell launcher route.

### 因風險拒絕測試

Unknown private Binder transactions, OTA execution, recovery/sideload,
partition writes, driver ioctls, Root attempts, and Fire Launcher state
changes were not performed.

## Runtime evidence matrix

| Finding | Observed | Classification | Evidence |
|---|---|---|---|
| HOME resolver | priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true \| com.amazon.firelauncher/.Launcher | Confirmed | home_resolve.stdout.txt |
| HOME candidates | 3 activities found: | Confirmed | home_candidates.stdout.txt |
| Fire User 0 state | User 0: ceDataInode=852182 installed=true hidden=false suspended=false stopped=false notLaunched=false enabled=0 instant=false virtual=false | Confirmed | firelauncher_package.stdout.txt |
| Fire User 10 state | User 10: ceDataInode=827498 installed=true hidden=false suspended=false stopped=false notLaunched=false enabled=2 instant=false virtual=false | Confirmed | firelauncher_package.stdout.txt |
| Users | Users: \| 	UserInfo{0:sinyu:13} running \| 	UserInfo{10:test:8010} | Confirmed | users.stdout.txt |
| Private service checks | amazonpackagemanager: Service amazonpackagemanager: not found; amazonactivitymanager: Service amazonactivitymanager: not found; amazonwindowmanager: Service amazonwindowmanager: not found; amazondevicepolicymanager: Service amazondevicepolicymanager: not found; amazonaccessibilitymanager: Service amazonaccessibilitymanager: not found; amazonusermanagerservice: Service amazonusermanagerservice: not found; amazonprofileservice: Service amazonprofileservice: not found | Confirmed | service_*_stdout.txt |
| Service-name listing | selected Amazon names are present in service list; listing is not a shell Binder handle | Confirmed | service_list.stdout.txt |

## Reproduction

Capture:

    tools/scripts/capture_phase6mv_runtime_readonly.sh --serial G001LT0511550CFT --output adb/phase6mv/PHASE6MV-READONLY-20260810-02

Build report:

    python3 tools/scripts/build_phase6mv_runtime_report.py --dry-run
    python3 tools/scripts/build_phase6mv_runtime_report.py --force

The original capture hash manifest remains in the capture directory.
