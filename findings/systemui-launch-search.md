# SystemUI Fire Launcher Reference — Phase 2

## Scope

This finding records the focused search of the device-derived TabletSystemUI sources and the distinction between a Fire Launcher reference and a Home-launch call. It does not claim that every Amazon native or framework path is absent from SystemUI.

## Evidence

`decompiled/jadx/systemui/sources/com/amazon/systemui/SGObserver.java:162-170` obtains the current running task, checks whether the foreground activity is `com.amazon.firelauncher.Launcher`, and then starts an explicit Smart Genie popup:

```text
target package: com.amazon.smartgenie
target activity: com.amazon.smartgenie.ui.EducationalPopupActivity
```

The Fire Launcher string is therefore a conditional observation target for a post-launch Smart Genie action. The inspected code does not construct an explicit `com.amazon.firelauncher/.Launcher` intent and does not handle the Home key.

The focused search also found no direct Fire Launcher component launch in the inspected SystemUI Home/key path. Android framework classes copied into the SystemUI decompilation make this a bounded negative result; the system_server VDEX and Amazon `fosservices` callbacks remain the authoritative sources for framework behavior.

## Determination

`Confirmed observation`: SystemUI contains a Fire Launcher reference in `SGObserver`.

`Confirmed observation`: the referenced launch target in that method is Smart Genie, not Fire Launcher.

`Disproved for inspected path`: the evidence does not support “SystemUI directly launches Fire Launcher on Home.”

`Hypothesis`: an uninspected native, privileged or version-specific component could still launch Fire Launcher. This requires a new positive trace and explicit component evidence.

