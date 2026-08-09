# Phase 6BK：KFT child-profile runtime boundary

## Scope

This note records the only controlled device mutation in Phase 6BK: starting and
switching to the already-existing User 10 profile, then switching back to User 0
and stopping User 10. It does not invoke a private Binder transaction, change a
package or setting, run an OTA/recovery path, or write a partition.

Device: `G001LT0511550CFT`  
Build: `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`

## Preflight evidence

The read-only preflight found User 10 as `test:8010`, stopped/unstarted, with a
Profile Owner. The Device Policy dump identifies the owner as
`com.amazon.tahoe/.deviceadmin.FreeTimeDeviceAdminReceiver`:

- `adb/phase6bk/PHASE6BK-KFT-PREFLIGHT-RO-20260810-01/users_dump.stdout.txt:19-26`
- `adb/phase6bk/PHASE6BK-KFT-PREFLIGHT-RO-20260810-01/device_policy.stdout.txt:7-10`

Before the lifecycle observation, User 0 resolved HOME to Fire Launcher at
priority 50:

- `adb/phase6bk/PHASE6BK-KFT-PREFLIGHT-RO-20260810-01/home_resolve.stdout.txt:1-2`

The package dump records the expected per-user distinction. Fire Launcher is
default-enabled for User 0 (`enabled=0`) and disabled for User 10
(`enabled=2`, `lastDisabledCaller: android`):

- `adb/phase6bk/PHASE6BK-KFT-PREFLIGHT-RO-20260810-01/firelauncher_package.stdout.txt:855-867`

Tahoe is enabled for User 0 and has its FreeTime launcher component enabled for
User 10:

- `adb/phase6bk/PHASE6BK-KFT-PREFLIGHT-RO-20260810-01/tahoe_package.stdout.txt:1482-1498`

## Controlled runtime observation

The runner executed only:

```text
adb -s G001LT0511550CFT shell am start-user 10
adb -s G001LT0511550CFT shell am switch-user 10
adb -s G001LT0511550CFT shell am switch-user 0
adb -s G001LT0511550CFT shell am stop-user -w 10
```

The target user became active and rollback returned to User 0:

- `adb/phase6bk/PHASE6BK-KFT-RUNTIME-20260810-01/result.md:3-10`
- `adb/phase6bk/PHASE6BK-KFT-RUNTIME-20260810-01/metadata.json:172-217`

While User 10 was selected, its HOME query returned `FallbackHome` with
priority `-1000`; User 0 continued to resolve to Fire Launcher. This is a
profile lifecycle/setup observation, not evidence that Tahoe became the formal
HOME resolver result:

- `adb/phase6bk/PHASE6BK-KFT-RUNTIME-20260810-01/home_target_after_switch.stdout.txt`
- `adb/phase6bk/PHASE6BK-KFT-RUNTIME-20260810-01/home_user0_after_switch.stdout.txt`

The runner's metadata confirms that no private Binder, package/settings, OTA, or
partition mutation occurred:

- `metadata.json:173-195,208-217`

## Classification

- **Confirmed:** User 10 has the Tahoe Profile Owner and the per-user Fire/Tahoe
  component state matches the KFT child-profile model.
- **Strong evidence:** the live state correspondence is consistent with the
  statically recovered KFT launcher-state path.
- **Not established:** that `createChildUser()` or
  `enableKftLauncherComponent()` executed during this run.
- **Disproved for this route:** switching the existing child profile provides a
  User-0 HOME replacement or a shell-accessible Fire Launcher mutation.

