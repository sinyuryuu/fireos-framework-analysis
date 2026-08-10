# Phase 17, branch D — OTA/OOBE reachability

Scope: host-side review of the existing Fire OS 7.3.3.1 / PS7331 extraction,
APK/JAR/VDEX/disassembly, fosinit, manifest, and saved artifacts only. No OTA,
recovery, sideload, broadcast replay, reboot, partition write, exploit/root,
device contact, or package construction was performed.

## Result

The new reachability join is bounded and negative for ordinary app or shell
callers. The OTA app exposes an exported controller service and several
exported receivers, but the controller/deferred/check paths are protected by
the signature|privileged `com.amazon.dcp.ota.permission.CONTROLLER`; the boot
receiver is a system lifecycle entry, not proof of arbitrary broadcast
delivery. `BootAfterSystemOTAReceiver` has no observed component-local
`android:permission`, but its only confirmed sender is system-server passing
`com.amazon.permission.RECEIVE_BOOT_AFTER_SYSTEM_OTA`, followed by action,
OOBE-running, and retail-demo gates. The missing component attribute therefore
does not close an ordinary-app or shell route.

The guarded OOBE sink is real at source level: it enables `OobeHomeActivity`
and writes `user_setup_complete=0` / `isOOBEActive=1` through the settings
provider path. The exact numeric user and SettingsProvider authorization/data
flow are not closed. The preserved User 0 snapshot shows the receiver
registered and OOBE home disabled; it is not an execution result.

The shipped updater retains fixed partition-write capability in recovery /
update-binary context. No existing artifact connects shell or an ordinary APK
to recovery execution, native verification, or the partition writer. This
report does not treat exportedness, static native write calls, or a missing
manifest permission as an exploit.

## Reachability disposition

| Surface | Closed fact | Still missing |
|---|---|---|
| OTA controller service | Exported, single-user, `CONTROLLER`-protected | Exact accepted producer and native/recovery handoff |
| OTA check/deferred receivers | Exported but `CONTROLLER`-protected | Exact framework/controller caller joins |
| OTA boot receiver | System boot lifecycle entry | Full framework delivery proof and receiver caller context |
| Boot-after-system-OTA OOBE receiver | System-server sender plus receiver-side predicates; no local permission attribute observed | Protected-broadcast classification, numeric user, runtime delivery |
| SettingsProvider | System shared UID, exported provider, settings authority | Exact read/write authorization and per-user routing |
| OTA updater | Fixed high-privilege writer capability | Recovery exec/verifier/SELinux caller chain |

## Evidence boundary

The machine-readable matrix contains 10 rows and uses the requested fixed
header. It intentionally includes only the missing edges needed to join
exported components, permissions, caller context, OOBE/Settings sinks, and the
ordinary-app/shell closure; previously established Phase 16 facts are not
repeated as independent rows.

Safe continuation is host-only: offline manifest/protected-broadcast and
exact-build caller CFG joins, plus hash/provenance checks. Runtime confirmation
would require a natural official OTA event followed by read-only observation;
no synthetic trigger is permitted.

Row count: 10 data rows (excluding header).
