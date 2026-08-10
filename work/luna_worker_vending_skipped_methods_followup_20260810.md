# Phase 6PZ residual follow-up — PS7331 Play/Vending

Host-only reverse-analysis result for the exact-build Play/Vending corpus. No
ADB, broadcast, service call, Binder transaction, install, OTA, root action, or
device mutation was performed. Existing artifacts were read only; this report
and its CSV are new files.

## Result

The residual is now bounded into two distinct surfaces:

1. `LauncherConfigurationReceiver` has a recovered baksmali body. It is an
   exported receiver for `FIRST_SCREEN_ACTIVE_INSTALLS` with no manifest
   permission. The body does not accept an arbitrary broadcast as sufficient:
   it requires a `verificationToken` `PendingIntent`, checks its creator
   against the current launcher, and applies setup/HOME-candidate checks. The
   accepted path consumes hotseat/widget/workspace/folder item lists and calls
   Play Store restore bookkeeping (`aoba.k`, then `aofc.y`). This is a launcher
   metadata/restore path, not evidence of a Fire Launcher replacement or HOME
   resolver write.

2. `DseService` is not a blank skipped class. The host JADX source recovers the
   service lifecycle, binder gate, caller-package authorization, DSE/search
   selection, browser-default, secure-settings eligibility, pending-intent
   return, and install bookkeeping methods. `g()` carries JADX duplicated-block
   warnings, so exact branch-level equivalence remains partial. The service is
   exported but permission-gated by `com.google.android.finsky.permission.DSE`;
   the host runtime snapshot says that permission is `normal` and owned by
   `com.android.vending`, but that fact alone does not establish an arbitrary
   caller or a bypass. `mi()` requires the DeviceSetup feature flag, and `o()`
   checks `Binder.getCallingUid()` through package resolution and an
   authorization helper before API use.

## Chain evidence

### LauncherConfigurationReceiver

- Manifest: `artifacts/phase6mb-vending-static-20260810-01/manifest-print.txt:1470-1479`.
  The receiver is `exported=true`, has no `android:permission`, and receives
  `com.android.launcher3.action.FIRST_SCREEN_ACTIVE_INSTALLS`.
- Trigger observation: `artifacts/phase6k/readonly-device-20260805-01/preferred_activities.stdout.txt:5251-5252` lists the Vending receiver for that action. This is runtime registration evidence, not proof of a particular sender.
- Recovered body: `artifacts/phase6ps-vending-receiver-20260810-01/LauncherConfigurationReceiver.java:43-369`.
  The first boundary is `verificationToken`; missing token returns early. A
  creator matching the current launcher is accepted; otherwise the body checks
  setup state and package/launcher qualification before rejecting or accepting.
- First state consumer: item arrays become Play Store restore records through
  `aoba.k(...)` and `aofc.y(...)` (recovered body around lines 329-350). No
  literal Fire Launcher target, `replacePreferredActivity`,
  `setComponentEnabledSetting`, or direct HOME launch was recovered.

### DseService

- Manifest: `artifacts/phase6mb-vending-static-20260810-01/manifest-print.txt:1571-1581`.
  The service is `exported=true`, requires `com.google.android.finsky.permission.DSE`,
  and advertises `com.android.vending.setup.IDseService.BIND`.
- Permission provenance: the same manifest declares/uses the DSE permission
  (`:26`, `:537`); the read-only host snapshot records source package
  `com.android.vending`, `protectionLevel=normal`, and Vending's grant at
  `artifacts/phase6k/readonly-device-20260805-01/preferred_activities.stdout.txt:13785-13789,21440-21441,21494`.
  This is not caller provenance.
- Registration observation: `preferred_activities.stdout.txt:8048-8049,33161`
  lists the DSE service for the bind action.
- Identity gate: `DseService.java:655-673` (`mi`, `o`) returns a binder only
  when the DeviceSetup flag is enabled, then maps `Binder.getCallingUid()` to
  packages and rejects unauthorized package sets.
- First consumers by recovered method:
  - `f()` / `g()` (`:272-484`): selected browser/search-provider package,
    existing-package checks, install scheduling/bookkeeping; `g()` may call
    `uez.a(str)` under the DeviceDefaultAppSelection gate.
  - `h()` (`:487-526`): starts the explicit Setup Wizard search-selector
    activity.
  - `i()` (`:528-574`): may send a supplied first-party `PendingIntent` back
    after feature gating; target identity is not supplied by the caller path
    here.
  - `j()` (`:576-603`): writes eligibility secure-settings state through an
    injected writer.
  - `t()` (`:233-245`): calls
    `PackageManager.setDefaultBrowserPackageNameAsUser`, not a HOME preferred
    writer.
  - `s()` (`:699-736`): creates DSE install work/bookkeeping.

No recovered path reaches Fire Launcher, `MAIN + HOME` preferred resolution,
component enablement for Fire Launcher, root, or a system/root sink. The
recovered browser/default-search and secure-settings sinks are real state
consumers, but they are not to be relabeled as HOME control. The unknown
smali/DEX branch regions remain unknown; skipped/partial code is not itself a
vulnerability finding.

## Deliverables

- CSV: `work/luna_worker_vending_skipped_methods_followup_20260810.csv`
- This report: `work/luna_worker_vending_skipped_methods_followup_20260810.md`
- CSV data rows: 2 (header excluded).
- CSV schema validation: 2 rows, 9 fields each.
- CSV SHA-256: `63edbe2e77c6d203101b8f022c0c389f0505ac23a3ea8a430be20dab0790c4df`
- Markdown SHA-256 before this hash line was added: `806acd048e5b084faa61853e724c58eff2d59691c61252a3fc02d11da628f6ac`.
