# Phase 3C snapshot comparison

- Before: `adb/phase3c/PHASE3C-PREFERRED-P0-02/before`
- After: `adb/phase3c/PHASE3C-PREFERRED-P0-02/after_preferred`
- Before files: `175`
- After files: `175`
- Changed files: `23`

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
- `summary.md` — changed
- `users/dumpsys_user.stdout.txt` — changed
- `window/input.stdout.txt` — changed
- `window/processes.stdout.txt` — changed

## Focused evidence

### `activity/activities.stdout.txt`

```text
4:   Stack #0: type=home mode=fullscreen
12:     * TaskRecord{87ddf9b #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
14:       affinity=10120:com.amazon.firelauncher
15:       intent={act=android.intent.action.MAIN cat=[android.intent.category.HOME] flg=0x10000100 cmp=com.amazon.firelauncher/.Launcher}
16:       realActivity=com.amazon.firelauncher/.Launcher
19:       Activities=[ActivityRecord{1fb24c3 u0 com.amazon.firelauncher/.Launcher t2}]
21:       mRootProcess=ProcessRecord{49b9f38 1963:com.amazon.firelauncher/u0a120}
24:       * Hist #0: ActivityRecord{1fb24c3 u0 com.amazon.firelauncher/.Launcher t2}
25:           packageName=com.amazon.firelauncher processName=com.amazon.firelauncher
27:           app=ProcessRecord{49b9f38 1963:com.amazon.firelauncher/u0a120}
28:           Intent { act=android.intent.action.MAIN cat=[android.intent.category.HOME] flg=0x10000100 cmp=com.amazon.firelauncher/.Launcher }
29:           frontOfTask=true task=TaskRecord{87ddf9b #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
30:           taskAffinity=10120:com.amazon.firelauncher
31:           realActivity=com.amazon.firelauncher/.Launcher
32:           baseDir=/system/priv-app/com.amazon.firelauncher/com.amazon.firelauncher.apk
33:           dataDir=/data/user/0/com.amazon.firelauncher
34:           stateNotNeeded=false componentSpecified=false mActivityType=home
38:            mOverrideConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
39:           CurrentConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
40:           OverrideConfiguration={0.0 ?mcc?mnc ?localeList ?layoutDir ?swdp ?wdp ?hdp ?density ?lsize ?long ?ldr ?wideColorGamut ?orien ?uimode ?night ?touch ?keyb/?/? ?nav/? winConfig={ mBounds=Rect(0, 0 - 0, 0) mAppBounds=null mWindowingMode=undefined mActivityType=home}}
51:           mActivityType=home
57:       TaskRecord{87ddf9b #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
58:         Run #0: ActivityRecord{1fb24c3 u0 com.amazon.firelauncher/.Launcher t2}
60:     mResumedActivity: ActivityRecord{1fb24c3 u0 com.amazon.firelauncher/.Launcher t2}
71:     * TaskRecord{dd3d92d #26 I=com.android.launcher3/com.android.quickstep.RecentsActivity U=0 StackId=2 sz=1}
72:       userId=0 effectiveUid=u0a75 mCallingUid=u0a75 mUserSetupComplete=true mCallingPackage=com.android.launcher3
73:       intent={act=android.intent.action.MAIN cat=[android.intent.category.DEFAULT] flg=0x10800000 cmp=com.android.launcher3/com.android.quickstep.RecentsActivity}
74:       realActivity=com.android.launcher3/com.android.quickstep.RecentsActivity
77:       Activities=[ActivityRecord{eb77636 u0 com.android.launcher3/com.android.quickstep.RecentsActivity t26}]
81:       * Hist #0: ActivityRecord{eb77636 u0 com.android.launcher3/com.android.quickstep.RecentsActivity t26}
82:           packageName=com.android.launcher3 processName=com.android.launcher3
83:           launchedFromUid=10075 launchedFromPackage=com.android.launcher3 userId=0
84:           app=ProcessRecord{97e6c35 1948:com.android.launcher3/u0a75}
85:           Intent { act=android.intent.action.MAIN cat=[android.intent.category.DEFAULT] flg=0x10800000 cmp=com.android.launcher3/com.android.quickstep.RecentsActivity }
86:           frontOfTask=true task=TaskRecord{dd3d92d #26 I=com.android.launcher3/com.android.quickstep.RecentsActivity U=0 StackId=2 sz=1}
88:           realActivity=com.android.launcher3/com.android.quickstep.RecentsActivity
89:           baseDir=/system/priv-app/com.android.launcher3/com.android.launcher3.apk
90:           dataDir=/data/user/0/com.android.launcher3
114:       TaskRecord{dd3d92d #26 I=com.android.launcher3/com.android.quickstep.RecentsActivity U=0 StackId=2 sz=1}
115:         Run #0: ActivityRecord{eb77636 u0 com.android.launcher3/com.android.quickstep.RecentsActivity t26}
117:     mLastPausedActivity: ActivityRecord{eb77636 u0 com.android.launcher3/com.android.quickstep.RecentsActivity t26}
119:   ResumedActivity: ActivityRecord{1fb24c3 u0 com.amazon.firelauncher/.Launcher t2}
120:   mFocusedStack=ActivityStack{88f66b4 stackId=0 type=home mode=fullscreen visible=true translucent=false, 1 tasks} mLastFocusedStack=ActivityStack{88f66b4 stackId=0 type=home mode=fullscreen visible=true translucent=false, 1 tasks}
124:    mHomeStack=ActivityStack{88f66b4 stackId=0 type=home mode=fullscreen visible=true translucent=false, 1 tasks}
126:   isHomeRecentsComponent=false  KeyguardController:
```

### `activity/recents.stdout.txt`

```text
3: mRecentsComponent=ComponentInfo{com.android.launcher3/com.android.quickstep.RecentsActivity}
5:   * Recent #0: TaskRecord{87ddf9b #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
7:     affinity=10120:com.amazon.firelauncher
8:     intent={act=android.intent.action.MAIN cat=[android.intent.category.HOME] flg=0x10000100 cmp=com.amazon.firelauncher/.Launcher}
9:     realActivity=com.amazon.firelauncher/.Launcher
12:     Activities=[ActivityRecord{1fb24c3 u0 com.amazon.firelauncher/.Launcher t2}]
14:     mRootProcess=ProcessRecord{49b9f38 1963:com.amazon.firelauncher/u0a120}
17:   * Recent #1: TaskRecord{dd3d92d #26 I=com.android.launcher3/com.android.quickstep.RecentsActivity U=0 StackId=2 sz=1}
18:     userId=0 effectiveUid=u0a75 mCallingUid=u0a75 mUserSetupComplete=true mCallingPackage=com.android.launcher3
19:     intent={act=android.intent.action.MAIN cat=[android.intent.category.DEFAULT] flg=0x10800000 cmp=com.android.launcher3/com.android.quickstep.RecentsActivity}
20:     realActivity=com.android.launcher3/com.android.quickstep.RecentsActivity
23:     Activities=[ActivityRecord{eb77636 u0 com.android.launcher3/com.android.quickstep.RecentsActivity t26}]
```

### `activity/top.stdout.txt`

