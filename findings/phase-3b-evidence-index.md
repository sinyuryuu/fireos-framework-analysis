# Phase 3B evidence index

All evidence IDs below refer to preserved raw inputs. Hashes are calculated by
this script from the current working tree; missing inputs are reported as
`MISSING` instead of being silently omitted.

## P3B-BASE-001 — canonical device baseline

- Source: device, package, service, settings, overlay, policy and classpath snapshot
- File: `adb/phase3b/PHASE3B-BASELINE-20260803-02/command_manifest.tsv`
- SHA-256: `e1ce292234050167ace2f0f1e0006c1e965165f00f4155544b8f7d58e44ff892`
- Test ID: `PHASE3B-BASELINE-20260803-02`
- Timestamp: recorded in the manifest per command
- Command: the exact ADB invocations are listed in the manifest
- Observed result: required commands completed; optional `pm help`, `cmd package help`,
  HOME role-holder, and `device_config list` were unsupported or unavailable
- Interpretation: canonical read-only baseline; no state mutation
- Confidence: Confirmed
- Related hypothesis: device/build and environment identity

## P3B-PKG-001 — Fire Launcher package identity

- Source: `dumpsys package com.amazon.firelauncher`
- File: `adb/phase3b/PHASE3B-BASELINE-20260803-02/commands/package_dump_com.amazon.firelauncher.stdout.txt`
- SHA-256: `5b5c449a29703cc36fed58aa5980598d0c3c5e8ac3fdcc595c8acb7b5aea6e05`
- Test ID: `PHASE3B-BASELINE-20260803-02`
- Timestamp: command manifest
- Command: `adb -s G001LT0511550CFT shell dumpsys package com.amazon.firelauncher`
- Observed result: `/system/priv-app/com.amazon.firelauncher`, version `1.3.232663.0_82020310`,
  UID `10120`, `privateFlags` includes `PRIVILEGED`, User 0 installed/enabled
- Interpretation: Fire is a privileged system app and not comparable to Phase 3A sideloaded apps
- Confidence: Confirmed
- Related hypothesis: privilege/signature/installation location affects HOME ranking

## P3B-HOME-001 — HOME candidate and resolver result

- Source: `cmd package query-activities` and `resolve-activity`
- File: `adb/phase3b/PHASE3B-BASELINE-20260803-02/commands/home_query_cmd.stdout.txt`,
  `home_resolve_cmd.stdout.txt`
- SHA-256: `1be13029fed592ecfb838026e848c3f80e3201018b8d1b4c550d06f5ccaacbd8`;
  `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6`
- Test ID: `PHASE3B-BASELINE-20260803-02`
- Timestamp: command manifest
- Command: `cmd package query-activities/resolve-activity ... MAIN HOME --user 0`
- Observed result: Fire priority `50`; Microsoft priority `0`; FallbackHome `-1000`; resolver returns Fire
- Interpretation: third-party candidate is not filtered out, but loses current ranking
- Confidence: Confirmed
- Related hypothesis: candidate filtering versus priority

## P3B-PREF-001 — preferred XML and ordinary preferred state

- Source: `preferred-xml` plus full package preferred dump
- File: `adb/phase3b/PHASE3B-BASELINE-20260803-02/commands/preferred_xml.stdout.txt`,
  `preferred_activities.stdout.txt`, `persistent_preferred.stdout.txt`
- SHA-256: `302cf49f4e191a709f8db980787e382dac2ffe6b1794fa1d844e815c901095f3`;
  `610076fd386e1b45283554ae94a0536b62faa51520677bd9c971e2cdcc0a952c`
- Test ID: `PHASE3B-BASELINE-20260803-02`
- Timestamp: command manifest
- Command: `dumpsys package preferred-xml`, `preferred-activities`, and the attempted persistent query
- Observed result: ordinary User 0 Fire HOME record is at
  `preferred_activities.stdout.txt:8874-8885` with `mMatch=0x100000`
  and `mAlways=true`; the attempted persistent-only command returned the same
  ordinary section and exposed no separate active persistent HOME record
- Interpretation: ordinary preferred record exists; persistent negative is bounded by command support
- Confidence: Strong evidence
- Related hypothesis: persistent preferred activity is the overriding mechanism

## P3B-PATH-EXPLICIT-001 — clean explicit HOME path

- Source: sequential HOME path capture
- File: `adb/phase3b/HOME-PATH-EXPLICIT-02/logcat.txt` and `result.md`
- SHA-256: `6e41e22c26bf8958217619f3eee631bc5faa47b601f1769c4b8579cb2698b893`
- Test ID: `HOME-PATH-EXPLICIT-02`
- Timestamp: `metadata.tsv`
- Command: `am start -a android.intent.action.MAIN -c android.intent.category.HOME`
- Observed result: ActivityManager START at `logcat.txt:2158` shows `from uid 2000`,
  standard HOME intent, and explicit `cmp=com.amazon.firelauncher/.Launcher`; the
  matching `am_new_intent` is at `:2160`; final activity/window state is Fire
