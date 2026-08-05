# Phase 6AV evidence index

| Evidence ID | Source | File / method | Observed result | Interpretation | Confidence |
|---|---|---|---|---|---|
| 6AV-IPC-001 | PS7331 VDEX | `fosservices/disassembly.log:19829-19999`, `registerKeyEventInterceptor` | GET_KEYEVENTS, calling UID package lookup, whitelist and foreground checks are present | Input interception is protected and not an ordinary HOME setter | Confirmed |
| 6AV-IPC-002 | PS7331 VDEX | `fosservices/disassembly.log:20112-20122`, `setInputFilter` | Delegates to synthetic helper then `registerSecondaryInputFilter`; helper body not in bounded excerpt | Requires further static closure; no bypass claim | Strong evidence |
| 6AV-IPC-003 | PS7331 VDEX | `fosservices/disassembly.log:20679-20713`, `setInputLockingMode` | `INPUT_LOCKING` permission and mode validation are present | Shell input-locking route not established | Confirmed |
| 6AV-IPC-004 | PS7331 VDEX | `fosservices/disassembly.log:76246-76256,78949-78966`, `initiateLauncher` | `PROFILE_INTERACTION` guard; method returns profile success | Not a bounded HOME resolver write | Confirmed |
| 6AV-IPC-005 | PS7331 VDEX | `fosservices/disassembly.log:77222-77266`, `startProfilePicker` | Configured profile picker is started explicitly for current user | Profile UI route, not HOME replacement | Strong evidence |
| 6AV-IPC-006 | PS7331 VDEX | `fosservices/disassembly.log:54297-54325`, `enableKftLauncherComponent` | Explicit disabled state request for Fire Launcher in KFT path | High-risk lifecycle path; device test rejected | Confirmed |
| 6AV-IPC-007 | PS7331 VDEX + live AVC | `fosservices/disassembly.log:40453-40534`, `preWarmApplicationForUser` | Permission check is not locally consumed before identity clear; shell service discovery is denied | Static authorization anomaly candidate, not shell-reachable proof | Strong evidence |
| 6AV-LIVE-001 | Saved live capture | `artifacts/phase6aq/public-summary-20260805-05/service-check-results.txt` | `service check` returns not found for private Amazon services | Shell lacks a Binder handle under enforcing policy | Confirmed |
| 6AV-LIVE-002 | Saved live capture | `artifacts/phase6aq/public-summary-20260805-05/amazon-service-avc.txt` | shell UID 2000 `service_manager find` denied | Service inventory is not callability | Confirmed |
