# Fire Launcher Manifest Analysis

Status: `Confirmed` for the installed Fire Launcher artifact and baseline.

Source: `decompiled/jadx/firelauncher/resources/AndroidManifest.xml`

SHA-256: `ba88dc674466a2c4561e7258586ca31f739e8527153d81dc6cd2a262a3f2fdab`

## 1. HOME activity

| Field | Observed value | Evidence |
|---|---|---|
| Package | `com.amazon.firelauncher` | Manifest/application and runtime package dump |
| HOME activity | `com.amazon.firelauncher.Launcher` (`.Launcher`) | Manifest lines 316–330; runtime HOME query |
| Activity launch mode | `singleTask` | Manifest line 319 |
| HOME filter priority | `50` | Manifest line 323 |
| Actions | `android.intent.action.MAIN` plus Amazon tutorial actions | Manifest lines 324–327 |
| Categories | `android.intent.category.HOME`, `android.intent.category.DEFAULT` | Manifest lines 328–329 |
| `LAUNCHER` category in this filter | Not present | Manifest lines 323–330 |
| Explicit `android:exported` attribute | Not present in this activity block | Runtime Android 9 query reports `exported=true` |
| Activity alias used for HOME | Not observed in the inspected manifest | Manifest search |
| Direct-boot-aware | Runtime query reports `false` | `home_query_cmd.txt` |
| System/priv-app | `/system/priv-app/com.amazon.firelauncher` | Package dump |
| User 0 enabled state | `0` / default; installed, not hidden or suspended | Package dump |

## 2. Relevant manifest excerpt

```xml
<activity
    android:name="com.amazon.firelauncher.Launcher"
    android:launchMode="singleTask">
    <intent-filter android:priority="50">
        <action android:name="android.intent.action.MAIN"/>
        <category android:name="android.intent.category.HOME"/>
        <category android:name="android.intent.category.DEFAULT"/>
    </intent-filter>
</activity>
```

The actual manifest includes additional tutorial actions in the same filter. The excerpt is limited to the fields relevant to HOME resolution.

## 3. Priority conclusion

`Confirmed`: priority `50` is declared by the Fire Launcher HOME intent filter in the manifest.

`Not established`: priority 50 is not by itself proof that Amazon modified the resolver or that no preferred activity can ever override it. Android 9 resolver selection considers priority, preferred state, match, and default status; the existing Microsoft `set-home-activity` test remained Fire because Fire was still the effective top candidate on this build.

## 4. Other launcher candidates

The baseline HOME query contains:

| Package/activity | Priority | Runtime status |
|---|---:|---|
| `com.amazon.firelauncher/.Launcher` | 50 | Enabled, exported, selected |
| `com.microsoft.launcher/.Launcher` | 0 | Enabled, exported, candidate |
| `com.android.settings/.FallbackHome` | -1000 | Enabled, direct-boot-aware fallback |

Evidence: `P2-HOME-001`.

This disproves the narrow theory that PackageManager removes every third-party HOME candidate before query results are returned. It does not disprove an additional selection or policy rule after query enumeration.

## 5. Focused code-search result

The inspected Fire Launcher manifest and focused launcher code search establish the HOME declaration and package identity. They do not, by themselves, prove that the launcher app intercepts the hardware Home key or rewrites PackageManager state. Those questions are covered by the system-server and runtime evidence in `findings/home-key-vs-home-intent.md` and `findings/home-preferred-state.md`.
