# HOME Resolver Decision Tree

## 1. Observed decision tree

```text
MAIN + HOME query for user 0
  |
  +-- Fire Launcher candidate? -- yes, priority 50, enabled/exported
  |
  +-- Microsoft Launcher candidate? -- yes, priority 0, enabled/exported
  |
  +-- Settings FallbackHome candidate? -- yes, priority -1000
  |
  +-- Preferred record in baseline? -- Fire Launcher ordinary HOME record
  |
  +-- Effective result? -- com.amazon.firelauncher/.Launcher
```

The candidate query result and resolver output are captured in `P2-HOME-001` and the preferred record in `P2-HOME-002`.

## 2. Branch analysis

### Candidate filtering

```text
Are third-party HOME activities returned by query-activities?
  +-- No -> investigate filtering
  +-- Yes -> continue
```

For this build the answer is `Yes`: Microsoft Launcher is returned. Therefore a complete “Amazon removes every third-party HOME candidate” explanation is `Disproved` for the observed query.

Phase 3A adds an important boundary: an APK may declare a positive
`android:priority`, but Android 9 `adjustPriority()` caps a non-privileged
application's effective priority to 0. The five research APKs declared
49/50/51/100 and were all returned at effective priority 0. Fire is a
privileged system package and retains effective priority 50.

### Preferred activity

```text
Is a normal Fire preferred HOME record present?
  +-- Yes -> record exists; compare priority/selection behavior
  +-- No -> investigate manifest/default provisioning
```

The answer is `Yes`. A persistent-preferred record was not observed in the captured dump.

### Priority/ranking

```text
Does Fire have a higher effective priority than ordinary candidates?
  +-- Yes: 50 vs capped third-party 0 -> standard ranking is sufficient as a candidate explanation
  +-- No -> investigate preferred/policy/custom resolver
```

The answer is `Yes`. Phase 3A confirms the normal-app priority cap and shows
that declared priority 51/100 does not change the effective candidate value.
This is the leading explanation for the unchanged result; Amazon's separate
vendor callback remains an unproven HOME-specific influence.

### `set-home-activity`

```text
Does setting Microsoft return success?
  +-- No -> command/API permission or implementation restriction
  +-- Yes -> compare effective resolve and Home behavior
```

The command returned success, but the effective resolver and foreground remained Fire. This narrows the issue to selection semantics/policy rather than a simple shell command rejection.

### Custom resolver/filter

No current evidence proves an Amazon-specific filter that removes Microsoft during final selection. Static PackageManager work must compare the Fire OS `chooseBestActivity`/preferred logic with AOSP and inspect any vendor callback around HOME resolution.

Status: `Hypothesis`; no package-specific resolver branch was found in the
selected Fire VDEX method scan.

### Home-key explicit component path

The inspected normal tablet Home path constructs a standard `ACTION_MAIN` + `CATEGORY_HOME` intent and calls `startActivityAsUser`; it does not contain a Fire Launcher component target. The observed ADB keyevent and explicit HOME intent both result in Fire, which is consistent with resolver selection.

Status: `Strong evidence` for the normal path; a physical button equivalence remains `Hypothesis` until manually sampled.

## 3. Current conclusion

The most economical supported model is:

```text
HOME candidates remain visible
  -> third-party positive priorities are capped to 0 by standard adjustPriority
  -> Fire Launcher declares and retains privileged priority 50
  -> Fire ordinary preferred record is present
  -> effective resolver returns Fire
  -> Home-key standard path and explicit HOME intent converge on that result
```

The Amazon protected-package extension is independently `Confirmed`, but it explains why enabled-state mutation fails; it does not by itself prove that Amazon directly launches Fire for HOME.

## 4. Minimal next tests

1. Obtain an exact-build resolver trace or source-level call path for `chooseBestActivity` and `findPreferredActivity`.
2. Capture a physical Home-key event while unlocked and compare it with the existing `input keyevent 3` trace.
3. If a future `set-home-activity` test is performed, capture the complete preferred and persistent-preferred dumps before, immediately after, after a wait, and after reboot, with a restore script created first.
4. Inspect Amazon vendor PackageManager callbacks for HOME-specific ranking/filtering. Do not infer from the callback class name alone.
