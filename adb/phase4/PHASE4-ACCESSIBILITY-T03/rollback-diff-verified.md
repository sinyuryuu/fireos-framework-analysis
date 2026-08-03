# Phase 3C snapshot comparison

- Before: `adb/phase4/PHASE4-ACCESSIBILITY-T03/before`
- After: `adb/phase4/PHASE4-ACCESSIBILITY-T03/after_rollback`
- Before files: `175`
- After files: `175`
- Changed files: `21`

## Changed files

- `activity/activities.stdout.txt` — changed
- `activity/recents.stdout.txt` — changed
- `activity/top.stdout.txt` — changed
- `appops/all.stdout.txt` — changed
- `appops/firelauncher.stdout.txt` — changed
- `appops/microsoft.stdout.txt` — changed
- `metadata.tsv` — changed
- `overlay/dump.stdout.txt` — changed
- `package/all_packages.stdout.txt` — changed
- `package/firelauncher.stdout.txt` — changed
- `package/full_dump.stdout.txt` — changed
- `package/home_query_cmd.stdout.txt` — changed
- `package/home_query_pm.stdout.txt` — changed
- `package/persistent_preferred.stdout.txt` — changed
- `package/preferred_activities.stdout.txt` — changed
- `settings/secure.stdout.txt` — changed
- `summary.md` — changed
- `users/dumpsys_user.stdout.txt` — changed
- `window/input.stdout.txt` — changed
- `window/processes.stdout.txt` — changed
- `window/windows.stdout.txt` — changed

## Focused evidence

### `activity/activities.stdout.txt`

```text
12:     * TaskRecord{226d575 #36 I=com.android.launcher3/com.android.quickstep.RecentsActivity U=0 StackId=8 sz=1}
13:       userId=0 effectiveUid=u0a75 mCallingUid=u0a75 mUserSetupComplete=true mCallingPackage=com.android.launcher3
14:       intent={act=android.intent.action.MAIN cat=[android.intent.category.DEFAULT] flg=0x10800000 cmp=com.android.launcher3/com.android.quickstep.RecentsActivity}
15:       realActivity=com.android.launcher3/com.android.quickstep.RecentsActivity
18:       Activities=[ActivityRecord{7620f3f u0 com.android.launcher3/com.android.quickstep.RecentsActivity t36}]
22:       * Hist #0: ActivityRecord{7620f3f u0 com.android.launcher3/com.android.quickstep.RecentsActivity t36}
23:           packageName=com.android.launcher3 processName=com.android.launcher3
24:           launchedFromUid=10075 launchedFromPackage=com.android.launcher3 userId=0
25:           app=ProcessRecord{205196e 1923:com.android.launcher3/u0a75}
26:           Intent { act=android.intent.action.MAIN cat=[android.intent.category.DEFAULT] flg=0x10800000 cmp=com.android.launcher3/com.android.quickstep.RecentsActivity }
27:           frontOfTask=true task=TaskRecord{226d575 #36 I=com.android.launcher3/com.android.quickstep.RecentsActivity U=0 StackId=8 sz=1}
29:           realActivity=com.android.launcher3/com.android.quickstep.RecentsActivity
30:           baseDir=/system/priv-app/com.android.launcher3/com.android.launcher3.apk
31:           dataDir=/data/user/0/com.android.launcher3
56:       TaskRecord{226d575 #36 I=com.android.launcher3/com.android.quickstep.RecentsActivity U=0 StackId=8 sz=1}
57:         Run #0: ActivityRecord{7620f3f u0 com.android.launcher3/com.android.quickstep.RecentsActivity t36}
59:     mResumedActivity: ActivityRecord{7620f3f u0 com.android.launcher3/com.android.quickstep.RecentsActivity t36}
61:   Stack #0: type=home mode=fullscreen
70:     * TaskRecord{38663ed #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
72:       affinity=10120:com.amazon.firelauncher
73:       intent={act=android.intent.action.MAIN cat=[android.intent.category.HOME] flg=0x10000100 cmp=com.amazon.firelauncher/.Launcher}
74:       realActivity=com.amazon.firelauncher/.Launcher
77:       Activities=[ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}]
79:       mRootProcess=ProcessRecord{8f8f222 1942:com.amazon.firelauncher/u0a120}
82:       * Hist #0: ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}
83:           packageName=com.amazon.firelauncher processName=com.amazon.firelauncher
85:           app=ProcessRecord{8f8f222 1942:com.amazon.firelauncher/u0a120}
86:           Intent { act=android.intent.action.MAIN cat=[android.intent.category.HOME] flg=0x10000100 cmp=com.amazon.firelauncher/.Launcher }
87:           frontOfTask=true task=TaskRecord{38663ed #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
88:           taskAffinity=10120:com.amazon.firelauncher
89:           realActivity=com.amazon.firelauncher/.Launcher
90:           baseDir=/system/priv-app/com.amazon.firelauncher/com.amazon.firelauncher.apk
91:           dataDir=/data/user/0/com.amazon.firelauncher
92:           stateNotNeeded=false componentSpecified=false mActivityType=home
96:            mOverrideConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
97:           CurrentConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
98:           OverrideConfiguration={0.0 ?mcc?mnc ?localeList ?layoutDir ?swdp ?wdp ?hdp ?density ?lsize ?long ?ldr ?wideColorGamut ?orien ?uimode ?night ?touch ?keyb/?/? ?nav/? winConfig={ mBounds=Rect(0, 0 - 0, 0) mAppBounds=null mWindowingMode=undefined mActivityType=home}}
109:           mActivityType=home
115:       TaskRecord{38663ed #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
116:         Run #0: ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}
118:     mLastPausedActivity: ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}
120:   ResumedActivity: ActivityRecord{7620f3f u0 com.android.launcher3/com.android.quickstep.RecentsActivity t36}
125:    mHomeStack=ActivityStack{411a4b3 stackId=0 type=home mode=fullscreen visible=false translucent=true, 1 tasks}
127:   isHomeRecentsComponent=false  KeyguardController:
```

### `activity/recents.stdout.txt`

```text
3: mRecentsComponent=ComponentInfo{com.android.launcher3/com.android.quickstep.RecentsActivity}
5:   * Recent #0: TaskRecord{226d575 #36 I=com.android.launcher3/com.android.quickstep.RecentsActivity U=0 StackId=8 sz=1}
6:     userId=0 effectiveUid=u0a75 mCallingUid=u0a75 mUserSetupComplete=true mCallingPackage=com.android.launcher3
7:     intent={act=android.intent.action.MAIN cat=[android.intent.category.DEFAULT] flg=0x10800000 cmp=com.android.launcher3/com.android.quickstep.RecentsActivity}
8:     realActivity=com.android.launcher3/com.android.quickstep.RecentsActivity
11:     Activities=[ActivityRecord{7620f3f u0 com.android.launcher3/com.android.quickstep.RecentsActivity t36}]
15:   * Recent #1: TaskRecord{38663ed #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
17:     affinity=10120:com.amazon.firelauncher
18:     intent={act=android.intent.action.MAIN cat=[android.intent.category.HOME] flg=0x10000100 cmp=com.amazon.firelauncher/.Launcher}
19:     realActivity=com.amazon.firelauncher/.Launcher
22:     Activities=[ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}]
24:     mRootProcess=ProcessRecord{8f8f222 1942:com.amazon.firelauncher/u0a120}
```

### `activity/top.stdout.txt`

```text
1: TASK 10120:com.amazon.firelauncher id=2 userId=0
2:   ACTIVITY com.amazon.firelauncher/.Launcher 873be7c pid=1942
6:       mCurrentConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
43:       DecorView@b17a258[Launcher]
46:             com.amazon.firelauncher.appsgrid.ui.drag.DragLayer{eea9017 V.E...... .......D 0,0-1200,1920 #7f090336 app:id/magazine_container}
49:               com.amazon.firelauncher.view.EnhancedViewPager{fe7ec22 VFED..... .......D 0,0-1200,1920 #7f090379 app:id/pager}
50:                 com.amazon.firelauncher.appsgrid.ui.ScrollableMainView{3fe16b3 V.E...... .......D 0,0-1200,1920}
51:                   com.amazon.firelauncher.appsgrid.ui.GradientScrimFrameLayout{f8c6470 V.E...... .......D 0,0-1200,1920}
52:                     com.amazon.firelauncher.appsgrid.ui.GridView{40113e9 VFED..... .......D 0,0-1200,1920 #7f09027a app:id/favorites_page}
55:                           com.amazon.firelauncher.view.LoadingDotsView{341d7dc V.E...... ......I. 0,0-0,0 #7f09032c app:id/loading_dots}
144:                 com.amazon.firelauncher.view.ScrollObservableContainer{c2ba92b V.E...... .......D 1200,0-2400,1920}
145:                   com.amazon.firelauncher.view.ChannelBackgroundView{e645188 V.ED..... ........ 0,0-1200,1920 #7f0900ef app:id/background_view}
146:                   com.amazon.firelauncher.view.ScrollingLinearRecyclerView{1f7ee7f VFED..... .......D 0,0-1200,1920 #7f09039e app:id/recycler}
164:                         com.amazon.firelauncher.view.LoadingDotsView{48d331b V.E...... ......I. 0,0-0,0 #7f09032c app:id/loading_dots}
177:                         com.amazon.firelauncher.view.NavTabView{3cadc6b VFE...C.. ......ID 0,0-240,84}
180:                         com.amazon.firelauncher.view.NavTabView{6e2a0da VFE...C.. ..S...ID 240,0-431,84}
183:                         com.amazon.firelauncher.view.NavTabView{dd1fa01 VFE...C.. ......ID 431,0-719,84}
186:                 com.amazon.firelauncher.view.SearchWidgetHostLayout{28fa694 V.E...... .......D -18,-6-1218,192 #7f0903ba app:id/search_bar_widget}
187:                   com.amazon.firelauncher.search.SearchAppWidgetHostView{663353d V.E...... R......D 0,0-1236,198}
203:                     com.amazon.firelauncher.appsgrid.ui.FolderView{8f8b5 VFED..... ......I. 0,0-0,0 #7f090288 app:id/folder_grid}
208:       Message 0: { when=+4s809ms callback=com.amazon.firelauncher.magazine.MagazineController$1 target=android.view.ViewRootImpl$ViewRootHandler isAsync=false }
215:       context: com.amazon.firelauncher.Launcher@b21ee9c
216:       client: com.amazon.firelauncher.Launcher@b21ee9c
258:         mSavedViewState={2131296495=com.amazon.firelauncher.view.ChannelBackgroundView$SavedState@81f5a4b, 2131296688=android.view.AbsSavedState$1@5993cf2, 2131296689=android.view.AbsSavedState$1@5993cf2, 2131296690=android.view.AbsSavedState$1@5993cf2, 2131296941=android.view.AbsSavedState$1@5993cf2, 2131296946=android.view.AbsSavedState$1@5993cf2, 2131297061=android.view.AbsSavedState$1@5993cf2, 2131297068=android.view.AbsSavedState$1@5993cf2, 2131297072=android.view.AbsSavedState$1@5993cf2, 2131297073=android.view.AbsSavedState$1@5993cf2, 2131297074=android.view.AbsSavedState$1@5993cf2, 2131297075=android.view.AbsSavedState$1@5993cf2, 2131297076=android.view.AbsSavedState$1@5993cf2, 2131297182=androidx.recyclerview.widget.RecyclerView$SavedState@3de7c28, 2131297186=android.view.AbsSavedState$1@5993cf2, 2131297263=android.view.AbsSavedState$1@5993cf2, 2131297407=android.view.AbsSavedState$1@5993cf2}
259:         mContainer=com.amazon.firelauncher.view.EnhancedViewPager{fe7ec22 VFED..... .......D 0,0-1200,1920 #7f090379 app:id/pager}
260:         mView=com.amazon.firelauncher.view.ScrollObservableContainer{c2ba92b V.E...... .......D 1200,0-2400,1920}
277:         mContainer=com.amazon.firelauncher.view.EnhancedViewPager{fe7ec22 VFED..... .......D 0,0-1200,1920 #7f090379 app:id/pager}
296:         mContainer=com.amazon.firelauncher.view.EnhancedViewPager{fe7ec22 VFED..... .......D 0,0-1200,1920 #7f090379 app:id/pager}
297:         mView=com.amazon.firelauncher.appsgrid.ui.ScrollableMainView{3fe16b3 V.E...... .......D 0,0-1200,1920}
317:   ACTIVITY com.android.launcher3/com.android.quickstep.RecentsActivity 7620f3f pid=1923
```

### `appops/all.stdout.txt`

```text
702:     Package com.android.launcher3:
990:     Package com.amazon.firelauncher:
1297:     Package com.microsoft.launcher:
```

### `package/all_packages.stdout.txt`

```text
36: package:/system/priv-app/com.amazon.firelauncher/com.amazon.firelauncher.apk=com.amazon.firelauncher
73: package:/data/app/com.microsoft.launcher-bTT5nKLHn89n_d_gJojj-Q==/base.apk=com.microsoft.launcher
75: package:/system/priv-app/com.android.launcher3/com.android.launcher3.apk=com.android.launcher3
183: package:/system/priv-app/com.amazon.tv.launcher/com.amazon.tv.launcher.apk=com.amazon.tv.launcher
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
67:     priority=-1000 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
69:       name=com.android.settings.FallbackHome
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
67:     priority=-1000 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
69:       name=com.android.settings.FallbackHome
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

### `settings/secure.stdout.txt`

```text
18: LAUNCHER_FTUE_FLAG=amzn1.account.AF3AIQ5HTDU5DJYSLOSPPGKHUUZA
102: enable_launcher_tutorial=1
106: enabled_notification_listeners=com.amazon.kindle.otter.oobe/com.amazon.kindle.otter.oobe.modules.settings.wifi.CaptivePortalActivityLauncher:com.amazon.alexa.multimodal.gemini/com.amazon.knight.blink.BlinkNotificationListenerService:com.amazon.settings/com.amazon.settings.wifi.CaptivePortalActivityLauncher
112: firelauncher_appsgrid_version=2
130: launcher_zero_margin_enabled=1
212: smart_home_lock_screen_access=0
220: sysui_nav_bar=left[1WC],;back[1WC],key(130:file:///storage/emulated/0/NavIcons0/home.png)[1WC],recent[1WC];right[1WC]
233: tb_custom_launcher=com.teslacoilsw.launcher
```

### `window/input.stdout.txt`

```text
454:   FocusedApplication: name='AppWindowToken{c1e3d55 token=Token{f1fe00c ActivityRecord{7620f3f u0 com.android.launcher3/com.android.quickstep.RecentsActivity t36}}}', dispatchingTimeout=5000.000ms
455:   FocusedWindow: name='Window{ced5e7a u0 com.android.launcher3/com.android.quickstep.RecentsActivity}'
462:     4: name='Window{ced5e7a u0 com.android.launcher3/com.android.quickstep.RecentsActivity}', displayId=0, paused=false, hasFocus=true, hasWallpaper=true, visible=true, canReceiveKeys=true, flags=0x81910120, type=0x00000001, layer=0, frame=[0,0][1200,1920], scale=1.000000, touchableRegion=[0,0][1200,1920], inputFeatures=0x00000000, ownerPid=1923, ownerUid=10075, dispatchingTimeout=5000.000ms
463:     5: name='Window{80793f7 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher EXITING}', displayId=0, paused=false, hasFocus=false, hasWallpaper=false, visible=false, canReceiveKeys=false, flags=0x81910120, type=0x00000001, layer=0, frame=[0,0][1200,1920], scale=1.000000, touchableRegion=[0,0][1200,1920], inputFeatures=0x00000000, ownerPid=1942, ownerUid=10120, dispatchingTimeout=5000.000ms
500:     6: channelName='80793f7 com.amazon.firelauncher/com.amazon.firelauncher.Launcher (server)', windowName='Window{80793f7 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher EXITING}', status=NORMAL, monitor=false, inputPublisherBlocked=false
506:     8: channelName='ced5e7a com.android.launcher3/com.android.quickstep.RecentsActivity (server)', windowName='Window{ced5e7a u0 com.android.launcher3/com.android.quickstep.RecentsActivity}', status=NORMAL, monitor=false, inputPublisherBlocked=false
```

### `window/processes.stdout.txt`

```text
259: system         422     1 wmt_launcher                wmt_launcher -p /vendor/firmware/
328: u0_a75        1923   352 com.android.launcher3       com.android.launcher3
329: u0_a120       1942   352 com.amazon.firelauncher     com.amazon.firelauncher
```

### `window/windows.stdout.txt`

```text
124:   Window #4 Window{ced5e7a u0 com.android.launcher3/com.android.quickstep.RecentsActivity}:
126:     mOwnerUid=10075 mShowToOwnerOnly=true package=com.android.launcher3 appop=NONE
133:     mToken=AppWindowToken{c1e3d55 token=Token{f1fe00c ActivityRecord{7620f3f u0 com.android.launcher3/com.android.quickstep.RecentsActivity t36}}}
134:     mAppToken=AppWindowToken{c1e3d55 token=Token{f1fe00c ActivityRecord{7620f3f u0 com.android.launcher3/com.android.quickstep.RecentsActivity t36}}}
150:     WindowStateAnimator{2ce5dbd com.android.launcher3/com.android.quickstep.RecentsActivity}:
151:       mSurface=Surface(name=com.android.launcher3/com.android.quickstep.RecentsActivity)/@0xea505d5
157:   Window #5 Window{80793f7 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher EXITING}:
159:     mOwnerUid=10120 mShowToOwnerOnly=true package=com.amazon.firelauncher appop=NONE
166:     mToken=AppWindowToken{e63cf5a token=Token{d3a1305 ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}}}
167:     mAppToken=AppWindowToken{e63cf5a token=Token{d3a1305 ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}}}
172:     mFullConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
173:     mLastReportedConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
183:     WindowStateAnimator{bffb519 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}:
184:       mSurface=Surface(name=com.amazon.firelauncher/com.amazon.firelauncher.Launcher)/@0xafab378
225:   mCurrentFocus=Window{ced5e7a u0 com.android.launcher3/com.android.quickstep.RecentsActivity}
226:   mFocusedApp=AppWindowToken{c1e3d55 token=Token{f1fe00c ActivityRecord{7620f3f u0 com.android.launcher3/com.android.quickstep.RecentsActivity t36}}}
238:   mWallpaperTarget=Window{ced5e7a u0 com.android.launcher3/com.android.quickstep.RecentsActivity}
239:   mPrevWallpaperTarget=Window{80793f7 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher EXITING}
253:     mLastOpeningApp=AppWindowToken{c1e3d55 token=Token{f1fe00c ActivityRecord{7620f3f u0 com.android.launcher3/com.android.quickstep.RecentsActivity t36}}}
254:     mLastClosingApp=AppWindowToken{e63cf5a token=Token{d3a1305 ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}}}
```


## Small text diffs

### `activity/activities.stdout.txt`

```diff
--- before/activity/activities.stdout.txt

