# Phase 3C snapshot comparison

- Before: `adb/phase4/PHASE4-ALIAS-T04/before`
- After: `adb/phase4/PHASE4-ALIAS-T04/after_rollback`
- Before files: `175`
- After files: `175`
- Changed files: `16`

## Changed files

- `activity/activities.stdout.txt` — changed
- `activity/recents.stdout.txt` — changed
- `activity/top.stdout.txt` — changed
- `appops/all.stdout.txt` — changed
- `appops/firelauncher.stdout.txt` — changed
- `appops/microsoft.stdout.txt` — changed
- `metadata.tsv` — changed
- `package/firelauncher.stdout.txt` — changed
- `package/full_dump.stdout.txt` — changed
- `package/persistent_preferred.stdout.txt` — changed
- `package/preferred_activities.stdout.txt` — changed
- `summary.md` — changed
- `users/dumpsys_user.stdout.txt` — changed
- `window/input.stdout.txt` — changed
- `window/processes.stdout.txt` — changed
- `window/windows.stdout.txt` — changed

## Focused evidence

### `activity/activities.stdout.txt`

```text
4:   Stack #0: type=home mode=fullscreen
12:     * TaskRecord{38663ed #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
14:       affinity=10120:com.amazon.firelauncher
15:       intent={act=android.intent.action.MAIN cat=[android.intent.category.HOME] flg=0x10000100 cmp=com.amazon.firelauncher/.Launcher}
16:       realActivity=com.amazon.firelauncher/.Launcher
19:       Activities=[ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}]
21:       mRootProcess=ProcessRecord{8f8f222 1942:com.amazon.firelauncher/u0a120}
24:       * Hist #0: ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}
25:           packageName=com.amazon.firelauncher processName=com.amazon.firelauncher
27:           app=ProcessRecord{8f8f222 1942:com.amazon.firelauncher/u0a120}
28:           Intent { act=android.intent.action.MAIN cat=[android.intent.category.HOME] flg=0x10000100 cmp=com.amazon.firelauncher/.Launcher }
29:           frontOfTask=true task=TaskRecord{38663ed #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
30:           taskAffinity=10120:com.amazon.firelauncher
31:           realActivity=com.amazon.firelauncher/.Launcher
32:           baseDir=/system/priv-app/com.amazon.firelauncher/com.amazon.firelauncher.apk
33:           dataDir=/data/user/0/com.amazon.firelauncher
34:           stateNotNeeded=false componentSpecified=false mActivityType=home
38:            mOverrideConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
39:           CurrentConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
40:           OverrideConfiguration={0.0 ?mcc?mnc ?localeList ?layoutDir ?swdp ?wdp ?hdp ?density ?lsize ?long ?ldr ?wideColorGamut ?orien ?uimode ?night ?touch ?keyb/?/? ?nav/? winConfig={ mBounds=Rect(0, 0 - 0, 0) mAppBounds=null mWindowingMode=undefined mActivityType=home}}
51:           mActivityType=home
57:       TaskRecord{38663ed #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
58:         Run #0: ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}
60:     mResumedActivity: ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}
62:   ResumedActivity: ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}
63:   mFocusedStack=ActivityStack{411a4b3 stackId=0 type=home mode=fullscreen visible=true translucent=false, 1 tasks} mLastFocusedStack=ActivityStack{411a4b3 stackId=0 type=home mode=fullscreen visible=true translucent=false, 1 tasks}
67:    mHomeStack=ActivityStack{411a4b3 stackId=0 type=home mode=fullscreen visible=true translucent=false, 1 tasks}
68:   isHomeRecentsComponent=false  KeyguardController:
```

### `activity/recents.stdout.txt`

```text
3: mRecentsComponent=ComponentInfo{com.android.launcher3/com.android.quickstep.RecentsActivity}
5:   * Recent #0: TaskRecord{38663ed #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
7:     affinity=10120:com.amazon.firelauncher
8:     intent={act=android.intent.action.MAIN cat=[android.intent.category.HOME] flg=0x10000100 cmp=com.amazon.firelauncher/.Launcher}
9:     realActivity=com.amazon.firelauncher/.Launcher
12:     Activities=[ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}]
14:     mRootProcess=ProcessRecord{8f8f222 1942:com.amazon.firelauncher/u0a120}
21:     origActivity=com.android.settings/.Settings
22:     realActivity=com.android.settings/.Settings
```

### `activity/top.stdout.txt`

```text
1: TASK 10120:com.amazon.firelauncher id=2 userId=0
2:   ACTIVITY com.amazon.firelauncher/.Launcher 873be7c pid=1942
6:       mCurrentConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
43:       DecorView@b17a258[Launcher]
46:             com.amazon.firelauncher.appsgrid.ui.drag.DragLayer{eea9017 V.E...... ........ 0,0-1200,1920 #7f090336 app:id/magazine_container}
49:               com.amazon.firelauncher.view.EnhancedViewPager{fe7ec22 VFED..... ........ 0,0-1200,1920 #7f090379 app:id/pager}
50:                 com.amazon.firelauncher.appsgrid.ui.ScrollableMainView{3fe16b3 V.E...... ........ 0,0-1200,1920}
51:                   com.amazon.firelauncher.appsgrid.ui.GradientScrimFrameLayout{f8c6470 V.E...... ........ 0,0-1200,1920}
52:                     com.amazon.firelauncher.appsgrid.ui.GridView{40113e9 VFED..... ........ 0,0-1200,1920 #7f09027a app:id/favorites_page}
55:                           com.amazon.firelauncher.view.LoadingDotsView{341d7dc V.E...... ......I. 0,0-0,0 #7f09032c app:id/loading_dots}
144:                 com.amazon.firelauncher.view.ScrollObservableContainer{c2ba92b V.E...... ........ 1200,0-2400,1920}
145:                   com.amazon.firelauncher.view.ChannelBackgroundView{e645188 V.ED..... ........ 0,0-1200,1920 #7f0900ef app:id/background_view}
146:                   com.amazon.firelauncher.view.ScrollingLinearRecyclerView{1f7ee7f VFED..... ........ 0,0-1200,1920 #7f09039e app:id/recycler}
164:                         com.amazon.firelauncher.view.LoadingDotsView{48d331b V.E...... ......I. 0,0-0,0 #7f09032c app:id/loading_dots}
177:                         com.amazon.firelauncher.view.NavTabView{3cadc6b VFE...C.. ........ 0,0-240,84}
180:                         com.amazon.firelauncher.view.NavTabView{6e2a0da VFE...C.. ..S..... 240,0-431,84}
183:                         com.amazon.firelauncher.view.NavTabView{dd1fa01 VFE...C.. ........ 431,0-719,84}
186:                 com.amazon.firelauncher.view.SearchWidgetHostLayout{28fa694 V.E...... ........ -18,-6-1218,192 #7f0903ba app:id/search_bar_widget}
187:                   com.amazon.firelauncher.search.SearchAppWidgetHostView{663353d V.E...... R....... 0,0-1236,198}
203:                     com.amazon.firelauncher.appsgrid.ui.FolderView{8f8b5 VFED..... ......I. 0,0-0,0 #7f090288 app:id/folder_grid}
214:       context: com.amazon.firelauncher.Launcher@b21ee9c
215:       client: com.amazon.firelauncher.Launcher@b21ee9c
257:         mContainer=com.amazon.firelauncher.view.EnhancedViewPager{fe7ec22 VFED..... ........ 0,0-1200,1920 #7f090379 app:id/pager}
258:         mView=com.amazon.firelauncher.view.ScrollObservableContainer{c2ba92b V.E...... ........ 1200,0-2400,1920}
274:         mContainer=com.amazon.firelauncher.view.EnhancedViewPager{fe7ec22 VFED..... ........ 0,0-1200,1920 #7f090379 app:id/pager}
292:         mContainer=com.amazon.firelauncher.view.EnhancedViewPager{fe7ec22 VFED..... ........ 0,0-1200,1920 #7f090379 app:id/pager}
293:         mView=com.amazon.firelauncher.appsgrid.ui.ScrollableMainView{3fe16b3 V.E...... ........ 0,0-1200,1920}
```

### `appops/all.stdout.txt`

```text
700:     Package com.android.launcher3:
986:     Package com.amazon.firelauncher:
1280:     Package com.microsoft.launcher:
```

### `package/firelauncher.stdout.txt`

