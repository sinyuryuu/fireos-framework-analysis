# Phase 5AB evidence index

| Evidence ID | Source | File / location | Observation | Interpretation | Confidence |
|---|---|---|---|---|---|
| P5AB-ANDROID-001 | Fixed public LauncherHijack source | HomePress.java, lines 20–33 | Builds ACTION_MAIN + CATEGORY_LAUNCHER, explicit component and launcher flags | Public implementation starts a selected Activity; it does not resolve HOME | 已證實 |
| P5AB-ANDROID-002 | Fixed public LauncherHijack source | HomePress.java, lines 36–50 | Uses PendingIntent.getActivity(...).send() after debounce | PendingIntent is a distinct public background-start boundary | 已證實 |
| P5AB-ANDROID-003 | Fixed public LauncherHijack source | AccServ.java, lines 23–33, 41–67, 80–102 | Observes Fire package, optionally handles HOME key, and calls HomePress.Perform() | Trigger is an Accessibility/event observer, not a system resolver hook | 已證實 |
| P5AB-ANDROID-004 | Fixed public LauncherHijack source | HomeWatcher.java, lines 23–63 | Observes ACTION_CLOSE_SYSTEM_DIALOGS and reason=homekey | Home key observation is separate from HOME resolution | 已證實 |
| P5AB-ANDROID-005 | Fixed public LauncherHijack source | AndroidManifest.xml, lines 6–9, 26–47 | Declares Accessibility, overlay and install-related capabilities | Public project has a broader legacy capability surface than the local safe harness | 已證實 |
| P5AB-LOCAL-001 | Local exact-device evidence | adb/phase4/PHASE4-ACCESSIBILITY-T03/ | Direct startActivity() route produced 0/30 foreground handoffs; Fire remained resumed | The historical implementation is not reliable on this build | 已證實 |
| P5AB-LOCAL-002 | Local source change | tools/phase4-accessibility/src/.../LauncherRedirectService.java | Current source uses explicit PendingIntent.getActivity().send() and retains consent/toggle/guard | A new Android implementation variant is prepared but not measured | 待驗證 |
| P5AB-LOCAL-003 | Exact-device Phase 5 evidence | findings/phase-5aa-android-implementation-review.md, P5E-CMDQ-007 | Pinned mtk-su exact route failed before UID 0 | New wrapper/source review cannot establish exact root compatibility | 已證實 |
| P5AB-SEC-001 | Safety boundary | artifact commands.txt | No install, Accessibility enable, root payload, ioctl, reboot or boot write | Review is host-only | 已證實 |

## Source URLs

- [LauncherHijack fixed repository](https://github.com/BaronKiko/LauncherHijack/tree/f79aee3ddd10c053d6d7c55d6f2fc29436001537)
- [HomePress.java](https://raw.githubusercontent.com/BaronKiko/LauncherHijack/f79aee3ddd10c053d6d7c55d6f2fc29436001537/app/src/main/java/com/baronkiko/launcherhijack/HomePress.java)
- [AccServ.java](https://raw.githubusercontent.com/BaronKiko/LauncherHijack/f79aee3ddd10c053d6d7c55d6f2fc29436001537/app/src/main/java/com/baronkiko/launcherhijack/AccServ.java)
- [HomeWatcher.java](https://raw.githubusercontent.com/BaronKiko/LauncherHijack/f79aee3ddd10c053d6d7c55d6f2fc29436001537/app/src/main/java/com/baronkiko/launcherhijack/HomeWatcher.java)
- [AndroidManifest.xml](https://raw.githubusercontent.com/BaronKiko/LauncherHijack/f79aee3ddd10c053d6d7c55d6f2fc29436001537/app/src/main/AndroidManifest.xml)