```text
2:   ACTIVITY com.android.launcher3/com.android.quickstep.RecentsActivity eb77636 pid=1948
65: TASK 10120:com.amazon.firelauncher id=2 userId=0
66:   ACTIVITY com.amazon.firelauncher/.Launcher 1fb24c3 pid=1963
70:       mCurrentConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
107:       DecorView@c990929[Launcher]
110:             com.amazon.firelauncher.appsgrid.ui.drag.DragLayer{c15824f V.E...... ........ 0,0-1200,1920 #7f090336 app:id/magazine_container}
113:               com.amazon.firelauncher.view.EnhancedViewPager{e7e4dba VFED..... ........ 0,0-1200,1920 #7f090379 app:id/pager}
114:                 com.amazon.firelauncher.appsgrid.ui.ScrollableMainView{1979eee V.E...... ........ 0,0-1200,1920}
115:                   com.amazon.firelauncher.appsgrid.ui.GradientScrimFrameLayout{f51f46b V.E...... ........ 0,0-1200,1920}
116:                     com.amazon.firelauncher.appsgrid.ui.GridView{574be6d VFED..... ........ 0,0-1200,1920 #7f09027a app:id/favorites_page}
119:                           com.amazon.firelauncher.view.LoadingDotsView{b37b461 V.E...... ......I. 0,0-0,0 #7f09032c app:id/loading_dots}
208:                 com.amazon.firelauncher.view.ScrollObservableContainer{f43721c V.E...... ........ 1200,0-2400,1920}
209:                   com.amazon.firelauncher.view.ChannelBackgroundView{5470515 V.ED..... ........ 0,0-1200,1920 #7f0900ef app:id/background_view}
210:                   com.amazon.firelauncher.view.ScrollingLinearRecyclerView{15aa862 VFED..... ........ 0,0-1200,1920 #7f09039e app:id/recycler}
228:                         com.amazon.firelauncher.view.LoadingDotsView{ec2740b V.E...... ......I. 0,0-0,0 #7f09032c app:id/loading_dots}
241:                         com.amazon.firelauncher.view.NavTabView{2639190 VFE...C.. ........ 0,0-240,84}
244:                         com.amazon.firelauncher.view.NavTabView{ea29b8a VFE...C.. ..S..... 240,0-431,84}
247:                         com.amazon.firelauncher.view.NavTabView{c977871 VFE...C.. ........ 431,0-719,84}
250:                 com.amazon.firelauncher.view.SearchWidgetHostLayout{9bc4bc4 V.E...... ........ -18,-6-1218,192 #7f0903ba app:id/search_bar_widget}
251:                   com.amazon.firelauncher.search.SearchAppWidgetHostView{1da2aad V.E...... R....... 0,0-1236,198}
267:                     com.amazon.firelauncher.appsgrid.ui.FolderView{88191d VFED..... ......I. 0,0-0,0 #7f090288 app:id/folder_grid}
277:       context: com.amazon.firelauncher.Launcher@38c4811
278:       client: com.amazon.firelauncher.Launcher@38c4811
304:         mContainer=com.amazon.firelauncher.view.EnhancedViewPager{e7e4dba VFED..... ........ 0,0-1200,1920 #7f090379 app:id/pager}
337:         mContainer=com.amazon.firelauncher.view.EnhancedViewPager{e7e4dba VFED..... ........ 0,0-1200,1920 #7f090379 app:id/pager}
338:         mView=com.amazon.firelauncher.view.ScrollObservableContainer{f43721c V.E...... ........ 1200,0-2400,1920}
355:         mContainer=com.amazon.firelauncher.view.EnhancedViewPager{e7e4dba VFED..... ........ 0,0-1200,1920 #7f090379 app:id/pager}
356:         mView=com.amazon.firelauncher.appsgrid.ui.ScrollableMainView{1979eee V.E...... ........ 0,0-1200,1920}
```

### `appops/all.stdout.txt`