```text
4:         ac2de99 com.amazon.firelauncher/.Launcher filter 798972c
8:           Authority: "com.amazon.firelauncher": -1
11:       com.amazon.firelauncher.REQUEST_LOCATION_PERMISSION:
12:         ac2de99 com.amazon.firelauncher/.Launcher filter 53caedf
13:           Action: "com.amazon.firelauncher.REQUEST_LOCATION_PERMISSION"
15:       com.amazon.firelauncher.intent.action.TUTORIALDONE:
16:         ac2de99 com.amazon.firelauncher/.Launcher filter 316597e
18:           Action: "com.amazon.firelauncher.intent.action.ALEXA_TUTORIAL"
19:           Action: "com.amazon.firelauncher.intent.action.TUTORIAL"
20:           Action: "com.amazon.firelauncher.intent.action.TUTORIALDONE"
21:           Category: "android.intent.category.HOME"
23:           mPriority=50, mOrder=0, mHasPartialTypes=false
24:       com.amazon.firelauncher.intent.action.ALEXA_TUTORIAL:
25:         ac2de99 com.amazon.firelauncher/.Launcher filter 316597e
27:           Action: "com.amazon.firelauncher.intent.action.ALEXA_TUTORIAL"
28:           Action: "com.amazon.firelauncher.intent.action.TUTORIAL"
29:           Action: "com.amazon.firelauncher.intent.action.TUTORIALDONE"
30:           Category: "android.intent.category.HOME"
32:           mPriority=50, mOrder=0, mHasPartialTypes=false
34:         ac2de99 com.amazon.firelauncher/.Launcher filter 316597e
36:           Action: "com.amazon.firelauncher.intent.action.ALEXA_TUTORIAL"
37:           Action: "com.amazon.firelauncher.intent.action.TUTORIAL"
38:           Action: "com.amazon.firelauncher.intent.action.TUTORIALDONE"
39:           Category: "android.intent.category.HOME"
41:           mPriority=50, mOrder=0, mHasPartialTypes=false
42:         dc5301d com.amazon.firelauncher/.LauncherUserSettings filter 20ff5f5
47:         dc5301d com.amazon.firelauncher/.LauncherUserSettings filter 20ff5f5
51:       com.amazon.firelauncher.intent.action.TUTORIAL:
52:         ac2de99 com.amazon.firelauncher/.Launcher filter 316597e
54:           Action: "com.amazon.firelauncher.intent.action.ALEXA_TUTORIAL"
55:           Action: "com.amazon.firelauncher.intent.action.TUTORIAL"
56:           Action: "com.amazon.firelauncher.intent.action.TUTORIALDONE"
57:           Category: "android.intent.category.HOME"
59:           mPriority=50, mOrder=0, mHasPartialTypes=false
64:         1fbb2e9 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.SystemNotificationProducerService$PackageRecencyReceiver filter b6c54f7
68:         6290acc com.amazon.firelauncher/.reccardproducer.ProducerService$MusicUnlimitedRegistrationReceiver filter 558d101
71:         e2b22ea com.amazon.firelauncher/com.amazon.fireappscardproducer.service.CardActionService$RemoveFromDeviceReceiverOld filter b585cd
73:       com.amazon.cmsfirecardproducer.REMOVE_FROM_HOME:
74:         8e98345 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.CardActionService$RemoveFromHomeReceiverOld filter d0d9f64
75:           Action: "com.amazon.cmsfirecardproducer.REMOVE_FROM_HOME"
76:       com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_APPS:
77:         967d41c com.amazon.firelauncher/com.amazon.fireappscardproducer.service.CardActionService$RemoveFromHomeReceiver filter 59c9e82
78:           Action: "com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_APPS"
79:           Action: "com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_GAMES"
80:       com.amazon.firelauncher.appmanager.APPS_REMOVED:
81:         f8a0b74 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$PackageChangeReceiver filter d383fb8
82:           Action: "com.amazon.firelauncher.appmanager.APPS_ADDED"
83:           Action: "com.amazon.firelauncher.appmanager.APPS_REMOVED"
84:           Action: "com.amazon.firelauncher.appmanager.APPS_UPDATED"
85:           Action: "com.amazon.firelauncher.APP_RECENCY_REBUILD"
87:         b510e55 com.amazon.firelauncher/.ui.GlobalSyncReceiver filter f4ea488
89:         e9f306a com.amazon.firelauncher/com.amazon.heroshoveler.weather.WeatherRefreshService$GlobalSyncReceiver filter 3cdae21
91:         684195b com.amazon.firelauncher/.cardproducer.LauncherProducerService$GlobalSyncReceiver filter dabc2cc
93:         d5ab5f8 com.amazon.firelauncher/com.amazon.hintscardproducer.HintsCardRefreshService$GlobalSyncReceiver filter 5c9a994
96:         bd57a41 com.amazon.firelauncher/.images.storage.LowStorageReceiver filter a067a9c
98:       com.amazon.firelauncher.appmanager.APPS_ADDED:
99:         f8a0b74 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$PackageChangeReceiver filter d383fb8
100:           Action: "com.amazon.firelauncher.appmanager.APPS_ADDED"
101:           Action: "com.amazon.firelauncher.appmanager.APPS_REMOVED"
102:           Action: "com.amazon.firelauncher.appmanager.APPS_UPDATED"
103:           Action: "com.amazon.firelauncher.APP_RECENCY_REBUILD"
104:       com.amazon.firelauncher.START_EDIT_MODE_EXTERNAL:
105:         99144cf com.amazon.firelauncher/.appsgrid.StartEditModeReceiver filter dcf682b
106:           Action: "com.amazon.firelauncher.START_EDIT_MODE_EXTERNAL"
107:           mPriority=100, mOrder=0, mHasPartialTypes=false
109:         7a63dea com.amazon.firelauncher/com.amazon.firecard.deviceclient.clients.MultiplexingMessageReceiver filter d444915
112:           Category: "com.amazon.firelauncher"
113:       com.amazon.firelauncher.action.REC_SUPPRESS:
114:         5b5e5c1 com.amazon.firelauncher/.reccardproducer.ProducerService$ItemSuppressionReceiver filter f0b76fc
115:           Action: "com.amazon.firelauncher.action.REC_SUPPRESS"
116:       com.amazon.firelauncher.action.UPSELL_TAPPED_NOTIFICATION:
117:         9d2f94a com.amazon.firelauncher/.reccardproducer.ProducerService$UpsellTappedNotificationReceiver filter 81706e8
118:           Action: "com.amazon.firelauncher.action.UPSELL_TAPPED_NOTIFICATION"
120:         20a176 com.amazon.firelauncher/com.amazon.identity.auth.accounts.SessionUserChangedToAccountForPackageChangedAdpater filter 87d9f39
122:       com.amazon.firelauncher.action.WEBLAB_UPDATE:
123:         74a6ae com.amazon.firelauncher/.reccardproducer.ProducerService$UpNextWeblabUpdateReceiver filter e8c580b
124:           Action: "com.amazon.firelauncher.action.WEBLAB_UPDATE"
126:         5c53e6b com.amazon.firelauncher/com.amazon.heroshoveler.weather.RefreshCardsBroadcastReceiver filter 96d8134
128:         fc25dc8 com.amazon.firelauncher/.cardproducer.LauncherProducerService$RefreshCardsReceiver filter 6cd0059
131:         f050e61 com.amazon.firelauncher/com.amazon.firecard.deviceclient.CloudCardEventService$RefreshCardsReceiver filter f95b42a
133:         f8edd86 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$RefreshCardsReceiver filter 21eb21b
135:         2f75647 com.amazon.firelauncher/.reccardproducer.ProducerService$RefreshCardsReceiver filter 8a1b1c9
137:         1838e74 com.amazon.firelauncher/com.amazon.hintscardproducer.HintsCardRefreshService$RefreshCardsReceiver filter 7a669e7
139:       com.amazon.firelauncher.action.FOR_YOU_CHANNEL_VISIBLE:
140:         dc5f37 com.amazon.firelauncher/com.amazon.heroshoveler.weather.WeatherRefreshBroadcastReceiver filter c675cd2
141:           Action: "com.amazon.firelauncher.action.FOR_YOU_CHANNEL_VISIBLE"
142:         e617ca4 com.amazon.firelauncher/.cardproducer.LauncherProducerService$ChannelVisibilityChangeReceiver filter a78c4ff
143:           Action: "com.amazon.firelauncher.action.FOR_YOU_CHANNEL_VISIBLE"
144:         e543a0d com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$ChannelVisibilityChangeReceiver filter ab74dd0
145:           Action: "com.amazon.firelauncher.action.FOR_YOU_CHANNEL_VISIBLE"
147:         e043bc3 com.amazon.firelauncher/.cardproducer.LauncherProducerService$AccountChangeReceiver filter 93a741e
151:         b545ad2 com.amazon.firelauncher/com.amazon.heroshoveler.weather.WeatherRefreshService$LocaleChangedReceiver filter 8276246
153:         702d7a3 com.amazon.firelauncher/amazon.alexa.locale.AlexaLocaleHelper filter 8fb7ca0
155:         fc25dc8 com.amazon.firelauncher/.cardproducer.LauncherProducerService$RefreshCardsReceiver filter 6cd0059
158:         4fbaaa0 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.SystemNotificationProducerService$LocaleChangeReceiver filter 8b2e8f6
160:         4e49659 com.amazon.firelauncher/.reccardproducer.ProducerService$LocaleChangedReceiver filter 652ebef
162:         cf9521e com.amazon.firelauncher/com.amazon.hintscardproducer.HintsCardRefreshService$LocaleChangedReceiver filter 5007c3d
164:       com.amazon.firelauncher.action.TAB_SETTINGS_CHANGED:
165:         25db856 com.amazon.firelauncher/.reccardproducer.ProducerService$TabSuppressionReceiver filter 90aa185
166:           Action: "com.amazon.firelauncher.action.TAB_SETTINGS_CHANGED"
167:       com.amazon.firelauncher.action.HOST_APP_COLD_START_ACTION:
168:         2eab16 com.amazon.firelauncher/.reccardproducer.ProducerService$ColdStartReceiver filter e457ba6
169:           Action: "com.amazon.firelauncher.action.HOST_APP_COLD_START_ACTION"
170:         503bc97 com.amazon.firelauncher/com.amazon.hintscardproducer.HintsCardRefreshService$ColdStartReceiver filter 465bd83
171:           Action: "com.amazon.firelauncher.action.HOST_APP_COLD_START_ACTION"
173:         1016c76 com.amazon.firelauncher/com.amazon.identity.auth.device.storage.LambortishClock$ChangeTimestampsBroadcastReceiver filter 561cb00
175:       com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_GAMES:
176:         967d41c com.amazon.firelauncher/com.amazon.fireappscardproducer.service.CardActionService$RemoveFromHomeReceiver filter 59c9e82
177:           Action: "com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_APPS"
178:           Action: "com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_GAMES"
179:       com.amazon.firelauncher.APP_RECENCY_REBUILD:
180:         f8a0b74 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$PackageChangeReceiver filter d383fb8
181:           Action: "com.amazon.firelauncher.appmanager.APPS_ADDED"
182:           Action: "com.amazon.firelauncher.appmanager.APPS_REMOVED"
183:           Action: "com.amazon.firelauncher.appmanager.APPS_UPDATED"
184:           Action: "com.amazon.firelauncher.APP_RECENCY_REBUILD"
185:       com.amazon.firelauncher.action.RECENCY_UPDATE:
186:         89940b8 com.amazon.firelauncher/.reccardproducer.ProducerService$RecencyUpdateReceiver filter 89b7bda
187:           Action: "com.amazon.firelauncher.action.RECENCY_UPDATE"
189:         7a63dea com.amazon.firelauncher/com.amazon.firecard.deviceclient.clients.MultiplexingMessageReceiver filter d444915
```

