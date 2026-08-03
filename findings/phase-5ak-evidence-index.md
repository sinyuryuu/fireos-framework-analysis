# Phase 5AK evidence index

| Evidence ID | Source | File / method | SHA-256 | Test ID / timestamp | Observed result | Interpretation | Confidence |
|---|---|---|---|---|---|---|---|
| P5AK-STATE-001 | read-only device capture | `adb/phase5/PHASE5AK-ANDROID-IMPLEMENTATION-STATE-20260804-01/` | `sha256sums.txt` = `80a743ad0a527cd7ef6fd94092caec84dd5428f357825fff8e71361df631060a` | `PHASE5AK-ANDROID-IMPLEMENTATION-STATE`; 2026-08-03T21:47:43Z | ADB `device`, shell UID 2000, no Accessibility service, HOME resolves to Fire Launcher | Current state is suitable for safe preparation, not measurement | 已證實 |
| P5AK-STATE-002 | read-only device capture | `accessibility_dump.stdout.txt` | `a7fa317a41a681576bda73bd5d2857d71dcc86e55c79498bdac7557ad6c3f35c` | same | `services:{}` | User consent is not currently active | 已證實 |
| P5AK-STATE-003 | read-only device capture | `home_resolver.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` | same | `com.amazon.firelauncher/.Launcher`, effective priority 50 | Redirect APK has not changed formal HOME | 已證實 |
| P5AK-APK-001 | device package hash + build record | `redirect_path.stdout.txt`; `tools/phase4-accessibility/BUILD-RECORD-20260803.md` | APK `e6a5536d11ff6be5de557d751817af7de69d841f7cd0d03e028d5da2537b013a` | Phase 5AE / current state | Installed redirect APK is the key-event + PendingIntent variant | Correct artifact identity | 已證實 |
| P5AK-APK-002 | prior build metadata + device package hash | `alias_path.stdout.txt`; `adb/phase5/PHASE5AE-KEYEVENT-PENDINGINTENT-T01/metadata.tsv` | APK `ac87bf9fde1ea1d501ef2ff5ce4ebe5e062952432f990384a64cbe49f77aa68a` | Phase 5AE / current state | Target alias artifact matches the prepared test | Measurement target is identified | 已證實 |
| P5AK-SRC-001 | local source review | `LauncherRedirectService.java:39-57` | `37ff8777f38c0a1f2c70adc4a28bc55cfb3cb9b4f07cb9052edb0846ddbc32a0` | host-only | Only HOME key is conditionally consumed after visible toggle | Public Accessibility key-event boundary | 已證實 |
| P5AK-SRC-002 | local source review | `LauncherRedirectService.java:75-101` | same | host-only | Explicit `CATEGORY_LAUNCHER` component is dispatched via PendingIntent | This is foreground redirect, not HOME resolver mutation | 已證實 |
| P5AK-SRC-003 | local manifest/XML review | `AndroidManifest.xml:17-26`; `accessibility_service_config.xml:2-8` | build record / source | host-only | Service requires `BIND_ACCESSIBILITY_SERVICE`, key filtering, no window-content retrieval | User consent and limited data scope are explicit | 已證實 |
| P5AK-ANDROID-001 | Android official API documentation | `AccessibilityService.onKeyEvent` | https://developer.android.com/reference/android/accessibilityservice/AccessibilityService.html | public reference | Callback observes key events and can consume them only when service is enabled | Explains Android implementation boundary | Strong evidence |
| P5AK-ANDROID-002 | Android official API documentation | `PendingIntent.getActivity` / `send` | https://developer.android.com/reference/android/app/PendingIntent.html | public reference | System-mediated execution of an already-created operation | Does not create HOME preference | Strong evidence |
| P5AK-CVE-001 | public Android GhostLock index | Mallory target summary | https://www.mallory.ai/vulnerabilities/CVE-2026-43499 | bounded public review | Public Android implementations are device/build-specific; no exact PS7330 profile observed | No safe exact target for live test | 高可信推論 |
| P5AK-CVE-002 | local prior exact-target review | `findings/phase-5aj-mtk-android9-cve-poc-review.md` | tracked report | prior Phase 5AJ | No exact KFTRWI/trona/MT8183/PS7330 Android root implementation found in bounded review | Do not execute mismatched native payload | Strong evidence |
| P5AK-MEASURE-001 | experiment status | no `measure/` directory created | N/A | current phase | Accessibility was not enabled; no measurement executed | No success/failure rate may be claimed | 已證實 |

## Reproduction commands

The collector and analyzer are host/project scripts. Both support a dry-run or are
read-only; neither writes device state. The raw capture's per-file hashes are the
authoritative source for device output integrity.