+++ after/activity/activities.stdout.txt

@@ -1,8 +1,66 @@

 ACTIVITY MANAGER ACTIVITIES (dumpsys activity activities)
 Display #0 (activities from top to bottom):
+
+  Stack #8: type=recents mode=fullscreen
+  isSleeping=false
+  mBounds=Rect(0, 0 - 0, 0)
+    Task id #36
+    mBounds=Rect(0, 0 - 0, 0)
+    mMinWidth=-1
+    mMinHeight=-1
+    mLastNonFullscreenBounds=null
+    * TaskRecord{226d575 #36 I=com.android.launcher3/com.android.quickstep.RecentsActivity U=0 StackId=8 sz=1}
+      userId=0 effectiveUid=u0a75 mCallingUid=u0a75 mUserSetupComplete=true mCallingPackage=com.android.launcher3
+      intent={act=android.intent.action.MAIN cat=[android.intent.category.DEFAULT] flg=0x10800000 cmp=com.android.launcher3/com.android.quickstep.RecentsActivity}
+      realActivity=com.android.launcher3/com.android.quickstep.RecentsActivity
+      autoRemoveRecents=false isPersistable=false numFullscreen=1 activityType=3
+      rootWasReset=false mNeverRelinquishIdentity=true mReuseTask=false mLockTaskAuth=LOCK_TASK_AUTH_PINNABLE
+      Activities=[ActivityRecord{7620f3f u0 com.android.launcher3/com.android.quickstep.RecentsActivity t36}]
+      askedCompatMode=false inRecents=true isAvailable=true
+      stackId=8
+      hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=6005216 (inactive for 3s)
+      * Hist #0: ActivityRecord{7620f3f u0 com.android.launcher3/com.android.quickstep.RecentsActivity t36}
+          packageName=com.android.launcher3 processName=com.android.launcher3
+          launchedFromUid=10075 launchedFromPackage=com.android.launcher3 userId=0
+          app=ProcessRecord{205196e 1923:com.android.launcher3/u0a75}
+          Intent { act=android.intent.action.MAIN cat=[android.intent.category.DEFAULT] flg=0x10800000 cmp=com.android.launcher3/com.android.quickstep.RecentsActivity }
+          frontOfTask=true task=TaskRecord{226d575 #36 I=com.android.launcher3/com.android.quickstep.RecentsActivity U=0 StackId=8 sz=1}
+          taskAffinity=null
+          realActivity=com.android.launcher3/com.android.quickstep.RecentsActivity
+          baseDir=/system/priv-app/com.android.launcher3/com.android.launcher3.apk
+          dataDir=/data/user/0/com.android.launcher3
+          stateNotNeeded=true componentSpecified=true mActivityType=recents
+          compat={240dpi always-compat} labelRes=0x7f110035 icon=0x7f08001b theme=0x7f12000a
+          mLastReportedConfigurations:
+           mGlobalConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 0, 0) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=undefined} s.6}
+           mOverrideConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=recents} s.6}
+          CurrentConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=recents} s.6}
+          OverrideConfiguration={0.0 ?mcc?mnc ?localeList ?layoutDir ?swdp ?wdp ?hdp ?density ?lsize ?long ?ldr ?wideColorGamut ?orien ?uimode ?night ?touch ?keyb/?/? ?nav/? winConfig={ mBounds=Rect(0, 0 - 0, 0) mAppBounds=null mWindowingMode=undefined mActivityType=recents}}
+          taskDescription: label="null" icon=null iconResource=0 iconFilename=null primaryColor=fff5f5f5
+           backgroundColor=fffafafa
+           statusBarColor=0
+           navigationBarColor=0
+          launchFailed=false launchCount=0 lastLaunchTime=-3m14s149ms
+          haveState=true icicle=Bundle[mParcelledData.dataSize=560]
+          state=RESUMED stopped=false delayedResume=false finishing=false
+          keysPaused=false inHistory=true visible=true sleeping=false idle=false mStartingWindowState=STARTING_WINDOW_REMOVED
+          fullscreen=true noDisplay=false immersive=false launchMode=2
+          frozenBeforeDestroy=false forceNewConfig=false
+          mActivityType=recents
+          displayStartTime=-35ms startTime=0
+          waitingVisible=false nowVisible=false lastVisibleTime=-6s904ms
+          resizeMode=RESIZE_MODE_RESIZEABLE
+          mLastReportedMultiWindowMode=false mLastReportedPictureInPictureMode=false
+
+    Running activities (most recent first):
+      TaskRecord{226d575 #36 I=com.android.launcher3/com.android.quickstep.RecentsActivity U=0 StackId=8 sz=1}
+        Run #0: ActivityRecord{7620f3f u0 com.android.launcher3/com.android.quickstep.RecentsActivity t36}
+
+    mResumedActivity: ActivityRecord{7620f3f u0 com.android.launcher3/com.android.quickstep.RecentsActivity t36}
 
   Stack #0: type=home mode=fullscreen
   isSleeping=false
   mBounds=Rect(0, 0 - 0, 0)
+
     Task id #2
     mBounds=Rect(0, 0 - 0, 0)
@@ -21,5 +79,5 @@

       mRootProcess=ProcessRecord{8f8f222 1942:com.amazon.firelauncher/u0a120}
       stackId=0
-      hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=3835662 (inactive for 50s)
+      hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=6008544 (inactive for 0s)
       * Hist #0: ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}
           packageName=com.amazon.firelauncher processName=com.amazon.firelauncher
@@ -43,12 +101,12 @@

            statusBarColor=0
            navigationBarColor=ff000000
-          launchFailed=false launchCount=0 lastLaunchTime=-1h4m26s120ms
+          launchFailed=false launchCount=0 lastLaunchTime=-1h39m48s903ms
           haveState=false icicle=null
-          state=RESUMED stopped=false delayedResume=false finishing=false
-          keysPaused=false inHistory=true visible=true sleeping=false idle=true mStartingWindowState=STARTING_WINDOW_NOT_SHOWN
+          state=STOPPING stopped=false delayedResume=false finishing=false
+          keysPaused=false inHistory=true visible=false sleeping=false idle=true mStartingWindowState=STARTING_WINDOW_NOT_SHOWN
           fullscreen=true noDisplay=false immersive=false launchMode=2
           frozenBeforeDestroy=false forceNewConfig=false
           mActivityType=home
-          waitingVisible=false nowVisible=true lastVisibleTime=-1m59s257ms
+          waitingVisible=false nowVisible=true lastVisibleTime=-2s915ms
           resizeMode=RESIZE_MODE_RESIZEABLE
           mLastReportedMultiWindowMode=false mLastReportedPictureInPictureMode=false
@@ -58,205 +116,13 @@

         Run #0: ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}
 
-    mResumedActivity: ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}
+    mLastPausedActivity: ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}
 
-  Stack #7: type=standard mode=fullscreen
-  isSleeping=false
-  mBounds=Rect(0, 0 - 0, 0)
-
-    Task id #35
-    mBounds=Rect(0, 0 - 0, 0)
-    mMinWidth=-1
-    mMinHeight=-1
-    mLastNonFullscreenBounds=null
-    * TaskRecord{4a862f5 #35 A=10197:org.fireosresearch.phase4.alias U=0 StackId=7 sz=1}
-      userId=0 effectiveUid=u0a197 mCallingUid=u0a196 mUserSetupComplete=true mCallingPackage=org.fireosresearch.phase4.redirect
-      affinity=10197:org.fireosresearch.phase4.alias
-      intent={flg=0x14000000 cmp=org.fireosresearch.phase4.alias/.HomeActivity}
-      realActivity=org.fireosresearch.phase4.alias/.HomeActivity
-      autoRemoveRecents=false isPersistable=true numFullscreen=1 activityType=1
-      rootWasReset=false mNeverRelinquishIdentity=true mReuseTask=false mLockTaskAuth=LOCK_TASK_AUTH_PINNABLE
-      Activities=[ActivityRecord{e911e93 u0 org.fireosresearch.phase4.alias/.HomeActivity t35}]
-      askedCompatMode=false inRecents=true isAvailable=true
-      stackId=7
-      hasBeenVisible=false mResizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION mSupportsPictureInPicture=false isResizeable=true lastActiveTime=3768932 (inactive for 116s)
-      * Hist #0: ActivityRecord{e911e93 u0 org.fireosresearch.phase4.alias/.HomeActivity t35}
-          packageName=org.fireosresearch.phase4.alias processName=org.fireosresearch.phase4.alias
-          launchedFromUid=10196 launchedFromPackage=org.fireosresearch.phase4.redirect userId=0
-          app=null
-          Intent { flg=0x14000000 cmp=org.fireosresearch.phase4.alias/.HomeActivity }
-          frontOfTask=true task=TaskRecord{4a862f5 #35 A=10197:org.fireosresearch.phase4.alias U=0 StackId=7 sz=1}
-          taskAffinity=10197:org.fireosresearch.phase4.alias
-          realActivity=org.fireosresearch.phase4.alias/.HomeActivity
-          baseDir=/data/app/org.fireosresearch.phase4.alias-QPoOZGfYDGBm13QC130wVQ==/base.apk
-          dataDir=/data/user/0/org.fireosresearch.phase4.alias
-          stateNotNeeded=false componentSpecified=true mActivityType=standard
-          compat=null labelRes=0x0 icon=0x0 theme=0x1030241
-          mLastReportedConfigurations:
-           mGlobalConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 0, 0) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=undefined} s.6}
-           mOverrideConfig={0.0 ?mcc?mnc ?localeList ?layoutDir ?swdp ?wdp ?hdp ?density ?lsize ?long ?ldr ?wideColorGamut ?orien ?uimode ?night ?touch ?keyb/?/? ?nav/? winConfig={ mBounds=Rect(0, 0 - 0, 0) mAppBounds=null mWindowingMode=undefined mActivityType=undefined}}
-          CurrentConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=standard} s.6}
-          launchFailed=false launchCount=0 lastLaunchTime=0
-          haveState=true icicle=null
-          state=INITIALIZING stopped=false delayedResume=true finishing=false
-          keysPaused=false inHistory=true visible=false sleeping=false idle=false mStartingWindowState=STARTING_WINDOW_REMOVED
-          fullscreen=true noDisplay=false immersive=false launchMode=2
-          frozenBeforeDestroy=false forceNewConfig=false
-          mActivityType=standard
-          resizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION
-          mLastReportedMultiWindowMode=false mLastReportedPictureInPictureMode=false
-
-  Stack #4: type=standard mode=fullscreen
-  isSleeping=false
-  mBounds=Rect(0, 0 - 0, 0)
-
-    Task id #32
-    mBounds=Rect(0, 0 - 0, 0)
-    mMinWidth=-1
-    mMinHeight=-1
-    mLastNonFullscreenBounds=null
-    * TaskRecord{a391b43 #32 A=10196:org.fireosresearch.phase4.redirect U=0 StackId=4 sz=1}
-      userId=0 effectiveUid=u0a196 mCallingUid=2000 mUserSetupComplete=true mCallingPackage=null
-      affinity=10196:org.fireosresearch.phase4.redirect
-      intent={flg=0x10000000 cmp=org.fireosresearch.phase4.redirect/.ControlActivity}
-      realActivity=org.fireosresearch.phase4.redirect/.ControlActivity
-      autoRemoveRecents=false isPersistable=true numFullscreen=1 activityType=1
-      rootWasReset=false mNeverRelinquishIdentity=true mReuseTask=false mLockTaskAuth=LOCK_TASK_AUTH_PINNABLE
-      Activities=[ActivityRecord{64534ba u0 org.fireosresearch.phase4.redirect/.ControlActivity t32}]
-      askedCompatMode=false inRecents=true isAvailable=true
-      mRootProcess=ProcessRecord{97135c0 8931:org.fireosresearch.phase4.redirect/u0a196}
-      stackId=4
-      hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION mSupportsPictureInPicture=false isResizeable=true lastActiveTime=3766243 (inactive for 119s)
-      * Hist #0: ActivityRecord{64534ba u0 org.fireosresearch.phase4.redirect/.ControlActivity t32}
-          packageName=org.fireosresearch.phase4.redirect processName=org.fireosresearch.phase4.redirect
-          launchedFromUid=2000 launchedFromPackage=null userId=0
-          app=ProcessRecord{97135c0 8931:org.fireosresearch.phase4.redirect/u0a196}
-          Intent { flg=0x10000000 cmp=org.fireosresearch.phase4.redirect/.ControlActivity }
-          frontOfTask=true task=TaskRecord{a391b43 #32 A=10196:org.fireosresearch.phase4.redirect U=0 StackId=4 sz=1}
-          taskAffinity=10196:org.fireosresearch.phase4.redirect
-          realActivity=org.fireosresearch.phase4.redirect/.ControlActivity
-          baseDir=/data/app/org.fireosresearch.phase4.redirect-HmZwcWLMh9DuFUo81iOafA==/base.apk
-          dataDir=/data/user/0/org.fireosresearch.phase4.redirect
-          stateNotNeeded=false componentSpecified=true mActivityType=standard
-          compat={240dpi always-compat} labelRes=0x0 icon=0x0 theme=0x1030241
-          mLastReportedConfigurations:
-           mGlobalConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 0, 0) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=undefined} s.6}
-           mOverrideConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=standard} s.6}
-          CurrentConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=standard} s.6}
-          taskDescription: label="null" icon=null iconResource=0 iconFilename=null primaryColor=fff5f5f5
-           backgroundColor=fffafafa
-           statusBarColor=ff757575
-           navigationBarColor=ff000000
-          launchFailed=false launchCount=0 lastLaunchTime=-13m21s51ms
-          haveState=true icicle=Bundle[mParcelledData.dataSize=256]
-          state=STOPPED stopped=true delayedResume=false finishing=false
-          keysPaused=false inHistory=true visible=false sleeping=false idle=true mStartingWindowState=STARTING_WINDOW_REMOVED
-          fullscreen=true noDisplay=false immersive=false launchMode=0
-          frozenBeforeDestroy=false forceNewConfig=false
-          mActivityType=standard
-          waitingVisible=false nowVisible=false lastVisibleTime=-9m11s492ms
-          resizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION
-          mLastReportedMultiWindowMode=false mLastReportedPictureInPictureMode=false
-
-    Running activities (most recent first):
-      TaskRecord{a391b43 #32 A=10196:org.fireosresearch.phase4.redirect U=0 StackId=4 sz=1}
-        Run #0: ActivityRecord{64534ba u0 org.fireosresearch.phase4.redirect/.ControlActivity t32}
-
-    mLastPausedActivity: ActivityRecord{64534ba u0 org.fireosresearch.phase4.redirect/.ControlActivity t32}
-
-  Stack #5: type=standard mode=fullscreen
-  isSleeping=false
-  mBounds=Rect(0, 0 - 0, 0)
-
-    Task id #33
-    mBounds=Rect(0, 0 - 0, 0)
-    mMinWidth=-1
-    mMinHeight=-1
-    mLastNonFullscreenBounds=null
-    * TaskRecord{e70e8f2 #33 I=com.amazon.settings/.accessibility.AccessibilitySettingsActivity U=0 StackId=5 sz=2}
-      userId=0 effectiveUid=1000 mCallingUid=2000 mUserSetupComplete=true mCallingPackage=null
-      intent={act=android.settings.ACCESSIBILITY_SETTINGS flg=0x10000000 cmp=com.amazon.settings/.accessibility.AccessibilitySettingsActivity}
-      realActivity=com.amazon.settings/.accessibility.AccessibilitySettingsActivity
-      autoRemoveRecents=false isPersistable=true numFullscreen=2 activityType=1
-      rootWasReset=false mNeverRelinquishIdentity=true mReuseTask=false mLockTaskAuth=LOCK_TASK_AUTH_PINNABLE
-      Activities=[ActivityRecord{84fab35 u0 com.amazon.settings/.accessibility.AccessibilitySettingsActivity t33}, ActivityRecord{fe90555 u0 com.amazon.switchaccess.root/com.amazon.switchaccess.SwitchAccessPreferenceActivity t33}]
-      askedCompatMode=false inRecents=true isAvailable=true
-      mRootProcess=ProcessRecord{b83af59 8976:com.amazon.settings/1000}
-      stackId=5
-      hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION mSupportsPictureInPicture=false isResizeable=true lastActiveTime=3234189 (inactive for 651s)
-      * Hist #1: ActivityRecord{fe90555 u0 com.amazon.switchaccess.root/com.amazon.switchaccess.SwitchAccessPreferenceActivity t33}
-          packageName=com.amazon.switchaccess.root processName=com.amazon.switchaccess.root
-          launchedFromUid=1000 launchedFromPackage=com.amazon.settings userId=0
-          app=ProcessRecord{c443779 9075:com.amazon.switchaccess.root/u0a134}
-          Intent { act=com.amazon.switchaccess.PREFERENCES cmp=com.amazon.switchaccess.root/com.amazon.switchaccess.SwitchAccessPreferenceActivity }
-          frontOfTask=false task=TaskRecord{e70e8f2 #33 I=com.amazon.settings/.accessibility.AccessibilitySettingsActivity U=0 StackId=5 sz=2}
-          taskAffinity=10134:com.amazon.switchaccess.root
-          realActivity=com.amazon.switchaccess.root/com.amazon.switchaccess.SwitchAccessPreferenceActivity
-          baseDir=/system/priv-app/com.amazon.switchaccess/com.amazon.switchaccess.apk
-          dataDir=/data/user/0/com.amazon.switchaccess.root
-          stateNotNeeded=false componentSpecified=false mActivityType=standard
-          compat={240dpi always-compat} labelRes=0x7f0e032e icon=0x0 theme=0x7f0f00ed
-          mLastReportedConfigurations:
-           mGlobalConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 0, 0) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=undefined} s.6}
-           mOverrideConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=standard} s.6}
-          CurrentConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=standard} s.6}
-          resultTo=null resultWho=android:fragment:0 resultCode=-1
```

### `activity/recents.stdout.txt`

```diff
--- before/activity/recents.stdout.txt