### `package/full_dump.stdout.txt`

```text
149:   android.software.home_screen
238:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
247:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
250:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
252:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
258:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
267:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
272:         9dee318 com.audible.application.kindle/com.audible.application.MainLauncher
275:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
300:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
303:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
305:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
314:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
319:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
322:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
327:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
330:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
336:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
343:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
348:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
351:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
353:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
358:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
360:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
363:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
364:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
367:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
368:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
371:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
372:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
379:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
382:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
385:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
386:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
393:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
396:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
398:         aa83af4 com.amazon.mp3/.activity.ExternalLauncherActivity
402:         84fa21d com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
403:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
416:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
417:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
420:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
423:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
426:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
431:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
443:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
446:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
468:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
475:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
481:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
485:         ceb8cb6 com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
491:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
504:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
513:         1c784a8 com.microsoft.launcher/com.microsoft.bing.ProcessTextSearch
520:         8918045 com.amazon.cloud9/com.amazon.slate.silo.SiloLauncherActivity
521:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
523:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
537:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
538:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
548:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
550:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
553:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
556:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
570:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
576:         16c40c0 com.amazon.photos/com.android.launcher3.WallpaperCropActivity
583:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
586:         ceb8cb6 com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
588:         f6c04b5 com.microsoft.launcher/.wallpaper.activity.WallpaperPreviewActivity (2 filters)
592:         9dee318 com.audible.application.kindle/com.audible.application.MainLauncher
594:         aa83af4 com.amazon.mp3/.activity.ExternalLauncherActivity
597:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
600:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
601:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
626:         aa83af4 com.amazon.mp3/.activity.ExternalLauncherActivity
644:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
646:         aa83af4 com.amazon.mp3/.activity.ExternalLauncherActivity
652:         1c784a8 com.microsoft.launcher/com.microsoft.bing.ProcessTextSearch
660:         8918045 com.amazon.cloud9/com.amazon.slate.silo.SiloLauncherActivity
661:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (7 filters)
663:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity (7 filters)
669:         9dee318 com.audible.application.kindle/com.audible.application.MainLauncher (2 filters)
680:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (9 filters)
685:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity (34 filters)
702:         84fa21d com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
703:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
709:         16c40c0 com.amazon.photos/com.android.launcher3.WallpaperCropActivity
716:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
719:         ceb8cb6 com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
721:         f6c04b5 com.microsoft.launcher/.wallpaper.activity.WallpaperPreviewActivity (2 filters)
726:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
730:         ceb8cb6 com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
735:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
752:         17159f0 com.amazon.windowshop/com.amazon.mShop.android.home.PublicUrlActivity
784:         90333dd com.android.vending/com.google.android.finsky.instantlaunchapi.InstantLauncherActivity
813:         9dee318 com.audible.application.kindle/com.audible.application.MainLauncher (3 filters)
819:       ms-launcher:
820:         661968 com.microsoft.launcher/.contacts.PeopleDeepLinkActivity
821:         766aa5a com.microsoft.launcher/com.microsoft.rewards.activity.RewardsActionsActivity
822:         a3a248b com.microsoft.launcher/com.microsoft.rewards.activity.OfferLandingActivity
831:         17159f0 com.amazon.windowshop/com.amazon.mShop.android.home.PublicUrlActivity
847:         558d35f com.google.android.gms/.home.SetupDeviceActivityQrCode
849:         1b321ac com.google.android.gms/.home.SetupDeviceActivityNfc
859:         861467b com.amazon.avod/.client.activity.HomeScreenActivity
869:         984ddc com.amazon.photos/com.amazon.gallery.thor.app.activity.ATCLauncherActivity
881:         3370461 com.microsoft.launcher/.setting.FakeSms
887:         3370461 com.microsoft.launcher/.setting.FakeSms
897:         138c7d1 com.amazon.venezia/.CFR.dialog.CFRLauncherActivity
900:         821955e com.amazon.kindle.otter.oobe/.OOBELauncherV2
903:         ac2de99 com.amazon.firelauncher/.Launcher
919:         84fa21d com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
922:         9dee318 com.audible.application.kindle/com.audible.application.MainLauncher (2 filters)
925:         ceb8cb6 com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
933:         331100d com.amazon.photos/com.amazon.gallery.thor.app.activity.LauncherActivity (22 filters)
936:         40c120e com.android.vending/com.google.android.finsky.protect.impl.PlayProtectHomeDeepLinkActivity
946:         7f3eaa4 com.amazon.cloud9/org.chromium.chrome.browser.DragAndDropLauncherActivity
952:         9dee318 com.audible.application.kindle/com.audible.application.MainLauncher (3 filters)
979:         c28d972 org.mozilla.firefox/org.mozilla.fenix.HomeActivity
983:         18fda40 com.google.android.inputmethod.latin/com.google.android.apps.inputmethod.latin.sharing.LinkReceivingLauncherActivity
987:         331100d com.amazon.photos/com.amazon.gallery.thor.app.activity.LauncherActivity (22 filters)
991:         40c120e com.android.vending/com.google.android.finsky.protect.impl.PlayProtectHomeDeepLinkActivity
```

### `package/persistent_preferred.stdout.txt`