```text
697:     Package com.android.launcher3:
981:     Package com.amazon.firelauncher:
1276:     Package com.microsoft.launcher:
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
4:         2be7ead com.amazon.firelauncher/.Launcher filter f41900c
8:           Authority: "com.amazon.firelauncher": -1
11:       com.amazon.firelauncher.REQUEST_LOCATION_PERMISSION:
12:         2be7ead com.amazon.firelauncher/.Launcher filter 13c7f3f
13:           Action: "com.amazon.firelauncher.REQUEST_LOCATION_PERMISSION"
15:       com.amazon.firelauncher.intent.action.TUTORIALDONE:
16:         2be7ead com.amazon.firelauncher/.Launcher filter 8abaf5e
18:           Action: "com.amazon.firelauncher.intent.action.ALEXA_TUTORIAL"
19:           Action: "com.amazon.firelauncher.intent.action.TUTORIAL"
20:           Action: "com.amazon.firelauncher.intent.action.TUTORIALDONE"
21:           Category: "android.intent.category.HOME"
23:           mPriority=50, mOrder=0, mHasPartialTypes=false
24:       com.amazon.firelauncher.intent.action.ALEXA_TUTORIAL:
25:         2be7ead com.amazon.firelauncher/.Launcher filter 8abaf5e
27:           Action: "com.amazon.firelauncher.intent.action.ALEXA_TUTORIAL"
28:           Action: "com.amazon.firelauncher.intent.action.TUTORIAL"
29:           Action: "com.amazon.firelauncher.intent.action.TUTORIALDONE"
30:           Category: "android.intent.category.HOME"
32:           mPriority=50, mOrder=0, mHasPartialTypes=false
34:         2be7ead com.amazon.firelauncher/.Launcher filter 8abaf5e
36:           Action: "com.amazon.firelauncher.intent.action.ALEXA_TUTORIAL"
37:           Action: "com.amazon.firelauncher.intent.action.TUTORIAL"
38:           Action: "com.amazon.firelauncher.intent.action.TUTORIALDONE"
39:           Category: "android.intent.category.HOME"
41:           mPriority=50, mOrder=0, mHasPartialTypes=false
42:         95eeef1 com.amazon.firelauncher/.LauncherUserSettings filter e162d55
47:         95eeef1 com.amazon.firelauncher/.LauncherUserSettings filter e162d55
51:       com.amazon.firelauncher.intent.action.TUTORIAL:
52:         2be7ead com.amazon.firelauncher/.Launcher filter 8abaf5e
54:           Action: "com.amazon.firelauncher.intent.action.ALEXA_TUTORIAL"
55:           Action: "com.amazon.firelauncher.intent.action.TUTORIAL"
56:           Action: "com.amazon.firelauncher.intent.action.TUTORIALDONE"
57:           Category: "android.intent.category.HOME"
59:           mPriority=50, mOrder=0, mHasPartialTypes=false
64:         190d9fd com.amazon.firelauncher/com.amazon.fireappscardproducer.service.SystemNotificationProducerService$PackageRecencyReceiver filter bac2157
68:         26cecf0 com.amazon.firelauncher/.reccardproducer.ProducerService$MusicUnlimitedRegistrationReceiver filter 6530661
71:         2ccefae com.amazon.firelauncher/com.amazon.fireappscardproducer.service.CardActionService$RemoveFromDeviceReceiverOld filter 92192d
73:       com.amazon.cmsfirecardproducer.REMOVE_FROM_HOME:
74:         5ed3599 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.CardActionService$RemoveFromHomeReceiverOld filter abce444
75:           Action: "com.amazon.cmsfirecardproducer.REMOVE_FROM_HOME"
76:       com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_APPS:
77:         346ad40 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.CardActionService$RemoveFromHomeReceiver filter 7ae9e62
78:           Action: "com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_APPS"
79:           Action: "com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_GAMES"
80:       com.amazon.firelauncher.appmanager.APPS_REMOVED:
81:         542a918 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$PackageChangeReceiver filter 42f698
82:           Action: "com.amazon.firelauncher.appmanager.APPS_ADDED"
83:           Action: "com.amazon.firelauncher.appmanager.APPS_REMOVED"
84:           Action: "com.amazon.firelauncher.appmanager.APPS_UPDATED"
85:           Action: "com.amazon.firelauncher.APP_RECENCY_REBUILD"
87:         515aba9 com.amazon.firelauncher/.ui.GlobalSyncReceiver filter 79be368
89:         23dc52e com.amazon.firelauncher/com.amazon.heroshoveler.weather.WeatherRefreshService$GlobalSyncReceiver filter 719b381
91:         5f528cf com.amazon.firelauncher/.cardproducer.LauncherProducerService$GlobalSyncReceiver filter 6decbac
93:         aeba25c com.amazon.firelauncher/com.amazon.hintscardproducer.HintsCardRefreshService$GlobalSyncReceiver filter 5c3e674
96:         54765d5 com.amazon.firelauncher/.images.storage.LowStorageReceiver filter 3e38b7c
98:       com.amazon.firelauncher.appmanager.APPS_ADDED:
99:         542a918 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$PackageChangeReceiver filter 42f698
100:           Action: "com.amazon.firelauncher.appmanager.APPS_ADDED"
101:           Action: "com.amazon.firelauncher.appmanager.APPS_REMOVED"
102:           Action: "com.amazon.firelauncher.appmanager.APPS_UPDATED"
103:           Action: "com.amazon.firelauncher.APP_RECENCY_REBUILD"
104:       com.amazon.firelauncher.START_EDIT_MODE_EXTERNAL:
105:         49df803 com.amazon.firelauncher/.appsgrid.StartEditModeReceiver filter ce0d68b
106:           Action: "com.amazon.firelauncher.START_EDIT_MODE_EXTERNAL"
107:           mPriority=100, mOrder=0, mHasPartialTypes=false
109:         e519aae com.amazon.firelauncher/com.amazon.firecard.deviceclient.clients.MultiplexingMessageReceiver filter 1f35075
112:           Category: "com.amazon.firelauncher"
113:       com.amazon.firelauncher.action.REC_SUPPRESS:
114:         33b3955 com.amazon.firelauncher/.reccardproducer.ProducerService$ItemSuppressionReceiver filter 50277dc
115:           Action: "com.amazon.firelauncher.action.REC_SUPPRESS"
116:       com.amazon.firelauncher.action.UPSELL_TAPPED_NOTIFICATION:
117:         a4080e com.amazon.firelauncher/.reccardproducer.ProducerService$UpsellTappedNotificationReceiver filter c2d35c8
118:           Action: "com.amazon.firelauncher.action.UPSELL_TAPPED_NOTIFICATION"
120:         603e6a5 com.amazon.firelauncher/com.amazon.identity.auth.accounts.SessionUserChangedToAccountForPackageChangedAdpater filter 11d2099
122:       com.amazon.firelauncher.action.WEBLAB_UPDATE:
123:         aca5e32 com.amazon.firelauncher/.reccardproducer.ProducerService$UpNextWeblabUpdateReceiver filter 834766b
124:           Action: "com.amazon.firelauncher.action.WEBLAB_UPDATE"
126:         dd318df com.amazon.firelauncher/com.amazon.heroshoveler.weather.RefreshCardsBroadcastReceiver filter 1ffce14
128:         fefb92c com.amazon.firelauncher/.cardproducer.LauncherProducerService$RefreshCardsReceiver filter 2851b9
131:         7856ff5 com.amazon.firelauncher/com.amazon.firecard.deviceclient.CloudCardEventService$RefreshCardsReceiver filter 69b180a
133:         86b818a com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$RefreshCardsReceiver filter 318787b
135:         1fa63fb com.amazon.firelauncher/.reccardproducer.ProducerService$RefreshCardsReceiver filter 7a41b29
137:         1353c18 com.amazon.firelauncher/com.amazon.hintscardproducer.HintsCardRefreshService$RefreshCardsReceiver filter 9220e47
139:       com.amazon.firelauncher.action.FOR_YOU_CHANNEL_VISIBLE:
140:         f2841eb com.amazon.firelauncher/com.amazon.heroshoveler.weather.WeatherRefreshBroadcastReceiver filter 867a4b2
141:           Action: "com.amazon.firelauncher.action.FOR_YOU_CHANNEL_VISIBLE"
142:         efbdb48 com.amazon.firelauncher/.cardproducer.LauncherProducerService$ChannelVisibilityChangeReceiver filter ea0e55f
143:           Action: "com.amazon.firelauncher.action.FOR_YOU_CHANNEL_VISIBLE"
144:         fbc7de1 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$ChannelVisibilityChangeReceiver filter 3c600b0
145:           Action: "com.amazon.firelauncher.action.FOR_YOU_CHANNEL_VISIBLE"
147:         b51fab7 com.amazon.firelauncher/.cardproducer.LauncherProducerService$AccountChangeReceiver filter 82759fe
151:         f41c31 com.amazon.firelauncher/com.amazon.heroshoveler.weather.WeatherRefreshService$LocaleChangedReceiver filter 168ec26
153:         76d1f16 com.amazon.firelauncher/amazon.alexa.locale.AlexaLocaleHelper filter c15b780
155:         fefb92c com.amazon.firelauncher/.cardproducer.LauncherProducerService$RefreshCardsReceiver filter 2851b9
158:         9f32097 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.SystemNotificationProducerService$LocaleChangeReceiver filter 3daaad6
160:         c3d1284 com.amazon.firelauncher/.reccardproducer.ProducerService$LocaleChangedReceiver filter 73e44f
162:         7bd4a6d com.amazon.firelauncher/com.amazon.hintscardproducer.HintsCardRefreshService$LocaleChangedReceiver filter 658a79d
164:       com.amazon.firelauncher.action.TAB_SETTINGS_CHANGED:
165:         97bcf05 com.amazon.firelauncher/.reccardproducer.ProducerService$TabSuppressionReceiver filter 2ba40e5
166:           Action: "com.amazon.firelauncher.action.TAB_SETTINGS_CHANGED"
167:       com.amazon.firelauncher.action.HOST_APP_COLD_START_ACTION:
168:         89a88c5 com.amazon.firelauncher/.reccardproducer.ProducerService$ColdStartReceiver filter d517586
169:           Action: "com.amazon.firelauncher.action.HOST_APP_COLD_START_ACTION"
170:         cd6721a com.amazon.firelauncher/com.amazon.hintscardproducer.HintsCardRefreshService$ColdStartReceiver filter e6747e3
171:           Action: "com.amazon.firelauncher.action.HOST_APP_COLD_START_ACTION"
173:         73f9c com.amazon.firelauncher/com.amazon.identity.auth.device.storage.LambortishClock$ChangeTimestampsBroadcastReceiver filter 672f5e0
175:       com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_GAMES:
176:         346ad40 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.CardActionService$RemoveFromHomeReceiver filter 7ae9e62
177:           Action: "com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_APPS"
178:           Action: "com.amazon.firecard.action.remove.FROM_HOME.CONTENT_TYPE_GAMES"
179:       com.amazon.firelauncher.APP_RECENCY_REBUILD:
180:         542a918 com.amazon.firelauncher/com.amazon.fireappscardproducer.service.LauncherNotificationProducerService$PackageChangeReceiver filter 42f698
181:           Action: "com.amazon.firelauncher.appmanager.APPS_ADDED"
182:           Action: "com.amazon.firelauncher.appmanager.APPS_REMOVED"
183:           Action: "com.amazon.firelauncher.appmanager.APPS_UPDATED"
184:           Action: "com.amazon.firelauncher.APP_RECENCY_REBUILD"
185:       com.amazon.firelauncher.action.RECENCY_UPDATE:
186:         71b5a8f com.amazon.firelauncher/.reccardproducer.ProducerService$RecencyUpdateReceiver filter f3197ba
187:           Action: "com.amazon.firelauncher.action.RECENCY_UPDATE"
189:         e519aae com.amazon.firelauncher/com.amazon.firecard.deviceclient.clients.MultiplexingMessageReceiver filter 1f35075
```

### `package/full_dump.stdout.txt`

