# Phase 6SN–6SQ broad privilege-surface closure

This is a host-only integration of four bounded static reviews. It does not claim a privilege path merely because a permission, service, native symbol, or sink exists. A positive route requires an evidence-complete caller → gate → identity/user scope → state or capability sink chain.

Integration HEAD at generation: `0f50f2f58bf15f1903e5510a43e0814fea596119`.

## Safety boundary

No ADB, Binder transaction, service call, driver open/ioctl, OTA/recovery execution, reboot, package/settings mutation, Root, exploit, or partition write was performed. Existing device evidence and raw worker files were not overwritten.

## Inputs

- **6SN permission-holder/caller:** `work/luna_worker_phase6sn_permission_caller_20260810.md` (d523e6a27b89961ebc1dd4fbd45054d459fc02a0eb262f91215b163dd8c9bb47); `work/luna_worker_phase6sn_permission_caller_20260810.csv` (56e9429f229afdd30f12d555d5b6b57aa33f13dffa1e8c045be03b9ddee98e17); 15 ledger row(s).
- **6SO native driver caller:** `work/luna_worker_phase6so_driver_native_20260810.md` (69657c1ab898b64910cd136d186c71a5643b42558dca453665942bec870625ea); `work/luna_worker_phase6so_driver_native_20260810.csv` (a534cd20d3034bf968f45b94f03afb62f6224052e9d99d741a8a9b8f2b7bac50); 11 ledger row(s).
- **6SP OTA/recovery native boundary:** `work/luna_worker_phase6sp_ota_native_20260810.md` (2c0bcfe491643d67d7c2c717d9e3e823c1e502fd344539b91523ed4111fa24f5); `work/luna_worker_phase6sp_ota_native_20260810.csv` (2b21953b3be5d797e8a677d6267469a7aa1b61745dee77eb3072de010f6edd2a); 17 ledger row(s).
- **6SQ HOME/PackageManager writer:** `work/luna_worker_phase6sq_home_pms_writer_20260810.md` (5f5f7ec2e30f4c96d1af322a42e56b9b9cd22784dfcd1f1624a04355674951ac); `work/luna_worker_phase6sq_home_pms_writer_20260810.csv` (c36c2c65fd5dd8b171bf074fe6fec5f8401e0dce80bd4513a8ad59de4c7b3266); 10 ledger row(s).

## Integrated interpretation

- **Permission/caller surface:** declaration, holder, grant, and production caller are separate claims. A `signature|privileged` declaration or a published Binder service is not an ordinary-app or shell capability.
- **Native drivers:** source/config strings and a shipped node do not establish a caller. A positive driver route requires an exact shipped native caller and policy/permission edge; unresolved edges remain `UNKNOWN`.
- **OTA/recovery:** privileged write capability is not a safe shell route and is not a HOME/package-state bypass. Parser or indirect-call gaps remain static unknowns and are not tested with crafted input.
- **HOME/PMS writers:** a writer must be shown to target User 0 and the Fire component/preferred record. Child/profile-scoped writers, OOBE setup writers, metadata stores, and process/window sinks are not equivalent.

## Evidence status rule

`Confirmed` means directly shown by the cited exact-build source/artifact; `Strong evidence` means a bounded edge is shown but runtime or a downstream condition remains; `Unknown` means the corpus does not establish the edge; `Disproved` means the cited evidence contradicts the hypothesis. No row is upgraded solely by naming, exported status, or a missing local check.

## Remaining safe work

Only additional exact-build corpus completeness, source-to-DEX/native mapping, and naturally obtained read-only captures are justified. Unknown Binder transactions, driver ioctls, OTA/recovery execution, package-state changes, and exploit/root testing remain out of scope for this safe closure.
