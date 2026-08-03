# Phase 3C snapshot comparison

- Before: `adb/phase3c/PHASE3C-PREFERRED-P0-02/before`
- After: `adb/phase3c/PHASE3C-PREFERRED-P0-02/after_reboot`
- Before files: `175`
- After files: `175`
- Changed files: `27`

## Changed files

- `activity/activities.stdout.txt` — changed
- `activity/recents.stdout.txt` — changed
- `activity/top.stdout.txt` — changed
- `appops/all.stdout.txt` — changed
- `appops/firelauncher.stdout.txt` — changed
- `appops/microsoft.stdout.txt` — changed
- `appops/test_p0.exit_code.txt` — changed
- `appops/test_p0.stderr.txt` — changed
- `appops/test_p0.stdout.txt` — changed
- `devices.stdout.txt` — changed
- `metadata.tsv` — changed
- `overlay/dump.stdout.txt` — changed
- `package/all_packages.stdout.txt` — changed
- `package/firelauncher.stdout.txt` — changed
- `package/full_dump.stdout.txt` — changed
- `package/home_query_cmd.stdout.txt` — changed
- `package/home_query_pm.stdout.txt` — changed
- `package/persistent_preferred.stdout.txt` — changed
- `package/preferred_activities.stdout.txt` — changed
- `package/preferred_xml.stdout.txt` — changed
- `properties/getprop.stdout.txt` — changed
- `settings/global.stdout.txt` — changed
- `summary.md` — changed
- `users/dumpsys_user.stdout.txt` — changed
- `window/input.stdout.txt` — changed
- `window/processes.stdout.txt` — changed
- `window/windows.stdout.txt` — changed

## Focused evidence

### `activity/activities.stdout.txt`

```text
4:   Stack #0: type=home mode=fullscreen
12:     * TaskRecord{55bad2e #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
14:       affinity=10120:com.amazon.firelauncher
15:       intent={act=android.intent.action.MAIN cat=[android.intent.category.HOME] flg=0x10000100 cmp=com.amazon.firelauncher/.Launcher}
16:       realActivity=com.amazon.firelauncher/.Launcher
19:       Activities=[ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}]
21:       mRootProcess=ProcessRecord{660f0cf 1919:com.amazon.firelauncher/u0a120}
24:       * Hist #0: ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}
25:           packageName=com.amazon.firelauncher processName=com.amazon.firelauncher
27:           app=ProcessRecord{660f0cf 1919:com.amazon.firelauncher/u0a120}
28:           Intent { act=android.intent.action.MAIN cat=[android.intent.category.HOME] flg=0x10000100 cmp=com.amazon.firelauncher/.Launcher }
29:           frontOfTask=true task=TaskRecord{55bad2e #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
30:           taskAffinity=10120:com.amazon.firelauncher
31:           realActivity=com.amazon.firelauncher/.Launcher
32:           baseDir=/system/priv-app/com.amazon.firelauncher/com.amazon.firelauncher.apk
33:           dataDir=/data/user/0/com.amazon.firelauncher
34:           stateNotNeeded=false componentSpecified=false mActivityType=home
38:            mOverrideConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
39:           CurrentConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
40:           OverrideConfiguration={0.0 ?mcc?mnc ?localeList ?layoutDir ?swdp ?wdp ?hdp ?density ?lsize ?long ?ldr ?wideColorGamut ?orien ?uimode ?night ?touch ?keyb/?/? ?nav/? winConfig={ mBounds=Rect(0, 0 - 0, 0) mAppBounds=null mWindowingMode=undefined mActivityType=home}}
51:           mActivityType=home
57:       TaskRecord{55bad2e #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
58:         Run #0: ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}
60:     mLastPausedActivity: ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}
64:     TaskRecord{55bad2e #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
65:       Sleep #0: ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}
67:   ResumedActivity: ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}
68:   mFocusedStack=ActivityStack{fbfca5c stackId=0 type=home mode=fullscreen visible=true translucent=false, 1 tasks} mLastFocusedStack=ActivityStack{fbfca5c stackId=0 type=home mode=fullscreen visible=true translucent=false, 1 tasks}
73:    mHomeStack=ActivityStack{fbfca5c stackId=0 type=home mode=fullscreen visible=true translucent=false, 1 tasks}
74:   isHomeRecentsComponent=false  KeyguardController:
```

### `activity/recents.stdout.txt`

```text
3: mRecentsComponent=ComponentInfo{com.android.launcher3/com.android.quickstep.RecentsActivity}
5:   * Recent #0: TaskRecord{55bad2e #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
7:     affinity=10120:com.amazon.firelauncher
8:     intent={act=android.intent.action.MAIN cat=[android.intent.category.HOME] flg=0x10000100 cmp=com.amazon.firelauncher/.Launcher}
9:     realActivity=com.amazon.firelauncher/.Launcher
12:     Activities=[ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}]
14:     mRootProcess=ProcessRecord{660f0cf 1919:com.amazon.firelauncher/u0a120}
21:     origActivity=com.android.settings/.Settings
22:     realActivity=com.android.settings/.Settings
```

### `activity/top.stdout.txt`

```text
1: TASK 10120:com.amazon.firelauncher id=2 userId=0
2:   ACTIVITY com.amazon.firelauncher/.Launcher f7a5258 pid=1919
6:       mCurrentConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
31:       Message 1: { when=-223ms what=0 target=com.amazon.firelauncher.templatedatasources.LauncherCdaClient$MainHandler isAsync=false }
32:       Message 2: { when=-214ms what=0 target=com.amazon.firelauncher.templatedatasources.LauncherCdaClient$MainHandler isAsync=false }
33:       Message 3: { when=-202ms what=1 obj=com.amazon.firelauncher.DemoFlagObserverHandler$DemoFlagObserverClient@1ea9037 target=com.amazon.firelauncher.DemoFlagObserverHandler isAsync=false }
35:       Message 5: { when=-175ms callback=com.amazon.firelauncher.search.SearchAppWidgetManager$4 target=android.os.Handler isAsync=false }
36:       Message 6: { when=-174ms callback=com.amazon.firelauncher.ads.AdImpressionHistory$3$1 target=android.os.Handler isAsync=false }
37:       Message 7: { when=-148ms callback=com.amazon.firelauncher.appsgrid.manager.AppManager$2 target=android.os.Handler isAsync=false }
42:       Message 12: { when=-7ms callback=com.amazon.firelauncher.Launcher$2$1 target=android.os.Handler isAsync=false }
43:       Message 13: { when=-7ms callback=com.amazon.firelauncher.Launcher$2$1 target=android.os.Handler isAsync=false }
44:       Message 14: { when=+2s130ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
45:       Message 15: { when=+2s156ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
46:       Message 16: { when=+2s293ms callback=com.amazon.firelauncher.weblab.DelayedWeblabController$2 target=android.os.Handler isAsync=false }
47:       Message 17: { when=+2s313ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
48:       Message 18: { when=+2s314ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
49:       Message 19: { when=+2s314ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
50:       Message 20: { when=+2s324ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
51:       Message 21: { when=+2s327ms callback=com.amazon.firelauncher.Launcher$OffScreenRunnable target=android.os.Handler isAsync=false }
52:       Message 22: { when=+2s446ms callback=com.amazon.firelauncher.services.DefaultMapCache$5 target=android.os.Handler isAsync=false }
53:       Message 23: { when=+2s493ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
54:       Message 24: { when=+2s645ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
55:       Message 25: { when=+2s671ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
56:       Message 26: { when=+2s815ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
57:       Message 27: { when=+2s843ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
58:       Message 28: { when=+4s852ms callback=com.amazon.firelauncher.metrics.drawn.DelayedMetricCallbackQueue$1 target=android.os.Handler isAsync=false }
66:       context: com.amazon.firelauncher.Launcher@5653290
67:       client: com.amazon.firelauncher.Launcher@5653290
```

### `appops/all.stdout.txt`

```text
700:     Package com.android.launcher3:
982:     Package com.amazon.firelauncher:
1274:     Package com.microsoft.launcher:
```

### `package/all_packages.stdout.txt`

```text
36: package:/system/priv-app/com.amazon.firelauncher/com.amazon.firelauncher.apk=com.amazon.firelauncher
73: package:/data/app/com.microsoft.launcher-bTT5nKLHn89n_d_gJojj-Q==/base.apk=com.microsoft.launcher
75: package:/system/priv-app/com.android.launcher3/com.android.launcher3.apk=com.android.launcher3
155: package:/data/app/org.fireosresearch.home.p0-Er8RUFCd6pl-r5QmHpD9PQ==/base.apk=org.fireosresearch.home.p0
184: package:/system/priv-app/com.amazon.tv.launcher/com.amazon.tv.launcher.apk=com.amazon.tv.launcher
```

### `package/firelauncher.stdout.txt`

```text
4:         f0c836e com.amazon.firelauncher/.Launcher filter 74a033a
8:           Authority: "com.amazon.firelauncher": -1
11:       com.amazon.firelauncher.REQUEST_LOCATION_PERMISSION:
12:         f0c836e com.amazon.firelauncher/.Launcher filter e8b2a65
13:           Action: "com.amazon.firelauncher.REQUEST_LOCATION_PERMISSION"
15:       com.amazon.firelauncher.intent.action.TUTORIALDONE:
16:         f0c836e com.amazon.firelauncher/.Launcher filter 247175c
18:           Action: "com.amazon.firelauncher.intent.action.ALEXA_TUTORIAL"
19:           Action: "com.amazon.firelauncher.intent.action.TUTORIAL"
20:           Action: "com.amazon.firelauncher.intent.action.TUTORIALDONE"
21:           Category: "android.intent.category.HOME"
23:           mPriority=50, mOrder=0, mHasPartialTypes=false
24:       com.amazon.firelauncher.intent.action.ALEXA_TUTORIAL:
25:         f0c836e com.amazon.firelauncher/.Launcher filter 247175c
27:           Action: "com.amazon.firelauncher.intent.action.ALEXA_TUTORIAL"
28:           Action: "com.amazon.firelauncher.intent.action.TUTORIAL"
29:           Action: "com.amazon.firelauncher.intent.action.TUTORIALDONE"
30:           Category: "android.intent.category.HOME"
32:           mPriority=50, mOrder=0, mHasPartialTypes=false
34:         f0c836e com.amazon.firelauncher/.Launcher filter 247175c
36:           Action: "com.amazon.firelauncher.intent.action.ALEXA_TUTORIAL"
37:           Action: "com.amazon.firelauncher.intent.action.TUTORIAL"
38:           Action: "com.amazon.firelauncher.intent.action.TUTORIALDONE"
39:           Category: "android.intent.category.HOME"
41:           mPriority=50, mOrder=0, mHasPartialTypes=false
42:         e93433 com.amazon.firelauncher/.LauncherUserSettings filter 5b3beb
47:         e93433 com.amazon.firelauncher/.LauncherUserSettings filter 5b3beb
51:       com.amazon.firelauncher.intent.action.TUTORIAL:
52:         f0c836e com.amazon.firelauncher/.Launcher filter 247175c
54:           Action: "com.amazon.firelauncher.intent.action.ALEXA_TUTORIAL"
55:           Action: "com.amazon.firelauncher.intent.action.TUTORIAL"
56:           Action: "com.amazon.firelauncher.intent.action.TUTORIALDONE"
57:           Category: "android.intent.category.HOME"
59:           mPriority=50, mOrder=0, mHasPartialTypes=false
64:         5b5d32c com.amazon.firelauncher/com.amazon.fireappscardproducer.service.SystemNotificationProducerService$PackageRecencyReceiver filter 816e03d
68:         7ec1548 com.amazon.firelauncher/.reccardproducer.ProducerService$MusicUnlimitedRegistrationReceiver filter f2f5ed7
71:         8cf43c6 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.CardActionService$RemoveFromDeviceReceiverOld filter 8bcc183
73:       com.amazon.cmsfirecardproducer.REMOVE_FROM_HOME:
74:         236b911 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.CardActionService$RemoveFromHomeReceiverOld filter 63e4032
75:           Action: "com.amazon.cmsfirecardproducer.REMOVE_FROM_HOME"
76:       com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_APPS:
77:         a00bf98 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.CardActionService$RemoveFromHomeReceiver filter 9a67f00
78:           Action: "com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_APPS"
79:           Action: "com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_GAMES"
80:       com.amazon.firelauncher.appmanager.APPS_REMOVED:
81:         62c670 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$PackageChangeReceiver filter a4cfa6
82:           Action: "com.amazon.firelauncher.appmanager.APPS_ADDED"
83:           Action: "com.amazon.firelauncher.appmanager.APPS_REMOVED"
84:           Action: "com.amazon.firelauncher.appmanager.APPS_UPDATED"
85:           Action: "com.amazon.firelauncher.APP_RECENCY_REBUILD"
87:         ed3c946 com.amazon.firelauncher/.ui.GlobalSyncReceiver filter 3d53cf6
89:         9a43707 com.amazon.firelauncher/com.amazon.heroshoveler.weather.WeatherRefreshService$GlobalSyncReceiver filter 6a218f7
91:         a19c034 com.amazon.firelauncher/.cardproducer.LauncherProducerService$GlobalSyncReceiver filter 5ed8fda
93:         1bede5d com.amazon.firelauncher/com.amazon.hintscardproducer.HintsCardRefreshService$GlobalSyncReceiver filter c2319e2
96:         a4c3582 com.amazon.firelauncher/.images.storage.LowStorageReceiver filter f7ac82a
98:       com.amazon.firelauncher.appmanager.APPS_ADDED:
99:         62c670 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$PackageChangeReceiver filter a4cfa6
100:           Action: "com.amazon.firelauncher.appmanager.APPS_ADDED"
101:           Action: "com.amazon.firelauncher.appmanager.APPS_REMOVED"
102:           Action: "com.amazon.firelauncher.appmanager.APPS_UPDATED"
103:           Action: "com.amazon.firelauncher.APP_RECENCY_REBUILD"
104:       com.amazon.firelauncher.START_EDIT_MODE_EXTERNAL:
105:         fa0dd8 com.amazon.firelauncher/.appsgrid.StartEditModeReceiver filter 548591
106:           Action: "com.amazon.firelauncher.START_EDIT_MODE_EXTERNAL"
107:           mPriority=100, mOrder=0, mHasPartialTypes=false
109:         d850e87 com.amazon.firelauncher/com.amazon.firecard.deviceclient.clients.MultiplexingMessageReceiver filter 496dc0b
112:           Category: "com.amazon.firelauncher"
113:       com.amazon.firelauncher.action.REC_SUPPRESS:
114:         18f302 com.amazon.firelauncher/.reccardproducer.ProducerService$ItemSuppressionReceiver filter e39a38a
115:           Action: "com.amazon.firelauncher.action.REC_SUPPRESS"
116:       com.amazon.firelauncher.action.UPSELL_TAPPED_NOTIFICATION:
117:         29c5c67 com.amazon.firelauncher/.reccardproducer.ProducerService$UpsellTappedNotificationReceiver filter 1966e56
118:           Action: "com.amazon.firelauncher.action.UPSELL_TAPPED_NOTIFICATION"
120:         a7de012 com.amazon.firelauncher/com.amazon.identity.auth.accounts.SessionUserChangedToAccountForPackageChangedAdpater filter e7151cf
122:       com.amazon.firelauncher.action.WEBLAB_UPDATE:
123:         93ee43b com.amazon.firelauncher/.reccardproducer.ProducerService$UpNextWeblabUpdateReceiver filter 4402071
124:           Action: "com.amazon.firelauncher.action.WEBLAB_UPDATE"
126:         3f29104 com.amazon.firelauncher/com.amazon.heroshoveler.weather.RefreshCardsBroadcastReceiver filter 2903282
128:         38f26ed com.amazon.firelauncher/.cardproducer.LauncherProducerService$RefreshCardsReceiver filter 1fd2fef
131:         a1df922 com.amazon.firelauncher/com.amazon.firecard.deviceclient.CloudCardEventService$RefreshCardsReceiver filter 6c93ae8
133:         2f79fb3 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$RefreshCardsReceiver filter b10f501
135:         d89b970 com.amazon.firelauncher/.reccardproducer.ProducerService$RefreshCardsReceiver filter 1fff2df
137:         6c444e9 com.amazon.firelauncher/com.amazon.hintscardproducer.HintsCardRefreshService$RefreshCardsReceiver filter f6552ad
139:       com.amazon.firelauncher.action.FOR_YOU_CHANNEL_VISIBLE:
140:         bf65ea0 com.amazon.firelauncher/com.amazon.heroshoveler.weather.WeatherRefreshBroadcastReceiver filter 9a701d0
141:           Action: "com.amazon.firelauncher.action.FOR_YOU_CHANNEL_VISIBLE"
142:         87b3a59 com.amazon.firelauncher/.cardproducer.LauncherProducerService$ChannelVisibilityChangeReceiver filter 6c88585
143:           Action: "com.amazon.firelauncher.action.FOR_YOU_CHANNEL_VISIBLE"
144:         215261e com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$ChannelVisibilityChangeReceiver filter f8c2d7e
145:           Action: "com.amazon.firelauncher.action.FOR_YOU_CHANNEL_VISIBLE"
147:         b335ef com.amazon.firelauncher/.cardproducer.LauncherProducerService$AccountChangeReceiver filter f426afc
151:         db6502e com.amazon.firelauncher/com.amazon.heroshoveler.weather.WeatherRefreshService$LocaleChangedReceiver filter caa1364
153:         4a257cf com.amazon.firelauncher/amazon.alexa.locale.AlexaLocaleHelper filter 612f4ce
155:         38f26ed com.amazon.firelauncher/.cardproducer.LauncherProducerService$RefreshCardsReceiver filter 1fd2fef
158:         8faa55c com.amazon.firelauncher/com.amazon.fireappscardproducer.service.SystemNotificationProducerService$LocaleChangeReceiver filter f6b1d94
160:         242a065 com.amazon.firelauncher/.reccardproducer.ProducerService$LocaleChangedReceiver filter d0ed9f5
162:         65b413a com.amazon.firelauncher/com.amazon.hintscardproducer.HintsCardRefreshService$LocaleChangedReceiver filter 3a11173
164:       com.amazon.firelauncher.action.TAB_SETTINGS_CHANGED:
165:         d5a6cf2 com.amazon.firelauncher/.reccardproducer.ProducerService$TabSuppressionReceiver filter 51addfb
166:           Action: "com.amazon.firelauncher.action.TAB_SETTINGS_CHANGED"
167:       com.amazon.firelauncher.action.HOST_APP_COLD_START_ACTION:
168:         93f5bb2 com.amazon.firelauncher/.reccardproducer.ProducerService$ColdStartReceiver filter 75b13c4
169:           Action: "com.amazon.firelauncher.action.HOST_APP_COLD_START_ACTION"
170:         b967703 com.amazon.firelauncher/com.amazon.hintscardproducer.HintsCardRefreshService$ColdStartReceiver filter 6316ca9
171:           Action: "com.amazon.firelauncher.action.HOST_APP_COLD_START_ACTION"
173:         9865a9d com.amazon.firelauncher/com.amazon.identity.auth.device.storage.LambortishClock$ChangeTimestampsBroadcastReceiver filter 5dcf22e
175:       com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_GAMES:
176:         a00bf98 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.CardActionService$RemoveFromHomeReceiver filter 9a67f00
177:           Action: "com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_APPS"
178:           Action: "com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_GAMES"
179:       com.amazon.firelauncher.APP_RECENCY_REBUILD:
180:         62c670 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$PackageChangeReceiver filter a4cfa6
181:           Action: "com.amazon.firelauncher.appmanager.APPS_ADDED"
182:           Action: "com.amazon.firelauncher.appmanager.APPS_REMOVED"
183:           Action: "com.amazon.firelauncher.appmanager.APPS_UPDATED"
184:           Action: "com.amazon.firelauncher.APP_RECENCY_REBUILD"
185:       com.amazon.firelauncher.action.RECENCY_UPDATE:
186:         98fc6f4 com.amazon.firelauncher/.reccardproducer.ProducerService$RecencyUpdateReceiver filter 7352e18
187:           Action: "com.amazon.firelauncher.action.RECENCY_UPDATE"
189:         d850e87 com.amazon.firelauncher/com.amazon.firecard.deviceclient.clients.MultiplexingMessageReceiver filter 496dc0b
```