```text
149:   android.software.home_screen
238:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
247:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
250:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
252:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
258:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
267:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
272:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher
275:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
300:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
303:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
305:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
314:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
319:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
322:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
327:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
330:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
337:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
343:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
348:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
351:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
353:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
357:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
359:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
363:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
364:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
367:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
368:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
371:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
372:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
379:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
382:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
385:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
386:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
392:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
396:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
398:         e0653b9 com.amazon.mp3/.activity.ExternalLauncherActivity
402:         4a33fe com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
405:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
416:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
417:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
420:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
423:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
426:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
431:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
443:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
446:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
468:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
475:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
482:         432e86b com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
484:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
491:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
504:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
513:         2242299 com.amazon.cloud9/com.amazon.slate.silo.SiloLauncherActivity
515:         58b4f55 com.microsoft.launcher/com.microsoft.bing.ProcessTextSearch
517:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
521:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
537:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
538:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
548:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
550:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
553:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
556:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
570:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
579:         432e86b com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
581:         58f140d com.amazon.photos/com.android.launcher3.WallpaperCropActivity
584:         993060e com.microsoft.launcher/.wallpaper.activity.WallpaperPreviewActivity (2 filters)
586:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
592:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher
594:         e0653b9 com.amazon.mp3/.activity.ExternalLauncherActivity
597:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
600:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
601:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
631:         e0653b9 com.amazon.mp3/.activity.ExternalLauncherActivity
643:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
648:         e0653b9 com.amazon.mp3/.activity.ExternalLauncherActivity
651:         2242299 com.amazon.cloud9/com.amazon.slate.silo.SiloLauncherActivity
653:         58b4f55 com.microsoft.launcher/com.microsoft.bing.ProcessTextSearch
656:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity (7 filters)
660:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (7 filters)
669:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher (2 filters)
680:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity (34 filters)
684:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (9 filters)
702:         4a33fe com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
705:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
712:         432e86b com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
714:         58f140d com.amazon.photos/com.android.launcher3.WallpaperCropActivity
717:         993060e com.microsoft.launcher/.wallpaper.activity.WallpaperPreviewActivity (2 filters)
719:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
727:         432e86b com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
729:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
735:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
752:         f7a1a7d com.amazon.windowshop/com.amazon.mShop.android.home.PublicUrlActivity
785:         a303796 com.android.vending/com.google.android.finsky.instantlaunchapi.InstantLauncherActivity
813:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher (3 filters)
819:       ms-launcher:
820:         4ad915 com.microsoft.launcher/.contacts.PeopleDeepLinkActivity
821:         57292cc com.microsoft.launcher/com.microsoft.rewards.activity.OfferLandingActivity
822:         cd8d4ff com.microsoft.launcher/com.microsoft.rewards.activity.RewardsActionsActivity
831:         f7a1a7d com.amazon.windowshop/com.amazon.mShop.android.home.PublicUrlActivity
847:         ec51dd0 com.google.android.gms/.home.SetupDeviceActivityQrCode
849:         7e341c9 com.google.android.gms/.home.SetupDeviceActivityNfc
867:         e2646fc com.amazon.avod/.client.activity.HomeScreenActivity
870:         3432f39 com.amazon.photos/com.amazon.gallery.thor.app.activity.ATCLauncherActivity
881:         fcddf8a com.microsoft.launcher/.setting.FakeSms
887:         fcddf8a com.microsoft.launcher/.setting.FakeSms
899:         2be7ead com.amazon.firelauncher/.Launcher
901:         4653f3a com.amazon.venezia/.CFR.dialog.CFRLauncherActivity
909:         fac1d73 com.amazon.kindle.otter.oobe/.OOBELauncherV2
914:         4a33fe com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
915:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher (2 filters)
920:         432e86b com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
931:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher (3 filters)
935:         2d81506 com.amazon.photos/com.amazon.gallery.thor.app.activity.LauncherActivity (22 filters)
957:         bd74963 com.android.vending/com.google.android.finsky.protect.impl.PlayProtectHomeDeepLinkActivity
958:         c5a73e1 com.amazon.cloud9/org.chromium.chrome.browser.DragAndDropLauncherActivity
978:         25d60b7 org.mozilla.firefox/org.mozilla.fenix.HomeActivity
982:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher (4 filters)
990:         2d81506 com.amazon.photos/com.amazon.gallery.thor.app.activity.LauncherActivity (22 filters)
1021:         a24d78d com.google.android.inputmethod.latin/com.google.android.apps.inputmethod.latin.sharing.LinkReceivingLauncherActivity
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
238:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
247:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
250:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
252:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
258:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
267:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
272:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher
275:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
300:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
303:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
305:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
314:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
319:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
322:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
327:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
330:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
337:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
343:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
348:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
351:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
353:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
357:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
359:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
363:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
364:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
367:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
368:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
371:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
372:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
379:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
382:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
385:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
386:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
392:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
396:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
398:         e0653b9 com.amazon.mp3/.activity.ExternalLauncherActivity
402:         4a33fe com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
405:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
416:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
417:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
420:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
423:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
426:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
431:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
443:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
446:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
468:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
475:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
482:         432e86b com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
484:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
491:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
504:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
513:         2242299 com.amazon.cloud9/com.amazon.slate.silo.SiloLauncherActivity
515:         58b4f55 com.microsoft.launcher/com.microsoft.bing.ProcessTextSearch
517:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
521:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
537:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
538:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
548:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
550:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
553:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
556:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
570:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
579:         432e86b com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
581:         58f140d com.amazon.photos/com.android.launcher3.WallpaperCropActivity
584:         993060e com.microsoft.launcher/.wallpaper.activity.WallpaperPreviewActivity (2 filters)
586:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
592:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher
594:         e0653b9 com.amazon.mp3/.activity.ExternalLauncherActivity
597:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
600:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
601:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
631:         e0653b9 com.amazon.mp3/.activity.ExternalLauncherActivity
643:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
648:         e0653b9 com.amazon.mp3/.activity.ExternalLauncherActivity
651:         2242299 com.amazon.cloud9/com.amazon.slate.silo.SiloLauncherActivity
653:         58b4f55 com.microsoft.launcher/com.microsoft.bing.ProcessTextSearch
656:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity (7 filters)
660:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (7 filters)
669:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher (2 filters)
680:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity (34 filters)
684:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (9 filters)
702:         4a33fe com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
705:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
712:         432e86b com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
714:         58f140d com.amazon.photos/com.android.launcher3.WallpaperCropActivity
717:         993060e com.microsoft.launcher/.wallpaper.activity.WallpaperPreviewActivity (2 filters)
719:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
727:         432e86b com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
729:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
735:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
752:         f7a1a7d com.amazon.windowshop/com.amazon.mShop.android.home.PublicUrlActivity
785:         a303796 com.android.vending/com.google.android.finsky.instantlaunchapi.InstantLauncherActivity
813:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher (3 filters)
819:       ms-launcher:
820:         4ad915 com.microsoft.launcher/.contacts.PeopleDeepLinkActivity
821:         57292cc com.microsoft.launcher/com.microsoft.rewards.activity.OfferLandingActivity
822:         cd8d4ff com.microsoft.launcher/com.microsoft.rewards.activity.RewardsActionsActivity
831:         f7a1a7d com.amazon.windowshop/com.amazon.mShop.android.home.PublicUrlActivity
847:         ec51dd0 com.google.android.gms/.home.SetupDeviceActivityQrCode
849:         7e341c9 com.google.android.gms/.home.SetupDeviceActivityNfc
867:         e2646fc com.amazon.avod/.client.activity.HomeScreenActivity
870:         3432f39 com.amazon.photos/com.amazon.gallery.thor.app.activity.ATCLauncherActivity
881:         fcddf8a com.microsoft.launcher/.setting.FakeSms
887:         fcddf8a com.microsoft.launcher/.setting.FakeSms
899:         2be7ead com.amazon.firelauncher/.Launcher
901:         4653f3a com.amazon.venezia/.CFR.dialog.CFRLauncherActivity
909:         fac1d73 com.amazon.kindle.otter.oobe/.OOBELauncherV2
914:         4a33fe com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
915:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher (2 filters)
920:         432e86b com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
931:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher (3 filters)
935:         2d81506 com.amazon.photos/com.amazon.gallery.thor.app.activity.LauncherActivity (22 filters)
957:         bd74963 com.android.vending/com.google.android.finsky.protect.impl.PlayProtectHomeDeepLinkActivity
958:         c5a73e1 com.amazon.cloud9/org.chromium.chrome.browser.DragAndDropLauncherActivity
978:         25d60b7 org.mozilla.firefox/org.mozilla.fenix.HomeActivity
982:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher (4 filters)
990:         2d81506 com.amazon.photos/com.amazon.gallery.thor.app.activity.LauncherActivity (22 filters)
1021:         a24d78d com.google.android.inputmethod.latin/com.google.android.apps.inputmethod.latin.sharing.LinkReceivingLauncherActivity
```

