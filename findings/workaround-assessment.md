# No-Root Workaround Assessment

## Summary

No stable no-root method that changes the real HOME default has been confirmed on this build.

| Route | Classification | Reason |
|---|---|---|
| `pm disable-user` Fire package | `Disproved` | Protected-package exception before state mutation |
| `pm`/`cmd package` disable only `.Launcher` | `Disproved` | Same protected gate; existing tests must not be repeated unchanged |
| `cmd package set-home-activity` Microsoft | `Disproved` as an effective default change | Command succeeds and preferred record changes, but effective resolver remains Fire |
| Directly start Microsoft Launcher | `Only a redirect/manual-launch route` | Manual activity start works; it does not change HOME selection |
| Accessibility/notification/foreground redirect | `Only a redirect workaround` | Would act after the Home event and is not a real resolver change; not tested here |
| Settings/DeviceConfig/AppOps/Overlay | `Unknown` | No single causal key or authorized low-risk mutation has been isolated |
| Device Owner | `Potentially viable only with separate provisioning` | May change policy boundaries but usually requires enrollment/reset conditions; not attempted |
| Shizuku/shell alternate Binder route | `Unproven` | An alternate caller still needs an allowed permission/UID; no bypass was established |
| Root/framework/partition modification | `Requires Root / Level 3` | Not executed; requires the separate approval report mandated by the project |

## Preferred Activity conclusion

`Strong evidence`: ordinary preferred-state writes are not sufficient on this device while Fire’s priority-50 candidate remains effective. The write can be visible in `dumpsys package preferred-activities`, yet `resolve-activity` still returns Fire.

This does not prove that every Fire OS 7 build behaves identically. It is a result for the installed PS7330.4104N build and the preserved test conditions.

## What remains plausible

1. Standard Android 9 ranking, combined with the Fire manifest priority 50, may be sufficient to explain the result.
2. Fire OS may modify resolver selection or preferred-activity handling in a path not yet isolated from the VDEX.
3. An Amazon service may rewrite or reassert HOME after the mutation; Phase 3A included reboot persistence but did not perform a long watchdog observation.
4. A permitted API with different semantics (suspend/hide/policy) might have a different boundary, but testing it against core Fire packages requires a verified recovery path and is not justified by the current evidence.

## Recommended next lowest-risk work

- Static comparison of Fire OS `chooseBestActivity` and `findPreferredActivity` against AOSP r1/r61.
- Read-only search of Amazon PackageManager callbacks for HOME-specific code.
- Physical Home-key capture while unlocked.
- Exact-build offline inspection of the deny-list source if an authorized artifact becomes available.

No route in this document should be described as a true launcher replacement unless the resolver, Home key, and reboot-persistence tests all pass.

## Phase 3A priority experiment

The controlled priority variants were built and executed. All normal
sideloaded variants (declared 0/49/50/51/100) were reported by PackageManager
at effective priority 0, while Fire retained effective priority 50. The
matching AOSP/Fire `adjustPriority()` method confirms the standard
non-privileged priority cap.

Classification:

- `Disproved`: a normal ADB-installed priority-51 or priority-100 APK is a
  true HOME replacement on this build.
- `Strong evidence`: ordinary preferred writes and reboot persistence do not
  change the effective HOME while Fire remains the privileged priority-50
  candidate.
- `Unknown`: a privileged/system-signed third-party HOME activity with an
  effective priority above 50; this is outside the no-Root test boundary.
- `Confirmed`: every tested variant restored to Fire and was uninstalled.