### `package/full_dump.stdout.txt`

```text
149:   android.software.home_screen
238:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
247:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
250:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
252:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
258:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
267:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
272:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher
275:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
300:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
303:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
305:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
314:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
319:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
322:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
327:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
330:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
337:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
343:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
348:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
351:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
353:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
356:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
357:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
363:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
364:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
367:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
368:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
371:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
372:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
379:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
382:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
385:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
386:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
393:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
396:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
398:         aa37633 com.amazon.mp3/.activity.ExternalLauncherActivity
402:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
403:         40f0df0 com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
416:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
417:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
420:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
423:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
426:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
431:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
443:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
446:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
468:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
475:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
480:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
484:         54f97dd com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
490:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
504:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
515:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
516:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
520:         6f20d77 com.microsoft.launcher/com.microsoft.bing.ProcessTextSearch
521:         89ae638 com.amazon.cloud9/com.amazon.slate.silo.SiloLauncherActivity
537:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
538:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
548:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
550:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
553:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
556:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
570:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
576:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
578:         4c7346f com.amazon.photos/com.android.launcher3.WallpaperCropActivity
580:         54f97dd com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
583:         6b04d68 com.microsoft.launcher/.wallpaper.activity.WallpaperPreviewActivity (2 filters)
592:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher
594:         aa37633 com.amazon.mp3/.activity.ExternalLauncherActivity
597:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
600:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
601:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
627:         aa37633 com.amazon.mp3/.activity.ExternalLauncherActivity
634:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
642:         aa37633 com.amazon.mp3/.activity.ExternalLauncherActivity
653:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (7 filters)
655:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity (7 filters)
659:         6f20d77 com.microsoft.launcher/com.microsoft.bing.ProcessTextSearch
661:         89ae638 com.amazon.cloud9/com.amazon.slate.silo.SiloLauncherActivity
669:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher (2 filters)
675:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (9 filters)
677:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity (34 filters)
702:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
703:         40f0df0 com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
709:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
711:         4c7346f com.amazon.photos/com.android.launcher3.WallpaperCropActivity
713:         54f97dd com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
716:         6b04d68 com.microsoft.launcher/.wallpaper.activity.WallpaperPreviewActivity (2 filters)
725:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
729:         54f97dd com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
735:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
752:         794175f com.amazon.windowshop/com.amazon.mShop.android.home.PublicUrlActivity
786:         9fc2ab0 com.android.vending/com.google.android.finsky.instantlaunchapi.InstantLauncherActivity
813:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher (3 filters)
819:       ms-launcher:
820:         5bebd1 com.microsoft.launcher/com.microsoft.rewards.activity.RewardsActionsActivity
821:         1ad8937 com.microsoft.launcher/.contacts.PeopleDeepLinkActivity
822:         da34636 com.microsoft.launcher/com.microsoft.rewards.activity.OfferLandingActivity
831:         794175f com.amazon.windowshop/com.amazon.mShop.android.home.PublicUrlActivity
847:         fd9551a com.google.android.gms/.home.SetupDeviceActivityQrCode
849:         393584b com.google.android.gms/.home.SetupDeviceActivityNfc
867:         fa7a8e6 com.amazon.avod/.client.activity.HomeScreenActivity
869:         74eea3b com.amazon.photos/com.amazon.gallery.thor.app.activity.ATCLauncherActivity
881:         573ff04 com.microsoft.launcher/.setting.FakeSms
887:         573ff04 com.microsoft.launcher/.setting.FakeSms
901:         817dca5 com.amazon.kindle.otter.oobe/.OOBELauncherV2
904:         8d73134 com.amazon.venezia/.CFR.dialog.CFRLauncherActivity
910:         f0c836e com.amazon.firelauncher/.Launcher
917:         40f0df0 com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
918:         54f97dd com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
923:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher (2 filters)
945:         5b021a3 com.amazon.cloud9/org.chromium.chrome.browser.DragAndDropLauncherActivity
949:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher (3 filters)
950:         6f23915 com.android.vending/com.google.android.finsky.protect.impl.PlayProtectHomeDeepLinkActivity
961:         d502ca0 com.amazon.photos/com.amazon.gallery.thor.app.activity.LauncherActivity (22 filters)
979:         feca1c9 org.mozilla.firefox/org.mozilla.fenix.HomeActivity
1007:         5b021a3 com.amazon.cloud9/org.chromium.chrome.browser.DragAndDropLauncherActivity
1012:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher (4 filters)
1013:         6f23915 com.android.vending/com.google.android.finsky.protect.impl.PlayProtectHomeDeepLinkActivity
```

### `package/home_query_cmd.stdout.txt`

```text
3:     priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
5:       name=com.amazon.firelauncher.Launcher
6:       packageName=com.amazon.firelauncher
9:       taskAffinity=com.amazon.firelauncher targetActivity=null persistableMode=PERSIST_ROOT_ONLY
15:         name=com.amazon.firelauncher.LauncherApp
16:         packageName=com.amazon.firelauncher
18:         className=com.amazon.firelauncher.LauncherApp
19:         processName=com.amazon.firelauncher
20:         taskAffinity=com.amazon.firelauncher
23:         sourceDir=/system/priv-app/com.amazon.firelauncher/com.amazon.firelauncher.apk
26:         dataDir=/data/user/0/com.amazon.firelauncher
27:         deviceProtectedDataDir=/data/user_de/0/com.amazon.firelauncher
28:         credentialProtectedDataDir=/data/user/0/com.amazon.firelauncher
36:     priority=0 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
38:       name=com.microsoft.launcher.Launcher
39:       packageName=com.microsoft.launcher
41:       taskAffinity=null targetActivity=com.microsoft.launcher.LauncherActivity persistableMode=PERSIST_ROOT_ONLY
47:         name=com.microsoft.launcher.LauncherApplication
48:         packageName=com.microsoft.launcher
50:         className=com.microsoft.launcher.LauncherApplication
51:         processName=com.microsoft.launcher
52:         taskAffinity=com.microsoft.launcher
55:         sourceDir=/data/app/com.microsoft.launcher-bTT5nKLHn89n_d_gJojj-Q==/base.apk
58:         dataDir=/data/user/0/com.microsoft.launcher
59:         deviceProtectedDataDir=/data/user_de/0/com.microsoft.launcher
60:         credentialProtectedDataDir=/data/user/0/com.microsoft.launcher
67:     priority=0 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
69:       name=org.fireosresearch.home.HomeActivity
70:       packageName=org.fireosresearch.home.p0
72:       taskAffinity=org.fireosresearch.home.p0 targetActivity=null persistableMode=PERSIST_ROOT_ONLY
78:         packageName=org.fireosresearch.home.p0
79:         labelRes=0x0 nonLocalizedLabel=Phase 3A org.fireosresearch.home.p0 priority 0 icon=0x0 banner=0x0
80:         processName=org.fireosresearch.home.p0
81:         taskAffinity=org.fireosresearch.home.p0
84:         sourceDir=/data/app/org.fireosresearch.home.p0-Er8RUFCd6pl-r5QmHpD9PQ==/base.apk
87:         dataDir=/data/user/0/org.fireosresearch.home.p0
88:         deviceProtectedDataDir=/data/user_de/0/org.fireosresearch.home.p0
89:         credentialProtectedDataDir=/data/user/0/org.fireosresearch.home.p0
95:     priority=-1000 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
97:       name=com.android.settings.FallbackHome
```

### `package/home_query_pm.stdout.txt`

```text
3:     priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
5:       name=com.amazon.firelauncher.Launcher
6:       packageName=com.amazon.firelauncher
9:       taskAffinity=com.amazon.firelauncher targetActivity=null persistableMode=PERSIST_ROOT_ONLY
15:         name=com.amazon.firelauncher.LauncherApp
16:         packageName=com.amazon.firelauncher
18:         className=com.amazon.firelauncher.LauncherApp
19:         processName=com.amazon.firelauncher
20:         taskAffinity=com.amazon.firelauncher
23:         sourceDir=/system/priv-app/com.amazon.firelauncher/com.amazon.firelauncher.apk
26:         dataDir=/data/user/0/com.amazon.firelauncher
27:         deviceProtectedDataDir=/data/user_de/0/com.amazon.firelauncher
28:         credentialProtectedDataDir=/data/user/0/com.amazon.firelauncher
36:     priority=0 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
38:       name=com.microsoft.launcher.Launcher
39:       packageName=com.microsoft.launcher
41:       taskAffinity=null targetActivity=com.microsoft.launcher.LauncherActivity persistableMode=PERSIST_ROOT_ONLY
47:         name=com.microsoft.launcher.LauncherApplication
48:         packageName=com.microsoft.launcher
50:         className=com.microsoft.launcher.LauncherApplication
51:         processName=com.microsoft.launcher
52:         taskAffinity=com.microsoft.launcher
55:         sourceDir=/data/app/com.microsoft.launcher-bTT5nKLHn89n_d_gJojj-Q==/base.apk
58:         dataDir=/data/user/0/com.microsoft.launcher
59:         deviceProtectedDataDir=/data/user_de/0/com.microsoft.launcher
60:         credentialProtectedDataDir=/data/user/0/com.microsoft.launcher
67:     priority=0 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
69:       name=org.fireosresearch.home.HomeActivity
70:       packageName=org.fireosresearch.home.p0
72:       taskAffinity=org.fireosresearch.home.p0 targetActivity=null persistableMode=PERSIST_ROOT_ONLY
78:         packageName=org.fireosresearch.home.p0
79:         labelRes=0x0 nonLocalizedLabel=Phase 3A org.fireosresearch.home.p0 priority 0 icon=0x0 banner=0x0
80:         processName=org.fireosresearch.home.p0
81:         taskAffinity=org.fireosresearch.home.p0
84:         sourceDir=/data/app/org.fireosresearch.home.p0-Er8RUFCd6pl-r5QmHpD9PQ==/base.apk
87:         dataDir=/data/user/0/org.fireosresearch.home.p0
88:         deviceProtectedDataDir=/data/user_de/0/org.fireosresearch.home.p0
89:         credentialProtectedDataDir=/data/user/0/org.fireosresearch.home.p0
95:     priority=-1000 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
97:       name=com.android.settings.FallbackHome
```

### `package/persistent_preferred.stdout.txt`

