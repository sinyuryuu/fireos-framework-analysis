# Phase 6MC H2 static artifact metadata

This directory documents a read-only pull and offline analysis of the installed
`com.amazon.alta.h2clientservice` package. The APK itself is not committed to
the public repository.

| Item | Value |
|---|---|
| Device build family | Fire OS PS7331 / Android 9 API 28 |
| Package | `com.amazon.alta.h2clientservice` |
| Installed path | `/system/priv-app/com.amazon.h2clientservice/com.amazon.h2clientservice.apk` |
| APK SHA-256 | `b1def31c9b1ba2aa8064d31d18e294a9b60e5a98a06a1ec657ad115a08f1850b` |
| Manifest-print SHA-256 | `f8ed581842c1f35d231e963246d91c2defb665f743d87db46a6b7791434d5dbd` |
| JADX | 1.5.6 |
| JADX output | `artifacts/phase6mc-alta-jadx-20260810-01/` (local, not committed) |
| Device operation | `pm path`, `dumpsys package`, `cmd package query-services`; no bind/start/transaction |

The service is exported but protected by
`com.amazon.alta.h2clientservice.permission.BIND_SERVICE`, declared as a
signature permission. The recovered APK contains household/profile workflows
and calls `AmazonUserManager.createChildUser()`/`createAdultUser()`, but the
bounded scan found no Fire Launcher literal or HOME/preferred-activity writer.
