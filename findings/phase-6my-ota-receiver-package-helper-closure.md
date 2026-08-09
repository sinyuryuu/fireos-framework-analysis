# Phase 6MY — BootAfterSystemOTAReceiver → PackageHelper closure

Date: 2026-08-10

Scope: host-only static analysis of the preserved PS7331 OOBE/OTA artifacts.
No ADB, broadcast, Binder transaction, updater, reboot, package mutation,
settings mutation, Fire Launcher mutation, or partition write was performed.

## Result

**已證實（bounded static path）:**

```text
AmazonPackageManagerService.onBootPhase(550)
  → guarded BOOT_AFTER_SYSTEM_OTA broadcast
  → BootAfterSystemOTAReceiver.onReceive
  → enableIncrementalFlow(context)
  → PackageHelper.enableComponent(context, OobeHomeActivity.class)
  → PackageManager.setComponentEnabledSetting(state=1, flags=1)
```

The same branch calls `OOBEActivationHelper.activateOOBEIF(context)`, which
writes OOBE setup keys through `Settings.Secure`/`Settings.Global` using a
context-derived `ContentResolver`. The receiver catch path can disable the
receiver itself (`state=2`), not Fire Launcher.

**已證實（bounded negative):** the reviewed receiver, OOBE activation helper,
PackageHelper, and SettingsDBUtils contain no `com.amazon.firelauncher`,
`setHomeActivity`, `addPreferredActivity`, or `replacePreferredActivity`
reference. Therefore this path is an OOBE/Setup Wizard component-state writer,
not evidence of a normal Fire Launcher HOME writer.

**高可信推論:** the state operations retain a context-derived user scope;
the preserved framework client path shows `ContextImpl.mUser` flowing into
provider/user resolution. The exact numeric post-OTA user is not encoded in
the selected sender callsite and remains **待驗證**.

**因風險拒絕測試:** replaying `BOOT_AFTER_SYSTEM_OTA` or executing the OTA
transition is rejected because the branch can enable `OobeHomeActivity` and
write `user_setup_complete`, `device_provisioned`, and `isOOBEActive`.

## Evidence and locations

| Edge | Evidence |
|---|---|
| Sender guard and broadcast | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96087-96126` |
| Receiver branch and error path | `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java:27-61` |
| Package state helper | `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/oobe/commons/utils/PackageHelper.java:11-22` |
| OOBE setting helper | `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java:53-56`; `SettingsDBUtils.java:51-64` |
| Context/user propagation | `decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log:435176-435236,449092-449185,452137-452150` |
| Manifest metadata | `artifacts/phase6j/ota-oobe-manifest-audit-20260805-01/manifest.txt:279-283,531-541` |

Input hashes: `activation` `6ebcb7eef7a03459a76b9c21cd59b61a30947f2b00a5624a4646825b8e3223d2`; `authorization_report` `4c2edb6e43b39bfbe615fd8779f49026f3694cad884ebab50103f0cfbd701fbc`; `boot_framework` `5ef6a8c6edea903e3bf7e5298be02041dc46be06881438457e79cbf8501b76df`; `fosservices` `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`; `manifest` `bcc51d83ee74bbc230b774a52684e3e4cdb5cbc6cff7be673e6e3979037275ff`; `package_helper` `900f2dd69d349b3b4718b7f988b7d5bd153af2e2cb3c1586600e5b048e760ad8`; `receiver` `c29b32bf6874b245859357d926773193c15771a6eb254f97edac57541ae5cb90`; `scope_report` `e962ba889cd93df672c9827a8411bdee6bc6c2bb2b75b7d2e5bf799002dc95d2`; `settings_helper` `6ceb23853939c6905bf2de12a6969e7568a3bf2119588a6c1d4347f4ba089b31`

Generated artifact: `artifacts/phase6my-bootafter-ota-package-helper-20260810-01`. Its `sha256sums.txt` must
pass before publication.

## Consequence for launcher/root research

This branch does not provide a supported or demonstrated ADB route to disable
`com.amazon.firelauncher`, change the ordinary HOME preferred record, or gain
root. It should not be replayed as a launcher workaround. The remaining safe
next step is provenance analysis of the exact framework service-context user
selection or a naturally occurring official OTA observation; neither justifies
manual broadcast injection.