```text
149:   android.software.home_screen
238:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
247:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
250:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
252:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
258:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
267:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
272:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher
275:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
300:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
303:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
305:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
314:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
319:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
322:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
327:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
330:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
337:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
343:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
348:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
351:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
353:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
356:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
357:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
363:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
364:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
367:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
368:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
371:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
372:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
379:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
382:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
385:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
386:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
393:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
396:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
398:         aa37633 com.amazon.mp3/.activity.ExternalLauncherActivity
402:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
403:         40f0df0 com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
416:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
417:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
420:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
423:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
426:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
431:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
443:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
446:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
468:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
475:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
480:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
484:         54f97dd com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
490:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
504:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
515:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
516:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
520:         6f20d77 com.microsoft.launcher/com.microsoft.bing.ProcessTextSearch
521:         89ae638 com.amazon.cloud9/com.amazon.slate.silo.SiloLauncherActivity
537:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
538:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
548:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
550:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
553:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
556:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
570:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
576:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
578:         4c7346f com.amazon.photos/com.android.launcher3.WallpaperCropActivity
580:         54f97dd com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
583:         6b04d68 com.microsoft.launcher/.wallpaper.activity.WallpaperPreviewActivity (2 filters)
592:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher
594:         aa37633 com.amazon.mp3/.activity.ExternalLauncherActivity
597:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
600:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
601:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
627:         aa37633 com.amazon.mp3/.activity.ExternalLauncherActivity
634:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
642:         aa37633 com.amazon.mp3/.activity.ExternalLauncherActivity
653:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (7 filters)
655:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity (7 filters)
659:         6f20d77 com.microsoft.launcher/com.microsoft.bing.ProcessTextSearch
661:         89ae638 com.amazon.cloud9/com.amazon.slate.silo.SiloLauncherActivity
669:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher (2 filters)
675:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (9 filters)
677:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity (34 filters)
702:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
703:         40f0df0 com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
709:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
711:         4c7346f com.amazon.photos/com.android.launcher3.WallpaperCropActivity
713:         54f97dd com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
716:         6b04d68 com.microsoft.launcher/.wallpaper.activity.WallpaperPreviewActivity (2 filters)
725:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
729:         54f97dd com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
735:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
752:         794175f com.amazon.windowshop/com.amazon.mShop.android.home.PublicUrlActivity
786:         9fc2ab0 com.android.vending/com.google.android.finsky.instantlaunchapi.InstantLauncherActivity
813:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher (3 filters)
819:       ms-launcher:
820:         5bebd1 com.microsoft.launcher/com.microsoft.rewards.activity.RewardsActionsActivity
821:         1ad8937 com.microsoft.launcher/.contacts.PeopleDeepLinkActivity
822:         da34636 com.microsoft.launcher/com.microsoft.rewards.activity.OfferLandingActivity
831:         794175f com.amazon.windowshop/com.amazon.mShop.android.home.PublicUrlActivity
847:         fd9551a com.google.android.gms/.home.SetupDeviceActivityQrCode
849:         393584b com.google.android.gms/.home.SetupDeviceActivityNfc
867:         fa7a8e6 com.amazon.avod/.client.activity.HomeScreenActivity
869:         74eea3b com.amazon.photos/com.amazon.gallery.thor.app.activity.ATCLauncherActivity
881:         573ff04 com.microsoft.launcher/.setting.FakeSms
887:         573ff04 com.microsoft.launcher/.setting.FakeSms
901:         817dca5 com.amazon.kindle.otter.oobe/.OOBELauncherV2
904:         8d73134 com.amazon.venezia/.CFR.dialog.CFRLauncherActivity
910:         f0c836e com.amazon.firelauncher/.Launcher
917:         40f0df0 com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
918:         54f97dd com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
923:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher (2 filters)
945:         5b021a3 com.amazon.cloud9/org.chromium.chrome.browser.DragAndDropLauncherActivity
949:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher (3 filters)
950:         6f23915 com.android.vending/com.google.android.finsky.protect.impl.PlayProtectHomeDeepLinkActivity
961:         d502ca0 com.amazon.photos/com.amazon.gallery.thor.app.activity.LauncherActivity (22 filters)
979:         feca1c9 org.mozilla.firefox/org.mozilla.fenix.HomeActivity
1007:         5b021a3 com.amazon.cloud9/org.chromium.chrome.browser.DragAndDropLauncherActivity
1012:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher (4 filters)
1013:         6f23915 com.android.vending/com.google.android.finsky.protect.impl.PlayProtectHomeDeepLinkActivity
```

### `package/preferred_activities.stdout.txt`

```text
149:   android.software.home_screen
238:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
247:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
250:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
252:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
258:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
267:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
272:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher
275:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
300:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
303:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
305:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
314:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
319:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
322:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
327:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
330:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
337:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
343:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
348:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
351:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
353:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
356:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
357:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
363:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
364:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
367:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
368:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
371:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
372:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
379:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
382:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
385:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
386:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
393:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
396:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
398:         aa37633 com.amazon.mp3/.activity.ExternalLauncherActivity
402:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
403:         40f0df0 com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
416:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
417:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
420:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
423:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
426:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
431:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
443:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
446:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
468:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
475:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
480:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
484:         54f97dd com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
490:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
504:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
515:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
516:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
520:         6f20d77 com.microsoft.launcher/com.microsoft.bing.ProcessTextSearch
521:         89ae638 com.amazon.cloud9/com.amazon.slate.silo.SiloLauncherActivity
537:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
538:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
548:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
550:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
553:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
556:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
570:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
576:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
578:         4c7346f com.amazon.photos/com.android.launcher3.WallpaperCropActivity
580:         54f97dd com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
583:         6b04d68 com.microsoft.launcher/.wallpaper.activity.WallpaperPreviewActivity (2 filters)
592:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher
594:         aa37633 com.amazon.mp3/.activity.ExternalLauncherActivity
597:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
600:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
601:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
627:         aa37633 com.amazon.mp3/.activity.ExternalLauncherActivity
634:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
642:         aa37633 com.amazon.mp3/.activity.ExternalLauncherActivity
653:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (7 filters)
655:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity (7 filters)
659:         6f20d77 com.microsoft.launcher/com.microsoft.bing.ProcessTextSearch
661:         89ae638 com.amazon.cloud9/com.amazon.slate.silo.SiloLauncherActivity
669:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher (2 filters)
675:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (9 filters)
677:         3335242 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity (34 filters)
702:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
703:         40f0df0 com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
709:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
711:         4c7346f com.amazon.photos/com.android.launcher3.WallpaperCropActivity
713:         54f97dd com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
716:         6b04d68 com.microsoft.launcher/.wallpaper.activity.WallpaperPreviewActivity (2 filters)
725:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
729:         54f97dd com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
735:         189c0af com.android.bluetooth/.opp.BluetoothOppLauncherActivity
752:         794175f com.amazon.windowshop/com.amazon.mShop.android.home.PublicUrlActivity
786:         9fc2ab0 com.android.vending/com.google.android.finsky.instantlaunchapi.InstantLauncherActivity
813:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher (3 filters)
819:       ms-launcher:
820:         5bebd1 com.microsoft.launcher/com.microsoft.rewards.activity.RewardsActionsActivity
821:         1ad8937 com.microsoft.launcher/.contacts.PeopleDeepLinkActivity
822:         da34636 com.microsoft.launcher/com.microsoft.rewards.activity.OfferLandingActivity
831:         794175f com.amazon.windowshop/com.amazon.mShop.android.home.PublicUrlActivity
847:         fd9551a com.google.android.gms/.home.SetupDeviceActivityQrCode
849:         393584b com.google.android.gms/.home.SetupDeviceActivityNfc
867:         fa7a8e6 com.amazon.avod/.client.activity.HomeScreenActivity
869:         74eea3b com.amazon.photos/com.amazon.gallery.thor.app.activity.ATCLauncherActivity
881:         573ff04 com.microsoft.launcher/.setting.FakeSms
887:         573ff04 com.microsoft.launcher/.setting.FakeSms
901:         817dca5 com.amazon.kindle.otter.oobe/.OOBELauncherV2
904:         8d73134 com.amazon.venezia/.CFR.dialog.CFRLauncherActivity
910:         f0c836e com.amazon.firelauncher/.Launcher
917:         40f0df0 com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
918:         54f97dd com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
923:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher (2 filters)
945:         5b021a3 com.amazon.cloud9/org.chromium.chrome.browser.DragAndDropLauncherActivity
949:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher (3 filters)
950:         6f23915 com.android.vending/com.google.android.finsky.protect.impl.PlayProtectHomeDeepLinkActivity
961:         d502ca0 com.amazon.photos/com.amazon.gallery.thor.app.activity.LauncherActivity (22 filters)
979:         feca1c9 org.mozilla.firefox/org.mozilla.fenix.HomeActivity
1007:         5b021a3 com.amazon.cloud9/org.chromium.chrome.browser.DragAndDropLauncherActivity
1012:         6cb16a7 com.audible.application.kindle/com.audible.application.MainLauncher (4 filters)
1013:         6f23915 com.android.vending/com.google.android.finsky.protect.impl.PlayProtectHomeDeepLinkActivity
```

### `package/preferred_xml.stdout.txt`

```text
3:     <item name="org.fireosresearch.home.p0/org.fireosresearch.home.HomeActivity">
6:             <cat name="android.intent.category.HOME" />
```

### `properties/getprop.stdout.txt`

```text
105: [init.svc.wmt_launcher]: [running]
```

### `window/input.stdout.txt`

```text
454:   FocusedApplication: name='AppWindowToken{1f10017 token=Token{e40cc96 ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}}}', dispatchingTimeout=5000.000ms
462:     4: name='Window{2c47b02 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}', displayId=0, paused=false, hasFocus=false, hasWallpaper=false, visible=false, canReceiveKeys=false, flags=0x81910120, type=0x00000001, layer=0, frame=[0,0][1200,1920], scale=1.000000, touchableRegion=[0,0][1200,1920], inputFeatures=0x00000000, ownerPid=1919, ownerUid=10120, dispatchingTimeout=5000.000ms
500:     6: channelName='2c47b02 com.amazon.firelauncher/com.amazon.firelauncher.Launcher (server)', windowName='Window{2c47b02 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}', status=NORMAL, monitor=false, inputPublisherBlocked=false
```

### `window/processes.stdout.txt`

```text
283: system         424     1 wmt_launcher                wmt_launcher -p /vendor/firmware/
377: u0_a75        1909   350 com.android.launcher3       com.android.launcher3
378: u0_a120       1919   350 com.amazon.firelauncher     com.amazon.firelauncher
```

### `window/windows.stdout.txt`

```text
127:   Window #4 Window{2c47b02 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}:
129:     mOwnerUid=10120 mShowToOwnerOnly=true package=com.amazon.firelauncher appop=NONE
136:     mToken=AppWindowToken{1f10017 token=Token{e40cc96 ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}}}
137:     mAppToken=AppWindowToken{1f10017 token=Token{e40cc96 ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}}}
142:     mFullConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
153:     WindowStateAnimator{d37c4f8 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}:
224:   mCurrentFocus=Window{f76e49b u0 StatusBar}
225:   mFocusedApp=AppWindowToken{1f10017 token=Token{e40cc96 ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}}}
252:     mLastClosingApp=AppWindowToken{1f10017 token=Token{e40cc96 ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}}}
```


## Small text diffs

### `activity/activities.stdout.txt`

```diff
--- before/activity/activities.stdout.txt

+++ after/activity/activities.stdout.txt

@@ -3,5 +3,5 @@

 
   Stack #0: type=home mode=fullscreen
-  isSleeping=false
+  isSleeping=true
   mBounds=Rect(0, 0 - 0, 0)
     Task id #2
@@ -10,5 +10,5 @@

     mMinHeight=-1
     mLastNonFullscreenBounds=null
-    * TaskRecord{87ddf9b #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
+    * TaskRecord{55bad2e #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
       userId=0 effectiveUid=u0a120 mCallingUid=0 mUserSetupComplete=true mCallingPackage=null
       affinity=10120:com.amazon.firelauncher
@@ -17,15 +17,15 @@

       autoRemoveRecents=false isPersistable=true numFullscreen=1 activityType=2
       rootWasReset=false mNeverRelinquishIdentity=true mReuseTask=false mLockTaskAuth=LOCK_TASK_AUTH_PINNABLE
-      Activities=[ActivityRecord{1fb24c3 u0 com.amazon.firelauncher/.Launcher t2}]
+      Activities=[ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}]
       askedCompatMode=false inRecents=true isAvailable=true
-      mRootProcess=ProcessRecord{49b9f38 1963:com.amazon.firelauncher/u0a120}
+      mRootProcess=ProcessRecord{660f0cf 1919:com.amazon.firelauncher/u0a120}
       stackId=0
-      hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=2250671 (inactive for 2434s)
-      * Hist #0: ActivityRecord{1fb24c3 u0 com.amazon.firelauncher/.Launcher t2}
+      hasBeenVisible=false mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=23218 (inactive for 1s)
+      * Hist #0: ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}
           packageName=com.amazon.firelauncher processName=com.amazon.firelauncher
           launchedFromUid=0 launchedFromPackage=null userId=0
-          app=ProcessRecord{49b9f38 1963:com.amazon.firelauncher/u0a120}
+          app=ProcessRecord{660f0cf 1919:com.amazon.firelauncher/u0a120}
           Intent { act=android.intent.action.MAIN cat=[android.intent.category.HOME] flg=0x10000100 cmp=com.amazon.firelauncher/.Launcher }
-          frontOfTask=true task=TaskRecord{87ddf9b #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
+          frontOfTask=true task=TaskRecord{55bad2e #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
           taskAffinity=10120:com.amazon.firelauncher
           realActivity=com.amazon.firelauncher/.Launcher
@@ -43,87 +43,35 @@

            statusBarColor=0
            navigationBarColor=ff000000
-          launchFailed=false launchCount=0 lastLaunchTime=-1h17m41s953ms
-          haveState=false icicle=null
-          state=RESUMED stopped=false delayedResume=false finishing=false
-          keysPaused=false inHistory=true visible=true sleeping=false idle=true mStartingWindowState=STARTING_WINDOW_NOT_SHOWN
+          launchFailed=false launchCount=1 lastLaunchTime=-4s246ms
+          haveState=true icicle=null
+          state=STOPPING stopped=false delayedResume=false finishing=false
+          keysPaused=false inHistory=true visible=false sleeping=true idle=false mStartingWindowState=STARTING_WINDOW_NOT_SHOWN
           fullscreen=true noDisplay=false immersive=false launchMode=2
           frozenBeforeDestroy=false forceNewConfig=false
           mActivityType=home
-          waitingVisible=false nowVisible=true lastVisibleTime=-1h7m58s70ms
+          displayStartTime=-4s242ms startTime=0
           resizeMode=RESIZE_MODE_RESIZEABLE
           mLastReportedMultiWindowMode=false mLastReportedPictureInPictureMode=false
 
     Running activities (most recent first):
-      TaskRecord{87ddf9b #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
-        Run #0: ActivityRecord{1fb24c3 u0 com.amazon.firelauncher/.Launcher t2}
+      TaskRecord{55bad2e #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
+        Run #0: ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}
 
-    mResumedActivity: ActivityRecord{1fb24c3 u0 com.amazon.firelauncher/.Launcher t2}
+    mLastPausedActivity: ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}
+Display #2 (activities from top to bottom):
 
-  Stack #2: type=recents mode=fullscreen
-  isSleeping=false
-  mBounds=Rect(0, 0 - 0, 0)
+  Activities waiting to sleep:
+    TaskRecord{55bad2e #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
+      Sleep #0: ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}
 
-    Task id #26
-    mBounds=Rect(0, 0 - 0, 0)
-    mMinWidth=-1
-    mMinHeight=-1
-    mLastNonFullscreenBounds=null
-    * TaskRecord{dd3d92d #26 I=com.android.launcher3/com.android.quickstep.RecentsActivity U=0 StackId=2 sz=1}
-      userId=0 effectiveUid=u0a75 mCallingUid=u0a75 mUserSetupComplete=true mCallingPackage=com.android.launcher3
-      intent={act=android.intent.action.MAIN cat=[android.intent.category.DEFAULT] flg=0x10800000 cmp=com.android.launcher3/com.android.quickstep.RecentsActivity}
-      realActivity=com.android.launcher3/com.android.quickstep.RecentsActivity
-      autoRemoveRecents=false isPersistable=false numFullscreen=1 activityType=3
-      rootWasReset=false mNeverRelinquishIdentity=true mReuseTask=false mLockTaskAuth=LOCK_TASK_AUTH_PINNABLE
-      Activities=[ActivityRecord{eb77636 u0 com.android.launcher3/com.android.quickstep.RecentsActivity t26}]
-      askedCompatMode=false inRecents=true isAvailable=true
-      stackId=2
-      hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=606300 (inactive for 4078s)
-      * Hist #0: ActivityRecord{eb77636 u0 com.android.launcher3/com.android.quickstep.RecentsActivity t26}
-          packageName=com.android.launcher3 processName=com.android.launcher3
-          launchedFromUid=10075 launchedFromPackage=com.android.launcher3 userId=0
-          app=ProcessRecord{97e6c35 1948:com.android.launcher3/u0a75}
-          Intent { act=android.intent.action.MAIN cat=[android.intent.category.DEFAULT] flg=0x10800000 cmp=com.android.launcher3/com.android.quickstep.RecentsActivity }
-          frontOfTask=true task=TaskRecord{dd3d92d #26 I=com.android.launcher3/com.android.quickstep.RecentsActivity U=0 StackId=2 sz=1}
-          taskAffinity=null
-          realActivity=com.android.launcher3/com.android.quickstep.RecentsActivity
-          baseDir=/system/priv-app/com.android.launcher3/com.android.launcher3.apk
-          dataDir=/data/user/0/com.android.launcher3
-          stateNotNeeded=true componentSpecified=true mActivityType=recents
-          compat={240dpi always-compat} labelRes=0x7f110035 icon=0x7f08001b theme=0x7f12000a
-          mLastReportedConfigurations:
-           mGlobalConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 0, 0) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=undefined} s.6}
-           mOverrideConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=recents} s.6}
-          CurrentConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=recents} s.6}
-          OverrideConfiguration={0.0 ?mcc?mnc ?localeList ?layoutDir ?swdp ?wdp ?hdp ?density ?lsize ?long ?ldr ?wideColorGamut ?orien ?uimode ?night ?touch ?keyb/?/? ?nav/? winConfig={ mBounds=Rect(0, 0 - 0, 0) mAppBounds=null mWindowingMode=undefined mActivityType=recents}}
-          taskDescription: label="null" icon=null iconResource=0 iconFilename=null primaryColor=fff5f5f5
-           backgroundColor=fffafafa
-           statusBarColor=0
-           navigationBarColor=0
-          launchFailed=false launchCount=0 lastLaunchTime=-1h8m0s425ms
-          haveState=true icicle=Bundle[mParcelledData.dataSize=560]
-          state=STOPPED stopped=true delayedResume=false finishing=false
-          keysPaused=false inHistory=true visible=false sleeping=false idle=true mStartingWindowState=STARTING_WINDOW_REMOVED
-          fullscreen=true noDisplay=false immersive=false launchMode=2
-          frozenBeforeDestroy=false forceNewConfig=false
-          mActivityType=recents
-          waitingVisible=false nowVisible=false lastVisibleTime=-1h8m0s149ms
-          resizeMode=RESIZE_MODE_RESIZEABLE
-          mLastReportedMultiWindowMode=false mLastReportedPictureInPictureMode=false
-
-    Running activities (most recent first):
-      TaskRecord{dd3d92d #26 I=com.android.launcher3/com.android.quickstep.RecentsActivity U=0 StackId=2 sz=1}
-        Run #0: ActivityRecord{eb77636 u0 com.android.launcher3/com.android.quickstep.RecentsActivity t26}
-
-    mLastPausedActivity: ActivityRecord{eb77636 u0 com.android.launcher3/com.android.quickstep.RecentsActivity t26}
-
-  ResumedActivity: ActivityRecord{1fb24c3 u0 com.amazon.firelauncher/.Launcher t2}
-  mFocusedStack=ActivityStack{88f66b4 stackId=0 type=home mode=fullscreen visible=true translucent=false, 1 tasks} mLastFocusedStack=ActivityStack{88f66b4 stackId=0 type=home mode=fullscreen visible=true translucent=false, 1 tasks}
-  mCurTaskIdForUser={0=26}
+  ResumedActivity: ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}
+  mFocusedStack=ActivityStack{fbfca5c stackId=0 type=home mode=fullscreen visible=true translucent=false, 1 tasks} mLastFocusedStack=ActivityStack{fbfca5c stackId=0 type=home mode=fullscreen visible=true translucent=false, 1 tasks}
+  mCurTaskIdForUser={0=27}
   mUserStackInFront={}
-  displayId=0 stacks=2
-   mHomeStack=ActivityStack{88f66b4 stackId=0 type=home mode=fullscreen visible=true translucent=false, 1 tasks}
-   mRecentsStack=ActivityStack{52d5e62 stackId=2 type=recents mode=fullscreen visible=false translucent=true, 1 tasks}
+  displayId=2 stacks=0
+  displayId=0 stacks=1
+   mHomeStack=ActivityStack{fbfca5c stackId=0 type=home mode=fullscreen visible=true translucent=false, 1 tasks}
   isHomeRecentsComponent=false  KeyguardController:
-    mKeyguardShowing=false
+    mKeyguardShowing=true
     mAodShowing=false
     mKeyguardGoingAway=false
```