### `package/preferred_activities.stdout.txt`

```text
149:   android.software.home_screen
238:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
247:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
250:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
252:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
258:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
267:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
272:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher
275:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
300:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
303:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
305:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
314:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
319:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
322:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
327:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
330:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
337:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
343:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
348:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
351:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
353:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
357:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
359:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
363:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
364:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
367:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
368:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
371:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
372:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
379:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
382:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
385:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
386:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
392:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
396:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
398:         e0653b9 com.amazon.mp3/.activity.ExternalLauncherActivity
402:         4a33fe com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
405:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
416:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
417:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
420:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
423:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
426:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
431:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
443:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
446:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
468:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
475:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
482:         432e86b com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
484:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
491:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
504:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
513:         2242299 com.amazon.cloud9/com.amazon.slate.silo.SiloLauncherActivity
515:         58b4f55 com.microsoft.launcher/com.microsoft.bing.ProcessTextSearch
517:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
521:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
537:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
538:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
548:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
550:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
553:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
556:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
570:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
579:         432e86b com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
581:         58f140d com.amazon.photos/com.android.launcher3.WallpaperCropActivity
584:         993060e com.microsoft.launcher/.wallpaper.activity.WallpaperPreviewActivity (2 filters)
586:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
592:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher
594:         e0653b9 com.amazon.mp3/.activity.ExternalLauncherActivity
597:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
600:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity
601:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
631:         e0653b9 com.amazon.mp3/.activity.ExternalLauncherActivity
643:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
648:         e0653b9 com.amazon.mp3/.activity.ExternalLauncherActivity
651:         2242299 com.amazon.cloud9/com.amazon.slate.silo.SiloLauncherActivity
653:         58b4f55 com.microsoft.launcher/com.microsoft.bing.ProcessTextSearch
656:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity (7 filters)
660:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (7 filters)
669:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher (2 filters)
680:         7fbf223 com.kingsoft.office.amz/cn.wps.moffice.main.select.phone.HomeSelectActivity (34 filters)
684:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (9 filters)
702:         4a33fe com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
705:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
712:         432e86b com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
714:         58f140d com.amazon.photos/com.android.launcher3.WallpaperCropActivity
717:         993060e com.microsoft.launcher/.wallpaper.activity.WallpaperPreviewActivity (2 filters)
719:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
727:         432e86b com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
729:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity (2 filters)
735:         9d0214c com.android.bluetooth/.opp.BluetoothOppLauncherActivity
752:         f7a1a7d com.amazon.windowshop/com.amazon.mShop.android.home.PublicUrlActivity
785:         a303796 com.android.vending/com.google.android.finsky.instantlaunchapi.InstantLauncherActivity
813:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher (3 filters)
819:       ms-launcher:
820:         4ad915 com.microsoft.launcher/.contacts.PeopleDeepLinkActivity
821:         57292cc com.microsoft.launcher/com.microsoft.rewards.activity.OfferLandingActivity
822:         cd8d4ff com.microsoft.launcher/com.microsoft.rewards.activity.RewardsActionsActivity
831:         f7a1a7d com.amazon.windowshop/com.amazon.mShop.android.home.PublicUrlActivity
847:         ec51dd0 com.google.android.gms/.home.SetupDeviceActivityQrCode
849:         7e341c9 com.google.android.gms/.home.SetupDeviceActivityNfc
867:         e2646fc com.amazon.avod/.client.activity.HomeScreenActivity
870:         3432f39 com.amazon.photos/com.amazon.gallery.thor.app.activity.ATCLauncherActivity
881:         fcddf8a com.microsoft.launcher/.setting.FakeSms
887:         fcddf8a com.microsoft.launcher/.setting.FakeSms
899:         2be7ead com.amazon.firelauncher/.Launcher
901:         4653f3a com.amazon.venezia/.CFR.dialog.CFRLauncherActivity
909:         fac1d73 com.amazon.kindle.otter.oobe/.OOBELauncherV2
914:         4a33fe com.amazon.cloud9/org.chromium.chrome.browser.media.AudioLauncherActivity
915:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher (2 filters)
920:         432e86b com.amazon.cloud9/org.chromium.chrome.browser.media.MediaLauncherActivity
931:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher (3 filters)
935:         2d81506 com.amazon.photos/com.amazon.gallery.thor.app.activity.LauncherActivity (22 filters)
957:         bd74963 com.android.vending/com.google.android.finsky.protect.impl.PlayProtectHomeDeepLinkActivity
958:         c5a73e1 com.amazon.cloud9/org.chromium.chrome.browser.DragAndDropLauncherActivity
978:         25d60b7 org.mozilla.firefox/org.mozilla.fenix.HomeActivity
982:         8f4de4 com.audible.application.kindle/com.audible.application.MainLauncher (4 filters)
990:         2d81506 com.amazon.photos/com.amazon.gallery.thor.app.activity.LauncherActivity (22 filters)
1021:         a24d78d com.google.android.inputmethod.latin/com.google.android.apps.inputmethod.latin.sharing.LinkReceivingLauncherActivity
```

### `package/preferred_xml.stdout.txt`

```text
3:     <item name="org.fireosresearch.home.p0/org.fireosresearch.home.HomeActivity">
6:             <cat name="android.intent.category.HOME" />
```

### `window/input.stdout.txt`

```text
454:   FocusedApplication: name='AppWindowToken{1617879 token=Token{ef44140 ActivityRecord{1fb24c3 u0 com.amazon.firelauncher/.Launcher t2}}}', dispatchingTimeout=5000.000ms
455:   FocusedWindow: name='Window{1ac9e16 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}'
464:     4: name='Window{1ac9e16 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}', displayId=0, paused=false, hasFocus=true, hasWallpaper=true, visible=true, canReceiveKeys=true, flags=0x81910120, type=0x00000001, layer=0, frame=[0,0][1200,1920], scale=1.000000, touchableRegion=[0,0][1200,1920], inputFeatures=0x00000000, ownerPid=1963, ownerUid=10120, dispatchingTimeout=5000.000ms
465:     5: name='Window{eb696b1 u0 com.android.launcher3/com.android.quickstep.RecentsActivity}', displayId=0, paused=false, hasFocus=false, hasWallpaper=false, visible=false, canReceiveKeys=false, flags=0x81910120, type=0x00000001, layer=0, frame=[0,0][1200,1920], scale=1.000000, touchableRegion=[0,0][1200,1920], inputFeatures=0x00000000, ownerPid=1948, ownerUid=10075, dispatchingTimeout=5000.000ms
502:     6: channelName='1ac9e16 com.amazon.firelauncher/com.amazon.firelauncher.Launcher (server)', windowName='Window{1ac9e16 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}', status=NORMAL, monitor=false, inputPublisherBlocked=false
505:     7: channelName='eb696b1 com.android.launcher3/com.android.quickstep.RecentsActivity (server)', windowName='Window{eb696b1 u0 com.android.launcher3/com.android.quickstep.RecentsActivity}', status=NORMAL, monitor=false, inputPublisherBlocked=false
```

### `window/processes.stdout.txt`

```text
258: system         420     1 wmt_launcher                wmt_launcher -p /vendor/firmware/
326: u0_a75        1948   348 com.android.launcher3       com.android.launcher3
327: u0_a120       1963   348 com.amazon.firelauncher     com.amazon.firelauncher
386: u0_a178       9104   348 com.microsoft.launcher      com.microsoft.launcher
```


## Small text diffs

### `activity/activities.stdout.txt`

