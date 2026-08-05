# Phase 6AJ evidence index

Canonical artifact：`artifacts/phase6aj/input-home-boundary-20260805-05/`

本階段沒有新的裝置接觸。所有 rows 均由 host-only script 以保存的 PS7331
disassembly、caller source、既有 read-only capture 和既有 Phase 6AG/6R 報告
產生。原始輸入雜湊見：
`artifacts/phase6aj/input-home-boundary-20260805-05/input-sha256.json`。

| Evidence ID | Source | File / method | Observed result | Interpretation | Confidence |
|---|---|---|---|---|---|
| `6AJ-HOME-001` | Fire OS VDEX | `fosservices/disassembly.log:22640-22655` | publishes `amazon_input` and `amazon_keyevent` | private input services exist | Confirmed |
| `6AJ-HOME-002` | live read-only capture | `phase6j-service-visibility-20260805-01/service_list.stdout.txt:55-56`; `filtered_avc.matches.txt` | services listed; shell UID 2000 `find` denied | no ordinary shell Binder handle | Confirmed |
| `6AJ-HOME-003` | Fire OS smali | `registerKeyEventInterceptor`, line 19829; `0x024c3e-0x024eaa` | permission, package, foreground, key whitelist checks | authorized callback only | Confirmed |
| `6AJ-HOME-004` | Fire OS smali | `registerKeyEventListener`, line 20048; `0x025710` | `GET_KEYEVENTS` gate and SecurityException | listener not shell-writable | Confirmed |
| `6AJ-HOME-005` | Fire OS smali | `registerNextKeyEventListener`, line 20077; `0x025780` | same `GET_KEYEVENTS` gate | one-shot listener not shell-writable | Confirmed |
| `6AJ-HOME-006` | Fire OS smali + permission dump | `setInputFilter`, line 20112; validator line 22437; permission dump | system app or `FILTER_INPUT_EVENTS(signature|amazon)` | input filter authorization closed | Confirmed |
| `6AJ-HOME-007` | Fire OS smali | `checkInjectEventsPermission`, `0x02667a`; `inject`/`injectSequence` | PID/UID and injection permission checks | no safe shell injection route | Confirmed |
| `6AJ-HOME-008` | Fire OS smali + permission dump | `KeyEventBinderService` methods 3845-3851 | private partner/input-locking permissions | no shell key-policy writer | Confirmed |
| `6AJ-HOME-009` | Alexa ARIA source | `AriaPartialScreen.java:56,77,174-180,323-335` | keycode 3 is observed for overlay dismissal | privileged observer, not resolver override | Strong evidence |
| `6AJ-HOME-010` | bounded negative scan | AmazonInputManagerService class scope | no resolver/HOME method names in scope | service itself not shown selecting HOME | Strong evidence |
| `6AJ-HOME-011` | Fire OS smali | `isCallerSystemApp`, line 21874; interceptor `0x024c56-0x024d2a` | system-app, whitelist and foreground restrictions | arbitrary third party cannot register | Confirmed |
| `6AJ-HOME-012` | Fire OS smali + live build | constructor `0x026c0e-0x026c30`; Phase 6AH build state | debug property only under `Build.IS_DEBUGGABLE`; production is `ro.debuggable=0` | not a production shell control | Confirmed |
| `6AJ-OTA-001` | prior static closure | Phase 6AG/6R reports | BootAfterSystemOTAReceiver remains guarded OOBE/OTA lifecycle | related static-only item; no replay | Confirmed |

## Safety record

```text
device_contacted=false
binder_transactions_sent=false
input_injected=false
broadcast_replayed=false
package_or_settings_mutated=false
ota_or_recovery_executed=false
partition_written=false
```

完整 machine-readable rows：
`artifacts/phase6aj/input-home-boundary-20260805-05/input-home-boundary.csv`。
