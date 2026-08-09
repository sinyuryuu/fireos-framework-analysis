# Phase 6MB bounded static-search summary

Input APK: `base.apk`

Commands:

```sh
strings artifacts/phase6mb-vending-static-20260810-01/base.apk | rg -n -i 'com\\.amazon\\.firelauncher|setApplicationEnabledSetting|setComponentEnabledSetting'
rg -n --fixed-strings 'com.amazon.firelauncher' artifacts/phase6mb-vending-jadx-20260810-01/base/sources
rg -n -i 'setApplicationEnabledSetting|setComponentEnabledSetting|setPreferredActivity|replacePreferredActivity|addPreferredActivity|startHomeActivity|CATEGORY_HOME|ACTION_MAIN' artifacts/phase6mb-vending-jadx-20260810-01/base/sources --glob '*.java'
python3 tools/scripts/audit_vending_state_writers.py --source-dir artifacts/phase6mb-vending-jadx-20260810-01/base/sources --apk artifacts/phase6mb-vending-static-20260810-01/base.apk --output output/tables/phase6mb-vending-state-writer-scan.csv
```

Observed:

- `com.amazon.firelauncher` had zero literal matches in the APK string scan and zero matches in the generated JADX source tree.
- Package-state setter call sites were found, but they use generic or internally supplied package/component values.
- No `setPreferredActivity`, `replacePreferredActivity`, `addPreferredActivity`, `startHomeActivity`, or HOME-selection writer was identified in the bounded generated source scan.
- `zib.onReceive()` observes `CLOSE_SYSTEM_DIALOGS` with `reason=homekey` only while a Play Store inline-details activity is resumed; its `zoi.k()` path records an internal event and does not start a launcher or write a preferred activity.
- The reproducible host-only script scanned 52,327 generated Java files and found 38 setter call sites; the opaque base-APK scan found zero `com.amazon.firelauncher` byte-string matches.

Interpretation: `com.android.vending` is not currently supported as the Fire Launcher controller. The package-state writers remain generic call sites subject to the system PackageManager gate. The static result does not justify invoking exported components or crafting intents/service calls.