```diff
--- before/activity/activities.stdout.txt

+++ after/activity/activities.stdout.txt

@@ -21,5 +21,5 @@

       mRootProcess=ProcessRecord{49b9f38 1963:com.amazon.firelauncher/u0a120}
       stackId=0
-      hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=2250671 (inactive for 2434s)
+      hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=2250671 (inactive for 2443s)
       * Hist #0: ActivityRecord{1fb24c3 u0 com.amazon.firelauncher/.Launcher t2}
           packageName=com.amazon.firelauncher processName=com.amazon.firelauncher
@@ -43,5 +43,5 @@

            statusBarColor=0
            navigationBarColor=ff000000
-          launchFailed=false launchCount=0 lastLaunchTime=-1h17m41s953ms
+          launchFailed=false launchCount=0 lastLaunchTime=-1h17m51s121ms
           haveState=false icicle=null
           state=RESUMED stopped=false delayedResume=false finishing=false
@@ -50,5 +50,5 @@

           frozenBeforeDestroy=false forceNewConfig=false
           mActivityType=home
-          waitingVisible=false nowVisible=true lastVisibleTime=-1h7m58s70ms
+          waitingVisible=false nowVisible=true lastVisibleTime=-1h8m7s238ms
           resizeMode=RESIZE_MODE_RESIZEABLE
           mLastReportedMultiWindowMode=false mLastReportedPictureInPictureMode=false
@@ -78,5 +78,5 @@

       askedCompatMode=false inRecents=true isAvailable=true
       stackId=2
-      hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=606300 (inactive for 4078s)
+      hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=606300 (inactive for 4087s)
       * Hist #0: ActivityRecord{eb77636 u0 com.android.launcher3/com.android.quickstep.RecentsActivity t26}
           packageName=com.android.launcher3 processName=com.android.launcher3
@@ -100,5 +100,5 @@

            statusBarColor=0
            navigationBarColor=0
-          launchFailed=false launchCount=0 lastLaunchTime=-1h8m0s425ms
+          launchFailed=false launchCount=0 lastLaunchTime=-1h8m9s593ms
           haveState=true icicle=Bundle[mParcelledData.dataSize=560]
           state=STOPPED stopped=true delayedResume=false finishing=false
@@ -107,5 +107,5 @@

           frozenBeforeDestroy=false forceNewConfig=false
           mActivityType=recents
-          waitingVisible=false nowVisible=false lastVisibleTime=-1h8m0s149ms
+          waitingVisible=false nowVisible=false lastVisibleTime=-1h8m9s317ms
           resizeMode=RESIZE_MODE_RESIZEABLE
           mLastReportedMultiWindowMode=false mLastReportedPictureInPictureMode=false
```

### `activity/recents.stdout.txt`

```diff
--- before/activity/recents.stdout.txt

+++ after/activity/recents.stdout.txt

@@ -14,5 +14,5 @@

     mRootProcess=ProcessRecord{49b9f38 1963:com.amazon.firelauncher/u0a120}
     stackId=0
-    hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=2250671 (inactive for 2434s)
+    hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=2250671 (inactive for 2443s)
   * Recent #1: TaskRecord{dd3d92d #26 I=com.android.launcher3/com.android.quickstep.RecentsActivity U=0 StackId=2 sz=1}
     userId=0 effectiveUid=u0a75 mCallingUid=u0a75 mUserSetupComplete=true mCallingPackage=com.android.launcher3
@@ -24,3 +24,3 @@

     askedCompatMode=false inRecents=true isAvailable=true
     stackId=2
-    hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=606300 (inactive for 4078s)
+    hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=606300 (inactive for 4087s)
```

### `activity/top.stdout.txt`

```diff
--- before/activity/top.stdout.txt

+++ after/activity/top.stdout.txt

@@ -22,5 +22,5 @@

     Choreographer:
       mFrameScheduled=false
-      mLastFrameTime=606732 (4078132 ms ago)
+      mLastFrameTime=606732 (4087300 ms ago)
     View Hierarchy:
       DecorView@928f1cf[RecentsActivity]
@@ -103,5 +103,5 @@

     Choreographer:
       mFrameScheduled=false
-      mLastFrameTime=4632326 (52541 ms ago)
+      mLastFrameTime=4687341 (6694 ms ago)
     View Hierarchy:
       DecorView@c990929[Launcher]
```

### `appops/all.stdout.txt`

