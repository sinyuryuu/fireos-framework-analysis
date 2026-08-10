# Play Store (`com.android.vending`) bounded unknown closure

Date: 2026-08-10 (Asia/Taipei). Scope was host-only static analysis of the preserved PS7331 package corpus. No device, ADB, Binder/service call, installation/start, permission/state change, or evidence mutation was performed.

## Corpus and integrity

Inputs:

- `artifacts/phase6mb-vending-static-20260810-01/base.apk` — SHA-256 `a5f456832018bbf571f915e949ea9dcd707ad514c269899e916b9b25d5297a50`; seven DEX files (`classes.dex` through `classes7.dex`), `AndroidManifest.xml`, `resources.arsc`.
- `artifacts/phase6mb-vending-static-20260810-01/split_config.arm64_v8a.apk` — SHA-256 `b59980b4c8764f59c20289c19935fa4da497d799e2a4763ca163c5ef1928f90a`; native libraries include `libapkanalysis.so`, `libcronet.143.0.7445.0.so`, `libtensorflowlite_jni.so`, `libzucchini.so`, and `libzwrapper.so`.
- `artifacts/phase6mb-vending-static-20260810-01/split_config.ja.apk` — SHA-256 `b55b5c31a778187abb394f169e95af79844ac93cfd4b242ea58383e6531df0ed`; resource split.
- `artifacts/phase6mb-vending-static-20260810-01/manifest-print.txt` — SHA-256 `e332aa77041fd4c4c58c4861471341a8563c7f6c51fc64f54c651fccb27e61c4`.
- Recovered Java: `artifacts/phase6mb-vending-jadx-20260810-01/base/sources/`. JADX exited nonzero and emitted partial output; no smali or disassembly directory is preserved in this corpus.

The machine-readable evidence index is [the companion CSV](luna_worker_vending_unclosed_surface_20260810.csv).

## Findings

### `com.amazon.firelauncher`: bounded negative for the inspected literal surface

The exact literal was absent from all seven base DEX string scans and from the recovered JADX source tree. This is corroborated by the existing `artifacts/phase6mb-vending-static-20260810-01/static-search-summary.md` and the 38-call-site scan at `output/tables/phase6mb-vending-state-writer-scan.csv`. It is not treated as proof about encoded/dynamic/native/resource behavior.

### HOME/default launcher: bounded negative for recovered code

The DEX string table does contain HOME-related strings at exact extracted-Dex offsets: `classes.dex` offset `7051158`; `classes2.dex` offset `6756767`; `classes3.dex` offset `9329981`; `classes4.dex` offsets `8039413` and `8157198`; `classes5.dex` offset `8294535`. These strings alone are not call evidence.

The recovered preferred-activity writer is `artifacts/phase6mb-vending-jadx-20260810-01/base/sources/defpackage/uez.java:22-63`. At lines 52-55 it constructs an `IntentFilter` for `android.intent.action.WEB_SEARCH` and `android.intent.category.DEFAULT`, then calls `PackageManager.replacePreferredActivity`; it selects a queried activity matching caller-supplied `str` (lines 41-55). This is a confirmed limited preferred-activity writer, but not a HOME/default-launcher writer. No recovered `setPreferredActivity`, `addPreferredActivity`, `startHomeActivity`, or HOME-selection writer was identified.

### Package/component state setters: confirmed generic callers

The existing scan reports 38 recovered setter call sites. Representative exact locations are:

- `defpackage/azbu.java:761-766`: `new ComponentName(str, str2)` followed by `setComponentEnabledSetting`.
- `defpackage/uls.java:361`: application package is `str6`.
- `com/google/android/finsky/verifier/impl/enforcement/UninstallTask.java:222`: application package is `this.j`.
- `defpackage/ayya.java:986` and `:1262`: component targets are computed/field-backed.

These are confirmed callers but no recovered call path binds them to `com.amazon.firelauncher`. The manifest's requested `CHANGE_COMPONENT_ENABLED_STATE` and `SET_PREFERRED_APPLICATIONS` permissions are provenance, not proof of a PackageManager authorization bypass (`manifest-print.txt:133` and `:257`).

### Exported entrypoints: unresolved boundary, not confirmed sink

`manifest-print.txt:1470-1479` declares exported `com.google.android.finsky.setup.LauncherConfigurationReceiver` for `com.android.launcher3.action.FIRST_SCREEN_ACTIVE_INSTALLS`. Its recovered source is `.../base/sources/com/google/android/finsky/setup/LauncherConfigurationReceiver.java:26-36`; JADX explicitly skipped `b(Context, Intent)` with “instruction units count: 723”. Because this method is an exported input boundary and may process package/component data, its target flow remains unresolved.

Other relevant exported setup surfaces include `VpaSelectionOptionalStepActivity` (`manifest-print.txt:1348-1386`) and `DseService` (`manifest-print.txt:1571-1581`), both permission-gated. `DseService.java:63-150` shows DSE package/install bookkeeping, but no recovered launcher setter in that excerpt. No component was invoked.

### Identity clearing: no confirmed relay to a high-impact sink in recovered code

Recovered clear/restore pairs occur at `defpackage/bgkh.java:506-529`, `beip.java:4750-4759`, `azml.java:833-853`, `qeb.java:66-74`, `qdy.java:38-56`, and `qet.java:240-248`. Their shown method bodies perform object construction, content-resolver/network/account work, or restoration; none contains a preferred-activity or package/component-enabled sink in the same recovered method. This is a bounded negative for recovered code only. Skipped methods, including the exported receiver above, remain unresolved.

## Native/resource and decompiler limits

The arm64 split contains native code, but no native disassembly was supplied; therefore native code is unresolved for behavior, while the literal `com.amazon.firelauncher` surface is bounded negative in the inspected extracted DEX strings. `resources.arsc`, the Japanese resource split, assets, baseline profiles, and native libraries were not treated as executable Java control-flow evidence. JADX partial output includes explicit skipped methods (for example `LauncherConfigurationReceiver.java:31-36`) and many decompiler warnings; no claim here upgrades a skipped region to negative.

## Bottom line

No confirmed Play Store path to `com.amazon.firelauncher`, HOME/default-launcher selection, or an identity-clearing relay to a high-impact sink was established. One confirmed limited sink exists: `replacePreferredActivity` for `WEB_SEARCH`/`DEFAULT`. The bounded unknown that remains is the skipped `LauncherConfigurationReceiver` body and any behavior implemented in native libraries/resources or other failed JADX regions; closing that remainder requires preserved smali/disassembly or an equivalent host-only decoder corpus, not invocation.
