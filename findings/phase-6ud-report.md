# Phase 6UD host-only H2 client, KFT scope and permission semantics

This bundle integrates the exact-build H2 grant-candidate/client search, the KFT child writer caller/scope search, and the `android.amazon.perm` protection-level comparison.

Generation HEAD: `869d3203d7dfd6bd36d4d6a913cff580e0233a35`.

## Safety boundary

No device, adb, Binder bind/call, service call, transaction construction, user creation or switch, package/permission mutation, driver operation, OTA, reboot, Root/exploit or partition write was performed.

## Inputs

- **6UA H2 grant/client:** `work/luna_worker_phase6ua_h2_grant_client_20260810.md` (76f847a4b3842874870e88d02f35b117ee075ed39608ce1c1e6e12d731e33ac9); `work/luna_worker_phase6ua_h2_grant_client_20260810.csv` (19ff5c49265689cb0d0e64324760c29c85e1e34c86134b349e7f89bd2a95d306); 12 row(s).
- **6UB KFT caller/scope:** `work/luna_worker_phase6ub_kft_caller_scope_20260810.md` (985baf87524b8c11746268ee861e430e9fc5ac26594268107cbc9f2dc4f858c4); `work/luna_worker_phase6ub_kft_caller_scope_20260810.csv` (03a5b7c38a1ab02f38a49e5d3c16e611e2ce72c1d056cc36a8de85b84d287f19); 7 row(s).
- **6UC Amazon permission semantics:** `work/luna_worker_phase6uc_amazon_perm_semantics_20260810.md` (f101c66f0d13e83ffadaa6cf0a718d23e084bb09016426263c5a38f2a05051a2); `work/luna_worker_phase6uc_amazon_perm_semantics_20260810.csv` (37dcc749b5fff557bc3612eab502b696ec044647ea88f914022d5c9974a84aba); 14 row(s).

Context hashes: `findings/phase-6tz-report.md` (fb73aebc8abcbc14f3e8877387511bc74b29936f9f584aef548f716d2749aa5e); `findings/phase-6tz-evidence-index.md` (4cd86a7b6c63fd5491e21efec0fbb1cb787aa00278f983675e118ecda32173ad); `output/tables/phase6tz-control-surface.csv` (a06b6616b63659ef53883aae21d62d867787005bdf6159255f2cfbc9550c9361); `findings/phase-6tv-report.md` (e766794a9683923e11a723e11d4e1b772512212745699f8e071e5ac0bb4cd31f)

## H2 client result

Ten exact custom grant records remain grant candidates. Three preserved XML trees show the requested custom permission for Tahoe, Kindle OOBE and Parental Controls, but no package has a closed `bindService` → `ServiceConnection` → `IH2ClientService` callsite in the bounded corpus. The other seven requested-permission fields are not preserved and remain `UNKNOWN`. Grant or request evidence is not actual runtime binding or a shell path.

## KFT caller and user scope

`AmazonUserManagerImpl.createChildUser(String)` creates a child user and passes its `UserInfo` through transaction 3 to `enableKftLauncher`; an upgrade lifecycle caller also processes only `isChildUser` entries. The writer uses `UserInfo.id` to enable Tahoe and disable Fire/Launcher3. The tx3 permission/UID and cross-user/admin gate are not joined in the bounded method slice, so this is child/profile writer evidence, not a User-0 Fire restoration or arbitrary caller claim.

## Permission semantics

`android.amazon.perm` is a system-shared-UID/core framework package and owns the custom records. `0x80000002` is statically consistent with a signature base plus an Amazon vendor flag, while the exact FireOS parser semantics and shell/ordinary-app eligibility remain `UNKNOWN`. AOSP's permission ownership/signature checks do not prove a FireOS bypass.

## Verdict

The research now has a stronger permission-owner fact and a confirmed child KFT writer path, but still no accepted ordinary-app/shell caller leading to User-0 HOME, Fire package state, root or partition effect. The next safe target is preserving exact candidate manifests and code-level bind/caller artifacts; no service invocation is justified by this evidence.

Integrated rows: `33`; parse warnings: `0`.

Warnings:
- None detected.