### `activity/recents.stdout.txt`

```diff
--- before/activity/recents.stdout.txt

+++ after/activity/recents.stdout.txt

@@ -3,5 +3,5 @@

 mRecentsComponent=ComponentInfo{com.android.launcher3/com.android.quickstep.RecentsActivity}
   Recent tasks:
-  * Recent #0: TaskRecord{87ddf9b #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
+  * Recent #0: TaskRecord{55bad2e #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
     userId=0 effectiveUid=u0a120 mCallingUid=0 mUserSetupComplete=true mCallingPackage=null
     affinity=10120:com.amazon.firelauncher
@@ -10,17 +10,19 @@

     autoRemoveRecents=false isPersistable=true numFullscreen=1 activityType=2
     rootWasReset=false mNeverRelinquishIdentity=true mReuseTask=false mLockTaskAuth=LOCK_TASK_AUTH_PINNABLE
-    Activities=[ActivityRecord{1fb24c3 u0 com.amazon.firelauncher/.Launcher t2}]
+    Activities=[ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}]
     askedCompatMode=false inRecents=true isAvailable=true
-    mRootProcess=ProcessRecord{49b9f38 1963:com.amazon.firelauncher/u0a120}
+    mRootProcess=ProcessRecord{660f0cf 1919:com.amazon.firelauncher/u0a120}
     stackId=0
-    hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=2250671 (inactive for 2434s)
-  * Recent #1: TaskRecord{dd3d92d #26 I=com.android.launcher3/com.android.quickstep.RecentsActivity U=0 StackId=2 sz=1}
-    userId=0 effectiveUid=u0a75 mCallingUid=u0a75 mUserSetupComplete=true mCallingPackage=com.android.launcher3
-    intent={act=android.intent.action.MAIN cat=[android.intent.category.DEFAULT] flg=0x10800000 cmp=com.android.launcher3/com.android.quickstep.RecentsActivity}
-    realActivity=com.android.launcher3/com.android.quickstep.RecentsActivity
-    autoRemoveRecents=false isPersistable=false numFullscreen=1 activityType=3
+    hasBeenVisible=false mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=23218 (inactive for 1s)
+  * Recent #1: TaskRecord{db8a92 #27 A=1000:com.android.settings.root U=0 StackId=-1 sz=0}
+    userId=0 effectiveUid=1000 mCallingUid=2000 mUserSetupComplete=true mCallingPackage=
+    affinity=1000:com.android.settings.root
+    intent={flg=0x10000000 cmp=com.android.settings/.Settings}
+    origActivity=com.android.settings/.Settings
+    realActivity=com.android.settings/.Settings
+    autoRemoveRecents=false isPersistable=true numFullscreen=0 activityType=0
     rootWasReset=false mNeverRelinquishIdentity=true mReuseTask=false mLockTaskAuth=LOCK_TASK_AUTH_PINNABLE
-    Activities=[ActivityRecord{eb77636 u0 com.android.launcher3/com.android.quickstep.RecentsActivity t26}]
+    Activities=[]
     askedCompatMode=false inRecents=true isAvailable=true
-    stackId=2
-    hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=606300 (inactive for 4078s)
+    stackId=-1
+    hasBeenVisible=false mResizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION mSupportsPictureInPicture=false isResizeable=true lastActiveTime=23130 (inactive for 1s)
```

### `activity/top.stdout.txt`