```text
149:   android.software.home_screen
238:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
247:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
250:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
252:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
258:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
267:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
272:         9dee318 com.audible.application.kindle/com.audible.application.MainLauncher
275:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
300:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
303:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
305:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
314:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
319:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
322:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
327:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
330:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
336:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
343:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
348:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
351:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
353:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
358:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
360:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
363:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
364:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
367:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
368:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
371:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
372:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
379:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
382:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
385:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
386:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
393:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
396:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
398:         aa83af4 com.amazon.mp3/.activity.ExternalLauncherActivity
402:         84fa21d com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
403:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
416:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
417:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
420:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
423:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
426:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
431:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
443:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
446:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
468:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
475:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
481:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
485:         ceb8cb6 com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
491:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
504:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
513:         1c784a8 com.microsoft.launcher/com.microsoft.bing.ProcessTextSearch
520:         8918045 com.amazon.cloud9/com.amazon.slate.silo.SiloLauncherActivity
521:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
523:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
537:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
538:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
548:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
550:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
553:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
556:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
570:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
576:         16c40c0 com.amazon.photos/com.android.launcher3.WallpaperCropActivity
583:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
586:         ceb8cb6 com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
588:         f6c04b5 com.microsoft.launcher/.wallpaper.activity.WallpaperPreviewActivity (2 filters)
592:         9dee318 com.audible.application.kindle/com.audible.application.MainLauncher
594:         aa83af4 com.amazon.mp3/.activity.ExternalLauncherActivity
597:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
600:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
601:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
626:         aa83af4 com.amazon.mp3/.activity.ExternalLauncherActivity
644:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
646:         aa83af4 com.amazon.mp3/.activity.ExternalLauncherActivity
652:         1c784a8 com.microsoft.launcher/com.microsoft.bing.ProcessTextSearch
660:         8918045 com.amazon.cloud9/com.amazon.slate.silo.SiloLauncherActivity
661:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (7 filters)
663:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity (7 filters)
669:         9dee318 com.audible.application.kindle/com.audible.application.MainLauncher (2 filters)
680:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (9 filters)
685:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity (34 filters)
702:         84fa21d com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
703:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
709:         16c40c0 com.amazon.photos/com.android.launcher3.WallpaperCropActivity
716:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
719:         ceb8cb6 com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
721:         f6c04b5 com.microsoft.launcher/.wallpaper.activity.WallpaperPreviewActivity (2 filters)
726:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
730:         ceb8cb6 com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
735:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
752:         17159f0 com.amazon.windowshop/com.amazon.mShop.android.home.PublicUrlActivity
784:         90333dd com.android.vending/com.google.android.finsky.instantlaunchapi.InstantLauncherActivity
813:         9dee318 com.audible.application.kindle/com.audible.application.MainLauncher (3 filters)
819:       ms-launcher:
820:         661968 com.microsoft.launcher/.contacts.PeopleDeepLinkActivity
821:         766aa5a com.microsoft.launcher/com.microsoft.rewards.activity.RewardsActionsActivity
822:         a3a248b com.microsoft.launcher/com.microsoft.rewards.activity.OfferLandingActivity
831:         17159f0 com.amazon.windowshop/com.amazon.mShop.android.home.PublicUrlActivity
847:         558d35f com.google.android.gms/.home.SetupDeviceActivityQrCode
849:         1b321ac com.google.android.gms/.home.SetupDeviceActivityNfc
859:         861467b com.amazon.avod/.client.activity.HomeScreenActivity
869:         984ddc com.amazon.photos/com.amazon.gallery.thor.app.activity.ATCLauncherActivity
881:         3370461 com.microsoft.launcher/.setting.FakeSms
887:         3370461 com.microsoft.launcher/.setting.FakeSms
897:         138c7d1 com.amazon.venezia/.CFR.dialog.CFRLauncherActivity
900:         821955e com.amazon.kindle.otter.oobe/.OOBELauncherV2
903:         ac2de99 com.amazon.firelauncher/.Launcher
919:         84fa21d com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
922:         9dee318 com.audible.application.kindle/com.audible.application.MainLauncher (2 filters)
925:         ceb8cb6 com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
933:         331100d com.amazon.photos/com.amazon.gallery.thor.app.activity.LauncherActivity (22 filters)
936:         40c120e com.android.vending/com.google.android.finsky.protect.impl.PlayProtectHomeDeepLinkActivity
946:         7f3eaa4 com.amazon.cloud9/org.chromium.chrome.browser.DragAndDropLauncherActivity
952:         9dee318 com.audible.application.kindle/com.audible.application.MainLauncher (3 filters)
979:         c28d972 org.mozilla.firefox/org.mozilla.fenix.HomeActivity
983:         18fda40 com.google.android.inputmethod.latin/com.google.android.apps.inputmethod.latin.sharing.LinkReceivingLauncherActivity
987:         331100d com.amazon.photos/com.amazon.gallery.thor.app.activity.LauncherActivity (22 filters)
991:         40c120e com.android.vending/com.google.android.finsky.protect.impl.PlayProtectHomeDeepLinkActivity
```

### `package/preferred_activities.stdout.txt`

```text
149:   android.software.home_screen
238:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
247:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
250:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
252:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
258:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
267:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
272:         9dee318 com.audible.application.kindle/com.audible.application.MainLauncher
275:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
300:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
303:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
305:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
314:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
319:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
322:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
327:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
330:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
336:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
343:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
348:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
351:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
353:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
358:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
360:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
363:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
364:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
367:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
368:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
371:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
372:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
379:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
382:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
385:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
386:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
393:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
396:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
398:         aa83af4 com.amazon.mp3/.activity.ExternalLauncherActivity
402:         84fa21d com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
403:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
416:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
417:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
420:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
423:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
426:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
431:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
443:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
446:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
468:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
475:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
481:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
485:         ceb8cb6 com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
491:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
504:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
513:         1c784a8 com.microsoft.launcher/com.microsoft.bing.ProcessTextSearch
520:         8918045 com.amazon.cloud9/com.amazon.slate.silo.SiloLauncherActivity
521:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
523:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
537:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
538:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
548:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
550:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
553:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
556:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
570:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
576:         16c40c0 com.amazon.photos/com.android.launcher3.WallpaperCropActivity
583:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
586:         ceb8cb6 com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
588:         f6c04b5 com.microsoft.launcher/.wallpaper.activity.WallpaperPreviewActivity (2 filters)
592:         9dee318 com.audible.application.kindle/com.audible.application.MainLauncher
594:         aa83af4 com.amazon.mp3/.activity.ExternalLauncherActivity
597:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
600:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
601:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
626:         aa83af4 com.amazon.mp3/.activity.ExternalLauncherActivity
644:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
646:         aa83af4 com.amazon.mp3/.activity.ExternalLauncherActivity
652:         1c784a8 com.microsoft.launcher/com.microsoft.bing.ProcessTextSearch
660:         8918045 com.amazon.cloud9/com.amazon.slate.silo.SiloLauncherActivity
661:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (7 filters)
663:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity (7 filters)
669:         9dee318 com.audible.application.kindle/com.audible.application.MainLauncher (2 filters)
680:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (9 filters)
685:         d9de6e7 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity (34 filters)
702:         84fa21d com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
703:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
709:         16c40c0 com.amazon.photos/com.android.launcher3.WallpaperCropActivity
716:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
719:         ceb8cb6 com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
721:         f6c04b5 com.microsoft.launcher/.wallpaper.activity.WallpaperPreviewActivity (2 filters)
726:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
730:         ceb8cb6 com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
735:         9829400 com.android.bluetooth/.opp.BluetoothOppLauncherActivity
752:         17159f0 com.amazon.windowshop/com.amazon.mShop.android.home.PublicUrlActivity
784:         90333dd com.android.vending/com.google.android.finsky.instantlaunchapi.InstantLauncherActivity
813:         9dee318 com.audible.application.kindle/com.audible.application.MainLauncher (3 filters)
819:       ms-launcher:
820:         661968 com.microsoft.launcher/.contacts.PeopleDeepLinkActivity
821:         766aa5a com.microsoft.launcher/com.microsoft.rewards.activity.RewardsActionsActivity
822:         a3a248b com.microsoft.launcher/com.microsoft.rewards.activity.OfferLandingActivity
831:         17159f0 com.amazon.windowshop/com.amazon.mShop.android.home.PublicUrlActivity
847:         558d35f com.google.android.gms/.home.SetupDeviceActivityQrCode
849:         1b321ac com.google.android.gms/.home.SetupDeviceActivityNfc
859:         861467b com.amazon.avod/.client.activity.HomeScreenActivity
869:         984ddc com.amazon.photos/com.amazon.gallery.thor.app.activity.ATCLauncherActivity
881:         3370461 com.microsoft.launcher/.setting.FakeSms
887:         3370461 com.microsoft.launcher/.setting.FakeSms
897:         138c7d1 com.amazon.venezia/.CFR.dialog.CFRLauncherActivity
900:         821955e com.amazon.kindle.otter.oobe/.OOBELauncherV2
903:         ac2de99 com.amazon.firelauncher/.Launcher
919:         84fa21d com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
922:         9dee318 com.audible.application.kindle/com.audible.application.MainLauncher (2 filters)
925:         ceb8cb6 com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
933:         331100d com.amazon.photos/com.amazon.gallery.thor.app.activity.LauncherActivity (22 filters)
936:         40c120e com.android.vending/com.google.android.finsky.protect.impl.PlayProtectHomeDeepLinkActivity
946:         7f3eaa4 com.amazon.cloud9/org.chromium.chrome.browser.DragAndDropLauncherActivity
952:         9dee318 com.audible.application.kindle/com.audible.application.MainLauncher (3 filters)
979:         c28d972 org.mozilla.firefox/org.mozilla.fenix.HomeActivity
983:         18fda40 com.google.android.inputmethod.latin/com.google.android.apps.inputmethod.latin.sharing.LinkReceivingLauncherActivity
987:         331100d com.amazon.photos/com.amazon.gallery.thor.app.activity.LauncherActivity (22 filters)
991:         40c120e com.android.vending/com.google.android.finsky.protect.impl.PlayProtectHomeDeepLinkActivity
```