+++ after/activity/recents.stdout.txt

@@ -3,15 +3,14 @@

 mRecentsComponent=ComponentInfo{com.android.launcher3/com.android.quickstep.RecentsActivity}
   Recent tasks:
-  * Recent #0: TaskRecord{4a862f5 #35 A=10197:org.fireosresearch.phase4.alias U=0 StackId=7 sz=1}
-    userId=0 effectiveUid=u0a197 mCallingUid=u0a196 mUserSetupComplete=true mCallingPackage=org.fireosresearch.phase4.redirect
-    affinity=10197:org.fireosresearch.phase4.alias
-    intent={flg=0x14000000 cmp=org.fireosresearch.phase4.alias/.HomeActivity}
-    realActivity=org.fireosresearch.phase4.alias/.HomeActivity
-    autoRemoveRecents=false isPersistable=true numFullscreen=1 activityType=1
+  * Recent #0: TaskRecord{226d575 #36 I=com.android.launcher3/com.android.quickstep.RecentsActivity U=0 StackId=8 sz=1}
+    userId=0 effectiveUid=u0a75 mCallingUid=u0a75 mUserSetupComplete=true mCallingPackage=com.android.launcher3
+    intent={act=android.intent.action.MAIN cat=[android.intent.category.DEFAULT] flg=0x10800000 cmp=com.android.launcher3/com.android.quickstep.RecentsActivity}
+    realActivity=com.android.launcher3/com.android.quickstep.RecentsActivity
+    autoRemoveRecents=false isPersistable=false numFullscreen=1 activityType=3
     rootWasReset=false mNeverRelinquishIdentity=true mReuseTask=false mLockTaskAuth=LOCK_TASK_AUTH_PINNABLE
-    Activities=[ActivityRecord{e911e93 u0 org.fireosresearch.phase4.alias/.HomeActivity t35}]
+    Activities=[ActivityRecord{7620f3f u0 com.android.launcher3/com.android.quickstep.RecentsActivity t36}]
     askedCompatMode=false inRecents=true isAvailable=true
-    stackId=7
-    hasBeenVisible=false mResizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION mSupportsPictureInPicture=false isResizeable=true lastActiveTime=3768932 (inactive for 116s)
+    stackId=8
+    hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=6005216 (inactive for 3s)
   * Recent #1: TaskRecord{38663ed #2 A=10120:com.amazon.firelauncher U=0 StackId=0 sz=1}
     userId=0 effectiveUid=u0a120 mCallingUid=0 mUserSetupComplete=true mCallingPackage=null
@@ -25,50 +24,3 @@

     mRootProcess=ProcessRecord{8f8f222 1942:com.amazon.firelauncher/u0a120}
     stackId=0
-    hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=3835662 (inactive for 50s)
-  * Recent #2: TaskRecord{a391b43 #32 A=10196:org.fireosresearch.phase4.redirect U=0 StackId=4 sz=1}
-    userId=0 effectiveUid=u0a196 mCallingUid=2000 mUserSetupComplete=true mCallingPackage=null
-    affinity=10196:org.fireosresearch.phase4.redirect
-    intent={flg=0x10000000 cmp=org.fireosresearch.phase4.redirect/.ControlActivity}
-    realActivity=org.fireosresearch.phase4.redirect/.ControlActivity
-    autoRemoveRecents=false isPersistable=true numFullscreen=1 activityType=1
-    rootWasReset=false mNeverRelinquishIdentity=true mReuseTask=false mLockTaskAuth=LOCK_TASK_AUTH_PINNABLE
-    Activities=[ActivityRecord{64534ba u0 org.fireosresearch.phase4.redirect/.ControlActivity t32}]
-    askedCompatMode=false inRecents=true isAvailable=true
-    mRootProcess=ProcessRecord{97135c0 8931:org.fireosresearch.phase4.redirect/u0a196}
-    stackId=4
-    hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION mSupportsPictureInPicture=false isResizeable=true lastActiveTime=3766243 (inactive for 119s)
-  * Recent #3: TaskRecord{e70e8f2 #33 I=com.amazon.settings/.accessibility.AccessibilitySettingsActivity U=0 StackId=5 sz=2}
-    userId=0 effectiveUid=1000 mCallingUid=2000 mUserSetupComplete=true mCallingPackage=null
-    intent={act=android.settings.ACCESSIBILITY_SETTINGS flg=0x10000000 cmp=com.amazon.settings/.accessibility.AccessibilitySettingsActivity}
-    realActivity=com.amazon.settings/.accessibility.AccessibilitySettingsActivity
-    autoRemoveRecents=false isPersistable=true numFullscreen=2 activityType=1
-    rootWasReset=false mNeverRelinquishIdentity=true mReuseTask=false mLockTaskAuth=LOCK_TASK_AUTH_PINNABLE
-    Activities=[ActivityRecord{84fab35 u0 com.amazon.settings/.accessibility.AccessibilitySettingsActivity t33}, ActivityRecord{fe90555 u0 com.amazon.switchaccess.root/com.amazon.switchaccess.SwitchAccessPreferenceActivity t33}]
-    askedCompatMode=false inRecents=true isAvailable=true
-    mRootProcess=ProcessRecord{b83af59 8976:com.amazon.settings/1000}
-    stackId=5
-    hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION mSupportsPictureInPicture=false isResizeable=true lastActiveTime=3234189 (inactive for 651s)
-  * Recent #4: TaskRecord{c3ff3b1 #34 A=10134:com.amazon.switchaccess.root U=0 StackId=-1 sz=0}
-    userId=0 effectiveUid=u0a134 mCallingUid=u0a134 mUserSetupComplete=true mCallingPackage=com.amazon.switchaccess.root
-    affinity=10134:com.amazon.switchaccess.root
-    intent={flg=0x10000000 cmp=com.amazon.switchaccess.root/com.amazon.switchaccess.setupwizard.SetupWizardActivity}
-    realActivity=com.amazon.switchaccess.root/com.amazon.switchaccess.setupwizard.SetupWizardActivity
-    autoRemoveRecents=false isPersistable=true numFullscreen=0 activityType=1
-    rootWasReset=false mNeverRelinquishIdentity=true mReuseTask=false mLockTaskAuth=LOCK_TASK_AUTH_PINNABLE
-    Activities=[]
-    askedCompatMode=false inRecents=true isAvailable=true
-    mRootProcess=ProcessRecord{c443779 9075:com.amazon.switchaccess.root/u0a134}
-    stackId=-1
-    hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION mSupportsPictureInPicture=false isResizeable=true lastActiveTime=3187670 (inactive for 698s)
-  * Recent #5: TaskRecord{ca627d2 #28 A=1000:com.android.settings.root U=0 StackId=-1 sz=0}
-    userId=0 effectiveUid=1000 mCallingUid=2000 mUserSetupComplete=true mCallingPackage=
-    affinity=1000:com.android.settings.root
-    intent={flg=0x10000000 cmp=com.android.settings/.Settings}
-    origActivity=com.android.settings/.Settings
-    realActivity=com.android.settings/.Settings
-    autoRemoveRecents=false isPersistable=true numFullscreen=0 activityType=0
-    rootWasReset=false mNeverRelinquishIdentity=true mReuseTask=false mLockTaskAuth=LOCK_TASK_AUTH_PINNABLE
-    Activities=[]
-    askedCompatMode=false inRecents=true isAvailable=true
-    stackId=-1
-    hasBeenVisible=false mResizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION mSupportsPictureInPicture=false isResizeable=true lastActiveTime=19930 (inactive for 3865s)
+    hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=6008544 (inactive for 0s)
```

### `activity/top.stdout.txt`

```diff
--- before/activity/top.stdout.txt

+++ after/activity/top.stdout.txt

@@ -1,12 +1,29 @@

-TASK null id=33 userId=0
-  ACTIVITY com.amazon.switchaccess.root/com.amazon.switchaccess.SwitchAccessPreferenceActivity fe90555 pid=9075
-    Local Activity 7878123 State:
+TASK 10120:com.amazon.firelauncher id=2 userId=0
+  ACTIVITY com.amazon.firelauncher/.Launcher 873be7c pid=1942
+    Local Activity b21ee9c State:
       mResumed=false mStopped=true mFinished=false
       mChangingConfigurations=false
-      mCurrentConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=standard} s.6}
+      mCurrentConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=home} s.6}
       mLoadersStarted=true
