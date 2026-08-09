This report is generated from the host-only artifact `artifacts/phase6mw-home-state-sinks-20260810-01`.

# Phase 6MW — HOME/package-state sink inventory

Classification: host-only static inventory. No ADB, Binder transaction, ioctl, reboot, OTA, Root, APK execution, or device mutation was performed.

## Inputs

- JADX Java files: 21871
- disassembly logs: 4
- sink/reference rows: 175
- The source hash manifest is `input-manifest.csv`; all output hashes are in `sha256sums.txt`.

## Results

### 已證實

- The bounded corpus produced 175 direct sink/reference rows; 59 are HOME/preferred-related or contain HOME literals.
- 2 rows contain a direct `com.amazon.firelauncher` literal in the bounded context; this is a static reference, not proof of a User-0 writer.
- Each row preserves source path, line, enclosing class/method, permission markers, identity markers, and user-scope markers for manual review.

### 高可信推論

- Existing Phase 6MH/6IA findings remain the authoritative closure for the known Amazon `fosservices` package-state writers: KFT child state is user-scoped, while the private Amazon Package Manager surface does not expose a HOME setter.
- A direct callsite in Settings, DPM, PMS, or SystemUI must still pass its own caller, admin, cross-user, and protected-package gates; this inventory does not turn it into an ordinary-app relay.

### 待驗證

- Native/reflective/indirect calls not represented as direct Java or disassembly method references remain outside this scan.
- The exact runtime deny-list resource provenance remains a separate resource/package audit.

### 已排除

- No device-side mutation or private transaction was used to turn a static sink into a launcher PoC.
- This scan does not justify repeating the already-rejected Fire component/package disable tests.

## Reproduction

```sh
python3 tools/scripts/audit_phase6mw_home_state_sinks.py --dry-run
python3 tools/scripts/audit_phase6mw_home_state_sinks.py --force
(cd artifacts/phase6mw-home-state-sinks-20260810-01 && sha256sum -c sha256sums.txt)
```

## Review queue