### `window/input.stdout.txt`

```text
454:   FocusedApplication: name='AppWindowToken{e63cf5a token=Token{d3a1305 ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}}}', dispatchingTimeout=5000.000ms
463:     5: name='Window{80793f7 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}', displayId=0, paused=false, hasFocus=false, hasWallpaper=true, visible=true, canReceiveKeys=true, flags=0x81910120, type=0x00000001, layer=0, frame=[0,0][1200,1920], scale=1.000000, touchableRegion=[0,0][1200,1920], inputFeatures=0x00000000, ownerPid=1942, ownerUid=10120, dispatchingTimeout=5000.000ms
503:     7: channelName='80793f7 com.amazon.firelauncher/com.amazon.firelauncher.Launcher (server)', windowName='Window{80793f7 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}', status=NORMAL, monitor=false, inputPublisherBlocked=false
```

### `window/processes.stdout.txt`

```text
260: system         422     1 wmt_launcher                wmt_launcher -p /vendor/firmware/
332: u0_a75        1923   352 com.android.launcher3       com.android.launcher3
333: u0_a120       1942   352 com.amazon.firelauncher     com.amazon.firelauncher
358: u0_a178       6293   352 com.microsoft.launcher      com.microsoft.launcher
```

### `window/windows.stdout.txt`

```text
155:   Window #5 Window{80793f7 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}:
157:     mOwnerUid=10120 mShowToOwnerOnly=true package=com.amazon.firelauncher appop=NONE
164:     mToken=AppWindowToken{e63cf5a token=Token{d3a1305 ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}}}
165:     mAppToken=AppWindowToken{e63cf5a token=Token{d3a1305 ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}}}
170:     mFullConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
171:     mLastReportedConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
181:     WindowStateAnimator{bffb519 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}:
182:       mSurface=Surface(name=com.amazon.firelauncher/com.amazon.firelauncher.Launcher)/@0xabc8ba2
222:   mCurrentFocus=Window{93484d6 u0 com.android.systemui}
223:   mFocusedApp=AppWindowToken{e63cf5a token=Token{d3a1305 ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}}}
235:   mWallpaperTarget=Window{80793f7 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}
249:     mLastOpeningApp=AppWindowToken{e63cf5a token=Token{d3a1305 ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}}}
250:     mLastClosingApp=AppWindowToken{2dd6ebc token=Token{56eaaf ActivityRecord{2a7e28e u0 org.fireosresearch.phase4.alias/.SecondaryHomeActivity t31}}}
```


## Small text diffs

### `activity/activities.stdout.txt`

```diff
--- before/activity/activities.stdout.txt

+++ after/activity/activities.stdout.txt

@@ -21,5 +21,5 @@

       mRootProcess=ProcessRecord{8f8f222 1942:com.amazon.firelauncher/u0a120}
       stackId=0
-      hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=2325741 (inactive for 36s)
+      hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=2366700 (inactive for 3s)
       * Hist #0: ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}
           packageName=com.amazon.firelauncher processName=com.amazon.firelauncher
@@ -43,5 +43,5 @@

            statusBarColor=0
            navigationBarColor=ff000000
-          launchFailed=false launchCount=0 lastLaunchTime=-39m2s337ms
+          launchFailed=false launchCount=0 lastLaunchTime=-39m10s318ms
           haveState=false icicle=null
           state=RESUMED stopped=false delayedResume=false finishing=false
@@ -50,5 +50,5 @@

           frozenBeforeDestroy=false forceNewConfig=false
           mActivityType=home
-          waitingVisible=false nowVisible=true lastVisibleTime=-37s4ms
+          waitingVisible=false nowVisible=true lastVisibleTime=-4s128ms
           resizeMode=RESIZE_MODE_RESIZEABLE
           mLastReportedMultiWindowMode=false mLastReportedPictureInPictureMode=false
@@ -62,5 +62,5 @@

   ResumedActivity: ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}
   mFocusedStack=ActivityStack{411a4b3 stackId=0 type=home mode=fullscreen visible=true translucent=false, 1 tasks} mLastFocusedStack=ActivityStack{411a4b3 stackId=0 type=home mode=fullscreen visible=true translucent=false, 1 tasks}
-  mCurTaskIdForUser={0=30}
+  mCurTaskIdForUser={0=31}
   mUserStackInFront={}
   displayId=0 stacks=1
```

### `activity/recents.stdout.txt`

```diff
--- before/activity/recents.stdout.txt

+++ after/activity/recents.stdout.txt

@@ -14,5 +14,5 @@

     mRootProcess=ProcessRecord{8f8f222 1942:com.amazon.firelauncher/u0a120}
     stackId=0
-    hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=2325741 (inactive for 36s)
+    hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=2366700 (inactive for 3s)
   * Recent #1: TaskRecord{ca627d2 #28 A=1000:com.android.settings.root U=0 StackId=-1 sz=0}
     userId=0 effectiveUid=1000 mCallingUid=2000 mUserSetupComplete=true mCallingPackage=
@@ -26,3 +26,3 @@

     askedCompatMode=false inRecents=true isAvailable=true
     stackId=-1
-    hasBeenVisible=false mResizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION mSupportsPictureInPicture=false isResizeable=true lastActiveTime=19930 (inactive for 2342s)
+    hasBeenVisible=false mResizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION mSupportsPictureInPicture=false isResizeable=true lastActiveTime=19930 (inactive for 2350s)
```

### `activity/top.stdout.txt`

```diff
--- before/activity/top.stdout.txt

+++ after/activity/top.stdout.txt

@@ -39,5 +39,5 @@

     Choreographer:
       mFrameScheduled=false
-      mLastFrameTime=2326276 (35871 ms ago)
+      mLastFrameTime=2367046 (3089 ms ago)
     View Hierarchy:
       DecorView@b17a258[Launcher]
@@ -206,5 +206,5 @@

           android.view.ViewStub{461ebd8 G.E...... ......I. 0,0-0,0 #10201ad android:id/action_mode_bar_stub}
     Looper (main, tid 2) {360f6d5}
-      Message 0: { when=+21m2s36ms callback=com.amazon.firecard.deviceagent.provider.CardProvider$5 target=android.os.Handler isAsync=false }
+      Message 0: { when=+20m54s48ms callback=com.amazon.firecard.deviceagent.provider.CardProvider$5 target=android.os.Handler isAsync=false }
       (Total messages: 1, polling=false, quitting=false)
     Autofill Compat Mode: false
```

### `appops/all.stdout.txt`

