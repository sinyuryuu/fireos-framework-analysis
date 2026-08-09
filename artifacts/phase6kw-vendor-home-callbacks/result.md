# Phase 6KW — Vendor HOME callback closure

Scope: host-only analysis of collected `fosinit` XML and VDEX disassembly. No device command, Binder transaction, APK execution, or state mutation was performed.

## Inputs

- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` — SHA-256 `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- `decompiled/baksmali/vdexExtractor/services/disassembly.log` — SHA-256 `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53`
- XML directory `artifacts/amazon-services`

## Observed callback registrations

| Implementation | Resolve line | Resolve override | Observed behavior | Fire literal | Confidence |
|---|---:|---:|---|---:|---|
| `com.amazon.android.server.am.AppCompatActivityStackSupervisorCallback` | 41123 | yes | delegates to IPackageManager.resolveIntent, then applies isUninstalledApp filter | no | Confirmed |
| `com.fireos.eve.EveActivityStackSupervisorCallback` | — | no | no concrete resolveIntent override; inherited base returns null | no | Confirmed |

## Decision

- **Confirmed:** `ActivityStackSupervisor.resolveIntent()` invokes the vendor callback chain first and falls back to the standard `PackageManagerInternal.resolveIntent()` result when every callback returns null.
- **Confirmed:** the collected AppCompat callback delegates to `IPackageManager.resolveIntent()` and only filters the observed uninstalled-app flag; the method does not contain the Fire Launcher package literal.
- **Confirmed:** the collected Eve supervisor callback has no concrete `resolveIntent` override and therefore inherits the base null result; its observed method is restart telemetry, not HOME selection.
- **Strong evidence:** the registered launcher-hijack-preventer fosinit files do not register a `VendorActivityStackSupervisorCallback`; their registrations are ActivityStack/AMS or PM/permission callbacks.
- **Not established:** this artifact scope alone cannot prove that every runtime-loaded callback or every non-VDEX native path is absent. The result is a static closure for the collected PS7331 artifacts, not a universal negative.

See the generated CSV and Mermaid graph for exact file-level evidence.