| Source | Line | Class/method | Target | Scope | Fire literal | HOME literal | Permissions | User markers |
|---|---:|---|---|---|---|---|---|---|
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log | 367356 | amazon.content.pm.AmazonPackageManagerImpl / addPreferredActivity (Landroid/content/IntentFilter;I[Landroid/content/ComponentName;Landroid/content/ComponentName;)V | addPreferredActivity | other | false | false |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log | 369211 | <unknown> / replacePreferredActivity (Landroid/content/IntentFilter;I[Landroid/content/ComponentName;Landroid/content/ComponentName;)V | replacePreferredActivity | other | false | false |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log | 50474 | android.app.admin.DevicePolicyManager / addPersistentPreferredActivity (Landroid/content/ComponentName;Landroid/content/IntentFilter;Landroid/content/ComponentName;)V | addPersistentPreferredActivity | aosp_framework | false | false |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log | 442564 | android.app.ApplicationPackageManager / addPreferredActivity (Landroid/content/IntentFilter;I[Landroid/content/ComponentName;Landroid/content/ComponentName;)V | addPreferredActivity | aosp_framework | false | false |  | UserId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log | 442584 | android.app.ApplicationPackageManager / addPreferredActivityAsUser (Landroid/content/IntentFilter;I[Landroid/content/ComponentName;Landroid/content/ComponentName;I)V | addPreferredActivity | aosp_framework | false | false |  | AsUser |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log | 445778 | <unknown> / replacePreferredActivity (Landroid/content/IntentFilter;I[Landroid/content/ComponentName;Landroid/content/ComponentName;)V | replacePreferredActivity | other | false | false |  | UserId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log | 445797 | <unknown> / replacePreferredActivityAsUser (Landroid/content/IntentFilter;I[Landroid/content/ComponentName;Landroid/content/ComponentName;I)V | replacePreferredActivity | other | false | false |  | AsUser |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log | 879670 | <unknown> / <unknown> | addPersistentPreferredActivity | other | false | false |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log | 939343 | android.content.pm.IPackageManager$Stub / <unknown> | setHomeActivity | aosp_framework | false | true |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log | 939557 | <unknown> / <unknown> | addPersistentPreferredActivity | other | false | false |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log | 939613 | <unknown> / <unknown> | replacePreferredActivity | other | false | false |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log | 939649 | <unknown> / <unknown> | addPreferredActivity | other | false | false |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log | 2228854 | <unknown> / <unknown> | addPreferredActivity | other | false | false |  | UserId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log | 2264600 | com.android.internal.telephony.SmsApplication / configurePreferredActivity (Landroid/content/pm/PackageManager;Landroid/content/ComponentName;I)V | replacePreferredActivity | other | false | false |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log | 2264602 | com.android.internal.telephony.SmsApplication / configurePreferredActivity (Landroid/content/pm/PackageManager;Landroid/content/ComponentName;I)V | replacePreferredActivity | other | false | false |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log | 2264604 | com.android.internal.telephony.SmsApplication / configurePreferredActivity (Landroid/content/pm/PackageManager;Landroid/content/ComponentName;I)V | replacePreferredActivity | other | false | false |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log | 2264606 | com.android.internal.telephony.SmsApplication / configurePreferredActivity (Landroid/content/pm/PackageManager;Landroid/content/ComponentName;I)V | replacePreferredActivity | other | false | false |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/fosservices/disassembly.log | 26056 | com.amazon.android.internal.server.input.keymapping.appadapter.AppAdapterHandler / goToRegistration ()V | setComponentEnabledSetting | amazon_or_oem | false | true |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/services/disassembly.log | 179266 | <unknown> / <unknown> | clearPackagePreferredActivities | other | false | true |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/services/disassembly.log | 500924 | <unknown> / runSetHomeActivity ()I | setHomeActivity | other | false | true |  | UserHandle |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/services/disassembly.log | 778680 | <unknown> / reportAssistContextExtras (Landroid/os/IBinder;Landroid/os/Bundle;Landroid/app/assist/AssistStructure;Landroid/app/assist/AssistContent;Landroid/net/Uri;)V | setHomeActivity | other | false | true |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/services/disassembly.log | 785598 | <unknown> / <unknown> | setComponentEnabledSetting | other | false | true |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/services/disassembly.log | 839077 | <unknown> / addPersistentPreferredActivity (Landroid/content/ComponentName;Landroid/content/IntentFilter;Landroid/content/ComponentName;)V | addPersistentPreferredActivity | other | false | false |  | UserHandle; CallingUserId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/services/disassembly.log | 931580 | <unknown> / addPreferredActivityInternal (Landroid/content/IntentFilter;I[Landroid/content/ComponentName;Landroid/content/ComponentName;ZILjava/lang/String;)V | addPreferredActivity | other | false | false | SET_PREFERRED_APPLICATIONS; checkCallingOrSelfPermission |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/services/disassembly.log | 965876 | <unknown> / replacePreferredActivity (Landroid/content/IntentFilter;I[Landroid/content/ComponentName;Landroid/content/ComponentName;I)V | replacePreferredActivity | other | false | false | SET_PREFERRED_APPLICATIONS; checkCallingOrSelfPermission |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/baksmali/vdexExtractor/services/disassembly.log | 966955 | <unknown> / setHomeActivity (Landroid/content/ComponentName;I)V | replacePreferredActivity | other | false | true |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/amazon-settings/sources/com/android/settingslib/wrapper/PackageManagerWrapper.java | 72 | PackageManagerWrapper / replacePreferredActivity | replacePreferredActivity | settings | false | true |  | AsUser; userId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/amazon-settings/sources/com/android/settingslib/wrapper/PackageManagerWrapper.java | 73 | PackageManagerWrapper / replacePreferredActivity | replacePreferredActivity | settings | false | true |  | AsUser; userId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/settings/sources/com/android/settings/applications/defaultapps/DefaultHomePicker.java | 90 | DefaultHomePicker / for | replacePreferredActivity | settings | false | true |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/settings/sources/com/android/settingslib/wrapper/PackageManagerWrapper.java | 71 | PackageManagerWrapper / replacePreferredActivity | replacePreferredActivity | settings | false | true |  | AsUser; userId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/settings/sources/com/android/settingslib/wrapper/PackageManagerWrapper.java | 72 | PackageManagerWrapper / replacePreferredActivity | replacePreferredActivity | settings | false | true |  | AsUser; userId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/settings/sources/com/android/settingslib/wrapper/PackageManagerWrapper.java | 91 | PackageManagerWrapper / setApplicationEnabledSetting | setApplicationEnabledSetting | settings | false | true |  | AsUser; userId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/settings/sources/com/android/settingslib/wrapper/PackageManagerWrapper.java | 92 | PackageManagerWrapper / setApplicationEnabledSetting | setApplicationEnabledSetting | settings | false | true |  | AsUser; userId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui-nores/sources/com/android/server/am/ActivityManagerService.java | 14285 | <unknown> / if | setHomeActivity | other | false | true |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui-nores/sources/com/android/server/am/AppErrors.java | 618 | AppErrors / if | clearPackagePreferredActivities | aosp_framework | false | true |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui-nores/sources/com/android/server/am/AppErrors.java | 652 | AppErrors / if | clearPackagePreferredActivities | aosp_framework | false | true |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui-nores/sources/com/android/server/devicepolicy/DevicePolicyManagerService.java | 6910 | <unknown> / addPersistentPreferredActivity | addPersistentPreferredActivity | other | false | false |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui-nores/sources/com/android/server/devicepolicy/DevicePolicyManagerService.java | 6918 | <unknown> / getActiveAdminForCallerLocked | addPersistentPreferredActivity | other | false | false |  | userHandle; UserHandle; CallingUserId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui-nores/sources/com/android/server/pm/PackageManagerService.java | 14839 | ClearStorageConnection / addPreferredActivity | addPreferredActivity | other | false | false |  | UserId; userId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui-nores/sources/com/android/server/pm/PackageManagerService.java | 14855 | ClearStorageConnection / if | addPreferredActivity | other | false | false | checkCallingOrSelfPermission; SET_PREFERRED_APPLICATIONS | userId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui-nores/sources/com/android/server/pm/PackageManagerService.java | 14910 | ClearStorageConnection / replacePreferredActivity | replacePreferredActivity | other | false | false |  | userId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui-nores/sources/com/android/server/pm/PackageManagerService.java | 14927 | ClearStorageConnection / if | replacePreferredActivity | other | false | false | checkCallingOrSelfPermission; SET_PREFERRED_APPLICATIONS | userId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui-nores/sources/com/android/server/pm/PackageManagerService.java | 15135 | ClearStorageConnection / addPersistentPreferredActivity | addPersistentPreferredActivity | other | false | false |  | userId; UserHandle; CallingUserId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui-nores/sources/com/android/server/pm/PackageManagerService.java | 15607 | <unknown> / setHomeActivity | setHomeActivity | other | false | true |  | AsUser; userId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui-nores/sources/com/android/server/pm/PackageManagerService.java | 15628 | <unknown> / replacePreferredActivity | replacePreferredActivity | other | false | true |  | userId; AsUser |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui-nores/sources/com/android/server/pm/PackageManagerShellCommand.java | 2383 | InstallParams / if | setHomeActivity | other | false | true |  | userId; UserHandle |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui/sources/com/android/server/am/ActivityManagerService.java | 11758 | <unknown> / if | setHomeActivity | other | false | true |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui/sources/com/android/server/am/AppErrors.java | 614 | AppErrors / if | clearPackagePreferredActivities | aosp_framework | false | true |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui/sources/com/android/server/am/AppErrors.java | 648 | AppErrors / if | clearPackagePreferredActivities | aosp_framework | false | true |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui/sources/com/android/server/devicepolicy/DevicePolicyManagerService.java | 6742 | <unknown> / addPersistentPreferredActivity | addPersistentPreferredActivity | other | false | false |  |  |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui/sources/com/android/server/devicepolicy/DevicePolicyManagerService.java | 6750 | <unknown> / getActiveAdminForCallerLocked | addPersistentPreferredActivity | other | false | false |  | userHandle; UserHandle; CallingUserId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui/sources/com/android/server/pm/PackageManagerService.java | 13049 | ClearStorageConnection / addPreferredActivity | addPreferredActivity | other | false | false |  | UserId; userId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui/sources/com/android/server/pm/PackageManagerService.java | 13065 | ClearStorageConnection / if | addPreferredActivity | other | false | false | checkCallingOrSelfPermission; SET_PREFERRED_APPLICATIONS | userId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui/sources/com/android/server/pm/PackageManagerService.java | 13120 | ClearStorageConnection / replacePreferredActivity | replacePreferredActivity | other | false | false |  | userId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui/sources/com/android/server/pm/PackageManagerService.java | 13137 | ClearStorageConnection / if | replacePreferredActivity | other | false | false | checkCallingOrSelfPermission; SET_PREFERRED_APPLICATIONS | userId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui/sources/com/android/server/pm/PackageManagerService.java | 13345 | ClearStorageConnection / addPersistentPreferredActivity | addPersistentPreferredActivity | other | false | false |  | userId; UserHandle; CallingUserId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui/sources/com/android/server/pm/PackageManagerService.java | 13817 | <unknown> / setHomeActivity | setHomeActivity | other | false | true |  | AsUser; userId |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui/sources/com/android/server/pm/PackageManagerService.java | 13838 | <unknown> / replacePreferredActivity | replacePreferredActivity | other | false | true |  | userId; AsUser |
| /Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/decompiled/jadx/ota-PS7331/systemui/sources/com/android/server/pm/PackageManagerShellCommand.java | 2451 | InstallParams / if | setHomeActivity | other | false | true |  | userId; UserHandle |
