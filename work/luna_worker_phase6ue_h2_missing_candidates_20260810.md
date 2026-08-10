# Phase 6UE — H2 missing-candidate bounded search ledger

Date: 2026-08-10. Scope is read-only and bounded to existing local artifacts only. No download, adb, bind/service call, or mutation was performed.

## Result

Seven Phase6TW candidates remain requested-permission `UNKNOWN` for the requested H2 exact-build question. The ledger is conservative: a package path, a permission name, or an AVOD binder self-check does not establish the missing H2 permission/bind contract.

| Candidate | Existing evidence | Classification |
|---|---|---|
| `com.amazon.venezia` | Baseline path/process; shared protected-permission names in a union manifest tree | UNKNOWN for requested H2 permission/bind; no candidate APK XML-tree/JADX bundle |
| `com.amazon.h2settingsfortablet` | APK exists, SHA-256 `9b769646…549b0`; manifest output is zero bytes | UNKNOWN; no XML-tree, signature/UID, split, or JADX bind evidence |
| `com.amazon.csapp` | Baseline path; CSApp/DYK permission names in union manifest tree | UNKNOWN for requested H2 permission/bind; no candidate APK XML-tree/JADX bundle |
| `com.amazon.wifilocker` | Baseline path; two CredentialLocker permission names in union manifest tree | UNKNOWN for requested H2 permission/bind; no candidate APK XML-tree/JADX bundle |
| `com.amazon.ags.app` | Baseline path; games-service/ADM permission names in union manifest tree | UNKNOWN for requested H2 permission/bind; no candidate APK XML-tree/JADX bundle |
| `com.amazon.avod` | APK/manifest/JADX provenance; `SDK_ACCESS`; `PlaybackSdkFeature` binds `PlaybackSdkService`; caller UID check | Requested H2 candidate remains UNKNOWN; evidence is AVOD-specific and not `IH2ClientService` |
| `com.amazon.kindle` | Baseline path; `LIBRARY_ACCESS` in union manifest tree | UNKNOWN for requested H2 permission/bind; no candidate APK XML-tree/JADX bundle |

## Bounded search scope

Searched only these existing local areas: `artifacts/phase6bg-h2-settings-readonly-20260805-01`, `artifacts/phase6do/*`, `artifacts/phase6ac/protected-broadcast-source-audit-20260805-02`, `device/baseline/BASELINE-20260803-02` and `BASELINE-20260803-05`, `firmware/manifests/*`, plus existing `artifacts/**/jadx` and `artifacts/**/decompiled` files. No corpus expansion was made after the missing-artifact condition was established.

## Key limitations

- `com.amazon.h2settingsfortablet` APK is present, but `manifest.txt` is empty (0 lines/0 bytes), so APK XML-tree uses-permission extraction is unavailable in the existing artifact.
- No per-candidate signing certificate, numeric package UID, `sharedUserId`, or split list was available for the seven requested candidates in the bounded scope.
- No candidate-specific `IH2ClientService`, `bindService`, or `ServiceConnection` proof was found. AVOD has a separate `PlaybackSdkService` bind and binder-caller check, recorded in the CSV.
- The `phase6ac` XML-tree is a union/protected-broadcast artifact, not provenance for each candidate APK; its permission-name hits are therefore marked partial.

See the companion CSV for SHA-256, path, line, class/symbol, and classification per evidence row.
