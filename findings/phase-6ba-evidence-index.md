# Phase 6BA evidence index

| Evidence ID | Source | Result | Status |
|---|---|---|---|
| `6BA-PM-001` | Phase 6AP PS7331 `fireos-res.apk` resource closure | `amazon.fireos:raw/package_manager_deny_list` explicitly contains `com.amazon.firelauncher` | Confirmed |
| `6BA-PM-002` | Phase 6AI / Phase 6V VDEX | `ControlProtectedPackagesCallback` joins system/privileged status, deny-list membership, and UID 2000 in the protected-package callback | Confirmed static |
| `6BA-KFT-001` | Phase 6AY/6AK VDEX `AmazonUserManagerService.BinderService.enableKftLauncherComponent:54297-54325` | KFT path requests enabled state 2 for Fire Launcher and Launcher3 after FreeTime launcher setup | Confirmed static; not invoked |
| `6BA-CB-001` | Phase 6AL VDEX/callback registrations | ActivityStackSupervisor pre-hook is present; AppCompat delegates to PM, Eve/base fall through; no inspected direct Fire component injection | Strong evidence, bounded scope |
| `6BA-IN-001` | Phase 6AJ VDEX/permission artifacts | Key interception/filter APIs require Amazon/system/foreground/whitelist gates; shell service lookup denied | Confirmed |
| `6BA-AM-001` | Phase 6AV/6K VDEX | `preWarmApplicationForUser` shows an unconsumed permission-result candidate before `startProcessLocked`; known caller is privileged Alexa and service is shell-inaccessible | Strong evidence candidate; not exploit proof |
| `6BA-OOBE-001` | Phase 6AB/6R OOBE and OTA artifacts | Post-OTA receiver can enable priority-100 OOBE Home and change setup state under lifecycle predicates | Confirmed static; replay rejected |
| `6BA-OTA-001` | Phase 6AH/6AW updater artifacts | Official updater has verification and high-impact block/firmware write boundaries | Confirmed static; execution rejected |
| `6BA-ADB-001` | Phase 6AT public runtime summary | 30/30 Fire foreground observations, 30/30 redirects, 30/30 target foreground observations; resolver unchanged | Confirmed temporary workaround |
| `6BA-SAFETY-001` | Phase 6AT/6AZ safety manifests | No unknown Binder, Fire Launcher mutation, OTA execution, partition write, or Root operation in the measured paths | Confirmed |