```diff
--- before/activity/top.stdout.txt

+++ after/activity/top.stdout.txt

@@ -1,43 +1,69 @@

-TASK null id=26 userId=0
-  ACTIVITY com.android.launcher3/com.android.quickstep.RecentsActivity eb77636 pid=1948
-    Local Activity 6047dfb State:
+TASK 10120:com.amazon.firelauncher id=2 userId=0
+  ACTIVITY com.amazon.firelauncher/.Launcher f7a5258 pid=1919
+    Local Activity 5653290 State:
       mResumed=false mStopped=true mFinished=false
       mChangingConfigurations=false
-      mCurrentConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=recents} s.6}
+      mCurrentConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
       mLoadersStarted=true
+      Active Fragments in e4fae55:
+        #0: ReportFragment{9c9506a #0 androidx.lifecycle.LifecycleDispatcher.report_fragment_tag}
+          mFragmentId=#0 mContainerId=#0 mTag=androidx.lifecycle.LifecycleDispatcher.report_fragment_tag
+          mState=3 mIndex=0 mWho=android:fragment:0 mBackStackNesting=0
+          mAdded=true mRemoving=false mFromLayout=false mInLayout=false
+          mHidden=false mDetached=false mMenuVisible=true mHasMenu=false
+          mRetainInstance=false mRetaining=false mUserVisibleHint=true
+          mFragmentManager=FragmentManager{e4fae55 in HostCallbacks{d33b95b}}
+          mHost=android.app.Activity$HostCallbacks@d33b95b
+          Child FragmentManager{8e1d5f8 in ReportFragment{9c9506a}}:
+            FragmentManager misc state:
+              mHost=android.app.Activity$HostCallbacks@d33b95b
+              mContainer=android.app.Fragment$1@d29dad1
+              mParent=ReportFragment{9c9506a #0 androidx.lifecycle.LifecycleDispatcher.report_fragment_tag}
+              mCurState=3 mStateSaved=true mDestroyed=false
+      Added Fragments:
+        #0: ReportFragment{9c9506a #0 androidx.lifecycle.LifecycleDispatcher.report_fragment_tag}
       FragmentManager misc state:
-        mHost=android.app.Activity$HostCallbacks@2f122e
-        mContainer=android.app.Activity$HostCallbacks@2f122e
+        mHost=android.app.Activity$HostCallbacks@d33b95b
+        mContainer=android.app.Activity$HostCallbacks@d33b95b
         mCurState=3 mStateSaved=true mDestroyed=false
-    ViewRoot:
-      mAdded=true mRemoved=false
-      mConsumeBatchedInputScheduled=false
-      mConsumeBatchedInputImmediatelyScheduled=false
-      mPendingInputEventCount=0
-      mProcessInputEventsScheduled=false
-      mTraversalScheduled=false      mIsAmbientMode=false
-      android.view.ViewRootImpl$NativePreImeInputStage: mQueueLength=0
-      android.view.ViewRootImpl$ImeInputStage: mQueueLength=0
-      android.view.ViewRootImpl$NativePostImeInputStage: mQueueLength=0
-    Choreographer:
-      mFrameScheduled=false
-      mLastFrameTime=606732 (4078132 ms ago)
-    View Hierarchy:
-      DecorView@928f1cf[RecentsActivity]
-        android.widget.FrameLayout{536375c V.E...... .......D 0,0-1200,1920}
-          android.widget.FrameLayout{a1bca65 V.E...... .......D 0,0-1200,1920 #1020002 android:id/content}
-            com.android.quickstep.fallback.RecentsRootView{49e233a V.E...... ......ID 0,0-1200,1920 #7f0a002d app:id/drag_layer}
-              com.android.quickstep.views.RecentsViewContainer{eecdbeb V.E...... ........ 0,0-1200,1920 #7f0a0059 app:id/overview_panel_container}
-                com.android.quickstep.views.ClearAllButton{89d6d48 IFED..C.. ........ 0,36-255,108 #7f0a0024 app:id/clear_all_button}
-                com.android.quickstep.fallback.FallbackRecentsView{3a7e1 V.ED..... ........ 0,0-1200,1920 #7f0a0058 app:id/overview_panel}
-          android.view.ViewStub{7bb3906 G.E...... ......I. 0,0-0,0 #10201ad android:id/action_mode_bar_stub}
-    Looper (main, tid 2) {6bb4bc7}
-      (Total messages: 0, polling=false, quitting=false)
+    Looper (main, tid 2) {a240936}
+      Message 0: { when=-364ms callback=android.app.-$$Lambda$LoadedApk$ReceiverDispatcher$Args$_BumDX2UKsnxLVrE6UJsJZkotuA target=android.app.ActivityThread$H isAsync=false }
+      Message 1: { when=-223ms what=0 target=com.amazon.firelauncher.templatedatasources.LauncherCdaClient$MainHandler isAsync=false }
+      Message 2: { when=-214ms what=0 target=com.amazon.firelauncher.templatedatasources.LauncherCdaClient$MainHandler isAsync=false }
+      Message 3: { when=-202ms what=1 obj=com.amazon.firelauncher.DemoFlagObserverHandler$DemoFlagObserverClient@1ea9037 target=com.amazon.firelauncher.DemoFlagObserverHandler isAsync=false }
+      Message 4: { when=-201ms callback=com.amazon.sics.SicsCache$2 target=android.os.Handler isAsync=false }
+      Message 5: { when=-175ms callback=com.amazon.firelauncher.search.SearchAppWidgetManager$4 target=android.os.Handler isAsync=false }
+      Message 6: { when=-174ms callback=com.amazon.firelauncher.ads.AdImpressionHistory$3$1 target=android.os.Handler isAsync=false }
+      Message 7: { when=-148ms callback=com.amazon.firelauncher.appsgrid.manager.AppManager$2 target=android.os.Handler isAsync=false }
+      Message 8: { when=-74ms callback=android.view.ViewRootImpl$4 target=android.view.ViewRootImpl$ViewRootHandler isAsync=false }
+      Message 9: { when=-74ms callback=android.view.Choreographer$FrameDisplayEventReceiver target=android.view.Choreographer$FrameHandler isAsync=true }
+      Message 10: { when=-65ms barrier=0 isAsync=false }
+      Message 11: { when=-8ms callback=android.app.servertransaction.PendingTransactionActions$StopInfo target=android.app.ActivityThread$H isAsync=false }
+      Message 12: { when=-7ms callback=com.amazon.firelauncher.Launcher$2$1 target=android.os.Handler isAsync=false }
+      Message 13: { when=-7ms callback=com.amazon.firelauncher.Launcher$2$1 target=android.os.Handler isAsync=false }
+      Message 14: { when=+2s130ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
+      Message 15: { when=+2s156ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
+      Message 16: { when=+2s293ms callback=com.amazon.firelauncher.weblab.DelayedWeblabController$2 target=android.os.Handler isAsync=false }
+      Message 17: { when=+2s313ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
+      Message 18: { when=+2s314ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
+      Message 19: { when=+2s314ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
+      Message 20: { when=+2s324ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
+      Message 21: { when=+2s327ms callback=com.amazon.firelauncher.Launcher$OffScreenRunnable target=android.os.Handler isAsync=false }
+      Message 22: { when=+2s446ms callback=com.amazon.firelauncher.services.DefaultMapCache$5 target=android.os.Handler isAsync=false }
+      Message 23: { when=+2s493ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
+      Message 24: { when=+2s645ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
+      Message 25: { when=+2s671ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
+      Message 26: { when=+2s815ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
+      Message 27: { when=+2s843ms callback=com.amazon.firelauncher.arcus.DelayedRemoteSettingsAccess$2 target=android.os.Handler isAsync=false }
+      Message 28: { when=+4s852ms callback=com.amazon.firelauncher.metrics.drawn.DelayedMetricCallbackQueue$1 target=android.os.Handler isAsync=false }
+      Message 29: { when=+9s319ms what=132 target=android.app.ActivityThread$H isAsync=false }
+      Message 30: { when=+59m59s660ms callback=com.amazon.firecard.deviceagent.provider.CardProvider$5 target=android.os.Handler isAsync=false }
+      (Total messages: 31, polling=false, quitting=false)
     Autofill Compat Mode: false
     AutofillManager:
       sessionId: -2147483648
       state: UNKNOWN
-      context: com.android.quickstep.RecentsActivity@6047dfb
-      client: com.android.quickstep.RecentsActivity@6047dfb
+      context: com.amazon.firelauncher.Launcher@5653290
+      client: com.amazon.firelauncher.Launcher@5653290
       enabled: false
       hasService: true
@@ -53,321 +79,11 @@

       debug: false verbose: false
     ResourcesManager:
-      total apks: 2
-      resources: 3
-      resource impls: 3
-    Misc:
- deviceProfile isTransposed=false
- orientation=1
- mSystemUiController: mStates=[10, 0, 0, 0, 0]
- mActivityFlags: 0
- mForceInvisible: 0
-
-TASK 10120:com.amazon.firelauncher id=2 userId=0
-  ACTIVITY com.amazon.firelauncher/.Launcher 1fb24c3 pid=1963
-    Local Activity 38c4811 State:
-      mResumed=true mStopped=false mFinished=false
-      mChangingConfigurations=false
-      mCurrentConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
-      mLoadersStarted=true
-      Active Fragments in 5c66a44:
-        #0: ReportFragment{e74272d #0 androidx.lifecycle.LifecycleDispatcher.report_fragment_tag}
-          mFragmentId=#0 mContainerId=#0 mTag=androidx.lifecycle.LifecycleDispatcher.report_fragment_tag
-          mState=5 mIndex=0 mWho=android:fragment:0 mBackStackNesting=0
-          mAdded=true mRemoving=false mFromLayout=false mInLayout=false
-          mHidden=false mDetached=false mMenuVisible=true mHasMenu=false
-          mRetainInstance=false mRetaining=false mUserVisibleHint=true
-          mFragmentManager=FragmentManager{5c66a44 in HostCallbacks{5329462}}
-          mHost=android.app.Activity$HostCallbacks@5329462
-          Child FragmentManager{58b39f3 in ReportFragment{e74272d}}:
-            FragmentManager misc state:
-              mHost=android.app.Activity$HostCallbacks@5329462
-              mContainer=android.app.Fragment$1@ce1e6b0
-              mParent=ReportFragment{e74272d #0 androidx.lifecycle.LifecycleDispatcher.report_fragment_tag}
-              mCurState=5 mStateSaved=false mDestroyed=false
-      Added Fragments:
-        #0: ReportFragment{e74272d #0 androidx.lifecycle.LifecycleDispatcher.report_fragment_tag}
-      FragmentManager misc state:
-        mHost=android.app.Activity$HostCallbacks@5329462
-        mContainer=android.app.Activity$HostCallbacks@5329462
-        mCurState=5 mStateSaved=false mDestroyed=false
-    ViewRoot:
-      mAdded=true mRemoved=false
-      mConsumeBatchedInputScheduled=false
-      mConsumeBatchedInputImmediatelyScheduled=false
-      mPendingInputEventCount=0
-      mProcessInputEventsScheduled=false
-      mTraversalScheduled=false      mIsAmbientMode=false
-      android.view.ViewRootImpl$NativePreImeInputStage: mQueueLength=0
-      android.view.ViewRootImpl$ImeInputStage: mQueueLength=0
-      android.view.ViewRootImpl$NativePostImeInputStage: mQueueLength=0
-    Choreographer:
-      mFrameScheduled=false
-      mLastFrameTime=4632326 (52541 ms ago)
-    View Hierarchy:
-      DecorView@c990929[Launcher]
-        android.widget.FrameLayout{ca994ae V.E...... ........ 0,0-1200,1920}
-          android.widget.FrameLayout{96ae89a V.E...... ........ 0,0-1200,1920 #1020002 android:id/content}
-            com.amazon.firelauncher.appsgrid.ui.drag.DragLayer{c15824f V.E...... ........ 0,0-1200,1920 #7f090336 app:id/magazine_container}
-              android.widget.FrameLayout{af6bddc V.E...... ........ 0,0-1200,1920 #7f0900ee app:id/background_parent}
-                android.widget.ImageView{d100ee5 V.ED..... ........ 0,0-1200,1920 #7f090125 app:id/channel_background}
-              com.amazon.firelauncher.view.EnhancedViewPager{e7e4dba VFED..... ........ 0,0-1200,1920 #7f090379 app:id/pager}
-                com.amazon.firelauncher.appsgrid.ui.ScrollableMainView{1979eee V.E...... ........ 0,0-1200,1920}
-                  com.amazon.firelauncher.appsgrid.ui.GradientScrimFrameLayout{f51f46b V.E...... ........ 0,0-1200,1920}
-                    com.amazon.firelauncher.appsgrid.ui.GridView{574be6d VFED..... ........ 0,0-1200,1920 #7f09027a app:id/favorites_page}
-                      com.amazon.firecard.view.widget.ScrollingTemplateViewHost{4294ed3 G.E...... ......I. 42,0-1158,252}
-                        android.widget.FrameLayout{41fdbc8 G.E...... ......I. 0,0-0,0 #7f09032e app:id/loading_placeholder}
-                          com.amazon.firelauncher.view.LoadingDotsView{b37b461 V.E...... ......I. 0,0-0,0 #7f09032c app:id/loading_dots}
-                            android.widget.ImageView{3b38b86 V.ED..... ......ID 0,0-0,0 #7f0901b0 app:id/dot1}
-                            android.widget.ImageView{7996c47 V.ED..... ......ID 0,0-0,0 #7f0901b1 app:id/dot2}
-                            android.widget.ImageView{13aec74 V.ED..... ......ID 0,0-0,0 #7f0901b2 app:id/dot3}
-                        com.amazon.firecard.view.widget.ScrollingTemplateView{fda359d G.ED..... ......I. 0,0-0,0 #7f090491 app:id/up_next_parent}
-                          com.amazon.firecard.view.widget.CarouselRecyclerView{acda12 GFED..... ......I. 0,0-0,0 #7f090310 app:id/item_list}
-                      android.widget.LinearLayout{cac1736 VFE...CL. ........ 42,312-236,504 #1}
-                        android.widget.FrameLayout{ff685e3 V.E...... ........ 0,0-194,126 #7f0902c1 app:id/icon_and_uninstall_container}
-                          amazon.fluid.widget.SmallCoverStateContainer{9545be0 V.E...... ........ 43,18-151,126 #7f0902a9 app:id/grid_item_image}
-                            android.widget.ImageView{c298e99 V.ED..... ........ 0,0-108,108}
-                          android.widget.ImageView{a7a855e GFED..C.. ......I. 0,0-0,0 #7f09048e app:id/uninstall_badge}
-                        android.widget.TextView{f819d3f V.ED..... ........ 0,144-194,189 #7f0902aa app:id/grid_item_text}
-                      android.widget.LinearLayout{5cd0a10 VFE...CL. ........ 272,312-467,504 #2}
-                        android.widget.FrameLayout{5d3560c V.E...... ........ 0,0-195,126 #7f0902c1 app:id/icon_and_uninstall_container}
-                          amazon.fluid.widget.SmallCoverStateContainer{87b7b55 V.E...... ........ 43,18-151,126 #7f0902a9 app:id/grid_item_image}
-                            android.widget.ImageView{4e5996a V.ED..... ........ 0,0-108,108}
-                          android.widget.ImageView{c7cce5b GFED..C.. ......I. 0,0-0,0 #7f09048e app:id/uninstall_badge}
-                        android.widget.TextView{d65c6f8 V.ED..... ........ 0,144-195,189 #7f0902aa app:id/grid_item_text}
-                      android.widget.LinearLayout{c9a70c2 VFE...CL. ........ 503,312-697,504 #3}
-                        android.widget.FrameLayout{2c577d1 V.E...... ........ 0,0-194,126 #7f0902c1 app:id/icon_and_uninstall_container}
-                          amazon.fluid.widget.SmallCoverStateContainer{53be236 V.E...... ........ 43,18-151,126 #7f0902a9 app:id/grid_item_image}
-                            android.widget.ImageView{52ff537 V.ED..... ........ 0,0-108,108}
-                          android.widget.ImageView{1ac5aa4 GFED..C.. ......I. 0,0-0,0 #7f09048e app:id/uninstall_badge}
-                        android.widget.TextView{8d8c00d V.ED..... ........ 0,144-194,189 #7f0902aa app:id/grid_item_text}
-                      android.widget.LinearLayout{89417a4 VFE...CL. ........ 733,312-927,504 #4}
-                        android.widget.FrameLayout{5dbebc2 V.E...... ........ 0,0-194,126 #7f0902c1 app:id/icon_and_uninstall_container}
-                          amazon.fluid.widget.SmallCoverStateContainer{a84add3 V.E...... ........ 43,18-151,126 #7f0902a9 app:id/grid_item_image}
-                            android.widget.ImageView{ba67d10 V.ED..... ........ 0,0-108,108}
-                          android.widget.ImageView{a5e5009 GFED..C.. ......I. 0,0-0,0 #7f09048e app:id/uninstall_badge}
-                        android.widget.TextView{681020e V.ED..... ........ 0,144-194,189 #7f0902aa app:id/grid_item_text}
-                      android.widget.LinearLayout{b22d70e VFE...CL. ........ 963,312-1158,504 #5}
-                        android.widget.FrameLayout{862542f V.E...... ........ 0,0-195,126 #7f0902c1 app:id/icon_and_uninstall_container}
-                          amazon.fluid.widget.SmallCoverStateContainer{2de5a3c V.E...... ........ 43,18-151,126 #7f0902a9 app:id/grid_item_image}
-                            android.widget.ImageView{e92e3c5 V.ED..... ........ 0,0-108,108}
-                          android.widget.ImageView{54f311a GFED..C.. ......I. 0,0-0,0 #7f09048e app:id/uninstall_badge}
-                        android.widget.TextView{7ca044b V.ED..... ........ 0,144-195,189 #7f0902aa app:id/grid_item_text}
-                      android.widget.LinearLayout{31a390d VFE...CL. ........ 42,564-236,756 #6}
-                        android.widget.FrameLayout{b54de28 V.E...... ........ 0,0-194,126 #7f0902c1 app:id/icon_and_uninstall_container}
-                          amazon.fluid.widget.SmallCoverStateContainer{9c2f741 V.E...... ........ 43,18-151,126 #7f0902a9 app:id/grid_item_image}
-                            android.widget.ImageView{c9f44e6 V.ED..... ........ 0,0-108,108}
-                          android.widget.ImageView{6b29a27 GFED..C.. ......I. 0,0-0,0 #7f09048e app:id/uninstall_badge}
-                        android.widget.TextView{62db4d4 V.ED..... ........ 0,144-194,189 #7f0902aa app:id/grid_item_text}
-                      android.widget.LinearLayout{fb160d1 VFE...CL. ........ 272,564-467,756 #7}
-                        android.widget.FrameLayout{e86c67d V.E...... ........ 0,0-195,126 #7f0902c1 app:id/icon_and_uninstall_container}
-                          amazon.fluid.widget.SmallCoverStateContainer{18ac972 V.E...... ........ 43,18-151,126 #7f0902a9 app:id/grid_item_image}
-                            android.widget.ImageView{1a4b1c3 V.ED..... ........ 0,0-108,108}
-                          android.widget.ImageView{11b4a40 GFED..C.. ......I. 0,0-0,0 #7f09048e app:id/uninstall_badge}
-                        android.widget.TextView{6be4d79 V.ED..... ........ 0,144-195,189 #7f0902aa app:id/grid_item_text}
-                      android.widget.LinearLayout{9be5909 VFE...CL. ........ 503,564-697,756 #8}
-                        android.widget.FrameLayout{f380abe V.E...... ........ 0,0-194,126 #7f0902c1 app:id/icon_and_uninstall_container}
-                          amazon.fluid.widget.SmallCoverStateContainer{b16a71f V.E...... ........ 43,18-151,126 #7f0902a9 app:id/grid_item_image}
-                            android.widget.ImageView{8aca6c V.ED..... ........ 0,0-108,108}
-                          android.widget.ImageView{4d4835 GFED..C.. ......I. 0,0-0,0 #7f09048e app:id/uninstall_badge}
-                        android.widget.TextView{ae614ca V.ED..... ........ 0,144-194,189 #7f0902aa app:id/grid_item_text}
-                      android.widget.LinearLayout{65bb3f8 VFE...CL. ........ 733,564-927,756 #9}
-                        android.widget.FrameLayout{c88963b V.E...... ........ 0,0-194,126 #7f0902c1 app:id/icon_and_uninstall_container}
-                          amazon.fluid.widget.SmallCoverStateContainer{902158 V.E...... ........ 43,18-151,126 #7f0902a9 app:id/grid_item_image}
-                            android.widget.ImageView{99732b1 V.ED..... ........ 0,0-108,108}
-                          android.widget.ImageView{cb8b396 GFED..C.. ......I. 0,0-0,0 #7f09048e app:id/uninstall_badge}
-                        android.widget.TextView{d605b17 V.ED..... ........ 0,144-194,189 #7f0902aa app:id/grid_item_text}
-                      android.widget.LinearLayout{d60b73c VFE...CL. ........ 963,564-1158,756 #a}
-                        android.widget.FrameLayout{891fb04 V.E...... ........ 0,0-195,126 #7f0902c1 app:id/icon_and_uninstall_container}
-                          amazon.fluid.widget.SmallCoverStateContainer{9bb48ed V.E...... ........ 43,18-151,126 #7f0902a9 app:id/grid_item_image}
-                            android.widget.ImageView{9447322 V.ED..... ........ 0,0-108,108}
-                          android.widget.ImageView{b8591b3 GFED..C.. ......I. 0,0-0,0 #7f09048e app:id/uninstall_badge}
-                        android.widget.TextView{db5c370 V.ED..... ........ 0,144-195,189 #7f0902aa app:id/grid_item_text}
-                      android.widget.LinearLayout{e1c8637 VFE...CL. ........ 42,816-236,1008 #b}
-                        android.widget.FrameLayout{9086e9 V.E...... ........ 0,0-194,126 #7f0902c1 app:id/icon_and_uninstall_container}
-                          amazon.fluid.widget.SmallCoverStateContainer{7da9f6e V.E...... ........ 43,18-151,126 #7f0902a9 app:id/grid_item_image}
```

### `appops/all.stdout.txt`