- Interpretation: explicit HOME test ends at Fire; the log does not identify which earlier layer set cmp
- Confidence: Confirmed
- Related hypothesis: standard resolver versus post-resolution rewrite

## P3B-PATH-KEYEVENT-001 — clean injected Home key path

- Source: sequential HOME key capture
- File: `adb/phase3b/HOME-PATH-KEYEVENT-02/logcat.txt` and `result.md`
- SHA-256: `78af6e9cce76c802a16f7244399daa935b943d9e2b8186187c1c5c0dc0cee2bb`
- Test ID: `HOME-PATH-KEYEVENT-02`
- Timestamp: `metadata.tsv`
- Command: `input keyevent 3`
- Observed result: Input key down/up at `logcat.txt:2177-2181` is followed by
  `am_new_intent` at `:2190` with `MAIN` and explicit Fire component; the clean
  capture has no matching `ActivityManager: START` line, so caller UID and full
  START flags are not inferred from this sample; final activity/window state is Fire
- Interpretation: tested keyevent does not bypass the standard HOME destination in the observed path
- Confidence: Confirmed
- Related hypothesis: Home key direct-launch hook

## P3B-STATIC-PMS-001 — resolver method structure

- Source: Fire OS JADX and matching VDEX-backed source
- File: `decompiled/jadx/systemui/sources/com/android/server/pm/PackageManagerService.java`
- SHA-256: `f0efc633c75524540dd8a5703e5db528bb81ed80c9c49ad34e5cdf4d2078b074`
- Test ID: offline static analysis
- Timestamp: source/decompilation metadata
- Command: `python3 tools/scripts/analyze_phase3b.py --root .`
- Observed result: `chooseBestActivity()` has AOSP-shaped leading priority comparison and only enters ordinary
  preferred selection on the tie path; no selected Fire package-name condition in that scope
- Interpretation: priority 50 explains why a priority-0 preferred record does not win
- Confidence: Strong evidence
- Related hypothesis: Amazon resolver ranking override

## P3B-STATIC-KEYPOLICY-001 — Amazon Home key hooks

- Source: services and private-services VDEX disassembly
- File: `decompiled/baksmali/vdexExtractor/services/disassembly.log`,
  `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`
- SHA-256: `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53`;
  `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Test ID: offline static analysis
- Timestamp: disassembly generation metadata
- Command: offline indexed search and manual smali review
- Observed result: key policy is called before framework Home launch; TabletKeyPolicyManager checks custom-home
  and otherwise permits standard flow; custom-home broadcasts to a permissioned foreground receiver
- Interpretation: Amazon has a real Home-key extension boundary, but no direct Fire component in the inspected methods
- Confidence: Confirmed hook; default Fire override unconfirmed
- Related hypothesis: SystemUI/PhoneWindowManager explicit Fire launch

## P3B-STATIC-DOCK-001 — PhoneWindowManager vendor callback boundary

- Source: services VDEX
- File: `decompiled/baksmali/vdexExtractor/services/disassembly.log:988383-988428`
- SHA-256: `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53`
- Test ID: offline static analysis
- Timestamp: disassembly generation metadata
- Command: offline indexed search and smali review
- Observed result: `startDockOrHome()` calls custom dock callback, on-start callback, then starts `mHomeIntent`
- Interpretation: callback can alter the path; current evidence does not show a Fire-returning callback
- Confidence: Confirmed hook; override unconfirmed
- Related hypothesis: Amazon vendor callback rewrites HOME

## P3B-CONFIG-001 — Amazon service/callback registration

- Source: FOS initialization XML
- File: `artifacts/amazon-services/tabletkeypolicymanager_fosinit.xml`,
  `launcherhijackpreventer_fosinit.xml`, `amazonpackagemanager_fosinit.xml`,
  `amazonactivitymanager_fosinit.xml`
- SHA-256: `a5faec416c32013f267ed58f47b598a0f715c4e49606d99affb0367931f02118`;
  `026a1efce008ef99cc2afa32a9bc8913bf929e74256af67971f426a97c968eea`
- Test ID: offline static analysis
- Timestamp: artifact manifest
- Command: XML inspection
- Observed result: key-policy, ActivityManager, PackageManager, and LauncherHijackPreventer callback registrations
- Interpretation: these are candidate control layers, not proof of runtime HOME rewriting
- Confidence: Confirmed registrations; causal role unknown
- Related hypothesis: Amazon private service/watchdog
