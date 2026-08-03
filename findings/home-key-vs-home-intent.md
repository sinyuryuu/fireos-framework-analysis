# Home Key vs Standard HOME Intent

## 1. Test comparison

| Route | Preserved observation | Result | Confidence |
|---|---|---|---|
| Existing ADB `input keyevent 3` from unlocked app | Activity/logcat/window snapshots | Fire Launcher foreground | Confirmed |
| Existing `am start -a android.intent.action.MAIN -c android.intent.category.HOME` | Activity/logcat snapshots | Fire Launcher foreground | Confirmed |
| Existing direct Microsoft Launcher start | Manual component start | Microsoft can be foreground manually | Confirmed |
| Microsoft in foreground, then ADB keyevent | `HOME-PREF-T17` | Fire Launcher foreground | Strong evidence |
| Microsoft target via `set-home-activity`, then explicit HOME | Existing controlled tests | Fire Launcher foreground | Strong evidence |
| Phase 3A research APK explicit HOME and `input keyevent 3` | `adb/mutation-tests/HOME-PRIORITY-P49/` through `P100/` | Fire resolver/foreground after each route; final state restored | Strong evidence |
| Physical hardware Home button | Not captured in the preserved tests | Unknown | Hypothesis |

The component-disable tests are not a separate successful Home-key route: their disable requests were rejected before state mutation. Evidence: `P2-STATE-001`, `P2-STATE-002`.

## 2. Fire OS static key path

The extracted Fire OS services VDEX contains this normal short-press path:

```text
PhoneWindowManager.handleShortPressOnHome()
  -> mKeyPolicyManager.handleShortPressOnHome()
       -> normal tablet callback may handle a custom Home event
       -> otherwise returns false
  -> PhoneWindowManager.launchHomeFromHotKey()
  -> startDockOrHome()
  -> optional vendor custom-dock/home callback
  -> startActivityAsUser(ACTION_MAIN + CATEGORY_HOME, UserHandle.CURRENT)
```

Relevant locations:

- `decompiled/baksmali/vdexExtractor/services/disassembly.log:977415-977444` — `PhoneWindowManager.handleShortPressOnHome()` invokes the Amazon key-policy hook and falls through to the normal home launch path when the hook does not handle the event.
- `services/disassembly.log:985822-985850` — `PhoneWindowManager.launchHomeFromHotKey()` handles keyguard/recents and proceeds to dock/home.
- `services/disassembly.log:988383-988465` — `startDockOrHome()` constructs/uses the home intent and starts it as the current user, with vendor callback opportunities.
- `fosservices/disassembly.log:314232-314270` — tablet key-policy custom-home branch.
- `fosservices/disassembly.log:141914-141927` — `KeyPolicyManagerCommon.launchHomeFromHotKey()` constructs `ACTION_MAIN`, adds `CATEGORY_HOME`, adds flags `0x10200000`, and calls `Context.startActivityAsUser(intent, UserHandle.CURRENT)`.

The normal inspected path does not hard-code `com.amazon.firelauncher/.Launcher` at the launch call. It hands a HOME intent to the activity resolver.

Evidence: `P2-KEY-001`.

## 3. Amazon-specific hooks

Amazon does add hooks before the standard launch:

- `TabletKeyPolicyManager.handleShortPressOnHome()` can call `HomeEventHandler.handleCustomHome()` and broadcast a custom-home event when a qualifying foreground app advertises the required receiver/permission.
- The vendor `startDockOrHome` callback can provide a custom dock/home intent in device-specific modes. The inspected Alexa mode branch starts a multimodal Home intent only for mode 1 and does not target Fire Launcher by component.

These are real framework modifications, but they are not evidence that SystemUI directly starts Fire Launcher for the normal observed path.

## 4. SystemUI result

The focused SystemUI search found a Fire Launcher reference in `SGObserver`, but the inspected use detects the current task before starting Smart Genie’s educational popup. It is not a HOME launch call.

Status: `Confirmed` for the inspected observation; `Disproved` as evidence of a direct SystemUI Home launch. This is a bounded negative result, not a proof about every SystemUI class.

## 5. Decision

`Strong evidence`: ADB keyevent and explicit HOME intent converge on the same PackageManager-resolved Fire component in the tested unlocked flows. The current evidence favors a resolver/selection explanation over a SystemUI explicit-component launch.

`Hypothesis`: the physical hardware button follows the same input policy path. A manually operated physical-button sample is the minimum remaining black-box check.