```diff
--- before/appops/all.stdout.txt

+++ after/appops/all.stdout.txt

@@ -10,46 +10,46 @@

   Op mode watchers:
     Op COARSE_LOCATION:
-      #0: ModeCallback{6927b80 watchinguid=-1 flags=0x0 from uid=1000 pid=788}
+      #0: ModeCallback{53bd757 watchinguid=-1 flags=0x0 from uid=1000 pid=807}
     Op SYSTEM_ALERT_WINDOW:
-      #0: ModeCallback{d6b7f5d watchinguid=-1 flags=0x0 from uid=1000 pid=788}
+      #0: ModeCallback{77f9c52 watchinguid=-1 flags=0x0 from uid=1000 pid=807}
     Op PLAY_AUDIO:
-      #0: ModeCallback{2c68b04 watchinguid=-1 flags=0x0 from uid=u0a35 pid=1862}
-      #1: ModeCallback{3d9af11 watchinguid=-1 flags=0x0 from uid=u0a36 pid=1151}
-      #2: ModeCallback{cbc257d watchinguid=-1 flags=0x0 from uid=1000 pid=788}
-      #3: ModeCallback{e0ea861 watchinguid=-1 flags=0x0 from uid=u0a36 pid=1151}
+      #0: ModeCallback{30bdb10 watchinguid=-1 flags=0x0 from uid=u0a36 pid=1109}
+      #1: ModeCallback{5d6a71b watchinguid=-1 flags=0x0 from uid=1000 pid=807}
+      #2: ModeCallback{aeea002 watchinguid=-1 flags=0x0 from uid=u0a36 pid=1109}
+      #3: ModeCallback{f6a581e watchinguid=-1 flags=0x0 from uid=u0a36 pid=1109}
     Op TOAST_WINDOW:
-      #0: ModeCallback{d6b7f5d watchinguid=-1 flags=0x0 from uid=1000 pid=788}
+      #0: ModeCallback{77f9c52 watchinguid=-1 flags=0x0 from uid=1000 pid=807}
     Op GET_ACCOUNTS:
-      #0: ModeCallback{c5e716a watchinguid=-1 flags=0x0 from uid=1000 pid=788}
+      #0: ModeCallback{e1febdb watchinguid=-1 flags=0x0 from uid=1000 pid=807}
     Op RUN_IN_BACKGROUND:
-      #0: ModeCallback{bc83b4 watchinguid=-1 flags=0x0 from uid=1000 pid=788}
+      #0: ModeCallback{158355d watchinguid=-1 flags=0x0 from uid=1000 pid=807}
     Op RUN_ANY_IN_BACKGROUND:
-      #0: ModeCallback{94b1f03 watchinguid=-1 flags=0x0 from uid=1000 pid=788}
+      #0: ModeCallback{2658e39 watchinguid=-1 flags=0x0 from uid=1000 pid=807}
   Package mode watchers:
-    Pkg amazon.speech.sim:
-      #0: ModeCallback{2c68b04 watchinguid=-1 flags=0x0 from uid=u0a35 pid=1862}
     Pkg com.android.systemui:
-      #0: ModeCallback{3d9af11 watchinguid=-1 flags=0x0 from uid=u0a36 pid=1151}
-      #1: ModeCallback{e0ea861 watchinguid=-1 flags=0x0 from uid=u0a36 pid=1151}
+      #0: ModeCallback{30bdb10 watchinguid=-1 flags=0x0 from uid=u0a36 pid=1109}
+      #1: ModeCallback{aeea002 watchinguid=-1 flags=0x0 from uid=u0a36 pid=1109}
+      #2: ModeCallback{f6a581e watchinguid=-1 flags=0x0 from uid=u0a36 pid=1109}
   All op mode watchers:
-    170b355: ModeCallback{c5e716a watchinguid=-1 flags=0x0 from uid=1000 pid=788}
-    44d2b17: ModeCallback{2c68b04 watchinguid=-1 flags=0x0 from uid=u0a35 pid=1862}
-    6004534: ModeCallback{d6b7f5d watchinguid=-1 flags=0x0 from uid=1000 pid=788}
-    6575338: ModeCallback{3d9af11 watchinguid=-1 flags=0x0 from uid=u0a36 pid=1151}
-    6712fd4: ModeCallback{cbc257d watchinguid=-1 flags=0x0 from uid=1000 pid=788}
-    8d1d887: ModeCallback{bc83b4 watchinguid=-1 flags=0x0 from uid=1000 pid=788}
-    8ea1fc8: ModeCallback{e0ea861 watchinguid=-1 flags=0x0 from uid=u0a36 pid=1151}
-    b20e003: ModeCallback{6927b80 watchinguid=-1 flags=0x0 from uid=1000 pid=788}
-    fbda3b2: ModeCallback{94b1f03 watchinguid=-1 flags=0x0 from uid=1000 pid=788}
+    ccc3d3: ModeCallback{30bdb10 watchinguid=-1 flags=0x0 from uid=u0a36 pid=1109}
+    1fdf459: ModeCallback{f6a581e watchinguid=-1 flags=0x0 from uid=u0a36 pid=1109}
+    2105d2a: ModeCallback{5d6a71b watchinguid=-1 flags=0x0 from uid=1000 pid=807}
+    3761334: ModeCallback{158355d watchinguid=-1 flags=0x0 from uid=1000 pid=807}
+    6f09d4d: ModeCallback{aeea002 watchinguid=-1 flags=0x0 from uid=u0a36 pid=1109}
+    7d4bcea: ModeCallback{e1febdb watchinguid=-1 flags=0x0 from uid=1000 pid=807}
+    99198dd: ModeCallback{77f9c52 watchinguid=-1 flags=0x0 from uid=1000 pid=807}
+    b9f78d6: ModeCallback{53bd757 watchinguid=-1 flags=0x0 from uid=1000 pid=807}
+    d481600: ModeCallback{2658e39 watchinguid=-1 flags=0x0 from uid=1000 pid=807}
   All op active watchers:
-    df5688c ->
+    fa9319a ->
         [SYSTEM_ALERT_WINDOW, CAMERA, RECORD_AUDIO]
-        ActiveCallback{f25d2e0 watchinguid=-1 from uid=u0a36 pid=1151}
+        ActiveCallback{7844579 watchinguid=-1 from uid=u0a36 pid=1109}
   Clients:
-    android.os.Binder@6a41ab5:
-      ClientState{mAppToken=android.os.Binder@6a41ab5, pid=788}
+    android.os.Binder@c67fa33:
+      ClientState{mAppToken=android.os.Binder@c67fa33, pid=807}
       Started ops:
         uid=1000 pkg=android op=MONITOR_LOCATION
-        uid=10036 pkg=com.android.systemui op=MONITOR_LOCATION
+        uid=10036 pkg=com.android.systemui op=SYSTEM_ALERT_WINDOW
+        uid=1041 pkg=audioserver op=WAKE_LOCK
 
   Uid 1000:
@@ -58,187 +58,190 @@

     Package com.amazon.platform.fdrw:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:26:28.449 (-1h26m40s4ms)
+          Access: pers  = 2026-08-03 14:26:28.449 (-1h27m56s282ms)
     Package amazon.fireos:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 09:20:46.628 (-6h32m21s825ms)
+          Access: pers  = 2026-08-03 09:20:46.628 (-6h33m38s103ms)
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2026-03-26 23:43:10.017 (-129d16h9m58s436ms)
+          Reject: pers  = 2026-03-26 23:43:10.017 (-129d16h11m14s714ms)
     Package com.amazon.device.logmanager:
       RUN_IN_BACKGROUND (allow): 
-          Access: pers  = 2026-08-03 14:35:30.788 (-1h17m37s665ms)
+          Access: pers  = 2026-08-03 14:35:30.788 (-1h18m53s943ms)
     Package com.amazon.accessorynotifier:
       RUN_IN_BACKGROUND (allow): 
-          Access: pers  = 2026-08-03 14:35:32.265 (-1h17m36s188ms)
+          Access: pers  = 2026-08-03 14:35:32.265 (-1h18m52s466ms)
     Package com.amazon.android.marketplace:
       WRITE_SETTINGS (default): 
-          Reject: pers  = 2025-12-06 20:49:21.625 (-239d19h3m46s828ms)
-      RECORD_AUDIO (allow): 
-          Access: pers  = 2026-04-06 07:13:25.558 (-119d8h39m42s895ms)
+          Reject: pers  = 2025-12-06 20:49:21.625 (-239d19h5m3s106ms)
+      RECORD_AUDIO (allow): 
+          Access: pers  = 2026-04-06 07:13:25.558 (-119d8h40m59s173ms)
     Package com.amazon.storagemanager:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-07-10 20:57:29.503 (-23d18h55m38s950ms)
+          Access: pers  = 2026-07-10 20:57:29.503 (-23d18h56m55s228ms)
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2026-08-03 07:45:44.987 (-8h7m23s466ms)
-      READ_EXTERNAL_STORAGE (allow): 
-          Access: pers  = 2026-08-03 07:45:41.642 (-8h7m26s811ms)
+          Reject: pers  = 2026-08-03 07:45:44.987 (-8h8m39s744ms)
+      READ_EXTERNAL_STORAGE (allow): 
+          Access: pers  = 2026-08-03 07:45:41.642 (-8h8m43s89ms)
     Package android:
       COARSE_LOCATION (allow): 
       FINE_LOCATION (allow / switch COARSE_LOCATION=allow): 
-          Access: pers  = 2026-08-03 14:35:23.584 (-1h17m44s869ms)
+          Access: pers  = 2026-08-03 15:54:17.159 (-7s572ms)
       READ_CALENDAR (allow): 
-          Access: pers  = 2026-08-03 14:35:28.221 (-1h17m40s232ms)
-      RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:29:54.943 (-1h23m13s510ms)
+          Access: pers  = 2026-08-03 15:54:23.606 (-1s125ms)
+      RECORD_AUDIO (allow): 
+          Access: pers  = 2026-08-03 14:29:54.943 (-1h24m29s788ms)
       AUDIO_MEDIA_VOLUME (allow): 
-          Access: pers  = 2026-08-01 21:11:23.169 (-1d18h41m45s284ms)
-      WAKE_LOCK (allow): 
-          Access: pers  = 2026-08-03 15:52:21.338 (-47s115ms)
-                  fg    = 2026-04-11 03:58:41.049 (-114d11h54m27s404ms)
-          duration=+2ms
+          Access: pers  = 2026-08-01 21:11:23.169 (-1d18h43m1s562ms)
+      WAKE_LOCK (allow): 
+          Access: pers  = 2026-08-03 15:54:24.359 (-372ms)
+                  fg    = 2026-04-11 03:58:41.049 (-114d11h55m43s682ms)
+          duration=+1ms
       MONITOR_LOCATION (allow / switch COARSE_LOCATION=allow): 
-          Access: pers  = 2026-08-03 14:35:23.577 (-1h17m44s876ms)
-                  fg    = 2026-04-11 03:58:41.049 (-114d11h54m27s404ms)
-          Running start at: +1h17m43s883ms
+          Access: pers  = 2026-08-03 15:54:17.151 (-7s580ms)
+                  fg    = 2026-04-11 03:58:41.049 (-114d11h55m43s682ms)
+          Running start at: +6s477ms
           startNesting=1
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2026-08-03 15:52:10.024 (-58s429ms)
+          Reject: pers  = 2026-08-03 15:54:17.150 (-7s581ms)
       TURN_ON_SCREEN (allow): 
-          Access: pers  = 2026-07-10 22:35:34.059 (-23d17h17m34s394ms)
+          Access: pers  = 2026-07-10 22:35:34.059 (-23d17h18m50s672ms)
     Package com.android.providers.settings:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2025-12-06 20:11:38.894 (-239d19h41m29s559ms)
+          Access: pers  = 2025-12-06 20:11:38.894 (-239d19h42m45s837ms)
     Package com.android.keychain:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2025-12-07 15:30:49.435 (-239d0h22m19s18ms)
+          Access: pers  = 2025-12-07 15:30:49.435 (-239d0h23m35s296ms)
     Package com.amazon.device.sale.service:
       RUN_IN_BACKGROUND (allow): 
-          Access: pers  = 2026-08-03 14:35:42.055 (-1h17m26s398ms)
+          Access: pers  = 2026-08-03 14:35:42.055 (-1h18m42s676ms)
     Package com.android.settings:
       WRITE_SETTINGS (default): 
-          Reject: pers  = 2026-08-01 21:54:35.634 (-1d17h58m32s819ms)
+          Reject: pers  = 2026-08-01 21:54:35.634 (-1d17h59m49s97ms)
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2026-08-03 12:07:40.636 (-3h45m27s817ms)
+          Reject: pers  = 2026-08-03 12:07:40.636 (-3h46m44s95ms)
       TOAST_WINDOW (allow): 
-          Access: pers  = 2025-12-07 16:06:55.266 (-238d23h46m13s187ms)
+          Access: pers  = 2025-12-07 16:06:55.266 (-238d23h47m29s465ms)
           duration=+4s550ms
     Package android.amazon.perm:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2025-12-06 19:11:18.089 (-239d20h41m50s364ms)
+          Access: pers  = 2025-12-06 19:11:18.089 (-239d20h43m6s642ms)
     Package com.android.wallpaperbackup:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:32:08.417 (-1h21m0s36ms)
+          Access: pers  = 2026-08-03 14:32:08.417 (-1h22m16s314ms)
     Package com.android.location.fused:
       COARSE_LOCATION (allow): 
       FINE_LOCATION (allow / switch COARSE_LOCATION=allow): 
-          Access: pers  = 2025-12-06 18:57:45.955 (-239d20h55m22s498ms)
-      RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:35:13.887 (-1h17m54s566ms)
+          Access: pers  = 2025-12-06 18:57:45.955 (-239d20h56m38s776ms)
+      RECORD_AUDIO (allow): 
+          Access: pers  = 2026-08-03 14:35:13.887 (-1h19m10s844ms)
       MONITOR_LOCATION (allow / switch COARSE_LOCATION=allow): 
-          Access: pers  = 2025-12-06 19:03:04.992 (-239d20h50m3s461ms)
+          Access: pers  = 2025-12-06 19:03:04.992 (-239d20h51m19s739ms)
           duration=+5m20s391ms
+    Package com.here.odnp.service:
+      RECORD_AUDIO (allow): 
+          Access: pers  = 2026-08-03 15:54:11.972 (-12s759ms)
     Package com.amazon.settings:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 07:45:33.063 (-8h7m35s390ms)
+          Access: pers  = 2026-08-03 07:45:33.063 (-8h8m51s668ms)
       TOAST_WINDOW (allow): 
-          Access: pers  = 2026-07-10 21:04:18.363 (-23d18h48m50s90ms)
+          Access: pers  = 2026-07-10 21:04:18.363 (-23d18h50m6s368ms)
           duration=+5s388ms
     Package com.amazon.shpm:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 09:19:52.283 (-6h33m16s170ms)
+          Access: pers  = 2026-08-03 09:19:52.283 (-6h34m32s448ms)
     Package com.amazon.fireos.cirruscloud:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:33:40.524 (-1h19m27s929ms)
+          Access: pers  = 2026-08-03 14:33:40.524 (-1h20m44s207ms)
   Uid 1002:
     state=cch  
     Package com.android.bluetooth:
       WAKE_LOCK (allow): 
-          Access: pers  = 2025-12-06 18:56:41.294 (-239d20h56m27s159ms)
-                  bg    = 2025-12-06 18:56:41.291 (-239d20h56m27s162ms)
+          Access: pers  = 2025-12-06 18:56:41.294 (-239d20h57m43s437ms)
+                  bg    = 2025-12-06 18:56:41.291 (-239d20h57m43s440ms)
           duration=+10ms
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2025-12-06 18:56:24.496 (-239d20h56m43s957ms)
-      READ_EXTERNAL_STORAGE (allow): 
-          Access: pers  = 2025-12-06 18:56:28.924 (-239d20h56m39s529ms)
-                  cch   = 2025-12-06 18:56:23.700 (-239d20h56m44s753ms)
-      WRITE_EXTERNAL_STORAGE (allow): 
-          Access: pers  = 2025-12-06 18:56:28.924 (-239d20h56m39s529ms)
-                  cch   = 2025-12-06 18:56:23.700 (-239d20h56m44s753ms)
+          Reject: pers  = 2025-12-06 18:56:24.496 (-239d20h58m0s235ms)
+      READ_EXTERNAL_STORAGE (allow): 
+          Access: pers  = 2025-12-06 18:56:28.924 (-239d20h57m55s807ms)
+                  cch   = 2025-12-06 18:56:23.700 (-239d20h58m1s31ms)
+      WRITE_EXTERNAL_STORAGE (allow): 
+          Access: pers  = 2025-12-06 18:56:28.924 (-239d20h57m55s807ms)
+                  cch   = 2025-12-06 18:56:23.700 (-239d20h58m1s31ms)
```

### `appops/firelauncher.stdout.txt`

```diff
--- before/appops/firelauncher.stdout.txt

+++ after/appops/firelauncher.stdout.txt

@@ -1,4 +1,4 @@

-TAKE_AUDIO_FOCUS: allow; time=+239d20h41m33s131ms ago
-READ_EXTERNAL_STORAGE: allow; time=+1h17m41s910ms ago
-WRITE_EXTERNAL_STORAGE: allow; time=+1h17m41s910ms ago
-REQUEST_DELETE_PACKAGES: allow; time=+238d23h48m34s856ms ago
+TAKE_AUDIO_FOCUS: allow; time=+239d20h42m49s352ms ago
+READ_EXTERNAL_STORAGE: allow; time=+815ms ago
+WRITE_EXTERNAL_STORAGE: allow; time=+815ms ago
+REQUEST_DELETE_PACKAGES: allow; time=+238d23h49m51s77ms ago
```

### `appops/microsoft.stdout.txt`

```diff
--- before/appops/microsoft.stdout.txt

+++ after/appops/microsoft.stdout.txt

@@ -1,5 +1,5 @@

 COARSE_LOCATION: allow
-FINE_LOCATION: allow; time=+30s225ms ago
-READ_EXTERNAL_STORAGE: allow; time=+30s320ms ago
-WRITE_EXTERNAL_STORAGE: allow; time=+30s320ms ago
-BIND_ACCESSIBILITY_SERVICE: allow; time=+53s420ms ago
+FINE_LOCATION: allow; time=+2h9m47s117ms ago
+READ_EXTERNAL_STORAGE: allow; time=+1h18m45s146ms ago
+WRITE_EXTERNAL_STORAGE: allow; time=+1h18m45s146ms ago
+BIND_ACCESSIBILITY_SERVICE: allow; time=+10s65ms ago
```

