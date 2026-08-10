# Phase 20A — IPC residual closure

Date: 2026-08-10 (Asia/Taipei). Baseline: public commit `d1592fb50377727342fb4c69fdd75eb7cc2fc4ff`, Phase 19A IPC ledger, and exact PS7331 artifacts. This is host-only static analysis. No ADB, Binder transaction, `service call`, bind/start action, driver/ioctl, root, reboot, OTA, package/settings mutation, or other device operation was performed.

## Result

The companion CSV contains six unique `P20A-*` rows, one closure pass for each P19A-001..006. Phase 17/18/19 completed rows were not copied as new hypotheses.

The main closure points are:

- KFT tx3 now has an exact static upstream: H2 `AndroidUserHelper.addAndroidUser` calls `AmazonUserManager.createChildUser` for child roles. The tx3 Stub still has descriptor-only dispatch and no visible local permission check. Crucially, `enableKftLauncher` calls the KFT package/component setters before `clearCallingIdentity`; the clear/restore pair surrounds only later DPM/profile-owner work. Thus the package-state setters are not shown to receive a laundered system identity. Exact UID/signature grant and PMS acceptance remain open, and `UserInfo.id` is child/profile-scoped rather than proven User 0.
- H2 `H2ClientService` is exported but `singleUser` and protected by `BIND_SERVICE`, declared `signature|amazon`. Its AIDL Stub dispatches API methods to workflow code without a second caller-UID check. Recovered manifest holders include parental controls, Tahoe and Tablet SystemUI; exact runtime caller/UID and role-to-user provenance remain unjoined. The H2 code reaches profile/user workflow and can hand off to KFT, but no direct HOME/PMS setter is present.
- AmazonProfile `startProfilePicker` has an internal handler caller and launches a configured component as `ActivityManager.getCurrentUser()`. The bounded method has no `clearCallingIdentity`, no explicit target-user argument, and no preferred/HOME/package-state sink. External Binder caller and configuration provenance remain unknown.
- AmazonWindowManager PIP caller provenance is narrowed to the system-server `AmazonWindowManagerPwmCallback`, which obtains `amazonwindowmanager` and calls `setPipVisibility`. The wrapper writes PIP state; overscan delegates to WMS. Neither bounded path reaches PMS/HOME/package state.
- The fosinit callback row is correspondingly bounded to system-server callback dispatch and non-HOME window/PIP effects. Runtime-loaded registration completeness remains an evidence gap, not a vulnerability claim.
- DCPMS is closed for the requested sink question: the service is signature|amazon, exported singleUser, UID 10090 in the public service map, and its AIDL/ServiceBinder paths retain process identity without a sensitive platform sink. External client provenance is still unknown, but it does not reopen a PMS/HOME route.

`UNKNOWN` in the CSV denotes an unobserved edge only. It does not mean that a vulnerability exists.

## No-repeat and safety boundary

This pass did not recreate Phase 17/18/19 Amazon flags, proxy receiver, prewarm, input injection, OOBE, or broad private-service rows. It used earlier DCPMS bounded evidence to close P19A-006 rather than treating the missing client as a new finding. Remaining next steps are offline joins of package signatures, exact UID provenance, manifest/config data, inherited permission checks, and PMS cross-user/protected checks. No private IPC invocation is justified.

CSV schema was checked for the requested caller, gate, identity, user scope, sink, missing edge, classification, evidence and next-safe-step fields, with unique P20A IDs and RFC-style quoted data rows.