```diff
--- before/appops/all.stdout.txt

+++ after/appops/all.stdout.txt

@@ -58,187 +58,187 @@

     Package com.amazon.platform.fdrw:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:26:28.449 (-1h26m40s4ms)
+          Access: pers  = 2026-08-03 14:26:28.449 (-1h26m49s115ms)
     Package amazon.fireos:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 09:20:46.628 (-6h32m21s825ms)
+          Access: pers  = 2026-08-03 09:20:46.628 (-6h32m30s936ms)
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2026-03-26 23:43:10.017 (-129d16h9m58s436ms)
+          Reject: pers  = 2026-03-26 23:43:10.017 (-129d16h10m7s547ms)
     Package com.amazon.device.logmanager:
       RUN_IN_BACKGROUND (allow): 
-          Access: pers  = 2026-08-03 14:35:30.788 (-1h17m37s665ms)
+          Access: pers  = 2026-08-03 14:35:30.788 (-1h17m46s776ms)
     Package com.amazon.accessorynotifier:
       RUN_IN_BACKGROUND (allow): 
-          Access: pers  = 2026-08-03 14:35:32.265 (-1h17m36s188ms)
+          Access: pers  = 2026-08-03 14:35:32.265 (-1h17m45s299ms)
     Package com.amazon.android.marketplace:
       WRITE_SETTINGS (default): 
-          Reject: pers  = 2025-12-06 20:49:21.625 (-239d19h3m46s828ms)
+          Reject: pers  = 2025-12-06 20:49:21.625 (-239d19h3m55s939ms)
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-04-06 07:13:25.558 (-119d8h39m42s895ms)
+          Access: pers  = 2026-04-06 07:13:25.558 (-119d8h39m52s6ms)
     Package com.amazon.storagemanager:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-07-10 20:57:29.503 (-23d18h55m38s950ms)
+          Access: pers  = 2026-07-10 20:57:29.503 (-23d18h55m48s61ms)
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2026-08-03 07:45:44.987 (-8h7m23s466ms)
-      READ_EXTERNAL_STORAGE (allow): 
-          Access: pers  = 2026-08-03 07:45:41.642 (-8h7m26s811ms)
+          Reject: pers  = 2026-08-03 07:45:44.987 (-8h7m32s577ms)
+      READ_EXTERNAL_STORAGE (allow): 
+          Access: pers  = 2026-08-03 07:45:41.642 (-8h7m35s922ms)
     Package android:
       COARSE_LOCATION (allow): 
       FINE_LOCATION (allow / switch COARSE_LOCATION=allow): 
-          Access: pers  = 2026-08-03 14:35:23.584 (-1h17m44s869ms)
+          Access: pers  = 2026-08-03 14:35:23.584 (-1h17m53s980ms)
       READ_CALENDAR (allow): 
-          Access: pers  = 2026-08-03 14:35:28.221 (-1h17m40s232ms)
+          Access: pers  = 2026-08-03 14:35:28.221 (-1h17m49s343ms)
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:29:54.943 (-1h23m13s510ms)
+          Access: pers  = 2026-08-03 14:29:54.943 (-1h23m22s621ms)
       AUDIO_MEDIA_VOLUME (allow): 
-          Access: pers  = 2026-08-01 21:11:23.169 (-1d18h41m45s284ms)
-      WAKE_LOCK (allow): 
-          Access: pers  = 2026-08-03 15:52:21.338 (-47s115ms)
-                  fg    = 2026-04-11 03:58:41.049 (-114d11h54m27s404ms)
+          Access: pers  = 2026-08-01 21:11:23.169 (-1d18h41m54s395ms)
+      WAKE_LOCK (allow): 
+          Access: pers  = 2026-08-03 15:52:21.338 (-56s226ms)
+                  fg    = 2026-04-11 03:58:41.049 (-114d11h54m36s515ms)
           duration=+2ms
       MONITOR_LOCATION (allow / switch COARSE_LOCATION=allow): 
-          Access: pers  = 2026-08-03 14:35:23.577 (-1h17m44s876ms)
-                  fg    = 2026-04-11 03:58:41.049 (-114d11h54m27s404ms)
-          Running start at: +1h17m43s883ms
+          Access: pers  = 2026-08-03 14:35:23.577 (-1h17m53s987ms)
+                  fg    = 2026-04-11 03:58:41.049 (-114d11h54m36s515ms)
+          Running start at: +1h17m52s994ms
           startNesting=1
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2026-08-03 15:52:10.024 (-58s429ms)
+          Reject: pers  = 2026-08-03 15:53:09.265 (-8s299ms)
       TURN_ON_SCREEN (allow): 
-          Access: pers  = 2026-07-10 22:35:34.059 (-23d17h17m34s394ms)
+          Access: pers  = 2026-07-10 22:35:34.059 (-23d17h17m43s505ms)
     Package com.android.providers.settings:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2025-12-06 20:11:38.894 (-239d19h41m29s559ms)
+          Access: pers  = 2025-12-06 20:11:38.894 (-239d19h41m38s670ms)
     Package com.android.keychain:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2025-12-07 15:30:49.435 (-239d0h22m19s18ms)
+          Access: pers  = 2025-12-07 15:30:49.435 (-239d0h22m28s129ms)
     Package com.amazon.device.sale.service:
       RUN_IN_BACKGROUND (allow): 
-          Access: pers  = 2026-08-03 14:35:42.055 (-1h17m26s398ms)
+          Access: pers  = 2026-08-03 14:35:42.055 (-1h17m35s509ms)
     Package com.android.settings:
       WRITE_SETTINGS (default): 
-          Reject: pers  = 2026-08-01 21:54:35.634 (-1d17h58m32s819ms)
+          Reject: pers  = 2026-08-01 21:54:35.634 (-1d17h58m41s930ms)
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2026-08-03 12:07:40.636 (-3h45m27s817ms)
+          Reject: pers  = 2026-08-03 12:07:40.636 (-3h45m36s928ms)
       TOAST_WINDOW (allow): 
-          Access: pers  = 2025-12-07 16:06:55.266 (-238d23h46m13s187ms)
+          Access: pers  = 2025-12-07 16:06:55.266 (-238d23h46m22s298ms)
           duration=+4s550ms
     Package android.amazon.perm:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2025-12-06 19:11:18.089 (-239d20h41m50s364ms)
+          Access: pers  = 2025-12-06 19:11:18.089 (-239d20h41m59s475ms)
     Package com.android.wallpaperbackup:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:32:08.417 (-1h21m0s36ms)
+          Access: pers  = 2026-08-03 14:32:08.417 (-1h21m9s147ms)
     Package com.android.location.fused:
       COARSE_LOCATION (allow): 
       FINE_LOCATION (allow / switch COARSE_LOCATION=allow): 
-          Access: pers  = 2025-12-06 18:57:45.955 (-239d20h55m22s498ms)
+          Access: pers  = 2025-12-06 18:57:45.955 (-239d20h55m31s609ms)
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:35:13.887 (-1h17m54s566ms)
+          Access: pers  = 2026-08-03 14:35:13.887 (-1h18m3s677ms)
       MONITOR_LOCATION (allow / switch COARSE_LOCATION=allow): 
-          Access: pers  = 2025-12-06 19:03:04.992 (-239d20h50m3s461ms)
+          Access: pers  = 2025-12-06 19:03:04.992 (-239d20h50m12s572ms)
           duration=+5m20s391ms
     Package com.amazon.settings:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 07:45:33.063 (-8h7m35s390ms)
+          Access: pers  = 2026-08-03 07:45:33.063 (-8h7m44s501ms)
       TOAST_WINDOW (allow): 
-          Access: pers  = 2026-07-10 21:04:18.363 (-23d18h48m50s90ms)
+          Access: pers  = 2026-07-10 21:04:18.363 (-23d18h48m59s201ms)
           duration=+5s388ms
     Package com.amazon.shpm:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 09:19:52.283 (-6h33m16s170ms)
+          Access: pers  = 2026-08-03 09:19:52.283 (-6h33m25s281ms)
     Package com.amazon.fireos.cirruscloud:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:33:40.524 (-1h19m27s929ms)
+          Access: pers  = 2026-08-03 14:33:40.524 (-1h19m37s40ms)
   Uid 1002:
     state=cch  
     Package com.android.bluetooth:
       WAKE_LOCK (allow): 
-          Access: pers  = 2025-12-06 18:56:41.294 (-239d20h56m27s159ms)
-                  bg    = 2025-12-06 18:56:41.291 (-239d20h56m27s162ms)
+          Access: pers  = 2025-12-06 18:56:41.294 (-239d20h56m36s270ms)
+                  bg    = 2025-12-06 18:56:41.291 (-239d20h56m36s273ms)
           duration=+10ms
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2025-12-06 18:56:24.496 (-239d20h56m43s957ms)
-      READ_EXTERNAL_STORAGE (allow): 
-          Access: pers  = 2025-12-06 18:56:28.924 (-239d20h56m39s529ms)
-                  cch   = 2025-12-06 18:56:23.700 (-239d20h56m44s753ms)
-      WRITE_EXTERNAL_STORAGE (allow): 
-          Access: pers  = 2025-12-06 18:56:28.924 (-239d20h56m39s529ms)
-                  cch   = 2025-12-06 18:56:23.700 (-239d20h56m44s753ms)
+          Reject: pers  = 2025-12-06 18:56:24.496 (-239d20h56m53s68ms)
+      READ_EXTERNAL_STORAGE (allow): 
+          Access: pers  = 2025-12-06 18:56:28.924 (-239d20h56m48s640ms)
+                  cch   = 2025-12-06 18:56:23.700 (-239d20h56m53s864ms)
+      WRITE_EXTERNAL_STORAGE (allow): 
+          Access: pers  = 2025-12-06 18:56:28.924 (-239d20h56m48s640ms)
+                  cch   = 2025-12-06 18:56:23.700 (-239d20h56m53s864ms)
   Uid 1041:
     state=cch  
     Package audioserver:
       WAKE_LOCK (allow): 
-          Access: cch   = 2026-08-03 14:44:54.796 (-1h8m13s657ms)
+          Access: cch   = 2026-08-03 14:44:54.796 (-1h8m22s768ms)
           duration=+2s877ms
       GET_USAGE_STATS (default): 
-          Reject: cch   = 2026-08-03 14:35:19.609 (-1h17m48s844ms)
+          Reject: cch   = 2026-08-03 14:35:19.609 (-1h17m57s955ms)
   Uid 1068:
     state=pers 
     Package com.android.se:
       READ_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2026-08-03 14:35:24.585 (-1h17m43s868ms)
-      WRITE_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2026-08-03 14:35:24.585 (-1h17m43s868ms)
+          Access: cch   = 2026-08-03 14:35:24.585 (-1h17m52s979ms)
+      WRITE_EXTERNAL_STORAGE (allow): 
+          Access: cch   = 2026-08-03 14:35:24.585 (-1h17m52s979ms)
   Uid 2000:
     state=cch  
     Package com.android.shell:
       AUDIO_RING_VOLUME (allow): 
-          Access: cch   = 2025-12-07 15:02:29.916 (-239d0h50m38s537ms)
+          Access: cch   = 2025-12-07 15:02:29.916 (-239d0h50m47s648ms)
   Uid u0a5:
     state=cch  
     Package com.ivona.orchestrator:
       READ_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2025-12-07 16:06:13.286 (-238d23h46m55s167ms)
-      WRITE_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2025-12-07 16:06:13.286 (-238d23h46m55s167ms)
-      RUN_IN_BACKGROUND (allow): 
-          Access: bg    = 2025-12-06 19:02:54.041 (-239d20h50m14s412ms)
-                  cch   = 2025-12-06 19:02:51.359 (-239d20h50m17s94ms)
+          Access: cch   = 2025-12-07 16:06:13.286 (-238d23h47m4s278ms)
+      WRITE_EXTERNAL_STORAGE (allow): 
+          Access: cch   = 2025-12-07 16:06:13.286 (-238d23h47m4s278ms)
+      RUN_IN_BACKGROUND (allow): 
+          Access: bg    = 2025-12-06 19:02:54.041 (-239d20h50m23s523ms)
+                  cch   = 2025-12-06 19:02:51.359 (-239d20h50m26s205ms)
   Uid u0a6:
     state=cch  
     Package com.amazon.dp.fbcontacts:
       READ_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2026-08-03 14:35:34.262 (-1h17m34s191ms)
-      WRITE_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2026-08-03 14:35:34.262 (-1h17m34s191ms)
-      RUN_IN_BACKGROUND (allow): 
-          Access: cch   = 2026-08-03 14:35:34.261 (-1h17m34s192ms)
+          Access: cch   = 2026-08-03 14:35:34.262 (-1h17m43s302ms)
+      WRITE_EXTERNAL_STORAGE (allow): 
+          Access: cch   = 2026-08-03 14:35:34.262 (-1h17m43s302ms)
+      RUN_IN_BACKGROUND (allow): 
+          Access: cch   = 2026-08-03 14:35:34.261 (-1h17m43s303ms)
   Uid u0a7:
     state=fg   
     Package com.amazon.client.metrics:
       WAKE_LOCK (allow): 
-          Access: fgsvc = 2026-08-03 14:35:44.007 (-1h17m24s446ms)
-                  fg    = 2026-08-03 15:42:06.862 (-11m1s591ms)
+          Access: fgsvc = 2026-08-03 14:35:44.007 (-1h17m33s557ms)
+                  fg    = 2026-08-03 15:42:06.862 (-11m10s702ms)
           duration=+934ms
       READ_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2026-08-03 14:35:23.600 (-1h17m44s853ms)
-      WRITE_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2026-08-03 14:35:23.600 (-1h17m44s853ms)
+          Access: cch   = 2026-08-03 14:35:23.600 (-1h17m53s964ms)
+      WRITE_EXTERNAL_STORAGE (allow): 
+          Access: cch   = 2026-08-03 14:35:23.600 (-1h17m53s964ms)
   Uid u0a9:
     state=bg   
     pendingState=cch  
-    pendingStateCommitTime=-5m0s627ms
+    pendingStateCommitTime=-5m9s738ms
     Package com.amazon.diode:
       READ_EXTERNAL_STORAGE (allow): 
-          Access: bg    = 2026-03-26 23:25:18.707 (-129d16h27m49s746ms)
-                  cch   = 2026-08-03 14:35:34.035 (-1h17m34s418ms)
-      WRITE_EXTERNAL_STORAGE (allow): 
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
+TAKE_AUDIO_FOCUS: allow; time=+239d20h41m42s196ms ago
+READ_EXTERNAL_STORAGE: allow; time=+1h17m50s975ms ago
+WRITE_EXTERNAL_STORAGE: allow; time=+1h17m50s975ms ago
+REQUEST_DELETE_PACKAGES: allow; time=+238d23h48m43s921ms ago
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
+FINE_LOCATION: allow; time=+39s243ms ago
+READ_EXTERNAL_STORAGE: allow; time=+39s338ms ago
+WRITE_EXTERNAL_STORAGE: allow; time=+39s338ms ago
+BIND_ACCESSIBILITY_SERVICE: allow; time=+7s444ms ago
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

### `metadata.tsv`

```diff
--- before/metadata.tsv

