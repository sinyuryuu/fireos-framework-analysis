# HOME Preferred and Persistent-Preferred State

## 1. Baseline preferred record

The preserved baseline `dumpsys package preferred-activities` contains a User 0 HOME record:

```text
Preferred Activities User 0:
  Non-Data Actions:
    android.intent.action.MAIN
      ... com.amazon.firelauncher/.Launcher
      mMatch=0x100000 mAlways=false
      categories: android.intent.category.HOME, android.intent.category.DEFAULT
```

Source: `adb/baseline/BASELINE-20260803-07/preferred_activities.txt:8874-8883`.

Evidence: `P2-HOME-002`.

The `mAlways=false` value is recorded exactly as dumped. It should not be silently relabeled as a persistent preferred activity.

## 2. Persistent preferred activity

No explicit `Persistent Preferred Activities` heading was observed in the inspected baseline dump. This supports:

- `Strong evidence`: an ordinary Fire HOME preferred record exists.
- `Hypothesis`: no persistent-preferred record was active in the captured dump.
- `Unknown`: absence of a matching heading in one dump is not a universal proof that no policy or runtime service can install one later.

The current evidence does not justify the statement that Fire is fixed by a DevicePolicy persistent-preferred activity.

## 3. HOME candidates

The query result contains all three relevant candidates:

```text
com.amazon.firelauncher/.Launcher  priority=50
com.microsoft.launcher/.Launcher   priority=0
com.android.settings/.FallbackHome priority=-1000
```

Therefore the third-party launcher is still visible to PackageManager query enumeration. Candidate filtering is not required to explain the baseline result.

Evidence: `P2-HOME-001`.

## 4. Existing preferred-activity mutation

`HOME-PREF-T17` executed:

```text
cmd package set-home-activity com.microsoft.launcher/.Launcher
```

The command output was `Success` (exit status 0). The subsequent resolver still reported:

```text
priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
com.amazon.firelauncher/.Launcher
```

The immediately following preferred-activities dump did contain a Microsoft record:

```text
android.intent.action.MAIN:
  com.microsoft.launcher/.Launcher
  mMatch=0x100000 mAlways=true
```

The `Selected from` list still contained Fire, Microsoft, and Settings FallbackHome. This is why the mutation is evidence that the preferred record can be written, but not evidence that the effective HOME resolver follows it on this build.

The following Home key action also resumed Fire Launcher. The restore command:

```text
cmd package set-home-activity com.amazon.firelauncher/.Launcher
```

also returned `Success`, and the final state was the original Fire state.

Evidence: `P2-HOME-003`.

### Interpretation

`Strong evidence`: this API call can return success without changing the effective HOME resolver on this build when Microsoft is the target.

`Not proven`: this does not distinguish between all possible causes, including Android priority ordering, an Amazon PackageManager/resolver modification, a persistent policy restored outside the captured record, or an implementation detail of `set-home-activity`. The static Android 9 control flow makes the priority-50 explanation plausible, but the OEM-specific path must be validated against the exact Fire OS implementation.

## 5. Device policy

The existing policy evidence records `com.amazon.parentalcontrols` as a User 0 Profile Owner and no Device Owner. The Fire Launcher is not the owner package. The owner-protection branch remains a framework possibility for other packages/users, but it is not the observed explanation for the shell error, which occurs in the PackageManager protected gate with the shell UID.

Evidence: `P2-DPM-001`, `P2-STATIC-001`, `P2-STATIC-004`.

## 6. Answers to the Phase 2 questions

| Question | Current answer | Confidence |
|---|---|---|
| Is there an ordinary preferred HOME record? | Yes, Fire Launcher User 0 | Confirmed |
| Is a persistent preferred record present? | Not observed in the baseline dump | Hypothesis / not confirmed |
| Are third-party HOME candidates still listed? | Yes, Microsoft and Settings fallback | Confirmed |
| Does `set-home-activity` report success for Microsoft? | Yes | Confirmed |
| Does that request change effective resolver? | No in the preserved test | Strong evidence |
| Is the failure solely because of priority 50? | Plausible, but not isolated from OEM behavior | Probable |
| Is a DevicePolicy persistent preferred HOME the cause? | Not supported by current evidence | Disproved for the observed cause; policy remains a separate unknown |
