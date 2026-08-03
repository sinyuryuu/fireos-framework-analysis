# Phase 3C snapshot comparison

- Before: `adb/phase3c/PHASE3C-PREFERRED-P0-02/before`
- After: `adb/phase3c/PHASE3C-PREFERRED-P0-02/after_rollback`
- Before files: `175`
- After files: `175`
- Changed files: `20`

## Changed files

- `activity/activities.stdout.txt` — changed
- `activity/recents.stdout.txt` — changed
- `activity/top.stdout.txt` — changed
- `appops/all.stdout.txt` — changed
- `appops/firelauncher.stdout.txt` — changed
- `appops/microsoft.stdout.txt` — changed
- `devices.stdout.txt` — changed
- `metadata.tsv` — changed
- `overlay/dump.stdout.txt` — changed
- `package/firelauncher.stdout.txt` — changed
- `package/full_dump.stdout.txt` — changed
- `package/persistent_preferred.stdout.txt` — changed
- `package/preferred_activities.stdout.txt` — changed
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
63:   ResumedActivity: ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}
64:   mFocusedStack=ActivityStack{fbfca5c stackId=0 type=home mode=fullscreen visible=true translucent=false, 1 tasks} mLastFocusedStack=ActivityStack{fbfca5c stackId=0 type=home mode=fullscreen visible=true translucent=false, 1 tasks}
69:    mHomeStack=ActivityStack{fbfca5c stackId=0 type=home mode=fullscreen visible=true translucent=false, 1 tasks}
70:   isHomeRecentsComponent=false  KeyguardController:
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
43:       DecorView@e44088a[Launcher]
46:             com.amazon.firelauncher.appsgrid.ui.drag.DragLayer{ec58971 V.E...... ......I. 0,0-0,0 #7f090336 app:id/magazine_container}
49:               com.amazon.firelauncher.view.EnhancedViewPager{5ca50c4 VFED..... ......I. 0,0-0,0 #7f090379 app:id/pager}
50:                 com.amazon.firelauncher.appsgrid.ui.ScrollableMainView{7584bad V.E...... ......I. 0,0-0,0}
51:                   com.amazon.firelauncher.appsgrid.ui.GradientScrimFrameLayout{c751ee2 V.E...... ......I. 0,0-0,0}
52:                     com.amazon.firelauncher.appsgrid.ui.GridView{2133273 VFED..... ......I. 0,0-0,0 #7f09027a app:id/favorites_page}
58:                 com.amazon.firelauncher.view.ScrollObservableContainer{c44365 V.E...... ......I. 0,0-0,0}
59:                   com.amazon.firelauncher.view.ChannelBackgroundView{537a83a V.ED..... ......I. 0,0-0,0 #7f0900ef app:id/background_view}
60:                   com.amazon.firelauncher.view.ScrollingLinearRecyclerView{4647f3c VFED..... ......I. 0,0-0,0 #7f09039e app:id/recycler}
75:                         com.amazon.firelauncher.view.LoadingDotsView{5e5cfd5 V.E...... ......I. 0,0-0,0 #7f09032c app:id/loading_dots}
88:                         com.amazon.firelauncher.view.NavTabView{1f58c88 VFE...C.. ......I. 0,0-0,0}
91:                         com.amazon.firelauncher.view.NavTabView{205d0bc VFE...C.. ..S...I. 0,0-0,0}
94:                         com.amazon.firelauncher.view.NavTabView{636cccb VFE...C.. ......I. 0,0-0,0}
97:                 com.amazon.firelauncher.view.SearchWidgetHostLayout{9470766 V.E...... ......I. 0,0-0,0 #7f0903ba app:id/search_bar_widget}
98:                   com.amazon.firelauncher.search.SearchAppWidgetHostView{6636aa7 V.E...... R.....I. 0,0-0,0}
170:                     com.amazon.firelauncher.appsgrid.ui.FolderView{456eb5f VFED..... ......I. 0,0-0,0 #7f090288 app:id/folder_grid}
182:       context: com.amazon.firelauncher.Launcher@5653290
183:       client: com.amazon.firelauncher.Launcher@5653290
210:         mContainer=com.amazon.firelauncher.view.EnhancedViewPager{5ca50c4 VFED..... ......I. 0,0-0,0 #7f090379 app:id/pager}
211:         mView=com.amazon.firelauncher.appsgrid.ui.ScrollableMainView{7584bad V.E...... ......I. 0,0-0,0}
228:         mContainer=com.amazon.firelauncher.view.EnhancedViewPager{5ca50c4 VFED..... ......I. 0,0-0,0 #7f090379 app:id/pager}
229:         mView=com.amazon.firelauncher.view.ScrollObservableContainer{c44365 V.E...... ......I. 0,0-0,0}
245:         mContainer=com.amazon.firelauncher.view.EnhancedViewPager{5ca50c4 VFED..... ......I. 0,0-0,0 #7f090379 app:id/pager}
```

### `appops/all.stdout.txt`

```text
725:     Package com.android.launcher3:
1019:     Package com.amazon.firelauncher:
1327:     Package com.microsoft.launcher:
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

### `properties/getprop.stdout.txt`

```text
105: [init.svc.wmt_launcher]: [running]
```

### `window/input.stdout.txt`

```text
454:   FocusedApplication: name='AppWindowToken{1f10017 token=Token{e40cc96 ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}}}', dispatchingTimeout=5000.000ms
463:     5: name='Window{2c47b02 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}', displayId=0, paused=false, hasFocus=false, hasWallpaper=false, visible=false, canReceiveKeys=false, flags=0x81910120, type=0x00000001, layer=0, frame=[0,0][1200,1920], scale=1.000000, touchableRegion=[0,0][1200,1920], inputFeatures=0x00000000, ownerPid=1919, ownerUid=10120, dispatchingTimeout=5000.000ms
501:     6: channelName='2c47b02 com.amazon.firelauncher/com.amazon.firelauncher.Launcher (server)', windowName='Window{2c47b02 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}', status=NORMAL, monitor=false, inputPublisherBlocked=false
```

### `window/processes.stdout.txt`

```text
283: system         424     1 wmt_launcher                wmt_launcher -p /vendor/firmware/
377: u0_a75        1909   350 com.android.launcher3       com.android.launcher3
378: u0_a120       1919   350 com.amazon.firelauncher     com.amazon.firelauncher
```

### `window/windows.stdout.txt`

```text
157:   Window #5 Window{2c47b02 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}:
159:     mOwnerUid=10120 mShowToOwnerOnly=true package=com.amazon.firelauncher appop=NONE
166:     mToken=AppWindowToken{1f10017 token=Token{e40cc96 ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}}}
167:     mAppToken=AppWindowToken{1f10017 token=Token{e40cc96 ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}}}
172:     mFullConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
183:     WindowStateAnimator{d37c4f8 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}:
254:   mCurrentFocus=Window{f76e49b u0 StatusBar}
255:   mFocusedApp=AppWindowToken{1f10017 token=Token{e40cc96 ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}}}
282:     mLastClosingApp=AppWindowToken{1f10017 token=Token{e40cc96 ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}}}
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
+      hasBeenVisible=false mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=23218 (inactive for 10s)
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
@@ -43,87 +43,31 @@

            statusBarColor=0
            navigationBarColor=ff000000
-          launchFailed=false launchCount=0 lastLaunchTime=-1h17m41s953ms
-          haveState=false icicle=null
-          state=RESUMED stopped=false delayedResume=false finishing=false
-          keysPaused=false inHistory=true visible=true sleeping=false idle=true mStartingWindowState=STARTING_WINDOW_NOT_SHOWN
+          launchFailed=false launchCount=0 lastLaunchTime=-13s439ms
+          haveState=true icicle=Bundle[mParcelledData.dataSize=1880]
+          state=STOPPED stopped=true delayedResume=false finishing=false
+          keysPaused=false inHistory=true visible=false sleeping=true idle=true mStartingWindowState=STARTING_WINDOW_NOT_SHOWN
           fullscreen=true noDisplay=false immersive=false launchMode=2
           frozenBeforeDestroy=false forceNewConfig=false
           mActivityType=home
-          waitingVisible=false nowVisible=true lastVisibleTime=-1h7m58s70ms
+          displayStartTime=-13s435ms startTime=0
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
-
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
+    hasBeenVisible=false mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=23218 (inactive for 10s)
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
+    hasBeenVisible=false mResizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION mSupportsPictureInPicture=false isResizeable=true lastActiveTime=23130 (inactive for 10s)
```

### `activity/top.stdout.txt`

```diff
--- before/activity/top.stdout.txt

+++ after/activity/top.stdout.txt

@@ -1,12 +1,29 @@

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
     ViewRoot:
@@ -22,22 +39,147 @@

     Choreographer:
       mFrameScheduled=false
-      mLastFrameTime=606732 (4078132 ms ago)
+      mLastFrameTime=29853 (4242 ms ago)
     View Hierarchy:
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
+      DecorView@e44088a[Launcher]
+        android.widget.FrameLayout{24ddefb V.E...... ......I. 0,0-0,0}
+          android.widget.FrameLayout{63a9b18 V.E...... ......I. 0,0-0,0 #1020002 android:id/content}
+            com.amazon.firelauncher.appsgrid.ui.drag.DragLayer{ec58971 V.E...... ......I. 0,0-0,0 #7f090336 app:id/magazine_container}
+              android.widget.FrameLayout{8622356 V.E...... ......I. 0,0-0,0 #7f0900ee app:id/background_parent}
+                android.widget.ImageView{3116fd7 V.ED..... ......ID 0,0-0,0 #7f090125 app:id/channel_background}
+              com.amazon.firelauncher.view.EnhancedViewPager{5ca50c4 VFED..... ......I. 0,0-0,0 #7f090379 app:id/pager}
+                com.amazon.firelauncher.appsgrid.ui.ScrollableMainView{7584bad V.E...... ......I. 0,0-0,0}
+                  com.amazon.firelauncher.appsgrid.ui.GradientScrimFrameLayout{c751ee2 V.E...... ......I. 0,0-0,0}
+                    com.amazon.firelauncher.appsgrid.ui.GridView{2133273 VFED..... ......I. 0,0-0,0 #7f09027a app:id/favorites_page}
+                    android.widget.ImageView{37db530 V.ED..... ......ID 0,0-0,0 #7f0902ad app:id/header_background}
+                    android.widget.ImageView{cdaf5a9 V.ED..... ......ID 0,0-0,0 #7f0902b2 app:id/header_shadow}
+                android.widget.FrameLayout{9ca472e V.E...... ......I. 0,0-0,0}
+                  androidx.fragment.app.FragmentContainerView{86482cf V.E...... ......I. 0,0-0,0 #7f09029a app:id/fragment_container}
+                  android.view.ViewStub{dc0f45c G.E...... ......I. 0,0-0,0 #7f090198 app:id/dali_fragment_stub}
+                com.amazon.firelauncher.view.ScrollObservableContainer{c44365 V.E...... ......I. 0,0-0,0}
+                  com.amazon.firelauncher.view.ChannelBackgroundView{537a83a V.ED..... ......I. 0,0-0,0 #7f0900ef app:id/background_view}
+                  com.amazon.firelauncher.view.ScrollingLinearRecyclerView{4647f3c VFED..... ......I. 0,0-0,0 #7f09039e app:id/recycler}
+                  android.widget.ImageView{4d07ceb V.ED..... ......ID 0,0-0,0 #7f0902ad app:id/header_background}
+                  android.widget.ImageView{b96fa48 V.ED..... ......ID 0,0-0,0 #7f0902b2 app:id/header_shadow}
+                  android.widget.LinearLayout{b3ab0e1 G.E...... ......I. 0,0-0,0 #7f0903a2 app:id/register_tab}
+                    android.view.View{8e80e06 V.ED..... ......ID 0,0-0,0 #7f09047f app:id/top_divider}
+                  android.widget.LinearLayout{db7fcc7 G.E...... ......I. 0,0-0,0 #7f090332 app:id/loading_view}
+                    android.widget.FrameLayout{f4572f4 GFE...C.. ......ID 0,0-0,0 #7f090334 app:id/loading_view_pablo}
+                      android.widget.LinearLayout{6507a1d V.E...... ......I. 0,0-0,0}
+                        android.widget.ImageView{4e70492 V.ED..... ......ID 0,0-0,0 #7f090325 app:id/loading_background}
+                        android.widget.ImageView{4ad9e63 V.ED..... ......ID 0,0-0,0 #7f090325 app:id/loading_background}
+                        android.widget.ImageView{7c0ca60 V.ED..... ......ID 0,0-0,0 #7f090325 app:id/loading_background}
+                        android.widget.ImageView{ff9b19 V.ED..... ......ID 0,0-0,0 #7f090325 app:id/loading_background}
+                        android.widget.ImageView{c6cd7de V.ED..... ......ID 0,0-0,0 #7f090325 app:id/loading_background}
+                      android.widget.LinearLayout{7d1bdbf V.E...... ......I. 0,0-0,0}
+                        android.widget.TextView{cd82c8c V.ED..... ......ID 0,0-0,0 #7f090331 app:id/loading_text_pablo}
+                        com.amazon.firelauncher.view.LoadingDotsView{5e5cfd5 V.E...... ......I. 0,0-0,0 #7f09032c app:id/loading_dots}
+                          android.widget.ImageView{bea93ea V.ED..... ......ID 0,0-0,0 #7f0901b0 app:id/dot1}
+                          android.widget.ImageView{cee76db V.ED..... ......ID 0,0-0,0 #7f0901b1 app:id/dot2}
+                          android.widget.ImageView{2218578 V.ED..... ......ID 0,0-0,0 #7f0901b2 app:id/dot3}
+                    android.widget.LinearLayout{1c09451 V.E...... ......I. 0,0-0,0 #7f090333 app:id/loading_view_magazine}
+                      android.widget.ProgressBar{3d604b6 V.ED..... ......ID 0,0-0,0}
+                      android.widget.TextView{253a5b7 V.ED..... ......ID 0,0-0,0 #7f090330 app:id/loading_text}
+                  android.view.View{ca58124 G.ED..... ......ID 0,0-0,0 #7f0903ef app:id/status_bar_underlay}
+              android.widget.FrameLayout{5a9248d V.E...... ......I. 0,0-0,0 #7f0902af app:id/header_container}
+                android.widget.FrameLayout{435b642 V.E...... ......I. 0,0-0,0 #7f090342 app:id/menu_bar_container}
+                  amazon.fluid.widget.ViewPagerTabBar{172e653 V.E...... ......I. 0,0-0,0 #7f090423 app:id/tab_container}
+                    amazon.fluid.widget.ViewPagerTabHorizontalScrollView{74b8b90 VFED..... ......ID 0,0-0,0 #7f090261 app:id/f_tab_horizontal_scroll_view}
+                      amazon.fluid.widget.ViewPagerTabStrip{1107c89 V.ED..... ......I. 0,0-0,0 #7f090262 app:id/f_tab_strip}
+                        com.amazon.firelauncher.view.NavTabView{1f58c88 VFE...C.. ......I. 0,0-0,0}
+                          android.widget.TextView{4ecf48e V.ED..... ......ID 0,0-0,0 #7f090051 app:id/active}
+                          android.widget.TextView{f3b94af V.ED..... ......ID 0,0-0,0 #7f0902f5 app:id/inactive}
+                        com.amazon.firelauncher.view.NavTabView{205d0bc VFE...C.. ..S...I. 0,0-0,0}
+                          android.widget.TextView{f7b5845 V.ED..... ..S...ID 0,0-0,0 #7f090051 app:id/active}
+                          android.widget.TextView{6c7cb9a V.ED..... ..S...ID 0,0-0,0 #7f0902f5 app:id/inactive}
+                        com.amazon.firelauncher.view.NavTabView{636cccb VFE...C.. ......I. 0,0-0,0}
+                          android.widget.TextView{7bd3ca8 V.ED..... ......ID 0,0-0,0 #7f090051 app:id/active}
+                          android.widget.TextView{5fe33c1 V.ED..... ......ID 0,0-0,0 #7f0902f5 app:id/inactive}
+                com.amazon.firelauncher.view.SearchWidgetHostLayout{9470766 V.E...... ......I. 0,0-0,0 #7f0903ba app:id/search_bar_widget}
+                  com.amazon.firelauncher.search.SearchAppWidgetHostView{6636aa7 V.E...... R.....I. 0,0-0,0}
+                    android.widget.LinearLayout{6fd7b54 VFE...C.. ......I. 0,0-0,0 #7f09004f app:id/anim_remote_widget_view}
+                      android.widget.ImageView{c794afd VFED..C.. ......ID 0,0-0,0 #7f090089 app:id/anim_widget_icon_view}
+                      android.widget.ViewFlipper{12c33f2 V.E...... ......I. 0,0-0,0 #7f09006c app:id/anim_view_flipper_1}
+                        android.widget.TextView{6d20a43 V.ED..C.. ......I. 0,0-0,0 #7f090050 app:id/anim_text_view_1}
+                      android.widget.ViewFlipper{960f8c0 V.E...... ......I. 0,0-0,0 #7f090077 app:id/anim_view_flipper_2}
+                        android.widget.TextView{e9499f9 V.ED..C.. ......I. 0,0-0,0 #7f09005b app:id/anim_text_view_2}
+                      android.widget.ViewFlipper{bc59d3e V.E...... ......I. 0,0-0,0 #7f090081 app:id/anim_view_flipper_3}
+                        android.widget.TextView{501079f V.ED..C.. ......I. 0,0-0,0 #7f090065 app:id/anim_text_view_3}
+                      android.widget.ViewFlipper{5bce0ec V.E...... ......I. 0,0-0,0 #7f090082 app:id/anim_view_flipper_4}
+                        android.widget.TextView{7bdcb5 V.ED..C.. ......I. 0,0-0,0 #7f090066 app:id/anim_text_view_4}
+                      android.widget.ViewFlipper{afa4f4a V.E...... ......I. 0,0-0,0 #7f090083 app:id/anim_view_flipper_5}
+                        android.widget.TextView{df87ebb V.ED..C.. ......I. 0,0-0,0 #7f090067 app:id/anim_text_view_5}
+                      android.widget.ViewFlipper{90d1fd8 V.E...... ......I. 0,0-0,0 #7f090084 app:id/anim_view_flipper_6}
+                        android.widget.TextView{35a8f31 V.ED..C.. ......I. 0,0-0,0 #7f090068 app:id/anim_text_view_6}
+                      android.widget.ViewFlipper{6161616 V.E...... ......I. 0,0-0,0 #7f090085 app:id/anim_view_flipper_7}
+                        android.widget.TextView{d264b97 V.ED..C.. ......I. 0,0-0,0 #7f090069 app:id/anim_text_view_7}
+                      android.widget.ViewFlipper{2206184 V.E...... ......I. 0,0-0,0 #7f090086 app:id/anim_view_flipper_8}
+                        android.widget.TextView{597ed6d V.ED..C.. ......I. 0,0-0,0 #7f09006a app:id/anim_text_view_8}
+                      android.widget.ViewFlipper{b557da2 V.E...... ......I. 0,0-0,0 #7f090087 app:id/anim_view_flipper_9}
+                        android.widget.TextView{cfa0a33 V.ED..C.. ......I. 0,0-0,0 #7f09006b app:id/anim_text_view_9}
+                      android.widget.ViewFlipper{c0411f0 G.E...... ......I. 0,0-0,0 #7f09006d app:id/anim_view_flipper_10}
+                        android.widget.TextView{ad2f369 V.ED..C.. ......I. 0,0-0,0 #7f090051 app:id/anim_text_view_10}
+                      android.widget.ViewFlipper{e31d1ee G.E...... ......I. 0,0-0,0 #7f09006e app:id/anim_view_flipper_11}
+                        android.widget.TextView{541168f V.ED..C.. ......I. 0,0-0,0 #7f090052 app:id/anim_text_view_11}
+                      android.widget.ViewFlipper{3305d1c G.E...... ......I. 0,0-0,0 #7f09006f app:id/anim_view_flipper_12}
+                        android.widget.TextView{79e5d25 V.ED..C.. ......I. 0,0-0,0 #7f090053 app:id/anim_text_view_12}
+                      android.widget.ViewFlipper{e6d1efa G.E...... ......I. 0,0-0,0 #7f090070 app:id/anim_view_flipper_13}
+                        android.widget.TextView{3428cab V.ED..C.. ......I. 0,0-0,0 #7f090054 app:id/anim_text_view_13}
+                      android.widget.ViewFlipper{1742f08 G.E...... ......I. 0,0-0,0 #7f090071 app:id/anim_view_flipper_14}
+                        android.widget.TextView{cfca6a1 V.ED..C.. ......I. 0,0-0,0 #7f090055 app:id/anim_text_view_14}
+                      android.widget.ViewFlipper{3de30c6 G.E...... ......I. 0,0-0,0 #7f090072 app:id/anim_view_flipper_15}
+                        android.widget.TextView{79b4887 V.ED..C.. ......I. 0,0-0,0 #7f090056 app:id/anim_text_view_15}
+                      android.widget.ViewFlipper{ca133b4 G.E...... ......I. 0,0-0,0 #7f090073 app:id/anim_view_flipper_16}
+                        android.widget.TextView{f9c0bdd V.ED..C.. ......I. 0,0-0,0 #7f090057 app:id/anim_text_view_16}
+                      android.widget.ViewFlipper{afc9352 G.E...... ......I. 0,0-0,0 #7f090074 app:id/anim_view_flipper_17}
+                        android.widget.TextView{5d9e623 V.ED..C.. ......I. 0,0-0,0 #7f090058 app:id/anim_text_view_17}
+                      android.widget.ViewFlipper{3f7d720 G.E...... ......I. 0,0-0,0 #7f090075 app:id/anim_view_flipper_18}
+                        android.widget.TextView{6d288d9 V.ED..C.. ......I. 0,0-0,0 #7f090059 app:id/anim_text_view_18}
+                      android.widget.ViewFlipper{e2c929e G.E...... ......I. 0,0-0,0 #7f090076 app:id/anim_view_flipper_19}
+                        android.widget.TextView{1dac17f V.ED..C.. ......I. 0,0-0,0 #7f09005a app:id/anim_text_view_19}
+                      android.widget.ViewFlipper{853454c G.E...... ......I. 0,0-0,0 #7f090078 app:id/anim_view_flipper_20}
+                        android.widget.TextView{f59d995 V.ED..C.. ......I. 0,0-0,0 #7f09005c app:id/anim_text_view_20}
+                      android.widget.ViewFlipper{7cb3aaa G.E...... ......I. 0,0-0,0 #7f090079 app:id/anim_view_flipper_21}
+                        android.widget.TextView{6e3f69b V.ED..C.. ......I. 0,0-0,0 #7f09005d app:id/anim_text_view_21}
+                      android.widget.ViewFlipper{b156a38 G.E...... ......I. 0,0-0,0 #7f09007a app:id/anim_view_flipper_22}
+                        android.widget.TextView{dcb7a11 V.ED..C.. ......I. 0,0-0,0 #7f09005e app:id/anim_text_view_22}
+                      android.widget.ViewFlipper{8fa5776 G.E...... ......I. 0,0-0,0 #7f09007b app:id/anim_view_flipper_23}
+                        android.widget.TextView{4816177 V.ED..C.. ......I. 0,0-0,0 #7f09005f app:id/anim_text_view_23}
+                      android.widget.ViewFlipper{fd2f1e4 G.E...... ......I. 0,0-0,0 #7f09007c app:id/anim_view_flipper_24}
+                        android.widget.TextView{cdca64d V.ED..C.. ......I. 0,0-0,0 #7f090060 app:id/anim_text_view_24}
+                      android.widget.ViewFlipper{12c7502 G.E...... ......I. 0,0-0,0 #7f09007d app:id/anim_view_flipper_25}
+                        android.widget.TextView{d209e13 V.ED..C.. ......I. 0,0-0,0 #7f090061 app:id/anim_text_view_25}
+                      android.widget.ViewFlipper{cbf4850 G.E...... ......I. 0,0-0,0 #7f09007e app:id/anim_view_flipper_26}
+                        android.widget.TextView{35a5a49 V.ED..C.. ......I. 0,0-0,0 #7f090062 app:id/anim_text_view_26}
+                      android.widget.ViewFlipper{270df4e G.E...... ......I. 0,0-0,0 #7f09007f app:id/anim_view_flipper_27}
+                        android.widget.TextView{26d086f V.ED..C.. ......I. 0,0-0,0 #7f090063 app:id/anim_text_view_27}
+                      android.widget.ViewFlipper{5d8997c G.E...... ......I. 0,0-0,0 #7f090080 app:id/anim_view_flipper_28}
+                        android.widget.TextView{de55205 V.ED..C.. ......I. 0,0-0,0 #7f090064 app:id/anim_text_view_28}
+                      android.widget.TextView{e7fa25a V.ED..C.. ......I. 0,0-0,0 #7f090088 app:id/anim_widget_empty_view}
+                      android.widget.ImageView{b6bbc8b G.ED..... ......I. 0,0-0,0 #7f0903e4 app:id/widget_festive_icon}
+                      android.widget.ImageView{ed3d168 GFED..C.. ......I. 0,0-0,0 #7f0903e8 app:id/widget_voice_icon_view}
+              android.widget.ImageView{86e0981 V.ED..... ......I. 0,0-0,0}
+              android.widget.ImageView{8858a26 V.ED..... ......I. 0,0-0,0}
+              android.widget.ImageView{579667 V.ED..... ......I. 0,0-0,0}
+              android.widget.FrameLayout{fc89c14 GFE...... ......I. 0,0-0,0 #7f09028b app:id/folder_view}
+                android.widget.LinearLayout{370bcbd VFE...C.. ......I. 0,0-0,0}
+                  android.widget.LinearLayout{7b022b2 V.E...... ......I. 0,0-0,0}
+                    android.widget.EditText{83d3203 VFED..CL. ......ID 0,0-0,0 #7f09028a app:id/folder_title}
+                    android.widget.ImageView{89d6580 VFED..C.. ......I. 0,0-0,0 #7f09028c app:id/folder_view_cancel_image}
+                  android.view.View{f167b9 V.ED..... ......I. 0,0-0,0 #7f09047b app:id/title_underline}
+                  android.widget.FrameLayout{679b7fe V.E...... ......I. 0,0-0,0 #7f09028b app:id/folder_view}
+                    com.amazon.firelauncher.appsgrid.ui.FolderView{456eb5f VFED..... ......I. 0,0-0,0 #7f090288 app:id/folder_grid}
+                    com.amazon.firecard.view.widget.PageIndicator{f3359ac V.E...... ......I. 0,0-0,0 #7f090289 app:id/folder_page_indicator}
+              android.widget.Button{537c675 GFED..C.. ......I. 0,0-0,0 #7f0901c4 app:id/edit_done_button}
+          android.view.ViewStub{ab5560a G.E...... ......I. 0,0-0,0 #10201ad android:id/action_mode_bar_stub}
+    Looper (main, tid 2) {a240936}
+      Message 0: { when=+544ms what=132 target=android.app.ActivityThread$H isAsync=false }
+      Message 1: { when=+59m50s885ms callback=com.amazon.firecard.deviceagent.provider.CardProvider$5 target=android.os.Handler isAsync=false }
+      (Total messages: 2, polling=false, quitting=false)
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
@@ -53,321 +195,69 @@

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
```

### `appops/all.stdout.txt`

```diff
--- before/appops/all.stdout.txt

+++ after/appops/all.stdout.txt

@@ -10,45 +10,50 @@

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
+      #2: ModeCallback{826e2ee watchinguid=-1 flags=0x0 from uid=u0a35 pid=1822}
+      #3: ModeCallback{aeea002 watchinguid=-1 flags=0x0 from uid=u0a36 pid=1109}
+      #4: ModeCallback{f6a581e watchinguid=-1 flags=0x0 from uid=u0a36 pid=1109}
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
     Pkg amazon.speech.sim:
-      #0: ModeCallback{2c68b04 watchinguid=-1 flags=0x0 from uid=u0a35 pid=1862}
+      #0: ModeCallback{826e2ee watchinguid=-1 flags=0x0 from uid=u0a35 pid=1822}
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
+    81da869: ModeCallback{826e2ee watchinguid=-1 flags=0x0 from uid=u0a35 pid=1822}
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
+        uid=10036 pkg=com.android.systemui op=SYSTEM_ALERT_WINDOW
+        uid=10135 pkg=com.amazon.tcomm op=WAKE_LOCK
         uid=10036 pkg=com.android.systemui op=MONITOR_LOCATION
 
@@ -58,187 +63,191 @@

     Package com.amazon.platform.fdrw:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:26:28.449 (-1h26m40s4ms)
+          Access: pers  = 2026-08-03 14:26:28.449 (-1h28m4s974ms)
     Package amazon.fireos:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 09:20:46.628 (-6h32m21s825ms)
+          Access: pers  = 2026-08-03 09:20:46.628 (-6h33m46s795ms)
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2026-03-26 23:43:10.017 (-129d16h9m58s436ms)
+          Reject: pers  = 2026-03-26 23:43:10.017 (-129d16h11m23s406ms)
     Package com.amazon.device.logmanager:
       RUN_IN_BACKGROUND (allow): 
-          Access: pers  = 2026-08-03 14:35:30.788 (-1h17m37s665ms)
+          Access: pers  = 2026-08-03 15:54:27.344 (-6s79ms)
     Package com.amazon.accessorynotifier:
       RUN_IN_BACKGROUND (allow): 
-          Access: pers  = 2026-08-03 14:35:32.265 (-1h17m36s188ms)
+          Access: pers  = 2026-08-03 15:54:28.644 (-4s779ms)
     Package com.amazon.android.marketplace:
       WRITE_SETTINGS (default): 
-          Reject: pers  = 2025-12-06 20:49:21.625 (-239d19h3m46s828ms)
+          Reject: pers  = 2025-12-06 20:49:21.625 (-239d19h5m11s798ms)
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-04-06 07:13:25.558 (-119d8h39m42s895ms)
+          Access: pers  = 2026-04-06 07:13:25.558 (-119d8h41m7s865ms)
     Package com.amazon.storagemanager:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-07-10 20:57:29.503 (-23d18h55m38s950ms)
+          Access: pers  = 2026-07-10 20:57:29.503 (-23d18h57m3s920ms)
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2026-08-03 07:45:44.987 (-8h7m23s466ms)
-      READ_EXTERNAL_STORAGE (allow): 
-          Access: pers  = 2026-08-03 07:45:41.642 (-8h7m26s811ms)
+          Reject: pers  = 2026-08-03 07:45:44.987 (-8h8m48s436ms)
+      READ_EXTERNAL_STORAGE (allow): 
+          Access: pers  = 2026-08-03 07:45:41.642 (-8h8m51s781ms)
     Package android:
       COARSE_LOCATION (allow): 
       FINE_LOCATION (allow / switch COARSE_LOCATION=allow): 
-          Access: pers  = 2026-08-03 14:35:23.584 (-1h17m44s869ms)
+          Access: pers  = 2026-08-03 15:54:17.159 (-16s264ms)
       READ_CALENDAR (allow): 
-          Access: pers  = 2026-08-03 14:35:28.221 (-1h17m40s232ms)
+          Access: pers  = 2026-08-03 15:54:23.606 (-9s817ms)
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:29:54.943 (-1h23m13s510ms)
+          Access: pers  = 2026-08-03 14:29:54.943 (-1h24m38s480ms)
       AUDIO_MEDIA_VOLUME (allow): 
-          Access: pers  = 2026-08-01 21:11:23.169 (-1d18h41m45s284ms)
-      WAKE_LOCK (allow): 
-          Access: pers  = 2026-08-03 15:52:21.338 (-47s115ms)
-                  fg    = 2026-04-11 03:58:41.049 (-114d11h54m27s404ms)
-          duration=+2ms
+          Access: pers  = 2026-08-01 21:11:23.169 (-1d18h43m10s254ms)
+      WAKE_LOCK (allow): 
+          Access: pers  = 2026-08-03 15:54:32.646 (-777ms)
+                  fg    = 2026-04-11 03:58:41.049 (-114d11h55m52s374ms)
       MONITOR_LOCATION (allow / switch COARSE_LOCATION=allow): 
-          Access: pers  = 2026-08-03 14:35:23.577 (-1h17m44s876ms)
-                  fg    = 2026-04-11 03:58:41.049 (-114d11h54m27s404ms)
-          Running start at: +1h17m43s883ms
+          Access: pers  = 2026-08-03 15:54:17.151 (-16s272ms)
+                  fg    = 2026-04-11 03:58:41.049 (-114d11h55m52s374ms)
+          Running start at: +15s168ms
           startNesting=1
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2026-08-03 15:52:10.024 (-58s429ms)
+          Reject: pers  = 2026-08-03 15:54:30.511 (-2s912ms)
       TURN_ON_SCREEN (allow): 
-          Access: pers  = 2026-07-10 22:35:34.059 (-23d17h17m34s394ms)
+          Access: pers  = 2026-07-10 22:35:34.059 (-23d17h18m59s364ms)
     Package com.android.providers.settings:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2025-12-06 20:11:38.894 (-239d19h41m29s559ms)
+          Access: pers  = 2025-12-06 20:11:38.894 (-239d19h42m54s529ms)
     Package com.android.keychain:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2025-12-07 15:30:49.435 (-239d0h22m19s18ms)
+          Access: pers  = 2025-12-07 15:30:49.435 (-239d0h23m43s988ms)
     Package com.amazon.device.sale.service:
       RUN_IN_BACKGROUND (allow): 
-          Access: pers  = 2026-08-03 14:35:42.055 (-1h17m26s398ms)
+          Access: pers  = 2026-08-03 15:54:30.713 (-2s710ms)
     Package com.android.settings:
       WRITE_SETTINGS (default): 
-          Reject: pers  = 2026-08-01 21:54:35.634 (-1d17h58m32s819ms)
+          Reject: pers  = 2026-08-01 21:54:35.634 (-1d17h59m57s789ms)
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2026-08-03 12:07:40.636 (-3h45m27s817ms)
+          Reject: pers  = 2026-08-03 12:07:40.636 (-3h46m52s787ms)
       TOAST_WINDOW (allow): 
-          Access: pers  = 2025-12-07 16:06:55.266 (-238d23h46m13s187ms)
+          Access: pers  = 2025-12-07 16:06:55.266 (-238d23h47m38s157ms)
           duration=+4s550ms
     Package android.amazon.perm:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2025-12-06 19:11:18.089 (-239d20h41m50s364ms)
+          Access: pers  = 2025-12-06 19:11:18.089 (-239d20h43m15s334ms)
     Package com.android.wallpaperbackup:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:32:08.417 (-1h21m0s36ms)
+          Access: pers  = 2026-08-03 14:32:08.417 (-1h22m25s6ms)
     Package com.android.location.fused:
       COARSE_LOCATION (allow): 
       FINE_LOCATION (allow / switch COARSE_LOCATION=allow): 
-          Access: pers  = 2025-12-06 18:57:45.955 (-239d20h55m22s498ms)
+          Access: pers  = 2025-12-06 18:57:45.955 (-239d20h56m47s468ms)
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:35:13.887 (-1h17m54s566ms)
+          Access: pers  = 2026-08-03 14:35:13.887 (-1h19m19s536ms)
       MONITOR_LOCATION (allow / switch COARSE_LOCATION=allow): 
-          Access: pers  = 2025-12-06 19:03:04.992 (-239d20h50m3s461ms)
+          Access: pers  = 2025-12-06 19:03:04.992 (-239d20h51m28s431ms)
           duration=+5m20s391ms
+    Package com.here.odnp.service:
+      RECORD_AUDIO (allow): 
+          Access: pers  = 2026-08-03 15:54:11.972 (-21s451ms)
     Package com.amazon.settings:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 07:45:33.063 (-8h7m35s390ms)
+          Access: pers  = 2026-08-03 07:45:33.063 (-8h9m0s360ms)
       TOAST_WINDOW (allow): 
-          Access: pers  = 2026-07-10 21:04:18.363 (-23d18h48m50s90ms)
+          Access: pers  = 2026-07-10 21:04:18.363 (-23d18h50m15s60ms)
           duration=+5s388ms
     Package com.amazon.shpm:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 09:19:52.283 (-6h33m16s170ms)
+          Access: pers  = 2026-08-03 09:19:52.283 (-6h34m41s140ms)
     Package com.amazon.fireos.cirruscloud:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:33:40.524 (-1h19m27s929ms)
+          Access: pers  = 2026-08-03 14:33:40.524 (-1h20m52s899ms)
   Uid 1002:
     state=cch  
     Package com.android.bluetooth:
       WAKE_LOCK (allow): 
-          Access: pers  = 2025-12-06 18:56:41.294 (-239d20h56m27s159ms)
-                  bg    = 2025-12-06 18:56:41.291 (-239d20h56m27s162ms)
+          Access: pers  = 2025-12-06 18:56:41.294 (-239d20h57m52s129ms)
+                  bg    = 2025-12-06 18:56:41.291 (-239d20h57m52s132ms)
           duration=+10ms
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2025-12-06 18:56:24.496 (-239d20h56m43s957ms)
-      READ_EXTERNAL_STORAGE (allow): 
-          Access: pers  = 2025-12-06 18:56:28.924 (-239d20h56m39s529ms)
-                  cch   = 2025-12-06 18:56:23.700 (-239d20h56m44s753ms)
-      WRITE_EXTERNAL_STORAGE (allow): 
-          Access: pers  = 2025-12-06 18:56:28.924 (-239d20h56m39s529ms)
-                  cch   = 2025-12-06 18:56:23.700 (-239d20h56m44s753ms)
+          Reject: pers  = 2025-12-06 18:56:24.496 (-239d20h58m8s927ms)
+      READ_EXTERNAL_STORAGE (allow): 
+          Access: pers  = 2025-12-06 18:56:28.924 (-239d20h58m4s499ms)
+                  cch   = 2025-12-06 18:56:23.700 (-239d20h58m9s723ms)
+      WRITE_EXTERNAL_STORAGE (allow): 
+          Access: pers  = 2025-12-06 18:56:28.924 (-239d20h58m4s499ms)
+                  cch   = 2025-12-06 18:56:23.700 (-239d20h58m9s723ms)
   Uid 1041:
     state=cch  
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
+TAKE_AUDIO_FOCUS: allow; time=+239d20h42m58s37ms ago
+READ_EXTERNAL_STORAGE: allow; time=+9s500ms ago
+WRITE_EXTERNAL_STORAGE: allow; time=+9s500ms ago
+REQUEST_DELETE_PACKAGES: allow; time=+238d23h49m59s762ms ago
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
+FINE_LOCATION: allow; time=+2h9m55s798ms ago
+READ_EXTERNAL_STORAGE: allow; time=+1h18m53s827ms ago
+WRITE_EXTERNAL_STORAGE: allow; time=+1h18m53s827ms ago
+BIND_ACCESSIBILITY_SERVICE: allow; time=+3s74ms ago
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
+test_id=PHASE3C-PREFERRED-P0-02-after_rollback
 serial=G001LT0511550CFT
-timestamp_utc=2026-08-03T07:53:04Z
+timestamp_utc=2026-08-03T07:54:30Z
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
@@ -146,5 +145,5 @@

 [persist.sys.locale]: [ja-JP]
 [persist.sys.metrics.last_app]: [com.google.android.youtube]
-[persist.sys.saved_time]: [1785738927772]
+[persist.sys.saved_time]: [1785743663226]
 [persist.sys.strictmode.visual]: []
 [persist.sys.timezone]: [Asia/Taipei]
@@ -382,5 +381,5 @@

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

@@ -25,5 +25,5 @@

 app_standby_enabled=1
 assisted_gps_enabled=1
-atz_response_provider={"timeStampInMillis":1785738932139,"isSuccess":true,"updatedTimeZone":"Asia\/Taipei","countryCode":"TW","dcasUpdatedTime":1785738932129}
+atz_response_provider={"timeStampInMillis":1785743669153,"isSuccess":true,"updatedTimeZone":"Asia\/Taipei","countryCode":"TW","dcasUpdatedTime":1785743669150}
 audio_safe_volume_state=3
 auto_time=1
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
+- Test ID: PHASE3C-PREFERRED-P0-02-after_rollback
 - Serial: G001LT0511550CFT
-- Timestamp UTC: 2026-08-03T07:53:08Z
+- Timestamp UTC: 2026-08-03T07:54:33Z
 - This snapshot executed read-only ADB commands only.
 - Individual command failures are preserved in *.exit_code.txt and are not silently treated as absence.
```

### `users/dumpsys_user.stdout.txt`

```diff
--- before/users/dumpsys_user.stdout.txt

+++ after/users/dumpsys_user.stdout.txt

@@ -3,11 +3,11 @@

     State: RUNNING_UNLOCKED
     Created: <unknown>
-    Last logged in: +1h17m43s91ms ago
+    Last logged in: +14s666ms ago
     Last logged in fingerprint: Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys
-    Start time: +1h17m46s725ms ago
-    Unlock time: +1h17m42s191ms ago
+    Start time: +18s842ms ago
+    Unlock time: +13s663ms ago
     Has profile owner: true
     Restrictions:
-      none
+      no_set_wallpaper
     Device policy global restrictions:
       null
@@ -15,5 +15,5 @@

       null
     Effective restrictions:
-      none
+      no_set_wallpaper
     Ignore errors preparing storage: true
 
```

### `window/input.stdout.txt`

```diff
--- before/window/input.stdout.txt

+++ after/window/input.stdout.txt

@@ -3,5 +3,5 @@

 Input Manager State:
   Interactive: true
-  System UI Visibility: 0x960a
+  System UI Visibility: 0x920a
   Pointer Speed: 0
   Pointer Gestures Enabled: true
@@ -25,5 +25,31 @@

       ConfigurationFile: 
       HaveKeyboardLayoutOverlay: false
-    1: mtk-kpd
+    1: fts_ts
+      Classes: 0x00000015
+      Path: /dev/input/event3
+      Enabled: true
+      Descriptor: a1cc21cba608c55d28d6dd2b1939004df0e0c756:00000000
+      Location: 
+      ControllerNumber: 0
+      UniqueId: 
+      Identifier: bus=0x0018, vendor=0x0000, product=0x0000, version=0x0000
+      KeyLayoutFile: /system/usr/keylayout/Generic.kl
+      KeyCharacterMapFile: /system/usr/keychars/Generic.kcm
+      ConfigurationFile: 
+      HaveKeyboardLayoutOverlay: false
+    2: mtk-tpd
+      Classes: 0x00000014
+      Path: /dev/input/event4
+      Enabled: true
+      Descriptor: 84931e976ab60191371c1c95baf408538ca4c4c5:00000000
+      Location: 
+      ControllerNumber: 0
+      UniqueId: 
+      Identifier: bus=0x0000, vendor=0x0000, product=0x0000, version=0x0000
+      KeyLayoutFile: 
+      KeyCharacterMapFile: 
+      ConfigurationFile: 
+      HaveKeyboardLayoutOverlay: false
+    3: mtk-kpd
       Classes: 0x00000001
       Path: /dev/input/event1
@@ -38,22 +64,9 @@

       ConfigurationFile: 
       HaveKeyboardLayoutOverlay: false
-    2: ACCDET
-      Classes: 0x00000081
-      Path: /dev/input/event0
-      Enabled: true
-      Descriptor: 1c78f7e0d16d4dbc8d3ab93943523f379203f90b:00000000
-      Location: 
-      ControllerNumber: 0
-      UniqueId: 
-      Identifier: bus=0x0019, vendor=0x0000, product=0x0000, version=0x0000
-      KeyLayoutFile: /system/usr/keylayout/ACCDET.kl
-      KeyCharacterMapFile: /system/usr/keychars/Generic.kcm
-      ConfigurationFile: 
-      HaveKeyboardLayoutOverlay: false
-    3: mtk-tpd
-      Classes: 0x00000014
-      Path: /dev/input/event4
-      Enabled: true
-      Descriptor: 84931e976ab60191371c1c95baf408538ca4c4c5:00000000
+    4: hall-sensor
+      Classes: 0x00000080
+      Path: /dev/input/event2
+      Enabled: true
+      Descriptor: f5e065ca35c951f762d11b4bd22005ed59a004a2:00000000
       Location: 
       ControllerNumber: 0
@@ -64,27 +77,14 @@

       ConfigurationFile: 
       HaveKeyboardLayoutOverlay: false
-    4: hall-sensor
-      Classes: 0x00000080
-      Path: /dev/input/event2
-      Enabled: true
-      Descriptor: f5e065ca35c951f762d11b4bd22005ed59a004a2:00000000
+    5: ACCDET
+      Classes: 0x00000081
+      Path: /dev/input/event0
+      Enabled: true
+      Descriptor: 1c78f7e0d16d4dbc8d3ab93943523f379203f90b:00000000
       Location: 
       ControllerNumber: 0
       UniqueId: 
-      Identifier: bus=0x0000, vendor=0x0000, product=0x0000, version=0x0000
-      KeyLayoutFile: 
-      KeyCharacterMapFile: 
-      ConfigurationFile: 
-      HaveKeyboardLayoutOverlay: false
-    5: fts_ts
-      Classes: 0x00000015
-      Path: /dev/input/event3
-      Enabled: true
-      Descriptor: a1cc21cba608c55d28d6dd2b1939004df0e0c756:00000000
-      Location: 
-      ControllerNumber: 0
-      UniqueId: 
-      Identifier: bus=0x0018, vendor=0x0000, product=0x0000, version=0x0000
-      KeyLayoutFile: /system/usr/keylayout/Generic.kl
+      Identifier: bus=0x0019, vendor=0x0000, product=0x0000, version=0x0000
+      KeyLayoutFile: /system/usr/keylayout/ACCDET.kl
       KeyCharacterMapFile: /system/usr/keychars/Generic.kcm
       ConfigurationFile: 
@@ -121,10 +121,19 @@

       MetaState: 0x0
       DownTime: 0
-  Device 1: mtk-kpd
-    Generation: 12
-    IsExternal: false
-    HasMic:     false
-    Sources: 0x00000101
+  Device 1: fts_ts
+    Generation: 14
+    IsExternal: false
+    HasMic:     false
+    Sources: 0x00001103
     KeyboardType: 1
+    Motion Ranges:
+      X: source=0x00001002, min=0.000, max=1199.000, flat=0.000, fuzz=0.000, resolution=0.000
+      Y: source=0x00001002, min=0.000, max=1919.000, flat=0.000, fuzz=0.000, resolution=0.000
+      PRESSURE: source=0x00001002, min=0.000, max=1.000, flat=0.000, fuzz=0.000, resolution=0.000
+      SIZE: source=0x00001002, min=0.000, max=1.000, flat=0.000, fuzz=0.000, resolution=0.000
+      TOUCH_MAJOR: source=0x00001002, min=0.000, max=2264.156, flat=0.000, fuzz=0.000, resolution=0.000
+      TOUCH_MINOR: source=0x00001002, min=0.000, max=2264.156, flat=0.000, fuzz=0.000, resolution=0.000
+      TOOL_MAJOR: source=0x00001002, min=0.000, max=2264.156, flat=0.000, fuzz=0.000, resolution=0.000
+      TOOL_MINOR: source=0x00001002, min=0.000, max=2264.156, flat=0.000, fuzz=0.000, resolution=0.000
     Keyboard Input Mapper:
       Parameters:
@@ -137,24 +146,75 @@

       MetaState: 0x0
       DownTime: 0
-  Device 2: ACCDET
-    Generation: 10
-    IsExternal: false
-    HasMic:     false
-    Sources: 0x80000101
-    KeyboardType: 1
-    Switch Input Mapper:
-      SwitchValues: 0
-    Keyboard Input Mapper:
-      Parameters:
-        HasAssociatedDisplay: false
-        OrientationAware: false
-        HandlesKeyRepeat: false
-      KeyboardType: 1
-      Orientation: 0
-      KeyDowns: 0 keys currently down
-      MetaState: 0x0
-      DownTime: 0
-  Device 3: mtk-tpd
-    Generation: 14
+    Touch Input Mapper (mode - direct):
+      Parameters:
+        GestureMode: multi-touch
+        DeviceType: touchScreen
+        AssociatedDisplay: hasAssociatedDisplay=true, isExternal=false, displayId=''
+        OrientationAware: true
+      Raw Touch Axes:
+        X: min=0, max=1200, flat=0, fuzz=0, resolution=0
+        Y: min=0, max=1920, flat=0, fuzz=0, resolution=0
+        Pressure: min=0, max=255, flat=0, fuzz=0, resolution=0
+        TouchMajor: min=0, max=255, flat=0, fuzz=0, resolution=0
+        TouchMinor: unknown range
+        ToolMajor: unknown range
+        ToolMinor: unknown range
+        Orientation: unknown range
+        Distance: unknown range
+        TiltX: unknown range
+        TiltY: unknown range
+        TrackingId: min=0, max=65535, flat=0, fuzz=0, resolution=0
+        Slot: min=0, max=9, flat=0, fuzz=0, resolution=0
+      Calibration:
+        touch.size.calibration: geometric
+        touch.pressure.calibration: physical
+        touch.orientation.calibration: none
+        touch.distance.calibration: none
+        touch.coverage.calibration: none
+      Affine Transformation:
+        X scale: 1.000
+        X ymix: 0.000
+        X offset: 0.000
+        Y xmix: 0.000
+        Y scale: 1.000
+        Y offset: 0.000
+      Viewport: displayId=0, orientation=0, logicalFrame=[0, 0, 1200, 1920], physicalFrame=[0, 0, 1200, 1920], deviceSize=[1200, 1920]
+      SurfaceWidth: 1200px
+      SurfaceHeight: 1920px
+      SurfaceLeft: 0
+      SurfaceTop: 0
+      SurfaceOrientation: 0
+      Translation and Scaling Factors:
+        XTranslate: 0.000
+        YTranslate: 0.000
+        XScale: 0.999
+        YScale: 0.999
+        XPrecision: 1.001
+        YPrecision: 1.001
+        GeometricScale: 0.999
+        PressureScale: 0.004
+        SizeScale: 0.004
+        OrientationScale: 0.000
+        DistanceScale: 0.000
+        HaveTilt: false
+        TiltXCenter: 0.000
+        TiltXScale: 0.000
+        TiltYCenter: 0.000
+        TiltYScale: 0.000
+      Last Raw Button State: 0x00000000
+      Last Raw Touch: pointerCount=0
+      Last Cooked Button State: 0x00000000
+      Last Cooked Touch: pointerCount=0
+      Stylus Fusion:
+        ExternalStylusConnected: false
+        External Stylus ID: -1
+        External Stylus Data Timeout: 9223372036854775807
+      External Stylus State:
+        When: 9223372036854775807
+        Pressure: 0.000000
+        Button State: 0x00000000
+        Tool Type: 0
+  Device 2: mtk-tpd
+    Generation: 15
     IsExternal: false
     HasMic:     false
@@ -239,27 +299,10 @@

         Button State: 0x00000000
         Tool Type: 0
-  Device 4: hall-sensor
-    Generation: 6
-    IsExternal: false
-    HasMic:     false
-    Sources: 0x80000000
-    KeyboardType: 0
-    Switch Input Mapper:
-      SwitchValues: 0
-  Device 5: fts_ts
-    Generation: 15
-    IsExternal: false
```

### `window/processes.stdout.txt`

```diff
--- before/window/processes.stdout.txt

+++ after/window/processes.stdout.txt

@@ -3,5 +3,7 @@

 root             2     0 [kthreadd]                  [kthreadd]
 root             3     2 [ksoftirqd/0]               [ksoftirqd/0]
+root             4     2 [kworker/0:0]               [kworker/0:0]
 root             5     2 [kworker/0:0H]              [kworker/0:0H]
+root             6     2 [kworker/u16:0]             [kworker/u16:0]
 root             7     2 [rcu_preempt]               [rcu_preempt]
 root             8     2 [rcu_sched]                 [rcu_sched]
@@ -10,4 +12,5 @@

 root            11     2 [migration/1]               [migration/1]
 root            12     2 [ksoftirqd/1]               [ksoftirqd/1]
+root            13     2 [kworker/1:0]               [kworker/1:0]
 root            14     2 [kworker/1:0H]              [kworker/1:0H]
 root            15     2 [migration/2]               [migration/2]
@@ -17,16 +20,21 @@

 root            19     2 [migration/3]               [migration/3]
 root            20     2 [ksoftirqd/3]               [ksoftirqd/3]
+root            21     2 [kworker/3:0]               [kworker/3:0]
 root            22     2 [kworker/3:0H]              [kworker/3:0H]
 root            23     2 [migration/4]               [migration/4]
 root            24     2 [ksoftirqd/4]               [ksoftirqd/4]
+root            25     2 [kworker/4:0]               [kworker/4:0]
 root            26     2 [kworker/4:0H]              [kworker/4:0H]
 root            27     2 [migration/5]               [migration/5]
 root            28     2 [ksoftirqd/5]               [ksoftirqd/5]
+root            29     2 [kworker/5:0]               [kworker/5:0]
 root            30     2 [kworker/5:0H]              [kworker/5:0H]
 root            31     2 [migration/6]               [migration/6]
 root            32     2 [ksoftirqd/6]               [ksoftirqd/6]
+root            33     2 [kworker/6:0]               [kworker/6:0]
 root            34     2 [kworker/6:0H]              [kworker/6:0H]
 root            35     2 [migration/7]               [migration/7]
 root            36     2 [ksoftirqd/7]               [ksoftirqd/7]
+root            37     2 [kworker/7:0]               [kworker/7:0]
 root            38     2 [kworker/7:0H]              [kworker/7:0H]
 root            39     2 [perf]                      [perf]
@@ -61,5 +69,7 @@

 root            69     2 [kworker/4:1]               [kworker/4:1]
 root            70     2 [cfg80211]                  [cfg80211]
-root            73     2 [kworker/2:1]               [kworker/2:1]
+root            71     2 [kworker/u16:1]             [kworker/u16:1]
+root            72     2 [kworker/u16:2]             [kworker/u16:2]
+root            73     2 [kworker/1:1]               [kworker/1:1]
 root            74     2 [pmic_thread]               [pmic_thread]
 root            75     2 [lbat_service]              [lbat_service]
@@ -76,5 +86,5 @@

 root            98     2 [fsnotify_mark]             [fsnotify_mark]
 root            99     2 [fuse_log]                  [fuse_log]
-root           130     2 [kworker/6:1]               [kworker/6:1]
+root           130     2 [kworker/5:1]               [kworker/5:1]
 root           131     2 [bioset]                    [bioset]
 root           132     2 [bioset]                    [bioset]
@@ -107,6 +117,8 @@

 root           160     2 [ged_kpi]                   [ged_kpi]
 root           161     2 [gpu_bucks]                 [gpu_bucks]
+root           162     2 [kworker/u17:0]             [kworker/u17:0]
 root           163     2 [kbase_job_fault]           [kbase_job_fault]
 root           164     2 [mali_aeewp]                [mali_aeewp]
+root           165     2 [kworker/u17:1]             [kworker/u17:1]
 root           166     2 [WMFE-CMDQ-WQ]              [WMFE-CMDQ-WQ]
 root           167     2 [RSC-CMDQ-WQ]               [RSC-CMDQ-WQ]
@@ -138,250 +150,268 @@

 root           193     2 [irq/24-hall_sen]           [irq/24-hall_sen]
 root           194     2 [irq/29-mt6370_p]           [irq/29-mt6370_p]
-root           196     2 [tcpc_timer_type]           [tcpc_timer_type]
-root           197     2 [type_c_port0]              [type_c_port0]
-root           198     2 [gauge_coulomb_t]           [gauge_coulomb_t]
-root           199     2 [battery_thread]            [battery_thread]
-root           200     2 [power_misc_thre]           [power_misc_thre]
-root           201     2 [gauge_timer_thr]           [gauge_timer_thr]
-root           202     2 [dm_bufio_cache]            [dm_bufio_cache]
-root           203     2 [binder]                    [binder]
-root           210     2 [ipv6_addrconf]             [ipv6_addrconf]
-root           219     2 [deferwq]                   [deferwq]
-root           220     2 [ipi_cpu_dvfs_rt]           [ipi_cpu_dvfs_rt]
-root           221     2 [EEM_CTRL_2L]               [EEM_CTRL_2L]
-root           222     2 [EEM_CTRL_L]                [EEM_CTRL_L]
-root           223     2 [EEM_CTRL_CCI]              [EEM_CTRL_CCI]
-root           224     2 [EEM_CTRL_GPU]              [EEM_CTRL_GPU]
-root           225     2 [Init_1_Stress]             [Init_1_Stress]
-root           226     2 [hps_main]                  [hps_main]
-root           227     2 [qos_recv]                  [qos_recv]
-root           228     2 [kworker/5:2]               [kworker/5:2]
-root           229     2 [exe_cq]                    [exe_cq]
-root           230     2 [bioset]                    [bioset]
-root           231     2 [mmcqd/0]                   [mmcqd/0]
-root           232     2 [bioset]                    [bioset]
-root           233     2 [mmcqd/0boot0]              [mmcqd/0boot0]
-root           234     2 [bioset]                    [bioset]
-root           235     2 [mmcqd/0boot1]              [mmcqd/0boot1]
-root           236     2 [bioset]                    [bioset]
-root           237     2 [mmcqd/0rpmb]               [mmcqd/0rpmb]
-root           238     2 [ksched_hint]               [ksched_hint]
-root           239     2 [accel_polling]             [accel_polling]
-root           241     2 [entropy_thread]            [entropy_thread]
-root           242     2 [mt_touch_boost_]           [mt_touch_boost_]
-root           243     2 [dynamic_boost]             [dynamic_boost]
-root           244     2 [mtk-tpd]                   [mtk-tpd]
-root           245     2 [fts_wq]                    [fts_wq]
-root           246     2 [mtk-tpd]                   [mtk-tpd]
-root           247     2 [touch_resume]              [touch_resume]
-root           248     2 [charger_thread]            [charger_thread]
-root           249     2 [rise_rate_vs5]             [rise_rate_vs5]
-root           250     2 [rise_rate_vs6]             [rise_rate_vs6]
-root           251     2 [rise_rate_vs7]             [rise_rate_vs7]
-root           252     2 [rise_rate_vs8]             [rise_rate_vs8]
-root           253     2 [bioset]                    [bioset]
-root           255     2 [kdmflush]                  [kdmflush]
-root           256     2 [kworker/3:1H]              [kworker/3:1H]
-root           257     2 [kworker/0:1H]              [kworker/0:1H]
+root           195     2 [tcpc_timer_type]           [tcpc_timer_type]
+root           196     2 [type_c_port0]              [type_c_port0]
+root           197     2 [gauge_coulomb_t]           [gauge_coulomb_t]
+root           198     2 [battery_thread]            [battery_thread]
+root           199     2 [power_misc_thre]           [power_misc_thre]
+root           200     2 [gauge_timer_thr]           [gauge_timer_thr]
+root           201     2 [dm_bufio_cache]            [dm_bufio_cache]
+root           202     2 [binder]                    [binder]
+root           204     2 [kworker/4:2]               [kworker/4:2]
+root           206     2 [kworker/u16:3]             [kworker/u16:3]
+root           207     2 [kworker/u16:4]             [kworker/u16:4]
+root           208     2 [ipv6_addrconf]             [ipv6_addrconf]
+root           209     2 [kworker/0:1]               [kworker/0:1]
+root           218     2 [deferwq]                   [deferwq]
+root           219     2 [ipi_cpu_dvfs_rt]           [ipi_cpu_dvfs_rt]
+root           220     2 [EEM_CTRL_2L]               [EEM_CTRL_2L]
+root           221     2 [EEM_CTRL_L]                [EEM_CTRL_L]
+root           222     2 [EEM_CTRL_CCI]              [EEM_CTRL_CCI]
+root           223     2 [EEM_CTRL_GPU]              [EEM_CTRL_GPU]
+root           224     2 [Init_1_Stress]             [Init_1_Stress]
+root           225     2 [hps_main]                  [hps_main]
+root           226     2 [qos_recv]                  [qos_recv]
+root           227     2 [exe_cq]                    [exe_cq]
+root           228     2 [bioset]                    [bioset]
+root           229     2 [kworker/0:2]               [kworker/0:2]
+root           230     2 [mmcqd/0]                   [mmcqd/0]
+root           231     2 [bioset]                    [bioset]
+root           232     2 [mmcqd/0boot0]              [mmcqd/0boot0]
+root           233     2 [bioset]                    [bioset]
+root           234     2 [mmcqd/0boot1]              [mmcqd/0boot1]
+root           235     2 [bioset]                    [bioset]
+root           236     2 [mmcqd/0rpmb]               [mmcqd/0rpmb]
+root           237     2 [ksched_hint]               [ksched_hint]
+root           238     2 [accel_polling]             [accel_polling]
+root           240     2 [entropy_thread]            [entropy_thread]
+root           241     2 [mt_touch_boost_]           [mt_touch_boost_]
+root           242     2 [dynamic_boost]             [dynamic_boost]
+root           243     2 [mtk-tpd]                   [mtk-tpd]
+root           244     2 [fts_wq]                    [fts_wq]
+root           245     2 [mtk-tpd]                   [mtk-tpd]
+root           246     2 [touch_resume]              [touch_resume]
+root           247     2 [charger_thread]            [charger_thread]
+root           248     2 [rise_rate_vs5]             [rise_rate_vs5]
+root           249     2 [rise_rate_vs6]             [rise_rate_vs6]
+root           250     2 [rise_rate_vs7]             [rise_rate_vs7]
+root           251     2 [rise_rate_vs8]             [rise_rate_vs8]
+root           252     2 [bioset]                    [bioset]
+root           254     2 [kdmflush]                  [kdmflush]
+root           255     2 [kworker/0:1H]              [kworker/0:1H]
+root           256     2 [bioset]                    [bioset]
+root           257     2 [kverityd]                  [kverityd]
 root           258     2 [bioset]                    [bioset]
-root           259     2 [kverityd]                  [kverityd]
-root           261     2 [bioset]                    [bioset]
-root           262     2 [bioset]                    [bioset]
-root           263     2 [bioset]                    [bioset]
-root           264     2 [ext4-rsv-conver]           [ext4-rsv-conver]
-root           266     2 [kworker/2:1H]              [kworker/2:1H]
-root           267     2 [kworker/7:1]               [kworker/7:1]
-root           268     2 [kworker/1:1H]              [kworker/1:1H]
-root           271     2 [kdmflush]                  [kdmflush]
+root           259     2 [bioset]                    [bioset]
+root           260     2 [bioset]                    [bioset]
+root           261     2 [kworker/6:1]               [kworker/6:1]
+root           262     2 [ext4-rsv-conver]           [ext4-rsv-conver]
+root           263     2 [kworker/u16:5]             [kworker/u16:5]
+root           264     2 [kworker/1:1H]              [kworker/1:1H]
+root           267     2 [kdmflush]                  [kdmflush]
+root           268     2 [bioset]                    [bioset]
+root           269     2 [kverityd]                  [kverityd]
+root           270     2 [bioset]                    [bioset]
+root           271     2 [bioset]                    [bioset]
 root           272     2 [bioset]                    [bioset]
-root           273     2 [kverityd]                  [kverityd]
-root           274     2 [bioset]                    [bioset]
-root           275     2 [bioset]                    [bioset]
-root           276     2 [bioset]                    [bioset]
-root           277     2 [ext4-rsv-conver]           [ext4-rsv-conver]
-root           279     1 init                        init subcontext u:r:vendor_init:s0 9
-root           280     1 init                        init subcontext u:r:vendor_init:s0 10
-root           281     1 ueventd                     ueventd
-root           297     2 [jbd2/mmcblk0p21]           [jbd2/mmcblk0p21]
-root           298     2 [ext4-rsv-conver]           [ext4-rsv-conver]
-root           302     2 [jbd2/mmcblk0p18]           [jbd2/mmcblk0p18]
-root           303     2 [ext4-rsv-conver]           [ext4-rsv-conver]
-root           307     2 [jbd2/mmcblk0p10]           [jbd2/mmcblk0p10]
-root           308     2 [ext4-rsv-conver]           [ext4-rsv-conver]
-logd           309     1 logd                        logd
-system         310     1 servicemanager              servicemanager
-system         311     1 hwservicemanager            hwservicemanager
-system         312     1 vndservicemanager           vndservicemanager /dev/vndbinder
-root           313     2 [f_mtp]                     [f_mtp]
-system         314     1 android.hardware.keymaster@3.0-service android.hardware.keymaster@3.0-service
-root           315     1 vold                        vold --blkid_context=u:r:blkid:s0 --blkid_untrusted_context=u:r:blkid_untrusted:s0 --fsck_context=u:r:fsck:s0 --fsck_untrusted_context=u:r:fsck_untrusted:s0
-root           321     2 [kauditd]                   [kauditd]
-root           337     2 [jbd2/mmcblk0p3-]           [jbd2/mmcblk0p3-]
-root           338     2 [ext4-rsv-conver]           [ext4-rsv-conver]
-root           340     1 kisd                        kisd
-root           347     1 netd                        netd
-root           348     1 zygote64                    zygote64
-root           349     1 zygote                      zygote
-system         352     1 android.hidl.allocator@1.0-service android.hidl.allocator@1.0-service
-bluetooth      353     1 android.hardware.bluetooth@1.0-service-mediatek android.hardware.bluetooth@1.0-service-mediatek
-media          354     1 android.hardware.cas@1.0-service android.hardware.cas@1.0-service
-system         356     1 android.hardware.configstore@1.1-service android.hardware.configstore@1.1-service
-media          357     1 android.hardware.drm@1.0-service android.hardware.drm@1.0-service
-media          359     1 android.hardware.drm@1.1-service.clearkey android.hardware.drm@1.1-service.clearkey
-media          360     1 android.hardware.drm@1.1-service.widevine android.hardware.drm@1.1-service.widevine
-system         361     1 android.hardware.gatekeeper@1.0-service android.hardware.gatekeeper@1.0-service
-system         362     1 android.hardware.graphics.allocator@2.0-service android.hardware.graphics.allocator@2.0-service
-system         364     1 android.hardware.graphics.composer@2.1-service android.hardware.graphics.composer@2.1-service
-system         365     1 android.hardware.health@2.0-service android.hardware.health@2.0-service
-system         366     1 android.hardware.light@2.0-service-mediatek android.hardware.light@2.0-service-mediatek
-system         367     1 android.hardware.memtrack@1.0-service android.hardware.memtrack@1.0-service
-system         368     1 android.hardware.thermal@1.0-service android.hardware.thermal@1.0-service
-system         369     1 android.hardware.usb@1.1-service-mediatek android.hardware.usb@1.1-service-mediatek
-wifi           370     1 android.hardware.wifi@1.0-service-mediatek android.hardware.wifi@1.0-service-mediatek
-system         371     1 fireos.hardware.amazonhmod@1.0-service fireos.hardware.amazonhmod@1.0-service
-system         372     1 fireos.hardware.amazonthermal@1.0-service fireos.hardware.amazonthermal@1.0-service
-audioserver    373     1 fireos.hardware.audio@2.0-service fireos.hardware.audio@2.0-service
-root           374   347 iptables-restore            iptables-restore --noflush -w -v
-root           375   347 ip6tables-restore           ip6tables-restore --noflush -w -v
-system         377     1 fireos.hardware.connectivity.networkpower@1.0-service fireos.hardware.connectivity.networkpower@1.0-service
-keystore       379     1 fireos.hardware.fireosdha@2.0-service fireos.hardware.fireosdha@2.0-service
-system         380     1 fireos.hardware.idme@1.1-service fireos.hardware.idme@1.1-service
+root           273     2 [ext4-rsv-conver]           [ext4-rsv-conver]
+root           274     2 [kworker/u16:6]             [kworker/u16:6]
+root           275     2 [kworker/u16:7]             [kworker/u16:7]
```

### `window/windows.stdout.txt`

```diff
--- before/window/windows.stdout.txt

+++ after/window/windows.stdout.txt

@@ -1,12 +1,12 @@

 WINDOW MANAGER WINDOWS (dumpsys window windows)
-  Window #0 Window{29cade u0 SpeechUi}:
-    mDisplayId=0 stackId=0 mSession=Session{68ee594 1862:u0a10035} mClient=android.os.BinderProxy@d36afe1
+  Window #0 Window{e918457 u0 SpeechUi-Locked}:
+    mDisplayId=0 stackId=0 mSession=Session{f4a8b75 1822:u0a10035} mClient=android.os.BinderProxy@4569f1
     mOwnerUid=10035 mShowToOwnerOnly=false package=amazon.speech.sim appop=NONE
     mAttrs={(0,0)(fillxfill) sim={adjust=pan} ty=SECURE_SYSTEM_OVERLAY fmt=TRANSLUCENT
-      fl=NOT_FOCUSABLE NOT_TOUCHABLE LAYOUT_IN_SCREEN HARDWARE_ACCELERATED
+      fl=NOT_FOCUSABLE NOT_TOUCHABLE LAYOUT_IN_SCREEN FULLSCREEN
       pfl=SHOW_FOR_ALL_USERS}
-    Requested w=1200 h=1920 mLayoutSeq=138
+    Requested w=1200 h=1920 mLayoutSeq=48
     mBaseLayer=311000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
-    mToken=WindowToken{2e5a106 android.os.BinderProxy@d36afe1}
+    mToken=WindowToken{53bb9d6 android.os.BinderProxy@4569f1}
     mViewVisibility=0x0 mHaveFrame=true mObscured=false
     mSeq=0 mSystemUiVisibility=0x0
@@ -23,6 +23,6 @@

     Cur insets: overscan=[0,0][0,0] content=[0,0][0,0] visible=[0,36][0,0] stable=[0,36][0,72] surface=[0,0][0,0] outsets=[0,0][0,0] cutout=DisplayCutout{insets=Rect(0, 0 - 0, 0) boundingRect=Rect(0, 0 - 0, 0)}
     Lst insets: overscan=[0,0][0,0] content=[0,0][0,0] visible=[0,36][0,0] stable=[0,36][0,72] physical=[0,0][0,0] outset=[0,0][0,0] cutout=com.android.server.wm.utils.WmDisplayCutout@3c1
-    WindowStateAnimator{d64d121 SpeechUi}:
-      mSurface=Surface(name=SpeechUi-Locked)/@0x8df3bf3
+    WindowStateAnimator{35f1395 SpeechUi-Locked}:
+      mSurface=Surface(name=SpeechUi-Locked)/@0x1b0ecaa
       Surface: shown=true layer=0 alpha=1.0 rect=(0.0,0.0) 1200 x 1920 transform=(1.0, 0.0, 1.0, 0.0)
       mDrawState=HAS_DRAWN       mLastHidden=false
@@ -30,13 +30,13 @@

     isOnScreen=true
     isVisible=true
-  Window #1 Window{8e2d242 u0 NavigationBar}:
-    mDisplayId=0 stackId=0 mSession=Session{d1d50da 1151:u0a10036} mClient=android.os.BinderProxy@e59d1b7
+  Window #1 Window{9569ab5 u0 NavigationBar}:
+    mDisplayId=0 stackId=0 mSession=Session{7b3ccfb 1109:u0a10036} mClient=android.os.BinderProxy@40a233e
     mOwnerUid=10036 mShowToOwnerOnly=false package=com.android.systemui appop=NONE
     mAttrs={(0,0)(fillxfill) sim={adjust=pan} ty=NAVIGATION_BAR fmt=TRANSLUCENT
       fl=NOT_FOCUSABLE NOT_TOUCH_MODAL TOUCHABLE_WHEN_WAKING WATCH_OUTSIDE_TOUCH SPLIT_TOUCH HARDWARE_ACCELERATED FLAG_SLIPPERY}
-    Requested w=1200 h=72 mLayoutSeq=138
+    Requested w=1200 h=1920 mLayoutSeq=20
     mBaseLayer=231000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
-    mToken=WindowToken{2a9308d android.os.BinderProxy@4ae3d24}
-    mViewVisibility=0x0 mHaveFrame=true mObscured=false
+    mToken=WindowToken{e73d6ec android.os.BinderProxy@f02159f}
+    mViewVisibility=0x8 mHaveFrame=true mObscured=false
     mSeq=0 mSystemUiVisibility=0x0
     mPolicyVisibility=false mLegacyPolicyVisibilityAfterAnim=false mAppOpVisibility=true parentHidden=false mPermanentlyHidden=false mHiddenWhileSuspended=false mForceHideNonSystemOverlayWindow=false
@@ -44,5 +44,5 @@

     mFullConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=undefined} s.6}
     mLastReportedConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=undefined} s.6}
-    mHasSurface=true isReadyForDisplay()=false mWindowRemovalAllowed=false
+    mHasSurface=false isReadyForDisplay()=false mWindowRemovalAllowed=false
     mFrame=[0,1848][1200,1920] last=[0,1848][1200,1920]
     Frames: containing=[0,1848][1200,1920] parent=[0,1848][1200,1920]
@@ -53,43 +53,75 @@

     Cur insets: overscan=[0,0][0,0] content=[0,0][0,0] visible=[0,0][0,0] stable=[0,0][0,0] surface=[0,0][0,0] outsets=[0,0][0,0] cutout=DisplayCutout{insets=Rect(0, 0 - 0, 0) boundingRect=Rect(0, 0 - 0, 0)}
     Lst insets: overscan=[0,0][0,0] content=[0,0][0,0] visible=[0,0][0,0] stable=[0,0][0,0] physical=[0,0][0,0] outset=[0,0][0,0] cutout=com.android.server.wm.utils.WmDisplayCutout@3c1
-    WindowStateAnimator{7d5b0d1 NavigationBar}:
-      mSurface=Surface(name=NavigationBar)/@0xc42c0b0
-      Surface: shown=false layer=0 alpha=1.0 rect=(0.0,0.0) 1200 x 72 transform=(1.0, 0.0, 1.0, 0.0)
-      mDrawState=HAS_DRAWN       mLastHidden=true
+    WindowStateAnimator{7e0fbe3 NavigationBar}:
+      mDrawState=NO_SURFACE       mLastHidden=true
       mSystemDecorRect=[0,0][1200,72] mLastClipRect=[0,0][1200,72]
-    isOnScreen=false
-    isVisible=false
-  Window #2 Window{fca8df0 u0 StatusBar}:
-    mDisplayId=0 stackId=0 mSession=Session{d1d50da 1151:u0a10036} mClient=android.os.BinderProxy@b8df96d
+      mShownAlpha=1.0 mAlpha=1.0 mLastAlpha=0.0
+    isOnScreen=false
+    isVisible=false
+  Window #2 Window{f76e49b u0 StatusBar}:
+    mDisplayId=0 stackId=0 mSession=Session{7b3ccfb 1109:u0a10036} mClient=android.os.BinderProxy@bbd3b4c
     mOwnerUid=10036 mShowToOwnerOnly=false package=com.android.systemui appop=NONE
-    mAttrs={(0,0)(fillx36) gr=TOP CENTER_VERTICAL sim={adjust=resize} layoutInDisplayCutoutMode=always ty=STATUS_BAR fmt=TRANSLUCENT
-      fl=NOT_FOCUSABLE TOUCHABLE_WHEN_WAKING WATCH_OUTSIDE_TOUCH SPLIT_TOUCH HARDWARE_ACCELERATED DRAWS_SYSTEM_BAR_BACKGROUNDS}
-    Requested w=1200 h=36 mLayoutSeq=138
+    mAttrs={(0,0)(fillxfill) gr=TOP CENTER_VERTICAL sim={adjust=resize} layoutInDisplayCutoutMode=always ty=STATUS_BAR fmt=TRANSLUCENT or=SCREEN_ORIENTATION_USER if=DISABLE_USER_ACTIVITY userActivityTimeout=30000
+      fl=TOUCHABLE_WHEN_WAKING ALT_FOCUSABLE_IM WATCH_OUTSIDE_TOUCH SHOW_WALLPAPER SPLIT_TOUCH HARDWARE_ACCELERATED DRAWS_SYSTEM_BAR_BACKGROUNDS
+      pfl=KEYGUARD}
+    Requested w=1200 h=36 mLayoutSeq=48
     mBaseLayer=171000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
-    mToken=WindowToken{a1cf633 android.os.BinderProxy@4c099a2}
-    mViewVisibility=0x0 mHaveFrame=true mObscured=false
-    mSeq=0 mSystemUiVisibility=0x0
-    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
-    mFullConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=undefined} s.6}
-    mLastReportedConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=undefined} s.6}
-    mHasSurface=true isReadyForDisplay()=true mWindowRemovalAllowed=false
-    mFrame=[0,0][1200,36] last=[0,0][1200,36]
+    mToken=WindowToken{83d20aa android.os.BinderProxy@6b9795}
+    mViewVisibility=0x0 mHaveFrame=true mObscured=false
+    mSeq=0 mSystemUiVisibility=0x0
+    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
+    mFullConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=undefined} s.6}
+    mLastReportedConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=undefined} s.6}
+    mHasSurface=true isReadyForDisplay()=true mWindowRemovalAllowed=false
+    mFrame=[0,0][1200,1920] last=[0,0][1200,1920]
     Frames: containing=[0,0][1200,1920] parent=[0,0][1200,1920]
         display=[0,0][1200,1920] overscan=[0,0][1200,1848]
-        content=[0,0][1200,36] visible=[0,0][1200,36]
+        content=[0,0][1200,1848] visible=[0,0][1200,1848]
         decor=[0,0][0,0]
         outset=[0,0][1200,1848]
-    Cur insets: overscan=[0,0][0,72] content=[0,0][0,0] visible=[0,0][0,0] stable=[0,0][0,0] surface=[0,0][0,0] outsets=[0,0][0,0] cutout=DisplayCutout{insets=Rect(0, 0 - 0, 0) boundingRect=Rect(0, 0 - 0, 0)}
-    Lst insets: overscan=[0,0][0,72] content=[0,0][0,0] visible=[0,0][0,0] stable=[0,0][0,0] physical=[0,0][0,0] outset=[0,0][0,0] cutout=com.android.server.wm.utils.WmDisplayCutout@3c1
-    WindowStateAnimator{4822736 StatusBar}:
-      mSurface=Surface(name=StatusBar)/@0xbbe5b3
-      Surface: shown=true layer=0 alpha=1.0 rect=(0.0,0.0) 1200 x 36 transform=(1.0, 0.0, 1.0, 0.0)
-      mDrawState=HAS_DRAWN       mLastHidden=false
-      mSystemDecorRect=[0,0][1200,36] mLastClipRect=[0,0][1200,36]
-    mLastFreezeDuration=+860ms
-    isOnScreen=true
-    isVisible=true
-  Window #3 Window{37e2ae7 u0 DockedStackDivider}:
-    mDisplayId=0 stackId=0 mSession=Session{d1d50da 1151:u0a10036} mClient=android.os.BinderProxy@57963e8
+    Cur insets: overscan=[0,0][0,72] content=[0,0][0,72] visible=[0,0][0,72] stable=[0,0][0,72] surface=[0,0][0,0] outsets=[0,0][0,0] cutout=DisplayCutout{insets=Rect(0, 0 - 0, 0) boundingRect=Rect(0, 0 - 0, 0)}
+    Lst insets: overscan=[0,0][0,72] content=[0,0][0,72] visible=[0,0][0,72] stable=[0,0][0,72] physical=[0,0][0,0] outset=[0,0][0,0] cutout=com.android.server.wm.utils.WmDisplayCutout@3c1
+    WindowStateAnimator{c1c99e0 StatusBar}:
+      mSurface=Surface(name=StatusBar)/@0x498ae2a
+      Surface: shown=true layer=0 alpha=1.0 rect=(0.0,0.0) 1200 x 1920 transform=(1.0, 0.0, 1.0, 0.0)
+      mDrawState=HAS_DRAWN       mLastHidden=false
+      mSystemDecorRect=[0,0][1200,1920] mLastClipRect=[0,0][1200,1920]
+    mLastFreezeDuration=+864ms
+    isOnScreen=true
+    isVisible=true
+  Window #3 Window{1de2240 u0 com.android.systemui}:
+    mDisplayId=0 stackId=0 mSession=Session{7b3ccfb 1109:u0a10036} mClient=android.os.BinderProxy@e6be172
+    mOwnerUid=10036 mShowToOwnerOnly=false package=com.android.systemui appop=SYSTEM_ALERT_WINDOW
+    mAttrs={(0,0)(wrapxwrap) gr=CENTER sim={adjust=pan forwardNavigation} ty=SYSTEM_ALERT fmt=TRANSLUCENT wanim=0x1030002 surfaceInsets=Rect(24, 24 - 24, 24)
+      fl=DIM_BEHIND ALT_FOCUSABLE_IM SPLIT_TOUCH HARDWARE_ACCELERATED
+      pfl=SHOW_FOR_ALL_USERS}
+    Requested w=870 h=412 mLayoutSeq=48
+    mBaseLayer=111000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
+    mToken=WindowToken{2cbe9c3 android.os.BinderProxy@e6be172}
+    mViewVisibility=0x0 mHaveFrame=true mObscured=false
+    mSeq=0 mSystemUiVisibility=0x0
+    mPolicyVisibility=false mLegacyPolicyVisibilityAfterAnim=false mAppOpVisibility=true parentHidden=false mPermanentlyHidden=false mHiddenWhileSuspended=false mForceHideNonSystemOverlayWindow=false
+    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
+    mFullConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=undefined} s.6}
+    mLastReportedConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=undefined} s.6}
+    mHasSurface=true isReadyForDisplay()=false mWindowRemovalAllowed=false
+    mFrame=[165,754][1035,1166] last=[165,754][1035,1166]
+    Frames: containing=[0,0][1200,1920] parent=[0,0][1200,1920]
+        display=[0,0][1200,1920] overscan=[0,0][1200,1920]
+        content=[165,754][1035,1166] visible=[165,754][1035,1166]
+        decor=[0,0][1200,1920]
+        outset=[0,0][0,0]
+    Cur insets: overscan=[0,0][0,0] content=[0,0][0,0] visible=[0,0][0,0] stable=[0,0][0,0] surface=[24,24][24,24] outsets=[0,0][0,0] cutout=DisplayCutout{insets=Rect(0, 0 - 0, 0) boundingRect=Rect(0, 0 - 0, 0)}
+    Lst insets: overscan=[0,0][0,0] content=[0,0][0,0] visible=[0,0][0,0] stable=[0,0][0,0] physical=[0,0][0,0] outset=[0,0][0,0] cutout=com.android.server.wm.utils.WmDisplayCutout@3c1
+    WindowStateAnimator{24ff499 }:
+      mSurface=Surface(name=)/@0xfe7f35e
+      Surface: shown=false layer=0 alpha=0.0 rect=(0.0,0.0) 918 x 460 transform=(1.0, 0.0, 1.0, 0.0)
+      mDrawState=READY_TO_SHOW       mLastHidden=true
+      mSystemDecorRect=[0,0][870,412] mLastClipRect=[0,0][918,460]
+      mShownAlpha=1.0 mAlpha=1.0 mLastAlpha=0.0
+    isOnScreen=false
+    isVisible=false
+  Window #4 Window{488e073 u0 DockedStackDivider}:
+    mDisplayId=0 stackId=0 mSession=Session{7b3ccfb 1109:u0a10036} mClient=android.os.BinderProxy@80406c4
     mOwnerUid=10036 mShowToOwnerOnly=false package=com.android.systemui appop=NONE
     mAttrs={(0,0)(fillx72) sim={adjust=pan} layoutInDisplayCutoutMode=always ty=DOCK_DIVIDER fmt=TRANSLUCENT
@@ -97,7 +129,7 @@

       pfl=NO_MOVE_ANIMATION
       vsysui=LAYOUT_STABLE LAYOUT_HIDE_NAVIGATION LAYOUT_FULLSCREEN}
-    Requested w=1200 h=72 mLayoutSeq=138
+    Requested w=1200 h=72 mLayoutSeq=48
     mBaseLayer=21000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
-    mToken=WindowToken{18fa0a6 android.os.BinderProxy@e906a01}
+    mToken=WindowToken{99cc4e2 android.os.BinderProxy@35ec9ad}
     mViewVisibility=0x4 mHaveFrame=true mObscured=false
     mSeq=0 mSystemUiVisibility=0x700
@@ -117,5 +149,5 @@

     Cur insets: overscan=[0,0][0,0] content=[0,0][0,0] visible=[0,0][0,0] stable=[0,36][0,72] surface=[0,0][0,0] outsets=[0,0][0,0] cutout=DisplayCutout{insets=Rect(0, 0 - 0, 0) boundingRect=Rect(0, 0 - 0, 0)}
     Lst insets: overscan=[0,0][0,0] content=[0,0][0,0] visible=[0,0][0,0] stable=[0,36][0,72] physical=[0,0][0,0] outset=[0,0][0,0] cutout=com.android.server.wm.utils.WmDisplayCutout@3c1
-    WindowStateAnimator{80c9e6 DockedStackDivider}:
+    WindowStateAnimator{fe1740c DockedStackDivider}:
       mDrawState=NO_SURFACE       mLastHidden=false
       mSystemDecorRect=[0,0][0,0] mLastClipRect=[0,0][0,0]
@@ -123,56 +155,23 @@

     isOnScreen=false
     isVisible=false
-  Window #4 Window{1ac9e16 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}:
-    mDisplayId=0 stackId=0 mSession=Session{c513bf2 1963:u0a10120} mClient=android.os.BinderProxy@c963731
+  Window #5 Window{2c47b02 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}:
+    mDisplayId=0 stackId=0 mSession=Session{9607795 1919:u0a10120} mClient=android.os.BinderProxy@159044d
     mOwnerUid=10120 mShowToOwnerOnly=true package=com.amazon.firelauncher appop=NONE
-    mAttrs={(0,0)(fillxfill) sim={state=always_hidden adjust=resize} ty=BASE_APPLICATION fmt=TRANSPARENT wanim=0x10302f8
+    mAttrs={(0,0)(fillxfill) sim={state=always_hidden adjust=pan forwardNavigation} ty=BASE_APPLICATION fmt=TRANSPARENT wanim=0x10302f8
       fl=LAYOUT_IN_SCREEN LAYOUT_INSET_DECOR SHOW_WALLPAPER SPLIT_TOUCH HARDWARE_ACCELERATED DRAWS_SYSTEM_BAR_BACKGROUNDS
       pfl=FORCE_DRAW_STATUS_BAR_BACKGROUND
       vsysui=LAYOUT_STABLE LAYOUT_HIDE_NAVIGATION LAYOUT_FULLSCREEN}
-    Requested w=1200 h=1920 mLayoutSeq=138
+    Requested w=0 h=0 mLayoutSeq=42
     mBaseLayer=21000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
-    mToken=AppWindowToken{1617879 token=Token{ef44140 ActivityRecord{1fb24c3 u0 com.amazon.firelauncher/.Launcher t2}}}
-    mAppToken=AppWindowToken{1617879 token=Token{ef44140 ActivityRecord{1fb24c3 u0 com.amazon.firelauncher/.Launcher t2}}}
-     isAnimatingWithSavedSurface()= mAppDied=false    drawnStateEvaluated=true    mightAffectAllDrawn=true
-    mViewVisibility=0x0 mHaveFrame=true mObscured=false
-    mSeq=0 mSystemUiVisibility=0x700
-    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
-    mFullConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
-    mLastReportedConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
-    mHasSurface=true isReadyForDisplay()=true mWindowRemovalAllowed=false
-    mFrame=[0,0][1200,1920] last=[0,0][1200,1920]
-    Frames: containing=[0,0][1200,1920] parent=[0,0][1200,1920]
-        display=[0,0][1200,1920] overscan=[0,0][1200,1920]
-        content=[0,36][1200,1920] visible=[0,36][1200,1920]
-        decor=[0,0][1200,1920]
-        outset=[0,0][0,0]
-    Cur insets: overscan=[0,0][0,0] content=[0,36][0,0] visible=[0,36][0,0] stable=[0,36][0,72] surface=[0,0][0,0] outsets=[0,0][0,0] cutout=DisplayCutout{insets=Rect(0, 0 - 0, 0) boundingRect=Rect(0, 0 - 0, 0)}
-    Lst insets: overscan=[0,0][0,0] content=[0,36][0,0] visible=[0,36][0,0] stable=[0,36][0,72] physical=[0,0][0,0] outset=[0,0][0,0] cutout=com.android.server.wm.utils.WmDisplayCutout@3c1
-    WindowStateAnimator{c2b4946 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}:
-      mSurface=Surface(name=com.amazon.firelauncher/com.amazon.firelauncher.Launcher)/@0x741db29
-      Surface: shown=true layer=0 alpha=1.0 rect=(0.0,0.0) 1200 x 1920 transform=(1.0, 0.0, 1.0, 0.0)
-      mDrawState=HAS_DRAWN       mLastHidden=false
-      mSystemDecorRect=[0,0][1200,1920] mLastClipRect=[0,0][1200,1920]
-    isOnScreen=true
-    isVisible=true
-  Window #5 Window{eb696b1 u0 com.android.launcher3/com.android.quickstep.RecentsActivity}:
-    mDisplayId=0 stackId=2 mSession=Session{fb22b1f 1948:u0a10075} mClient=android.os.BinderProxy@abe9558
-    mOwnerUid=10075 mShowToOwnerOnly=true package=com.android.launcher3 appop=NONE
-    mAttrs={(0,0)(fillxfill) sim={adjust=pan forwardNavigation} ty=BASE_APPLICATION fmt=TRANSPARENT wanim=0x10302f8
-      fl=LAYOUT_IN_SCREEN LAYOUT_INSET_DECOR SHOW_WALLPAPER SPLIT_TOUCH HARDWARE_ACCELERATED DRAWS_SYSTEM_BAR_BACKGROUNDS
-      pfl=FORCE_DRAW_STATUS_BAR_BACKGROUND
-      vsysui=LAYOUT_STABLE LAYOUT_HIDE_NAVIGATION LAYOUT_FULLSCREEN}
-    Requested w=1200 h=1920 mLayoutSeq=110
-    mBaseLayer=21000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
-    mToken=AppWindowToken{4640ea4 token=Token{de5f937 ActivityRecord{eb77636 u0 com.android.launcher3/com.android.quickstep.RecentsActivity t26}}}
-    mAppToken=AppWindowToken{4640ea4 token=Token{de5f937 ActivityRecord{eb77636 u0 com.android.launcher3/com.android.quickstep.RecentsActivity t26}}}
+    mToken=AppWindowToken{1f10017 token=Token{e40cc96 ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}}}
+    mAppToken=AppWindowToken{1f10017 token=Token{e40cc96 ActivityRecord{f7a5258 u0 com.amazon.firelauncher/.Launcher t2}}}
      isAnimatingWithSavedSurface()= mAppDied=false    drawnStateEvaluated=true    mightAffectAllDrawn=true
     mViewVisibility=0x8 mHaveFrame=true mObscured=false
     mSeq=0 mSystemUiVisibility=0x700
     mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
-    mFullConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=recents} s.6}
-    mLastReportedConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=recents} s.6}
+    mFullConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
```