+      Active Fragments in ea3fd60:
+        #0: ReportFragment{b465219 #0 androidx.lifecycle.LifecycleDispatcher.report_fragment_tag}
+          mFragmentId=#0 mContainerId=#0 mTag=androidx.lifecycle.LifecycleDispatcher.report_fragment_tag
+          mState=3 mIndex=0 mWho=android:fragment:0 mBackStackNesting=0
+          mAdded=true mRemoving=false mFromLayout=false mInLayout=false
+          mHidden=false mDetached=false mMenuVisible=true mHasMenu=false
+          mRetainInstance=false mRetaining=false mUserVisibleHint=true
+          mFragmentManager=FragmentManager{ea3fd60 in HostCallbacks{24ac2de}}
+          mHost=android.app.Activity$HostCallbacks@24ac2de
+          Child FragmentManager{6e8ccbf in ReportFragment{b465219}}:
+            FragmentManager misc state:
+              mHost=android.app.Activity$HostCallbacks@24ac2de
+              mContainer=android.app.Fragment$1@a3b8f8c
+              mParent=ReportFragment{b465219 #0 androidx.lifecycle.LifecycleDispatcher.report_fragment_tag}
+              mCurState=3 mStateSaved=true mDestroyed=false
+      Added Fragments:
+        #0: ReportFragment{b465219 #0 androidx.lifecycle.LifecycleDispatcher.report_fragment_tag}
       FragmentManager misc state:
-        mHost=android.app.Activity$HostCallbacks@c451bd9
-        mContainer=android.app.Activity$HostCallbacks@c451bd9
+        mHost=android.app.Activity$HostCallbacks@24ac2de
+        mContainer=android.app.Activity$HostCallbacks@24ac2de
         mCurState=3 mStateSaved=true mDestroyed=false
     ViewRoot:
@@ -22,269 +39,16 @@

     Choreographer:
       mFrameScheduled=false
-      mLastFrameTime=3234533 (651350 ms ago)
-    View Hierarchy:
-      DecorView@4788ae9[SwitchAccessPreferenceActivity]
-        com.android.internal.widget.ActionBarOverlayLayout{dcf682b V.E...... .......D 0,0-1200,1920 #102024a android:id/decor_content_parent}
-          android.widget.FrameLayout{4fe387a V.E...... .......D 0,132-1200,1920 #1020002 android:id/content}
-            android.widget.LinearLayout{ec5eca5 V.E...... .......D 0,0-1200,1788}
-              android.widget.LinearLayout{a067a9c V.E...... .......D 0,0-1200,1788}
-                android.widget.LinearLayout{64f3a0f V.E...... .......D 0,0-1200,1788 #102033e android:id/headers}
-                  android.widget.ListView{adc536e VFED.VC.. .......D 0,0-1200,1788 #102000a android:id/list}
-                    android.widget.LinearLayout{6cd0059 V.ED..... ........ 48,48-1152,133}
-                      android.widget.TextView{93a741e V.ED..... ........ 36,0-1068,84 #1020016 android:id/title}
-                    android.widget.LinearLayout{d0d9f64 V.E...... ......ID 48,134-1152,300}
-                      android.widget.LinearLayout{abf299e G.E...... ......I. 0,0-0,0 #102003e android:id/icon_frame}
-                        com.android.internal.widget.PreferenceImageView{470c7f G.ED..... ......I. 0,0-0,0 #1020006 android:id/icon}
-                      android.widget.RelativeLayout{6874993 V.E...... ........ 36,0-948,166}
-                        android.widget.TextView{59c9e82 V.ED..... ........ 0,24-191,55 #1020016 android:id/title}
-                        android.widget.TextView{ab74dd0 V.ED..... ........ 0,55-912,142 #1020010 android:id/summary}
-                      android.widget.LinearLayout{b7a20ce V.E...... ........ 948,0-1068,166 #1020018 android:id/widget_frame}
-                        android.widget.Switch{8a1b1c9 V.ED..... ........ 24,53-120,113 #1020040 android:id/switch_widget}
-                    android.widget.LinearLayout{e8c580b V.E...... ......ID 48,301-1152,409}
-                      android.widget.ImageView{d49344c G.ED..... ......I. 0,0-0,0 #1020006 android:id/icon}
-                      android.widget.RelativeLayout{558d101 V.E...... ........ 36,35-1068,66}
-                        android.widget.TextView{81706e8 V.ED..... ........ 0,0-431,31 #1020016 android:id/title}
-                        android.widget.TextView{4e29c95 G.ED..... ......ID 0,0-0,0 #1020010 android:id/summary}
-                      android.widget.LinearLayout{7041aa G.E...... ......I. 0,0-0,0 #1020018 android:id/widget_frame}
-                    android.widget.LinearLayout{7a669e7 V.ED..... ........ 48,410-1152,495}
-                      android.widget.TextView{5c9a994 V.ED..... ........ 36,0-1068,84 #1020016 android:id/title}
-                    android.widget.LinearLayout{b3dac32 V.E...... ......ID 48,496-1152,604}
-                      android.widget.ImageView{749f19b G.ED..... ......I. 0,0-0,0 #1020006 android:id/icon}
-                      android.widget.RelativeLayout{561cb00 V.E...... ........ 36,35-1068,66}
-                        android.widget.TextView{465bd83 V.ED..... ........ 0,0-360,31 #1020016 android:id/title}
-                        android.widget.TextView{afb4938 G.ED..... ......ID 0,0-0,0 #1020010 android:id/summary}
-                      android.widget.LinearLayout{69d6d11 G.E...... ......I. 0,0-0,0 #1020018 android:id/widget_frame}
-                    android.widget.LinearLayout{316597e V.E...... ......ID 48,605-1152,713}
-                      android.widget.ImageView{468ce76 G.ED..... ......I. 0,0-0,0 #1020006 android:id/icon}
-                      android.widget.RelativeLayout{798972c V.E...... ........ 36,35-1068,66}
-                        android.widget.TextView{53caedf V.ED..... ........ 0,0-383,31 #1020016 android:id/title}
-                        android.widget.TextView{4cc0c77 G.ED..... ......ID 0,0-0,0 #1020010 android:id/summary}
-                      android.widget.LinearLayout{1b7c0e4 G.E...... ......I. 0,0-0,0 #1020018 android:id/widget_frame}
-                    android.widget.LinearLayout{20ff5f5 V.ED..... ........ 48,714-1152,799}
-                      android.widget.TextView{e3a8f8a V.ED..... ........ 36,0-1068,84 #1020016 android:id/title}
-                    android.widget.LinearLayout{d8dfa18 V.E...... ......ID 48,800-1152,906}
-                      android.widget.LinearLayout{c5ac94d G.E...... ......I. 0,0-0,0 #102003e android:id/icon_frame}
-                        com.android.internal.widget.PreferenceImageView{a8b5c02 G.ED..... ......I. 0,0-0,0 #1020006 android:id/icon}
-                      android.widget.RelativeLayout{8749fc4 V.E...... ........ 36,0-1068,106}
-                        android.widget.TextView{dc79ad7 V.ED..... ........ 0,24-144,55 #1020016 android:id/title}
-                        android.widget.TextView{7edeead V.ED..... ........ 0,55-147,82 #1020010 android:id/summary}
-                      android.widget.LinearLayout{e36fc71 G.E...... ......I. 0,0-0,0 #1020018 android:id/widget_frame}
-                    android.widget.LinearLayout{64a1e2e V.E...... ......ID 48,907-1152,1015}
-                      android.widget.ImageView{eeaf913 G.ED..... ......I. 0,0-0,0 #1020006 android:id/icon}
-                      android.widget.RelativeLayout{386235c V.E...... ........ 36,35-1068,66}
-                        android.widget.TextView{8550dcf V.ED..... ........ 0,0-360,31 #1020016 android:id/title}
-                        android.widget.TextView{9a20750 G.ED..... ......ID 0,0-0,0 #1020010 android:id/summary}
-                      android.widget.LinearLayout{17ad49 G.E...... ......I. 0,0-0,0 #1020018 android:id/widget_frame}
-                    android.widget.LinearLayout{f5def3a V.E...... ......ID 48,1016-1152,1095}
-                      android.widget.LinearLayout{57364e G.E...... ......I. 0,0-0,0 #102003e android:id/icon_frame}
-                        com.android.internal.widget.PreferenceImageView{602136f G.ED..... ......I. 0,0-0,0 #1020006 android:id/icon}
-                      android.widget.RelativeLayout{f6ee3e1 V.E...... ........ 36,0-948,79}
-                        android.widget.TextView{a001948 V.ED..... ........ 0,24-144,55 #1020016 android:id/title}
-                        android.widget.TextView{7a8487c G.ED..... ......I. 0,0-0,0 #1020010 android:id/summary}
-                      android.widget.LinearLayout{3cee7c7 V.E...... ........ 948,0-1068,79 #1020018 android:id/widget_frame}
-                        android.widget.Switch{cabc506 V.ED..... ........ 24,9-120,69 #1020040 android:id/switch_widget}
-                    android.widget.LinearLayout{514dd1d V.E...... ......ID 48,1096-1152,1202}
-                      android.widget.LinearLayout{4a4d505 G.E...... ......I. 0,0-0,0 #102003e android:id/icon_frame}
-                        com.android.internal.widget.PreferenceImageView{9f4695a G.ED..... ......I. 0,0-0,0 #1020006 android:id/icon}
-                      android.widget.RelativeLayout{b272e19 V.E...... ........ 36,0-1068,106}
-                        android.widget.TextView{84ec960 V.ED..... ........ 0,24-192,55 #1020016 android:id/title}
-                        android.widget.TextView{106ede V.ED..... ........ 0,55-62,82 #1020010 android:id/summary}
-                      android.widget.LinearLayout{6af2b92 G.E...... ......I. 0,0-0,0 #1020018 android:id/widget_frame}
-                    android.widget.LinearLayout{67b08bf V.E...... ......ID 48,1203-1152,1309}
-                      android.widget.LinearLayout{ac6778b G.E...... ......I. 0,0-0,0 #102003e android:id/icon_frame}
-                        com.android.internal.widget.PreferenceImageView{f6f7068 G.ED..... ......I. 0,0-0,0 #1020006 android:id/icon}
-                      android.widget.RelativeLayout{46171db V.E...... ........ 36,0-1068,106}
-                        android.widget.TextView{bb09aea V.ED..... ........ 0,24-144,55 #1020016 android:id/title}
-                        android.widget.TextView{8906478 V.ED..... ........ 0,55-95,82 #1020010 android:id/summary}
-                      android.widget.LinearLayout{1c71b8c G.E...... ......I. 0,0-0,0 #1020018 android:id/widget_frame}
-                    android.widget.LinearLayout{e78751 V.E...... ......ID 48,1310-1152,1416}
-                      android.widget.LinearLayout{f22bc81 G.E...... ......I. 0,0-0,0 #102003e android:id/icon_frame}
-                        com.android.internal.widget.PreferenceImageView{3ffc126 G.ED..... ......I. 0,0-0,0 #1020006 android:id/icon}
-                      android.widget.RelativeLayout{4a35024 V.E...... ........ 36,0-948,106}
-                        android.widget.TextView{d7b50b7 V.ED..... ........ 0,24-264,55 #1020016 android:id/title}
-                        android.widget.TextView{bcc478d V.ED..... ........ 0,55-418,82 #1020010 android:id/summary}
-                      android.widget.LinearLayout{eea4153 V.E...... ........ 948,0-1068,106 #1020018 android:id/widget_frame}
-                        android.widget.Switch{7d59d42 V.ED..... ........ 24,23-120,83 #1020040 android:id/switch_widget}
-                    android.widget.LinearLayout{2d74a90 V.E...... ......ID 48,1417-1152,1496}
-                      android.widget.LinearLayout{a230167 G.E...... ......I. 0,0-0,0 #102003e android:id/icon_frame}
-                        com.android.internal.widget.PreferenceImageView{7ff2b14 G.ED..... ......I. 0,0-0,0 #1020006 android:id/icon}
-                      android.widget.RelativeLayout{40e7fbc V.E...... ........ 36,0-1068,79}
-                        android.widget.TextView{c4d9faf V.ED..... ........ 0,24-240,55 #1020016 android:id/title}
-                        android.widget.TextView{c3d9fbd G.ED..... ......I. 0,0-0,0 #1020010 android:id/summary}
-                      android.widget.LinearLayout{9c2cf89 G.E...... ......I. 0,0-0,0 #1020018 android:id/widget_frame}
-                    android.widget.LinearLayout{c7fdb45 V.E...... ......ID 48,1497-1152,1603}
-                      android.widget.LinearLayout{616c9b2 G.E...... ......I. 0,0-0,0 #102003e android:id/icon_frame}
-                        com.android.internal.widget.PreferenceImageView{ad44d03 G.ED..... ......I. 0,0-0,0 #1020006 android:id/icon}
-                      android.widget.RelativeLayout{247e6c1 V.E...... ........ 36,0-1068,106}
-                        android.widget.TextView{321dba8 V.ED..... ........ 0,24-238,55 #1020016 android:id/title}
-                        android.widget.TextView{b323e66 V.ED..... ........ 0,55-62,82 #1020010 android:id/summary}
-                      android.widget.LinearLayout{39d929a G.E...... ......I. 0,0-0,0 #1020018 android:id/widget_frame}
-                    android.widget.LinearLayout{c4bd5a7 V.E...... ......ID 48,1604-1152,1710}
-                      android.widget.LinearLayout{f2de480 G.E...... ......I. 0,0-0,0 #102003e android:id/icon_frame}
-                        com.android.internal.widget.PreferenceImageView{d297ab9 G.ED..... ......I. 0,0-0,0 #1020006 android:id/icon}
-                      android.widget.RelativeLayout{a562543 V.E...... ........ 36,0-1068,106}
-                        android.widget.TextView{c13daf2 V.ED..... ........ 0,24-262,55 #1020016 android:id/title}
-                        android.widget.TextView{ada77c0 V.ED..... ........ 0,55-62,82 #1020010 android:id/summary}
-                      android.widget.LinearLayout{d8d0a54 G.E...... ......I. 0,0-0,0 #1020018 android:id/widget_frame}
-                    android.widget.LinearLayout{e01acf9 V.E...... ......ID 48,1711-1152,1817}
-                      android.widget.LinearLayout{223cefe G.E...... ......I. 0,0-0,0 #102003e android:id/icon_frame}
-                        com.android.internal.widget.PreferenceImageView{8c4b65f G.ED..... ......I. 0,0-0,0 #1020006 android:id/icon}
-                      android.widget.RelativeLayout{ecf4fec V.E...... ........ 36,0-948,106}
-                        android.widget.TextView{c2bd29f V.ED..... ........ 0,24-239,55 #1020016 android:id/title}
-                        android.widget.TextView{5271fb5 V.ED..... ........ 0,55-420,82 #1020010 android:id/summary}
-                      android.widget.LinearLayout{484f9bb V.E...... ........ 948,0-1068,106 #1020018 android:id/widget_frame}
-                        android.widget.Switch{84fd64a V.ED..... ........ 24,23-120,83 #1020040 android:id/switch_widget}
-                  android.widget.FrameLayout{f4ea488 V.E...... ........ 0,1788-1200,1788 #1020397 android:id/list_footer}
-              android.widget.RelativeLayout{7ccc8ac G.E...... ......I. 0,0-0,0 #1020206 android:id/button_bar}
-                android.widget.Button{85e0975 VFED..C.. ......I. 0,0-0,0 #10201eb android:id/back_button}
-                android.widget.LinearLayout{c69dd0a V.E...... ......I. 0,0-0,0}
-                  android.widget.Button{a28597b GFED..C.. ......I. 0,0-0,0 #10204b3 android:id/skip_button}
-                  android.widget.Button{e93c398 VFED..C.. ......I. 0,0-0,0 #10203dc android:id/next_button}
-          com.android.internal.widget.ActionBarContainer{da5c07 V.ED..... ......ID 0,36-1200,132 #10201a4 android:id/action_bar_container}
-            android.widget.Toolbar{8276246 V.E...... ......ID 0,0-1200,96 #10201a3 android:id/action_bar}
-              android.widget.ImageButton{3cdae21 VFED..C.. ......ID 18,0-102,96}
-              android.widget.TextView{96d8134 V.ED..... ........ 120,25-514,70}
-              android.widget.ActionMenuView{2577ed8 V.E...... ........ 1182,0-1182,96}
-            com.android.internal.widget.ActionBarContextView{a12c7f1 G.E...... ......ID 0,0-0,0 #10201a8 android:id/action_context_bar}
-        android.view.View{7eb5770 V.ED..... ......ID 0,0-1200,36 #102002f android:id/statusBarBackground}
-    Looper (main, tid 2) {850bfd6}
-      Message 0: { when=+3m16s124ms callback=com.amazon.b.j target=android.os.Handler isAsync=false }
-      (Total messages: 1, polling=false, quitting=false)
-    Autofill Compat Mode: false
-    AutofillManager:
-      sessionId: -2147483648
-      state: UNKNOWN
-      context: com.amazon.switchaccess.SwitchAccessPreferenceActivity@7878123
-      client: com.amazon.switchaccess.SwitchAccessPreferenceActivity@7878123
-      enabled: false
-      hasService: true
-      hasCallback: false
-      onInvisibleCalled false
-      last autofilled data: null
-      tracked views: null
-      fillable ids: null
-      entered ids: null
-      save trigger id: null
-      save on finish(): false
-      compat mode enabled: false
-      debug: false verbose: false
-    ResourcesManager:
-      total apks: 3
-      resources: 4
-      resource impls: 4
-
-TASK 10196:org.fireosresearch.phase4.redirect id=32 userId=0
-  ACTIVITY org.fireosresearch.phase4.redirect/.ControlActivity 64534ba pid=8931
-    Local Activity 85dc65 State:
-      mResumed=false mStopped=true mFinished=false
-      mChangingConfigurations=false
-      mCurrentConfig={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1848) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=standard} s.6}
-      mLoadersStarted=true
-      FragmentManager misc state:
-        mHost=android.app.Activity$HostCallbacks@cc6b9b6
-        mContainer=android.app.Activity$HostCallbacks@cc6b9b6
-        mCurState=3 mStateSaved=true mDestroyed=false
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
-      mLastFrameTime=3766572 (119316 ms ago)
-    View Hierarchy:
-      DecorView@5f6b6b7[ControlActivity]
-        android.widget.LinearLayout{e41be24 V.E...... .......D 0,0-1200,1920}
-          android.view.ViewStub{dc51d8d G.E...... ......I. 0,0-0,0 #10201ad android:id/action_mode_bar_stub}
-          android.widget.FrameLayout{3fcbb42 V.E...... .......D 0,36-1200,1920 #1020002 android:id/content}
-            android.widget.LinearLayout{ab60753 V.E...... .......D 0,0-1200,1884}
-              android.widget.TextView{2ee9890 V.ED..... ........ 0,855-1200,956}
-              android.widget.ToggleButton{1730589 VFED..C.. ......ID 0,956-1200,1028}
-        android.view.View{a9f498e V.ED..... ......ID 0,0-1200,36 #102002f android:id/statusBarBackground}
-    Looper (main, tid 2) {fc5af}
-      (Total messages: 0, polling=false, quitting=false)
-    Autofill Compat Mode: false
-    AutofillManager:
-      sessionId: -2147483648
-      state: UNKNOWN
-      context: org.fireosresearch.phase4.redirect.ControlActivity@85dc65
-      client: org.fireosresearch.phase4.redirect.ControlActivity@85dc65
-      enabled: false
-      hasService: true
-      hasCallback: false
-      onInvisibleCalled false
-      last autofilled data: null
-      tracked views: null
```

### `appops/all.stdout.txt`

```diff
--- before/appops/all.stdout.txt

+++ after/appops/all.stdout.txt

@@ -58,190 +58,190 @@

     Package com.amazon.platform.fdrw:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:26:28.449 (-2h51m42s130ms)
+          Access: pers  = 2026-08-03 14:26:28.449 (-3h27m5s120ms)
     Package amazon.fireos:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 09:20:46.628 (-7h57m23s951ms)
+          Access: pers  = 2026-08-03 09:20:46.628 (-8h32m46s941ms)
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2026-03-26 23:43:10.017 (-129d17h35m0s562ms)
+          Reject: pers  = 2026-03-26 23:43:10.017 (-129d18h10m23s552ms)
     Package com.amazon.device.logmanager:
       RUN_IN_BACKGROUND (allow): 
-          Access: pers  = 2026-08-03 16:13:51.305 (-1h4m19s274ms)
+          Access: pers  = 2026-08-03 16:13:51.305 (-1h39m42s264ms)
     Package com.amazon.accessorynotifier:
       RUN_IN_BACKGROUND (allow): 
-          Access: pers  = 2026-08-03 16:13:52.826 (-1h4m17s753ms)
+          Access: pers  = 2026-08-03 16:13:52.826 (-1h39m40s743ms)
     Package com.amazon.android.marketplace:
       WRITE_SETTINGS (default): 
-          Reject: pers  = 2025-12-06 20:49:21.625 (-239d20h28m48s954ms)
+          Reject: pers  = 2025-12-06 20:49:21.625 (-239d21h4m11s944ms)
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-04-06 07:13:25.558 (-119d10h4m45s21ms)
+          Access: pers  = 2026-04-06 07:13:25.558 (-119d10h40m8s11ms)
     Package com.amazon.storagemanager:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 16:13:37.895 (-1h4m32s684ms)
+          Access: pers  = 2026-08-03 16:13:37.895 (-1h39m55s674ms)
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2026-08-03 07:45:44.987 (-9h32m25s592ms)
-      READ_EXTERNAL_STORAGE (allow): 
-          Access: pers  = 2026-08-03 07:45:41.642 (-9h32m28s937ms)
+          Reject: pers  = 2026-08-03 07:45:44.987 (-10h7m48s582ms)
+      READ_EXTERNAL_STORAGE (allow): 
+          Access: pers  = 2026-08-03 07:45:41.642 (-10h7m51s927ms)
     Package android:
       COARSE_LOCATION (allow): 
       FINE_LOCATION (allow / switch COARSE_LOCATION=allow): 
-          Access: pers  = 2026-08-03 16:13:42.326 (-1h4m28s253ms)
+          Access: pers  = 2026-08-03 16:13:42.326 (-1h39m51s243ms)
       READ_CALENDAR (allow): 
-          Access: pers  = 2026-08-03 16:13:48.515 (-1h4m22s64ms)
+          Access: pers  = 2026-08-03 16:13:48.515 (-1h39m45s54ms)
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:29:54.943 (-2h48m15s636ms)
+          Access: pers  = 2026-08-03 14:29:54.943 (-3h23m38s626ms)
       AUDIO_MEDIA_VOLUME (allow): 
-          Access: pers  = 2026-08-01 21:11:23.169 (-1d20h6m47s410ms)
-      WAKE_LOCK (allow): 
-          Access: pers  = 2026-08-03 17:13:56.810 (-4m13s769ms)
-                  fg    = 2026-04-11 03:58:41.049 (-114d13h19m29s530ms)
-          duration=+1ms
+          Access: pers  = 2026-08-01 21:11:23.169 (-1d20h42m10s400ms)
+      WAKE_LOCK (allow): 
+          Access: pers  = 2026-08-03 17:53:30.215 (-3s354ms)
+                  fg    = 2026-04-11 03:58:41.049 (-114d13h54m52s520ms)
+          duration=+46ms
       MONITOR_LOCATION (allow / switch COARSE_LOCATION=allow): 
-          Access: pers  = 2026-08-03 16:13:42.317 (-1h4m28s262ms)
-                  fg    = 2026-04-11 03:58:41.049 (-114d13h19m29s530ms)
-          Running start at: +1h4m27s956ms
+          Access: pers  = 2026-08-03 16:13:42.317 (-1h39m51s252ms)
+                  fg    = 2026-04-11 03:58:41.049 (-114d13h54m52s520ms)
+          Running start at: +1h39m50s946ms
           startNesting=1
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2026-08-03 17:06:36.343 (-11m34s236ms)
+          Reject: pers  = 2026-08-03 17:53:16.500 (-17s69ms)
       TURN_ON_SCREEN (allow): 
-          Access: pers  = 2026-07-10 22:35:34.059 (-23d18h42m36s520ms)
+          Access: pers  = 2026-07-10 22:35:34.059 (-23d19h17m59s510ms)
     Package com.android.providers.settings:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2025-12-06 20:11:38.894 (-239d21h6m31s685ms)
+          Access: pers  = 2025-12-06 20:11:38.894 (-239d21h41m54s675ms)
     Package com.android.keychain:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2025-12-07 15:30:49.435 (-239d1h47m21s144ms)
+          Access: pers  = 2025-12-07 15:30:49.435 (-239d2h22m44s134ms)
     Package com.amazon.device.sale.service:
       RUN_IN_BACKGROUND (allow): 
-          Access: pers  = 2026-08-03 16:14:05.671 (-1h4m4s908ms)
+          Access: pers  = 2026-08-03 16:14:05.671 (-1h39m27s898ms)
     Package com.android.settings:
       WRITE_SETTINGS (default): 
-          Reject: pers  = 2026-08-01 21:54:35.634 (-1d19h23m34s945ms)
+          Reject: pers  = 2026-08-01 21:54:35.634 (-1d19h58m57s935ms)
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2026-08-03 12:07:40.636 (-5h10m29s943ms)
+          Reject: pers  = 2026-08-03 12:07:40.636 (-5h45m52s933ms)
       TOAST_WINDOW (allow): 
-          Access: pers  = 2025-12-07 16:06:55.266 (-239d1h11m15s313ms)
+          Access: pers  = 2025-12-07 16:06:55.266 (-239d1h46m38s303ms)
           duration=+4s550ms
     Package android.amazon.perm:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2025-12-06 19:11:18.089 (-239d22h6m52s490ms)
+          Access: pers  = 2025-12-06 19:11:18.089 (-239d22h42m15s480ms)
     Package com.android.wallpaperbackup:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:32:08.417 (-2h46m2s162ms)
+          Access: pers  = 2026-08-03 14:32:08.417 (-3h21m25s152ms)
     Package com.android.location.fused:
       COARSE_LOCATION (allow): 
       FINE_LOCATION (allow / switch COARSE_LOCATION=allow): 
-          Access: pers  = 2025-12-06 18:57:45.955 (-239d22h20m24s624ms)
+          Access: pers  = 2025-12-06 18:57:45.955 (-239d22h55m47s614ms)
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:35:13.887 (-2h42m56s692ms)
+          Access: pers  = 2026-08-03 14:35:13.887 (-3h18m19s682ms)
       MONITOR_LOCATION (allow / switch COARSE_LOCATION=allow): 
-          Access: pers  = 2025-12-06 19:03:04.992 (-239d22h15m5s587ms)
+          Access: pers  = 2025-12-06 19:03:04.992 (-239d22h50m28s577ms)
           duration=+5m20s391ms
     Package com.here.odnp.service:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 15:54:11.972 (-1h23m58s607ms)
+          Access: pers  = 2026-08-03 15:54:11.972 (-1h59m21s597ms)
     Package com.amazon.settings:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 07:45:33.063 (-9h32m37s516ms)
+          Access: pers  = 2026-08-03 07:45:33.063 (-10h8m0s506ms)
       TOAST_WINDOW (allow): 
-          Access: pers  = 2026-07-10 21:04:18.363 (-23d20h13m52s216ms)
+          Access: pers  = 2026-07-10 21:04:18.363 (-23d20h49m15s206ms)
           duration=+5s388ms
     Package com.amazon.shpm:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 09:19:52.283 (-7h58m18s296ms)
+          Access: pers  = 2026-08-03 09:19:52.283 (-8h33m41s286ms)
     Package com.amazon.fireos.cirruscloud:
       RECORD_AUDIO (allow): 
-          Access: pers  = 2026-08-03 14:33:40.524 (-2h44m30s55ms)
+          Access: pers  = 2026-08-03 14:33:40.524 (-3h19m53s45ms)
   Uid 1002:
     state=cch  
     Package com.android.bluetooth:
       WAKE_LOCK (allow): 
-          Access: pers  = 2025-12-06 18:56:41.294 (-239d22h21m29s285ms)
-                  bg    = 2025-12-06 18:56:41.291 (-239d22h21m29s288ms)
+          Access: pers  = 2025-12-06 18:56:41.294 (-239d22h56m52s275ms)
+                  bg    = 2025-12-06 18:56:41.291 (-239d22h56m52s278ms)
           duration=+10ms
       GET_USAGE_STATS (default): 
-          Reject: pers  = 2025-12-06 18:56:24.496 (-239d22h21m46s83ms)
-      READ_EXTERNAL_STORAGE (allow): 
-          Access: pers  = 2025-12-06 18:56:28.924 (-239d22h21m41s655ms)
-                  cch   = 2025-12-06 18:56:23.700 (-239d22h21m46s879ms)
-      WRITE_EXTERNAL_STORAGE (allow): 
-          Access: pers  = 2025-12-06 18:56:28.924 (-239d22h21m41s655ms)
-                  cch   = 2025-12-06 18:56:23.700 (-239d22h21m46s879ms)
+          Reject: pers  = 2025-12-06 18:56:24.496 (-239d22h57m9s73ms)
+      READ_EXTERNAL_STORAGE (allow): 
+          Access: pers  = 2025-12-06 18:56:28.924 (-239d22h57m4s645ms)
+                  cch   = 2025-12-06 18:56:23.700 (-239d22h57m9s869ms)
+      WRITE_EXTERNAL_STORAGE (allow): 
+          Access: pers  = 2025-12-06 18:56:28.924 (-239d22h57m4s645ms)
+                  cch   = 2025-12-06 18:56:23.700 (-239d22h57m9s869ms)
   Uid 1041:
     state=cch  
     Package audioserver:
       WAKE_LOCK (allow): 
-          Access: cch   = 2026-08-03 16:51:31.806 (-26m38s773ms)
-          duration=+2s888ms
+          Access: cch   = 2026-08-03 17:50:21.253 (-3m12s316ms)
+          duration=+3s13ms
       GET_USAGE_STATS (default): 
-          Reject: cch   = 2026-08-03 16:13:38.716 (-1h4m31s863ms)
+          Reject: cch   = 2026-08-03 16:13:38.716 (-1h39m54s853ms)
   Uid 1068:
     state=pers 
     Package com.android.se:
       READ_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2026-08-03 16:13:43.435 (-1h4m27s144ms)
-      WRITE_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2026-08-03 16:13:43.435 (-1h4m27s144ms)
+          Access: cch   = 2026-08-03 16:13:43.435 (-1h39m50s134ms)
+      WRITE_EXTERNAL_STORAGE (allow): 
+          Access: cch   = 2026-08-03 16:13:43.435 (-1h39m50s134ms)
   Uid 2000:
     state=cch  
     Package com.android.shell:
       AUDIO_RING_VOLUME (allow): 
-          Access: cch   = 2025-12-07 15:02:29.916 (-239d2h15m40s663ms)
+          Access: cch   = 2025-12-07 15:02:29.916 (-239d2h51m3s653ms)
   Uid u0a5:
     state=cch  
     Package com.ivona.orchestrator:
       READ_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2025-12-07 16:06:13.286 (-239d1h11m57s293ms)
-      WRITE_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2025-12-07 16:06:13.286 (-239d1h11m57s293ms)
-      RUN_IN_BACKGROUND (allow): 
-          Access: bg    = 2025-12-06 19:02:54.041 (-239d22h15m16s538ms)
-                  cch   = 2025-12-06 19:02:51.359 (-239d22h15m19s220ms)
+          Access: cch   = 2025-12-07 16:06:13.286 (-239d1h47m20s283ms)
+      WRITE_EXTERNAL_STORAGE (allow): 
+          Access: cch   = 2025-12-07 16:06:13.286 (-239d1h47m20s283ms)
+      RUN_IN_BACKGROUND (allow): 
+          Access: bg    = 2025-12-06 19:02:54.041 (-239d22h50m39s528ms)
+                  cch   = 2025-12-06 19:02:51.359 (-239d22h50m42s210ms)
   Uid u0a6:
     state=cch  
     Package com.amazon.dp.fbcontacts:
       READ_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2026-08-03 16:13:56.403 (-1h4m14s176ms)
-      WRITE_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2026-08-03 16:13:56.403 (-1h4m14s176ms)
-      RUN_IN_BACKGROUND (allow): 
-          Access: cch   = 2026-08-03 16:13:56.402 (-1h4m14s177ms)
+          Access: cch   = 2026-08-03 16:13:56.403 (-1h39m37s166ms)
+      WRITE_EXTERNAL_STORAGE (allow): 
+          Access: cch   = 2026-08-03 16:13:56.403 (-1h39m37s166ms)
+      RUN_IN_BACKGROUND (allow): 
+          Access: cch   = 2026-08-03 16:13:56.402 (-1h39m37s167ms)
   Uid u0a7:
     state=fg   
     Package com.amazon.client.metrics:
       WAKE_LOCK (allow): 
-          Access: fgsvc = 2026-08-03 16:14:08.155 (-1h4m2s424ms)
-                  fg    = 2026-08-03 17:16:15.688 (-1m54s891ms)
-          duration=+248ms
-      READ_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2026-08-03 16:13:42.352 (-1h4m28s227ms)
-      WRITE_EXTERNAL_STORAGE (allow): 
-          Access: cch   = 2026-08-03 16:13:42.352 (-1h4m28s227ms)
+          Access: fgsvc = 2026-08-03 16:14:08.155 (-1h39m25s414ms)
+                  fg    = 2026-08-03 17:20:25.421 (-33m8s148ms)
+          duration=+1s123ms
+      READ_EXTERNAL_STORAGE (allow): 
+          Access: cch   = 2026-08-03 16:13:42.352 (-1h39m51s217ms)
+      WRITE_EXTERNAL_STORAGE (allow): 
+          Access: cch   = 2026-08-03 16:13:42.352 (-1h39m51s217ms)
   Uid u0a9:
     state=bg   
```

### `appops/firelauncher.stdout.txt`

```diff
--- before/appops/firelauncher.stdout.txt

+++ after/appops/firelauncher.stdout.txt

@@ -1,4 +1,4 @@

-TAKE_AUDIO_FOCUS: allow; time=+239d22h6m35s196ms ago
-READ_EXTERNAL_STORAGE: allow; time=+1h4m22s83ms ago
-WRITE_EXTERNAL_STORAGE: allow; time=+1h4m22s83ms ago
-REQUEST_DELETE_PACKAGES: allow; time=+239d1h13m36s921ms ago
+TAKE_AUDIO_FOCUS: allow; time=+239d22h41m58s212ms ago
+READ_EXTERNAL_STORAGE: allow; time=+1h39m45s99ms ago
+WRITE_EXTERNAL_STORAGE: allow; time=+1h39m45s99ms ago
+REQUEST_DELETE_PACKAGES: allow; time=+239d1h48m59s937ms ago
```

### `appops/microsoft.stdout.txt`

```diff
--- before/appops/microsoft.stdout.txt

+++ after/appops/microsoft.stdout.txt

@@ -1,5 +1,5 @@

 COARSE_LOCATION: allow
-FINE_LOCATION: allow; time=+3h33m32s954ms ago
-READ_EXTERNAL_STORAGE: allow; time=+32m14s456ms ago
-WRITE_EXTERNAL_STORAGE: allow; time=+32m14s456ms ago
-BIND_ACCESSIBILITY_SERVICE: allow; time=+13m21s990ms ago
+FINE_LOCATION: allow; time=+4h8m55s980ms ago
+READ_EXTERNAL_STORAGE: allow; time=+1h7m37s482ms ago
+WRITE_EXTERNAL_STORAGE: allow; time=+1h7m37s482ms ago
+BIND_ACCESSIBILITY_SERVICE: allow; time=+3s314ms ago
```

### `metadata.tsv`

```diff
--- before/metadata.tsv

+++ after/metadata.tsv

@@ -1,3 +1,3 @@

-test_id=PHASE4-ACCESSIBILITY-T03-BEFORE
+test_id=PHASE4-ACCESSIBILITY-T03-AFTER-ROLLBACK
 serial=G001LT0511550CFT
-timestamp_utc=2026-08-03T09:18:07Z
+timestamp_utc=2026-08-03T09:53:30Z
```

### `overlay/dump.stdout.txt`

```diff
--- before/overlay/dump.stdout.txt

+++ after/overlay/dump.stdout.txt

@@ -46,3 +46,3 @@

 Default overlays: 
 PackageInfo cache
-    10 package(s)
+    8 package(s)
```

### `package/all_packages.stdout.txt`

```diff
--- before/package/all_packages.stdout.txt

+++ after/package/all_packages.stdout.txt

@@ -29,5 +29,4 @@

 package:/system/priv-app/com.amazon.appaccesskeyprovider/com.amazon.appaccesskeyprovider.apk=com.amazon.appaccesskeyprovider
 package:/system/priv-app/ExternalStorageProvider/ExternalStorageProvider.apk=com.android.externalstorage
-package:/data/app/org.fireosresearch.phase4.redirect-HmZwcWLMh9DuFUo81iOafA==/base.apk=org.fireosresearch.phase4.redirect
 package:/system/priv-app/com.amazon.imdb.tv.mobile.app-stub/com.amazon.imdb.tv.mobile.app-stub.apk=com.amazon.imdb.tv.mobile.app
 package:/system/priv-app/com.amazon.dpcclient/com.amazon.dpcclient.apk=com.amazon.dpcclient
@@ -138,5 +137,4 @@

 package:/system/priv-app/amazon.jackson-19/amazon.jackson-19.apk=amazon.jackson19
 package:/system/priv-app/com.audible.application.kindle/com.audible.application.kindle.apk=com.audible.application.kindle
-package:/data/app/org.fireosresearch.phase4.alias-QPoOZGfYDGBm13QC130wVQ==/base.apk=org.fireosresearch.phase4.alias
 package:/system/priv-app/ManagedProvisioning/ManagedProvisioning.apk=com.android.managedprovisioning
 package:/system/priv-app/DeviceSoftwareOTA/DeviceSoftwareOTA.apk=com.amazon.device.software.ota
```

### `package/firelauncher.stdout.txt`

```diff
--- before/package/firelauncher.stdout.txt

+++ after/package/firelauncher.stdout.txt

@@ -855,11 +855,11 @@

 
 Package Changes:
-  Sequence number=14
+  Sequence number=16
   User 0:
     seq=0, package=org.fireosresearch.home.p0
     seq=4, package=com.google.android.gms
     seq=5, package=com.microsoft.launcher
-    seq=12, package=org.fireosresearch.phase4.redirect
-    seq=13, package=org.fireosresearch.phase4.alias
+    seq=14, package=org.fireosresearch.phase4.redirect
+    seq=15, package=org.fireosresearch.phase4.alias
 
 
```

### `package/home_query_cmd.stdout.txt`

```diff
--- before/package/home_query_cmd.stdout.txt

+++ after/package/home_query_cmd.stdout.txt

@@ -1,3 +1,3 @@

-7 activities found:
+3 activities found:
   Activity #0:
     priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
@@ -65,116 +65,4 @@

         HiddenApiEnforcementPolicy=2
   Activity #2:
-    priority=0 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
-    ActivityInfo:
-      name=org.fireosresearch.phase4.alias.HomeActivity
-      packageName=org.fireosresearch.phase4.alias
-      enabled=true exported=true directBootAware=false
-      taskAffinity=org.fireosresearch.phase4.alias targetActivity=null persistableMode=PERSIST_ROOT_ONLY
-      launchMode=2 flags=0x200 theme=0x0
-      screenOrientation=-1 configChanges=0x3 softInputMode=0x0
-      lockTaskLaunchMode=LOCK_TASK_LAUNCH_MODE_DEFAULT
-      resizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION
-      ApplicationInfo:
-        packageName=org.fireosresearch.phase4.alias
-        labelRes=0x0 nonLocalizedLabel=Phase 4 alias/filter probe icon=0x0 banner=0x0
-        processName=org.fireosresearch.phase4.alias
-        taskAffinity=org.fireosresearch.phase4.alias
-        uid=10197 flags=0x30e83e44 privateFlags=0x1100 theme=0x1030241
-        requiresSmallestWidthDp=0 compatibleWidthLimitDp=0 largestWidthLimitDp=0
-        sourceDir=/data/app/org.fireosresearch.phase4.alias-QPoOZGfYDGBm13QC130wVQ==/base.apk
-        seinfo=default:targetSdkVersion=28
-        seinfoUser=:complete
-        dataDir=/data/user/0/org.fireosresearch.phase4.alias
-        deviceProtectedDataDir=/data/user_de/0/org.fireosresearch.phase4.alias
-        credentialProtectedDataDir=/data/user/0/org.fireosresearch.phase4.alias
-        enabled=true minSdkVersion=28 targetSdkVersion=28 versionCode=1 targetSandboxVersion=1
-        supportsRtl=true
-        fullBackupContent=true
-        HiddenApiEnforcementPolicy=2
-  Activity #3:
-    priority=0 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
-    ActivityInfo:
-      name=org.fireosresearch.phase4.alias.HomeAliasDefault
-      packageName=org.fireosresearch.phase4.alias
-      enabled=true exported=true directBootAware=false
-      taskAffinity=org.fireosresearch.phase4.alias targetActivity=org.fireosresearch.phase4.alias.HomeActivity persistableMode=PERSIST_ROOT_ONLY
-      launchMode=2 flags=0x200 theme=0x0
-      screenOrientation=-1 configChanges=0x3 softInputMode=0x0
-      lockTaskLaunchMode=LOCK_TASK_LAUNCH_MODE_DEFAULT
-      resizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION
-      ApplicationInfo:
-        packageName=org.fireosresearch.phase4.alias
-        labelRes=0x0 nonLocalizedLabel=Phase 4 alias/filter probe icon=0x0 banner=0x0
-        processName=org.fireosresearch.phase4.alias
-        taskAffinity=org.fireosresearch.phase4.alias
-        uid=10197 flags=0x30e83e44 privateFlags=0x1100 theme=0x1030241
-        requiresSmallestWidthDp=0 compatibleWidthLimitDp=0 largestWidthLimitDp=0
-        sourceDir=/data/app/org.fireosresearch.phase4.alias-QPoOZGfYDGBm13QC130wVQ==/base.apk
-        seinfo=default:targetSdkVersion=28
-        seinfoUser=:complete
-        dataDir=/data/user/0/org.fireosresearch.phase4.alias
-        deviceProtectedDataDir=/data/user_de/0/org.fireosresearch.phase4.alias
-        credentialProtectedDataDir=/data/user/0/org.fireosresearch.phase4.alias
-        enabled=true minSdkVersion=28 targetSdkVersion=28 versionCode=1 targetSandboxVersion=1
-        supportsRtl=true
-        fullBackupContent=true
-        HiddenApiEnforcementPolicy=2
-  Activity #4:
-    priority=0 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
-    ActivityInfo:
-      name=org.fireosresearch.phase4.alias.DirectBootHomeActivity
-      packageName=org.fireosresearch.phase4.alias
-      enabled=true exported=true directBootAware=true
-      taskAffinity=org.fireosresearch.phase4.alias targetActivity=null persistableMode=PERSIST_ROOT_ONLY
-      launchMode=0 flags=0x200 theme=0x0
-      screenOrientation=-1 configChanges=0x3 softInputMode=0x0
-      lockTaskLaunchMode=LOCK_TASK_LAUNCH_MODE_DEFAULT
-      resizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION
-      ApplicationInfo:
-        packageName=org.fireosresearch.phase4.alias
-        labelRes=0x0 nonLocalizedLabel=Phase 4 alias/filter probe icon=0x0 banner=0x0
-        processName=org.fireosresearch.phase4.alias
-        taskAffinity=org.fireosresearch.phase4.alias
-        uid=10197 flags=0x30e83e44 privateFlags=0x1100 theme=0x1030241
-        requiresSmallestWidthDp=0 compatibleWidthLimitDp=0 largestWidthLimitDp=0
-        sourceDir=/data/app/org.fireosresearch.phase4.alias-QPoOZGfYDGBm13QC130wVQ==/base.apk
-        seinfo=default:targetSdkVersion=28
-        seinfoUser=:complete
-        dataDir=/data/user/0/org.fireosresearch.phase4.alias
-        deviceProtectedDataDir=/data/user_de/0/org.fireosresearch.phase4.alias
-        credentialProtectedDataDir=/data/user/0/org.fireosresearch.phase4.alias
-        enabled=true minSdkVersion=28 targetSdkVersion=28 versionCode=1 targetSandboxVersion=1
-        supportsRtl=true
-        fullBackupContent=true
-        HiddenApiEnforcementPolicy=2
-  Activity #5:
-    priority=0 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=false
-    ActivityInfo:
-      name=org.fireosresearch.phase4.alias.HomeAliasHomeOnly
-      packageName=org.fireosresearch.phase4.alias
-      enabled=true exported=true directBootAware=false
-      taskAffinity=org.fireosresearch.phase4.alias targetActivity=org.fireosresearch.phase4.alias.HomeActivity persistableMode=PERSIST_ROOT_ONLY
-      launchMode=2 flags=0x200 theme=0x0
-      screenOrientation=-1 configChanges=0x3 softInputMode=0x0
-      lockTaskLaunchMode=LOCK_TASK_LAUNCH_MODE_DEFAULT
-      resizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION
-      ApplicationInfo:
-        packageName=org.fireosresearch.phase4.alias
-        labelRes=0x0 nonLocalizedLabel=Phase 4 alias/filter probe icon=0x0 banner=0x0
-        processName=org.fireosresearch.phase4.alias
-        taskAffinity=org.fireosresearch.phase4.alias
-        uid=10197 flags=0x30e83e44 privateFlags=0x1100 theme=0x1030241
-        requiresSmallestWidthDp=0 compatibleWidthLimitDp=0 largestWidthLimitDp=0
-        sourceDir=/data/app/org.fireosresearch.phase4.alias-QPoOZGfYDGBm13QC130wVQ==/base.apk
-        seinfo=default:targetSdkVersion=28
-        seinfoUser=:complete
-        dataDir=/data/user/0/org.fireosresearch.phase4.alias
-        deviceProtectedDataDir=/data/user_de/0/org.fireosresearch.phase4.alias
-        credentialProtectedDataDir=/data/user/0/org.fireosresearch.phase4.alias
-        enabled=true minSdkVersion=28 targetSdkVersion=28 versionCode=1 targetSandboxVersion=1
-        supportsRtl=true
-        fullBackupContent=true
-        HiddenApiEnforcementPolicy=2
-  Activity #6:
     priority=-1000 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
     ActivityInfo:
```

### `package/home_query_pm.stdout.txt`

```diff
--- before/package/home_query_pm.stdout.txt

+++ after/package/home_query_pm.stdout.txt

@@ -1,3 +1,3 @@

-7 activities found:
+3 activities found:
   Activity #0:
     priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
@@ -65,116 +65,4 @@

         HiddenApiEnforcementPolicy=2
   Activity #2:
-    priority=0 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
-    ActivityInfo:
-      name=org.fireosresearch.phase4.alias.HomeActivity
-      packageName=org.fireosresearch.phase4.alias
-      enabled=true exported=true directBootAware=false
-      taskAffinity=org.fireosresearch.phase4.alias targetActivity=null persistableMode=PERSIST_ROOT_ONLY
-      launchMode=2 flags=0x200 theme=0x0
-      screenOrientation=-1 configChanges=0x3 softInputMode=0x0
-      lockTaskLaunchMode=LOCK_TASK_LAUNCH_MODE_DEFAULT
-      resizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION
-      ApplicationInfo:
-        packageName=org.fireosresearch.phase4.alias
-        labelRes=0x0 nonLocalizedLabel=Phase 4 alias/filter probe icon=0x0 banner=0x0
-        processName=org.fireosresearch.phase4.alias
-        taskAffinity=org.fireosresearch.phase4.alias
-        uid=10197 flags=0x30e83e44 privateFlags=0x1100 theme=0x1030241
-        requiresSmallestWidthDp=0 compatibleWidthLimitDp=0 largestWidthLimitDp=0
-        sourceDir=/data/app/org.fireosresearch.phase4.alias-QPoOZGfYDGBm13QC130wVQ==/base.apk
-        seinfo=default:targetSdkVersion=28
-        seinfoUser=:complete
-        dataDir=/data/user/0/org.fireosresearch.phase4.alias
-        deviceProtectedDataDir=/data/user_de/0/org.fireosresearch.phase4.alias
-        credentialProtectedDataDir=/data/user/0/org.fireosresearch.phase4.alias
-        enabled=true minSdkVersion=28 targetSdkVersion=28 versionCode=1 targetSandboxVersion=1
-        supportsRtl=true
-        fullBackupContent=true
-        HiddenApiEnforcementPolicy=2
-  Activity #3:
-    priority=0 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
-    ActivityInfo:
-      name=org.fireosresearch.phase4.alias.HomeAliasDefault
-      packageName=org.fireosresearch.phase4.alias
-      enabled=true exported=true directBootAware=false
-      taskAffinity=org.fireosresearch.phase4.alias targetActivity=org.fireosresearch.phase4.alias.HomeActivity persistableMode=PERSIST_ROOT_ONLY
-      launchMode=2 flags=0x200 theme=0x0
-      screenOrientation=-1 configChanges=0x3 softInputMode=0x0
-      lockTaskLaunchMode=LOCK_TASK_LAUNCH_MODE_DEFAULT
-      resizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION
-      ApplicationInfo:
-        packageName=org.fireosresearch.phase4.alias
-        labelRes=0x0 nonLocalizedLabel=Phase 4 alias/filter probe icon=0x0 banner=0x0
-        processName=org.fireosresearch.phase4.alias
-        taskAffinity=org.fireosresearch.phase4.alias
-        uid=10197 flags=0x30e83e44 privateFlags=0x1100 theme=0x1030241
-        requiresSmallestWidthDp=0 compatibleWidthLimitDp=0 largestWidthLimitDp=0
-        sourceDir=/data/app/org.fireosresearch.phase4.alias-QPoOZGfYDGBm13QC130wVQ==/base.apk
-        seinfo=default:targetSdkVersion=28
-        seinfoUser=:complete
-        dataDir=/data/user/0/org.fireosresearch.phase4.alias
-        deviceProtectedDataDir=/data/user_de/0/org.fireosresearch.phase4.alias
-        credentialProtectedDataDir=/data/user/0/org.fireosresearch.phase4.alias
-        enabled=true minSdkVersion=28 targetSdkVersion=28 versionCode=1 targetSandboxVersion=1
-        supportsRtl=true
-        fullBackupContent=true
-        HiddenApiEnforcementPolicy=2
-  Activity #4:
-    priority=0 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
-    ActivityInfo:
-      name=org.fireosresearch.phase4.alias.DirectBootHomeActivity
-      packageName=org.fireosresearch.phase4.alias
-      enabled=true exported=true directBootAware=true
-      taskAffinity=org.fireosresearch.phase4.alias targetActivity=null persistableMode=PERSIST_ROOT_ONLY
-      launchMode=0 flags=0x200 theme=0x0
-      screenOrientation=-1 configChanges=0x3 softInputMode=0x0
-      lockTaskLaunchMode=LOCK_TASK_LAUNCH_MODE_DEFAULT
-      resizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION
-      ApplicationInfo:
-        packageName=org.fireosresearch.phase4.alias
-        labelRes=0x0 nonLocalizedLabel=Phase 4 alias/filter probe icon=0x0 banner=0x0
-        processName=org.fireosresearch.phase4.alias
-        taskAffinity=org.fireosresearch.phase4.alias
-        uid=10197 flags=0x30e83e44 privateFlags=0x1100 theme=0x1030241
-        requiresSmallestWidthDp=0 compatibleWidthLimitDp=0 largestWidthLimitDp=0
-        sourceDir=/data/app/org.fireosresearch.phase4.alias-QPoOZGfYDGBm13QC130wVQ==/base.apk
-        seinfo=default:targetSdkVersion=28
-        seinfoUser=:complete
-        dataDir=/data/user/0/org.fireosresearch.phase4.alias
-        deviceProtectedDataDir=/data/user_de/0/org.fireosresearch.phase4.alias
-        credentialProtectedDataDir=/data/user/0/org.fireosresearch.phase4.alias
-        enabled=true minSdkVersion=28 targetSdkVersion=28 versionCode=1 targetSandboxVersion=1
-        supportsRtl=true
-        fullBackupContent=true
-        HiddenApiEnforcementPolicy=2
-  Activity #5:
-    priority=0 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=false
-    ActivityInfo:
-      name=org.fireosresearch.phase4.alias.HomeAliasHomeOnly
-      packageName=org.fireosresearch.phase4.alias
-      enabled=true exported=true directBootAware=false
-      taskAffinity=org.fireosresearch.phase4.alias targetActivity=org.fireosresearch.phase4.alias.HomeActivity persistableMode=PERSIST_ROOT_ONLY
-      launchMode=2 flags=0x200 theme=0x0
-      screenOrientation=-1 configChanges=0x3 softInputMode=0x0
-      lockTaskLaunchMode=LOCK_TASK_LAUNCH_MODE_DEFAULT
-      resizeMode=RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION
-      ApplicationInfo:
-        packageName=org.fireosresearch.phase4.alias
-        labelRes=0x0 nonLocalizedLabel=Phase 4 alias/filter probe icon=0x0 banner=0x0
-        processName=org.fireosresearch.phase4.alias
-        taskAffinity=org.fireosresearch.phase4.alias
-        uid=10197 flags=0x30e83e44 privateFlags=0x1100 theme=0x1030241
-        requiresSmallestWidthDp=0 compatibleWidthLimitDp=0 largestWidthLimitDp=0
-        sourceDir=/data/app/org.fireosresearch.phase4.alias-QPoOZGfYDGBm13QC130wVQ==/base.apk
-        seinfo=default:targetSdkVersion=28
-        seinfoUser=:complete
-        dataDir=/data/user/0/org.fireosresearch.phase4.alias
-        deviceProtectedDataDir=/data/user_de/0/org.fireosresearch.phase4.alias
-        credentialProtectedDataDir=/data/user/0/org.fireosresearch.phase4.alias
-        enabled=true minSdkVersion=28 targetSdkVersion=28 versionCode=1 targetSandboxVersion=1
-        supportsRtl=true
-        fullBackupContent=true
-        HiddenApiEnforcementPolicy=2
-  Activity #6:
     priority=-1000 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
     ActivityInfo:
```

### `settings/secure.stdout.txt`

```diff
--- before/settings/secure.stdout.txt

+++ after/settings/secure.stdout.txt

@@ -42,5 +42,5 @@

 accessibility_display_magnification_mode=0
 accessibility_display_magnification_scale=2.0
-accessibility_enabled=1
+accessibility_enabled=0
 accessibility_shortcut=none
 accessory_name=
@@ -101,5 +101,5 @@

 enable_find_my_device=-1
 enable_launcher_tutorial=1
-enabled_accessibility_services=org.fireosresearch.phase4.redirect/org.fireosresearch.phase4.redirect.LauncherRedirectService
+enabled_accessibility_services=
 enabled_input_methods=com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME:com.google.android.googlequicksearchbox/com.google.android.voicesearch.ime.VoiceInputMethodService
 enabled_notification_assistant=android.ext.services/android.ext.services.notification.Assistant
```

### `summary.md`

```diff
--- before/summary.md

+++ after/summary.md

@@ -1,7 +1,7 @@

 # Phase 3C state snapshot
 
-- Test ID: PHASE4-ACCESSIBILITY-T03-BEFORE
+- Test ID: PHASE4-ACCESSIBILITY-T03-AFTER-ROLLBACK
 - Serial: G001LT0511550CFT
-- Timestamp UTC: 2026-08-03T09:18:10Z
+- Timestamp UTC: 2026-08-03T09:53:33Z
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
-    Last logged in: +1h4m26s552ms ago
+    Last logged in: +1h39m49s321ms ago
     Last logged in fingerprint: Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys
-    Start time: +1h4m30s774ms ago
-    Unlock time: +1h4m26s382ms ago
+    Start time: +1h39m53s543ms ago
+    Unlock time: +1h39m49s151ms ago
     Has profile owner: true
     Restrictions:
```

### `window/input.stdout.txt`

```diff
--- before/window/input.stdout.txt

+++ after/window/input.stdout.txt

@@ -452,32 +452,28 @@

   DispatchEnabled: 1
   DispatchFrozen: 0
-  FocusedApplication: name='AppWindowToken{e63cf5a token=Token{d3a1305 ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}}}', dispatchingTimeout=5000.000ms
-  FocusedWindow: name='Window{80793f7 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}'
-  TouchStatesByDisplay:
-    0: down=false, split=false, deviceId=0, source=0x00002002
-      Windows: <none>
+  FocusedApplication: name='AppWindowToken{c1e3d55 token=Token{f1fe00c ActivityRecord{7620f3f u0 com.android.launcher3/com.android.quickstep.RecentsActivity t36}}}', dispatchingTimeout=5000.000ms
+  FocusedWindow: name='Window{ced5e7a u0 com.android.launcher3/com.android.quickstep.RecentsActivity}'
+  TouchStates: <no displays touched>
   Windows:
     0: name='Window{18aa5ec u0 SpeechUi}', displayId=0, paused=false, hasFocus=false, hasWallpaper=false, visible=true, canReceiveKeys=false, flags=0x01000118, type=0x000007df, layer=0, frame=[0,0][1200,1920], scale=1.000000, touchableRegion=[0,0][1200,1920], inputFeatures=0x00000000, ownerPid=1842, ownerUid=10035, dispatchingTimeout=5000.000ms
-    1: name='Window{a15b6a6 u0 NavigationBar}', displayId=0, paused=false, hasFocus=false, hasWallpaper=false, visible=false, canReceiveKeys=false, flags=0x21840068, type=0x000007e3, layer=0, frame=[0,1848][1200,1920], scale=1.000000, touchableRegion=[0,1848][1200,1920], inputFeatures=0x00000000, ownerPid=1150, ownerUid=10036, dispatchingTimeout=5000.000ms
+    1: name='Window{a15b6a6 u0 NavigationBar}', displayId=0, paused=false, hasFocus=false, hasWallpaper=false, visible=true, canReceiveKeys=false, flags=0x21840068, type=0x000007e3, layer=0, frame=[0,1848][1200,1920], scale=1.000000, touchableRegion=[0,1848][1200,1920], inputFeatures=0x00000000, ownerPid=1150, ownerUid=10036, dispatchingTimeout=5000.000ms
     2: name='Window{f9d34f4 u0 StatusBar}', displayId=0, paused=false, hasFocus=false, hasWallpaper=false, visible=true, canReceiveKeys=false, flags=0x81840048, type=0x000007d0, layer=0, frame=[0,0][1200,36], scale=1.000000, touchableRegion=[0,0][1200,36], inputFeatures=0x00000000, ownerPid=1150, ownerUid=10036, dispatchingTimeout=5000.000ms
     3: name='Window{d69e296 u0 DockedStackDivider}', displayId=0, paused=false, hasFocus=false, hasWallpaper=false, visible=false, canReceiveKeys=false, flags=0x21840028, type=0x000007f2, layer=0, frame=[0,0][0,0], scale=1.000000, touchableRegion=[-72,0][72,72], inputFeatures=0x00000000, ownerPid=1150, ownerUid=10036, dispatchingTimeout=5000.000ms
-    4: name='Window{80793f7 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}', displayId=0, paused=false, hasFocus=true, hasWallpaper=true, visible=true, canReceiveKeys=true, flags=0x81910120, type=0x00000001, layer=0, frame=[0,0][1200,1920], scale=1.000000, touchableRegion=[0,0][1200,1920], inputFeatures=0x00000000, ownerPid=1942, ownerUid=10120, dispatchingTimeout=5000.000ms
-    5: name='Window{f2b1d28 u0 org.fireosresearch.phase4.redirect/org.fireosresearch.phase4.redirect.ControlActivity}', displayId=0, paused=false, hasFocus=false, hasWallpaper=false, visible=false, canReceiveKeys=false, flags=0x81810120, type=0x00000001, layer=0, frame=[0,0][1200,1920], scale=1.000000, touchableRegion=[0,0][1200,1920], inputFeatures=0x00000000, ownerPid=8931, ownerUid=10196, dispatchingTimeout=5000.000ms
-    6: name='Window{ecbc856 u0 com.amazon.switchaccess.root/com.amazon.switchaccess.SwitchAccessPreferenceActivity}', displayId=0, paused=false, hasFocus=false, hasWallpaper=false, visible=false, canReceiveKeys=false, flags=0x81810120, type=0x00000001, layer=0, frame=[0,0][1200,1920], scale=1.000000, touchableRegion=[0,0][1200,1920], inputFeatures=0x00000000, ownerPid=9075, ownerUid=10134, dispatchingTimeout=5000.000ms
-    7: name='Window{5aaf091 u0 com.amazon.settings/com.amazon.settings.accessibility.AccessibilitySettingsActivity}', displayId=0, paused=false, hasFocus=false, hasWallpaper=false, visible=false, canReceiveKeys=false, flags=0x81810120, type=0x00000001, layer=0, frame=[0,0][1200,1920], scale=1.000000, touchableRegion=[0,0][1200,1920], inputFeatures=0x00000000, ownerPid=8976, ownerUid=1000, dispatchingTimeout=5000.000ms
-    8: name='Window{525cba u0 com.android.systemui.ImageWallpaper}', displayId=0, paused=false, hasFocus=false, hasWallpaper=false, visible=true, canReceiveKeys=false, flags=0x00010318, type=0x000007dd, layer=0, frame=[0,0][1920,1920], scale=1.000000, touchableRegion=[0,0][1920,1920], inputFeatures=0x00000000, ownerPid=1150, ownerUid=10036, dispatchingTimeout=5000.000ms
+    4: name='Window{ced5e7a u0 com.android.launcher3/com.android.quickstep.RecentsActivity}', displayId=0, paused=false, hasFocus=true, hasWallpaper=true, visible=true, canReceiveKeys=true, flags=0x81910120, type=0x00000001, layer=0, frame=[0,0][1200,1920], scale=1.000000, touchableRegion=[0,0][1200,1920], inputFeatures=0x00000000, ownerPid=1923, ownerUid=10075, dispatchingTimeout=5000.000ms
+    5: name='Window{80793f7 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher EXITING}', displayId=0, paused=false, hasFocus=false, hasWallpaper=false, visible=false, canReceiveKeys=false, flags=0x81910120, type=0x00000001, layer=0, frame=[0,0][1200,1920], scale=1.000000, touchableRegion=[0,0][1200,1920], inputFeatures=0x00000000, ownerPid=1942, ownerUid=10120, dispatchingTimeout=5000.000ms
+    6: name='Window{525cba u0 com.android.systemui.ImageWallpaper}', displayId=0, paused=false, hasFocus=false, hasWallpaper=false, visible=true, canReceiveKeys=false, flags=0x00010318, type=0x000007dd, layer=0, frame=[0,0][1920,1920], scale=1.000000, touchableRegion=[0,0][1920,1920], inputFeatures=0x00000000, ownerPid=1150, ownerUid=10036, dispatchingTimeout=5000.000ms
   MonitoringChannels:
     0: 'WindowManager (server)'
   RecentQueue: length=10
-    KeyEvent, age=59848.5ms
-    KeyEvent, age=59848.5ms
-    KeyEvent, age=57472.5ms
-    KeyEvent, age=57472.5ms
-    KeyEvent, age=55078.5ms
-    KeyEvent, age=55078.5ms
-    KeyEvent, age=52692.5ms
-    KeyEvent, age=52692.5ms
-    KeyEvent, age=50331.5ms
-    KeyEvent, age=50331.5ms
+    MotionEvent, age=386.8ms
+    MotionEvent, age=269.1ms
+    MotionEvent, age=261.0ms
+    MotionEvent, age=252.8ms
+    MotionEvent, age=244.4ms
+    MotionEvent, age=236.3ms
+    MotionEvent, age=227.7ms
+    MotionEvent, age=219.6ms
+    MotionEvent, age=211.0ms
+    MotionEvent, age=204.0ms
   PendingEvent: <none>
   InboundQueue: <empty>
@@ -502,17 +498,11 @@

       OutboundQueue: <empty>
       WaitQueue: <empty>
-    6: channelName='ecbc856 com.amazon.switchaccess.root/com.amazon.switchaccess.SwitchAccessPreferenceActivity (server)', windowName='Window{ecbc856 u0 com.amazon.switchaccess.root/com.amazon.switchaccess.SwitchAccessPreferenceActivity}', status=NORMAL, monitor=false, inputPublisherBlocked=false
-      OutboundQueue: <empty>
-      WaitQueue: <empty>
-    7: channelName='80793f7 com.amazon.firelauncher/com.amazon.firelauncher.Launcher (server)', windowName='Window{80793f7 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}', status=NORMAL, monitor=false, inputPublisherBlocked=false
-      OutboundQueue: <empty>
-      WaitQueue: <empty>
-    8: channelName='18aa5ec SpeechUi (server)', windowName='Window{18aa5ec u0 SpeechUi}', status=NORMAL, monitor=false, inputPublisherBlocked=false
-      OutboundQueue: <empty>
-      WaitQueue: <empty>
-    9: channelName='5aaf091 com.amazon.settings/com.amazon.settings.accessibility.AccessibilitySettingsActivity (server)', windowName='Window{5aaf091 u0 com.amazon.settings/com.amazon.settings.accessibility.AccessibilitySettingsActivity}', status=NORMAL, monitor=false, inputPublisherBlocked=false
-      OutboundQueue: <empty>
-      WaitQueue: <empty>
-    10: channelName='f2b1d28 org.fireosresearch.phase4.redirect/org.fireosresearch.phase4.redirect.ControlActivity (server)', windowName='Window{f2b1d28 u0 org.fireosresearch.phase4.redirect/org.fireosresearch.phase4.redirect.ControlActivity}', status=NORMAL, monitor=false, inputPublisherBlocked=false
+    6: channelName='80793f7 com.amazon.firelauncher/com.amazon.firelauncher.Launcher (server)', windowName='Window{80793f7 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher EXITING}', status=NORMAL, monitor=false, inputPublisherBlocked=false
+      OutboundQueue: <empty>
+      WaitQueue: <empty>
+    7: channelName='18aa5ec SpeechUi (server)', windowName='Window{18aa5ec u0 SpeechUi}', status=NORMAL, monitor=false, inputPublisherBlocked=false
+      OutboundQueue: <empty>
+      WaitQueue: <empty>
+    8: channelName='ced5e7a com.android.launcher3/com.android.quickstep.RecentsActivity (server)', windowName='Window{ced5e7a u0 com.android.launcher3/com.android.quickstep.RecentsActivity}', status=NORMAL, monitor=false, inputPublisherBlocked=false
       OutboundQueue: <empty>
       WaitQueue: <empty>
```

### `window/processes.stdout.txt`

```diff
--- before/window/processes.stdout.txt

+++ after/window/processes.stdout.txt

@@ -19,5 +19,4 @@

 root            23     2 [migration/4]               [migration/4]
 root            24     2 [ksoftirqd/4]               [ksoftirqd/4]
-root            25     2 [kworker/4:0]               [kworker/4:0]
 root            26     2 [kworker/4:0H]              [kworker/4:0H]
 root            27     2 [migration/5]               [migration/5]
@@ -312,10 +311,8 @@

 webview_zygote 1132  353 webview_zygote              webview_zygote
 u0_a36        1150   352 com.android.systemui        com.android.systemui
-u0_a74        1176   352 com.amazon.kindle.kso       com.amazon.kindle.kso
 root          1193     2 [kworker/5:2]               [kworker/5:2]
 system        1197   352 com.here.odnp.service:remote com.here.odnp.service:remote
 u0_a43        1289   352 com.amazon.imp              com.amazon.imp
 u0_a59        1327   352 android.ext.services        android.ext.services
-root          1452     2 [kbase_event]               [kbase_event]
 root          1487     2 [kbase_event]               [kbase_event]
 root          1513     1 perfmonitord                perfmonitord
@@ -332,61 +329,56 @@

 u0_a120       1942   352 com.amazon.firelauncher     com.amazon.firelauncher
 u0_a179       2021   352 com.google.android.gms      com.google.android.gms
-u0_a179       2160   352 com.google.process.gservices com.google.process.gservices
 u0_a41        2279   352 com.amazon.platform         com.amazon.platform
 u0_a26        2503   352 com.amazon.kindle.unifiedSearch com.amazon.kindle.unifiedSearch
 root          3044     2 [kbase_event]               [kbase_event]
 root          3061     2 [kworker/6:2]               [kworker/6:2]
-u0_a132       3290   353 com.amazon.adep             com.amazon.adep
 system        3506   352 com.amazon.device.services  com.amazon.device.services
 u0_a9         3558   352 com.amazon.diode            com.amazon.diode
 u0_a126       3866   352 com.amazon.whisperlink.core.android com.amazon.whisperlink.core.android
-u0_a180       4055   352 com.android.vending         com.android.vending
-u0_a70        5391   352 com.amazon.appverification  com.amazon.appverification
 u0_a58        5875   352 com.amazon.parentalcontrols com.amazon.parentalcontrols
-root          5949     2 [kworker/0:0]               [kworker/0:0]
 root          6105     2 [kworker/u16:5]             [kworker/u16:5]
 u0_a136       6711   352 com.android.defcontainer    com.android.defcontainer
 u0_a17        6921   352 com.amazon.device.software.ota com.amazon.device.software.ota
-u0_a90        6950   352 com.amazon.dcpms.fos.service com.amazon.dcpms.fos.service
-system        7006   352 com.android.settings        com.android.settings
 u0_a14        7043   352 com.android.providers.downloads com.android.providers.downloads
 u0_a76        7084   353 com.amazon.venezia          com.amazon.venezia
 root          7098     2 [kbase_event]               [kbase_event]
-u0_a76        7112   353 com.amazon.venezia:sync     com.amazon.venezia:sync
 u0_a27        7179   352 com.amazon.sync.service     com.amazon.sync.service
 root          7209     2 [kbase_event]               [kbase_event]
-system        7316   352 com.android.keychain        com.android.keychain
-u0_a107       7341   352 com.android.documentsui     com.android.documentsui
-u0_a180       7375   352 com.android.vending:background com.android.vending:background
-root          8530     2 [kworker/u16:4]             [kworker/u16:4]
 shell         8533   432 sh                          sh -c CLASSPATH=/data/local/tmp/scrcpy-server.jar app_process / com.genymobile.scrcpy.Server 4.1 scid=05106434 log_level=info
 shell         8535  8533 app_process                 app_process / com.genymobile.scrcpy.Server 4.1 scid=05106434 log_level=info
 shell         8545  8535 app_process                 app_process / com.genymobile.scrcpy.CleanUp 0 -1 false false -1 -1
-root          8583     2 [kworker/u17:1]             [kworker/u17:1]
-u0_a33        8585   352 android.process.acore       android.process.acore
-root          8681     2 [kworker/u17:2]             [kworker/u17:2]
-root          8844     2 [kworker/u16:3]             [kworker/u16:3]
-root          8845     2 [kworker/u16:6]             [kworker/u16:6]
-root          8846     2 [kworker/u16:7]             [kworker/u16:7]
-u0_a196       8931   352 org.fireosresearch.phase4.redirect org.fireosresearch.phase4.redirect
-root          8952     2 [kbase_event]               [kbase_event]
-system        8976   352 com.amazon.settings         com.amazon.settings
 root          8991     2 [kworker/u16:9]             [kworker/u16:9]
-root          9009     2 [kbase_event]               [kbase_event]
-root          9061     2 [kworker/0:2]               [kworker/0:2]
-u0_a134       9075   352 com.amazon.switchaccess.root com.amazon.switchaccess.root
-root          9097     2 [kbase_event]               [kbase_event]
-u0_a103       9125   353 com.ivona.tts.oem           com.ivona.tts.oem
-root          9469     2 [kworker/4:1]               [kworker/4:1]
-root          9872     2 [kworker/3:2]               [kworker/3:2]
-root          9896     2 [kworker/u17:0]             [kworker/u17:0]
-root          9942     2 [kworker/u16:0]             [kworker/u16:0]
-root          9943     2 [kworker/u16:1]             [kworker/u16:1]
-root          9944     2 [kworker/u16:2]             [kworker/u16:2]
 u0_a69        9945   352 com.amazon.wifilocker       com.amazon.wifilocker
 u0_a104       9982   352 com.amazon.sync.provider.ipc com.amazon.sync.provider.ipc
-root         10008     2 [kworker/4:2]               [kworker/4:2]
-root         10012     2 [kworker/0:1]               [kworker/0:1]
-root         10021     2 [kworker/3:0]               [kworker/3:0]
-root         10850   497 sleep                       sleep 120
-shell        10942   432 ps                          ps -A -o USER,PID,PPID,NAME,ARGS
+root         11793     2 [kworker/0:2]               [kworker/0:2]
+u0_a179      11925   352 com.google.process.gservices com.google.process.gservices
+root         11970     2 [kworker/4:2]               [kworker/4:2]
+root         11972     2 [kworker/u16:1]             [kworker/u16:1]
+root         11990     2 [kworker/u17:0]             [kworker/u17:0]
+root         11991     2 [kworker/0:1]               [kworker/0:1]
+root         12009     2 [kworker/4:0]               [kworker/4:0]
+root         12027     2 [kworker/u16:0]             [kworker/u16:0]
+root         12045     2 [kworker/u17:2]             [kworker/u17:2]
+root         12065     2 [kworker/u16:2]             [kworker/u16:2]
+root         12066     2 [kworker/u16:3]             [kworker/u16:3]
+root         12070     2 [kworker/3:0]               [kworker/3:0]
+root         12088     2 [kworker/u16:12]            [kworker/u16:12]
+root         12089     2 [kworker/u16:13]            [kworker/u16:13]
+root         12090     2 [kworker/u16:14]            [kworker/u16:14]
+root         12091     2 [kworker/u16:15]            [kworker/u16:15]
+u0_a177      12104   352 com.aurora.store            com.aurora.store
+root         12150     2 [kworker/0:0]               [kworker/0:0]
+root         12169     2 [kworker/u17:1]             [kworker/u17:1]
+u0_a182      12170   352 com.google.android.youtube  com.google.android.youtube
+root         12272     2 [kbase_event]               [kbase_event]
+root         12322     2 [kworker/3:2]               [kworker/3:2]
+root         12342   497 sleep                       sleep 120
+u0_a112      12423   352 com.amazon.frameworksettings com.amazon.frameworksettings
+root         12449     2 [kbase_event]               [kbase_event]
+system       12501   352 com.android.keychain        com.android.keychain
+u0_a107      12530   352 com.android.documentsui     com.android.documentsui
+u0_a180      12577   352 com.android.vending         com.android.vending
+u0_a179      12653   352 com.google.process.gapps    com.google.process.gapps
+u0_a180      12724   352 com.android.vending:background com.android.vending:background
+u0_a132      12792   353 com.amazon.adep             com.amazon.adep
+shell        12880   432 ps                          ps -A -o USER,PID,PPID,NAME,ARGS
```

### `window/windows.stdout.txt`

```diff
--- before/window/windows.stdout.txt

+++ after/window/windows.stdout.txt

@@ -6,5 +6,5 @@

       fl=NOT_FOCUSABLE NOT_TOUCHABLE LAYOUT_IN_SCREEN HARDWARE_ACCELERATED
       pfl=SHOW_FOR_ALL_USERS}
-    Requested w=1200 h=1920 mLayoutSeq=738
+    Requested w=1200 h=1920 mLayoutSeq=1544
     mBaseLayer=311000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
     mToken=WindowToken{e06c09f android.os.BinderProxy@cda9a3e}
@@ -35,14 +35,13 @@

     mAttrs={(0,0)(fillxfill) sim={adjust=pan} ty=NAVIGATION_BAR fmt=TRANSLUCENT
       fl=NOT_FOCUSABLE NOT_TOUCH_MODAL TOUCHABLE_WHEN_WAKING WATCH_OUTSIDE_TOUCH SPLIT_TOUCH HARDWARE_ACCELERATED FLAG_SLIPPERY}
-    Requested w=1200 h=72 mLayoutSeq=738
+    Requested w=1200 h=72 mLayoutSeq=1544
     mBaseLayer=231000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
     mToken=WindowToken{7a91801 android.os.BinderProxy@1f009e8}
     mViewVisibility=0x0 mHaveFrame=true mObscured=false
     mSeq=0 mSystemUiVisibility=0x0
-    mPolicyVisibility=false mLegacyPolicyVisibilityAfterAnim=false mAppOpVisibility=true parentHidden=false mPermanentlyHidden=false mHiddenWhileSuspended=false mForceHideNonSystemOverlayWindow=false
-    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
-    mFullConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=undefined} s.6}
-    mLastReportedConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=undefined} s.6}
-    mHasSurface=true isReadyForDisplay()=false mWindowRemovalAllowed=false
+    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
+    mFullConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=undefined} s.6}
+    mLastReportedConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=undefined} s.6}
+    mHasSurface=true isReadyForDisplay()=true mWindowRemovalAllowed=false
     mFrame=[0,1848][1200,1920] last=[0,1848][1200,1920]
     Frames: containing=[0,1848][1200,1920] parent=[0,1848][1200,1920]
@@ -54,16 +53,16 @@

     Lst insets: overscan=[0,0][0,0] content=[0,0][0,0] visible=[0,0][0,0] stable=[0,0][0,0] physical=[0,0][0,0] outset=[0,0][0,0] cutout=com.android.server.wm.utils.WmDisplayCutout@3c1
     WindowStateAnimator{acd94f4 NavigationBar}:
-      mSurface=Surface(name=NavigationBar)/@0x47938e9
-      Surface: shown=false layer=0 alpha=1.0 rect=(0.0,0.0) 1200 x 72 transform=(1.0, 0.0, 1.0, 0.0)
-      mDrawState=HAS_DRAWN       mLastHidden=true
+       mAnimationIsEntrance=true      mSurface=Surface(name=NavigationBar)/@0x47938e9
+      Surface: shown=true layer=0 alpha=1.0 rect=(0.0,0.0) 1200 x 72 transform=(1.0, 0.0, 1.0, 0.0)
+      mDrawState=HAS_DRAWN       mLastHidden=false
       mSystemDecorRect=[0,0][1200,72] mLastClipRect=[0,0][1200,72]
-    isOnScreen=false
-    isVisible=false
+    isOnScreen=true
+    isVisible=true
   Window #2 Window{f9d34f4 u0 StatusBar}:
     mDisplayId=0 stackId=0 mSession=Session{1172335 1150:u0a10036} mClient=android.os.BinderProxy@16eaae1
     mOwnerUid=10036 mShowToOwnerOnly=false package=com.android.systemui appop=NONE
-    mAttrs={(0,0)(fillx36) gr=TOP CENTER_VERTICAL sim={adjust=resize} layoutInDisplayCutoutMode=always ty=STATUS_BAR fmt=TRANSLUCENT
+    mAttrs={(0,0)(fillxfill) gr=TOP CENTER_VERTICAL sim={adjust=resize} layoutInDisplayCutoutMode=always ty=STATUS_BAR fmt=TRANSLUCENT
       fl=NOT_FOCUSABLE TOUCHABLE_WHEN_WAKING WATCH_OUTSIDE_TOUCH SPLIT_TOUCH HARDWARE_ACCELERATED DRAWS_SYSTEM_BAR_BACKGROUNDS}
-    Requested w=1200 h=36 mLayoutSeq=738
+    Requested w=1200 h=1920 mLayoutSeq=1544
     mBaseLayer=171000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
     mToken=WindowToken{16d86c7 android.os.BinderProxy@f358006}
@@ -74,17 +73,17 @@

     mLastReportedConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=undefined} s.6}
     mHasSurface=true isReadyForDisplay()=true mWindowRemovalAllowed=false
-    mFrame=[0,0][1200,36] last=[0,0][1200,36]
+    mFrame=[0,0][1200,1920] last=[0,0][1200,1920]
     Frames: containing=[0,0][1200,1920] parent=[0,0][1200,1920]
         display=[0,0][1200,1920] overscan=[0,0][1200,1848]
-        content=[0,0][1200,36] visible=[0,0][1200,36]
+        content=[0,0][1200,1848] visible=[0,0][1200,1848]
         decor=[0,0][0,0]
         outset=[0,0][1200,1848]
-    Cur insets: overscan=[0,0][0,72] content=[0,0][0,0] visible=[0,0][0,0] stable=[0,0][0,0] surface=[0,0][0,0] outsets=[0,0][0,0] cutout=DisplayCutout{insets=Rect(0, 0 - 0, 0) boundingRect=Rect(0, 0 - 0, 0)}
-    Lst insets: overscan=[0,0][0,72] content=[0,0][0,0] visible=[0,0][0,0] stable=[0,0][0,0] physical=[0,0][0,0] outset=[0,0][0,0] cutout=com.android.server.wm.utils.WmDisplayCutout@3c1
+    Cur insets: overscan=[0,0][0,72] content=[0,0][0,72] visible=[0,0][0,72] stable=[0,0][0,72] surface=[0,0][0,0] outsets=[0,0][0,0] cutout=DisplayCutout{insets=Rect(0, 0 - 0, 0) boundingRect=Rect(0, 0 - 0, 0)}
+    Lst insets: overscan=[0,0][0,72] content=[0,0][0,72] visible=[0,0][0,72] stable=[0,0][0,72] physical=[0,0][0,0] outset=[0,0][0,0] cutout=com.android.server.wm.utils.WmDisplayCutout@3c1
     WindowStateAnimator{5a2f41d StatusBar}:
       mSurface=Surface(name=StatusBar)/@0x479de47
-      Surface: shown=true layer=0 alpha=1.0 rect=(0.0,0.0) 1200 x 36 transform=(1.0, 0.0, 1.0, 0.0)
-      mDrawState=HAS_DRAWN       mLastHidden=false
-      mSystemDecorRect=[0,0][1200,36] mLastClipRect=[0,0][1200,36]
+      Surface: shown=true layer=0 alpha=1.0 rect=(0.0,0.0) 1200 x 1920 transform=(1.0, 0.0, 1.0, 0.0)
+      mDrawState=HAS_DRAWN       mLastHidden=false
+      mSystemDecorRect=[0,0][1200,1920] mLastClipRect=[0,0][1200,1920]
     mLastFreezeDuration=+937ms
     isOnScreen=true
@@ -97,5 +96,5 @@

       pfl=NO_MOVE_ANIMATION
       vsysui=LAYOUT_STABLE LAYOUT_HIDE_NAVIGATION LAYOUT_FULLSCREEN}
-    Requested w=1200 h=72 mLayoutSeq=738
+    Requested w=1200 h=72 mLayoutSeq=1544
     mBaseLayer=21000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
     mToken=WindowToken{ca3bdb1 android.os.BinderProxy@b1bf858}
@@ -123,17 +122,50 @@

     isOnScreen=false
     isVisible=false
-  Window #4 Window{80793f7 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}:
-    mDisplayId=0 stackId=0 mSession=Session{15ce2b8 1942:u0a10120} mClient=android.os.BinderProxy@bc7c3f6
-    mOwnerUid=10120 mShowToOwnerOnly=true package=com.amazon.firelauncher appop=NONE
-    mAttrs={(0,0)(fillxfill) sim={state=always_hidden adjust=resize} ty=BASE_APPLICATION fmt=TRANSPARENT wanim=0x10302f8
+  Window #4 Window{ced5e7a u0 com.android.launcher3/com.android.quickstep.RecentsActivity}:
+    mDisplayId=0 stackId=8 mSession=Session{cb92d70 1923:u0a10075} mClient=android.os.BinderProxy@e01eaa5
+    mOwnerUid=10075 mShowToOwnerOnly=true package=com.android.launcher3 appop=NONE
+    mAttrs={(0,0)(fillxfill) sim={adjust=pan forwardNavigation} ty=BASE_APPLICATION fmt=TRANSPARENT wanim=0x10302f8
       fl=LAYOUT_IN_SCREEN LAYOUT_INSET_DECOR SHOW_WALLPAPER SPLIT_TOUCH HARDWARE_ACCELERATED DRAWS_SYSTEM_BAR_BACKGROUNDS
       pfl=FORCE_DRAW_STATUS_BAR_BACKGROUND
       vsysui=LAYOUT_STABLE LAYOUT_HIDE_NAVIGATION LAYOUT_FULLSCREEN}
-    Requested w=1200 h=1920 mLayoutSeq=738
+    Requested w=1200 h=1920 mLayoutSeq=1544
+    mBaseLayer=21000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
+    mToken=AppWindowToken{c1e3d55 token=Token{f1fe00c ActivityRecord{7620f3f u0 com.android.launcher3/com.android.quickstep.RecentsActivity t36}}}
+    mAppToken=AppWindowToken{c1e3d55 token=Token{f1fe00c ActivityRecord{7620f3f u0 com.android.launcher3/com.android.quickstep.RecentsActivity t36}}}
+     isAnimatingWithSavedSurface()= mAppDied=false    drawnStateEvaluated=true    mightAffectAllDrawn=true
+    mViewVisibility=0x0 mHaveFrame=true mObscured=false
+    mSeq=0 mSystemUiVisibility=0x700
+    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
+    mFullConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=recents} s.6}
+    mLastReportedConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=recents} s.6}
+    mHasSurface=true isReadyForDisplay()=true mWindowRemovalAllowed=false
+    mFrame=[0,0][1200,1920] last=[0,0][1200,1920]
+    Frames: containing=[0,0][1200,1920] parent=[0,0][1200,1920]
+        display=[0,0][1200,1920] overscan=[0,0][1200,1920]
+        content=[0,36][1200,1920] visible=[0,36][1200,1920]
+        decor=[0,0][1200,1920]
+        outset=[0,0][0,0]
+    Cur insets: overscan=[0,0][0,0] content=[0,36][0,0] visible=[0,36][0,0] stable=[0,36][0,72] surface=[0,0][0,0] outsets=[0,0][0,0] cutout=DisplayCutout{insets=Rect(0, 0 - 0, 0) boundingRect=Rect(0, 0 - 0, 0)}
+    Lst insets: overscan=[0,0][0,0] content=[0,36][0,0] visible=[0,36][0,0] stable=[0,36][0,72] physical=[0,0][0,0] outset=[0,0][0,0] cutout=com.android.server.wm.utils.WmDisplayCutout@3c1
+    WindowStateAnimator{2ce5dbd com.android.launcher3/com.android.quickstep.RecentsActivity}:
+      mSurface=Surface(name=com.android.launcher3/com.android.quickstep.RecentsActivity)/@0xea505d5
+      Surface: shown=true layer=0 alpha=1.0 rect=(0.0,0.0) 1200 x 1920 transform=(1.0, 0.0, 1.0, 0.0)
+      mDrawState=HAS_DRAWN       mLastHidden=false
+      mSystemDecorRect=[0,0][1200,1920] mLastClipRect=[0,0][1200,1920]
+    isOnScreen=true
+    isVisible=true
+  Window #5 Window{80793f7 u0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher EXITING}:
+    mDisplayId=0 stackId=0 mSession=Session{15ce2b8 1942:u0a10120} mClient=android.os.BinderProxy@bc7c3f6
+    mOwnerUid=10120 mShowToOwnerOnly=true package=com.amazon.firelauncher appop=NONE
+    mAttrs={(0,0)(fillxfill) sim={state=always_hidden adjust=pan} ty=BASE_APPLICATION fmt=TRANSPARENT wanim=0x10302f8
+      fl=LAYOUT_IN_SCREEN LAYOUT_INSET_DECOR SHOW_WALLPAPER SPLIT_TOUCH HARDWARE_ACCELERATED DRAWS_SYSTEM_BAR_BACKGROUNDS
+      pfl=FORCE_DRAW_STATUS_BAR_BACKGROUND
+      vsysui=LAYOUT_STABLE LAYOUT_HIDE_NAVIGATION LAYOUT_FULLSCREEN}
+    Requested w=1200 h=1920 mLayoutSeq=1537
     mBaseLayer=21000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
     mToken=AppWindowToken{e63cf5a token=Token{d3a1305 ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}}}
     mAppToken=AppWindowToken{e63cf5a token=Token{d3a1305 ActivityRecord{873be7c u0 com.amazon.firelauncher/.Launcher t2}}}
-     isAnimatingWithSavedSurface()= mAppDied=false    drawnStateEvaluated=true    mightAffectAllDrawn=true
-    mViewVisibility=0x0 mHaveFrame=true mObscured=false
+     isAnimatingWithSavedSurface()= mAppDied=false    drawnStateEvaluated=true    mightAffectAllDrawn=false
+    mViewVisibility=0x4 mHaveFrame=true mObscured=false
     mSeq=0 mSystemUiVisibility=0x700
     mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
@@ -150,106 +182,17 @@

     Lst insets: overscan=[0,0][0,0] content=[0,36][0,0] visible=[0,36][0,0] stable=[0,36][0,72] physical=[0,0][0,0] outset=[0,0][0,0] cutout=com.android.server.wm.utils.WmDisplayCutout@3c1
     WindowStateAnimator{bffb519 com.amazon.firelauncher/com.amazon.firelauncher.Launcher}:
-      mSurface=Surface(name=com.amazon.firelauncher/com.amazon.firelauncher.Launcher)/@0x3899d2a
-      Surface: shown=true layer=0 alpha=1.0 rect=(0.0,0.0) 1200 x 1920 transform=(1.0, 0.0, 1.0, 0.0)
-      mDrawState=HAS_DRAWN       mLastHidden=false
-      mSystemDecorRect=[0,0][1200,1920] mLastClipRect=[0,0][1200,1920]
-    isOnScreen=true
-    isVisible=true
-  Window #5 Window{f2b1d28 u0 org.fireosresearch.phase4.redirect/org.fireosresearch.phase4.redirect.ControlActivity}:
-    mDisplayId=0 stackId=4 mSession=Session{ce686c5 8931:u0a10196} mClient=android.os.BinderProxy@e25df4b
-    mOwnerUid=10196 mShowToOwnerOnly=true package=org.fireosresearch.phase4.redirect appop=NONE
-    mAttrs={(0,0)(fillxfill) sim={adjust=pan forwardNavigation} ty=BASE_APPLICATION wanim=0x10302f8
-      fl=LAYOUT_IN_SCREEN LAYOUT_INSET_DECOR SPLIT_TOUCH HARDWARE_ACCELERATED DRAWS_SYSTEM_BAR_BACKGROUNDS
-      pfl=FORCE_DRAW_STATUS_BAR_BACKGROUND}
-    Requested w=1200 h=1920 mLayoutSeq=669
-    mBaseLayer=21000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
-    mToken=AppWindowToken{9aa9ac8 token=Token{3644f6b ActivityRecord{64534ba u0 org.fireosresearch.phase4.redirect/.ControlActivity t32}}}
-    mAppToken=AppWindowToken{9aa9ac8 token=Token{3644f6b ActivityRecord{64534ba u0 org.fireosresearch.phase4.redirect/.ControlActivity t32}}}
-     isAnimatingWithSavedSurface()= mAppDied=false    drawnStateEvaluated=true    mightAffectAllDrawn=true
-    mViewVisibility=0x8 mHaveFrame=true mObscured=false
-    mSeq=0 mSystemUiVisibility=0x0
-    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
-    mFullConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=standard} s.6}
-    mLastReportedConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=standard} s.6}
-    mHasSurface=false isReadyForDisplay()=false mWindowRemovalAllowed=false
-    mFrame=[0,0][1200,1920] last=[0,0][1200,1920]
-    Frames: containing=[0,0][1200,1920] parent=[0,0][1200,1920]
-        display=[0,0][1200,1920] overscan=[0,0][1200,1920]
-        content=[0,36][1200,1920] visible=[0,36][1200,1920]
-        decor=[0,0][1200,1920]
-        outset=[0,0][0,0]
-    Cur insets: overscan=[0,0][0,0] content=[0,36][0,0] visible=[0,36][0,0] stable=[0,36][0,72] surface=[0,0][0,0] outsets=[0,0][0,0] cutout=DisplayCutout{insets=Rect(0, 0 - 0, 0) boundingRect=Rect(0, 0 - 0, 0)}
-    Lst insets: overscan=[0,0][0,0] content=[0,36][0,0] visible=[0,36][0,0] stable=[0,36][0,72] physical=[0,0][0,0] outset=[0,0][0,0] cutout=com.android.server.wm.utils.WmDisplayCutout@3c1
-    WindowStateAnimator{1fb5600 org.fireosresearch.phase4.redirect/org.fireosresearch.phase4.redirect.ControlActivity}:
-      mDrawState=NO_SURFACE       mLastHidden=true
-      mSystemDecorRect=[0,0][1200,1920] mLastClipRect=[0,0][1200,1920]
-    isOnScreen=false
+      mSurface=Surface(name=com.amazon.firelauncher/com.amazon.firelauncher.Launcher)/@0xafab378
+      Surface: shown=true layer=0 alpha=1.0 rect=(0.0,0.0) 1200 x 1920 transform=(1.0, 0.0, 1.0, 0.0)
+      mDrawState=HAS_DRAWN       mLastHidden=false
+      mSystemDecorRect=[0,0][1200,1920] mLastClipRect=[0,0][1200,1920]
+    mAnimatingExit=true mRemoveOnExit=false mDestroying=false mRemoved=false
+    isOnScreen=true
     isVisible=false
-  Window #6 Window{ecbc856 u0 com.amazon.switchaccess.root/com.amazon.switchaccess.SwitchAccessPreferenceActivity}:
-    mDisplayId=0 stackId=5 mSession=Session{9bc22d6 9075:u0a10134} mClient=android.os.BinderProxy@deaa271
-    mOwnerUid=10134 mShowToOwnerOnly=true package=com.amazon.switchaccess.root appop=NONE
-    mAttrs={(0,0)(fillxfill) sim={adjust=pan} ty=BASE_APPLICATION wanim=0x10302f8
-      fl=LAYOUT_IN_SCREEN LAYOUT_INSET_DECOR SPLIT_TOUCH HARDWARE_ACCELERATED DRAWS_SYSTEM_BAR_BACKGROUNDS
-      pfl=FORCE_DRAW_STATUS_BAR_BACKGROUND}
-    Requested w=1200 h=1920 mLayoutSeq=584
-    mBaseLayer=21000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
-    mToken=AppWindowToken{16e685b token=Token{a955b6a ActivityRecord{fe90555 u0 com.amazon.switchaccess.root/com.amazon.switchaccess.SwitchAccessPreferenceActivity t33}}}
-    mAppToken=AppWindowToken{16e685b token=Token{a955b6a ActivityRecord{fe90555 u0 com.amazon.switchaccess.root/com.amazon.switchaccess.SwitchAccessPreferenceActivity t33}}}
-     isAnimatingWithSavedSurface()= mAppDied=false    drawnStateEvaluated=true    mightAffectAllDrawn=true
-    mViewVisibility=0x8 mHaveFrame=true mObscured=false
-    mSeq=0 mSystemUiVisibility=0x0
-    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
-    mFullConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=standard} s.6}
-    mLastReportedConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=standard} s.6}
-    mHasSurface=false isReadyForDisplay()=false mWindowRemovalAllowed=false
-    mFrame=[0,0][1200,1920] last=[0,0][1200,1920]
-    Frames: containing=[0,0][1200,1920] parent=[0,0][1200,1920]
-        display=[0,0][1200,1920] overscan=[0,0][1200,1920]
-        content=[0,36][1200,1920] visible=[0,36][1200,1920]
-        decor=[0,0][1200,1920]
-        outset=[0,0][0,0]
-    Cur insets: overscan=[0,0][0,0] content=[0,36][0,0] visible=[0,36][0,0] stable=[0,36][0,72] surface=[0,0][0,0] outsets=[0,0][0,0] cutout=DisplayCutout{insets=Rect(0, 0 - 0, 0) boundingRect=Rect(0, 0 - 0, 0)}
-    Lst insets: overscan=[0,0][0,0] content=[0,36][0,0] visible=[0,36][0,0] stable=[0,36][0,72] physical=[0,0][0,0] outset=[0,0][0,0] cutout=com.android.server.wm.utils.WmDisplayCutout@3c1
-    WindowStateAnimator{120a23e com.amazon.switchaccess.root/com.amazon.switchaccess.SwitchAccessPreferenceActivity}:
-      mDrawState=NO_SURFACE       mLastHidden=true
-      mSystemDecorRect=[0,0][1200,1920] mLastClipRect=[0,0][1200,1920]
-    isOnScreen=false
-    isVisible=false
-  Window #7 Window{5aaf091 u0 com.amazon.settings/com.amazon.settings.accessibility.AccessibilitySettingsActivity}:
-    mDisplayId=0 stackId=5 mSession=Session{f55672a 8976:1000} mClient=android.os.BinderProxy@a86aab8
-    mOwnerUid=1000 mShowToOwnerOnly=true package=com.amazon.settings appop=NONE
-    mAttrs={(0,0)(fillxfill) sim={adjust=pan} ty=BASE_APPLICATION wanim=0x10302f8
-      fl=LAYOUT_IN_SCREEN LAYOUT_INSET_DECOR SPLIT_TOUCH HARDWARE_ACCELERATED DRAWS_SYSTEM_BAR_BACKGROUNDS
-      pfl=FORCE_DRAW_STATUS_BAR_BACKGROUND}
-    Requested w=1200 h=1920 mLayoutSeq=537
-    mBaseLayer=21000 mSubLayer=0 mAnimLayer=0+=0 mLastLayer=0
-    mToken=AppWindowToken{b11313b token=Token{143bca ActivityRecord{84fab35 u0 com.amazon.settings/.accessibility.AccessibilitySettingsActivity t33}}}
-    mAppToken=AppWindowToken{b11313b token=Token{143bca ActivityRecord{84fab35 u0 com.amazon.settings/.accessibility.AccessibilitySettingsActivity t33}}}
-     isAnimatingWithSavedSurface()= mAppDied=false    drawnStateEvaluated=true    mightAffectAllDrawn=true
-    mViewVisibility=0x8 mHaveFrame=true mObscured=false
-    mSeq=0 mSystemUiVisibility=0x0
-    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
-    mFullConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=standard} s.6}
-    mLastReportedConfiguration={1.0 ?mcc?mnc [ja_JP] ldltr sw800dp w800dp h1208dp 240dpi xlrg port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1200, 1920) mAppBounds=Rect(0, 0 - 1200, 1848) mWindowingMode=fullscreen mActivityType=standard} s.6}
-    mHasSurface=false isReadyForDisplay()=false mWindowRemovalAllowed=false
-    mFrame=[0,0][1200,1920] last=[0,0][1200,1920]
-    Frames: containing=[0,0][1200,1920] parent=[0,0][1200,1920]
-        display=[0,0][1200,1920] overscan=[0,0][1200,1920]
-        content=[0,36][1200,1920] visible=[0,36][1200,1920]
-        decor=[0,0][1200,1920]
```
