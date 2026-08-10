# Phase 6QC-B — ASP/Audio permission-to-sink closure (exact PS7331)

Scope: host-only static analysis of the preserved Fire OS PS7331 VDEX/disassembly and saved read-only artifacts. No device access was performed by this worker; no Binder/broadcast/settings/APK/root/OTA/reboot operation was performed. Existing user changes were preserved.

## Executive result

The ASP tablet branch is a real static authorization anomaly candidate, but it is not an exploit finding. In the exact disassembly, `AmazonAspService$BinderService.hasCallerGotPermission()` returns `true` immediately when `ro.build.configuration == "tablet"`; only the non-tablet branch checks `com.amazon.permission.ASP_PERMISSION`. The saved PS7331 tablet runtime nevertheless denied shell UID 2000 with `-13/EACCES` before `nativeCommand`, so the static branch and the observed runtime result must be kept separate rather than collapsed into an exploit claim.

`AmazonAudioService` has no matching tablet/device-family permission short-circuit. Its mutating methods use explicit Android/Amazon signature-or-privileged permission checks (or `checkCallingOrSelfPermission`/`checkCallingPermission`) and some then clear identity. Its sinks are audio routing, volume, Dolby/audio settings, HDMI/audio capability, and native/HAL-adjacent state. No production path in the reviewed corpus reaches PackageManager package state, HOME resolver/preferred activity, system/root credential state, APK install, or OTA/reboot from these two services.

## Exact static findings

### AmazonAspService