### `appops/test_p0.exit_code.txt`

```diff
--- before/appops/test_p0.exit_code.txt

+++ after/appops/test_p0.exit_code.txt

@@ -1 +1 @@

-255
+0
```

### `appops/test_p0.stderr.txt`

```diff
--- before/appops/test_p0.stderr.txt

+++ after/appops/test_p0.stderr.txt

@@ -1 +0,0 @@

-Error: No UID for org.fireosresearch.home.p0 in user 0
```

### `appops/test_p0.stdout.txt`

```diff
--- before/appops/test_p0.stdout.txt

+++ after/appops/test_p0.stdout.txt

@@ -0,0 +1 @@

+No operations.
```

### `devices.stdout.txt`

```diff
--- before/devices.stdout.txt

+++ after/devices.stdout.txt

@@ -1,3 +1,3 @@

 List of devices attached
-G001LT0511550CFT       device usb:1-1 product:trona model:KFTRWI device:trona transport_id:10
+G001LT0511550CFT       device usb:1-1 product:trona model:KFTRWI device:trona transport_id:11
 
```

### `metadata.tsv`

```diff
--- before/metadata.tsv

+++ after/metadata.tsv

@@ -1,3 +1,3 @@

-test_id=PHASE3C-PREFERRED-P0-02-before
+test_id=PHASE3C-PREFERRED-P0-02-after_reboot
 serial=G001LT0511550CFT
-timestamp_utc=2026-08-03T07:53:04Z
+timestamp_utc=2026-08-03T07:54:18Z
```

### `overlay/dump.stdout.txt`

```diff
--- before/overlay/dump.stdout.txt

+++ after/overlay/dump.stdout.txt

@@ -46,3 +46,3 @@

 Default overlays: 
 PackageInfo cache
-    7 package(s)
+    6 package(s)
```

### `package/all_packages.stdout.txt`

```diff
--- before/package/all_packages.stdout.txt

+++ after/package/all_packages.stdout.txt

@@ -153,4 +153,5 @@

 package:/system/priv-app/amazon.speech.davs.davcservice/amazon.speech.davs.davcservice.apk=amazon.speech.davs.davcservice
 package:/system/priv-app/com.amazon.geo.client.maps/com.amazon.geo.client.maps.apk=com.amazon.geo.client.maps
+package:/data/app/org.fireosresearch.home.p0-Er8RUFCd6pl-r5QmHpD9PQ==/base.apk=org.fireosresearch.home.p0
 package:/system/app/jp.co.omronsoft.iwnnime.mlaz/jp.co.omronsoft.iwnnime.mlaz.apk=jp.co.omronsoft.iwnnime.mlaz
 package:/system/priv-app/com.amazon.afe.app-stub/com.amazon.afe.app-stub.apk=com.amazon.afe.app
```

### `package/firelauncher.stdout.txt`

```diff
--- before/package/firelauncher.stdout.txt

+++ after/package/firelauncher.stdout.txt

@@ -2,5 +2,5 @@

   Schemes:
       amzn:
-        2be7ead com.amazon.firelauncher/.Launcher filter f41900c
+        f0c836e com.amazon.firelauncher/.Launcher filter 74a033a
           Action: "android.intent.action.VIEW"
           Category: "android.intent.category.DEFAULT"
@@ -10,9 +10,9 @@

   Non-Data Actions:
       com.amazon.firelauncher.REQUEST_LOCATION_PERMISSION:
-        2be7ead com.amazon.firelauncher/.Launcher filter 13c7f3f
+        f0c836e com.amazon.firelauncher/.Launcher filter e8b2a65
           Action: "com.amazon.firelauncher.REQUEST_LOCATION_PERMISSION"
           Category: "android.intent.category.DEFAULT"
       com.amazon.firelauncher.intent.action.TUTORIALDONE:
-        2be7ead com.amazon.firelauncher/.Launcher filter 8abaf5e
+        f0c836e com.amazon.firelauncher/.Launcher filter 247175c
           Action: "android.intent.action.MAIN"
           Action: "com.amazon.firelauncher.intent.action.ALEXA_TUTORIAL"
@@ -23,5 +23,5 @@

           mPriority=50, mOrder=0, mHasPartialTypes=false
       com.amazon.firelauncher.intent.action.ALEXA_TUTORIAL:
-        2be7ead com.amazon.firelauncher/.Launcher filter 8abaf5e
+        f0c836e com.amazon.firelauncher/.Launcher filter 247175c
           Action: "android.intent.action.MAIN"
           Action: "com.amazon.firelauncher.intent.action.ALEXA_TUTORIAL"
@@ -32,5 +32,5 @@

           mPriority=50, mOrder=0, mHasPartialTypes=false
       android.intent.action.MAIN:
-        2be7ead com.amazon.firelauncher/.Launcher filter 8abaf5e
+        f0c836e com.amazon.firelauncher/.Launcher filter 247175c
           Action: "android.intent.action.MAIN"
           Action: "com.amazon.firelauncher.intent.action.ALEXA_TUTORIAL"
@@ -40,15 +40,15 @@

           Category: "android.intent.category.DEFAULT"
           mPriority=50, mOrder=0, mHasPartialTypes=false
-        95eeef1 com.amazon.firelauncher/.LauncherUserSettings filter e162d55
+        e93433 com.amazon.firelauncher/.LauncherUserSettings filter 5b3beb
           Action: "android.intent.action.MAIN"
           Action: "android.intent.action.VIEW"
           Category: "amazon.intent.category.SETTINGS"
       android.intent.action.VIEW:
-        95eeef1 com.amazon.firelauncher/.LauncherUserSettings filter e162d55
+        e93433 com.amazon.firelauncher/.LauncherUserSettings filter 5b3beb
           Action: "android.intent.action.MAIN"
           Action: "android.intent.action.VIEW"
           Category: "amazon.intent.category.SETTINGS"
       com.amazon.firelauncher.intent.action.TUTORIAL:
-        2be7ead com.amazon.firelauncher/.Launcher filter 8abaf5e
+        f0c836e com.amazon.firelauncher/.Launcher filter 247175c
           Action: "android.intent.action.MAIN"
           Action: "com.amazon.firelauncher.intent.action.ALEXA_TUTORIAL"
@@ -62,22 +62,22 @@

   Non-Data Actions:
       com.amazon.action.PACKAGE_RECENCY_NOTIFICATION:
-        190d9fd com.amazon.firelauncher/com.amazon.fireappscardproducer.service.SystemNotificationProducerService$PackageRecencyReceiver filter bac2157
+        5b5d32c com.amazon.firelauncher/com.amazon.fireappscardproducer.service.SystemNotificationProducerService$PackageRecencyReceiver filter 816e03d
           Action: "com.amazon.action.PACKAGE_RECENCY_NOTIFICATION"
           Category: "android.intent.category.DEFAULT"
       com.amazon.mp3.USER_BENEFIT_UPDATE:
-        26cecf0 com.amazon.firelauncher/.reccardproducer.ProducerService$MusicUnlimitedRegistrationReceiver filter 6530661
+        7ec1548 com.amazon.firelauncher/.reccardproducer.ProducerService$MusicUnlimitedRegistrationReceiver filter f2f5ed7
           Action: "com.amazon.mp3.USER_BENEFIT_UPDATE"
       com.amazon.cmsfirecardproducer.REMOVE_FROM_DEVICE:
-        2ccefae com.amazon.firelauncher/com.amazon.fireappscardproducer.service.CardActionService$RemoveFromDeviceReceiverOld filter 92192d
+        8cf43c6 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.CardActionService$RemoveFromDeviceReceiverOld filter 8bcc183
           Action: "com.amazon.cmsfirecardproducer.REMOVE_FROM_DEVICE"
       com.amazon.cmsfirecardproducer.REMOVE_FROM_HOME:
-        5ed3599 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.CardActionService$RemoveFromHomeReceiverOld filter abce444
+        236b911 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.CardActionService$RemoveFromHomeReceiverOld filter 63e4032
           Action: "com.amazon.cmsfirecardproducer.REMOVE_FROM_HOME"
       com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_APPS:
-        346ad40 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.CardActionService$RemoveFromHomeReceiver filter 7ae9e62
+        a00bf98 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.CardActionService$RemoveFromHomeReceiver filter 9a67f00
           Action: "com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_APPS"
           Action: "com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_GAMES"
       com.amazon.firelauncher.appmanager.APPS_REMOVED:
-        542a918 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$PackageChangeReceiver filter 42f698
+        62c670 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$PackageChangeReceiver filter a4cfa6
           Action: "com.amazon.firelauncher.appmanager.APPS_ADDED"
           Action: "com.amazon.firelauncher.appmanager.APPS_REMOVED"
@@ -85,17 +85,17 @@

           Action: "com.amazon.firelauncher.APP_RECENCY_REBUILD"
       com.amazon.intent.SYNC:
-        515aba9 com.amazon.firelauncher/.ui.GlobalSyncReceiver filter 79be368
+        ed3c946 com.amazon.firelauncher/.ui.GlobalSyncReceiver filter 3d53cf6
           Action: "com.amazon.intent.SYNC"
-        23dc52e com.amazon.firelauncher/com.amazon.heroshoveler.weather.WeatherRefreshService$GlobalSyncReceiver filter 719b381
+        9a43707 com.amazon.firelauncher/com.amazon.heroshoveler.weather.WeatherRefreshService$GlobalSyncReceiver filter 6a218f7
           Action: "com.amazon.intent.SYNC"
-        5f528cf com.amazon.firelauncher/.cardproducer.LauncherProducerService$GlobalSyncReceiver filter 6decbac
+        a19c034 com.amazon.firelauncher/.cardproducer.LauncherProducerService$GlobalSyncReceiver filter 5ed8fda
           Action: "com.amazon.intent.SYNC"
-        aeba25c com.amazon.firelauncher/com.amazon.hintscardproducer.HintsCardRefreshService$GlobalSyncReceiver filter 5c3e674
+        1bede5d com.amazon.firelauncher/com.amazon.hintscardproducer.HintsCardRefreshService$GlobalSyncReceiver filter c2319e2
           Action: "com.amazon.intent.SYNC"
       android.intent.action.DEVICE_STORAGE_LOW:
-        54765d5 com.amazon.firelauncher/.images.storage.LowStorageReceiver filter 3e38b7c
+        a4c3582 com.amazon.firelauncher/.images.storage.LowStorageReceiver filter f7ac82a
           Action: "android.intent.action.DEVICE_STORAGE_LOW"
       com.amazon.firelauncher.appmanager.APPS_ADDED:
-        542a918 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$PackageChangeReceiver filter 42f698
+        62c670 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$PackageChangeReceiver filter a4cfa6
           Action: "com.amazon.firelauncher.appmanager.APPS_ADDED"
           Action: "com.amazon.firelauncher.appmanager.APPS_REMOVED"
@@ -103,80 +103,80 @@

           Action: "com.amazon.firelauncher.APP_RECENCY_REBUILD"
       com.amazon.firelauncher.START_EDIT_MODE_EXTERNAL:
-        49df803 com.amazon.firelauncher/.appsgrid.StartEditModeReceiver filter ce0d68b
+        fa0dd8 com.amazon.firelauncher/.appsgrid.StartEditModeReceiver filter 548591
           Action: "com.amazon.firelauncher.START_EDIT_MODE_EXTERNAL"
           mPriority=100, mOrder=0, mHasPartialTypes=false
       com.amazon.device.messaging.intent.REGISTRATION:
-        e519aae com.amazon.firelauncher/com.amazon.firecard.deviceclient.clients.MultiplexingMessageReceiver filter 1f35075
+        d850e87 com.amazon.firelauncher/com.amazon.firecard.deviceclient.clients.MultiplexingMessageReceiver filter 496dc0b
           Action: "com.amazon.device.messaging.intent.REGISTRATION"
           Action: "com.amazon.device.messaging.intent.RECEIVE"
           Category: "com.amazon.firelauncher"
       com.amazon.firelauncher.action.REC_SUPPRESS:
-        33b3955 com.amazon.firelauncher/.reccardproducer.ProducerService$ItemSuppressionReceiver filter 50277dc
+        18f302 com.amazon.firelauncher/.reccardproducer.ProducerService$ItemSuppressionReceiver filter e39a38a
           Action: "com.amazon.firelauncher.action.REC_SUPPRESS"
       com.amazon.firelauncher.action.UPSELL_TAPPED_NOTIFICATION:
-        a4080e com.amazon.firelauncher/.reccardproducer.ProducerService$UpsellTappedNotificationReceiver filter c2d35c8
+        29c5c67 com.amazon.firelauncher/.reccardproducer.ProducerService$UpsellTappedNotificationReceiver filter 1966e56
           Action: "com.amazon.firelauncher.action.UPSELL_TAPPED_NOTIFICATION"
       com.amazon.dcp.sso.action.session.users.changed:
-        603e6a5 com.amazon.firelauncher/com.amazon.identity.auth.accounts.SessionUserChangedToAccountForPackageChangedAdpater filter 11d2099
+        a7de012 com.amazon.firelauncher/com.amazon.identity.auth.accounts.SessionUserChangedToAccountForPackageChangedAdpater filter e7151cf
           Action: "com.amazon.dcp.sso.action.session.users.changed"
       com.amazon.firelauncher.action.WEBLAB_UPDATE:
-        aca5e32 com.amazon.firelauncher/.reccardproducer.ProducerService$UpNextWeblabUpdateReceiver filter 834766b
+        93ee43b com.amazon.firelauncher/.reccardproducer.ProducerService$UpNextWeblabUpdateReceiver filter 4402071
           Action: "com.amazon.firelauncher.action.WEBLAB_UPDATE"
       com.amazon.firecard.action.REFRESH_CARDS:
-        dd318df com.amazon.firelauncher/com.amazon.heroshoveler.weather.RefreshCardsBroadcastReceiver filter 1ffce14
+        3f29104 com.amazon.firelauncher/com.amazon.heroshoveler.weather.RefreshCardsBroadcastReceiver filter 2903282
           Action: "com.amazon.firecard.action.REFRESH_CARDS"
-        fefb92c com.amazon.firelauncher/.cardproducer.LauncherProducerService$RefreshCardsReceiver filter 2851b9
+        38f26ed com.amazon.firelauncher/.cardproducer.LauncherProducerService$RefreshCardsReceiver filter 1fd2fef
           Action: "com.amazon.firecard.action.REFRESH_CARDS"
           Action: "android.intent.action.LOCALE_CHANGED"
-        7856ff5 com.amazon.firelauncher/com.amazon.firecard.deviceclient.CloudCardEventService$RefreshCardsReceiver filter 69b180a
+        a1df922 com.amazon.firelauncher/com.amazon.firecard.deviceclient.CloudCardEventService$RefreshCardsReceiver filter 6c93ae8
           Action: "com.amazon.firecard.action.REFRESH_CARDS"
-        86b818a com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$RefreshCardsReceiver filter 318787b
+        2f79fb3 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$RefreshCardsReceiver filter b10f501
           Action: "com.amazon.firecard.action.REFRESH_CARDS"
-        1fa63fb com.amazon.firelauncher/.reccardproducer.ProducerService$RefreshCardsReceiver filter 7a41b29
+        d89b970 com.amazon.firelauncher/.reccardproducer.ProducerService$RefreshCardsReceiver filter 1fff2df
           Action: "com.amazon.firecard.action.REFRESH_CARDS"
-        1353c18 com.amazon.firelauncher/com.amazon.hintscardproducer.HintsCardRefreshService$RefreshCardsReceiver filter 9220e47
+        6c444e9 com.amazon.firelauncher/com.amazon.hintscardproducer.HintsCardRefreshService$RefreshCardsReceiver filter f6552ad
           Action: "com.amazon.firecard.action.REFRESH_CARDS"
       com.amazon.firelauncher.action.FOR_YOU_CHANNEL_VISIBLE:
-        f2841eb com.amazon.firelauncher/com.amazon.heroshoveler.weather.WeatherRefreshBroadcastReceiver filter 867a4b2
+        bf65ea0 com.amazon.firelauncher/com.amazon.heroshoveler.weather.WeatherRefreshBroadcastReceiver filter 9a701d0
           Action: "com.amazon.firelauncher.action.FOR_YOU_CHANNEL_VISIBLE"
-        efbdb48 com.amazon.firelauncher/.cardproducer.LauncherProducerService$ChannelVisibilityChangeReceiver filter ea0e55f
+        87b3a59 com.amazon.firelauncher/.cardproducer.LauncherProducerService$ChannelVisibilityChangeReceiver filter 6c88585
           Action: "com.amazon.firelauncher.action.FOR_YOU_CHANNEL_VISIBLE"
-        fbc7de1 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$ChannelVisibilityChangeReceiver filter 3c600b0
+        215261e com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$ChannelVisibilityChangeReceiver filter f8c2d7e
           Action: "com.amazon.firelauncher.action.FOR_YOU_CHANNEL_VISIBLE"
       com.amazon.identity.auth.account.removed.on.device:
-        b51fab7 com.amazon.firelauncher/.cardproducer.LauncherProducerService$AccountChangeReceiver filter 82759fe
+        b335ef com.amazon.firelauncher/.cardproducer.LauncherProducerService$AccountChangeReceiver filter f426afc
           Action: "com.amazon.identity.auth.account.added.on.device"
           Action: "com.amazon.identity.auth.account.removed.on.device"
       android.intent.action.LOCALE_CHANGED:
-        f41c31 com.amazon.firelauncher/com.amazon.heroshoveler.weather.WeatherRefreshService$LocaleChangedReceiver filter 168ec26
+        db6502e com.amazon.firelauncher/com.amazon.heroshoveler.weather.WeatherRefreshService$LocaleChangedReceiver filter caa1364
           Action: "android.intent.action.LOCALE_CHANGED"
-        76d1f16 com.amazon.firelauncher/amazon.alexa.locale.AlexaLocaleHelper filter c15b780
+        4a257cf com.amazon.firelauncher/amazon.alexa.locale.AlexaLocaleHelper filter 612f4ce
           Action: "android.intent.action.LOCALE_CHANGED"
-        fefb92c com.amazon.firelauncher/.cardproducer.LauncherProducerService$RefreshCardsReceiver filter 2851b9
+        38f26ed com.amazon.firelauncher/.cardproducer.LauncherProducerService$RefreshCardsReceiver filter 1fd2fef
           Action: "com.amazon.firecard.action.REFRESH_CARDS"
           Action: "android.intent.action.LOCALE_CHANGED"
-        9f32097 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.SystemNotificationProducerService$LocaleChangeReceiver filter 3daaad6
+        8faa55c com.amazon.firelauncher/com.amazon.fireappscardproducer.service.SystemNotificationProducerService$LocaleChangeReceiver filter f6b1d94
           Action: "android.intent.action.LOCALE_CHANGED"
-        c3d1284 com.amazon.firelauncher/.reccardproducer.ProducerService$LocaleChangedReceiver filter 73e44f
+        242a065 com.amazon.firelauncher/.reccardproducer.ProducerService$LocaleChangedReceiver filter d0ed9f5
           Action: "android.intent.action.LOCALE_CHANGED"
-        7bd4a6d com.amazon.firelauncher/com.amazon.hintscardproducer.HintsCardRefreshService$LocaleChangedReceiver filter 658a79d
+        65b413a com.amazon.firelauncher/com.amazon.hintscardproducer.HintsCardRefreshService$LocaleChangedReceiver filter 3a11173
           Action: "android.intent.action.LOCALE_CHANGED"
       com.amazon.firelauncher.action.TAB_SETTINGS_CHANGED:
-        97bcf05 com.amazon.firelauncher/.reccardproducer.ProducerService$TabSuppressionReceiver filter 2ba40e5
+        d5a6cf2 com.amazon.firelauncher/.reccardproducer.ProducerService$TabSuppressionReceiver filter 51addfb
           Action: "com.amazon.firelauncher.action.TAB_SETTINGS_CHANGED"
       com.amazon.firelauncher.action.HOST_APP_COLD_START_ACTION:
-        89a88c5 com.amazon.firelauncher/.reccardproducer.ProducerService$ColdStartReceiver filter d517586
+        93f5bb2 com.amazon.firelauncher/.reccardproducer.ProducerService$ColdStartReceiver filter 75b13c4
           Action: "com.amazon.firelauncher.action.HOST_APP_COLD_START_ACTION"
-        cd6721a com.amazon.firelauncher/com.amazon.hintscardproducer.HintsCardRefreshService$ColdStartReceiver filter e6747e3
+        b967703 com.amazon.firelauncher/com.amazon.hintscardproducer.HintsCardRefreshService$ColdStartReceiver filter 6316ca9
           Action: "com.amazon.firelauncher.action.HOST_APP_COLD_START_ACTION"
       android.intent.action.TIME_SET:
-        73f9c com.amazon.firelauncher/com.amazon.identity.auth.device.storage.LambortishClock$ChangeTimestampsBroadcastReceiver filter 672f5e0
+        9865a9d com.amazon.firelauncher/com.amazon.identity.auth.device.storage.LambortishClock$ChangeTimestampsBroadcastReceiver filter 5dcf22e
           Action: "android.intent.action.TIME_SET"
       com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_GAMES:
-        346ad40 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.CardActionService$RemoveFromHomeReceiver filter 7ae9e62
+        a00bf98 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.CardActionService$RemoveFromHomeReceiver filter 9a67f00
           Action: "com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_APPS"
           Action: "com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_GAMES"
       com.amazon.firelauncher.APP_RECENCY_REBUILD:
-        542a918 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$PackageChangeReceiver filter 42f698
+        62c670 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$PackageChangeReceiver filter a4cfa6
           Action: "com.amazon.firelauncher.appmanager.APPS_ADDED"
           Action: "com.amazon.firelauncher.appmanager.APPS_REMOVED"
@@ -184,31 +184,31 @@

           Action: "com.amazon.firelauncher.APP_RECENCY_REBUILD"
       com.amazon.firelauncher.action.RECENCY_UPDATE:
-        71b5a8f com.amazon.firelauncher/.reccardproducer.ProducerService$RecencyUpdateReceiver filter f3197ba
+        98fc6f4 com.amazon.firelauncher/.reccardproducer.ProducerService$RecencyUpdateReceiver filter 7352e18
           Action: "com.amazon.firelauncher.action.RECENCY_UPDATE"
       com.amazon.device.messaging.intent.RECEIVE:
-        e519aae com.amazon.firelauncher/com.amazon.firecard.deviceclient.clients.MultiplexingMessageReceiver filter 1f35075
+        d850e87 com.amazon.firelauncher/com.amazon.firecard.deviceclient.clients.MultiplexingMessageReceiver filter 496dc0b
           Action: "com.amazon.device.messaging.intent.REGISTRATION"
           Action: "com.amazon.device.messaging.intent.RECEIVE"
           Category: "com.amazon.firelauncher"
       com.amazon.identity.auth.account.added.on.device:
-        b51fab7 com.amazon.firelauncher/.cardproducer.LauncherProducerService$AccountChangeReceiver filter 82759fe
+        b335ef com.amazon.firelauncher/.cardproducer.LauncherProducerService$AccountChangeReceiver filter f426afc
           Action: "com.amazon.identity.auth.account.added.on.device"
           Action: "com.amazon.identity.auth.account.removed.on.device"
       com.amazon.kor.demo.CMS_RESET:
-        7a41014 com.amazon.firelauncher/.appsgrid.DemoModeMonitor$CmsResetReceiver filter a90e45a
+        7a020b5 com.amazon.firelauncher/.appsgrid.DemoModeMonitor$CmsResetReceiver filter 83573b8
           Action: "com.amazon.kor.demo.CMS_RESET"
           mPriority=100, mOrder=0, mHasPartialTypes=false
-        13920bd com.amazon.firelauncher/com.amazon.fireappscardproducer.service.SystemNotificationProducerService$DemoResetReceiver filter b677bf3
+        a23434a com.amazon.firelauncher/com.amazon.fireappscardproducer.service.SystemNotificationProducerService$DemoResetReceiver filter 964339
```