```diff
--- before/appops/all.stdout.txt

+++ after/appops/all.stdout.txt

@@ -59,188 +59,188 @@

     Package com.amazon.platform.fdrw:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:26:28.449 (-2h26m18s546ms)
+          Access: pers  = 2026-08-03 14:26:28.449 (-2h26m26s601ms)
     Package amazon.fireos:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 09:20:46.628 (-7h32m0s367ms)
+          Access: pers  = 2026-08-03 09:20:46.628 (-7h32m8s422ms)
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2026-03-26 23:43:10.017 (-129d17h9m36s978ms)
+          Reject: pers  = 2026-03-26 23:43:10.017 (-129d17h9m45s33ms)
     Package com.amazon.device.logmanager:
       RUN_IN_BACKGROUND (allow): 
-          Access: pers  = 2026-08-03 16:13:51.305 (-38m55s690ms)
+          Access: pers  = 2026-08-03 16:13:51.305 (-39m3s745ms)
     Package com.amazon.accessorynotifier:
       RUN_IN_BACKGROUND (allow): 
-          Access: pers  = 2026-08-03 16:13:52.826 (-38m54s169ms)
+          Access: pers  = 2026-08-03 16:13:52.826 (-39m2s224ms)
     Package com.amazon.android.marketplace:
       WRITE_SETTINGS (default): 
-          Reject: pers  = 2025-12-06 20:49:21.625 (-239d20h3m25s370ms)
-      RECORD_AUDIO (allow): 
-          Access: pers  = 2026-04-06 07:13:25.558 (-119d9h39m21s437ms)
+          Reject: pers  = 2025-12-06 20:49:21.625 (-239d20h3m33s425ms)
+      RECORD_AUDIO (allow): 
+          Access: pers  = 2026-04-06 07:13:25.558 (-119d9h39m29s492ms)
     Package com.amazon.storagemanager:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 16:13:37.895 (-39m9s100ms)
+          Access: pers  = 2026-08-03 16:13:37.895 (-39m17s155ms)
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2026-08-03 07:45:44.987 (-9h7m2s8ms)
-      READ_EXTERNAL_STORAGE (allow): 
-          Access: pers  = 2026-08-03 07:45:41.642 (-9h7m5s353ms)
+          Reject: pers  = 2026-08-03 07:45:44.987 (-9h7m10s63ms)
+      READ_EXTERNAL_STORAGE (allow): 
+          Access: pers  = 2026-08-03 07:45:41.642 (-9h7m13s408ms)
     Package android:
       COARSE_LOCATION (allow): 
       FINE_LOCATION (allow / switch COARSE_LOCATION=allow): 
-          Access: pers  = 2026-08-03 16:13:42.326 (-39m4s669ms)
+          Access: pers  = 2026-08-03 16:13:42.326 (-39m12s724ms)
       READ_CALENDAR (allow): 
-          Access: pers  = 2026-08-03 16:13:48.515 (-38m58s480ms)
-      RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:29:54.943 (-2h22m52s52ms)
+          Access: pers  = 2026-08-03 16:13:48.515 (-39m6s535ms)
+      RECORD_AUDIO (allow): 
+          Access: pers  = 2026-08-03 14:29:54.943 (-2h23m0s107ms)
       AUDIO_MEDIA_VOLUME (allow): 
-          Access: pers  = 2026-08-01 21:11:23.169 (-1d19h41m23s826ms)
-      WAKE_LOCK (allow): 
-          Access: pers  = 2026-08-03 16:52:10.471 (-36s524ms)
-                  fg    = 2026-04-11 03:58:41.049 (-114d12h54m5s946ms)
-          duration=+24ms
+          Access: pers  = 2026-08-01 21:11:23.169 (-1d19h41m31s881ms)
+      WAKE_LOCK (allow): 
+          Access: pers  = 2026-08-03 16:52:51.243 (-3s807ms)
+                  fg    = 2026-04-11 03:58:41.049 (-114d12h54m14s1ms)
+          duration=+23ms
       MONITOR_LOCATION (allow / switch COARSE_LOCATION=allow): 
-          Access: pers  = 2026-08-03 16:13:42.317 (-39m4s678ms)
-                  fg    = 2026-04-11 03:58:41.049 (-114d12h54m5s946ms)
-          Running start at: +39m4s372ms
+          Access: pers  = 2026-08-03 16:13:42.317 (-39m12s733ms)
+                  fg    = 2026-04-11 03:58:41.049 (-114d12h54m14s1ms)
+          Running start at: +39m12s427ms
           startNesting=1
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2026-08-03 16:52:18.037 (-28s958ms)
+          Reject: pers  = 2026-08-03 16:52:47.579 (-7s471ms)
       TURN_ON_SCREEN (allow): 
-          Access: pers  = 2026-07-10 22:35:34.059 (-23d18h17m12s936ms)
+          Access: pers  = 2026-07-10 22:35:34.059 (-23d18h17m20s991ms)
     Package com.android.providers.settings:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2025-12-06 20:11:38.894 (-239d20h41m8s101ms)
+          Access: pers  = 2025-12-06 20:11:38.894 (-239d20h41m16s156ms)
     Package com.android.keychain:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2025-12-07 15:30:49.435 (-239d1h21m57s560ms)
+          Access: pers  = 2025-12-07 15:30:49.435 (-239d1h22m5s615ms)
     Package com.amazon.device.sale.service:
       RUN_IN_BACKGROUND (allow): 
-          Access: pers  = 2026-08-03 16:14:05.671 (-38m41s324ms)
+          Access: pers  = 2026-08-03 16:14:05.671 (-38m49s379ms)
     Package com.android.settings:
       WRITE_SETTINGS (default): 
-          Reject: pers  = 2026-08-01 21:54:35.634 (-1d18h58m11s361ms)
+          Reject: pers  = 2026-08-01 21:54:35.634 (-1d18h58m19s416ms)
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2026-08-03 12:07:40.636 (-4h45m6s359ms)
+          Reject: pers  = 2026-08-03 12:07:40.636 (-4h45m14s414ms)
       TOAST_WINDOW (allow): 
-          Access: pers  = 2025-12-07 16:06:55.266 (-239d0h45m51s729ms)
+          Access: pers  = 2025-12-07 16:06:55.266 (-239d0h45m59s784ms)
           duration=+4s550ms
     Package android.amazon.perm:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2025-12-06 19:11:18.089 (-239d21h41m28s906ms)
+          Access: pers  = 2025-12-06 19:11:18.089 (-239d21h41m36s961ms)
     Package com.android.wallpaperbackup:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:32:08.417 (-2h20m38s578ms)
+          Access: pers  = 2026-08-03 14:32:08.417 (-2h20m46s633ms)
     Package com.android.location.fused:
       COARSE_LOCATION (allow): 
       FINE_LOCATION (allow / switch COARSE_LOCATION=allow): 
-          Access: pers  = 2025-12-06 18:57:45.955 (-239d21h55m1s40ms)
-      RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:35:13.887 (-2h17m33s108ms)
+          Access: pers  = 2025-12-06 18:57:45.955 (-239d21h55m9s95ms)
+      RECORD_AUDIO (allow): 
+          Access: pers  = 2026-08-03 14:35:13.887 (-2h17m41s163ms)
       MONITOR_LOCATION (allow / switch COARSE_LOCATION=allow): 
-          Access: pers  = 2025-12-06 19:03:04.992 (-239d21h49m42s3ms)
+          Access: pers  = 2025-12-06 19:03:04.992 (-239d21h49m50s58ms)
           duration=+5m20s391ms
     Package com.here.odnp.service:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 15:54:11.972 (-58m35s23ms)
+          Access: pers  = 2026-08-03 15:54:11.972 (-58m43s78ms)
     Package com.amazon.settings:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 07:45:33.063 (-9h7m13s932ms)
+          Access: pers  = 2026-08-03 07:45:33.063 (-9h7m21s987ms)
       TOAST_WINDOW (allow): 
-          Access: pers  = 2026-07-10 21:04:18.363 (-23d19h48m28s632ms)
+          Access: pers  = 2026-07-10 21:04:18.363 (-23d19h48m36s687ms)
           duration=+5s388ms
     Package com.amazon.shpm:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 09:19:52.283 (-7h32m54s712ms)
+          Access: pers  = 2026-08-03 09:19:52.283 (-7h33m2s767ms)
     Package com.amazon.fireos.cirruscloud:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:33:40.524 (-2h19m6s471ms)
+          Access: pers  = 2026-08-03 14:33:40.524 (-2h19m14s526ms)
   Uid 1002:
     state=cch  
     Package com.android.bluetooth:
       WAKE_LOCK (allow): 
-          Access: pers  = 2025-12-06 18:56:41.294 (-239d21h56m5s701ms)
-                  bg    = 2025-12-06 18:56:41.291 (-239d21h56m5s704ms)
+          Access: pers  = 2025-12-06 18:56:41.294 (-239d21h56m13s756ms)
+                  bg    = 2025-12-06 18:56:41.291 (-239d21h56m13s759ms)
           duration=+10ms
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2025-12-06 18:56:24.496 (-239d21h56m22s499ms)
-      READ_EXTERNAL_STORAGE (allow): 
-          Access: pers  = 2025-12-06 18:56:28.924 (-239d21h56m18s71ms)
-                  cch   = 2025-12-06 18:56:23.700 (-239d21h56m23s295ms)
-      WRITE_EXTERNAL_STORAGE (allow): 
-          Access: pers  = 2025-12-06 18:56:28.924 (-239d21h56m18s71ms)
-                  cch   = 2025-12-06 18:56:23.700 (-239d21h56m23s295ms)
+          Reject: pers  = 2025-12-06 18:56:24.496 (-239d21h56m30s554ms)
+      READ_EXTERNAL_STORAGE (allow): 
+          Access: pers  = 2025-12-06 18:56:28.924 (-239d21h56m26s126ms)
+                  cch   = 2025-12-06 18:56:23.700 (-239d21h56m31s350ms)
+      WRITE_EXTERNAL_STORAGE (allow): 
+          Access: pers  = 2025-12-06 18:56:28.924 (-239d21h56m26s126ms)
+                  cch   = 2025-12-06 18:56:23.700 (-239d21h56m31s350ms)
   Uid 1041:
     state=cch  
     Package audioserver:
       WAKE_LOCK (allow): 
-          Access: cch   = 2026-08-03 16:51:31.806 (-1m15s189ms)
+          Access: cch   = 2026-08-03 16:51:31.806 (-1m23s244ms)
           duration=+2s888ms
       GET_USAGE_STATS (default): 
-          Reject: cch   = 2026-08-03 16:13:38.716 (-39m8s279ms)
+          Reject: cch   = 2026-08-03 16:13:38.716 (-39m16s334ms)
   Uid 1068:
     state=pers 
     Package com.android.se:
       READ_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2026-08-03 16:13:43.435 (-39m3s560ms)
-      WRITE_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2026-08-03 16:13:43.435 (-39m3s560ms)
+          Access: cch   = 2026-08-03 16:13:43.435 (-39m11s615ms)
+      WRITE_EXTERNAL_STORAGE (allow): 
+          Access: cch   = 2026-08-03 16:13:43.435 (-39m11s615ms)
   Uid 2000:
     state=cch  
     Package com.android.shell:
       AUDIO_RING_VOLUME (allow): 
-          Access: cch   = 2025-12-07 15:02:29.916 (-239d1h50m17s79ms)
+          Access: cch   = 2025-12-07 15:02:29.916 (-239d1h50m25s134ms)
   Uid u0a5:
     state=cch  
     Package com.ivona.orchestrator:
       READ_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2025-12-07 16:06:13.286 (-239d0h46m33s709ms)
-      WRITE_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2025-12-07 16:06:13.286 (-239d0h46m33s709ms)
-      RUN_IN_BACKGROUND (allow): 
-          Access: bg    = 2025-12-06 19:02:54.041 (-239d21h49m52s954ms)
-                  cch   = 2025-12-06 19:02:51.359 (-239d21h49m55s636ms)
+          Access: cch   = 2025-12-07 16:06:13.286 (-239d0h46m41s764ms)
+      WRITE_EXTERNAL_STORAGE (allow): 
+          Access: cch   = 2025-12-07 16:06:13.286 (-239d0h46m41s764ms)
+      RUN_IN_BACKGROUND (allow): 
+          Access: bg    = 2025-12-06 19:02:54.041 (-239d21h50m1s9ms)
+                  cch   = 2025-12-06 19:02:51.359 (-239d21h50m3s691ms)
   Uid u0a6:
     state=cch  
     Package com.amazon.dp.fbcontacts:
       READ_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2026-08-03 16:13:56.403 (-38m50s592ms)
-      WRITE_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2026-08-03 16:13:56.403 (-38m50s592ms)
-      RUN_IN_BACKGROUND (allow): 
-          Access: cch   = 2026-08-03 16:13:56.402 (-38m50s593ms)
+          Access: cch   = 2026-08-03 16:13:56.403 (-38m58s647ms)
+      WRITE_EXTERNAL_STORAGE (allow): 
+          Access: cch   = 2026-08-03 16:13:56.403 (-38m58s647ms)
+      RUN_IN_BACKGROUND (allow): 
+          Access: cch   = 2026-08-03 16:13:56.402 (-38m58s648ms)
   Uid u0a7:
     state=fg   
     Package com.amazon.client.metrics:
       WAKE_LOCK (allow): 
-          Access: fgsvc = 2026-08-03 16:14:08.155 (-38m38s840ms)
-                  fg    = 2026-08-03 16:20:24.304 (-32m22s691ms)
+          Access: fgsvc = 2026-08-03 16:14:08.155 (-38m46s895ms)
+                  fg    = 2026-08-03 16:20:24.304 (-32m30s746ms)
           duration=+1s99ms
       READ_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2026-08-03 16:13:42.352 (-39m4s643ms)
-      WRITE_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2026-08-03 16:13:42.352 (-39m4s643ms)
+          Access: cch   = 2026-08-03 16:13:42.352 (-39m12s698ms)
+      WRITE_EXTERNAL_STORAGE (allow): 
+          Access: cch   = 2026-08-03 16:13:42.352 (-39m12s698ms)
   Uid u0a9:
     state=cch  
```