+++ after/metadata.tsv

@@ -1,3 +1,3 @@

-test_id=PHASE3C-PREFERRED-P0-02-before
+test_id=PHASE3C-PREFERRED-P0-02-after_preferred
 serial=G001LT0511550CFT
-timestamp_utc=2026-08-03T07:53:04Z
+timestamp_utc=2026-08-03T07:53:14Z
```

### `overlay/dump.stdout.txt`

```diff
--- before/overlay/dump.stdout.txt

+++ after/overlay/dump.stdout.txt

@@ -46,3 +46,3 @@

 Default overlays: 
 PackageInfo cache
-    7 package(s)
+    8 package(s)
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

@@ -322,17 +322,4 @@

         c2d0578 com.amazon.firelauncher/.search.SearchIndexingProvider filter dddb74c
           Action: "android.content.action.SEARCH_INDEXABLES_PROVIDER"
-
-Preferred Activities User 0:
-  Non-Data Actions:
-      android.intent.action.MAIN:
-        64d16ed com.amazon.firelauncher/.Launcher
-         mMatch=0x100000 mAlways=true
-          Selected from:
-            com.amazon.firelauncher/.Launcher
-            com.microsoft.launcher/.Launcher
-            com.android.settings/.FallbackHome
-          Action: "android.intent.action.MAIN"
-          Category: "android.intent.category.HOME"
-          Category: "android.intent.category.DEFAULT"
 
 Permissions:
@@ -743,4 +730,6 @@

       amazon.aosp.permission.INTERACT_ACROSS_USERS_FULL
       com.amazon.permission.INTERACT_ACROSS_USERS_FULL
+      amazon.aosp.permission.INTERACT_ACROSS_USERS_FULL
+      com.amazon.permission.INTERACT_ACROSS_USERS_FULL
     install permissions:
       com.amazon.firelauncher.cardproducer.utils.HOST_APP_COLD_START_RECEIVER: granted=true
@@ -851,9 +840,9 @@

 
 Package Changes:
-  Sequence number=7
+  Sequence number=8
   User 0:
     seq=0, package=org.fireosresearch.home.p100
     seq=4, package=com.google.android.gms
-    seq=6, package=org.fireosresearch.home.p0
+    seq=7, package=org.fireosresearch.home.p0
 
 
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

### `summary.md`

```diff
--- before/summary.md

+++ after/summary.md

@@ -1,7 +1,7 @@

 # Phase 3C state snapshot
 
-- Test ID: PHASE3C-PREFERRED-P0-02-before
+- Test ID: PHASE3C-PREFERRED-P0-02-after_preferred
 - Serial: G001LT0511550CFT
-- Timestamp UTC: 2026-08-03T07:53:08Z
+- Timestamp UTC: 2026-08-03T07:53:17Z
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
-    Last logged in: +1h17m43s91ms ago
+    Last logged in: +1h17m52s259ms ago
     Last logged in fingerprint: Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys
-    Start time: +1h17m46s725ms ago
-    Unlock time: +1h17m42s191ms ago
+    Start time: +1h17m55s893ms ago
+    Unlock time: +1h17m51s359ms ago
     Has profile owner: true
     Restrictions:
```

### `window/input.stdout.txt`

```diff
--- before/window/input.stdout.txt

+++ after/window/input.stdout.txt

@@ -468,14 +468,14 @@

     0: 'WindowManager (server)'
   RecentQueue: length=10
-    MotionEvent, age=2271202.8ms
-    MotionEvent, age=2271201.8ms
-    MotionEvent, age=2271137.8ms
-    MotionEvent, age=2271134.8ms
-    MotionEvent, age=2271125.8ms
-    MotionEvent, age=2270602.0ms
-    MotionEvent, age=2270582.8ms
-    MotionEvent, age=2270559.0ms
-    MotionEvent, age=2270522.8ms
-    MotionEvent, age=2014270.9ms
+    MotionEvent, age=2280350.0ms
+    MotionEvent, age=2280349.2ms
+    MotionEvent, age=2280285.0ms
+    MotionEvent, age=2280282.0ms
+    MotionEvent, age=2280273.2ms
+    MotionEvent, age=2279749.2ms
+    MotionEvent, age=2279730.0ms
+    MotionEvent, age=2279706.2ms
+    MotionEvent, age=2279670.0ms
+    MotionEvent, age=2023418.1ms
   PendingEvent: <none>
   InboundQueue: <empty>
```

### `window/processes.stdout.txt`

```diff
--- before/window/processes.stdout.txt

+++ after/window/processes.stdout.txt

@@ -385,3 +385,3 @@

 root          9063     2 [kbase_event]               [kbase_event]
 u0_a178       9104   348 com.microsoft.launcher      com.microsoft.launcher
-shell         9282   428 ps                          ps -A -o USER,PID,PPID,NAME,ARGS
+shell         9601   428 ps                          ps -A -o USER,PID,PPID,NAME,ARGS
```