### `package/home_query_cmd.stdout.txt`

```diff
--- before/package/home_query_cmd.stdout.txt

+++ after/package/home_query_cmd.stdout.txt

@@ -1,3 +1,3 @@

-3 activities found:
+4 activities found:
   Activity #0:
     priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
@@ -65,4 +65,32 @@

         HiddenApiEnforcementPolicy=2
   Activity #2:
+    priority=0 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
+    ActivityInfo:
+      name=org.fireosresearch.home.HomeActivity
+      packageName=org.fireosresearch.home.p0
+      enabled=true exported=true directBootAware=false
+      taskAffinity=org.fireosresearch.home.p0 targetActivity=null persistableMode=PERSIST_ROOT_ONLY
+      launchMode=2 flags=0x200 theme=0x0
+      screenOrientation=-1 configChanges=0x3 softInputMode=0x0
+      lockTaskLaunchMode=LOCK_TASK_LAUNCH_MODE_DEFAULT
+      resizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION
+      ApplicationInfo:
+        packageName=org.fireosresearch.home.p0
+        labelRes=0x0 nonLocalizedLabel=Phase 3A org.fireosresearch.home.p0 priority 0 icon=0x0 banner=0x0
+        processName=org.fireosresearch.home.p0
+        taskAffinity=org.fireosresearch.home.p0
+        uid=10191 flags=0x30e83e44 privateFlags=0x1000 theme=0x1030241
+        requiresSmallestWidthDp=0 compatibleWidthLimitDp=0 largestWidthLimitDp=0
+        sourceDir=/data/app/org.fireosresearch.home.p0-Er8RUFCd6pl-r5QmHpD9PQ==/base.apk
+        seinfo=default:targetSdkVersion=28
+        seinfoUser=:complete
+        dataDir=/data/user/0/org.fireosresearch.home.p0
+        deviceProtectedDataDir=/data/user_de/0/org.fireosresearch.home.p0
+        credentialProtectedDataDir=/data/user/0/org.fireosresearch.home.p0
+        enabled=true minSdkVersion=28 targetSdkVersion=28 versionCode=1 targetSandboxVersion=1
+        supportsRtl=true
+        fullBackupContent=true
+        HiddenApiEnforcementPolicy=2
+  Activity #3:
     priority=-1000 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
     ActivityInfo:
```

### `package/home_query_pm.stdout.txt`

```diff
--- before/package/home_query_pm.stdout.txt

+++ after/package/home_query_pm.stdout.txt

@@ -1,3 +1,3 @@

-3 activities found:
+4 activities found:
   Activity #0:
     priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
@@ -65,4 +65,32 @@

         HiddenApiEnforcementPolicy=2
   Activity #2:
+    priority=0 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
+    ActivityInfo:
+      name=org.fireosresearch.home.HomeActivity
+      packageName=org.fireosresearch.home.p0
+      enabled=true exported=true directBootAware=false
+      taskAffinity=org.fireosresearch.home.p0 targetActivity=null persistableMode=PERSIST_ROOT_ONLY
+      launchMode=2 flags=0x200 theme=0x0
+      screenOrientation=-1 configChanges=0x3 softInputMode=0x0
+      lockTaskLaunchMode=LOCK_TASK_LAUNCH_MODE_DEFAULT
+      resizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION
+      ApplicationInfo:
+        packageName=org.fireosresearch.home.p0
+        labelRes=0x0 nonLocalizedLabel=Phase 3A org.fireosresearch.home.p0 priority 0 icon=0x0 banner=0x0
+        processName=org.fireosresearch.home.p0
+        taskAffinity=org.fireosresearch.home.p0
+        uid=10191 flags=0x30e83e44 privateFlags=0x1000 theme=0x1030241
+        requiresSmallestWidthDp=0 compatibleWidthLimitDp=0 largestWidthLimitDp=0
+        sourceDir=/data/app/org.fireosresearch.home.p0-Er8RUFCd6pl-r5QmHpD9PQ==/base.apk
+        seinfo=default:targetSdkVersion=28
+        seinfoUser=:complete
+        dataDir=/data/user/0/org.fireosresearch.home.p0
+        deviceProtectedDataDir=/data/user_de/0/org.fireosresearch.home.p0
+        credentialProtectedDataDir=/data/user/0/org.fireosresearch.home.p0
+        enabled=true minSdkVersion=28 targetSdkVersion=28 versionCode=1 targetSandboxVersion=1
+        supportsRtl=true
+        fullBackupContent=true
+        HiddenApiEnforcementPolicy=2
+  Activity #3:
     priority=-1000 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
     ActivityInfo:
```

### `package/preferred_xml.stdout.txt`

```diff
--- before/package/preferred_xml.stdout.txt

+++ after/package/preferred_xml.stdout.txt

@@ -1,5 +1,5 @@

 <?xml version='1.0' encoding='utf-8' standalone='yes' ?>
 <preferred-activities>
-    <item name="com.amazon.firelauncher/.Launcher">
+    <item name="org.fireosresearch.home.p0/org.fireosresearch.home.HomeActivity">
         <filter>
             <action name="android.intent.action.MAIN" />
```

### `properties/getprop.stdout.txt`

```diff
--- before/properties/getprop.stdout.txt

+++ after/properties/getprop.stdout.txt

@@ -80,5 +80,4 @@

 [init.svc.pr_devcertid]: [stopped]
 [init.svc.read_diskstat]: [stopped]
-[init.svc.read_lifetime]: [stopped]
 [init.svc.rpmb_svc]: [running]
 [init.svc.securetime]: [running]
@@ -115,7 +114,5 @@

 [logd.init.METRICS_SUBSCRIBER]: [ready]
 [logd.init.SPAM_DETECTOR]: [ready]
-[logd.time.update]: [false]
 [net.bt.name]: [Android]
-[net.netid]: [100]
 [net.qtaguid_enabled]: [1]
 [net.tcp.default_init_rwnd]: [60]
@@ -365,9 +362,7 @@

 [sys.ipo.disable]: [1]
 [sys.ipo.pwrdncap]: [2]
-[sys.lab126.hasDeviceTime]: [true]
 [sys.logbootcomplete]: [1]
 [sys.retaildemo.enabled]: [0]
 [sys.sysctl.extra_free_kbytes]: [27000]
-[sys.sysctl.tcp_def_init_rwnd]: [60]
 [sys.uidcpupower]: []
 [sys.usb.config]: [adb]
@@ -382,5 +377,5 @@

 [vendor.connsys.driver.ready]: [yes]
 [vendor.connsys.formeta.ready]: [yes]
-[vendor.debug.chg_log.pid]: [488]
+[vendor.debug.chg_log.pid]: [476]
 [vendor.debug.log.coredump.enable]: [n]
 [vendor.debug.pq.acaltm.dbg]: [0]
```

### `settings/global.stdout.txt`

```diff
--- before/settings/global.stdout.txt

+++ after/settings/global.stdout.txt

@@ -42,5 +42,5 @@

 bluetooth_disabled_profiles=0
 bluetooth_on=0
-boot_count=22
+boot_count=23
 broadcast_sync_enabled=0
 bugreport_in_power_menu=0
```

### `summary.md`

```diff
--- before/summary.md

+++ after/summary.md

@@ -1,7 +1,7 @@

 # Phase 3C state snapshot
 
-- Test ID: PHASE3C-PREFERRED-P0-02-before
+- Test ID: PHASE3C-PREFERRED-P0-02-after_reboot
 - Serial: G001LT0511550CFT
-- Timestamp UTC: 2026-08-03T07:53:08Z
+- Timestamp UTC: 2026-08-03T07:54:25Z
 - This snapshot executed read-only ADB commands only.
 - Individual command failures are preserved in *.exit_code.txt and are not silently treated as absence.
```