### `appops/firelauncher.stdout.txt`

```diff
--- before/appops/firelauncher.stdout.txt

+++ after/appops/firelauncher.stdout.txt

@@ -1,4 +1,4 @@

-TAKE_AUDIO_FOCUS: allow; time=+239d21h41m11s622ms ago
-READ_EXTERNAL_STORAGE: allow; time=+38m58s509ms ago
-WRITE_EXTERNAL_STORAGE: allow; time=+38m58s509ms ago
-REQUEST_DELETE_PACKAGES: allow; time=+239d0h48m13s347ms ago
+TAKE_AUDIO_FOCUS: allow; time=+239d21h41m19s708ms ago
+READ_EXTERNAL_STORAGE: allow; time=+39m6s595ms ago
+WRITE_EXTERNAL_STORAGE: allow; time=+39m6s595ms ago
+REQUEST_DELETE_PACKAGES: allow; time=+239d0h48m21s433ms ago
```

### `appops/microsoft.stdout.txt`

```diff
--- before/appops/microsoft.stdout.txt

+++ after/appops/microsoft.stdout.txt

@@ -1,5 +1,5 @@

 COARSE_LOCATION: allow
-FINE_LOCATION: allow; time=+3h8m9s386ms ago
-READ_EXTERNAL_STORAGE: allow; time=+6m50s888ms ago
-WRITE_EXTERNAL_STORAGE: allow; time=+6m50s888ms ago
-BIND_ACCESSIBILITY_SERVICE: allow; time=+36s721ms ago
+FINE_LOCATION: allow; time=+3h8m17s496ms ago
+READ_EXTERNAL_STORAGE: allow; time=+6m58s998ms ago
+WRITE_EXTERNAL_STORAGE: allow; time=+6m58s998ms ago
+BIND_ACCESSIBILITY_SERVICE: allow; time=+4s5ms ago
```

### `metadata.tsv`

```diff
--- before/metadata.tsv

+++ after/metadata.tsv

@@ -1,3 +1,3 @@

-test_id=PHASE4-ALIAS-T04-BEFORE
+test_id=PHASE4-ALIAS-T04-AFTER-ROLLBACK
 serial=G001LT0511550CFT
-timestamp_utc=2026-08-03T08:52:43Z
+timestamp_utc=2026-08-03T08:52:51Z
```

### `package/firelauncher.stdout.txt`

```diff
--- before/package/firelauncher.stdout.txt

+++ after/package/firelauncher.stdout.txt

@@ -741,4 +741,6 @@

       amazon.aosp.permission.INTERACT_ACROSS_USERS_FULL
       com.amazon.permission.INTERACT_ACROSS_USERS_FULL
+      amazon.aosp.permission.INTERACT_ACROSS_USERS_FULL
+      com.amazon.permission.INTERACT_ACROSS_USERS_FULL
     install permissions:
       com.amazon.firelauncher.cardproducer.utils.HOST_APP_COLD_START_RECEIVER: granted=true
@@ -849,10 +851,10 @@

 
 Package Changes:
-  Sequence number=10
+  Sequence number=12
   User 0:
     seq=0, package=org.fireosresearch.home.p0
     seq=4, package=com.google.android.gms
     seq=5, package=com.microsoft.launcher
-    seq=9, package=org.fireosresearch.phase4.alias
+    seq=11, package=org.fireosresearch.phase4.alias
 
 
```

### `summary.md`

```diff
--- before/summary.md

+++ after/summary.md

@@ -1,7 +1,7 @@

 # Phase 3C state snapshot
 
-- Test ID: PHASE4-ALIAS-T04-BEFORE
+- Test ID: PHASE4-ALIAS-T04-AFTER-ROLLBACK
 - Serial: G001LT0511550CFT
-- Timestamp UTC: 2026-08-03T08:52:47Z
+- Timestamp UTC: 2026-08-03T08:52:55Z
 - This snapshot executed read-only ADB commands only.
 - Individual command failures are preserved in *.exit_code.txt and are not silently treated as absence.
```

