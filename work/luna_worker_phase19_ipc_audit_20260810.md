# Phase 19A — host-side Amazon Framework/System Services IPC inventory

Date: 2026-08-10 (Asia/Taipei). Scope is read-only host analysis of the exact PS7331 artifacts, VDEX/decompiled logs, fosinit XML, manifests and Phase 1–18 evidence. No ADB, Binder transaction, service call, driver/ioctl, root, OTA/recovery, reboot, package/settings mutation or other device operation was performed. Only the requested CSV and this Markdown file were added.

## Result

Six non-duplicate residual rows are recorded in the companion CSV. They retain only caller→gate→identity/user-scope→sink edges that remain open after comparison with the Phase 17 IPC residual ledger and Phase 18 reconciliation. Existing Phase 17/18 rows for Amazon flags/metadata, proxy receiver, profile `initiateLauncher`, input injection, OOBE, prewarm, KFT child writer, and the broad private profile/input family were not copied as duplicate rows.

`UNKNOWN` means the saved artifacts do not establish the edge; it is not a vulnerability classification. Every row separates static capability from caller reachability and runtime effect.

## Residual rows

| ID | Surface | Unclosed edge | Sink / disposition |
|---|---|---|---|
| P19A-001 | KFT `IAmazonUserManager` tx3 | Trusted `createChildUser` client, tx3 authorization, and exact `UserInfo.id` provenance | Static child/profile package-state writer; no User-0 route established |
| P19A-002 | AmazonProfileService `startProfilePicker` tx41 | Caller permission, picker config provenance, and current-user/component enforcement | Explicit current-user activity launch; no HOME resolver or package writer in slice |
| P19A-003 | AmazonWindowManager `setPipVisibility` / `setOverscan` | Wrapper gate, Binder caller, and downstream WMS enforcement | PIP/display/window state only in bounded implementation; no HOME sink |
| P19A-004 | H2ClientService exported bind | Signature-bound caller and adult/child user creation data flow | Profile lifecycle handoff; no direct Fire/HOME sink recovered |
| P19A-005 | `amazonwindowmanager_fosinit` callbacks | Callback completeness and consumer permission/data flow | Window/PIP policy/event sinks; no HOME/package writer found |
| P19A-006 | DCPMS child-experience decision | Production client, permission holder, service visibility and consumer | Process-global read/callback map only; downstream sink unknown |

## Coverage and exclusions

The host scan covered ServiceManager publication/visibility, AIDL Proxy and Stub transaction maps, `onTransact` dispatch, `getCallingUid`/`getCallingPid`, permission checks, `clearCallingIdentity`/`restoreCallingIdentity`, explicit user arguments, parent/profile/KFT paths, input/window manager paths, HOME callback registrations, package/component/settings sinks, and fosinit registration. The exact input `inject`/`injectSequence` helper-to-native gap was reviewed but excluded from new rows because Phase 17 already owns that row; the same no-repeat rule was applied to prewarm and flags/metadata.

Saved runtime evidence is limited to prior captures: private-service shell lookup denial, existing service visibility, and no new execution. No runtime result is inferred for rows classified UNKNOWN.

## Safe next steps

Continue only with offline source/manifest/fosinit joins: recover production caller packages and signatures, complete inherited permission checks, map user IDs and service contexts, and trace first consumers. Do not call private Binder services, bind H2/profile services, trigger callbacks, create users, mutate package/settings state, or perform device operations.

CSV QA target: exact requested 14-column schema, RFC-style quoted fields, unique IDs, and one row per residual edge.