- Path: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`
- `BinderService.hasCallerGotPermission()`: lines 82014–82063; method offset `05c9f2` / exact branch body around `05ca9e–05cb5e`.
- Permission: `com.amazon.permission.ASP_PERMISSION`; exact tablet branch returns `true` at `05cab4–05cab8`, before the permission check at `05caca`; non-tablet branch invokes `Context.checkCallingPermission` and returns its result. Do not infer exploitability from the branch alone.
- Callers: `command(I,[B,[B)I` lines 82064–82077; `setActiveInputSource` 82238–82261; `startCapture` 82262–82280; `startInjection` 82281–82305; `startIrCodeDetection` 82306–82317; `stopCapture` 82318–82331; `stopInjection` 82332–82345. Each uses the helper before native/audio operation in the reviewed body.
- Identity: no `Binder.clearCallingIdentity()` in the reviewed ASP guard/method bodies.
- Publication: `onStart()` lines 82734–82746, exact offset `05d3c6–05d3f0`: publishes Binder name `audiosignalprocessor`, then local service and native ASP initialization.
- Sink: `nativeCommand`, `nativeSetActiveInputSource`, capture/injection/IR native methods, callback/listener and audio-volume notification paths. No `PackageManager`, `IPackageManager`, `ActivityManager/ATMS`, preferred-HOME, package-state writer, credential/root, APK, OTA, or reboot sink found in the reviewed ASP class/callers.
- Runtime evidence already saved: `adb/phase6bv/PHASE6BV-ASP-RO-20260805-01/`; `id.txt` records shell UID 2000, `getenforce.txt` records Enforcing, `service_check.txt` records service found, `probe.txt` records method result `-13`, and `logcat_asp.txt` records caller permission denial. `home_after.txt` and before/after dumps are preserved. This is read-only evidence, not a new probe.

### AmazonAudioService

- Path: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`
- Service class/Binder: lines 46739 onward / class `AmazonAudioService.BinderService`; Binder publication `onStart()` lines 48974–48989, exact offset `03eddc–03edf8`, service name from `com.amazon.media.AmazonAudioManager.SERVICE_NAME` (`amazonaudioservice`).
- Device-family branch: no `hasCallerGotPermission()` equivalent and no tablet-specific unconditional authorization branch found in the class. The only platform branches observed are feature/television/Fire-TV/audio-port behavior, not permission bypasses.
- Permissions and methods: `adjustStreamVolumeOnDevice` (46907–47004) uses `MODIFY_AUDIO_SETTINGS` through the service-side check plus calling UID; `enableDualOutput` (47005–47047) checks `com.amazon.permission.FORCE_SIMULTANEOUS_AUDIO_OUTPUT`; `getDolbyDapEnabled` (47217–47229), `setDolbyDapEnabled` (47830–47843), `setDolbyWithoutDeathNotifier` (47844–47879), `setForceDeviceRouting` (47880–47904), and related audio setters use `MODIFY_AUDIO_SETTINGS`; `setAudioRoutingMode` (47765–47829) uses `MODIFY_AUDIO_ROUTING`; `setForceUse` (47905–47992) uses `com.amazon.permission.AUDIO_FORCE_USE`; `getPackageInFocus` (47317–47329) uses `PACKAGE_USAGE_STATS` and reads focus only; `setAudioMute` (47685–47714), `setAudioOutputFormat` (47715–47764), and `setSpeakerMute` (48018–48050) include permission enforcement and `clearCallingIdentity`.
- Identity: `clearCallingIdentity` is present in the three methods above and in the audio-capability update path; corresponding restore calls are present in the bounded methods. Identity clearing occurs after permission/argument checks and leads to audio service/capability operations, not package/HOME/root state.
- Sink inventory: `AudioSystem.setForceUse`, AudioService volume/routing, `AudioSettings`, `AudioCapabilities.updateAudioCapabilitiesFromUI`, Dolby state/death tracking, HDMI/audio encoding hints, and audio/native resource state. `getPackageInFocus` is a read-only package-name observation, not a package writer.
- Negative sink review: no call to `PackageManager.set*`, `IPackageManager` package/component/preferred-HOME setters, `ActivityTaskManager`, `startActivity` for HOME, root/credential/SELinux mutation, APK install, OTA updater, reboot, or system-property write was found in the class and its direct API facade paths.

## Production caller inventory

The preserved framework implementation exposes `AmazonAudioManager` as the production client facade. Its service lookup is `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:9120–9202`, using literal service name `amazonaudioservice` and `ServiceManager.getService`. The facade methods dispatch to `IAmazonAudioManager` at offsets/callsites including `adjustStreamVolumeOnDevice` `078bba–078c02`, `enableDualOutput` `078298–0782c6`, `filterDevices` `078b16–078b32`, `getAdvancedAudioSettingState` `0782e6–078304`, `getDolbyDapEnabled` `078332–078350`, `getDualOutputDevices` `0786ae–0786cc`, `getPackageInFocus` `078ab4–078ad0`, `getStreamVolumeOnDevice` `07874a–078768`, `getSystemSettingsData` `078386–0783a4`, `setAudioRoutingMode`/related setters in the same facade class, and observer registration/acquisition methods through `078d1c` onward. A corpus-wide search of the preserved `boot-fosframework` and `fosservices` disassemblies found no direct production caller of the Binder service outside this facade/system-server integration surface. This establishes caller shape, not live reachability for arbitrary apps.

## Closest higher-privilege writer in the same anomaly family

The closest reviewed service is `AmazonActivityManagerService.BinderService.preWarmApplicationForUser(String,int,int)`, not either audio service. Exact path `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:preWarmApplicationForUser` lines 40453–40534, offsets `036f0c–037036`: it checks `com.amazon.permission.APP_PREWARM` at `036f4a–036f5c`, then calls `Binder.clearCallingIdentity()` at `036f5c`, and reaches `SystemJumpTable$ActivityManagerService.startProcessLocked` at `036fc8`; identity is restored at `03702a`. This is a process-start/prewarm sink, not a package/HOME/root writer in the bounded body. It is therefore the nearest high-impact identity-clearing service candidate, but it is not evidence that ASP/Audio can pivot to it. No transaction was sent.

## SELinux/publication/runtime boundary

Static publication is proven by the two `onStart()` bodies above. Saved runtime service evidence proves `amazonaudioservice` was listed and ASP `audiosignalprocessor` was found in prior read-only captures. Saved PS7331 runtime evidence records SELinux `Enforcing` and shell context. The workspace contains the ASP init path `/system/fireos/etc/init/amazonaspservice_fosinit.xml` in the saved filesystem manifest. A complete OEM `service_contexts` mapping for these names is not present in the preserved host artifacts; therefore this report does not claim a source-level SELinux allow rule. The safe conclusion is publication + observed service-manager/SELinux boundary, with policy mapping completeness remaining an artifact gap.

## Status and safe next step

Status: `STATIC_CANDIDATE_CLOSED_FOR_EXPLOIT_CLAIM`; ASP anomaly is confirmed as a code-review candidate, current tablet runtime denial is already saved, AudioService sink closure is static-only, and no package/HOME/system/root sink is demonstrated.

Next safe step: if further assurance is required, perform only a host-side completeness/hash cross-check of the exact PS7331 VDEX, native symbol inventory, and OEM SELinux `service_contexts`/`te` artifacts. Do not send new Binder calls, broadcasts, settings writes, APKs, or native audio operations. A non-tablet product comparison would require a separately identified signed build and a new safety review.

## Evidence hashes

`fosservices/disassembly.log` SHA-256 `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`; `boot-fosframework/disassembly.log` SHA-256 `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`; `artifacts/phase6q/binder-service-audit-20260805-03/binder-method-candidates.csv` SHA-256 `d72839a9a936d8f338f5496f62f960b6e91b00501ffbb05069ef8088a6e050b7`; runtime directory manifest `adb/phase6bv/PHASE6BV-ASP-RO-20260805-01/sha256sums.txt` SHA-256 `5127e7a16039556ce825165d97c787f9f7a2512e7a33a2834ddf618c54c97673`.