### `users/dumpsys_user.stdout.txt`

```diff
--- before/users/dumpsys_user.stdout.txt

+++ after/users/dumpsys_user.stdout.txt

@@ -3,8 +3,8 @@

     State: RUNNING_UNLOCKED
     Created: <unknown>
-    Last logged in: +39m2s760ms ago
+    Last logged in: +39m10s723ms ago
     Last logged in fingerprint: Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys
-    Start time: +39m6s982ms ago
-    Unlock time: +39m2s590ms ago
+    Start time: +39m14s945ms ago
+    Unlock time: +39m10s553ms ago
     Has profile owner: true
     Restrictions:
```

### `window/input.stdout.txt`

```diff
--- before/window/input.stdout.txt

+++ after/window/input.stdout.txt

@@ -466,14 +466,14 @@

     0: 'WindowManager (server)'
   RecentQueue: length=10
-    DeviceResetEvent(deviceId=6), policyFlags=0x00000000, age=2349058.5ms
-    ConfigurationChangedEvent(), policyFlags=0x00000000, age=2349058.5ms
-    KeyEvent, age=79027.4ms
-    KeyEvent, age=79027.4ms
-    KeyEvent, age=78489.4ms
-    KeyEvent, age=78489.4ms
-    KeyEvent, age=76264.4ms
-    KeyEvent, age=76264.4ms
-    KeyEvent, age=37066.4ms
-    KeyEvent, age=37066.4ms
+    KeyEvent, age=87017.1ms
+    KeyEvent, age=87017.1ms
+    KeyEvent, age=86479.1ms
+    KeyEvent, age=86479.1ms
+    KeyEvent, age=84254.1ms
+    KeyEvent, age=84254.1ms
+    KeyEvent, age=45056.1ms
+    KeyEvent, age=45056.1ms
+    KeyEvent, age=4131.1ms
+    KeyEvent, age=4131.1ms
   PendingEvent: <none>
   InboundQueue: <empty>
```

### `window/processes.stdout.txt`

```diff
--- before/window/processes.stdout.txt

+++ after/window/processes.stdout.txt

@@ -380,3 +380,3 @@

 u0_a180       7375   352 com.android.vending:background com.android.vending:background
 root          7441   497 sleep                       sleep 120
-shell         8066   432 ps                          ps -A -o USER,PID,PPID,NAME,ARGS
+shell         8397   432 ps                          ps -A -o USER,PID,PPID,NAME,ARGS
```

### `window/windows.stdout.txt`

```diff
--- before/window/windows.stdout.txt

+++ after/window/windows.stdout.txt

@@ -6,5 +6,5 @@

       fl=NOT_FOCUSABLE NOT_TOUCHABLE LAYOUT_IN_SCREEN HARDWARE_ACCELERATED
       pfl=SHOW_FOR_ALL_USERS}
-    Requested w=1200 h=1920 mLayoutSeq=285
+    Requested w=1200 h=1920 mLayoutSeq=456
     mBaseLayer=311000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
     mToken=WindowToken{e06c09f android.os.BinderProxy@cda9a3e}
@@ -35,5 +35,5 @@

     mAttrs={(0,0)(fillxfill) sim={adjust=pan} ty=NAVIGATION_BAR fmt=TRANSLUCENT
       fl=NOT_FOCUSABLE NOT_TOUCH_MODAL TOUCHABLE_WHEN_WAKING WATCH_OUTSIDE_TOUCH SPLIT_TOUCH HARDWARE_ACCELERATED FLAG_SLIPPERY}
-    Requested w=1200 h=72 mLayoutSeq=285
+    Requested w=1200 h=72 mLayoutSeq=456
     mBaseLayer=231000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
     mToken=WindowToken{7a91801 android.os.BinderProxy@1f009e8}
@@ -65,5 +65,5 @@

     mAttrs={(0,0)(fillx36) gr=TOP CENTER_VERTICAL sim={adjust=resize} layoutInDisplayCutoutMode=always ty=STATUS_BAR fmt=TRANSLUCENT
       fl=NOT_FOCUSABLE TOUCHABLE_WHEN_WAKING WATCH_OUTSIDE_TOUCH SPLIT_TOUCH HARDWARE_ACCELERATED DRAWS_SYSTEM_BAR_BACKGROUNDS}
-    Requested w=1200 h=36 mLayoutSeq=285
+    Requested w=1200 h=36 mLayoutSeq=456
     mBaseLayer=171000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
     mToken=WindowToken{16d86c7 android.os.BinderProxy@f358006}
@@ -96,5 +96,5 @@

       fl=DIM_BEHIND ALT_FOCUSABLE_IM SPLIT_TOUCH HARDWARE_ACCELERATED
       pfl=SHOW_FOR_ALL_USERS}
-    Requested w=870 h=412 mLayoutSeq=285
+    Requested w=870 h=412 mLayoutSeq=456
     mBaseLayer=111000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
     mToken=WindowToken{6c680f1 android.os.BinderProxy@d4ec098}
@@ -127,5 +127,5 @@

       pfl=NO_MOVE_ANIMATION
       vsysui=LAYOUT_STABLE LAYOUT_HIDE_NAVIGATION LAYOUT_FULLSCREEN}
-    Requested w=1200 h=72 mLayoutSeq=285
+    Requested w=1200 h=72 mLayoutSeq=456
     mBaseLayer=21000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
     mToken=WindowToken{ca3bdb1 android.os.BinderProxy@b1bf858}
@@ -160,5 +160,5 @@

       pfl=FORCE_DRAW_STATUS_BAR_BACKGROUND
       vsysui=LAYOUT_STABLE LAYOUT_HIDE_NAVIGATION LAYOUT_FULLSCREEN}
-    Requested w=1200 h=1920 mLayoutSeq=285
+    Requested w=1200 h=1920 mLayoutSeq=456
     mBaseLayer=21000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
     mToken=AppWindowToken{e63cf5a token=Token{d3a1305 ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}}}
@@ -180,5 +180,5 @@

     Lst insets: overscan=[0,0][0,0] content=[0,36][0,0] visible=[0,36][0,0] stable=[0,36][0,72] physical=[0,0][0,0] outset=[0,0][0,0] cutout=com.android.server.wm.utils.WmDisplayCutout@3c1
     WindowStateAnimator{bffb519 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}:
-      mSurface=Surface(name=com.amazon.firelauncher/com.amazon.firelauncher.Launcher)/@0xf3d0bc2
+      mSurface=Surface(name=com.amazon.firelauncher/com.amazon.firelauncher.Launcher)/@0xabc8ba2
       Surface: shown=true layer=0 alpha=1.0 rect=(0.0,0.0) 1200 x 1920 transform=(1.0, 0.0, 1.0, 0.0)
       mDrawState=HAS_DRAWN       mLastHidden=false
@@ -191,5 +191,5 @@

     mAttrs={(0,0)(1920x1920) gr=TOP START CENTER layoutInDisplayCutoutMode=always ty=WALLPAPER fmt=RGBX_8888 wanim=0x1030308
       fl=NOT_FOCUSABLE NOT_TOUCHABLE LAYOUT_IN_SCREEN LAYOUT_NO_LIMITS LAYOUT_INSET_DECOR}
-    Requested w=1920 h=1920 mLayoutSeq=285
+    Requested w=1920 h=1920 mLayoutSeq=456
     mIsImWindow=false mIsWallpaper=true mIsFloatingLayer=true mWallpaperVisible=true
     mBaseLayer=11000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
@@ -236,5 +236,5 @@

   mLastWallpaperX=0.0 mLastWallpaperY=0.5
   mSystemBooted=true mDisplayEnabled=true
-  mTransactionSequence=438
+  mTransactionSequence=630
   mDisplayFrozen=false windows=0 client=false apps=0  mRotation=0 mAltOrientation=false
   mLastWindowForcedOrientation=-1 mLastOrientation=-1
@@ -248,3 +248,3 @@

     mLastUsedAppTransition=TRANSIT_WALLPAPER_OPEN
     mLastOpeningApp=AppWindowToken{e63cf5a token=Token{d3a1305 ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}}}
-    mLastClosingApp=AppWindowToken{5bedddc token=Token{26a224f ActivityRecord{aecb4ae u0 org.fireosresearch.phase4.alias/.SecondaryHomeActivity t30}}}
+    mLastClosingApp=AppWindowToken{2dd6ebc token=Token{56eaaf ActivityRecord{2a7e28e u0 org.fireosresearch.phase4.alias/.SecondaryHomeActivity t31}}}
```
