package com.android.launcher3;

/* JADX INFO: loaded from: classes.dex */
@android.annotation.SuppressLint({"Registered"})
public class Launcher extends com.android.launcher3.statemanager.StatefulActivity<com.android.launcher3.LauncherState> implements com.android.systemui.plugins.shared.LauncherExterns, com.android.launcher3.model.BgDataModel.Callbacks, com.android.systemui.plugins.PluginListener<com.android.systemui.plugins.OverlayPlugin> {
    public static final com.android.launcher3.util.ActivityTracker<com.android.launcher3.Launcher> ACTIVITY_TRACKER = null;
    public boolean alreadyAddedEmptyPage;
    public b.a.m.n4.d0.e delayedUIHandler;
    public boolean goToFeedWhenReenterOverview;
    public boolean isSlideBarTempHide;
    public com.android.launcher3.accessibility.LauncherAccessibilityDelegate mAccessibilityDelegate;
    public com.android.launcher3.accessibility.MultiSelectionAccessibilityDelegate mAccessibilityDelegateForMultiSelection;
    public com.android.launcher3.accessibility.LauncherAccessibilityDelegateWrapper mAccessibilityDelegateWrapper;
    public java.lang.Runnable mAfterEnterOverviewRunnable;
    public com.android.launcher3.allapps.AllAppsTransitionController mAllAppsController;
    public com.android.launcher3.allapps.AppDrawerBehavior mAppDrawerBehavior;
    public com.android.launcher3.appselection.AppSelectionPage mAppSelectionPageForFolder;
    public com.microsoft.launcher.AppSetManager mAppSetManager;
    public com.android.launcher3.LauncherAppTransitionManager mAppTransitionManager;
    public com.android.launcher3.LauncherAppWidgetHost mAppWidgetHost;
    public com.android.launcher3.widget.WidgetManagerHelper mAppWidgetManager;
    public com.android.launcher3.allapps.AllAppsContainerView mAppsView;
    public com.android.launcher3.bingsearch.BingSearchBehavior mBingSearchBehavior;
    public android.view.View mBingSearchContentContainer;
    public com.android.launcher3.bingsearch.BingSearchTransitionController mBingSearchController;
    public com.microsoft.launcher.slidebar.SlideBarDropTarget mBottomSlideBar;
    public java.util.List<com.android.launcher3.BubbleTextView> mCurrentAnimatedIcons;
    public b.a.m.h3.v mCurrentMultiSelectable;
    public boolean mDeferOverlayCallbacks;
    public final java.lang.Runnable mDeferredOverlayCallbacks;
    public com.android.launcher3.dragndrop.DragController mDragController;
    public com.android.launcher3.dragndrop.DragLayer mDragLayer;
    public com.android.launcher3.DropTargetBar mDropTargetBar;
    public b.a.m.r2.c mFeaturePageHost;
    public com.microsoft.launcher.featurepage.FeaturePageStateManager mFeaturePageStateManager;
    public com.android.launcher3.keyboard.ViewGroupFocusHelper mFocusHandler;
    public final java.lang.Runnable mHandleDeferredResume;
    public final android.os.Handler mHandler;
    public com.android.launcher3.Hotseat mHotseat;
    public com.android.launcher3.uioverrides.hotseat.HotseatTransitionController mHotseatController;
    public b.a.m.x2.n0 mHotseatLayoutBehavior;
    public com.android.launcher3.icons.IconCache mIconCache;
    public boolean mIncorrectLaunchState;
    public boolean mIsExitOverviewModeByPanelButton;
    public boolean mIsInOverviewWhenConfigChange;
    public boolean mIsUpdateConfig;
    public long mLastTouchUpTime;
    public com.android.launcher3.LauncherRootView mLauncherView;
    public com.microsoft.launcher.slidebar.SlideBarDropTarget mLeftSlideBar;
    public com.android.launcher3.LauncherModel mModel;
    public com.android.launcher3.model.ModelWriter mModelWriter;
    public com.microsoft.launcher.multiselection.MultiSelectionDropTargetBar mMultiSelectionTargetBar;
    public android.content.res.Configuration mOldConfig;
    public java.util.ArrayList<com.android.launcher3.Launcher.OnResumeCallback> mOnResumeCallbacks;
    public com.android.systemui.plugins.shared.LauncherOverlayManager mOverlayManager;
    public com.android.launcher3.OverlayPanel mOverlayPanel;
    public com.microsoft.launcher.overview.OverviewPanel mOverviewPanel;
    public int mPageToBindSynchronously;
    public int mPendingActivityRequestCode;
    public com.android.launcher3.util.ActivityResultInfo mPendingActivityResult;
    public com.android.launcher3.util.ViewOnDrawExecutor mPendingExecutor;
    public com.android.launcher3.util.PendingRequestArgs mPendingRequestArgs;
    public com.android.launcher3.popup.PopupDataProvider mPopupDataProvider;
    public java.lang.Runnable mPostOnResumeRunnable;
    public int mRestoredOverlayState;
    public com.microsoft.launcher.slidebar.SlideBarDropTarget mRightSlideBar;
    public com.android.launcher3.states.RotationHelper mRotationHelper;
    public final android.content.BroadcastReceiver mScreenOffReceiver;
    public com.android.launcher3.views.ScrimView mScrimView;
    public com.android.launcher3.SessionCommitReceiver mSessionCommitReceiver;
    public android.content.SharedPreferences mSharedPrefs;
    public com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> mStateManager;
    public int mSynchronouslyBoundPage;
    public com.android.launcher3.tasklayout.TaskLayoutHelper mTaskLayoutHelper;
    public final int[] mTmpAddItemCellCoordinates;
    public com.microsoft.launcher.slidebar.SlideBarDropTarget mTopSlideBar;
    public boolean mTouchInProgress;
    public com.android.launcher3.util.SafeCloseable mUserChangedCallbackCloseable;
    public com.microsoft.launcher.overview.VerticalOverviewPanel mVerticalOverviewPanel;
    public android.view.View mWallpaperWatermark;
    public com.android.launcher3.Workspace mWorkspace;
    public boolean mWorkspaceLoading;
    public boolean needRecreateAppDrawerBehavior;
    public boolean needRecreateSearchBehavior;







    /* JADX INFO: renamed from: com.android.launcher3.Launcher$2, reason: invalid class name */
    public class AnonymousClass2 implements com.android.systemui.plugins.shared.LauncherOverlayManager {
        public AnonymousClass2(com.android.launcher3.Launcher r1) {
                r0 = this;
                r0.<init>()
                return
        }

        @Override // com.android.systemui.plugins.shared.LauncherOverlayManager
        public /* synthetic */ void dump(java.lang.String r1, java.io.PrintWriter r2) {
                r0 = this;
                b.c.d.a.c.b.a(r0, r1, r2)
                return
        }

        @Override // com.android.systemui.plugins.shared.LauncherOverlayManager
        public /* synthetic */ void hideOverlay(int r1) {
                r0 = this;
                b.c.d.a.c.b.b(r0, r1)
                return
        }

        @Override // com.android.systemui.plugins.shared.LauncherOverlayManager
        public /* synthetic */ void hideOverlay(boolean r1) {
                r0 = this;
                b.c.d.a.c.b.c(r0, r1)
                return
        }

        @Override // com.android.systemui.plugins.shared.LauncherOverlayManager, android.app.Application.ActivityLifecycleCallbacks
        public /* synthetic */ void onActivityCreated(android.app.Activity r1, android.os.Bundle r2) {
                r0 = this;
                b.c.d.a.c.b.d(r0, r1, r2)
                return
        }

        @Override // com.android.systemui.plugins.shared.LauncherOverlayManager, android.app.Application.ActivityLifecycleCallbacks
        public /* synthetic */ void onActivityDestroyed(android.app.Activity r1) {
                r0 = this;
                b.c.d.a.c.b.e(r0, r1)
                return
        }

        @Override // com.android.systemui.plugins.shared.LauncherOverlayManager, android.app.Application.ActivityLifecycleCallbacks
        public /* synthetic */ void onActivityPaused(android.app.Activity r1) {
                r0 = this;
                b.c.d.a.c.b.f(r0, r1)
                return
        }

        @Override // com.android.systemui.plugins.shared.LauncherOverlayManager, android.app.Application.ActivityLifecycleCallbacks
        public /* synthetic */ void onActivityResumed(android.app.Activity r1) {
                r0 = this;
                b.c.d.a.c.b.g(r0, r1)
                return
        }

        @Override // com.android.systemui.plugins.shared.LauncherOverlayManager, android.app.Application.ActivityLifecycleCallbacks
        public /* synthetic */ void onActivitySaveInstanceState(android.app.Activity r1, android.os.Bundle r2) {
                r0 = this;
                b.c.d.a.c.b.h(r0, r1, r2)
                return
        }

        @Override // com.android.systemui.plugins.shared.LauncherOverlayManager, android.app.Application.ActivityLifecycleCallbacks
        public /* synthetic */ void onActivityStarted(android.app.Activity r1) {
                r0 = this;
                b.c.d.a.c.b.i(r0, r1)
                return
        }

        @Override // com.android.systemui.plugins.shared.LauncherOverlayManager, android.app.Application.ActivityLifecycleCallbacks
        public /* synthetic */ void onActivityStopped(android.app.Activity r1) {
                r0 = this;
                b.c.d.a.c.b.j(r0, r1)
                return
        }

        @Override // com.android.systemui.plugins.shared.LauncherOverlayManager
        public /* synthetic */ void onAttachedToWindow() {
                r0 = this;
                b.c.d.a.c.b.k(r0)
                return
        }

        @Override // com.android.systemui.plugins.shared.LauncherOverlayManager
        public /* synthetic */ void onDetachedFromWindow() {
                r0 = this;
                b.c.d.a.c.b.l(r0)
                return
        }

        @Override // com.android.systemui.plugins.shared.LauncherOverlayManager
        public /* synthetic */ void onDeviceProvideChanged() {
                r0 = this;
                b.c.d.a.c.b.m(r0)
                return
        }

        @Override // com.android.systemui.plugins.shared.LauncherOverlayManager
        public /* synthetic */ void openOverlay() {
                r0 = this;
                b.c.d.a.c.b.n(r0)
                return
        }

        @Override // com.android.systemui.plugins.shared.LauncherOverlayManager
        public /* synthetic */ boolean startSearch(byte[] r1, android.os.Bundle r2) {
                r0 = this;
                boolean r1 = b.c.d.a.c.b.o(r0, r1, r2)
                return r1
        }
    }








    public interface LauncherOverlay {
    }

    public interface LauncherOverlayCallbacks {
        void onScrollChanged(float r1);
    }

    public class LauncherOverlayCallbacksImpl implements com.android.launcher3.Launcher.LauncherOverlayCallbacks {
        public final /* synthetic */ com.android.launcher3.Launcher this$0;

        public LauncherOverlayCallbacksImpl(com.android.launcher3.Launcher r1) {
                r0 = this;
                r0.this$0 = r1
                r0.<init>()
                return
        }

        @Override // com.android.launcher3.Launcher.LauncherOverlayCallbacks
        public void onScrollChanged(float r2) {
                r1 = this;
                com.android.launcher3.Launcher r0 = r1.this$0
                com.android.launcher3.Workspace r0 = r0.mWorkspace
                if (r0 == 0) goto L9
                r0.onOverlayScrollChanged(r2)
            L9:
                return
        }
    }

    public interface OnResumeCallback {
        void onLauncherResume();
    }

    public static class ReleaseDbRunnable extends b.a.m.m4.t1.e {
        public ReleaseDbRunnable() {
                r1 = this;
                java.lang.String r0 = "onTrimMemory"
                r1.<init>(r0)
                return
        }

        @Override // b.a.m.m4.t1.e
        public void doInBackground() {
                r0 = this;
                android.database.sqlite.SQLiteDatabase.releaseMemory()
                return
        }
    }

    static {
            com.android.launcher3.util.ActivityTracker r0 = new com.android.launcher3.util.ActivityTracker
            r0.<init>()
            com.android.launcher3.Launcher.ACTIVITY_TRACKER = r0
            return
    }

    public Launcher() {
            r3 = this;
            r3.<init>()
            r0 = 0
            r3.mIsUpdateConfig = r0
            r1 = 2
            int[] r1 = new int[r1]
            r3.mTmpAddItemCellCoordinates = r1
            r3.needRecreateAppDrawerBehavior = r0
            r3.needRecreateSearchBehavior = r0
            r1 = 1
            r3.mWorkspaceLoading = r1
            java.util.ArrayList r1 = new java.util.ArrayList
            r1.<init>()
            r3.mOnResumeCallbacks = r1
            r1 = -1
            r3.mSynchronouslyBoundPage = r1
            r3.mPageToBindSynchronously = r1
            r3.mRestoredOverlayState = r1
            r3.mPendingActivityRequestCode = r1
            android.os.Handler r1 = new android.os.Handler
            r1.<init>()
            r3.mHandler = r1
            b.c.b.b0 r1 = new b.c.b.b0
            r1.<init>(r3)
            r3.mHandleDeferredResume = r1
            b.c.b.m0 r1 = new b.c.b.m0
            r1.<init>(r3)
            r3.mDeferredOverlayCallbacks = r1
            r1 = -1
            r3.mLastTouchUpTime = r1
            r3.mIsExitOverviewModeByPanelButton = r0
            r3.mIncorrectLaunchState = r0
            r3.mIsInOverviewWhenConfigChange = r0
            r3.goToFeedWhenReenterOverview = r0
            r0 = 0
            r3.mPostOnResumeRunnable = r0
            java.util.ArrayList r0 = new java.util.ArrayList
            r0.<init>()
            r3.mCurrentAnimatedIcons = r0
            com.android.launcher3.Launcher$8 r0 = new com.android.launcher3.Launcher$8
            r0.<init>(r3)
            r3.mScreenOffReceiver = r0
            return
    }

    public static com.android.launcher3.Launcher getLauncher(android.content.Context r1) {
            boolean r0 = r1 instanceof com.android.launcher3.Launcher
            if (r0 == 0) goto L7
            com.android.launcher3.Launcher r1 = (com.android.launcher3.Launcher) r1
            return r1
        L7:
            android.content.ContextWrapper r1 = (android.content.ContextWrapper) r1
            android.content.Context r0 = r1.getBaseContext()
            boolean r0 = r0 instanceof com.android.launcher3.Launcher
            if (r0 == 0) goto L18
            android.content.Context r1 = r1.getBaseContext()
            com.android.launcher3.Launcher r1 = (com.android.launcher3.Launcher) r1
            return r1
        L18:
            r1 = 0
            return r1
    }

    public void addAppWidgetImpl(int r2, com.android.launcher3.model.data.ItemInfo r3, android.appwidget.AppWidgetHostView r4, com.android.launcher3.widget.WidgetAddFlowHandler r5, int r6) {
            r1 = this;
            r0 = 5
            boolean r0 = r5.startConfigActivity(r1, r2, r3, r0)
            if (r0 != 0) goto L1b
            com.android.launcher3.Launcher$10 r0 = new com.android.launcher3.Launcher$10
            r0.<init>(r1)
            android.appwidget.AppWidgetProviderInfo r5 = r5.mProviderInfo
            com.android.launcher3.LauncherAppWidgetProviderInfo r5 = com.android.launcher3.LauncherAppWidgetProviderInfo.fromProviderInfo(r1, r5)
            r1.completeAddAppWidget(r2, r3, r4, r5)
            com.android.launcher3.Workspace r2 = r1.mWorkspace
            r3 = 0
            r2.removeExtraEmptyScreenDelayed(r6, r3, r0)
        L1b:
            return
    }

    public com.android.launcher3.folder.FolderIcon addFolder(com.android.launcher3.CellLayout r8, int r9, int r10, int r11, int r12) {
            r7 = this;
            r6 = 0
            r0 = r7
            r1 = r8
            r2 = r9
            r3 = r10
            r4 = r11
            r5 = r12
            com.android.launcher3.folder.FolderIcon r8 = r0.addFolder(r1, r2, r3, r4, r5, r6)
            return r8
    }

    public com.android.launcher3.folder.FolderIcon addFolder(com.android.launcher3.CellLayout r10, int r11, int r12, int r13, int r14, boolean r15) {
            r9 = this;
            com.android.launcher3.model.data.FolderInfo r8 = new com.android.launcher3.model.data.FolderInfo
            r8.<init>()
            r0 = 2131821819(0x7f1104fb, float:1.9276392E38)
            java.lang.CharSequence r0 = r9.getText(r0)
            r8.title = r0
            r0 = -100
            if (r11 != r0) goto L1e
            int r0 = b.a.m.c4.v8.L0()
            r8.spanX = r0
            int r0 = b.a.m.c4.v8.L0()
            r8.spanY = r0
        L1e:
            com.android.launcher3.model.ModelWriter r0 = r9.mModelWriter
            long r2 = (long) r11
            long r4 = (long) r12
            r1 = r8
            r6 = r13
            r7 = r14
            r0.addItemToDatabase(r1, r2, r4, r6, r7)
            if (r15 == 0) goto L2e
            r11 = 2131493121(0x7f0c0101, float:1.8609713E38)
            goto L31
        L2e:
            r11 = 2131493120(0x7f0c0100, float:1.8609711E38)
        L31:
            com.android.launcher3.folder.FolderIcon r10 = com.android.launcher3.folder.FolderIcon.inflateFolderAndIcon(r11, r9, r10, r8)
            com.android.launcher3.Workspace r11 = r9.mWorkspace
            r11.addInScreen(r10, r8)
            com.android.launcher3.Workspace r11 = r9.mWorkspace
            com.android.launcher3.CellLayout r11 = r11.getParentCellLayoutForView(r10)
            if (r11 == 0) goto L49
            com.android.launcher3.ShortcutAndWidgetContainer r11 = r11.getShortcutsAndWidgets()
            r11.measureChild(r10)
        L49:
            return r10
    }

    public void addPendingBindAppWidget(com.android.launcher3.model.data.LauncherAppWidgetInfo r1) {
            r0 = this;
            return
    }

    public void addPendingItem(com.android.launcher3.PendingAddItemInfo r7, int r8, int r9, int[] r10, int r11, int r12) {
            r6 = this;
            r7.container = r8
            r7.screenId = r9
            r8 = 0
            r9 = 1
            if (r10 == 0) goto L10
            r0 = r10[r8]
            r7.cellX = r0
            r10 = r10[r9]
            r7.cellY = r10
        L10:
            r7.spanX = r11
            r7.spanY = r12
            int r10 = r7.itemType
            r11 = 0
            if (r10 == r9) goto L92
            r9 = 4
            r12 = 5
            if (r10 == r9) goto L35
            if (r10 != r12) goto L20
            goto L35
        L20:
            java.lang.IllegalStateException r8 = new java.lang.IllegalStateException
            java.lang.String r9 = "Unknown item type: "
            java.lang.StringBuilder r9 = b.c.e.c.a.G(r9)
            int r7 = r7.itemType
            r9.append(r7)
            java.lang.String r7 = r9.toString()
            r8.<init>(r7)
            throw r8
        L35:
            com.android.launcher3.widget.PendingAddWidgetInfo r7 = (com.android.launcher3.widget.PendingAddWidgetInfo) r7
            android.appwidget.AppWidgetHostView r3 = r7.boundWidget
            com.android.launcher3.widget.WidgetAddFlowHandler r4 = r7.getHandler()
            if (r3 == 0) goto L51
            com.android.launcher3.dragndrop.DragLayer r8 = r6.mDragLayer
            r8.removeView(r3)
            int r1 = r3.getAppWidgetId()
            r5 = 0
            r0 = r6
            r2 = r7
            r0.addAppWidgetImpl(r1, r2, r3, r4, r5)
            r7.boundWidget = r11
            goto Lb8
        L51:
            int r9 = r7.itemType
            if (r9 != r12) goto L64
            com.android.launcher3.util.MainThreadInitializedObject<com.android.launcher3.widget.custom.CustomWidgetManager> r9 = com.android.launcher3.widget.custom.CustomWidgetManager.INSTANCE
            java.lang.Object r8 = r9.get(r6, r8)
            com.android.launcher3.widget.custom.CustomWidgetManager r8 = (com.android.launcher3.widget.custom.CustomWidgetManager) r8
            android.content.ComponentName r9 = r7.componentName
            int r8 = r8.getWidgetIdForCustomProvider(r9)
            goto L6a
        L64:
            com.android.launcher3.LauncherAppWidgetHost r8 = r6.mAppWidgetHost
            int r8 = r8.allocateAppWidgetId()
        L6a:
            r1 = r8
            android.os.Bundle r8 = r7.bindOptions
            com.android.launcher3.widget.WidgetManagerHelper r9 = r6.mAppWidgetManager
            com.android.launcher3.LauncherAppWidgetProviderInfo r10 = r7.info
            boolean r8 = r9.bindAppWidgetIdIfAllowed(r1, r10, r8)
            if (r8 == 0) goto L7f
            r3 = 0
            r5 = 0
            r0 = r6
            r2 = r7
            r0.addAppWidgetImpl(r1, r2, r3, r4, r5)
            goto Lb8
        L7f:
            r8 = 11
            java.util.Objects.requireNonNull(r4)
            com.android.launcher3.util.PendingRequestArgs r7 = com.android.launcher3.util.PendingRequestArgs.forWidgetInfo(r1, r4, r7)
            r6.mPendingRequestArgs = r7
            com.android.launcher3.LauncherAppWidgetHost r7 = r6.mAppWidgetHost
            android.appwidget.AppWidgetProviderInfo r9 = r4.mProviderInfo
            r7.startBindFlow(r6, r1, r9, r8)
            goto Lb8
        L92:
            com.android.launcher3.widget.PendingAddShortcutInfo r7 = (com.android.launcher3.widget.PendingAddShortcutInfo) r7
            android.content.Intent r10 = new android.content.Intent
            java.lang.String r12 = "android.intent.action.CREATE_SHORTCUT"
            r10.<init>(r12)
            android.content.ComponentName r12 = r7.componentName
            android.content.Intent r10 = r10.setComponent(r12)
            com.android.launcher3.util.PendingRequestArgs r12 = new com.android.launcher3.util.PendingRequestArgs
            r12.<init>(r9, r9, r10)
            r12.copyFrom(r7)
            r6.mPendingRequestArgs = r12
            boolean r10 = com.android.launcher3.Utilities.IS_RUNNING_IN_TEST_HARNESS
            com.android.launcher3.pm.ShortcutConfigActivityInfo r7 = r7.activityInfo
            boolean r7 = r7.startConfigActivity(r6, r9)
            if (r7 != 0) goto Lb8
            r6.handleActivityResult(r9, r8, r11)
        Lb8:
            return
    }

    public final void bindAddScreens(com.android.launcher3.util.IntArray r7) {
            r6 = this;
            int r0 = r7.mSize
            r1 = 0
        L3:
            if (r1 >= r0) goto L24
            int r2 = r7.get(r1)
            long r2 = (long) r2
            com.android.launcher3.Workspace r4 = r6.mWorkspace
            java.util.Objects.requireNonNull(r4)
            int r3 = (int) r2
            com.android.launcher3.util.IntArrayCompat r2 = r4.mScreenOrder
            r5 = -201(0xffffffffffffff37, float:NaN)
            int r2 = r2.indexOf(r5)
            if (r2 >= 0) goto L1e
            com.android.launcher3.util.IntArrayCompat r2 = r4.mScreenOrder
            int r2 = r2.mSize
        L1e:
            r4.insertNewWorkspaceScreen(r3, r2)
            int r1 = r1 + 1
            goto L3
        L24:
            return
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void bindAllApplications(com.android.launcher3.model.data.AppInfo[] r2, int r3) {
            r1 = this;
            com.android.launcher3.allapps.AllAppsContainerView r0 = r1.mAppsView
            if (r0 == 0) goto L12
            com.android.launcher3.allapps.AllAppsStore r0 = r0.getAppsStore()
            java.util.Objects.requireNonNull(r0)
            java.util.List r2 = java.util.Arrays.asList(r2)
            r0.setApps(r2, r1, r3)
        L12:
            return
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void bindAllWidgets(java.util.ArrayList<com.android.launcher3.widget.WidgetListRowEntry> r2) {
            r1 = this;
            com.android.launcher3.popup.PopupDataProvider r0 = r1.mPopupDataProvider
            r0.mAllWidgets = r2
            com.android.launcher3.popup.PopupDataProvider$PopupDataChangeListener r2 = r0.mChangeListener
            r2.onWidgetsBound()
            b.a.m.u4.i r2 = b.a.m.u4.i.b()
            r2.c()
            r2 = 131071(0x1ffff, float:1.8367E-40)
            com.android.launcher3.AbstractFloatingView r2 = com.android.launcher3.AbstractFloatingView.getOpenView(r1, r2)
            if (r2 == 0) goto L1c
            r2.onWidgetsBound()
        L1c:
            return
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void bindAppEditInfoChanged() {
            r0 = this;
            return
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void bindAppSetDegenerated(java.util.Collection<com.android.launcher3.model.data.WorkspaceItemInfo> r7, java.util.Collection<com.android.launcher3.model.data.WorkspaceItemInfo> r8, android.util.SparseIntArray r9) {
            r6 = this;
            java.util.ArrayList r0 = new java.util.ArrayList
            r0.<init>()
            java.util.Iterator r7 = r7.iterator()
        L9:
            boolean r1 = r7.hasNext()
            if (r1 == 0) goto L29
            java.lang.Object r1 = r7.next()
            com.android.launcher3.model.data.WorkspaceItemInfo r1 = (com.android.launcher3.model.data.WorkspaceItemInfo) r1
            com.android.launcher3.Workspace r2 = r6.mWorkspace
            int r3 = r1.id
            android.view.View r2 = r2.getHomescreenIconByItemId(r3)
            if (r2 == 0) goto L25
            com.android.launcher3.Workspace r1 = r6.mWorkspace
            r1.removeWorkspaceItem(r2)
            goto L9
        L25:
            r0.add(r1)
            goto L9
        L29:
            java.util.Iterator r7 = r8.iterator()
        L2d:
            boolean r8 = r7.hasNext()
            r1 = 0
            if (r8 == 0) goto L7c
            java.lang.Object r8 = r7.next()
            com.android.launcher3.model.data.WorkspaceItemInfo r8 = (com.android.launcher3.model.data.WorkspaceItemInfo) r8
            int r2 = r8.container
            if (r2 < 0) goto L6c
            com.android.launcher3.Workspace r3 = r6.mWorkspace
            long r4 = (long) r2
            com.android.launcher3.folder.FolderIcon r2 = r3.getFolderById(r4)
            if (r2 == 0) goto L53
            com.android.launcher3.model.data.FolderInfo r2 = r2.mInfo
            java.util.List<com.android.launcher3.model.data.WorkspaceItemInfo> r3 = r2.contents
            int r3 = r3.size()
            r2.add(r8, r3, r1)
            goto L2d
        L53:
            int r2 = r8.id
            r3 = -1
            int r2 = r9.get(r2, r3)
            if (r2 == r3) goto L64
            java.util.List r8 = java.util.Collections.singletonList(r8)
            b.a.m.n4.b0.b(r6, r8, r2, r1)
            goto L2d
        L64:
            java.lang.IllegalStateException r7 = new java.lang.IllegalStateException
            java.lang.String r8 = "App set degenerated error"
            r7.<init>(r8)
            throw r7
        L6c:
            int r1 = r8.screenId
            com.android.launcher3.CellLayout r1 = r6.getCellLayout(r2, r1)
            android.view.View r1 = r6.createShortcut(r1, r8)
            com.android.launcher3.Workspace r2 = r6.mWorkspace
            r2.addInScreen(r1, r8)
            goto L2d
        L7c:
            java.util.Iterator r7 = r0.iterator()
        L80:
            boolean r8 = r7.hasNext()
            if (r8 == 0) goto Led
            java.lang.Object r8 = r7.next()
            com.android.launcher3.model.data.WorkspaceItemInfo r8 = (com.android.launcher3.model.data.WorkspaceItemInfo) r8
            com.android.launcher3.Workspace r9 = r6.mWorkspace
            java.util.Objects.requireNonNull(r9)
            int r0 = r8.container
            long r2 = (long) r0
            com.android.launcher3.folder.FolderIcon r9 = r9.getFolderById(r2)
            if (r9 == 0) goto L80
            java.lang.Object r9 = r9.getTag()
            com.android.launcher3.model.data.FolderInfo r9 = (com.android.launcher3.model.data.FolderInfo) r9
            r9.remove(r8, r1)
            int r9 = r8.itemType
            r0 = 100
            if (r9 != r0) goto L80
            int r9 = r8.id
            long r2 = (long) r9
            b.c.b.k3.o r9 = new b.c.b.k3.o
            r9.<init>(r2)
            com.android.launcher3.model.BgDataModel r0 = com.android.launcher3.LauncherModel.sBgDataModel
            com.android.launcher3.util.IntSparseArrayMap<com.android.launcher3.model.data.ItemInfo> r0 = r0.itemsIdMap
            java.util.HashSet r9 = r9.filterItemInfos(r0)
            int r0 = r9.size()
            r2 = 1
            if (r0 > r2) goto Le5
            java.util.Iterator r9 = r9.iterator()
        Lc4:
            boolean r0 = r9.hasNext()
            if (r0 == 0) goto L80
            java.lang.Object r0 = r9.next()
            com.android.launcher3.model.data.ItemInfo r0 = (com.android.launcher3.model.data.ItemInfo) r0
            boolean r2 = r0 instanceof com.android.launcher3.model.data.WorkspaceItemInfo
            if (r2 == 0) goto Lc4
            int r2 = r8.container
            r0.container = r2
            int r2 = r8.screenId
            r0.screenId = r2
            int r2 = r8.cellX
            r0.cellX = r2
            int r2 = r8.cellY
            r0.cellY = r2
            goto Lc4
        Le5:
            java.lang.IllegalArgumentException r7 = new java.lang.IllegalArgumentException
            java.lang.String r8 = "app set data error"
            r7.<init>(r8)
            throw r7
        Led:
            return
    }

    public void bindAppWidget(com.android.launcher3.model.data.LauncherAppWidgetInfo r3) {
            r2 = this;
            android.view.View r0 = r2.inflateAppWidget(r3)
            if (r0 == 0) goto L10
            com.android.launcher3.Workspace r1 = r2.mWorkspace
            r1.addInScreen(r0, r3)
            com.android.launcher3.Workspace r3 = r2.mWorkspace
            r3.requestLayout()
        L10:
            return
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void bindAppsAdded(com.android.launcher3.util.IntArray r4, java.util.ArrayList<com.android.launcher3.model.data.ItemInfo> r5, java.util.ArrayList<com.android.launcher3.model.data.ItemInfo> r6) {
            r3 = this;
            if (r4 == 0) goto L5
            r3.bindAddScreens(r4)
        L5:
            r4 = 0
            boolean r0 = r5.isEmpty()
            if (r0 != 0) goto Lf
            r3.bindItems(r5, r4)
        Lf:
            boolean r5 = r6.isEmpty()
            if (r5 != 0) goto L3f
            java.lang.Object r5 = r6.get(r4)
            com.android.launcher3.model.data.ItemInfo r5 = (com.android.launcher3.model.data.ItemInfo) r5
            com.android.launcher3.Workspace r0 = r3.mWorkspace
            int r1 = r5.screenId
            int r0 = r0.getPageIndexForScreenId(r1)
            com.android.launcher3.DeviceProfile r1 = r3.mDeviceProfile
            com.android.launcher3.InvariantDeviceProfile r1 = r1.inv
            int r1 = r1.numScreens
            com.android.launcher3.Workspace r2 = r3.mWorkspace
            int r2 = r2.getCurrentPage()
            if (r0 < r2) goto L34
            int r2 = r2 + r1
            if (r0 < r2) goto L3b
        L34:
            com.android.launcher3.Workspace r0 = r3.mWorkspace
            int r5 = r5.screenId
            r0.snapToPage(r5)
        L3b:
            r5 = 1
            r3.bindItems(r6, r5)
        L3f:
            com.android.launcher3.Workspace r5 = r3.mWorkspace
            r5.removeExtraEmptyScreen(r4)
            return
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void bindAppsAddedOrUpdated(java.util.ArrayList<com.android.launcher3.model.data.AppInfo> r14) {
            r13 = this;
            com.android.launcher3.allapps.AllAppsContainerView r0 = r13.mAppsView
            if (r0 == 0) goto L11
            com.android.launcher3.allapps.AllAppsStore r0 = r0.getAppsStore()
            com.android.launcher3.allapps.AllAppsContainerView r1 = r13.mAppsView
            android.content.Context r1 = r1.getContext()
            r0.addOrUpdateApps(r14, r1)
        L11:
            b.a.m.n2.k0.e r0 = b.a.m.n2.k0.e.b.a
            boolean r0 = r0.k(r13)
            if (r0 == 0) goto L3e
            if (r14 == 0) goto L3e
            int r0 = r14.size()
            if (r0 <= 0) goto L3e
            java.util.ArrayList r0 = new java.util.ArrayList
            r0.<init>()
            java.util.Iterator r1 = r14.iterator()
        L2a:
            boolean r2 = r1.hasNext()
            if (r2 == 0) goto L3e
            java.lang.Object r2 = r1.next()
            com.android.launcher3.model.data.AppInfo r2 = (com.android.launcher3.model.data.AppInfo) r2
            java.lang.String r2 = r2.getPackageName()
            r0.add(r2)
            goto L2a
        L3e:
            com.android.launcher3.Workspace r0 = r13.mWorkspace
            int r1 = b.a.m.n4.b0.a
            if (r0 == 0) goto L1de
            if (r14 == 0) goto L1de
            int r0 = r14.size()
            r1 = 1
            if (r0 >= r1) goto L4f
            goto L1de
        L4f:
            java.lang.String r0 = com.microsoft.launcher.enterprise.helpers.EnterpriseHelper.a
            com.microsoft.launcher.enterprise.helpers.EnterpriseHelper r0 = com.microsoft.launcher.enterprise.helpers.EnterpriseHelper.a.a
            r2 = 0
            boolean r3 = r0.h(r13, r2)
            if (r3 != 0) goto L5c
            goto L1de
        L5c:
            b.a.m.e2.n r0 = r0.f9561b
            if (r0 != 0) goto L62
            goto L1de
        L62:
            float[] r3 = b.a.m.n2.h0.a
            b.a.m.n2.h0 r3 = b.a.m.n2.h0.c.a
            boolean r4 = r3.e(r13)
            if (r4 == 0) goto L1de
            long r3 = r3.d(r13)
            com.android.launcher3.model.data.FolderInfo r3 = com.android.launcher3.LauncherModel.getFolderInfoById(r3)
            if (r3 != 0) goto L78
            goto L1de
        L78:
            com.android.launcher3.Workspace r4 = r13.mWorkspace
            int r3 = r3.screenId
            com.android.launcher3.CellLayout r3 = r4.getScreenWithId(r3)
            if (r3 != 0) goto L84
            goto L1de
        L84:
            java.util.ArrayList r4 = new java.util.ArrayList
            r4.<init>()
            java.util.HashSet r5 = new java.util.HashSet
            r5.<init>()
            boolean r6 = com.android.launcher3.config.FeatureFlags.IS_E_OS
            if (r6 == 0) goto L9d
            int r6 = com.microsoft.launcher.enterprise.EnterpriseConstant.a
            java.lang.String[] r6 = b.a.m.m4.a1.a
            java.util.List r6 = java.util.Arrays.asList(r6)
            r5.addAll(r6)
        L9d:
            java.util.Iterator r14 = r14.iterator()
        La1:
            boolean r6 = r14.hasNext()
            if (r6 == 0) goto Lc7
            java.lang.Object r6 = r14.next()
            com.android.launcher3.model.data.AppInfo r6 = (com.android.launcher3.model.data.AppInfo) r6
            android.os.UserHandle r7 = r6.user
            android.os.UserHandle r8 = r0.a
            boolean r7 = r7.equals(r8)
            if (r7 == 0) goto La1
            android.content.ComponentName r7 = r6.componentName
            java.lang.String r7 = r7.getPackageName()
            boolean r7 = r5.contains(r7)
            if (r7 != 0) goto La1
            r4.add(r6)
            goto La1
        Lc7:
            java.util.ArrayList r14 = new java.util.ArrayList
            r14.<init>()
            android.content.Context r0 = b.a.m.c4.v8.L()
            java.util.HashSet r5 = new java.util.HashSet
            r5.<init>()
            java.lang.String r6 = "blocklistdataspkey"
            java.lang.String r7 = "HiddenListKey"
            java.util.Set r0 = b.a.m.m4.t.t(r0, r6, r7, r5)
            boolean r5 = r0.isEmpty()
            if (r5 != 0) goto L10f
            android.content.Context r5 = r13.getApplicationContext()
            java.util.Iterator r4 = r4.iterator()
        Leb:
            boolean r6 = r4.hasNext()
            if (r6 == 0) goto L10e
            java.lang.Object r6 = r4.next()
            com.android.launcher3.model.data.AppInfo r6 = (com.android.launcher3.model.data.AppInfo) r6
            com.android.launcher3.util.ComponentKey r7 = new com.android.launcher3.util.ComponentKey
            android.content.ComponentName r8 = r6.componentName
            android.os.UserHandle r9 = r6.user
            r7.<init>(r8, r9)
            java.lang.String r7 = r7.serialize(r5)
            boolean r7 = r0.contains(r7)
            if (r7 != 0) goto Leb
            r14.add(r6)
            goto Leb
        L10e:
            r4 = r14
        L10f:
            int r14 = r4.size()
            if (r14 >= r1) goto L117
            goto L1de
        L117:
            com.android.launcher3.ShortcutAndWidgetContainer r14 = r3.getShortcutsAndWidgets()
            r0 = 0
        L11c:
            int r3 = r14.getChildCount()
            if (r0 >= r3) goto L1de
            android.view.View r3 = r14.getChildAt(r0)
            boolean r5 = r3 instanceof com.microsoft.launcher.enterprise.views.WorkFolderIcon
            if (r5 == 0) goto L1da
            com.microsoft.launcher.enterprise.views.WorkFolderIcon r3 = (com.microsoft.launcher.enterprise.views.WorkFolderIcon) r3
            m.f.a r5 = new m.f.a
            r5.<init>()
            com.android.launcher3.model.data.FolderInfo r6 = r3.getFolderInfo()
            java.util.List<com.android.launcher3.model.data.WorkspaceItemInfo> r6 = r6.contents
            java.util.Iterator r6 = r6.iterator()
            r7 = 0
        L13c:
            boolean r8 = r6.hasNext()
            if (r8 == 0) goto L159
            java.lang.Object r8 = r6.next()
            com.android.launcher3.model.data.WorkspaceItemInfo r8 = (com.android.launcher3.model.data.WorkspaceItemInfo) r8
            android.content.Intent r8 = r8.intent
            android.content.ComponentName r8 = r8.getComponent()
            int r9 = r7 + 1
            java.lang.Integer r7 = java.lang.Integer.valueOf(r7)
            r5.put(r8, r7)
            r7 = r9
            goto L13c
        L159:
            java.util.Iterator r6 = r4.iterator()
        L15d:
            boolean r7 = r6.hasNext()
            if (r7 == 0) goto L1da
            java.lang.Object r7 = r6.next()
            com.android.launcher3.model.data.AppInfo r7 = (com.android.launcher3.model.data.AppInfo) r7
            r8 = 0
            android.content.ComponentName r9 = r7.componentName
            boolean r9 = r5.containsKey(r9)
            r10 = 270532608(0x10200000, float:3.1554436E-29)
            if (r9 == 0) goto L1b3
            android.content.ComponentName r8 = r7.componentName
            java.lang.Object r8 = r5.get(r8)
            java.lang.Integer r8 = (java.lang.Integer) r8
            if (r8 != 0) goto L17f
            goto L15d
        L17f:
            com.android.launcher3.model.data.FolderInfo r9 = r3.getFolderInfo()
            java.util.List<com.android.launcher3.model.data.WorkspaceItemInfo> r9 = r9.contents
            int r11 = r8.intValue()
            java.lang.Object r9 = r9.get(r11)
            com.android.launcher3.model.data.WorkspaceItemInfo r9 = (com.android.launcher3.model.data.WorkspaceItemInfo) r9
            com.android.launcher3.model.data.WorkspaceItemInfo r11 = new com.android.launcher3.model.data.WorkspaceItemInfo
            r11.<init>(r7)
            android.content.ComponentName r12 = r7.componentName
            r11.setActivity(r12, r10)
            com.android.launcher3.model.data.FolderInfo r10 = r3.getFolderInfo()
            int r8 = r8.intValue()
            int r8 = r8 + r1
            r10.add(r11, r8, r2)
            com.android.launcher3.model.data.FolderInfo r8 = r3.getFolderInfo()
            r8.remove(r9, r2)
            com.android.launcher3.model.ModelWriter r8 = r13.mModelWriter
            r8.deleteItemFromDatabase(r9)
            r8 = r11
            goto L1cd
        L1b3:
            int r9 = r7.type
            r11 = 4
            if (r9 != r11) goto L1cd
            com.android.launcher3.model.data.WorkspaceItemInfo r8 = new com.android.launcher3.model.data.WorkspaceItemInfo
            r8.<init>(r7)
            android.content.ComponentName r9 = r7.componentName
            r8.setActivity(r9, r10)
            com.android.launcher3.model.data.FolderInfo r9 = r3.mInfo
            java.util.List<com.android.launcher3.model.data.WorkspaceItemInfo> r10 = r9.contents
            int r10 = r10.size()
            r9.add(r8, r10, r1)
        L1cd:
            if (r8 == 0) goto L1d2
            r8.toString()
        L1d2:
            int r8 = r7.type
            r9 = 5
            if (r8 != r9) goto L15d
            r7.type = r2
            goto L15d
        L1da:
            int r0 = r0 + 1
            goto L11c
        L1de:
            return
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void bindDeepShortcutMap(java.util.HashMap<com.android.launcher3.util.ComponentKey, java.lang.Integer> r2) {
            r1 = this;
            com.android.launcher3.popup.PopupDataProvider r0 = r1.mPopupDataProvider
            r0.mDeepShortcutMap = r2
            return
    }

    public boolean bindFeaturePage(com.microsoft.launcher.featurepage.FeaturePageInfo r5) {
            r4 = this;
            com.microsoft.launcher.featurepage.FeaturePageStateManager r0 = r4.mFeaturePageStateManager
            boolean r0 = r0.d()
            r1 = 0
            if (r0 != 0) goto La
            return r1
        La:
            b.a.m.r2.c r0 = r4.mFeaturePageHost
            if (r0 != 0) goto Lf
            return r1
        Lf:
            android.view.View r0 = r4.inflateFeaturePage(r5)
            if (r0 == 0) goto L2b
            com.android.launcher3.Workspace r1 = r4.mWorkspace
            r1.addInScreen(r0, r5)
            com.android.launcher3.Workspace r0 = r4.mWorkspace
            r0.requestLayout()
            com.microsoft.launcher.featurepage.FeaturePageStateManager r0 = r4.mFeaturePageStateManager
            int r1 = r5.featurePageId
            int r5 = r5.screenId
            long r2 = (long) r5
            r0.f(r1, r2)
            r5 = 1
            return r5
        L2b:
            return r1
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void bindItems(java.util.List<com.android.launcher3.model.data.ItemInfo> r23, boolean r24) {
            r22 = this;
            r6 = r22
            r7 = r23
            java.util.ArrayList r8 = new java.util.ArrayList
            r8.<init>()
            r0 = 0
            if (r24 == 0) goto L2a
            com.android.launcher3.dragndrop.DragController r1 = r6.mDragController
            boolean r1 = r1.isDragging()
            if (r1 == 0) goto L15
            goto L24
        L15:
            long r1 = java.lang.System.currentTimeMillis()
            long r3 = r6.mLastTouchUpTime
            long r1 = r1 - r3
            r3 = 5000(0x1388, double:2.4703E-320)
            int r5 = (r1 > r3 ? 1 : (r1 == r3 ? 0 : -1))
            if (r5 <= 0) goto L24
            r1 = 1
            goto L25
        L24:
            r1 = 0
        L25:
            if (r1 == 0) goto L2a
            r1 = 1
            r9 = 1
            goto L2c
        L2a:
            r1 = 0
            r9 = 0
        L2c:
            com.android.launcher3.Workspace r10 = r6.mWorkspace
            int r11 = r23.size()
            java.util.ArrayList r12 = new java.util.ArrayList
            r12.<init>()
            java.util.HashSet r13 = new java.util.HashSet
            r13.<init>()
            boolean r14 = r22.isHasMicrosoftFolder()
            r1 = -101(0xffffffffffffff9b, float:NaN)
            if (r11 <= 0) goto L51
            java.lang.Object r0 = r7.get(r0)
            com.android.launcher3.model.data.ItemInfo r0 = (com.android.launcher3.model.data.ItemInfo) r0
            int r0 = r0.container
            if (r0 != r1) goto L51
            r0 = 1
            r15 = 1
            goto L53
        L51:
            r0 = 0
            r15 = 0
        L53:
            if (r15 == 0) goto L5a
            b.a.m.x2.n0 r0 = r6.mHotseatLayoutBehavior
            r0.j()
        L5a:
            r16 = -1
            r0 = 0
            r3 = r16
            r5 = 0
        L60:
            if (r5 >= r11) goto L2cc
            java.lang.Object r0 = r7.get(r5)
            r2 = r0
            com.android.launcher3.model.data.ItemInfo r2 = (com.android.launcher3.model.data.ItemInfo) r2
            int r0 = r2.container
            if (r0 != r1) goto L75
            com.android.launcher3.Hotseat r1 = r6.mHotseat
            if (r1 != 0) goto L75
            r18 = r3
            goto L10b
        L75:
            r1 = -103(0xffffffffffffff99, float:NaN)
            r18 = r3
            r3 = 4
            if (r0 != r1) goto L8f
            int r0 = r2.itemType
            if (r0 != r3) goto L10b
            com.android.launcher3.model.data.LauncherAppWidgetInfo r2 = (com.android.launcher3.model.data.LauncherAppWidgetInfo) r2
            r0 = 64
            boolean r0 = r2.hasRestoreFlag(r0)
            if (r0 == 0) goto L10b
            r6.inflateAppWidget(r2)
            goto L10b
        L8f:
            long r0 = (long) r0
            boolean r0 = com.android.launcher3.Hotseat.enableDebugLog(r0)
            if (r0 == 0) goto Lb7
            java.lang.String r0 = "Bind item "
            java.lang.StringBuilder r0 = b.c.e.c.a.G(r0)
            java.lang.CharSequence r1 = r2.title
            r0.append(r1)
            java.lang.String r1 = " with cellX "
            r0.append(r1)
            int r1 = r2.cellX
            r0.append(r1)
            java.lang.String r1 = " cellY "
            r0.append(r1)
            int r1 = r2.cellY
            java.lang.String r4 = "Hotseat"
            b.c.e.c.a.h0(r0, r1, r4)
        Lb7:
            int r0 = r2.itemType
            if (r0 == 0) goto L1bd
            r1 = 1
            if (r0 == r1) goto L1bd
            r1 = 2
            if (r0 == r1) goto L15b
            if (r0 == r3) goto L143
            r1 = 5
            if (r0 == r1) goto L143
            r1 = 6
            if (r0 == r1) goto L1bd
            r1 = 100
            if (r0 == r1) goto L1bd
            r1 = 200(0xc8, float:2.8E-43)
            if (r0 != r1) goto L13b
            com.microsoft.launcher.featurepage.FeaturePageStateManager r0 = r6.mFeaturePageStateManager
            boolean r0 = r0.d()
            if (r0 != 0) goto Lda
            goto L10b
        Lda:
            r0 = r2
            com.microsoft.launcher.featurepage.FeaturePageInfo r0 = (com.microsoft.launcher.featurepage.FeaturePageInfo) r0
            int r1 = r0.featurePageId
            java.util.Set<java.lang.Integer> r3 = com.microsoft.launcher.featurepage.FeaturePageStateManager.a
            java.lang.Integer r4 = java.lang.Integer.valueOf(r1)
            boolean r3 = r3.contains(r4)
            if (r3 == 0) goto Lef
            r13.add(r0)
            goto L10b
        Lef:
            android.util.SparseArray<com.microsoft.launcher.featurepage.FeaturePageProviderInfo> r3 = b.a.m.r2.g.a
            r3 = -1
            if (r1 > r3) goto Lf5
            goto L108
        Lf5:
            j$.util.concurrent.ConcurrentHashMap<java.lang.Integer, b.a.m.r2.f> r3 = b.a.m.r2.g.g
            java.lang.Integer r4 = java.lang.Integer.valueOf(r1)
            java.lang.Object r3 = r3.get(r4)
            b.a.m.r2.f r3 = (b.a.m.r2.f) r3
            if (r3 == 0) goto L108
            boolean r3 = r3.b(r6)
            goto L109
        L108:
            r3 = 0
        L109:
            if (r3 != 0) goto L10e
        L10b:
            r24 = r5
            goto L14e
        L10e:
            com.android.launcher3.Workspace r3 = r6.mWorkspace
            com.android.launcher3.Workspace$16 r4 = new com.android.launcher3.Workspace$16
            r4.<init>(r3, r1)
            android.view.View r3 = r3.getFirstMatch(r4)
            com.microsoft.launcher.featurepage.FeaturePageHostView r3 = (com.microsoft.launcher.featurepage.FeaturePageHostView) r3
            if (r3 == 0) goto L12a
            r4 = 0
            r6.removeItem(r3, r2, r4)
            b.a.m.r2.c r3 = r6.mFeaturePageHost
            if (r3 == 0) goto L12a
            android.util.SparseArray<com.microsoft.launcher.featurepage.FeaturePageHostView> r3 = r3.f4114b
            r3.remove(r1)
        L12a:
            android.view.View r0 = r6.inflateFeaturePage(r0)
            com.microsoft.launcher.featurepage.FeaturePageStateManager r3 = r6.mFeaturePageStateManager
            int r4 = r2.screenId
            r24 = r5
            long r4 = (long) r4
            r3.f(r1, r4)
            if (r0 != 0) goto L154
            goto L14e
        L13b:
            java.lang.RuntimeException r0 = new java.lang.RuntimeException
            java.lang.String r1 = "Invalid Item Type"
            r0.<init>(r1)
            throw r0
        L143:
            r24 = r5
            r0 = r2
            com.android.launcher3.model.data.LauncherAppWidgetInfo r0 = (com.android.launcher3.model.data.LauncherAppWidgetInfo) r0
            android.view.View r0 = r6.inflateAppWidget(r0)
            if (r0 != 0) goto L154
        L14e:
            r20 = r18
            r18 = r24
            goto L2c2
        L154:
            r7 = r2
            r20 = r18
            r18 = r24
            goto L1d3
        L15b:
            r24 = r5
            r5 = r2
            com.android.launcher3.model.data.FolderInfo r5 = (com.android.launcher3.model.data.FolderInfo) r5
            boolean r0 = r5.isCOBO()
            if (r0 == 0) goto L17a
            r0 = 2131493120(0x7f0c0100, float:1.8609711E38)
            r1 = 2131493039(0x7f0c00af, float:1.8609547E38)
            r3 = 2131493040(0x7f0c00b0, float:1.8609549E38)
        L16f:
            int r4 = r10.getCurrentPage()
            android.view.View r4 = r10.getChildAt(r4)
            android.view.ViewGroup r4 = (android.view.ViewGroup) r4
            goto L18a
        L17a:
            boolean r0 = r5.hasOption(r1)
            if (r0 == 0) goto L19b
            r0 = 2131493882(0x7f0c03fa, float:1.8611257E38)
            r1 = 2131493883(0x7f0c03fb, float:1.8611259E38)
            r3 = 2131493884(0x7f0c03fc, float:1.861126E38)
            goto L16f
        L18a:
            r7 = r2
            r2 = r3
            r20 = r18
            r3 = r22
            r18 = r24
            r24 = r5
            com.android.launcher3.folder.FolderIcon r0 = com.android.launcher3.folder.FolderIcon.inflateFolderAndIcon(r0, r1, r2, r3, r4, r5)
            r2 = r24
            goto L1b5
        L19b:
            r7 = r2
            r20 = r18
            r18 = r24
            r24 = r5
            r0 = 2131493120(0x7f0c0100, float:1.8609711E38)
            int r1 = r10.getCurrentPage()
            android.view.View r1 = r10.getChildAt(r1)
            android.view.ViewGroup r1 = (android.view.ViewGroup) r1
            r2 = r24
            com.android.launcher3.folder.FolderIcon r0 = com.android.launcher3.folder.FolderIcon.inflateFolderAndIcon(r0, r6, r1, r2)
        L1b5:
            java.util.List<com.android.launcher3.model.data.WorkspaceItemInfo> r1 = r2.contents
            if (r1 == 0) goto L1ce
            r6.processCoboFolderContents(r1, r0)
            goto L1ce
        L1bd:
            r7 = r2
            r20 = r18
            r18 = r5
            r2 = r7
            com.android.launcher3.model.data.WorkspaceItemInfo r2 = (com.android.launcher3.model.data.WorkspaceItemInfo) r2
            android.view.View r0 = r6.createShortcut(r2)
            if (r14 == 0) goto L1ce
            r12.add(r2)
        L1ce:
            com.android.launcher3.accessibility.LauncherAccessibilityDelegateWrapper r1 = r6.mAccessibilityDelegateWrapper
            m.i.p.r.t(r0, r1)
        L1d3:
            int r1 = r7.container
            r2 = -100
            if (r1 != r2) goto L254
            com.android.launcher3.Workspace r1 = r6.mWorkspace
            int r2 = r7.screenId
            com.android.launcher3.CellLayout r1 = r1.getScreenWithId(r2)
            if (r1 == 0) goto L1fc
            int r2 = r7.cellX
            int r3 = r7.cellY
            if (r2 < 0) goto L1f7
            if (r3 >= 0) goto L1ec
            goto L1f7
        L1ec:
            int r4 = r1.mCountX
            if (r2 >= r4) goto L1f7
            int r2 = r1.mCountY
            if (r3 < r2) goto L1f5
            goto L1f7
        L1f5:
            r2 = 0
            goto L1f8
        L1f7:
            r2 = 1
        L1f8:
            if (r2 == 0) goto L1fc
            goto L2c2
        L1fc:
            if (r1 == 0) goto L238
            int r2 = r7.cellX
            int r3 = r7.cellY
            boolean r2 = r1.isOccupied(r2, r3)
            if (r2 == 0) goto L238
            int r0 = r7.cellX
            int r2 = r7.cellY
            android.view.View r0 = r1.getChildAt(r0, r2)
            if (r0 != 0) goto L215
            java.lang.String r0 = ""
            goto L219
        L215:
            java.lang.Object r0 = r0.getTag()
        L219:
            java.lang.StringBuilder r1 = new java.lang.StringBuilder
            r1.<init>()
            java.lang.String r2 = "Collision while binding workspace item: "
            r1.append(r2)
            r1.append(r7)
            java.lang.String r2 = ". Collides with "
            r1.append(r2)
            r1.append(r0)
            r1.toString()
            com.android.launcher3.model.ModelWriter r0 = r6.mModelWriter
            r0.deleteItemFromDatabase(r7)
            goto L2c2
        L238:
            if (r1 != 0) goto L254
            java.lang.StringBuilder r1 = new java.lang.StringBuilder
            r1.<init>()
            java.lang.String r2 = "Screen is nto exist while binding workspace item: "
            r1.append(r2)
            r1.append(r7)
            java.lang.String r2 = "."
            r1.append(r2)
            r1.toString()
            com.android.launcher3.model.ModelWriter r1 = r6.mModelWriter
            r1.deleteItemFromDatabase(r7)
        L254:
            r10.addInScreenFromBind(r0, r7)
            if (r9 == 0) goto L2c2
            r1 = 0
            r0.setAlpha(r1)
            r0.setScaleX(r1)
            r0.setScaleY(r1)
            java.util.ArrayList r1 = new java.util.ArrayList
            r1.<init>()
            android.util.Property r2 = android.view.View.ALPHA
            r3 = 1
            float[] r4 = new float[r3]
            r5 = 1065353216(0x3f800000, float:1.0)
            r19 = 0
            r4[r19] = r5
            android.animation.PropertyValuesHolder r2 = android.animation.PropertyValuesHolder.ofFloat(r2, r4)
            r1.add(r2)
            android.util.Property r2 = android.view.View.SCALE_X
            float[] r4 = new float[r3]
            r4[r19] = r5
            android.animation.PropertyValuesHolder r2 = android.animation.PropertyValuesHolder.ofFloat(r2, r4)
            r1.add(r2)
            android.util.Property r2 = android.view.View.SCALE_Y
            float[] r3 = new float[r3]
            r3[r19] = r5
            android.animation.PropertyValuesHolder r2 = android.animation.PropertyValuesHolder.ofFloat(r2, r3)
            r1.add(r2)
            int r2 = r1.size()
            android.animation.PropertyValuesHolder[] r2 = new android.animation.PropertyValuesHolder[r2]
            java.lang.Object[] r1 = r1.toArray(r2)
            android.animation.PropertyValuesHolder[] r1 = (android.animation.PropertyValuesHolder[]) r1
            android.animation.ObjectAnimator r0 = android.animation.ObjectAnimator.ofPropertyValuesHolder(r0, r1)
            r1 = 450(0x1c2, double:2.223E-321)
            android.animation.ObjectAnimator r0 = r0.setDuration(r1)
            int r5 = r18 * 85
            long r1 = (long) r5
            r0.setStartDelay(r1)
            android.view.animation.OvershootInterpolator r1 = new android.view.animation.OvershootInterpolator
            r2 = 1067869798(0x3fa66666, float:1.3)
            r1.<init>(r2)
            r0.setInterpolator(r1)
            r8.add(r0)
            int r0 = r7.screenId
            long r3 = (long) r0
            goto L2c4
        L2c2:
            r3 = r20
        L2c4:
            int r5 = r18 + 1
            r1 = -101(0xffffffffffffff9b, float:NaN)
            r7 = r23
            goto L60
        L2cc:
            r20 = r3
            b.a.m.r2.c r0 = r6.mFeaturePageHost
            if (r0 == 0) goto L309
            java.util.Objects.requireNonNull(r0)
            java.util.Set<java.lang.Integer> r1 = com.microsoft.launcher.featurepage.FeaturePageStateManager.a
            com.microsoft.launcher.featurepage.FeaturePageStateManager r1 = com.microsoft.launcher.featurepage.FeaturePageStateManager.b.a
            android.content.Context r2 = r0.a
            com.android.launcher3.Launcher r2 = (com.android.launcher3.Launcher) r2
            com.android.launcher3.Workspace r2 = r2.mWorkspace
            java.util.Iterator r3 = r13.iterator()
        L2e3:
            boolean r4 = r3.hasNext()
            if (r4 == 0) goto L309
            java.lang.Object r4 = r3.next()
            com.microsoft.launcher.featurepage.FeaturePageInfo r4 = (com.microsoft.launcher.featurepage.FeaturePageInfo) r4
            int r5 = r4.featurePageId
            r1.e(r5)
            r0.k(r4)
            android.util.SparseArray<com.microsoft.launcher.featurepage.FeaturePageHostView> r7 = r0.f4114b
            r7.remove(r5)
            int r4 = r4.screenId
            int r5 = r2.getDefaultScreenId()
            if (r4 != r5) goto L305
            goto L2e3
        L305:
            r2.removeScreenWithoutAnim(r4)
            goto L2e3
        L309:
            if (r14 == 0) goto L30e
            r6.onBindMicrosoftFolderItems(r12)
        L30e:
            if (r15 == 0) goto L316
            b.a.m.x2.n0 r0 = r6.mHotseatLayoutBehavior
            r1 = 1
            r0.G(r1)
        L316:
            if (r9 == 0) goto L350
            r3 = r20
            int r0 = (r3 > r16 ? 1 : (r3 == r16 ? 0 : -1))
            if (r0 <= 0) goto L350
            android.animation.AnimatorSet r0 = new android.animation.AnimatorSet
            r0.<init>()
            r0.playTogether(r8)
            com.android.launcher3.Workspace r1 = r6.mWorkspace
            int r2 = r1.getNextPage()
            int r1 = r1.getScreenIdForPageIndex(r2)
            com.android.launcher3.Workspace r2 = r6.mWorkspace
            int r2 = r2.f(r3)
            b.c.b.b2 r5 = new b.c.b.b2
            r5.<init>(r0)
            long r0 = (long) r1
            r7 = 500(0x1f4, double:2.47E-321)
            int r9 = (r3 > r0 ? 1 : (r3 == r0 ? 0 : -1))
            com.android.launcher3.Workspace r0 = r6.mWorkspace
            if (r9 == 0) goto L34d
            com.android.launcher3.Launcher$12 r1 = new com.android.launcher3.Launcher$12
            r1.<init>(r6, r2, r5)
            r0.postDelayed(r1, r7)
            goto L350
        L34d:
            r0.postDelayed(r5, r7)
        L350:
            boolean r0 = r10.isDefaultScreenInit
            if (r0 == 0) goto L355
            goto L3af
        L355:
            com.android.launcher3.Launcher r0 = r10.mLauncher
            android.content.SharedPreferences r0 = r0.getSharedPrefs()
            r1 = 0
            java.lang.String r3 = "HOME_SCREEN_DEFAULT_SCREEN"
            long r0 = r0.getLong(r3, r1)
            int r1 = (int) r0
            java.lang.Integer r0 = java.lang.Integer.valueOf(r1)
            r10.mDefaultScreenId = r0
            boolean r0 = r10.p()
            if (r0 == 0) goto L37f
            r0 = 0
            r10.mCurrentPage = r0
            r0 = 1
            r10.isDefaultScreenInit = r0
            com.android.launcher3.Launcher r1 = r10.mLauncher
            int r1 = r1.mRestoredOverlayState
            if (r1 == 0) goto L3af
            r10.mShouldOpenFeedAfterBinding = r0
            goto L3af
        L37f:
            java.lang.Integer r0 = r10.mDefaultScreenId
            int r0 = r0.intValue()
            int r0 = r10.getPageIndexForScreenId(r0)
            r1 = -1
            if (r0 != r1) goto L39b
            r0 = 0
            java.lang.Integer r1 = java.lang.Integer.valueOf(r0)
            r10.mDefaultScreenId = r1
            int r1 = r1.intValue()
            r10.setDefaultScreen(r1)
            goto L39c
        L39b:
            r0 = 0
        L39c:
            java.lang.Integer r1 = r10.mDefaultScreenId
            int r1 = r1.intValue()
            int r1 = r10.getPageIndexForScreenId(r1)
            int r0 = java.lang.Math.max(r0, r1)
            r10.mCurrentPage = r0
            r0 = 1
            r10.isDefaultScreenInit = r0
        L3af:
            r10.requestLayout()
            return
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void bindPromiseAppProgressUpdated(com.android.launcher3.model.data.PromiseAppInfo r3) {
            r2 = this;
            com.android.launcher3.allapps.AllAppsContainerView r0 = r2.mAppsView
            if (r0 == 0) goto L10
            com.android.launcher3.allapps.AllAppsStore r0 = r0.getAppsStore()
            b.c.b.n2.q r1 = new b.c.b.n2.q
            r1.<init>(r3)
            r0.updateAllIcons(r1)
        L10:
            return
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void bindRestoreItemsChange(java.util.HashSet<com.android.launcher3.model.data.ItemInfo> r3) {
            r2 = this;
            com.android.launcher3.Workspace r0 = r2.mWorkspace
            b.c.b.u1 r1 = new b.c.b.u1
            r1.<init>(r0, r3)
            r0.mapOverItems(r1)
            com.android.launcher3.Launcher r3 = r0.mLauncher
            com.android.launcher3.folder.Folder r3 = com.android.launcher3.folder.Folder.getOpen(r3)
            if (r3 == 0) goto L17
            com.android.launcher3.folder.FolderPagedView r3 = r3.mContent
            r3.iterateOverItems(r1)
        L17:
            return
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void bindScreens(com.android.launcher3.util.IntArray r2) {
            r1 = this;
            boolean r0 = r2.isEmpty()
            if (r0 == 0) goto Lb
            com.android.launcher3.Workspace r0 = r1.mWorkspace
            r0.addExtraEmptyScreen()
        Lb:
            r1.bindAddScreens(r2)
            com.android.launcher3.Workspace r2 = r1.mWorkspace
            com.android.launcher3.util.WallpaperOffsetInterpolator r0 = r2.mWallpaperOffset
            boolean r0 = r0.mLockedToDefaultPage
            if (r0 == 0) goto L1c
            r0 = 1
            r2.mUnlockWallpaperFromDefaultPageOnLayout = r0
            r2.requestLayout()
        L1c:
            return
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void bindWidgetsRestored(java.util.ArrayList<com.android.launcher3.model.data.LauncherAppWidgetInfo> r9) {
            r8 = this;
            com.android.launcher3.Workspace r0 = r8.mWorkspace
            java.util.Objects.requireNonNull(r0)
            boolean r1 = r9.isEmpty()
            if (r1 != 0) goto L89
            com.android.launcher3.Workspace$DeferredWidgetRefresh r1 = new com.android.launcher3.Workspace$DeferredWidgetRefresh
            com.android.launcher3.Launcher r2 = r0.mLauncher
            com.android.launcher3.LauncherAppWidgetHost r2 = r2.mAppWidgetHost
            r1.<init>(r0, r9, r2)
            r2 = 0
            java.lang.Object r2 = r9.get(r2)
            com.android.launcher3.model.data.LauncherAppWidgetInfo r2 = (com.android.launcher3.model.data.LauncherAppWidgetInfo) r2
            android.content.Context r3 = r0.getContext()
            android.appwidget.AppWidgetManager r4 = android.appwidget.AppWidgetManager.getInstance(r3)
            r5 = 1
            boolean r5 = r2.hasRestoreFlag(r5)
            r6 = 0
            if (r5 == 0) goto L5d
            android.content.ComponentName r4 = r2.providerName
            android.os.UserHandle r2 = r2.user
            com.android.launcher3.util.PackageUserKey r5 = new com.android.launcher3.util.PackageUserKey
            java.lang.String r7 = r4.getPackageName()
            r5.<init>(r7, r2)
            com.android.launcher3.compat.AppWidgetManagerCompat r2 = com.android.launcher3.compat.AppWidgetManagerCompat.getInstance(r3)
            java.util.List r2 = r2.getAllProviders(r5)
            java.util.Iterator r2 = r2.iterator()
        L44:
            boolean r5 = r2.hasNext()
            if (r5 == 0) goto L7b
            java.lang.Object r5 = r2.next()
            android.appwidget.AppWidgetProviderInfo r5 = (android.appwidget.AppWidgetProviderInfo) r5
            android.content.ComponentName r7 = r5.provider
            boolean r7 = r7.equals(r4)
            if (r7 == 0) goto L44
            com.android.launcher3.LauncherAppWidgetProviderInfo r6 = com.android.launcher3.LauncherAppWidgetProviderInfo.fromProviderInfo(r3, r5)
            goto L7b
        L5d:
            int r2 = r2.appWidgetId
            r5 = -100
            if (r2 > r5) goto L70
            com.android.launcher3.util.MainThreadInitializedObject<com.android.launcher3.widget.custom.CustomWidgetManager> r4 = com.android.launcher3.widget.custom.CustomWidgetManager.INSTANCE
            java.lang.Object r3 = r4.get(r3)
            com.android.launcher3.widget.custom.CustomWidgetManager r3 = (com.android.launcher3.widget.custom.CustomWidgetManager) r3
            com.android.launcher3.LauncherAppWidgetProviderInfo r6 = r3.getWidgetProvider(r2)
            goto L7b
        L70:
            android.appwidget.AppWidgetProviderInfo r2 = r4.getAppWidgetInfo(r2)
            if (r2 != 0) goto L77
            goto L7b
        L77:
            com.android.launcher3.LauncherAppWidgetProviderInfo r6 = com.android.launcher3.LauncherAppWidgetProviderInfo.fromProviderInfo(r3, r2)
        L7b:
            if (r6 == 0) goto L81
            r1.run()
            goto L89
        L81:
            com.android.launcher3.Workspace$19 r1 = new com.android.launcher3.Workspace$19
            r1.<init>(r0, r9)
            r0.mapOverItems(r1)
        L89:
            return
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void bindWorkspaceComponentsRemoved(com.android.launcher3.util.ItemInfoMatcher r8) {
            r7 = this;
            com.android.launcher3.Workspace r0 = r7.mWorkspace
            java.util.HashSet r0 = r0.removeItemsByMatcher(r8)
            java.util.ArrayList r1 = new java.util.ArrayList
            r1.<init>()
            java.util.Iterator r2 = r0.iterator()
        Lf:
            boolean r3 = r2.hasNext()
            if (r3 == 0) goto L5b
            java.lang.Object r3 = r2.next()
            com.android.launcher3.model.data.ItemInfo r3 = (com.android.launcher3.model.data.ItemInfo) r3
            int r4 = r3.itemType
            r5 = 100
            if (r4 != r5) goto Lf
            int r4 = r3.id
            long r4 = (long) r4
            b.c.b.k3.o r6 = new b.c.b.k3.o
            r6.<init>(r4)
            com.android.launcher3.model.BgDataModel r4 = com.android.launcher3.LauncherModel.sBgDataModel
            com.android.launcher3.util.IntSparseArrayMap<com.android.launcher3.model.data.ItemInfo> r4 = r4.itemsIdMap
            java.util.HashSet r4 = r6.filterItemInfos(r4)
            java.util.Iterator r4 = r4.iterator()
        L35:
            boolean r5 = r4.hasNext()
            if (r5 == 0) goto Lf
            java.lang.Object r5 = r4.next()
            com.android.launcher3.model.data.ItemInfo r5 = (com.android.launcher3.model.data.ItemInfo) r5
            boolean r6 = r5 instanceof com.android.launcher3.model.data.WorkspaceItemInfo
            if (r6 == 0) goto L35
            int r6 = r3.container
            r5.container = r6
            int r6 = r3.screenId
            r5.screenId = r6
            int r6 = r3.cellX
            r5.cellX = r6
            int r6 = r3.cellY
            r5.cellY = r6
            com.android.launcher3.model.data.WorkspaceItemInfo r5 = (com.android.launcher3.model.data.WorkspaceItemInfo) r5
            r1.add(r5)
            goto L35
        L5b:
            int r0 = r0.size()
            if (r0 <= 0) goto L66
            com.android.launcher3.Workspace r0 = r7.mWorkspace
            r0.updateShortcuts(r1)
        L66:
            com.android.launcher3.dragndrop.DragController r0 = r7.mDragController
            com.android.launcher3.DropTarget$DragObject r1 = r0.mDragObject
            if (r1 == 0) goto L81
            com.android.launcher3.model.data.ItemInfo r1 = r1.dragInfo
            boolean r2 = r1 instanceof com.android.launcher3.model.data.WorkspaceItemInfo
            if (r2 == 0) goto L81
            android.content.ComponentName r2 = r1.getTargetComponent()
            if (r2 == 0) goto L81
            boolean r8 = r8.matches(r1, r2)
            if (r8 == 0) goto L81
            r0.cancelDrag()
        L81:
            return
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void bindWorkspaceItemsChanged(java.util.ArrayList<com.android.launcher3.model.data.WorkspaceItemInfo> r2) {
            r1 = this;
            boolean r0 = r2.isEmpty()
            if (r0 != 0) goto Lb
            com.android.launcher3.Workspace r0 = r1.mWorkspace
            r0.updateShortcuts(r2)
        Lb:
            return
    }

    public final void checkIfOverlayStillDeferred() {
            r2 = this;
            boolean r0 = r2.mDeferOverlayCallbacks
            if (r0 != 0) goto L5
            return
        L5:
            boolean r0 = r2.isStarted()
            if (r0 == 0) goto L1f
            boolean r0 = r2.hasBeenResumed()
            if (r0 == 0) goto L1e
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r0 = r2.mStateManager
            STATE_TYPE extends com.android.launcher3.statemanager.BaseState<STATE_TYPE> r0 = r0.mState
            com.android.launcher3.LauncherState r0 = (com.android.launcher3.LauncherState) r0
            r1 = 1
            boolean r0 = r0.hasFlag(r1)
            if (r0 == 0) goto L1f
        L1e:
            return
        L1f:
            r0 = 0
            r2.mDeferOverlayCallbacks = r0
            boolean r0 = r2.isStarted()
            if (r0 == 0) goto L2d
            com.android.systemui.plugins.shared.LauncherOverlayManager r0 = r2.mOverlayManager
            r0.onActivityStarted(r2)
        L2d:
            boolean r0 = r2.hasBeenResumed()
            if (r0 == 0) goto L39
            com.android.systemui.plugins.shared.LauncherOverlayManager r0 = r2.mOverlayManager
            r0.onActivityResumed(r2)
            goto L3e
        L39:
            com.android.systemui.plugins.shared.LauncherOverlayManager r0 = r2.mOverlayManager
            r0.onActivityPaused(r2)
        L3e:
            boolean r0 = r2.isStarted()
            if (r0 != 0) goto L49
            com.android.systemui.plugins.shared.LauncherOverlayManager r0 = r2.mOverlayManager
            r0.onActivityStopped(r2)
        L49:
            return
    }

    public boolean checkPendingBindAppWidgets() {
            r1 = this;
            r1.notifyBindAppWidgetsCompleted()
            r0 = 0
            return r0
    }

    public void checkSlideBarDuringDrag(boolean r1, boolean r2) {
            r0 = this;
            r1 = 0
            r0.isSlideBarTempHide = r1
            return
    }

    public void checkSlideBarDuringPageSwitch() {
            r5 = this;
            com.android.launcher3.dragndrop.DragController r0 = r5.mDragController
            boolean r0 = r0.isDragging()
            if (r0 != 0) goto L9
            return
        L9:
            com.android.launcher3.Workspace r0 = r5.mWorkspace
            int r0 = r0.getCurrentPage()
            com.android.launcher3.Workspace r1 = r5.mWorkspace
            boolean r1 = r1.shouldScrollVertically()
            r2 = 0
            if (r1 == 0) goto L1b
            com.microsoft.launcher.slidebar.SlideBarDropTarget r3 = r5.mTopSlideBar
            goto L1d
        L1b:
            com.microsoft.launcher.slidebar.SlideBarDropTarget r3 = r5.mLeftSlideBar
        L1d:
            r3.setVisibility(r2)
            if (r0 <= 0) goto L23
            return
        L23:
            com.android.launcher3.DeviceProfile r0 = r5.mDeviceProfile
            com.android.launcher3.InvariantDeviceProfile r0 = r0.inv
            int r0 = r0.numScreens
            r3 = 1
            r4 = 8
            if (r0 <= r3) goto L5a
            com.android.launcher3.Workspace r0 = r5.mWorkspace
            com.microsoft.launcher.hotseat.OverlayAwareHotseat$g r0 = r0.getOccupyChecker()
            boolean r0 = r0.b(r3)
            if (r0 == 0) goto L50
            com.android.launcher3.Workspace r0 = r5.mWorkspace
            r3 = -1000(0xfffffffffffffc18, float:NaN)
            com.android.launcher3.CellLayout r0 = r0.getScreenWithId(r3)
            if (r0 == 0) goto L45
            goto L50
        L45:
            if (r1 == 0) goto L4a
            com.microsoft.launcher.slidebar.SlideBarDropTarget r0 = r5.mTopSlideBar
            goto L4c
        L4a:
            com.microsoft.launcher.slidebar.SlideBarDropTarget r0 = r5.mLeftSlideBar
        L4c:
            r0.setVisibility(r2)
            goto L6e
        L50:
            if (r1 == 0) goto L64
            com.microsoft.launcher.slidebar.SlideBarDropTarget r0 = r5.mTopSlideBar
            r0.clearAnimation()
            com.microsoft.launcher.slidebar.SlideBarDropTarget r0 = r5.mTopSlideBar
            goto L6b
        L5a:
            com.microsoft.launcher.slidebar.SlideBarDropTarget r0 = r5.mTopSlideBar
            r0.clearAnimation()
            com.microsoft.launcher.slidebar.SlideBarDropTarget r0 = r5.mTopSlideBar
            r0.setVisibility(r4)
        L64:
            com.microsoft.launcher.slidebar.SlideBarDropTarget r0 = r5.mLeftSlideBar
            r0.clearAnimation()
            com.microsoft.launcher.slidebar.SlideBarDropTarget r0 = r5.mLeftSlideBar
        L6b:
            r0.setVisibility(r4)
        L6e:
            return
    }

    public boolean checkSlidebarShow(com.microsoft.launcher.slidebar.SlideBarDropTarget r7) {
            r6 = this;
            com.android.launcher3.Workspace r0 = r6.mWorkspace
            int r0 = r0.getCurrentPage()
            r1 = 1
            if (r0 <= 0) goto La
            return r1
        La:
            com.android.launcher3.Workspace r0 = r6.mWorkspace
            com.android.launcher3.DeviceProfile r2 = r6.mDeviceProfile
            com.android.launcher3.InvariantDeviceProfile r2 = r2.inv
            int r2 = r2.numScreens
            r3 = 0
            if (r2 <= r1) goto L66
            com.microsoft.launcher.hotseat.OverlayAwareHotseat$g r2 = r0.getOccupyChecker()
            boolean r4 = com.microsoft.launcher.allapps.AllAppsDragBehaviorFeature.a
            if (r4 == 0) goto L3c
            com.android.launcher3.dragndrop.DragController r4 = r6.mDragController
            com.android.launcher3.DropTarget$DragObject r4 = r4.mDragObject
            com.android.launcher3.allapps.AppDrawerBehavior r5 = r6.mAppDrawerBehavior
            if (r4 == 0) goto L2d
            com.android.launcher3.DragSource r4 = r4.dragSource
            boolean r4 = r4 instanceof com.android.launcher3.allapps.AllAppsContainerView
            if (r4 == 0) goto L2d
            r4 = 1
            goto L2e
        L2d:
            r4 = 0
        L2e:
            if (r4 == 0) goto L3c
            boolean r4 = r5.isAllowDismissDuringDrag(r6)
            if (r4 == 0) goto L3c
            boolean r4 = r5.isOpenOnLeftScreen
            if (r4 == 0) goto L3c
            r2 = 0
            goto L40
        L3c:
            boolean r2 = r2.b(r1)
        L40:
            if (r2 == 0) goto L4a
            r2 = -1000(0xfffffffffffffc18, float:NaN)
            com.android.launcher3.CellLayout r2 = r0.getScreenWithId(r2)
            if (r2 == 0) goto L65
        L4a:
            boolean r2 = r0.shouldScrollVertically()
            if (r2 == 0) goto L58
            int r2 = r7.getSlidePos()
            r4 = 2
            if (r2 != r4) goto L58
            return r3
        L58:
            boolean r0 = r0.shouldScrollVertically()
            if (r0 != 0) goto L65
            int r7 = r7.getSlidePos()
            if (r7 != 0) goto L65
            return r3
        L65:
            return r1
        L66:
            return r3
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void clearPendingBinds() {
            r3 = this;
            com.android.launcher3.util.ViewOnDrawExecutor r0 = r3.mPendingExecutor
            if (r0 == 0) goto L18
            r0.markCompleted()
            r0 = 0
            r3.mPendingExecutor = r0
            com.android.launcher3.allapps.AllAppsContainerView r0 = r3.mAppsView
            if (r0 == 0) goto L18
            com.android.launcher3.allapps.AllAppsStore r0 = r0.getAppsStore()
            int r1 = r0.mDeferUpdatesFlags
            r2 = -2
            r1 = r1 & r2
            r0.mDeferUpdatesFlags = r1
        L18:
            return
    }

    public void closeOverlay() {
            r2 = this;
            com.android.launcher3.Workspace r0 = r2.mWorkspace
            if (r0 == 0) goto L10
            boolean r0 = r2.isOverlayClosed()
            if (r0 != 0) goto L10
            com.android.launcher3.Workspace r0 = r2.mWorkspace
            r1 = 0
            r0.onOverlayScrollChanged(r1)
        L10:
            return
    }

    public final long completeAdd(int r18, android.content.Intent r19, int r20, com.android.launcher3.util.PendingRequestArgs r21) {
            r17 = this;
            r0 = r17
            r1 = r18
            r2 = r19
            r3 = r20
            r4 = r21
            int r5 = r4.screenId
            int r6 = r4.container
            r7 = -100
            if (r6 != r7) goto L16
            int r5 = r0.ensurePendingDropLayoutExists(r5)
        L16:
            r6 = 0
            r8 = 0
            r9 = 1
            if (r1 == r9) goto L4d
            r2 = 5
            if (r1 == r2) goto L48
            r2 = 12
            r6 = 13
            if (r1 == r2) goto L2d
            if (r1 == r6) goto L28
            goto L207
        L28:
            r0.completeRestoreAppWidget(r3, r4, r8)
            goto L207
        L2d:
            r1 = 4
            com.android.launcher3.model.data.LauncherAppWidgetInfo r1 = r0.completeRestoreAppWidget(r3, r4, r1)
            if (r1 == 0) goto L207
            com.android.launcher3.widget.WidgetManagerHelper r2 = r0.mAppWidgetManager
            com.android.launcher3.LauncherAppWidgetProviderInfo r2 = r2.getLauncherAppWidgetInfo(r3)
            if (r2 == 0) goto L207
            com.android.launcher3.widget.WidgetAddFlowHandler r3 = new com.android.launcher3.widget.WidgetAddFlowHandler
            r3.<init>(r2)
            int r2 = r1.appWidgetId
            r3.startConfigActivity(r0, r2, r1, r6)
            goto L207
        L48:
            r0.completeAddAppWidget(r3, r4, r6, r6)
            goto L207
        L4d:
            int r1 = r4.container
            int r3 = r4.cellX
            int r10 = r4.cellY
            int r11 = r4.mObjectType
            if (r11 != r9) goto L5a
            int r11 = r4.mArg1
            goto L5b
        L5a:
            r11 = 0
        L5b:
            if (r11 != r9) goto L1fb
            android.content.Intent r9 = r21.getPendingIntent()
            android.content.ComponentName r9 = r9.getComponent()
            if (r9 != 0) goto L69
            goto L1fb
        L69:
            int[] r15 = r0.mTmpAddItemCellCoordinates
            com.android.launcher3.CellLayout r14 = r0.getCellLayout(r1, r5)
            boolean r9 = com.android.launcher3.Utilities.ATLEAST_OREO
            java.lang.String r11 = "Launcher"
            if (r9 == 0) goto La6
            java.lang.String r9 = "android.content.pm.extra.PIN_ITEM_REQUEST"
            android.os.Parcelable r9 = r2.getParcelableExtra(r9)     // Catch: java.lang.RuntimeException -> L8a
            boolean r12 = r9 instanceof android.content.pm.LauncherApps.PinItemRequest     // Catch: java.lang.RuntimeException -> L8a
            if (r12 == 0) goto L82
            android.content.pm.LauncherApps$PinItemRequest r9 = (android.content.pm.LauncherApps.PinItemRequest) r9     // Catch: java.lang.RuntimeException -> L8a
            goto L83
        L82:
            r9 = r6
        L83:
            r12 = 0
            com.android.launcher3.model.data.WorkspaceItemInfo r9 = androidx.transition.CanvasUtils.createWorkspaceItemFromPinItemRequest(r0, r9, r12)     // Catch: java.lang.RuntimeException -> L8a
            goto La7
        L8a:
            java.lang.StringBuilder r1 = new java.lang.StringBuilder
            r1.<init>()
            java.lang.String r3 = "Unable to parse a valid custom shortcut result from Intent "
            r1.append(r3)
            r1.append(r2)
            java.lang.String r1 = r1.toString()
            android.util.Log.e(r11, r1)
            java.lang.String r1 = "Unable to create a shortcut"
            android.widget.Toast r1 = android.widget.Toast.makeText(r0, r1, r8)
            goto L144
        La6:
            r9 = r6
        La7:
            if (r9 != 0) goto L14b
            android.os.UserHandle r9 = android.os.Process.myUserHandle()
            android.os.UserHandle r12 = r4.user
            boolean r9 = r9.equals(r12)
            if (r9 == 0) goto Lc5
            com.android.launcher3.InstallShortcutReceiver$PendingInstallShortcutInfo r2 = com.android.launcher3.InstallShortcutReceiver.createPendingInfo(r0, r2)
            if (r2 != 0) goto Lbc
            goto Lc5
        Lbc:
            android.util.Pair r2 = r2.getItemInfo()
            java.lang.Object r2 = r2.first
            r6 = r2
            com.android.launcher3.model.data.WorkspaceItemInfo r6 = (com.android.launcher3.model.data.WorkspaceItemInfo) r6
        Lc5:
            if (r6 != 0) goto Lcb
            java.lang.String r1 = "Unable to parse a valid custom shortcut result"
            goto L1f8
        Lcb:
            android.content.pm.PackageManager r2 = r17.getPackageManager()
            com.android.launcher3.compat.LauncherAppsCompat.getInstance(r17)
            android.content.Intent r9 = r6.intent
            android.content.Intent r12 = r21.getPendingIntent()
            android.content.ComponentName r12 = r12.getComponent()
            java.lang.String r12 = r12.getPackageName()
            android.content.pm.ResolveInfo r9 = com.microsoft.intune.mam.j.f.d.a.t(r2, r9, r8)
            if (r9 != 0) goto Le7
            goto L124
        Le7:
            android.content.pm.ActivityInfo r13 = r9.activityInfo
            java.lang.String r13 = r13.permission
            boolean r13 = android.text.TextUtils.isEmpty(r13)
            if (r13 == 0) goto Lf2
            goto L122
        Lf2:
            boolean r13 = android.text.TextUtils.isEmpty(r12)
            if (r13 == 0) goto Lf9
            goto L124
        Lf9:
            android.content.pm.ActivityInfo r13 = r9.activityInfo
            java.lang.String r13 = r13.permission
            int r13 = com.microsoft.intune.mam.j.f.d.a.a(r2, r13, r12)
            if (r13 == 0) goto L104
            goto L124
        L104:
            boolean r13 = com.android.launcher3.Utilities.ATLEAST_MARSHMALLOW
            if (r13 != 0) goto L109
            goto L122
        L109:
            android.content.pm.ActivityInfo r9 = r9.activityInfo
            java.lang.String r9 = r9.permission
            java.lang.String r9 = android.app.AppOpsManager.permissionToOp(r9)
            boolean r9 = android.text.TextUtils.isEmpty(r9)
            if (r9 == 0) goto L118
            goto L122
        L118:
            android.content.pm.ApplicationInfo r2 = com.microsoft.intune.mam.j.f.d.a.e(r2, r12, r8)     // Catch: android.content.pm.PackageManager.NameNotFoundException -> L124
            int r2 = r2.targetSdkVersion     // Catch: android.content.pm.PackageManager.NameNotFoundException -> L124
            r9 = 23
            if (r2 < r9) goto L124
        L122:
            r2 = 1
            goto L125
        L124:
            r2 = 0
        L125:
            if (r2 != 0) goto L149
            java.lang.String r1 = "Ignoring malicious intent "
            java.lang.StringBuilder r1 = b.c.e.c.a.G(r1)
            android.content.Intent r2 = r6.intent
            java.lang.String r2 = r2.toUri(r8)
            r1.append(r2)
            java.lang.String r1 = r1.toString()
            android.util.Log.e(r11, r1)
            r1 = 2131823195(0x7f110a5b, float:1.9279183E38)
            android.widget.Toast r1 = android.widget.Toast.makeText(r0, r1, r8)
        L144:
            r1.show()
            goto L1fb
        L149:
            r2 = r6
            goto L14c
        L14b:
            r2 = r9
        L14c:
            if (r1 >= 0) goto L1d5
            r2.container = r1
            if (r1 != r7) goto L166
            int r4 = r2.spanX
            int r6 = b.a.m.c4.v8.L0()
            int r6 = r6 * r4
            r2.spanX = r6
            int r4 = r2.spanY
            int r6 = b.a.m.c4.v8.L0()
            int r6 = r6 * r4
            r2.spanY = r6
        L166:
            android.view.View r4 = r0.createShortcut(r2)
            if (r3 < 0) goto L1a5
            if (r10 < 0) goto L1a5
            r15[r8] = r3
            r3 = 1
            r15[r3] = r10
            com.android.launcher3.dragndrop.MsDragObject r3 = new com.android.launcher3.dragndrop.MsDragObject
            r3.<init>()
            r3.dragInfo = r2
            com.android.launcher3.Workspace r9 = r0.mWorkspace
            r6 = 0
            r7 = 1
            r10 = r4
            r11 = r1
            r12 = r14
            r13 = r15
            r18 = r14
            r14 = r6
            r6 = r15
            r15 = r7
            r16 = r3
            boolean r7 = r9.createUserFolderIfNecessary(r10, r11, r12, r13, r14, r15, r16)
            if (r7 == 0) goto L191
            goto L1fb
        L191:
            com.android.launcher3.Workspace r11 = r0.mWorkspace
            r14 = 0
            r16 = 1
            r12 = r18
            r13 = r6
            r15 = r3
            boolean r3 = r11.addToExistingFolderIfNecessary(r12, r13, r14, r15, r16)
            if (r3 == 0) goto L1a1
            goto L1fb
        L1a1:
            r3 = 1
            r9 = r18
            goto L1b6
        L1a5:
            r18 = r14
            r6 = r15
            int r3 = b.a.m.c4.v8.L0()
            int r7 = b.a.m.c4.v8.L0()
            r9 = r18
            boolean r3 = r9.findCellForSpan(r6, r3, r7)
        L1b6:
            if (r3 != 0) goto L1be
            com.android.launcher3.Workspace r1 = r0.mWorkspace
            r1.onNoCellFound(r9)
            goto L1fb
        L1be:
            com.android.launcher3.model.ModelWriter r3 = r0.mModelWriter
            long r9 = (long) r1
            long r11 = (long) r5
            r1 = r6[r8]
            r7 = 1
            r13 = r6[r7]
            r6 = r3
            r7 = r2
            r8 = r9
            r10 = r11
            r12 = r1
            r6.addItemToDatabase(r7, r8, r10, r12, r13)
            com.android.launcher3.Workspace r1 = r0.mWorkspace
            r1.addInScreen(r4, r2)
            goto L1fb
        L1d5:
            com.android.launcher3.Workspace r3 = r0.mWorkspace
            b.c.b.q1 r6 = new b.c.b.q1
            r6.<init>(r1)
            android.view.View r3 = r3.getFirstMatch(r6)
            com.android.launcher3.folder.FolderIcon r3 = (com.android.launcher3.folder.FolderIcon) r3
            if (r3 == 0) goto L1f0
            java.lang.Object r1 = r3.getTag()
            com.android.launcher3.model.data.FolderInfo r1 = (com.android.launcher3.model.data.FolderInfo) r1
            int r3 = r4.rank
            r1.add(r2, r3, r8)
            goto L1fb
        L1f0:
            java.lang.String r2 = "Could not find folder with id "
            java.lang.String r3 = " to add shortcut."
            java.lang.String r1 = b.c.e.c.a.l(r2, r1, r3)
        L1f8:
            android.util.Log.e(r11, r1)
        L1fb:
            r1 = 2131822092(0x7f11060c, float:1.9276946E38)
            com.android.launcher3.dragndrop.DragLayer r2 = r0.mDragLayer
            java.lang.String r1 = r0.getString(r1)
            r2.announceForAccessibility(r1)
        L207:
            long r1 = (long) r5
            return r1
    }

    public void completeAddAppWidget(int r10, com.android.launcher3.model.data.ItemInfo r11, android.appwidget.AppWidgetHostView r12, com.android.launcher3.LauncherAppWidgetProviderInfo r13) {
            r9 = this;
            if (r13 != 0) goto L8
            com.android.launcher3.widget.WidgetManagerHelper r13 = r9.mAppWidgetManager
            com.android.launcher3.LauncherAppWidgetProviderInfo r13 = r13.getLauncherAppWidgetInfo(r10)
        L8:
            if (r13 != 0) goto L17
            java.lang.Exception r10 = new java.lang.Exception
            java.lang.String r11 = "null_appWidgetInfo"
            r10.<init>(r11)
            java.lang.String r11 = "appWidgetInfo should NOT be null"
            b.a.m.m4.h0.c(r11, r10)
            return
        L17:
            com.android.launcher3.model.data.LauncherAppWidgetInfo r8 = new com.android.launcher3.model.data.LauncherAppWidgetInfo
            android.content.ComponentName r0 = r13.provider
            r8.<init>(r10, r0)
            int r0 = r11.spanX
            r8.spanX = r0
            int r0 = r11.spanY
            r8.spanY = r0
            int r0 = r11.minSpanX
            r8.minSpanX = r0
            int r0 = r11.minSpanY
            r8.minSpanY = r0
            android.os.UserHandle r0 = r13.getProfile()
            r8.user = r0
            com.android.launcher3.model.ModelWriter r0 = r9.mModelWriter
            int r1 = r11.container
            long r2 = (long) r1
            int r1 = r11.screenId
            long r4 = (long) r1
            int r6 = r11.cellX
            int r7 = r11.cellY
            r1 = r8
            r0.addItemToDatabase(r1, r2, r4, r6, r7)
            if (r12 != 0) goto L4c
            com.android.launcher3.LauncherAppWidgetHost r11 = r9.mAppWidgetHost
            android.appwidget.AppWidgetHostView r12 = r11.createView(r9, r10, r13)
        L4c:
            r10 = 0
            r12.setVisibility(r10)
            r12.setTag(r8)
            r8.onBindAppWidget(r9, r12)
            r10 = 1
            r12.setFocusable(r10)
            com.android.launcher3.keyboard.ViewGroupFocusHelper r10 = r9.mFocusHandler
            r12.setOnFocusChangeListener(r10)
            com.android.launcher3.Workspace r10 = r9.mWorkspace
            r10.addInScreen(r12, r8)
            r10 = 2131822092(0x7f11060c, float:1.9276946E38)
            com.android.launcher3.dragndrop.DragLayer r11 = r9.mDragLayer
            java.lang.String r10 = r9.getString(r10)
            r11.announceForAccessibility(r10)
            return
    }

    public com.android.launcher3.model.data.LauncherAppWidgetInfo completeRestoreAppWidget(int r2, com.android.launcher3.util.PendingRequestArgs r3, int r4) {
            r1 = this;
            com.android.launcher3.Workspace r3 = r1.mWorkspace
            b.c.b.t1 r0 = new b.c.b.t1
            r0.<init>(r2)
            android.view.View r2 = r3.getFirstMatch(r0)
            com.android.launcher3.widget.LauncherAppWidgetHostView r2 = (com.android.launcher3.widget.LauncherAppWidgetHostView) r2
            r3 = 0
            if (r2 == 0) goto L3a
            boolean r0 = r2 instanceof com.android.launcher3.widget.PendingAppWidgetHostView
            if (r0 != 0) goto L15
            goto L3a
        L15:
            java.lang.Object r0 = r2.getTag()
            com.android.launcher3.model.data.LauncherAppWidgetInfo r0 = (com.android.launcher3.model.data.LauncherAppWidgetInfo) r0
            r0.restoreStatus = r4
            if (r4 != 0) goto L21
            r0.pendingItemInfo = r3
        L21:
            r3 = r2
            com.android.launcher3.widget.PendingAppWidgetHostView r3 = (com.android.launcher3.widget.PendingAppWidgetHostView) r3
            int r4 = r3.mStartState
            com.android.launcher3.model.data.LauncherAppWidgetInfo r3 = r3.mInfo
            int r3 = r3.restoreStatus
            if (r4 == r3) goto L2e
            r3 = 1
            goto L2f
        L2e:
            r3 = 0
        L2f:
            if (r3 == 0) goto L34
            r2.reInflate()
        L34:
            com.android.launcher3.model.ModelWriter r2 = r1.mModelWriter
            r2.updateItemInDatabase(r0)
            return r0
        L3a:
            java.lang.String r2 = "Launcher"
            java.lang.String r4 = "Widget update called, when the widget no longer exists."
            android.util.Log.e(r2, r4)
            return r3
    }

    public void completeTwoStageWidgetDrop(int r11, int r12, com.android.launcher3.util.PendingRequestArgs r13) {
            r10 = this;
            com.android.launcher3.Workspace r0 = r10.mWorkspace
            int r1 = r13.screenId
            com.android.launcher3.CellLayout r4 = r0.getScreenWithId(r1)
            r0 = 0
            r1 = -1
            if (r11 != r1) goto L26
            r11 = 3
            com.android.launcher3.LauncherAppWidgetHost r0 = r10.mAppWidgetHost
            com.android.launcher3.widget.WidgetAddFlowHandler r1 = r13.getWidgetHandler()
            android.appwidget.AppWidgetProviderInfo r1 = r1.mProviderInfo
            com.android.launcher3.LauncherAppWidgetProviderInfo r1 = com.android.launcher3.LauncherAppWidgetProviderInfo.fromProviderInfo(r10, r1)
            android.appwidget.AppWidgetHostView r0 = r0.createView(r10, r12, r1)
            com.android.launcher3.Launcher$4 r1 = new com.android.launcher3.Launcher$4
            r1.<init>(r10, r12, r13, r0)
            r8 = r0
            r6 = r1
            r7 = 3
            goto L36
        L26:
            if (r11 != 0) goto L32
            com.android.launcher3.LauncherAppWidgetHost r11 = r10.mAppWidgetHost
            r11.deleteAppWidgetId(r12)
            r11 = 4
            r6 = r0
            r8 = r6
            r7 = 4
            goto L36
        L32:
            r11 = 0
            r6 = r0
            r8 = r6
            r7 = 0
        L36:
            com.android.launcher3.dragndrop.DragLayer r11 = r10.mDragLayer
            android.view.View r11 = r11.getAnimatedView()
            if (r11 == 0) goto L4f
            com.android.launcher3.Workspace r2 = r10.mWorkspace
            com.android.launcher3.dragndrop.DragLayer r11 = r10.mDragLayer
            android.view.View r11 = r11.getAnimatedView()
            r5 = r11
            com.android.launcher3.dragndrop.DragView r5 = (com.android.launcher3.dragndrop.DragView) r5
            r9 = 1
            r3 = r13
            r2.animateWidgetDrop(r3, r4, r5, r6, r7, r8, r9)
            goto L54
        L4f:
            if (r6 == 0) goto L54
            r6.run()
        L54:
            return
    }

    public android.view.View createShortcut(android.view.ViewGroup r4, com.android.launcher3.model.data.WorkspaceItemInfo r5) {
            r3 = this;
            android.view.LayoutInflater r0 = android.view.LayoutInflater.from(r3)
            int r1 = r3.getIconLayout(r5)
            r2 = 0
            android.view.View r4 = r0.inflate(r1, r4, r2)
            com.android.launcher3.BubbleTextView r4 = (com.android.launcher3.BubbleTextView) r4
            r4.applyFromWorkspaceItem(r5, r2)
            android.view.View$OnClickListener r5 = com.android.launcher3.touch.ItemClickHandler.INSTANCE
            r4.setOnClickListener(r5)
            com.android.launcher3.keyboard.ViewGroupFocusHelper r5 = r3.mFocusHandler
            r4.setOnFocusChangeListener(r5)
            return r4
    }

    public android.view.View createShortcut(com.android.launcher3.model.data.WorkspaceItemInfo r3) {
            r2 = this;
            com.android.launcher3.Workspace r0 = r2.mWorkspace
            int r1 = r0.getCurrentPage()
            android.view.View r0 = r0.getChildAt(r1)
            android.view.ViewGroup r0 = (android.view.ViewGroup) r0
            android.view.View r3 = r2.createShortcut(r0, r3)
            return r3
    }

    public void dismissToolTip(int r1) {
            r0 = this;
            return
    }

    public void dispatchDeviceProfileChanged() {
            r3 = this;
            java.util.ArrayList<com.android.launcher3.DeviceProfile$OnDeviceProfileChangeListener> r0 = r3.mDPChangeListeners
            int r0 = r0.size()
        L6:
            int r0 = r0 + (-1)
            if (r0 < 0) goto L18
            java.util.ArrayList<com.android.launcher3.DeviceProfile$OnDeviceProfileChangeListener> r1 = r3.mDPChangeListeners
            java.lang.Object r1 = r1.get(r0)
            com.android.launcher3.DeviceProfile$OnDeviceProfileChangeListener r1 = (com.android.launcher3.DeviceProfile.OnDeviceProfileChangeListener) r1
            com.android.launcher3.DeviceProfile r2 = r3.mDeviceProfile
            r1.onDeviceProfileChanged(r2)
            goto L6
        L18:
            com.android.systemui.plugins.shared.LauncherOverlayManager r0 = r3.mOverlayManager
            r0.onDeviceProvideChanged()
            return
    }

    @Override // android.app.Activity, android.view.Window.Callback
    public boolean dispatchKeyEvent(android.view.KeyEvent r3) {
            r2 = this;
            boolean r0 = com.android.launcher3.Utilities.IS_RUNNING_IN_TEST_HARNESS
            if (r0 == 0) goto L19
            java.lang.StringBuilder r0 = new java.lang.StringBuilder
            r0.<init>()
            java.lang.String r1 = "Key event"
            r0.append(r1)
            java.lang.String r1 = ": "
            r0.append(r1)
            r0.append(r3)
            r0.toString()
        L19:
            int r0 = r3.getKeyCode()
            r1 = 3
            if (r0 == r1) goto L29
            boolean r3 = super.dispatchKeyEvent(r3)
            if (r3 == 0) goto L27
            goto L29
        L27:
            r3 = 0
            goto L2a
        L29:
            r3 = 1
        L2a:
            return r3
    }

    @Override // android.app.Activity, android.view.Window.Callback
    public boolean dispatchPopulateAccessibilityEvent(android.view.accessibility.AccessibilityEvent r3) {
            r2 = this;
            boolean r0 = super.dispatchPopulateAccessibilityEvent(r3)
            java.util.List r3 = r3.getText()
            r3.clear()
            com.android.launcher3.Workspace r1 = r2.mWorkspace
            if (r1 != 0) goto L17
            r1 = 2131821099(0x7f11022b, float:1.9274932E38)
            java.lang.String r1 = r2.getString(r1)
            goto L21
        L17:
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r1 = r2.mStateManager
            STATE_TYPE extends com.android.launcher3.statemanager.BaseState<STATE_TYPE> r1 = r1.mState
            com.android.launcher3.LauncherState r1 = (com.android.launcher3.LauncherState) r1
            java.lang.String r1 = r1.getDescription(r2)
        L21:
            r3.add(r1)
            return r0
    }

    @Override // android.app.Activity, android.view.Window.Callback
    public boolean dispatchTouchEvent(android.view.MotionEvent r3) {
            r2 = this;
            int r0 = r3.getAction()
            r1 = 1
            if (r0 == 0) goto L17
            if (r0 == r1) goto Ld
            r1 = 3
            if (r0 == r1) goto L13
            goto L19
        Ld:
            long r0 = java.lang.System.currentTimeMillis()
            r2.mLastTouchUpTime = r0
        L13:
            r0 = 0
            r2.mTouchInProgress = r0
            goto L19
        L17:
            r2.mTouchInProgress = r1
        L19:
            boolean r0 = com.android.launcher3.Utilities.IS_RUNNING_IN_TEST_HARNESS
            if (r0 == 0) goto L39
            int r0 = r3.getAction()
            r1 = 2
            if (r0 == r1) goto L39
            java.lang.StringBuilder r0 = new java.lang.StringBuilder
            r0.<init>()
            java.lang.String r1 = "Touch event"
            r0.append(r1)
            java.lang.String r1 = ": "
            r0.append(r1)
            r0.append(r3)
            r0.toString()
        L39:
            boolean r3 = super.dispatchTouchEvent(r3)
            return r3
    }

    @Override // android.app.Activity
    public void dump(java.lang.String r8, java.io.FileDescriptor r9, java.io.PrintWriter r10, java.lang.String[] r11) {
            r7 = this;
            super.dump(r8, r9, r10, r11)
            int r0 = r11.length
            r1 = 0
            if (r0 <= 0) goto Lc0
            r0 = r11[r1]
            java.lang.String r2 = "--all"
            boolean r0 = android.text.TextUtils.equals(r0, r2)
            if (r0 == 0) goto Lc0
            java.lang.StringBuilder r0 = new java.lang.StringBuilder
            r0.<init>()
            r0.append(r8)
            java.lang.String r2 = "Workspace Items"
            r0.append(r2)
            java.lang.String r0 = r0.toString()
            r10.println(r0)
            r0 = 0
        L26:
            com.android.launcher3.Workspace r2 = r7.mWorkspace
            int r2 = r2.getPageCount()
            java.lang.String r3 = "    "
            if (r0 >= r2) goto L7c
            java.lang.StringBuilder r2 = new java.lang.StringBuilder
            r2.<init>()
            r2.append(r8)
            java.lang.String r4 = "  Homescreen "
            r2.append(r4)
            r2.append(r0)
            java.lang.String r2 = r2.toString()
            r10.println(r2)
            com.android.launcher3.Workspace r2 = r7.mWorkspace
            android.view.View r2 = r2.getChildAt(r0)
            com.android.launcher3.CellLayout r2 = (com.android.launcher3.CellLayout) r2
            com.android.launcher3.ShortcutAndWidgetContainer r2 = r2.getShortcutsAndWidgets()
            r4 = 0
        L54:
            int r5 = r2.getChildCount()
            if (r4 >= r5) goto L79
            android.view.View r5 = r2.getChildAt(r4)
            java.lang.Object r5 = r5.getTag()
            if (r5 == 0) goto L76
            java.lang.StringBuilder r6 = b.c.e.c.a.J(r8, r3)
            java.lang.String r5 = r5.toString()
            r6.append(r5)
            java.lang.String r5 = r6.toString()
            r10.println(r5)
        L76:
            int r4 = r4 + 1
            goto L54
        L79:
            int r0 = r0 + 1
            goto L26
        L7c:
            java.lang.StringBuilder r0 = new java.lang.StringBuilder
            r0.<init>()
            r0.append(r8)
            java.lang.String r2 = "  Hotseat"
            r0.append(r2)
            java.lang.String r0 = r0.toString()
            r10.println(r0)
            com.android.launcher3.Hotseat r0 = r7.mHotseat
            com.android.launcher3.CellLayout r0 = r0.getLayout()
            com.android.launcher3.ShortcutAndWidgetContainer r0 = r0.getShortcutsAndWidgets()
            r2 = 0
        L9b:
            int r4 = r0.getChildCount()
            if (r2 >= r4) goto Lc0
            android.view.View r4 = r0.getChildAt(r2)
            java.lang.Object r4 = r4.getTag()
            if (r4 == 0) goto Lbd
            java.lang.StringBuilder r5 = b.c.e.c.a.J(r8, r3)
            java.lang.String r4 = r4.toString()
            r5.append(r4)
            java.lang.String r4 = r5.toString()
            r10.println(r4)
        Lbd:
            int r2 = r2 + 1
            goto L9b
        Lc0:
            java.lang.StringBuilder r0 = new java.lang.StringBuilder
            r0.<init>()
            r0.append(r8)
            java.lang.String r2 = "Misc:"
            r0.append(r2)
            java.lang.String r0 = r0.toString()
            r10.println(r0)
            r7.dumpMisc(r8, r10)
            java.lang.StringBuilder r0 = new java.lang.StringBuilder
            r0.<init>()
            r0.append(r8)
            java.lang.String r2 = "\tmWorkspaceLoading="
            r0.append(r2)
            boolean r2 = r7.mWorkspaceLoading
            r0.append(r2)
            java.lang.String r0 = r0.toString()
            r10.print(r0)
            java.lang.StringBuilder r0 = new java.lang.StringBuilder
            r0.<init>()
            java.lang.String r2 = " mPendingRequestArgs="
            r0.append(r2)
            com.android.launcher3.util.PendingRequestArgs r2 = r7.mPendingRequestArgs
            r0.append(r2)
            java.lang.String r0 = r0.toString()
            r10.print(r0)
            java.lang.StringBuilder r0 = new java.lang.StringBuilder
            r0.<init>()
            java.lang.String r2 = " mPendingActivityResult="
            r0.append(r2)
            com.android.launcher3.util.ActivityResultInfo r2 = r7.mPendingActivityResult
            r0.append(r2)
            java.lang.String r0 = r0.toString()
            r10.println(r0)
            java.lang.StringBuilder r0 = new java.lang.StringBuilder
            r0.<init>()
            java.lang.String r2 = " mRotationHelper: "
            r0.append(r2)
            com.android.launcher3.states.RotationHelper r2 = r7.mRotationHelper
            r0.append(r2)
            java.lang.String r0 = r0.toString()
            r10.println(r0)
            java.lang.StringBuilder r0 = new java.lang.StringBuilder
            r0.<init>()
            r0.append(r8)
            java.lang.String r2 = "\tmAppWidgetHost.isListening: "
            r0.append(r2)
            com.android.launcher3.LauncherAppWidgetHost r2 = r7.mAppWidgetHost
            int r2 = r2.mFlags
            r3 = 1
            r2 = r2 & r3
            if (r2 == 0) goto L149
            r2 = 1
            goto L14a
        L149:
            r2 = 0
        L14a:
            r0.append(r2)
            java.lang.String r0 = r0.toString()
            r10.println(r0)
            com.android.launcher3.dragndrop.DragLayer r0 = r7.mDragLayer
            java.util.Objects.requireNonNull(r0)
            java.lang.StringBuilder r2 = new java.lang.StringBuilder
            r2.<init>()
            r2.append(r8)
            java.lang.String r4 = "DragLayer:"
            r2.append(r4)
            java.lang.String r2 = r2.toString()
            r10.println(r2)
            com.android.launcher3.util.TouchController r2 = r0.mActiveController
            if (r2 == 0) goto L199
            java.lang.String r2 = "\tactiveController: "
            java.lang.StringBuilder r2 = b.c.e.c.a.J(r8, r2)
            com.android.launcher3.util.TouchController r4 = r0.mActiveController
            r2.append(r4)
            java.lang.String r2 = r2.toString()
            r10.println(r2)
            com.android.launcher3.util.TouchController r2 = r0.mActiveController
            java.lang.StringBuilder r4 = new java.lang.StringBuilder
            r4.<init>()
            r4.append(r8)
            java.lang.String r5 = "\t"
            r4.append(r5)
            java.lang.String r4 = r4.toString()
            r2.dump(r4, r10)
        L199:
            java.lang.String r2 = "\tdragLayerAlpha : "
            java.lang.StringBuilder r2 = b.c.e.c.a.J(r8, r2)
            com.android.launcher3.util.MultiValueAlpha r0 = r0.mMultiValueAlpha
            r2.append(r0)
            java.lang.String r0 = r2.toString()
            r10.println(r0)
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r0 = r7.mStateManager
            java.util.Objects.requireNonNull(r0)
            java.lang.StringBuilder r2 = new java.lang.StringBuilder
            r2.<init>()
            r2.append(r8)
            java.lang.String r4 = "StateManager:"
            r2.append(r4)
            java.lang.String r2 = r2.toString()
            r10.println(r2)
            java.lang.StringBuilder r2 = new java.lang.StringBuilder
            r2.<init>()
            r2.append(r8)
            java.lang.String r4 = "\tmLastStableState:"
            r2.append(r4)
            STATE_TYPE extends com.android.launcher3.statemanager.BaseState<STATE_TYPE> r4 = r0.mLastStableState
            r2.append(r4)
            java.lang.String r2 = r2.toString()
            r10.println(r2)
            java.lang.StringBuilder r2 = new java.lang.StringBuilder
            r2.<init>()
            r2.append(r8)
            java.lang.String r4 = "\tmCurrentStableState:"
            r2.append(r4)
            STATE_TYPE extends com.android.launcher3.statemanager.BaseState<STATE_TYPE> r4 = r0.mCurrentStableState
            r2.append(r4)
            java.lang.String r2 = r2.toString()
            r10.println(r2)
            java.lang.StringBuilder r2 = new java.lang.StringBuilder
            r2.<init>()
            r2.append(r8)
            java.lang.String r4 = "\tmState:"
            r2.append(r4)
            STATE_TYPE extends com.android.launcher3.statemanager.BaseState<STATE_TYPE> r4 = r0.mState
            r2.append(r4)
            java.lang.String r2 = r2.toString()
            r10.println(r2)
            java.lang.StringBuilder r2 = new java.lang.StringBuilder
            r2.<init>()
            r2.append(r8)
            java.lang.String r4 = "\tmRestState:"
            r2.append(r4)
            STATE_TYPE extends com.android.launcher3.statemanager.BaseState<STATE_TYPE> r4 = r0.mRestState
            r2.append(r4)
            java.lang.String r2 = r2.toString()
            r10.println(r2)
            java.lang.StringBuilder r2 = new java.lang.StringBuilder
            r2.<init>()
            r2.append(r8)
            java.lang.String r4 = "\tisInTransition:"
            r2.append(r4)
            com.android.launcher3.statemanager.StateManager$AnimationState r0 = r0.mConfig
            android.animation.AnimatorSet r0 = r0.currentAnimation
            if (r0 == 0) goto L23c
            r1 = 1
        L23c:
            r2.append(r1)
            java.lang.String r0 = r2.toString()
            r10.println(r0)
            com.android.launcher3.popup.PopupDataProvider r0 = r7.mPopupDataProvider
            java.util.Objects.requireNonNull(r0)
            java.lang.StringBuilder r1 = new java.lang.StringBuilder
            r1.<init>()
            r1.append(r8)
            java.lang.String r2 = "PopupDataProvider:"
            r1.append(r2)
            java.lang.String r1 = r1.toString()
            r10.println(r1)
            java.lang.StringBuilder r1 = new java.lang.StringBuilder
            r1.<init>()
            r1.append(r8)
            java.lang.String r2 = "\tmPackageUserToDotInfos:"
            r1.append(r2)
            java.util.Map<com.android.launcher3.util.PackageUserKey, com.android.launcher3.dot.DotInfo> r0 = r0.mPackageUserToDotInfos
            r1.append(r0)
            java.lang.String r0 = r1.toString()
            r10.println(r0)
            boolean r0 = com.android.launcher3.logging.FileLog.ENABLED     // Catch: java.lang.Exception -> L29c
            if (r0 != 0) goto L27d
            goto L29c
        L27d:
            java.util.concurrent.CountDownLatch r0 = new java.util.concurrent.CountDownLatch     // Catch: java.lang.Exception -> L29c
            r0.<init>(r3)     // Catch: java.lang.Exception -> L29c
            android.os.Handler r1 = com.android.launcher3.logging.FileLog.getHandler()     // Catch: java.lang.Exception -> L29c
            r2 = 3
            android.util.Pair r3 = android.util.Pair.create(r10, r0)     // Catch: java.lang.Exception -> L29c
            android.os.Message r1 = android.os.Message.obtain(r1, r2, r3)     // Catch: java.lang.Exception -> L29c
            r1.sendToTarget()     // Catch: java.lang.Exception -> L29c
            r1 = 2
            java.util.concurrent.TimeUnit r3 = java.util.concurrent.TimeUnit.SECONDS     // Catch: java.lang.Exception -> L29c
            r0.await(r1, r3)     // Catch: java.lang.Exception -> L29c
            r0.getCount()     // Catch: java.lang.Exception -> L29c
        L29c:
            com.android.launcher3.LauncherModel r0 = r7.mModel
            r0.dumpState(r8, r9, r10, r11)
            com.android.systemui.plugins.shared.LauncherOverlayManager r9 = r7.mOverlayManager
            r9.dump(r8, r10)
            return
    }

    public final int ensurePendingDropLayoutExists(int r2) {
            r1 = this;
            com.android.launcher3.Workspace r0 = r1.mWorkspace
            com.android.launcher3.util.IntSparseArrayMap<com.android.launcher3.CellLayout> r0 = r0.mWorkspaceScreens
            java.lang.Object r0 = r0.get(r2)
            com.android.launcher3.CellLayout r0 = (com.android.launcher3.CellLayout) r0
            if (r0 != 0) goto L17
            com.android.launcher3.Workspace r2 = r1.mWorkspace
            r2.addExtraEmptyScreen()
            com.android.launcher3.Workspace r2 = r1.mWorkspace
            int r2 = r2.commitExtraEmptyScreen()
        L17:
            return r2
    }

    public void enterMultiSelectionMode(com.android.launcher3.model.data.ItemInfo r7, b.a.m.h3.v r8) {
            r6 = this;
            b.a.m.h3.v r0 = r6.mCurrentMultiSelectable
            if (r0 == 0) goto L7
            r6.exitMultiSelectionMode1()
        L7:
            com.android.launcher3.LauncherRootView r0 = r6.mLauncherView
            r1 = 2131823502(0x7f110b8e, float:1.9279805E38)
            java.lang.String r1 = r6.getString(r1)
            r2 = 2
            java.lang.Object[] r2 = new java.lang.Object[r2]
            java.lang.CharSequence r3 = r7.contentDescription
            r4 = 0
            r2[r4] = r3
            r3 = 2131820721(0x7f1100b1, float:1.9274165E38)
            java.lang.String r3 = r6.getString(r3)
            r5 = 1
            r2[r5] = r3
            java.lang.String r1 = java.lang.String.format(r1, r2)
            r0.announceForAccessibility(r1)
            r6.mCurrentMultiSelectable = r8
            com.android.launcher3.DropTargetBar r8 = r6.getDropTargetBar()
            com.android.launcher3.ButtonDropTarget[] r8 = r8.mDropTargets
            int r0 = r8.length
        L32:
            if (r4 >= r0) goto L46
            r1 = r8[r4]
            boolean r2 = r1 instanceof com.microsoft.launcher.multiselection.MultiSelectableDropTarget
            if (r2 == 0) goto L43
            com.microsoft.launcher.multiselection.MultiSelectableDropTarget r1 = (com.microsoft.launcher.multiselection.MultiSelectableDropTarget) r1
            r2 = 0
            boolean r2 = r1.l(r2, r7)
            r1.f9665b = r2
        L43:
            int r4 = r4 + 1
            goto L32
        L46:
            b.a.m.h3.v r8 = r6.mCurrentMultiSelectable
            r8.enterMultiSelectionMode(r7)
            com.android.launcher3.DropTargetBar r7 = r6.getDropTargetBar()
            r7.showTargetBar()
            return
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void executeOnNextDraw(com.android.launcher3.util.ViewOnDrawExecutor r4) {
            r3 = this;
            r3.clearPendingBinds()
            r3.mPendingExecutor = r4
            com.android.launcher3.LauncherState r0 = com.android.launcher3.LauncherState.ALL_APPS
            boolean r0 = r3.isInState(r0)
            r1 = 1
            if (r0 != 0) goto L2e
            com.android.launcher3.allapps.AllAppsContainerView r0 = r3.mAppsView
            if (r0 == 0) goto L2e
            com.android.launcher3.allapps.AllAppsStore r0 = r0.getAppsStore()
            int r2 = r0.mDeferUpdatesFlags
            r2 = r2 | r1
            r0.mDeferUpdatesFlags = r2
            com.android.launcher3.util.ViewOnDrawExecutor r0 = r3.mPendingExecutor
            b.c.b.j0 r2 = new b.c.b.j0
            r2.<init>(r3)
            java.util.ArrayList<java.lang.Runnable> r0 = r0.mTasks
            r0.add(r2)
            com.android.launcher3.util.LooperExecutor r0 = com.android.launcher3.util.Executors.MODEL_EXECUTOR
            r2 = 10
            r0.setThreadPriority(r2)
        L2e:
            java.util.Objects.requireNonNull(r4)
            com.android.launcher3.Workspace r0 = r3.mWorkspace
            b.c.b.k3.z r2 = new b.c.b.k3.z
            r2.<init>(r3)
            r4.attachTo(r0, r1, r2)
            return
    }

    public boolean exitMultiSelectionMode1() {
            r2 = this;
            b.a.m.h3.v r0 = r2.mCurrentMultiSelectable
            if (r0 == 0) goto L22
            b.a.m.h3.w r1 = r0.getState()
            if (r1 == 0) goto L11
            boolean r1 = r1.d
            if (r1 == 0) goto L11
            r0.exitMultiSelectionMode()
        L11:
            com.android.launcher3.DropTargetBar r0 = r2.getDropTargetBar()
            r0.hideTargetBar()
            r0 = 0
            r2.mCurrentMultiSelectable = r0
            com.android.launcher3.Hotseat r0 = r2.mHotseat
            r0.handleExitMultiSelectionMode()
            r0 = 1
            return r0
        L22:
            r0 = 0
            return r0
    }

    public com.android.launcher3.folder.FolderIcon findFolderIcon(int r3) {
            r2 = this;
            com.android.launcher3.Workspace r0 = r2.mWorkspace
            b.c.b.q1 r1 = new b.c.b.q1
            r1.<init>(r3)
            android.view.View r3 = r0.getFirstMatch(r1)
            com.android.launcher3.folder.FolderIcon r3 = (com.android.launcher3.folder.FolderIcon) r3
            return r3
    }

    @Override // com.android.launcher3.statemanager.StatefulActivity, android.app.Activity
    public <T extends android.view.View> T findViewById(int r2) {
            r1 = this;
            com.android.launcher3.LauncherRootView r0 = r1.mLauncherView
            android.view.View r2 = r0.findViewById(r2)
            return r2
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void finishBindingItems(int r13) {
            r12 = this;
            com.android.launcher3.util.TraceHelper r0 = com.android.launcher3.util.TraceHelper.INSTANCE
            java.lang.String r0 = "finishBindingItems"
            com.android.launcher3.util.TraceHelper.beginSection(r0)
            com.android.launcher3.Workspace r1 = r12.mWorkspace
            int r2 = r1.getChildCount()
            r3 = 0
            r4 = 0
        Lf:
            if (r4 >= r2) goto L1f
            com.android.launcher3.util.IntArray r5 = r1.mRestoredPages
            boolean r5 = r5.contains(r4)
            if (r5 != 0) goto L1c
            r1.restoreInstanceStateForChild(r4)
        L1c:
            int r4 = r4 + 1
            goto Lf
        L1f:
            com.android.launcher3.util.IntArray r2 = r1.mRestoredPages
            r2.mSize = r3
            r2 = 0
            r1.mSavedStates = r2
            r12.mWorkspaceLoading = r3
            com.android.launcher3.util.ActivityResultInfo r1 = r12.mPendingActivityResult
            if (r1 == 0) goto L37
            int r4 = r1.requestCode
            int r5 = r1.resultCode
            android.content.Intent r1 = r1.data
            r12.handleActivityResult(r4, r5, r1)
            r12.mPendingActivityResult = r2
        L37:
            r1 = 2
            com.android.launcher3.InstallShortcutReceiver.disableAndFlushInstallQueue(r1, r12)
            com.android.launcher3.Workspace r2 = r12.mWorkspace
            com.android.launcher3.Launcher r4 = r2.mLauncher
            com.android.launcher3.DeviceProfile r5 = r4.mDeviceProfile
            com.android.launcher3.InvariantDeviceProfile r5 = r5.inv
            int r5 = r5.numScreens
            r2.mNumScreens = r5
            r6 = 1
            int r5 = r5 + r6
            int[] r5 = new int[r5]
            r2.mIntervals = r5
            b.a.m.u3.n r5 = new b.a.m.u3.n
            r5.<init>(r4)
            boolean r4 = r2.shouldScrollVertically()
            if (r4 == 0) goto L5b
            int r4 = r5.c
            goto L5d
        L5b:
            int r4 = r5.f4517b
        L5d:
            int r5 = r2.mNumScreens
            int r4 = r4 / r5
            boolean r5 = r2.shouldScrollVertically()
            r2.mIntervalsAxis = r5
            int[] r5 = r2.mIntervals
            r5[r3] = r3
            r5 = 1
        L6b:
            int r7 = r2.mNumScreens
            if (r5 > r7) goto L7b
            int[] r7 = r2.mIntervals
            int r8 = r5 + (-1)
            r8 = r7[r8]
            int r8 = r8 + r4
            r7[r5] = r8
            int r5 = r5 + 1
            goto L6b
        L7b:
            com.android.launcher3.Workspace r2 = r12.mWorkspace
            float r2 = r2.getTranslationY()
            r4 = 0
            int r2 = (r2 > r4 ? 1 : (r2 == r4 ? 0 : -1))
            if (r2 == 0) goto L8b
            com.android.launcher3.Workspace r2 = r12.mWorkspace
            r2.setTranslationY(r4)
        L8b:
            android.graphics.Rect r2 = com.android.launcher3.folder.Folder.sTempRect
            com.android.launcher3.AbstractFloatingView r2 = com.android.launcher3.AbstractFloatingView.getOpenView(r12, r6)
            com.android.launcher3.folder.Folder r2 = (com.android.launcher3.folder.Folder) r2
            if (r2 == 0) goto Lff
            com.android.launcher3.model.data.FolderInfo r5 = r2.mInfo
            int r5 = r5.id
            com.android.launcher3.folder.FolderIcon r5 = r12.findFolderIcon(r5)
            r7 = 8
            r8 = 3
            if (r5 == 0) goto Lc1
            r2.setTranslationX(r4)
            r2.setTranslationY(r4)
            r2.setFolderIcon(r5)
            com.android.launcher3.model.data.FolderInfo r4 = r2.mInfo
            r4.addListener(r2)
            r2.updateCellSize(r6)
            r2.centerAboutIcon()
            int r4 = r2.mState
            if (r4 == r8) goto Lbb
            goto Lff
        Lbb:
            com.android.launcher3.pageindicators.FolderPageIndicatorDots r2 = r2.mPageIndicator
            r2.setVisibility(r7)
            goto Lff
        Lc1:
            com.android.launcher3.model.data.FolderInfo r4 = r2.getInfo()
            int r4 = r4.container
            r5 = -102(0xffffffffffffff9a, float:NaN)
            if (r4 != r5) goto Lfc
            com.android.launcher3.allapps.AllAppsContainerView r4 = r12.mAppsView
            com.android.launcher3.model.data.FolderInfo r5 = r2.mInfo
            com.android.launcher3.folder.FolderIcon r4 = r4.getFolderIcon(r5)
            if (r4 == 0) goto Ld8
            r2.setFolderIcon(r4)
        Ld8:
            int r4 = r2.mState
            if (r4 != r8) goto Lde
            r4 = 1
            goto Ldf
        Lde:
            r4 = 0
        Ldf:
            r2.updateCellSize(r6)
            r2.centerAboutIcon()
            int r5 = r2.mState
            if (r5 == r8) goto Lea
            goto Lef
        Lea:
            com.android.launcher3.pageindicators.FolderPageIndicatorDots r5 = r2.mPageIndicator
            r5.setVisibility(r7)
        Lef:
            com.android.launcher3.Launcher$14 r5 = new com.android.launcher3.Launcher$14
            r5.<init>(r12, r4, r2)
            com.android.launcher3.model.data.FolderInfo r4 = r2.mInfo
            java.util.List<com.android.launcher3.model.data.WorkspaceItemInfo> r4 = r4.contents
            r2.animateOpen(r4, r3, r5, r3)
            goto Lff
        Lfc:
            r2.close(r3)
        Lff:
            b.a.m.r3.c r2 = b.a.m.r3.c.b()
            java.util.Objects.requireNonNull(r2)
            b.a.m.r3.g r4 = new b.a.m.r3.g
            java.lang.String r5 = "PillCountDataManagerNotifify"
            r4.<init>(r2, r5)
            java.lang.String r2 = com.microsoft.launcher.util.threadpool.ThreadPool.a
            com.microsoft.launcher.util.threadpool.ThreadPool$ThreadPriority r2 = com.microsoft.launcher.util.threadpool.ThreadPool.ThreadPriority.Normal
            com.microsoft.launcher.util.threadpool.ThreadPool.b(r4, r2)
            boolean r2 = r12.mIsUpdateConfig
            if (r2 == 0) goto L12c
            boolean r2 = r12.isMultiSelectionMode()
            if (r2 == 0) goto L12a
            b.a.m.h3.v r2 = r12.mCurrentMultiSelectable
            r2.restoreVisitViews()
            com.microsoft.launcher.multiselection.MultiSelectionDropTargetBar r2 = r12.mMultiSelectionTargetBar
            android.graphics.Rect r4 = r2.f9669b
            r2.setInsets(r4)
        L12a:
            r12.mIsUpdateConfig = r3
        L12c:
            com.android.launcher3.Workspace r2 = r12.mWorkspace
            boolean r3 = r2.mShouldOpenFeedAfterBinding
            if (r3 == 0) goto L13a
            com.android.launcher3.Launcher$15 r3 = new com.android.launcher3.Launcher$15
            r3.<init>(r12)
            r2.post(r3)
        L13a:
            boolean r2 = r12.mIsInOverviewWhenConfigChange
            if (r2 != 0) goto L145
            com.android.launcher3.LauncherState r2 = com.android.launcher3.LauncherState.OVERVIEW
            com.android.launcher3.uioverrides.overview.OverviewState r2 = (com.android.launcher3.uioverrides.overview.OverviewState) r2
            r2.refreshScaleAndTranslationResult(r12, r6)
        L145:
            com.android.launcher3.dragndrop.DragController r2 = r12.mDragController
            boolean r2 = r2.isDragging()
            if (r2 == 0) goto L196
            com.android.launcher3.Workspace r2 = r12.mWorkspace
            com.android.launcher3.CellLayout$CellInfo r2 = r2.getDragInfo()
            if (r2 != 0) goto L156
            goto L196
        L156:
            android.view.View r2 = r2.cell
            if (r2 != 0) goto L15b
            goto L196
        L15b:
            java.lang.Object r3 = r2.getTag()
            com.android.launcher3.model.data.ItemInfo r3 = (com.android.launcher3.model.data.ItemInfo) r3
            if (r3 != 0) goto L164
            goto L196
        L164:
            int r4 = r3.id
            long r4 = (long) r4
            com.android.launcher3.model.BgDataModel r6 = com.android.launcher3.LauncherModel.sBgDataModel
            com.android.launcher3.util.IntSparseArrayMap<com.android.launcher3.model.data.ItemInfo> r6 = r6.itemsIdMap
            java.lang.Object r4 = r6.get(r4)
            com.android.launcher3.model.data.ItemInfo r4 = (com.android.launcher3.model.data.ItemInfo) r4
            if (r4 != 0) goto L174
            goto L196
        L174:
            r4.copyFrom(r3)
            int r6 = r3.getCellXinDB()
            int r7 = r3.getCellYinDB()
            int r8 = r3.getSpanXinDB()
            int r9 = r3.getSpanYinDB()
            int r10 = r3.getMinSpanXinDB()
            int r11 = r3.getMinSpanYinDB()
            r5 = r4
            r5.setInitDBItemData(r6, r7, r8, r9, r10, r11)
            r2.setTag(r4)
        L196:
            com.android.launcher3.Workspace r2 = r12.mWorkspace
            r2.setCurrentPage(r13, r13)
            r13 = -1
            r12.mPageToBindSynchronously = r13
            com.android.launcher3.util.ViewCache r13 = r12.mViewCache
            r2 = 2131493118(0x7f0c00fe, float:1.8609707E38)
            com.android.launcher3.DeviceProfile r3 = r12.mDeviceProfile
            com.android.launcher3.InvariantDeviceProfile r3 = r3.inv
            int r4 = r3.numFolderColumns
            int r3 = r3.numFolderRows
            int r4 = r4 * r3
            android.util.SparseArray<com.android.launcher3.util.ViewCache$CacheEntry> r13 = r13.mCache
            com.android.launcher3.util.ViewCache$CacheEntry r3 = new com.android.launcher3.util.ViewCache$CacheEntry
            r3.<init>(r4)
            r13.put(r2, r3)
            com.android.launcher3.util.ViewCache r13 = r12.mViewCache
            r2 = 2131493123(0x7f0c0103, float:1.8609717E38)
            android.util.SparseArray<com.android.launcher3.util.ViewCache$CacheEntry> r13 = r13.mCache
            com.android.launcher3.util.ViewCache$CacheEntry r3 = new com.android.launcher3.util.ViewCache$CacheEntry
            r3.<init>(r1)
            r13.put(r2, r3)
            java.lang.String r13 = "End"
            com.android.launcher3.util.TraceHelper.endSection(r0, r13)
            com.android.launcher3.util.TraceHelper r0 = com.android.launcher3.util.TraceHelper.INSTANCE
            java.lang.String r0 = "startup"
            com.android.launcher3.util.TraceHelper.endSection(r0, r13)
            return
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void finishFirstPageBind(com.android.launcher3.util.ViewOnDrawExecutor r6) {
            r5 = this;
            com.android.launcher3.dragndrop.DragLayer r0 = r5.mDragLayer
            r1 = 1
            com.android.launcher3.util.MultiValueAlpha$AlphaProperty r0 = r0.getAlphaProperty(r1)
            float r2 = r0.mValue
            r3 = 1065353216(0x3f800000, float:1.0)
            int r2 = (r2 > r3 ? 1 : (r2 == r3 ? 0 : -1))
            if (r2 >= 0) goto L28
            android.util.FloatProperty<com.android.launcher3.util.MultiValueAlpha$AlphaProperty> r2 = com.android.launcher3.util.MultiValueAlpha.VALUE
            float[] r1 = new float[r1]
            r4 = 0
            r1[r4] = r3
            android.animation.ObjectAnimator r0 = android.animation.ObjectAnimator.ofFloat(r0, r2, r1)
            if (r6 == 0) goto L24
            com.android.launcher3.Launcher$13 r1 = new com.android.launcher3.Launcher$13
            r1.<init>(r5, r6)
            r0.addListener(r1)
        L24:
            r0.start()
            goto L2d
        L28:
            if (r6 == 0) goto L2d
            r6.onLoadAnimationCompleted()
        L2d:
            return
    }

    public void folderCreatedFromItem() {
            r0 = this;
            return
    }

    @Override // com.android.launcher3.BaseActivity, com.android.launcher3.widget.WidgetCellHost
    public m.i.p.a getAccessibilityDelegate() {
            r1 = this;
            com.android.launcher3.accessibility.LauncherAccessibilityDelegate r0 = r1.mAccessibilityDelegate
            return r0
    }

    @Override // com.android.launcher3.BaseActivity, com.android.launcher3.views.ActivityContext
    public m.i.p.a getAccessibilityDelegateWrapper() {
            r1 = this;
            com.android.launcher3.accessibility.LauncherAccessibilityDelegateWrapper r0 = r1.mAccessibilityDelegateWrapper
            return r0
    }

    @Override // com.android.launcher3.BaseDraggingActivity
    @android.annotation.TargetApi(23)
    public android.app.ActivityOptions getActivityLaunchOptions(android.view.View r2) {
            r1 = this;
            com.android.launcher3.LauncherAppTransitionManager r0 = r1.mAppTransitionManager
            android.app.ActivityOptions r2 = r0.getActivityLaunchOptions(r1, r2)
            return r2
    }

    public com.android.launcher3.CellLayout getCellLayout(int r2, int r3) {
            r1 = this;
            r0 = -101(0xffffffffffffff9b, float:NaN)
            if (r2 != r0) goto Lf
            com.android.launcher3.Hotseat r2 = r1.mHotseat
            if (r2 == 0) goto Ld
            com.android.launcher3.CellLayout r2 = r2.getLayout()
            return r2
        Ld:
            r2 = 0
            return r2
        Lf:
            com.android.launcher3.Workspace r2 = r1.mWorkspace
            com.android.launcher3.util.IntSparseArrayMap<com.android.launcher3.CellLayout> r2 = r2.mWorkspaceScreens
            java.lang.Object r2 = r2.get(r3)
            com.android.launcher3.CellLayout r2 = (com.android.launcher3.CellLayout) r2
            return r2
    }

    public com.microsoft.launcher.overview.BaseOverviewPanel getCurrentOverviewPanel() {
            r1 = this;
            com.android.launcher3.Workspace r0 = r1.mWorkspace
            boolean r0 = r0.shouldScrollVertically()
            if (r0 == 0) goto Ld
            com.microsoft.launcher.overview.VerticalOverviewPanel r0 = r1.getVerticalOverviewPanel()
            return r0
        Ld:
            com.microsoft.launcher.overview.OverviewPanel r0 = r1.mOverviewPanel
            return r0
    }

    public b.a.m.u3.r getCurrentPosture() {
            r1 = this;
            com.android.launcher3.DeviceProfile r0 = r1.mDeviceProfile
            boolean r0 = r0.isLandscape
            if (r0 == 0) goto L9
            b.a.m.u3.r r0 = b.a.m.u3.r.a
            goto Lb
        L9:
            b.a.m.u3.r r0 = b.a.m.u3.r.f4543b
        Lb:
            return r0
    }

    public int getCurrentWorkspaceScreen() {
            r1 = this;
            com.android.launcher3.Workspace r0 = r1.mWorkspace
            if (r0 == 0) goto L9
            int r0 = r0.getCurrentPage()
            return r0
        L9:
            r0 = 0
            return r0
    }

    @Override // com.android.systemui.plugins.shared.LauncherExterns
    public android.content.SharedPreferences getDevicePrefs() {
            r1 = this;
            android.content.SharedPreferences r0 = com.android.launcher3.Utilities.getDevicePrefs(r1)
            return r0
    }

    @Override // com.android.launcher3.BaseActivity, com.android.launcher3.views.ActivityContext
    public com.android.launcher3.dot.DotInfo getDotInfoForItem(com.android.launcher3.model.data.ItemInfo r2) {
            r1 = this;
            com.android.launcher3.popup.PopupDataProvider r0 = r1.mPopupDataProvider
            com.android.launcher3.dot.DotInfo r2 = r0.getDotInfoForItem(r2)
            return r2
    }

    @Override // com.android.launcher3.BaseActivity, com.android.launcher3.views.ActivityContext
    public com.android.launcher3.views.BaseDragLayer getDragLayer() {
            r1 = this;
            com.android.launcher3.dragndrop.DragLayer r0 = r1.mDragLayer
            return r0
    }

    public com.android.launcher3.DropTargetBar getDropTargetBar() {
            r1 = this;
            com.android.launcher3.DropTargetBar r0 = r1.mDropTargetBar
            return r0
    }

    public com.android.launcher3.CellLayout getHotseatLayout() {
            r1 = this;
            com.android.launcher3.Hotseat r0 = r1.mHotseat
            com.android.launcher3.CellLayout r0 = r0.getLayout()
            return r0
    }

    public int getIconLayout(com.android.launcher3.model.data.WorkspaceItemInfo r1) {
            r0 = this;
            r1 = 2131493010(0x7f0c0092, float:1.8609488E38)
            return r1
    }

    public b.a.m.w2.i getLauncherActivityStateFromLauncher() {
            r1 = this;
            r0 = 0
            return r0
    }

    public int getNextPageForFlip() {
            r1 = this;
            com.android.launcher3.Workspace r0 = r1.mWorkspace
            int r0 = r0.getCurrentPage()
            return r0
    }

    public float getOverlayOpenScrollProgress() {
            r1 = this;
            r0 = 1065353216(0x3f800000, float:1.0)
            return r0
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public int getPageToBindSynchronously() {
            r2 = this;
            int r0 = r2.mPageToBindSynchronously
            r1 = -1
            if (r0 == r1) goto L6
            return r0
        L6:
            com.android.launcher3.Workspace r0 = r2.mWorkspace
            if (r0 == 0) goto Lf
            int r0 = r0.getCurrentPage()
            return r0
        Lf:
            r0 = 0
            return r0
    }

    @Override // com.android.launcher3.statemanager.StatefulActivity
    public com.android.launcher3.LauncherRootView getRootView() {
            r1 = this;
            com.android.launcher3.LauncherRootView r0 = r1.mLauncherView
            return r0
    }

    @Override // com.android.systemui.plugins.shared.LauncherExterns
    public android.content.SharedPreferences getSharedPrefs() {
            r1 = this;
            android.content.SharedPreferences r0 = r1.mSharedPrefs
            return r0
    }

    public com.microsoft.launcher.slidebar.SlideBarDropTarget getSlideBar(int r2) {
            r1 = this;
            if (r2 != 0) goto L5
            com.microsoft.launcher.slidebar.SlideBarDropTarget r2 = r1.mLeftSlideBar
            return r2
        L5:
            r0 = 1
            if (r2 != r0) goto Lb
            com.microsoft.launcher.slidebar.SlideBarDropTarget r2 = r1.mRightSlideBar
            return r2
        Lb:
            r0 = 2
            if (r2 != r0) goto L11
            com.microsoft.launcher.slidebar.SlideBarDropTarget r2 = r1.mTopSlideBar
            return r2
        L11:
            r0 = 3
            if (r2 != r0) goto L17
            com.microsoft.launcher.slidebar.SlideBarDropTarget r2 = r1.mBottomSlideBar
            return r2
        L17:
            r2 = 0
            return r2
    }

    @Override // com.android.launcher3.statemanager.StatefulActivity
    public com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> getStateManager() {
            r1 = this;
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r0 = r1.mStateManager
            return r0
    }

    public com.android.launcher3.tasklayout.TaskLayoutHelper getTaskLayoutHelper() {
            r1 = this;
            com.android.launcher3.tasklayout.TaskLayoutHelper r0 = r1.mTaskLayoutHelper
            if (r0 != 0) goto L10
            com.android.launcher3.DeviceProfile r0 = r1.mDeviceProfile
            com.android.launcher3.InvariantDeviceProfile r0 = r0.inv
            com.android.launcher3.DeviceBehavior r0 = r0.mBehavior
            com.android.launcher3.tasklayout.TaskLayoutHelper r0 = r0.getTaskLayoutHelper(r1)
            r1.mTaskLayoutHelper = r0
        L10:
            com.android.launcher3.tasklayout.TaskLayoutHelper r0 = r1.mTaskLayoutHelper
            return r0
    }

    public final com.microsoft.launcher.overview.VerticalOverviewPanel getVerticalOverviewPanel() {
            r3 = this;
            com.microsoft.launcher.overview.VerticalOverviewPanel r0 = r3.mVerticalOverviewPanel
            if (r0 != 0) goto L20
            boolean r0 = com.android.launcher3.config.FeatureFlags.IS_E_OS
            r1 = 0
            if (r0 == 0) goto L11
            android.view.LayoutInflater r0 = android.view.LayoutInflater.from(r3)
            r2 = 2131493719(0x7f0c0357, float:1.8610926E38)
            goto L18
        L11:
            android.view.LayoutInflater r0 = android.view.LayoutInflater.from(r3)
            r2 = 2131493720(0x7f0c0358, float:1.8610928E38)
        L18:
            android.view.View r0 = r0.inflate(r2, r1)
            com.microsoft.launcher.overview.VerticalOverviewPanel r0 = (com.microsoft.launcher.overview.VerticalOverviewPanel) r0
            r3.mVerticalOverviewPanel = r0
        L20:
            com.microsoft.launcher.overview.VerticalOverviewPanel r0 = r3.mVerticalOverviewPanel
            return r0
    }

    @Override // com.android.launcher3.BaseActivity, com.android.launcher3.views.ActivityContext
    public com.android.launcher3.DeviceProfile getWallpaperDeviceProfile() {
            r1 = this;
            com.android.launcher3.DeviceProfile r0 = r1.mDeviceProfile
            return r0
    }

    public b.a.m.u4.n getWidgetLogger() {
            r1 = this;
            r0 = 0
            return r0
    }

    @Override // com.android.systemui.plugins.shared.LauncherExterns
    public /* synthetic */ com.android.launcher3.LoopScrollable getWorkspaceLoopScrollableDelegate() {
            r1 = this;
            com.android.launcher3.LoopScrollable r0 = b.c.d.a.c.a.a(r1)
            return r0
    }

    public void gotoOverviewState() {
            r1 = this;
            r0 = 0
            r1.gotoOverviewState(r0)
            return
    }

    public void gotoOverviewState(boolean r7) {
            r6 = this;
            com.android.launcher3.Workspace r0 = r6.mWorkspace
            int r0 = r0.mTouchState
            r1 = 1
            if (r0 == 0) goto Lc
            r2 = 5
            if (r0 == r2) goto Lc
            r0 = 0
            goto Ld
        Lc:
            r0 = 1
        Ld:
            if (r0 != 0) goto L10
            return
        L10:
            b.a.m.s2.g r0 = com.microsoft.launcher.features.FeatureManager.b()
            com.microsoft.launcher.codegen.launcher3.features.Feature r2 = com.microsoft.launcher.codegen.launcher3.features.Feature.OVERVIEW_SINGLE_SCREEN
            com.microsoft.launcher.features.FeatureManager r0 = (com.microsoft.launcher.features.FeatureManager) r0
            boolean r0 = r0.d(r2)
            if (r0 != 0) goto L3e
            com.android.launcher3.tasklayout.TaskLayoutHelper r0 = r6.getTaskLayoutHelper()
            boolean r0 = r0.isActivityOpenOnDisplay(r1)
            if (r0 != 0) goto L33
            com.android.launcher3.tasklayout.TaskLayoutHelper r0 = r6.getTaskLayoutHelper()
            r2 = 2
            boolean r0 = r0.isActivityOpenOnDisplay(r2)
            if (r0 == 0) goto L3e
        L33:
            r7 = 2131821727(0x7f11049f, float:1.9276205E38)
            android.widget.Toast r7 = android.widget.Toast.makeText(r6, r7, r1)
            r7.show()
            return
        L3e:
            boolean r0 = r6.isOverlayOpen()
            if (r0 != 0) goto L57
            com.android.launcher3.Workspace r0 = r6.mWorkspace
            boolean r0 = r0.shouldScrollVertically()
            if (r0 != 0) goto L57
            com.android.launcher3.dragndrop.DragLayer r0 = r6.mDragLayer
            float r0 = r0.getTranslationX()
            r2 = 0
            int r0 = (r0 > r2 ? 1 : (r0 == r2 ? 0 : -1))
            if (r0 != 0) goto L5d
        L57:
            boolean r0 = r6.isOverlayOpen()
            if (r0 == 0) goto L60
        L5d:
            r6.handleOverlayAnimatingOrOpen()
        L60:
            com.android.launcher3.Workspace r0 = r6.mWorkspace
            boolean r2 = r0.mIsPageInTransition
            if (r2 == 0) goto L72
            com.android.launcher3.dragndrop.DragLayer r2 = r6.mDragLayer
            java.lang.Object r2 = r2.getSwipeUpActionItem()
            if (r2 != 0) goto L72
            r0.snapToDestination()
            return
        L72:
            android.graphics.Rect r2 = new android.graphics.Rect
            r2.<init>()
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r3 = r6.mStateManager
            com.android.launcher3.LauncherState r4 = com.android.launcher3.LauncherState.OVERVIEW
            com.android.launcher3.Launcher$5 r5 = new com.android.launcher3.Launcher$5
            r5.<init>(r6, r0, r2, r7)
            r3.goToState(r4, r1, r5)
            return
    }

    public final void handleActivityResult(int r10, int r11, android.content.Intent r12) {
            r9 = this;
            boolean r0 = r9.mWorkspaceLoading
            if (r0 == 0) goto Lc
            com.android.launcher3.util.ActivityResultInfo r0 = new com.android.launcher3.util.ActivityResultInfo
            r0.<init>(r10, r11, r12)
            r9.mPendingActivityResult = r0
            return
        Lc:
            r0 = 0
            r9.mPendingActivityResult = r0
            com.android.launcher3.util.PendingRequestArgs r5 = r9.mPendingRequestArgs
            r9.mPendingRequestArgs = r0
            r0 = 1101(0x44d, float:1.543E-42)
            java.lang.String r1 = "appWidgetId"
            r2 = -1
            r3 = 1
            r7 = 0
            if (r10 != r0) goto L30
            if (r12 == 0) goto L23
            int r0 = r12.getIntExtra(r1, r2)
            goto L24
        L23:
            r0 = -1
        L24:
            b.a.m.u4.i r4 = b.a.m.u4.i.b()
            if (r11 != r2) goto L2c
            r6 = 1
            goto L2d
        L2c:
            r6 = 0
        L2d:
            r4.g(r0, r6, r3)
        L30:
            if (r5 != 0) goto L33
            return
        L33:
            int r0 = r5.mObjectType
            r4 = 2
            if (r0 != r4) goto L3b
            int r0 = r5.mArg1
            goto L3c
        L3b:
            r0 = 0
        L3c:
            com.android.launcher3.Launcher$3 r4 = new com.android.launcher3.Launcher$3
            r4.<init>(r9)
            r6 = 11
            r8 = 500(0x1f4, float:7.0E-43)
            if (r10 != r6) goto L6b
            if (r12 == 0) goto L4e
            int r10 = r12.getIntExtra(r1, r2)
            goto L4f
        L4e:
            r10 = -1
        L4f:
            if (r11 != 0) goto L5a
            r9.completeTwoStageWidgetDrop(r7, r10, r5)
            com.android.launcher3.Workspace r10 = r9.mWorkspace
            r10.removeExtraEmptyScreenDelayed(r8, r7, r4)
            goto L6a
        L5a:
            if (r11 != r2) goto L6a
            r4 = 0
            com.android.launcher3.widget.WidgetAddFlowHandler r11 = r5.getWidgetHandler()
            r6 = 500(0x1f4, float:7.0E-43)
            r1 = r9
            r2 = r10
            r3 = r5
            r5 = r11
            r1.addAppWidgetImpl(r2, r3, r4, r5, r6)
        L6a:
            return
        L6b:
            r6 = 9
            if (r10 == r6) goto L75
            r6 = 5
            if (r10 != r6) goto L73
            goto L75
        L73:
            r6 = 0
            goto L76
        L75:
            r6 = 1
        L76:
            if (r6 == 0) goto Lc4
            if (r12 == 0) goto L7e
            int r2 = r12.getIntExtra(r1, r2)
        L7e:
            if (r2 >= 0) goto L82
            r4 = r0
            goto L83
        L82:
            r4 = r2
        L83:
            if (r4 < 0) goto Laf
            if (r11 != 0) goto L88
            goto Laf
        L88:
            int r10 = r5.container
            r12 = -100
            if (r10 != r12) goto L96
            int r10 = r5.screenId
            int r10 = r9.ensurePendingDropLayoutExists(r10)
            r5.screenId = r10
        L96:
            com.android.launcher3.Workspace r10 = r9.mWorkspace
            int r12 = r5.screenId
            com.android.launcher3.CellLayout r6 = r10.getScreenWithId(r12)
            r6.setDropPending(r3)
            b.c.b.f0 r10 = new b.c.b.f0
            r1 = r10
            r2 = r9
            r3 = r11
            r1.<init>(r2, r3, r4, r5, r6)
            com.android.launcher3.Workspace r11 = r9.mWorkspace
            r11.removeExtraEmptyScreenDelayed(r8, r7, r10)
            goto Lc3
        Laf:
            java.lang.String r10 = "Launcher"
            java.lang.String r11 = "Error: appWidgetId (EXTRA_APPWIDGET_ID) was not returned from the widget configuration activity."
            android.util.Log.e(r10, r11)
            r9.completeTwoStageWidgetDrop(r7, r4, r5)
            com.android.launcher3.Workspace r10 = r9.mWorkspace
            b.c.b.d0 r11 = new b.c.b.d0
            r11.<init>(r9)
            r10.removeExtraEmptyScreenDelayed(r8, r7, r11)
        Lc3:
            return
        Lc4:
            r1 = 13
            if (r10 == r1) goto Le6
            r1 = 12
            if (r10 != r1) goto Lcd
            goto Le6
        Lcd:
            if (r10 != r3) goto Le0
            if (r11 != r2) goto Ld9
            int r0 = r5.container
            if (r0 == r2) goto Ld9
            r9.completeAdd(r10, r12, r2, r5)
            goto Ldb
        Ld9:
            if (r11 != 0) goto Le0
        Ldb:
            com.android.launcher3.Workspace r10 = r9.mWorkspace
            r10.removeExtraEmptyScreenDelayed(r8, r7, r4)
        Le0:
            com.android.launcher3.dragndrop.DragLayer r10 = r9.mDragLayer
            r10.clearAnimatedView()
            return
        Le6:
            if (r11 != r2) goto Leb
            r9.completeAdd(r10, r12, r0, r5)
        Leb:
            return
    }

    public void handleGestureContract(android.content.Intent r7) {
            r6 = this;
            boolean r0 = com.android.launcher3.Utilities.ATLEAST_R
            r1 = 0
            if (r0 != 0) goto L6
            goto L57
        L6:
            java.lang.String r0 = "gesture_nav_contract_v1"
            android.os.Bundle r2 = r7.getBundleExtra(r0)
            if (r2 != 0) goto Lf
            goto L57
        Lf:
            r7.removeExtra(r0)
            java.lang.String r0 = "android.intent.extra.COMPONENT_NAME"
            android.os.Parcelable r0 = r2.getParcelable(r0)
            android.content.ComponentName r0 = (android.content.ComponentName) r0
            java.lang.String r3 = "android.intent.extra.USER"
            android.os.Parcelable r3 = r2.getParcelable(r3)
            android.os.UserHandle r3 = (android.os.UserHandle) r3
            java.lang.String r4 = "android.intent.extra.REMOTE_CALLBACK"
            android.os.Parcelable r2 = r2.getParcelable(r4)
            android.os.Message r2 = (android.os.Message) r2
            java.lang.String r4 = "com.microsoft.surface.navux.hgm.KEY_RECT_HOME_GESTURE_PANEL"
            android.os.Parcelable r7 = r7.getParcelableExtra(r4)
            android.graphics.Rect r7 = (android.graphics.Rect) r7
            java.lang.StringBuilder r4 = new java.lang.StringBuilder
            r4.<init>()
            java.lang.String r5 = "HomeGesture from panel:"
            r4.append(r5)
            r4.append(r7)
            java.lang.String r4 = r4.toString()
            java.lang.String r5 = "GestureNavContract"
            android.util.Log.w(r5, r4)
            if (r0 == 0) goto L57
            if (r3 == 0) goto L57
            if (r2 == 0) goto L57
            android.os.Messenger r4 = r2.replyTo
            if (r4 == 0) goto L57
            com.android.launcher3.GestureNavContract r1 = new com.android.launcher3.GestureNavContract
            r1.<init>(r0, r3, r2, r7)
        L57:
            if (r1 == 0) goto L9b
            r7 = 0
            r0 = 4096(0x1000, float:5.74E-42)
            int r2 = com.android.launcher3.AbstractFloatingView.a
            com.android.launcher3.views.BaseDragLayer r2 = r6.getDragLayer()
            if (r2 != 0) goto L65
            goto L68
        L65:
            com.android.launcher3.AbstractFloatingView.closeAllOpenViews(r2, r7, r0)
        L68:
            int r7 = com.android.launcher3.views.FloatingSurfaceView.f7546b
            com.android.launcher3.util.ViewCache r7 = r6.mViewCache
            r0 = 2131493117(0x7f0c00fd, float:1.8609705E38)
            com.android.launcher3.dragndrop.DragLayer r2 = r6.mDragLayer
            android.view.View r7 = r7.getView(r0, r6, r2)
            com.android.launcher3.views.FloatingSurfaceView r7 = (com.android.launcher3.views.FloatingSurfaceView) r7
            r7.mContract = r1
            r0 = 1
            r7.mIsOpen = r0
            com.android.launcher3.util.LooperExecutor r1 = com.android.launcher3.util.Executors.MAIN_EXECUTOR
            android.os.Handler r1 = r1.mHandler
            java.lang.Runnable r2 = r7.mRemoveViewRunnable
            r1.removeCallbacks(r2)
            android.graphics.Picture r1 = r7.mPicture
            r1.beginRecording(r0, r0)
            android.graphics.Picture r0 = r7.mPicture
            r0.endRecording()
            com.android.launcher3.Launcher r0 = r7.mLauncher
            com.android.launcher3.dragndrop.DragLayer r0 = r0.mDragLayer
            r0.removeView(r7)
            com.android.launcher3.dragndrop.DragLayer r0 = r6.mDragLayer
            r0.addView(r7)
        L9b:
            return
    }

    public void handleOverlayAnimatingOrOpen() {
            r0 = this;
            return
    }

    public android.view.View inflateAppWidget(com.android.launcher3.model.data.LauncherAppWidgetInfo r11) {
            r10 = this;
            int r0 = r11.options
            r1 = 1
            r0 = r0 & r1
            r2 = 0
            if (r0 == 0) goto L9
            r0 = 1
            goto La
        L9:
            r0 = 0
        La:
            r3 = 0
            if (r0 == 0) goto L1b
            android.content.ComponentName r0 = com.android.launcher3.qsb.QsbContainerView.getSearchComponentName(r10)
            r11.providerName = r0
            if (r0 != 0) goto L1b
            com.android.launcher3.model.ModelWriter r0 = r10.mModelWriter
            r0.deleteItemFromDatabase(r11)
            return r3
        L1b:
            boolean r0 = r10.mIsSafeModeEnabled
            if (r0 == 0) goto L35
            com.android.launcher3.widget.PendingAppWidgetHostView r0 = new com.android.launcher3.widget.PendingAppWidgetHostView
            com.android.launcher3.icons.IconCache r2 = r10.mIconCache
            r0.<init>(r10, r11, r2, r1)
            r0.setTag(r11)
            r11.onBindAppWidget(r10, r0)
            r0.setFocusable(r1)
            com.android.launcher3.keyboard.ViewGroupFocusHelper r11 = r10.mFocusHandler
            r0.setOnFocusChangeListener(r11)
            return r0
        L35:
            com.android.launcher3.util.TraceHelper r0 = com.android.launcher3.util.TraceHelper.INSTANCE
            java.lang.String r0 = "BIND_WIDGET"
            com.android.launcher3.util.TraceHelper.beginSection(r0)
            r0 = 2
            boolean r4 = r11.hasRestoreFlag(r0)     // Catch: java.lang.Throwable -> L1e0
            if (r4 == 0) goto L45
            r4 = r3
            goto L5e
        L45:
            boolean r4 = r11.hasRestoreFlag(r1)     // Catch: java.lang.Throwable -> L1e0
            if (r4 == 0) goto L56
            com.android.launcher3.widget.WidgetManagerHelper r4 = r10.mAppWidgetManager     // Catch: java.lang.Throwable -> L1e0
            android.content.ComponentName r5 = r11.providerName     // Catch: java.lang.Throwable -> L1e0
            android.os.UserHandle r6 = r11.user     // Catch: java.lang.Throwable -> L1e0
            com.android.launcher3.LauncherAppWidgetProviderInfo r4 = r4.findProvider(r5, r6)     // Catch: java.lang.Throwable -> L1e0
            goto L5e
        L56:
            com.android.launcher3.widget.WidgetManagerHelper r4 = r10.mAppWidgetManager     // Catch: java.lang.Throwable -> L1e0
            int r5 = r11.appWidgetId     // Catch: java.lang.Throwable -> L1e0
            com.android.launcher3.LauncherAppWidgetProviderInfo r4 = r4.getLauncherAppWidgetInfo(r5)     // Catch: java.lang.Throwable -> L1e0
        L5e:
            boolean r0 = r11.hasRestoreFlag(r0)     // Catch: java.lang.Throwable -> L1e0
            if (r0 != 0) goto L14e
            int r0 = r11.restoreStatus     // Catch: java.lang.Throwable -> L1e0
            if (r0 == 0) goto L14e
            if (r4 != 0) goto L96
            java.lang.StringBuilder r0 = new java.lang.StringBuilder     // Catch: java.lang.Throwable -> L1e0
            r0.<init>()     // Catch: java.lang.Throwable -> L1e0
            java.lang.String r1 = "Removing restored widget: id="
            r0.append(r1)     // Catch: java.lang.Throwable -> L1e0
            int r1 = r11.appWidgetId     // Catch: java.lang.Throwable -> L1e0
            r0.append(r1)     // Catch: java.lang.Throwable -> L1e0
            java.lang.String r1 = " belongs to component "
            r0.append(r1)     // Catch: java.lang.Throwable -> L1e0
            android.content.ComponentName r1 = r11.providerName     // Catch: java.lang.Throwable -> L1e0
            r0.append(r1)     // Catch: java.lang.Throwable -> L1e0
            java.lang.String r1 = ", as the provider is null"
            r0.append(r1)     // Catch: java.lang.Throwable -> L1e0
            r0.toString()     // Catch: java.lang.Throwable -> L1e0
            com.android.launcher3.model.ModelWriter r0 = r10.mModelWriter     // Catch: java.lang.Throwable -> L1e0
            r0.deleteItemFromDatabase(r11)     // Catch: java.lang.Throwable -> L1e0
            com.android.launcher3.util.TraceHelper r11 = com.android.launcher3.util.TraceHelper.INSTANCE
            android.os.Trace.endSection()
            return r3
        L96:
            boolean r0 = r11.hasRestoreFlag(r1)     // Catch: java.lang.Throwable -> L1e0
            r5 = 4
            if (r0 == 0) goto L11d
            r0 = 16
            boolean r6 = r11.hasRestoreFlag(r0)     // Catch: java.lang.Throwable -> L1e0
            r7 = 64
            if (r6 == 0) goto Lb5
            boolean r8 = r11.hasRestoreFlag(r7)     // Catch: java.lang.Throwable -> L1e0
            if (r8 != 0) goto Lb5
            r8 = 128(0x80, float:1.8E-43)
            boolean r8 = r11.hasRestoreFlag(r8)     // Catch: java.lang.Throwable -> L1e0
            if (r8 == 0) goto L14e
        Lb5:
            if (r6 != 0) goto Lc4
            com.android.launcher3.LauncherAppWidgetHost r6 = r10.mAppWidgetHost     // Catch: java.lang.Throwable -> L1e0
            int r6 = r6.allocateAppWidgetId()     // Catch: java.lang.Throwable -> L1e0
            r11.appWidgetId = r6     // Catch: java.lang.Throwable -> L1e0
            int r6 = r11.restoreStatus     // Catch: java.lang.Throwable -> L1e0
            r0 = r0 | r6
            r11.restoreStatus = r0     // Catch: java.lang.Throwable -> L1e0
        Lc4:
            com.android.launcher3.widget.PendingAddWidgetInfo r0 = new com.android.launcher3.widget.PendingAddWidgetInfo     // Catch: java.lang.Throwable -> L1e0
            r0.<init>(r4)     // Catch: java.lang.Throwable -> L1e0
            int r6 = r11.spanX     // Catch: java.lang.Throwable -> L1e0
            r0.spanX = r6     // Catch: java.lang.Throwable -> L1e0
            int r6 = r11.spanY     // Catch: java.lang.Throwable -> L1e0
            r0.spanY = r6     // Catch: java.lang.Throwable -> L1e0
            int r6 = r11.minSpanX     // Catch: java.lang.Throwable -> L1e0
            r0.minSpanX = r6     // Catch: java.lang.Throwable -> L1e0
            int r6 = r11.minSpanY     // Catch: java.lang.Throwable -> L1e0
            r0.minSpanY = r6     // Catch: java.lang.Throwable -> L1e0
            android.os.Bundle r0 = com.android.launcher3.widget.WidgetHostViewLoader.getDefaultOptionsForWidget(r10, r0)     // Catch: java.lang.Throwable -> L1e0
            r6 = 32
            boolean r6 = r11.hasRestoreFlag(r6)     // Catch: java.lang.Throwable -> L1e0
            if (r6 == 0) goto Lf1
            android.content.Intent r8 = r11.bindOptions     // Catch: java.lang.Throwable -> L1e0
            if (r8 == 0) goto Lf1
            android.os.Bundle r8 = r8.getExtras()     // Catch: java.lang.Throwable -> L1e0
            r8.putAll(r0)     // Catch: java.lang.Throwable -> L1e0
            r0 = r8
        Lf1:
            com.android.launcher3.widget.WidgetManagerHelper r8 = r10.mAppWidgetManager     // Catch: java.lang.Throwable -> L1e0
            int r9 = r11.appWidgetId     // Catch: java.lang.Throwable -> L1e0
            boolean r0 = r8.bindAppWidgetIdIfAllowed(r9, r4, r0)     // Catch: java.lang.Throwable -> L1e0
            if (r0 != 0) goto L103
            boolean r7 = r11.hasRestoreFlag(r7)     // Catch: java.lang.Throwable -> L1e0
            if (r7 == 0) goto L103
            r0 = 1
            goto L117
        L103:
            r11.bindOptions = r3     // Catch: java.lang.Throwable -> L1e0
            int r7 = r11.restoreStatus     // Catch: java.lang.Throwable -> L1e0
            r7 = r7 & (-33)
            r11.restoreStatus = r7     // Catch: java.lang.Throwable -> L1e0
            if (r0 == 0) goto L116
            android.content.ComponentName r0 = r4.configure     // Catch: java.lang.Throwable -> L1e0
            if (r0 == 0) goto L113
            if (r6 == 0) goto L114
        L113:
            r5 = 0
        L114:
            r11.restoreStatus = r5     // Catch: java.lang.Throwable -> L1e0
        L116:
            r0 = 0
        L117:
            com.android.launcher3.model.ModelWriter r5 = r10.mModelWriter     // Catch: java.lang.Throwable -> L1e0
            r5.updateItemInDatabase(r11)     // Catch: java.lang.Throwable -> L1e0
            goto L14f
        L11d:
            boolean r0 = r11.hasRestoreFlag(r5)     // Catch: java.lang.Throwable -> L1e0
            if (r0 == 0) goto L12c
            android.content.ComponentName r0 = r4.configure     // Catch: java.lang.Throwable -> L1e0
            if (r0 != 0) goto L12c
            r11.restoreStatus = r2     // Catch: java.lang.Throwable -> L1e0
        L129:
            com.android.launcher3.model.ModelWriter r0 = r10.mModelWriter     // Catch: java.lang.Throwable -> L1e0
            goto L14b
        L12c:
            boolean r0 = r11.hasRestoreFlag(r5)     // Catch: java.lang.Throwable -> L1e0
            if (r0 == 0) goto L14e
            android.content.ComponentName r0 = r4.configure     // Catch: java.lang.Throwable -> L1e0
            if (r0 == 0) goto L14e
            com.android.launcher3.widget.WidgetManagerHelper r0 = r10.mAppWidgetManager     // Catch: java.lang.Throwable -> L1e0
            int r5 = r11.appWidgetId     // Catch: java.lang.Throwable -> L1e0
            android.appwidget.AppWidgetManager r0 = r0.mAppWidgetManager     // Catch: java.lang.Throwable -> L1e0
            android.os.Bundle r0 = r0.getAppWidgetOptions(r5)     // Catch: java.lang.Throwable -> L1e0
            java.lang.String r5 = "appWidgetRestoreCompleted"
            boolean r0 = r0.getBoolean(r5)     // Catch: java.lang.Throwable -> L1e0
            if (r0 == 0) goto L14e
            r11.restoreStatus = r2     // Catch: java.lang.Throwable -> L1e0
            goto L129
        L14b:
            r0.updateItemInDatabase(r11)     // Catch: java.lang.Throwable -> L1e0
        L14e:
            r0 = 0
        L14f:
            int r5 = r11.restoreStatus     // Catch: java.lang.Throwable -> L1e0
            if (r5 != 0) goto L1af
            if (r4 != 0) goto L17a
            java.lang.String r0 = "Launcher"
            java.lang.StringBuilder r1 = new java.lang.StringBuilder     // Catch: java.lang.Throwable -> L1e0
            r1.<init>()     // Catch: java.lang.Throwable -> L1e0
            java.lang.String r2 = "Removing invalid widget: id="
            r1.append(r2)     // Catch: java.lang.Throwable -> L1e0
            int r2 = r11.appWidgetId     // Catch: java.lang.Throwable -> L1e0
            r1.append(r2)     // Catch: java.lang.Throwable -> L1e0
            java.lang.String r1 = r1.toString()     // Catch: java.lang.Throwable -> L1e0
            com.android.launcher3.logging.FileLog.e(r0, r1)     // Catch: java.lang.Throwable -> L1e0
            com.android.launcher3.model.ModelWriter r0 = r10.mModelWriter     // Catch: java.lang.Throwable -> L1e0
            com.android.launcher3.LauncherAppWidgetHost r1 = r10.mAppWidgetHost     // Catch: java.lang.Throwable -> L1e0
            r0.deleteWidgetInfo(r11, r1)     // Catch: java.lang.Throwable -> L1e0
            com.android.launcher3.util.TraceHelper r11 = com.android.launcher3.util.TraceHelper.INSTANCE
            android.os.Trace.endSection()
            return r3
        L17a:
            int r2 = r4.minSpanX     // Catch: java.lang.Throwable -> L1e0
            r11.minSpanX = r2     // Catch: java.lang.Throwable -> L1e0
            int r2 = r4.minSpanY     // Catch: java.lang.Throwable -> L1e0
            r11.minSpanY = r2     // Catch: java.lang.Throwable -> L1e0
            com.android.launcher3.DeviceProfile r2 = r10.mDeviceProfile     // Catch: java.lang.Throwable -> L1e0
            com.android.launcher3.InvariantDeviceProfile r2 = r2.inv     // Catch: java.lang.Throwable -> L1e0
            int r3 = r2.numColumns     // Catch: java.lang.Throwable -> L1e0
            int r2 = r2.numRows     // Catch: java.lang.Throwable -> L1e0
            int r5 = r11.cellX     // Catch: java.lang.Throwable -> L1e0
            if (r3 <= r5) goto L1a6
            int r6 = r11.cellY     // Catch: java.lang.Throwable -> L1e0
            if (r2 <= r6) goto L1a6
            int r6 = r11.spanX     // Catch: java.lang.Throwable -> L1e0
            int r3 = r3 - r5
            int r3 = java.lang.Math.min(r6, r3)     // Catch: java.lang.Throwable -> L1e0
            r11.spanX = r3     // Catch: java.lang.Throwable -> L1e0
            int r3 = r11.spanY     // Catch: java.lang.Throwable -> L1e0
            int r5 = r11.cellY     // Catch: java.lang.Throwable -> L1e0
            int r2 = r2 - r5
            int r2 = java.lang.Math.min(r3, r2)     // Catch: java.lang.Throwable -> L1e0
            r11.spanY = r2     // Catch: java.lang.Throwable -> L1e0
        L1a6:
            com.android.launcher3.LauncherAppWidgetHost r2 = r10.mAppWidgetHost     // Catch: java.lang.Throwable -> L1e0
            int r3 = r11.appWidgetId     // Catch: java.lang.Throwable -> L1e0
            android.appwidget.AppWidgetHostView r2 = r2.createView(r10, r3, r4)     // Catch: java.lang.Throwable -> L1e0
            goto L1b7
        L1af:
            com.android.launcher3.widget.PendingAppWidgetHostView r3 = new com.android.launcher3.widget.PendingAppWidgetHostView     // Catch: java.lang.Throwable -> L1e0
            com.android.launcher3.icons.IconCache r4 = r10.mIconCache     // Catch: java.lang.Throwable -> L1e0
            r3.<init>(r10, r11, r4, r2)     // Catch: java.lang.Throwable -> L1e0
            r2 = r3
        L1b7:
            r2.setTag(r11)     // Catch: java.lang.Throwable -> L1e0
            r11.onBindAppWidget(r10, r2)     // Catch: java.lang.Throwable -> L1e0
            r2.setFocusable(r1)     // Catch: java.lang.Throwable -> L1e0
            com.android.launcher3.keyboard.ViewGroupFocusHelper r3 = r10.mFocusHandler     // Catch: java.lang.Throwable -> L1e0
            r2.setOnFocusChangeListener(r3)     // Catch: java.lang.Throwable -> L1e0
            int r3 = r11.container     // Catch: java.lang.Throwable -> L1e0
            r4 = -103(0xffffffffffffff99, float:NaN)
            if (r3 != r4) goto L1d5
            boolean r3 = r2 instanceof com.microsoft.launcher.view.LauncherPrivateWidgetHostView     // Catch: java.lang.Throwable -> L1e0
            if (r3 == 0) goto L1d5
            r3 = r2
            com.microsoft.launcher.view.LauncherPrivateWidgetHostView r3 = (com.microsoft.launcher.view.LauncherPrivateWidgetHostView) r3     // Catch: java.lang.Throwable -> L1e0
            r3.setFollowTheme(r1)     // Catch: java.lang.Throwable -> L1e0
        L1d5:
            if (r0 == 0) goto L1da
            r10.addPendingBindAppWidget(r11)     // Catch: java.lang.Throwable -> L1e0
        L1da:
            com.android.launcher3.util.TraceHelper r11 = com.android.launcher3.util.TraceHelper.INSTANCE
            android.os.Trace.endSection()
            return r2
        L1e0:
            r11 = move-exception
            com.android.launcher3.util.TraceHelper r0 = com.android.launcher3.util.TraceHelper.INSTANCE
            android.os.Trace.endSection()
            throw r11
    }

    public final android.view.View inflateFeaturePage(com.microsoft.launcher.featurepage.FeaturePageInfo r14) {
            r13 = this;
            b.a.m.r2.c r0 = r13.mFeaturePageHost
            r1 = 0
            if (r0 != 0) goto L6
            return r1
        L6:
            com.android.launcher3.util.TraceHelper r0 = com.android.launcher3.util.TraceHelper.INSTANCE
            java.lang.String r0 = "BIND_FEATURE_PAGE"
            com.android.launcher3.util.TraceHelper.beginSection(r0)
            r2 = 2
            boolean r2 = r14.hasRestoreFlag(r2)
            if (r2 == 0) goto L16
            r2 = r1
            goto L1c
        L16:
            int r2 = r14.featurePageId
            com.microsoft.launcher.featurepage.FeaturePageProviderInfo r2 = b.a.m.r2.g.e(r13, r2)
        L1c:
            int r3 = r14.restoreStatus
            if (r3 != 0) goto L9e
            if (r2 != 0) goto L3c
            java.lang.String r0 = "Removing invalid feature page: id="
            java.lang.StringBuilder r0 = b.c.e.c.a.G(r0)
            int r2 = r14.featurePageId
            r0.append(r2)
            java.lang.String r0 = r0.toString()
            java.lang.String r2 = "Launcher"
            com.android.launcher3.logging.FileLog.e(r2, r0)
            b.a.m.r2.c r0 = r13.mFeaturePageHost
            r0.k(r14)
            return r1
        L3c:
            int r1 = r2.f9587k
            r14.spanX = r1
            int r1 = r2.f9588l
            r14.spanY = r1
            b.a.m.r2.c r1 = r13.mFeaturePageHost
            int r9 = r14.featurePageId
            android.util.SparseArray<com.microsoft.launcher.featurepage.FeaturePageHostView> r3 = r1.f4114b
            java.lang.Object r3 = r3.get(r9)
            if (r3 == 0) goto L55
            android.util.SparseArray<com.microsoft.launcher.featurepage.FeaturePageHostView> r3 = r1.f4114b
            r3.remove(r9)
        L55:
            com.microsoft.launcher.featurepage.FeaturePageHostView r10 = new com.microsoft.launcher.featurepage.FeaturePageHostView
            r10.<init>(r13)
            r3 = r13
            com.microsoft.launcher.LauncherActivity r3 = (com.microsoft.launcher.LauncherActivity) r3
            b.a.m.z0<com.microsoft.launcher.LauncherActivity> r3 = r3.f9112p
            b.a.m.i3.t3 r11 = r3.f()
            b.a.m.r2.c$c r12 = new b.a.m.r2.c$c
            r8 = 0
            r3 = r12
            r4 = r13
            r5 = r11
            r6 = r2
            r7 = r10
            r3.<init>(r4, r5, r6, r7, r8)
            b.a.m.i3.z4.a r3 = r11.f2949b
            r3.a(r12)
            r10.setFeaturePage(r9, r2)
            android.util.SparseArray<com.microsoft.launcher.featurepage.FeaturePageHostView> r1 = r1.f4114b
            r1.put(r9, r10)
            r10.setTag(r14)
            r1 = 1
            r10.setFocusable(r1)
            com.android.launcher3.keyboard.ViewGroupFocusHelper r1 = r13.mFocusHandler
            r10.setOnFocusChangeListener(r1)
            java.lang.StringBuilder r1 = new java.lang.StringBuilder
            r1.<init>()
            java.lang.String r2 = "id="
            r1.append(r2)
            int r14 = r14.featurePageId
            r1.append(r14)
            java.lang.String r14 = r1.toString()
            com.android.launcher3.util.TraceHelper.endSection(r0, r14)
            return r10
        L9e:
            return r1
    }

    public final void initDeviceProfile() {
            r5 = this;
            com.android.launcher3.LauncherAppState r0 = com.android.launcher3.LauncherAppState.getInstance(r5)
            b.a.m.u3.r r1 = b.a.m.u3.r.a(r5)
            java.lang.String r2 = "RefreshIDP info, Posture: "
            java.lang.StringBuilder r2 = b.c.e.c.a.G(r2)
            java.lang.String r3 = r1.f
            r2.append(r3)
            java.lang.String r3 = "getDeviceProfile orientation: "
            r2.append(r3)
            android.content.Context r3 = r5.getApplicationContext()
            android.content.res.Resources r3 = r3.getResources()
            android.content.res.Configuration r3 = r3.getConfiguration()
            int r3 = r3.orientation
            r4 = 2
            if (r3 != r4) goto L2c
            java.lang.String r3 = "landscapeProfile"
            goto L2e
        L2c:
            java.lang.String r3 = "portraitProfile"
        L2e:
            r2.append(r3)
            java.lang.String r2 = r2.toString()
            java.lang.String r3 = "IDP"
            android.util.Log.w(r3, r2)
            com.android.launcher3.LauncherAppState$InvariantDeviceProfileContainer r0 = r0.mInvariantDeviceProfile
            r0.refreshCurrentIDP(r5, r1)
            com.android.launcher3.InvariantDeviceProfile r0 = com.android.launcher3.LauncherAppState.getIDP(r5)
            r5.initDeviceProfile(r0)
            return
    }

    public final void initDeviceProfile(com.android.launcher3.InvariantDeviceProfile r3) {
            r2 = this;
            com.android.launcher3.DeviceBehavior r0 = r3.mBehavior
            com.android.launcher3.DeviceProfile r3 = r0.getDeviceProfile(r2, r3)
            r2.mDeviceProfile = r3
            boolean r3 = r3.isVerticalBarLayout()
            if (r3 == 0) goto L13
            com.android.launcher3.DeviceProfile r3 = r2.mDeviceProfile
            r3.updateIsSeascape(r2)
        L13:
            com.android.launcher3.LauncherModel r3 = r2.mModel
            com.android.launcher3.DeviceProfile r0 = r2.mDeviceProfile
            r1 = 1
            com.android.launcher3.model.ModelWriter r3 = r3.getWriter(r0, r1)
            r2.mModelWriter = r3
            return
    }

    @Override // com.android.launcher3.BaseActivity, com.android.launcher3.views.ActivityContext
    public void invalidateParent(com.android.launcher3.model.data.ItemInfo r4) {
            r3 = this;
            int r0 = r4.container
            if (r0 < 0) goto L33
            com.android.launcher3.Workspace r1 = r3.mWorkspace
            android.view.View r0 = r1.getHomescreenIconByItemId(r0)
            boolean r1 = r0 instanceof com.android.launcher3.folder.FolderIcon
            if (r1 == 0) goto L33
            java.lang.Object r1 = r0.getTag()
            boolean r1 = r1 instanceof com.android.launcher3.model.data.FolderInfo
            if (r1 == 0) goto L33
            com.android.launcher3.folder.FolderGridOrganizer r1 = new com.android.launcher3.folder.FolderGridOrganizer
            com.android.launcher3.DeviceProfile r2 = r3.mDeviceProfile
            com.android.launcher3.InvariantDeviceProfile r2 = r2.inv
            r1.<init>(r2)
            java.lang.Object r2 = r0.getTag()
            com.android.launcher3.model.data.FolderInfo r2 = (com.android.launcher3.model.data.FolderInfo) r2
            r1.setFolderInfo(r2)
            int r4 = r4.rank
            boolean r4 = r1.isItemInPreview(r4)
            if (r4 == 0) goto L33
            r0.invalidate()
        L33:
            return
    }

    public boolean isAllAppsVisible() {
            r1 = this;
            com.android.launcher3.LauncherState r0 = com.android.launcher3.LauncherState.ALL_APPS
            boolean r0 = r1.isInState(r0)
            return r0
    }

    public boolean isDualScreenAppDrawerOrSearchActive() {
            r1 = this;
            com.android.launcher3.allapps.AppDrawerBehavior r0 = r1.mAppDrawerBehavior
            if (r0 == 0) goto La
            boolean r0 = r0.isActiveInDualScreen(r1)
            if (r0 != 0) goto L14
        La:
            com.android.launcher3.bingsearch.BingSearchBehavior r0 = r1.mBingSearchBehavior
            if (r0 == 0) goto L16
            boolean r0 = r0.isActiveInDualScreen(r1)
            if (r0 == 0) goto L16
        L14:
            r0 = 1
            goto L17
        L16:
            r0 = 0
        L17:
            return r0
    }

    public boolean isDuplicatedConfigChange(int r1) {
            r0 = this;
            r1 = 0
            return r1
    }

    public boolean isFolderHorizontalScroll() {
            r1 = this;
            boolean r0 = b.a.m.c4.d5.a
            return r0
    }

    public boolean isFolderModePopup() {
            r1 = this;
            r0 = 0
            return r0
    }

    public boolean isHasMicrosoftFolder() {
            r1 = this;
            r0 = 0
            return r0
    }

    public boolean isHotseatLayout(android.view.View r3) {
            r2 = this;
            com.android.launcher3.Hotseat r0 = r2.mHotseat
            if (r0 == 0) goto L12
            if (r3 == 0) goto L12
            boolean r1 = r3 instanceof com.android.launcher3.CellLayout
            if (r1 == 0) goto L12
            com.android.launcher3.CellLayout r0 = r0.getLayout()
            if (r3 != r0) goto L12
            r3 = 1
            goto L13
        L12:
            r3 = 0
        L13:
            return r3
    }

    public boolean isMultiSelectionMode() {
            r1 = this;
            b.a.m.h3.v r0 = r1.mCurrentMultiSelectable
            if (r0 == 0) goto L6
            r0 = 1
            goto L7
        L6:
            r0 = 0
        L7:
            return r0
    }

    public boolean isOverlayAnimating() {
            r1 = this;
            r0 = 0
            return r0
    }

    public boolean isOverlayClosed() {
            r2 = this;
            boolean r0 = r2.isOverlayOpen()
            if (r0 != 0) goto L1d
            com.android.launcher3.dragndrop.DragLayer r0 = r2.mDragLayer
            float r0 = r0.getTranslationX()
            r1 = 0
            int r0 = (r0 > r1 ? 1 : (r0 == r1 ? 0 : -1))
            if (r0 != 0) goto L1d
            com.android.launcher3.dragndrop.DragLayer r0 = r2.mDragLayer
            float r0 = r0.getTranslationY()
            int r0 = (r0 > r1 ? 1 : (r0 == r1 ? 0 : -1))
            if (r0 != 0) goto L1d
            r0 = 1
            goto L1e
        L1d:
            r0 = 0
        L1e:
            return r0
    }

    public boolean isOverlayClosing() {
            r1 = this;
            r0 = 0
            return r0
    }

    public boolean isOverlayOpen() {
            r1 = this;
            com.android.launcher3.Workspace r0 = r1.mWorkspace
            if (r0 == 0) goto La
            boolean r0 = r0.mOverlayShown
            if (r0 == 0) goto La
            r0 = 1
            goto Lb
        La:
            r0 = 0
        Lb:
            return r0
    }

    public boolean isOverlayScrolling() {
            r1 = this;
            r0 = 0
            return r0
    }

    public void notifyBindAppWidgetsCompleted() {
            r0 = this;
            return
    }

    @Override // android.app.Activity, android.view.Window.Callback
    public void onAttachedToWindow() {
            r1 = this;
            super.onAttachedToWindow()
            com.android.systemui.plugins.shared.LauncherOverlayManager r0 = r1.mOverlayManager
            r0.onAttachedToWindow()
            return
    }

    @Override // android.app.Activity
    public void onBackPressed() {
            r6 = this;
            boolean r0 = r6.finishAutoCancelActionMode()
            if (r0 == 0) goto L7
            return
        L7:
            com.android.launcher3.dragndrop.DragController r0 = r6.mDragController
            boolean r0 = r0.isDragging()
            if (r0 == 0) goto L15
            com.android.launcher3.dragndrop.DragController r0 = r6.mDragController
            r0.cancelDrag()
            return
        L15:
            com.android.launcher3.allapps.AppDrawerBehavior r0 = r6.mAppDrawerBehavior
            r1 = 0
            r0.isTouchOnOtherScreen = r1
            com.android.launcher3.bingsearch.BingSearchBehavior r0 = r6.mBingSearchBehavior
            r0.isTouchOnOtherScreen = r1
            r0 = 131071(0x1ffff, float:1.8367E-40)
            com.android.launcher3.AbstractFloatingView r0 = com.android.launcher3.AbstractFloatingView.getOpenView(r6, r0)
            if (r0 == 0) goto L2f
            boolean r0 = r0.onBackPressed()
            if (r0 == 0) goto L2f
            goto La8
        L2f:
            com.android.launcher3.OverlayPanel r0 = r6.mOverlayPanel
            boolean r0 = r0.closeViewInternal()
            if (r0 == 0) goto L39
            goto La8
        L39:
            com.android.launcher3.LauncherState r0 = com.android.launcher3.LauncherState.OVERVIEW
            boolean r0 = r6.isInState(r0)
            if (r0 == 0) goto L49
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r0 = r6.mStateManager
            com.android.launcher3.LauncherState r1 = com.android.launcher3.LauncherState.NORMAL
            r0.goToState(r1)
            goto La8
        L49:
            com.android.launcher3.LauncherState r0 = com.android.launcher3.LauncherState.NORMAL
            boolean r2 = r6.isInState(r0)
            r3 = 1
            if (r2 != 0) goto L88
            com.android.launcher3.allapps.AllAppsContainerView r2 = r6.mAppsView
            if (r2 == 0) goto L88
            r2.dismissPopupMenu()
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r0 = r6.mStateManager
            STATE_TYPE extends com.android.launcher3.statemanager.BaseState<STATE_TYPE> r2 = r0.mLastStableState
            r4 = r2
            com.android.launcher3.LauncherState r4 = (com.android.launcher3.LauncherState) r4
            STATE_TYPE extends com.android.launcher3.statemanager.BaseState<STATE_TYPE> r0 = r0.mState
            com.android.launcher3.LauncherState r5 = com.android.launcher3.LauncherState.ALL_APPS
            if (r0 != r5) goto L6f
            if (r2 == r5) goto L6f
            com.android.launcher3.tasklayout.TaskLayoutHelper r0 = r6.getTaskLayoutHelper()
            r0.updateOccupiedStatus(r1, r1)
        L6f:
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r0 = r6.mStateManager
            STATE_TYPE extends com.android.launcher3.statemanager.BaseState<STATE_TYPE> r2 = r0.mState
            com.android.launcher3.LauncherState r5 = com.android.launcher3.LauncherState.SEARCH_RESULT
            if (r2 != r5) goto L82
            STATE_TYPE extends com.android.launcher3.statemanager.BaseState<STATE_TYPE> r0 = r0.mLastStableState
            if (r0 == r5) goto L82
            com.android.launcher3.tasklayout.TaskLayoutHelper r0 = r6.getTaskLayoutHelper()
            r0.updateOccupiedStatus(r3, r1)
        L82:
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r0 = r6.mStateManager
            r0.goToState(r4)
            goto La8
        L88:
            boolean r1 = b.a.m.m4.o1.a(r6)
            if (r1 == 0) goto L94
            java.util.List<com.microsoft.launcher.account.ConnectedAppReminder> r0 = b.a.m.p1.e.a
            r6.moveTaskToBack(r3)
            goto La8
        L94:
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r1 = r6.mStateManager
            STATE_TYPE extends com.android.launcher3.statemanager.BaseState<STATE_TYPE> r1 = r1.mState
            com.android.launcher3.LauncherState r1 = (com.android.launcher3.LauncherState) r1
            java.util.Objects.requireNonNull(r1)
            if (r1 == r0) goto La8
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r0 = r6.mStateManager
            STATE_TYPE extends com.android.launcher3.statemanager.BaseState<STATE_TYPE> r1 = r0.mLastStableState
            com.android.launcher3.LauncherState r1 = (com.android.launcher3.LauncherState) r1
            r0.goToState(r1)
        La8:
            return
    }

    public void onBindMicrosoftFolderItems(java.util.List<com.android.launcher3.model.data.WorkspaceItemInfo> r1) {
            r0 = this;
            return
    }

    @Override // com.android.launcher3.BaseDraggingActivity, android.app.Activity, android.content.ComponentCallbacks
    public void onConfigurationChanged(android.content.res.Configuration r11) {
            r10 = this;
            if (r11 != 0) goto L5
            r0 = 2048(0x800, float:2.87E-42)
            goto Lb
        L5:
            android.content.res.Configuration r0 = r10.mOldConfig
            int r0 = r11.diff(r0)
        Lb:
            r1 = r0 & 3200(0xc80, float:4.484E-42)
            if (r1 == 0) goto L14e
            boolean r0 = r10.isDuplicatedConfigChange(r0)
            if (r0 != 0) goto L14e
            com.android.launcher3.tasklayout.TaskLayoutHelper r0 = r10.mTaskLayoutHelper
            android.util.SparseIntArray r0 = r0.mOccuipedStatus
            r0.clear()
            r0 = 1
            r10.mIsUpdateConfig = r0
            r1 = 0
            r10.mUserEventDispatcher = r1
            com.android.launcher3.LauncherState r2 = com.android.launcher3.LauncherState.OVERVIEW
            boolean r2 = r10.isInState(r2)
            if (r2 == 0) goto L2c
            r10.mIsInOverviewWhenConfigChange = r0
        L2c:
            boolean r2 = r10.mIsInOverviewWhenConfigChange
            r3 = 0
            if (r2 != 0) goto L47
            com.android.launcher3.LauncherState r2 = com.android.launcher3.LauncherState.SEARCH_RESULT
            boolean r2 = r10.isInState(r2)
            if (r2 == 0) goto L4e
            b.a.m.s2.g r2 = com.microsoft.launcher.features.FeatureManager.b()
            com.microsoft.launcher.codegen.launcher3.features.Feature r4 = com.microsoft.launcher.codegen.launcher3.features.Feature.ENABLE_SEARCH_APP_DRAG_AND_DROP
            com.microsoft.launcher.features.FeatureManager r2 = (com.microsoft.launcher.features.FeatureManager) r2
            boolean r2 = r2.d(r4)
            if (r2 != 0) goto L4e
        L47:
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r2 = r10.mStateManager
            com.android.launcher3.LauncherState r4 = com.android.launcher3.LauncherState.NORMAL
            r2.goToState(r4, r3)
        L4e:
            r10.initDeviceProfile()
            com.android.launcher3.allapps.AllAppsContainerView r2 = r10.mAppsView
            if (r2 == 0) goto L58
            r2.getPageCountBeforeRotate()
        L58:
            r10.reCreateAppDrawerBehavior()
            r10.dispatchDeviceProfileChanged()
            com.android.launcher3.allapps.AllAppsContainerView r2 = r10.mAppsView
            if (r2 == 0) goto L65
            r2.setPageCountBeforeRotate()
        L65:
            r2 = 24593(0x6011, float:3.4462E-41)
            com.android.launcher3.AbstractFloatingView r2 = com.android.launcher3.AbstractFloatingView.getOpenView(r10, r2)
            boolean r4 = r2 instanceof com.android.launcher3.OverlayAwareFloatable
            if (r4 == 0) goto L74
            com.android.launcher3.OverlayAwareFloatable r2 = (com.android.launcher3.OverlayAwareFloatable) r2
            r2.checkFolderStatusWhenConfigChange(r10)
        L74:
            com.android.launcher3.DeviceProfile r2 = r10.mDeviceProfile
            com.android.launcher3.InvariantDeviceProfile r2 = r2.inv
            com.android.launcher3.DeviceBehavior r2 = r2.mBehavior
            if (r2 == 0) goto L99
            b.a.m.x2.n0 r2 = r10.mHotseatLayoutBehavior
            if (r2 == 0) goto L88
            r2.g()
            b.a.m.x2.n0 r2 = r10.mHotseatLayoutBehavior
            r2.v()
        L88:
            com.android.launcher3.DeviceProfile r2 = r10.mDeviceProfile
            com.android.launcher3.InvariantDeviceProfile r4 = r2.inv
            com.android.launcher3.DeviceBehavior r4 = r4.mBehavior
            b.a.m.x2.n0 r2 = r4.getHotseatLayoutBehavior(r2)
            r10.mHotseatLayoutBehavior = r2
            com.android.launcher3.Hotseat r4 = r10.mHotseat
            r2.F(r4)
        L99:
            r10.reCreateBingSearchBehavior()
            r2 = 16
            com.android.launcher3.AbstractFloatingView r2 = com.android.launcher3.AbstractFloatingView.getOpenView(r10, r2)
            if (r2 == 0) goto Lb6
            com.android.launcher3.DeviceProfile r4 = r10.mDeviceProfile
            com.android.launcher3.InvariantDeviceProfile r5 = r4.inv
            com.android.launcher3.DeviceBehavior r5 = r5.mBehavior
            if (r5 != 0) goto Lad
            goto Lb6
        Lad:
            com.android.launcher3.widget.WidgetsSheetBehavior r4 = r5.getWidgetsSheetBehavior(r4)
            com.android.launcher3.widget.WidgetsFullSheet r2 = (com.android.launcher3.widget.WidgetsFullSheet) r2
            r4.setupWidgetsFullSheet(r2, r1)
        Lb6:
            r10.reapplyUi()
            com.android.launcher3.dragndrop.DragLayer r2 = r10.mDragLayer
            r2.recreateControllers()
            com.android.launcher3.AppWidgetResizeFrame.sCellSize = r1
            com.android.launcher3.LauncherModel r1 = r10.mModel
            if (r1 == 0) goto L135
            com.android.launcher3.InvariantDeviceProfile r1 = com.android.launcher3.LauncherAppState.getIDP(r10)
            com.android.launcher3.DeviceProfile r2 = r10.mDeviceProfile
            b.a.m.w2.h r4 = b.a.m.n2.u.b()
            b.a.m.q0 r4 = (b.a.m.q0) r4
            java.util.Objects.requireNonNull(r4)
            boolean r4 = com.android.launcher3.config.FeatureFlags.IS_E_OS
            if (r4 == 0) goto Ld8
            goto L135
        Ld8:
            if (r2 == 0) goto Le2
            boolean r4 = r2.isVerticalBarLayout()
            if (r4 == 0) goto Le2
            r4 = 1
            goto Le3
        Le2:
            r4 = 0
        Le3:
            if (r2 == 0) goto Lec
            boolean r2 = r2.isSeascape()
            if (r2 == 0) goto Lec
            r3 = 1
        Lec:
            int r2 = r1.numHotseatIcons
            int r1 = r1.numHotseatRows
            com.android.launcher3.model.BgDataModel r5 = com.android.launcher3.LauncherModel.sBgDataModel
            monitor-enter(r5)
            java.util.ArrayList<com.android.launcher3.model.data.ItemInfo> r6 = r5.workspaceItems     // Catch: java.lang.Throwable -> L132
            java.util.Iterator r6 = r6.iterator()     // Catch: java.lang.Throwable -> L132
        Lf9:
            boolean r7 = r6.hasNext()     // Catch: java.lang.Throwable -> L132
            if (r7 == 0) goto L130
            java.lang.Object r7 = r6.next()     // Catch: java.lang.Throwable -> L132
            com.android.launcher3.model.data.ItemInfo r7 = (com.android.launcher3.model.data.ItemInfo) r7     // Catch: java.lang.Throwable -> L132
            int r8 = r7.container     // Catch: java.lang.Throwable -> L132
            r9 = -101(0xffffffffffffff9b, float:NaN)
            if (r8 != r9) goto Lf9
            int r8 = r7.itemType     // Catch: java.lang.Throwable -> L132
            r9 = 2
            if (r8 != r9) goto Lf9
            if (r4 == 0) goto L126
            if (r3 == 0) goto L11d
            int r8 = r1 + (-1)
            int r9 = r7.screenId     // Catch: java.lang.Throwable -> L132
            int r9 = r9 / r2
            int r8 = r8 - r9
            r7.cellX = r8     // Catch: java.lang.Throwable -> L132
            goto L122
        L11d:
            int r8 = r7.screenId     // Catch: java.lang.Throwable -> L132
            int r8 = r8 / r2
            r7.cellX = r8     // Catch: java.lang.Throwable -> L132
        L122:
            int r8 = r7.screenId     // Catch: java.lang.Throwable -> L132
            int r8 = r8 % r2
            goto L12d
        L126:
            int r8 = r7.screenId     // Catch: java.lang.Throwable -> L132
            int r9 = r8 % r2
            r7.cellX = r9     // Catch: java.lang.Throwable -> L132
            int r8 = r8 / r2
        L12d:
            r7.cellY = r8     // Catch: java.lang.Throwable -> L132
            goto Lf9
        L130:
            monitor-exit(r5)     // Catch: java.lang.Throwable -> L132
            goto L135
        L132:
            r11 = move-exception
            monitor-exit(r5)     // Catch: java.lang.Throwable -> L132
            throw r11
        L135:
            r10.rebindModel()
            com.android.launcher3.OverlayPanel r1 = r10.mOverlayPanel
            r1.onConfigurationChanged()
            android.graphics.Rect r1 = com.android.launcher3.folder.Folder.sTempRect
            com.android.launcher3.AbstractFloatingView r0 = com.android.launcher3.AbstractFloatingView.getOpenView(r10, r0)
            com.android.launcher3.folder.Folder r0 = (com.android.launcher3.folder.Folder) r0
            if (r0 == 0) goto L14e
            boolean r1 = r0.mItemsInvalidated
            if (r1 == 0) goto L14e
            r0.getIconsInReadingOrder()
        L14e:
            if (r11 != 0) goto L151
            return
        L151:
            android.content.res.Configuration r0 = r10.mOldConfig
            r0.setTo(r11)
            super.onConfigurationChanged(r11)
            return
    }

    @Override // android.app.Activity, android.view.Window.Callback
    public void onDetachedFromWindow() {
            r1 = this;
            super.onDetachedFromWindow()
            com.android.systemui.plugins.shared.LauncherOverlayManager r0 = r1.mOverlayManager
            r0.onDetachedFromWindow()
            r1.closeContextMenu()
            return
    }

    @Override // android.app.Activity
    public void onEnterAnimationComplete() {
            r4 = this;
            super.onEnterAnimationComplete()
            com.android.launcher3.allapps.AllAppsTransitionController r0 = r4.mAllAppsController
            r1 = 0
            if (r0 == 0) goto L1d
            float r2 = r0.mProgress
            r3 = 0
            int r2 = java.lang.Float.compare(r2, r3)
            if (r2 != 0) goto L13
            r2 = 1
            goto L14
        L13:
            r2 = 0
        L14:
            if (r2 == 0) goto L1d
            com.android.launcher3.allapps.AllAppsContainerView r0 = r0.mAppsView
            if (r0 == 0) goto L1d
            r0.highlightWorkTabIfNecessary()
        L1d:
            com.android.launcher3.states.RotationHelper r0 = r4.mRotationHelper
            if (r0 == 0) goto L2a
            int r2 = r0.mCurrentTransitionRequest
            if (r2 == 0) goto L2a
            r0.mCurrentTransitionRequest = r1
            r0.notifyChange()
        L2a:
            r0 = 4096(0x1000, float:5.74E-42)
            int r2 = com.android.launcher3.AbstractFloatingView.a
            com.android.launcher3.views.BaseDragLayer r2 = r4.getDragLayer()
            if (r2 != 0) goto L35
            goto L38
        L35:
            com.android.launcher3.AbstractFloatingView.closeAllOpenViews(r2, r1, r0)
        L38:
            return
    }

    @Override // com.android.launcher3.BaseDraggingActivity
    @android.annotation.TargetApi(23)
    public boolean onErrorStartingShortcut(android.content.Intent r5, com.android.launcher3.model.data.ItemInfo r6) {
            r4 = this;
            android.content.ComponentName r0 = r5.getComponent()
            if (r0 != 0) goto L2f
            java.lang.String r0 = r5.getAction()
            java.lang.String r1 = "android.intent.action.CALL"
            boolean r0 = r1.equals(r0)
            if (r0 == 0) goto L2f
            java.lang.String r0 = "android.permission.CALL_PHONE"
            int r1 = r4.checkSelfPermission(r0)
            if (r1 == 0) goto L2f
            com.android.launcher3.util.PendingRequestArgs r1 = new com.android.launcher3.util.PendingRequestArgs
            r2 = 14
            r3 = 1
            r1.<init>(r2, r3, r5)
            r1.copyFrom(r6)
            r4.mPendingRequestArgs = r1
            java.lang.String[] r5 = new java.lang.String[]{r0}
            r4.requestPermissions(r5, r2)
            return r3
        L2f:
            r5 = 0
            return r5
    }

    @Override // android.app.Activity
    public boolean onKeyShortcut(int r6, android.view.KeyEvent r7) {
            r5 = this;
            r0 = 4096(0x1000, float:5.74E-42)
            boolean r0 = r7.hasModifiers(r0)
            if (r0 == 0) goto L75
            r0 = 29
            r1 = 1
            if (r6 == r0) goto L65
            r0 = 43
            if (r6 == r0) goto L55
            r0 = 47
            if (r6 == r0) goto L27
            r0 = 51
            if (r6 == r0) goto L1a
            goto L75
        L1a:
            com.android.launcher3.LauncherState r0 = com.android.launcher3.LauncherState.NORMAL
            boolean r0 = r5.isInState(r0)
            if (r0 == 0) goto L75
            r6 = 0
            com.android.launcher3.views.OptionsPopupView.openWidgets(r5, r6)
            return r1
        L27:
            android.view.View r0 = r5.getCurrentFocus()
            boolean r2 = r0 instanceof com.android.launcher3.BubbleTextView
            if (r2 == 0) goto L75
            java.lang.Object r2 = r0.getTag()
            boolean r2 = r2 instanceof com.android.launcher3.model.data.ItemInfo
            if (r2 == 0) goto L75
            com.android.launcher3.accessibility.LauncherAccessibilityDelegate r2 = r5.mAccessibilityDelegate
            java.lang.Object r3 = r0.getTag()
            com.android.launcher3.model.data.ItemInfo r3 = (com.android.launcher3.model.data.ItemInfo) r3
            r4 = 2131296364(0x7f09006c, float:1.8210643E38)
            boolean r0 = r2.performAction(r0, r3, r4)
            if (r0 == 0) goto L75
            int r6 = com.android.launcher3.popup.PopupContainerWithArrow.f7540j
            r6 = 2
            com.android.launcher3.AbstractFloatingView r6 = com.android.launcher3.AbstractFloatingView.getOpenView(r5, r6)
            com.android.launcher3.popup.PopupContainerWithArrow r6 = (com.android.launcher3.popup.PopupContainerWithArrow) r6
            r6.requestFocus()
            return r1
        L55:
            com.android.launcher3.keyboard.CustomActionsPopup r0 = new com.android.launcher3.keyboard.CustomActionsPopup
            android.view.View r2 = r5.getCurrentFocus()
            r0.<init>(r5, r2)
            boolean r0 = r0.show()
            if (r0 == 0) goto L75
            return r1
        L65:
            com.android.launcher3.LauncherState r0 = com.android.launcher3.LauncherState.NORMAL
            boolean r0 = r5.isInState(r0)
            if (r0 == 0) goto L75
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r6 = r5.mStateManager
            com.android.launcher3.LauncherState r7 = com.android.launcher3.LauncherState.ALL_APPS
            r6.goToState(r7)
            return r1
        L75:
            boolean r6 = super.onKeyShortcut(r6, r7)
            return r6
    }

    @Override // android.app.Activity, android.view.KeyEvent.Callback
    public boolean onKeyUp(int r7, android.view.KeyEvent r8) {
            r6 = this;
            r0 = 82
            if (r7 != r0) goto Le3
            com.android.launcher3.dragndrop.DragController r7 = r6.mDragController
            boolean r7 = r7.isDragging()
            r8 = 1
            if (r7 != 0) goto Le2
            com.android.launcher3.Workspace r7 = r6.mWorkspace
            boolean r7 = r7.mIsSwitchingState
            if (r7 != 0) goto Le2
            com.android.launcher3.LauncherState r7 = com.android.launcher3.LauncherState.NORMAL
            boolean r7 = r6.isInState(r7)
            if (r7 == 0) goto Le2
            com.android.launcher3.AbstractFloatingView.closeAllOpenViews(r6, r8)
            boolean r7 = com.android.launcher3.Utilities.IS_RUNNING_IN_TEST_HARNESS
            int r7 = com.android.launcher3.views.OptionsPopupView.f7547j
            android.content.res.Resources r7 = r6.getResources()
            r0 = 2131166396(0x7f0704bc, float:1.7947036E38)
            float r7 = r7.getDimension(r0)
            r0 = 1073741824(0x40000000, float:2.0)
            float r7 = r7 / r0
            com.android.launcher3.dragndrop.DragLayer r0 = r6.mDragLayer
            int r0 = r0.getWidth()
            int r0 = r0 / 2
            float r0 = (float) r0
            com.android.launcher3.dragndrop.DragLayer r1 = r6.mDragLayer
            int r1 = r1.getHeight()
            int r1 = r1 / 2
            float r1 = (float) r1
            android.graphics.RectF r2 = new android.graphics.RectF
            float r3 = r0 - r7
            float r4 = r1 - r7
            float r0 = r0 + r7
            float r1 = r1 + r7
            r2.<init>(r3, r4, r0, r1)
            java.util.ArrayList r7 = new java.util.ArrayList
            r7.<init>()
            r0 = 2131823611(0x7f110bfb, float:1.9280027E38)
            boolean r1 = com.android.launcher3.Utilities.existsStyleWallpapers(r6)
            if (r1 == 0) goto L5f
            r1 = 2131233204(0x7f0809b4, float:1.8082539E38)
            goto L62
        L5f:
            r1 = 2131233280(0x7f080a00, float:1.8082693E38)
        L62:
            com.android.launcher3.views.OptionsPopupView$OptionItem r3 = new com.android.launcher3.views.OptionsPopupView$OptionItem
            com.android.launcher3.logging.StatsLogManager$LauncherEvent r4 = com.android.launcher3.logging.StatsLogManager.LauncherEvent.IGNORE
            b.c.b.l3.i r5 = b.c.b.l3.i.a
            r3.<init>(r0, r1, r4, r5)
            r7.add(r3)
            com.android.launcher3.views.OptionsPopupView$OptionItem r0 = new com.android.launcher3.views.OptionsPopupView$OptionItem
            r1 = 2131823771(0x7f110c9b, float:1.9280351E38)
            r3 = 2131233288(0x7f080a08, float:1.808271E38)
            com.android.launcher3.logging.StatsLogManager$LauncherEvent r4 = com.android.launcher3.logging.StatsLogManager.LauncherEvent.LAUNCHER_WIDGETSTRAY_BUTTON_TAP_OR_LONGPRESS
            b.c.b.l3.p r5 = b.c.b.l3.p.a
            r0.<init>(r1, r3, r4, r5)
            r7.add(r0)
            com.android.launcher3.views.OptionsPopupView$OptionItem r0 = new com.android.launcher3.views.OptionsPopupView$OptionItem
            r1 = 2131823138(0x7f110a22, float:1.9279067E38)
            r3 = 2131233252(0x7f0809e4, float:1.8082636E38)
            com.android.launcher3.logging.StatsLogManager$LauncherEvent r4 = com.android.launcher3.logging.StatsLogManager.LauncherEvent.LAUNCHER_SETTINGS_BUTTON_TAP_OR_LONGPRESS
            b.c.b.l3.a r5 = b.c.b.l3.a.a
            r0.<init>(r1, r3, r4, r5)
            r7.add(r0)
            android.view.LayoutInflater r0 = r6.getLayoutInflater()
            com.android.launcher3.dragndrop.DragLayer r1 = r6.mDragLayer
            r3 = 0
            r4 = 2131493266(0x7f0c0192, float:1.8610007E38)
            android.view.View r0 = r0.inflate(r4, r1, r3)
            com.android.launcher3.views.OptionsPopupView r0 = (com.android.launcher3.views.OptionsPopupView) r0
            r0.mTargetRect = r2
            java.util.Iterator r7 = r7.iterator()
        La8:
            boolean r1 = r7.hasNext()
            if (r1 == 0) goto Ldb
            java.lang.Object r1 = r7.next()
            com.android.launcher3.views.OptionsPopupView$OptionItem r1 = (com.android.launcher3.views.OptionsPopupView.OptionItem) r1
            r2 = 2131493647(0x7f0c030f, float:1.861078E38)
            android.view.View r2 = r0.inflateAndAdd(r2, r0)
            com.android.launcher3.shortcuts.DeepShortcutView r2 = (com.android.launcher3.shortcuts.DeepShortcutView) r2
            androidx.appcompat.widget.AppCompatImageView r3 = r2.getIconView()
            int r4 = r1.mIconRes
            r3.setImageResource(r4)
            com.android.launcher3.BubbleTextView r3 = r2.getBubbleText()
            int r4 = r1.mLabelRes
            r3.setText(r4)
            r2.setOnClickListener(r0)
            r2.setOnLongClickListener(r0)
            android.util.ArrayMap<android.view.View, com.android.launcher3.views.OptionsPopupView$OptionItem> r3 = r0.mItemMap
            r3.put(r2, r1)
            goto La8
        Ldb:
            int r7 = r0.getChildCount()
            r0.reorderAndShow(r7)
        Le2:
            return r8
        Le3:
            boolean r7 = super.onKeyUp(r7, r8)
            return r7
    }

    @Override // com.microsoft.intune.mam.client.app.MAMActivity, com.microsoft.intune.mam.client.app.HookedActivity
    public void onMAMActivityResult(int r1, int r2, android.content.Intent r3) {
            r0 = this;
            r0.handleActivityResult(r1, r2, r3)
            return
    }

    @Override // com.android.launcher3.BaseDraggingActivity, com.microsoft.intune.mam.client.app.MAMActivity, com.microsoft.intune.mam.client.app.HookedActivity
    public void onMAMCreate(android.os.Bundle r14) {
            r13 = this;
            java.lang.String r0 = "Launcher"
            b.a.m.s3.f r1 = r13.mPiplConsentManager
            boolean r1 = r1.d()
            if (r1 == 0) goto Le
            super.onMAMCreate(r14)
            return
        Le:
            boolean r1 = r13.shouldShowHome()
            if (r1 != 0) goto L18
            super.onMAMCreate(r14)
            return
        L18:
            com.android.launcher3.util.TraceHelper r1 = com.android.launcher3.util.TraceHelper.INSTANCE
            java.lang.String r1 = "Launcher-onCreate"
            com.android.launcher3.util.TraceHelper.beginSection(r1)
            super.onMAMCreate(r14)
            boolean r2 = r13.mIncorrectLaunchState
            if (r2 == 0) goto L27
            return
        L27:
            java.lang.String r2 = "super call"
            com.android.launcher3.util.TraceHelper.partitionSection(r1, r2)
            android.content.SharedPreferences r2 = com.android.launcher3.Utilities.getPrefs(r13)
            r13.mSharedPrefs = r2
            r3 = 1
            java.lang.String r4 = "is_first_run"
            boolean r2 = r2.getBoolean(r4, r3)
            r4 = 0
            if (r2 == 0) goto L61
            java.util.concurrent.ExecutorService r5 = java.util.concurrent.Executors.newSingleThreadExecutor()
            com.android.launcher3.provider.OEMLoaderTask r6 = new com.android.launcher3.provider.OEMLoaderTask
            r6.<init>(r13)
            java.util.concurrent.FutureTask r7 = new java.util.concurrent.FutureTask
            r7.<init>(r6)
            r5.submit(r7)
            r5.shutdown()
            boolean r5 = com.android.launcher3.config.FeatureFlags.IS_E_OS
            if (r5 != 0) goto L55
            goto L62
        L55:
            long r5 = java.lang.System.currentTimeMillis()
            java.lang.String r8 = "GadernSalad"
            java.lang.String r9 = "FirstUseTime"
            b.a.m.m4.t.A(r13, r8, r9, r5)
            goto L62
        L61:
            r7 = r4
        L62:
            com.android.launcher3.LauncherAppState r5 = com.android.launcher3.LauncherAppState.getInstance(r13)
            android.content.res.Configuration r6 = new android.content.res.Configuration
            android.content.res.Resources r8 = r13.getResources()
            android.content.res.Configuration r8 = r8.getConfiguration()
            r6.<init>(r8)
            r13.mOldConfig = r6
            com.android.launcher3.LauncherModel r6 = r5.mModel
            r13.mModel = r6
            r13.initDeviceProfile()
            com.android.launcher3.icons.IconCache r5 = r5.mIconCache
            r13.mIconCache = r5
            com.android.launcher3.accessibility.LauncherAccessibilityDelegate r5 = new com.android.launcher3.accessibility.LauncherAccessibilityDelegate
            r5.<init>(r13)
            r13.mAccessibilityDelegate = r5
            com.android.launcher3.accessibility.MultiSelectionAccessibilityDelegate r5 = new com.android.launcher3.accessibility.MultiSelectionAccessibilityDelegate
            r5.<init>()
            r13.mAccessibilityDelegateForMultiSelection = r5
            com.android.launcher3.accessibility.LauncherAccessibilityDelegateWrapper r5 = new com.android.launcher3.accessibility.LauncherAccessibilityDelegateWrapper
            com.android.launcher3.accessibility.LauncherAccessibilityDelegate r6 = r13.mAccessibilityDelegate
            com.android.launcher3.accessibility.MultiSelectionAccessibilityDelegate r8 = r13.mAccessibilityDelegateForMultiSelection
            r5.<init>(r13, r6, r8)
            r13.mAccessibilityDelegateWrapper = r5
            if (r2 == 0) goto Lc9
            r5 = 500(0x1f4, double:2.47E-321)
            java.util.concurrent.TimeUnit r2 = java.util.concurrent.TimeUnit.MILLISECONDS     // Catch: java.lang.Exception -> Lb4
            java.lang.Object r2 = r7.get(r5, r2)     // Catch: java.lang.Exception -> Lb4
            java.lang.Boolean r2 = (java.lang.Boolean) r2     // Catch: java.lang.Exception -> Lb4
            boolean r2 = r2.booleanValue()     // Catch: java.lang.Exception -> Lb4
            if (r2 != r3) goto Lae
            java.lang.String r2 = "futureTask return true"
            goto Lb0
        Lae:
            java.lang.String r2 = "futureTask return false"
        Lb0:
            android.util.Log.w(r0, r2)     // Catch: java.lang.Exception -> Lb4
            goto Lc9
        Lb4:
            r2 = move-exception
            java.lang.String r5 = "Load Config settings failed. "
            java.lang.StringBuilder r5 = b.c.e.c.a.G(r5)
            java.lang.String r2 = r2.getMessage()
            r5.append(r2)
            java.lang.String r2 = r5.toString()
            android.util.Log.w(r0, r2)
        Lc9:
            com.android.launcher3.DeviceProfile r0 = r13.mDeviceProfile
            com.android.launcher3.InvariantDeviceProfile r2 = r0.inv
            com.android.launcher3.DeviceBehavior r2 = r2.mBehavior
            com.android.launcher3.allapps.AppDrawerBehavior r0 = r2.getAppDrawerBehavior(r0)
            r13.mAppDrawerBehavior = r0
            b.a.m.k4.b r0 = new b.a.m.k4.b
            r0.<init>(r13)
            r13.mDragController = r0
            b.a.m.r1.m r0 = new b.a.m.r1.m
            r0.<init>(r13)
            r13.mAllAppsController = r0
            com.android.launcher3.DeviceProfile r0 = r13.mDeviceProfile
            com.android.launcher3.InvariantDeviceProfile r2 = r0.inv
            com.android.launcher3.DeviceBehavior r2 = r2.mBehavior
            com.android.launcher3.bingsearch.BingSearchBehavior r0 = r2.getBingSearchBehavior(r0)
            r13.mBingSearchBehavior = r0
            com.android.launcher3.bingsearch.BingSearchTransitionController r0 = new com.android.launcher3.bingsearch.BingSearchTransitionController
            r0.<init>(r13)
            r13.mBingSearchController = r0
            com.android.launcher3.MsLauncherStateManager r0 = new com.android.launcher3.MsLauncherStateManager
            com.android.launcher3.LauncherState r2 = com.android.launcher3.LauncherState.NORMAL
            r0.<init>(r13, r2)
            r13.mStateManager = r0
            b.a.m.h4.n.c(r13)
            r0 = r13
            com.microsoft.launcher.LauncherActivity r0 = (com.microsoft.launcher.LauncherActivity) r0
            com.android.launcher3.tasklayout.TaskLayoutHelper r5 = r13.getTaskLayoutHelper()
            b.a.m.p3.n r6 = new b.a.m.p3.n
            r6.<init>(r0)
            r5.addLayoutListener(r6)
            com.android.launcher3.util.OnboardingPrefs r0 = new com.android.launcher3.util.OnboardingPrefs
            com.android.launcher3.widget.WidgetManagerHelper r0 = new com.android.launcher3.widget.WidgetManagerHelper
            r0.<init>(r13)
            r13.mAppWidgetManager = r0
            com.android.launcher3.LauncherAppWidgetHost r0 = new com.android.launcher3.LauncherAppWidgetHost
            b.c.b.g0 r5 = new b.c.b.g0
            r5.<init>(r13)
            r0.<init>(r13, r5)
            r13.mAppWidgetHost = r0
            java.lang.ref.WeakReference<android.appwidget.AppWidgetHost> r5 = b.a.m.u4.k.a
            java.lang.ref.WeakReference r5 = new java.lang.ref.WeakReference
            r5.<init>(r0)
            b.a.m.u4.k.a = r5
            com.android.launcher3.LauncherAppWidgetHost r0 = r13.mAppWidgetHost
            b.a.m.u4.k.a(r0)
            java.util.Set<java.lang.Integer> r0 = com.microsoft.launcher.featurepage.FeaturePageStateManager.a
            com.microsoft.launcher.featurepage.FeaturePageStateManager r0 = com.microsoft.launcher.featurepage.FeaturePageStateManager.b.a
            r13.mFeaturePageStateManager = r0
            b.a.m.r2.c r0 = new b.a.m.r2.c
            r0.<init>(r13)
            r13.mFeaturePageHost = r0
            r0 = 2131493222(0x7f0c0166, float:1.8609918E38)
            android.view.LayoutInflater r5 = android.view.LayoutInflater.from(r13)
            android.view.View r0 = r5.inflate(r0, r4)
            com.android.launcher3.LauncherRootView r0 = (com.android.launcher3.LauncherRootView) r0
            r13.mRootView = r0
            r5 = 1792(0x700, float:2.511E-42)
            r0.setSystemUiVisibility(r5)
            com.android.launcher3.LauncherRootView r0 = r13.mRootView
            r13.mLauncherView = r0
            r0 = 2131297173(0x7f090395, float:1.8212283E38)
            android.view.View r0 = r13.findViewById(r0)
            com.android.launcher3.dragndrop.DragLayer r0 = (com.android.launcher3.dragndrop.DragLayer) r0
            r13.mDragLayer = r0
            com.android.launcher3.keyboard.ViewGroupFocusHelper r0 = r0.getFocusIndicatorHelper()
            r13.mFocusHandler = r0
            com.android.launcher3.dragndrop.DragLayer r0 = r13.mDragLayer
            r6 = 2131299283(0x7f090bd3, float:1.8216563E38)
            android.view.View r0 = r0.findViewById(r6)
            com.android.launcher3.Workspace r0 = (com.android.launcher3.Workspace) r0
            r13.mWorkspace = r0
            com.android.launcher3.dragndrop.DragLayer r6 = r13.mDragLayer
            r0.initParentViews(r6)
            r0 = 2131297964(0x7f0906ac, float:1.8213888E38)
            android.view.View r0 = r13.findViewById(r0)
            com.microsoft.launcher.overview.OverviewPanel r0 = (com.microsoft.launcher.overview.OverviewPanel) r0
            r13.mOverviewPanel = r0
            r0 = 2131297379(0x7f090463, float:1.8212701E38)
            android.view.View r0 = r13.findViewById(r0)
            android.view.ViewStub r0 = (android.view.ViewStub) r0
            boolean r6 = com.android.launcher3.config.FeatureFlags.isVLMSupported(r13)
            if (r6 == 0) goto L19a
            r6 = 2131493145(0x7f0c0119, float:1.8609762E38)
            goto L1af
        L19a:
            b.a.m.s2.g r6 = com.microsoft.launcher.features.FeatureManager.b()
            com.microsoft.launcher.codegen.launcher3.features.Feature r7 = com.microsoft.launcher.codegen.launcher3.features.Feature.EXPANDABLE_HOTSEAT
            com.microsoft.launcher.features.FeatureManager r6 = (com.microsoft.launcher.features.FeatureManager) r6
            boolean r6 = r6.d(r7)
            if (r6 == 0) goto L1ac
            r6 = 2131493147(0x7f0c011b, float:1.8609766E38)
            goto L1af
        L1ac:
            r6 = 2131493144(0x7f0c0118, float:1.860976E38)
        L1af:
            r0.setLayoutResource(r6)
            com.android.launcher3.DeviceProfile r6 = r13.mDeviceProfile
            com.android.launcher3.InvariantDeviceProfile r7 = r6.inv
            com.android.launcher3.DeviceBehavior r7 = r7.mBehavior
            b.a.m.x2.n0 r6 = r7.getHotseatLayoutBehavior(r6)
            r13.mHotseatLayoutBehavior = r6
            android.view.View r0 = r0.inflate()
            com.android.launcher3.Hotseat r0 = (com.android.launcher3.Hotseat) r0
            r13.mHotseat = r0
            boolean r6 = r0 instanceof com.microsoft.launcher.hotseat.ExpandableHotseat
            if (r6 == 0) goto L1dc
            com.android.launcher3.uioverrides.hotseat.ExpandableHotseatTransitionController r0 = new com.android.launcher3.uioverrides.hotseat.ExpandableHotseatTransitionController
            r0.<init>(r13)
            r13.mHotseatController = r0
            com.android.launcher3.Hotseat r6 = r13.mHotseat
            r0.setupViews(r6)
            com.android.launcher3.Hotseat r0 = r13.mHotseat
            r0.bringToFront()
            goto L1f1
        L1dc:
            boolean r6 = r0 instanceof com.microsoft.launcher.hotseat.EHotseat
            if (r6 == 0) goto L1ea
            b.a.m.x2.f0 r6 = new b.a.m.x2.f0
            r6.<init>(r13)
            r13.mHotseatController = r6
            r6.mHotseat = r0
            goto L1f1
        L1ea:
            com.android.launcher3.uioverrides.hotseat.HotseatTransitionController r0 = new com.android.launcher3.uioverrides.hotseat.HotseatTransitionController
            r0.<init>(r13)
            r13.mHotseatController = r0
        L1f1:
            com.android.launcher3.Hotseat r0 = r13.mHotseat
            com.android.launcher3.Workspace r6 = r13.mWorkspace
            r0.setWorkspace(r6)
            b.a.m.x2.n0 r0 = r13.mHotseatLayoutBehavior
            com.android.launcher3.Hotseat r6 = r13.mHotseat
            r0.F(r6)
            com.android.launcher3.LauncherRootView r0 = r13.mLauncherView
            r0.setSystemUiVisibility(r5)
            com.android.launcher3.dragndrop.DragLayer r0 = r13.mDragLayer
            com.android.launcher3.dragndrop.DragController r5 = r13.mDragController
            com.android.launcher3.Workspace r6 = r13.mWorkspace
            r0.setup(r5, r6)
            com.android.launcher3.Workspace r0 = r13.mWorkspace
            com.android.launcher3.dragndrop.DragController r5 = r13.mDragController
            r0.setup(r5)
            com.android.launcher3.Workspace r0 = r13.mWorkspace
            com.android.launcher3.util.WallpaperOffsetInterpolator r5 = r0.mWallpaperOffset
            r5.mLockedToDefaultPage = r3
            r0.bindAndInitFirstWorkspaceScreen()
            com.android.launcher3.dragndrop.DragController r0 = r13.mDragController
            com.android.launcher3.Workspace r5 = r13.mWorkspace
            java.util.ArrayList<com.android.launcher3.dragndrop.DragController$DragListener> r0 = r0.mListeners
            r0.add(r5)
            com.android.launcher3.dragndrop.DragLayer r0 = r13.mDragLayer
            r5 = 2131297174(0x7f090396, float:1.8212285E38)
            android.view.View r0 = r0.findViewById(r5)
            com.android.launcher3.DropTargetBar r0 = (com.android.launcher3.DropTargetBar) r0
            r13.mDropTargetBar = r0
            r0 = 2131297769(0x7f0905e9, float:1.8213492E38)
            android.view.View r0 = r13.findViewById(r0)
            com.microsoft.launcher.multiselection.MultiSelectionDropTargetBar r0 = (com.microsoft.launcher.multiselection.MultiSelectionDropTargetBar) r0
            r13.mMultiSelectionTargetBar = r0
            r0.bringToFront()
            b.a.m.n4.d0.e r0 = new b.a.m.n4.d0.e
            android.os.Handler r5 = r13.mHandler
            r0.<init>(r13, r5)
            r13.delayedUIHandler = r0
            com.android.launcher3.Launcher$7 r5 = new com.android.launcher3.Launcher$7
            r5.<init>(r13)
            r0.a(r5)
            r0 = 2131298245(0x7f0907c5, float:1.8214458E38)
            android.view.View r0 = r13.findViewById(r0)
            com.android.launcher3.views.ScrimView r0 = (com.android.launcher3.views.ScrimView) r0
            r13.mScrimView = r0
            com.microsoft.launcher.multiselection.MultiSelectionDropTargetBar r0 = r13.mMultiSelectionTargetBar
            com.android.launcher3.dragndrop.DragController r5 = r13.mDragController
            r0.setup(r5)
            int r0 = com.android.launcher3.OverlayPanel.f7538b
            android.view.LayoutInflater r0 = r13.getLayoutInflater()
            r5 = 2131493404(0x7f0c021c, float:1.8610287E38)
            android.view.View r0 = r0.inflate(r5, r4)
            com.android.launcher3.OverlayPanel r0 = (com.android.launcher3.OverlayPanel) r0
            r13.mOverlayPanel = r0
            b.a.m.d4.h0 r0 = new b.a.m.d4.h0
            b.c.b.j3.c r5 = new b.c.b.j3.c
            r5.<init>(r13)
            r0.<init>(r13, r5)
            r13.mPopupDataProvider = r0
            com.android.launcher3.states.RotationHelper r0 = new com.android.launcher3.states.RotationHelper
            r0.<init>(r13)
            r13.mRotationHelper = r0
            java.lang.Class<com.android.launcher3.LauncherAppTransitionManager> r0 = com.android.launcher3.LauncherAppTransitionManager.class
            r5 = 2131821163(0x7f11026b, float:1.9275061E38)
            com.android.launcher3.util.ResourceBasedOverride r0 = androidx.transition.CanvasUtils.getObject(r0, r13, r5)
            com.android.launcher3.LauncherAppTransitionManager r0 = (com.android.launcher3.LauncherAppTransitionManager) r0
            r13.mAppTransitionManager = r0
            java.util.Objects.requireNonNull(r0)
            com.android.launcher3.util.ActivityTracker<com.android.launcher3.Launcher> r0 = com.android.launcher3.Launcher.ACTIVITY_TRACKER
            java.util.Objects.requireNonNull(r0)
            java.lang.ref.WeakReference r5 = new java.lang.ref.WeakReference
            r5.<init>(r13)
            r0.mCurrentActivity = r5
            android.content.Intent r5 = r13.getIntent()
            r6 = 0
            boolean r0 = r0.handleIntent(r13, r5, r6)
            java.lang.String r5 = "launcher.state"
            if (r0 == 0) goto L2b6
            if (r14 == 0) goto L2b6
            r14.remove(r5)
        L2b6:
            if (r14 != 0) goto L2ba
            goto L330
        L2ba:
            int r2 = r2.ordinal
            int r2 = r14.getInt(r5, r2)
            com.android.launcher3.LauncherState[] r5 = com.android.launcher3.LauncherState.sAllStates
            int r7 = r5.length
            java.lang.Object[] r5 = java.util.Arrays.copyOf(r5, r7)
            com.android.launcher3.LauncherState[] r5 = (com.android.launcher3.LauncherState[]) r5
            r2 = r5[r2]
            java.util.Objects.requireNonNull(r2)
            r5 = 2
            boolean r5 = r2.hasFlag(r5)
            if (r5 != 0) goto L2df
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r7 = r13.mStateManager
            r9 = 0
            r10 = 0
            r12 = 0
            r8 = r2
            r7.goToState(r8, r9, r10, r12)
        L2df:
            java.lang.String r5 = "launcher.request_args"
            android.os.Parcelable r5 = r14.getParcelable(r5)
            com.android.launcher3.util.PendingRequestArgs r5 = (com.android.launcher3.util.PendingRequestArgs) r5
            if (r5 == 0) goto L2eb
            r13.mPendingRequestArgs = r5
        L2eb:
            java.lang.String r5 = "launcher.request_code"
            int r5 = r14.getInt(r5)
            r13.mPendingActivityRequestCode = r5
            java.lang.String r5 = "launcher.activity_result"
            android.os.Parcelable r5 = r14.getParcelable(r5)
            com.android.launcher3.util.ActivityResultInfo r5 = (com.android.launcher3.util.ActivityResultInfo) r5
            r13.mPendingActivityResult = r5
            java.lang.String r5 = "launcher.widget_panel"
            android.util.SparseArray r5 = r14.getSparseParcelableArray(r5)
            if (r5 == 0) goto L330
            b.a.m.w2.h r7 = b.a.m.n2.u.b()
            b.a.m.q0 r7 = (b.a.m.q0) r7
            java.util.Objects.requireNonNull(r7)
            boolean r7 = com.android.launcher3.config.FeatureFlags.IS_E_OS
            if (r7 == 0) goto L327
            com.android.launcher3.LauncherState r7 = com.android.launcher3.LauncherState.ALL_APPS
            boolean r2 = r7.equals(r2)
            if (r2 == 0) goto L327
            android.os.Handler r2 = r13.mHandler
            b.c.b.l0 r4 = new b.c.b.l0
            r4.<init>(r13, r5)
            r7 = 800(0x320, double:3.953E-321)
            r2.postDelayed(r4, r7)
            goto L330
        L327:
            java.lang.String r2 = ""
            com.android.launcher3.widget.WidgetsFullSheet r2 = com.android.launcher3.widget.WidgetsFullSheet.show(r13, r4, r6, r2)
            r2.restoreHierarchyState(r5)
        L330:
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r2 = r13.mStateManager
            r2.reapplyState(r6)
            r2 = -1
            if (r14 == 0) goto L346
            java.lang.String r4 = "launcher.current_screen"
            int r4 = r14.getInt(r4, r2)
            java.lang.String r5 = "launcher.overlay"
            int r14 = r14.getInt(r5, r2)
            r2 = r4
            goto L347
        L346:
            r14 = -1
        L347:
            r13.mPageToBindSynchronously = r2
            r13.mRestoredOverlayState = r14
            com.android.launcher3.LauncherModel r14 = r13.mModel
            boolean r14 = r14.addCallbacksAndLoad(r13)
            if (r14 != 0) goto L35f
            if (r0 != 0) goto L35f
            com.android.launcher3.dragndrop.DragLayer r14 = r13.mDragLayer
            com.android.launcher3.util.MultiValueAlpha$AlphaProperty r14 = r14.getAlphaProperty(r3)
            r0 = 0
            r14.setValue(r0)
        L35f:
            r14 = 3
            r13.setDefaultKeyMode(r14)
            com.android.launcher3.LauncherRootView r14 = r13.getRootView()
            r13.setContentView(r14)
            com.android.launcher3.LauncherRootView r14 = r13.getRootView()
            r14.dispatchInsets()
            android.content.BroadcastReceiver r14 = r13.mScreenOffReceiver
            android.content.IntentFilter r0 = new android.content.IntentFilter
            java.lang.String r2 = "android.intent.action.SCREEN_OFF"
            r0.<init>(r2)
            r13.registerReceiver(r14, r0)
            com.android.launcher3.util.SystemUiController r14 = r13.getSystemUiController()
            r0 = 2130969301(0x7f0402d5, float:1.754728E38)
            boolean r0 = androidx.transition.CanvasUtils.getAttrBoolean(r13, r0)
            r14.updateUiState(r6, r0)
            com.android.launcher3.Launcher$2 r14 = new com.android.launcher3.Launcher$2
            r14.<init>(r13)
            r13.mOverlayManager = r14
            com.android.launcher3.util.MainThreadInitializedObject<com.android.launcher3.uioverrides.plugins.PluginManagerWrapper> r14 = com.android.launcher3.uioverrides.plugins.PluginManagerWrapper.INSTANCE
            java.lang.Object r14 = r14.get(r13, r6)
            com.android.launcher3.uioverrides.plugins.PluginManagerWrapper r14 = (com.android.launcher3.uioverrides.plugins.PluginManagerWrapper) r14
            java.lang.Class<com.android.systemui.plugins.OverlayPlugin> r0 = com.android.systemui.plugins.OverlayPlugin.class
            com.android.systemui.shared.plugins.PluginManager r14 = r14.mPluginManager
            if (r14 == 0) goto L3a3
            r14.addPluginListener(r13, r0, r6)
        L3a3:
            com.android.launcher3.states.RotationHelper r14 = r13.mRotationHelper
            boolean r0 = r14.mInitialized
            if (r0 != 0) goto L3be
            r14.mInitialized = r3
            r14.notifyChange()
            android.content.ContentResolver r0 = r14.mContentResolver
            java.lang.String r2 = "accelerometer_rotation"
            android.net.Uri r2 = android.provider.Settings.System.getUriFor(r2)
            android.database.ContentObserver r3 = r14.mSystemAutoRotateObserver
            r0.registerContentObserver(r2, r6, r3)
            r14.updateAutoRotateSetting()
        L3be:
            android.content.res.Resources r14 = r13.getResources()
            com.android.launcher3.Utilities.isRtl(r14)
            int r14 = android.os.Build.VERSION.SDK_INT
            r0 = 26
            if (r14 < r0) goto L3e1
            com.android.launcher3.SessionCommitReceiver r14 = new com.android.launcher3.SessionCommitReceiver
            r14.<init>()
            r13.mSessionCommitReceiver = r14
            android.content.IntentFilter r14 = new android.content.IntentFilter
            r14.<init>()
            java.lang.String r0 = "android.content.pm.action.SESSION_COMMITTED"
            r14.addAction(r0)
            com.android.launcher3.SessionCommitReceiver r0 = r13.mSessionCommitReceiver
            r13.registerReceiver(r0, r14)
        L3e1:
            android.graphics.Rect r14 = com.android.launcher3.folder.Folder.sTempRect
            android.content.res.Resources r14 = r13.getResources()
            r0 = 2131821819(0x7f1104fb, float:1.9276392E38)
            java.lang.String r14 = r14.getString(r0)
            com.android.launcher3.folder.Folder.sDefaultFolderName = r14
            android.content.res.Resources r14 = r13.getResources()
            r0 = 2131821817(0x7f1104f9, float:1.9276388E38)
            java.lang.String r14 = r14.getString(r0)
            com.android.launcher3.folder.Folder.sHintText = r14
            java.lang.String r14 = "End"
            com.android.launcher3.util.TraceHelper.endSection(r1, r14)
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r14 = r13.mStateManager
            com.android.launcher3.Launcher$1 r0 = new com.android.launcher3.Launcher$1
            r0.<init>(r13)
            java.util.ArrayList<com.android.launcher3.statemanager.StateManager$StateListener<STATE_TYPE extends com.android.launcher3.statemanager.BaseState<STATE_TYPE>>> r14 = r14.mListeners
            r14.add(r0)
            com.microsoft.launcher.AppSetManager r14 = new com.microsoft.launcher.AppSetManager
            r14.<init>(r13)
            r13.mAppSetManager = r14
            com.android.launcher3.compat.UserManagerCompat r14 = com.android.launcher3.compat.UserManagerCompat.getInstance(r13)
            b.c.b.h0 r0 = new b.c.b.h0
            r0.<init>(r13)
            com.android.launcher3.util.SafeCloseable r14 = r14.addUserChangeListener(r0)
            r13.mUserChangedCallbackCloseable = r14
            return
    }

    @Override // com.android.launcher3.BaseDraggingActivity, com.microsoft.intune.mam.client.app.MAMActivity, com.microsoft.intune.mam.client.app.HookedActivity
    public void onMAMDestroy() {
            r3 = this;
            b.a.m.s3.f r0 = r3.mPiplConsentManager
            boolean r0 = r0.d()
            if (r0 == 0) goto Lc
            super.onMAMDestroy()
            return
        Lc:
            boolean r0 = r3.shouldShowHome()
            super.onMAMDestroy()
            if (r0 != 0) goto L16
            return
        L16:
            com.android.launcher3.util.ActivityTracker<com.android.launcher3.Launcher> r0 = com.android.launcher3.Launcher.ACTIVITY_TRACKER
            java.lang.ref.WeakReference<T extends com.android.launcher3.BaseActivity> r1 = r0.mCurrentActivity
            java.lang.Object r1 = r1.get()
            if (r1 != r3) goto L25
            java.lang.ref.WeakReference<T extends com.android.launcher3.BaseActivity> r0 = r0.mCurrentActivity
            r0.clear()
        L25:
            boolean r0 = r3.mIncorrectLaunchState
            if (r0 == 0) goto L2a
            return
        L2a:
            android.content.BroadcastReceiver r0 = r3.mScreenOffReceiver
            r3.unregisterReceiver(r0)
            com.android.launcher3.SessionCommitReceiver r0 = r3.mSessionCommitReceiver
            if (r0 == 0) goto L36
            r3.unregisterReceiver(r0)
        L36:
            com.android.launcher3.Workspace r0 = r3.mWorkspace
            com.android.launcher3.Workspace$15 r1 = new com.android.launcher3.Workspace$15
            r1.<init>(r0)
            r0.mapOverItems(r1)
            com.android.launcher3.util.MainThreadInitializedObject<com.android.launcher3.uioverrides.plugins.PluginManagerWrapper> r0 = com.android.launcher3.uioverrides.plugins.PluginManagerWrapper.INSTANCE
            r1 = 0
            java.lang.Object r0 = r0.get(r3, r1)
            com.android.launcher3.uioverrides.plugins.PluginManagerWrapper r0 = (com.android.launcher3.uioverrides.plugins.PluginManagerWrapper) r0
            com.android.systemui.shared.plugins.PluginManager r0 = r0.mPluginManager
            if (r0 == 0) goto L50
            r0.removePluginListener(r3)
        L50:
            com.android.launcher3.LauncherModel r0 = r3.mModel
            r0.removeCallbacks(r3)
            com.android.launcher3.states.RotationHelper r0 = r3.mRotationHelper
            boolean r1 = r0.mDestroyed
            if (r1 != 0) goto L75
            r1 = 1
            r0.mDestroyed = r1
            android.content.SharedPreferences r1 = r0.mSharedPrefs
            if (r1 == 0) goto L65
            r1.unregisterOnSharedPreferenceChangeListener(r0)
        L65:
            b.a.m.s2.g r1 = com.microsoft.launcher.features.FeatureManager.b()
            com.microsoft.launcher.features.FeatureManager r1 = (com.microsoft.launcher.features.FeatureManager) r1
            r1.j(r0)
            android.content.ContentResolver r1 = r0.mContentResolver
            android.database.ContentObserver r0 = r0.mSystemAutoRotateObserver
            r1.unregisterContentObserver(r0)
        L75:
            com.android.launcher3.LauncherAppWidgetHost r0 = r3.mAppWidgetHost     // Catch: java.lang.NullPointerException -> L7b
            b.a.m.u4.k.b(r0)     // Catch: java.lang.NullPointerException -> L7b
            goto L83
        L7b:
            r0 = move-exception
            java.lang.String r1 = "Launcher"
            java.lang.String r2 = "problem while stopping AppWidgetHost during Launcher destruction"
            android.util.Log.w(r1, r2, r0)
        L83:
            java.lang.ref.WeakReference<android.appwidget.AppWidgetHost> r0 = b.a.m.u4.k.a
            if (r0 == 0) goto L8d
            r0.clear()
            r0 = 0
            b.a.m.u4.k.a = r0
        L8d:
            android.text.method.TextKeyListener r0 = android.text.method.TextKeyListener.getInstance()
            r0.release()
            r3.clearPendingBinds()
            com.microsoft.launcher.AppSetManager r0 = r3.mAppSetManager
            r0.i()
            com.android.systemui.plugins.shared.LauncherOverlayManager r0 = r3.mOverlayManager
            r0.onActivityDestroyed(r3)
            com.android.launcher3.LauncherAppTransitionManager r0 = r3.mAppTransitionManager
            java.util.Objects.requireNonNull(r0)
            com.android.launcher3.util.SafeCloseable r0 = r3.mUserChangedCallbackCloseable
            r0.close()
            com.android.launcher3.allapps.AllAppsTransitionController r0 = r3.mAllAppsController
            java.util.Objects.requireNonNull(r0)
            com.android.launcher3.util.MainThreadInitializedObject<com.android.launcher3.uioverrides.plugins.PluginManagerWrapper> r1 = com.android.launcher3.uioverrides.plugins.PluginManagerWrapper.INSTANCE
            com.android.launcher3.Launcher r2 = r0.mLauncher
            java.lang.Object r1 = r1.get(r2)
            com.android.launcher3.uioverrides.plugins.PluginManagerWrapper r1 = (com.android.launcher3.uioverrides.plugins.PluginManagerWrapper) r1
            com.android.systemui.shared.plugins.PluginManager r1 = r1.mPluginManager
            if (r1 == 0) goto Lc1
            r1.removePluginListener(r0)
        Lc1:
            return
    }

    @Override // com.microsoft.intune.mam.client.app.MAMActivity, com.microsoft.intune.mam.client.app.HookedActivity
    public void onMAMNewIntent(android.content.Intent r11) {
            r10 = this;
            boolean r0 = com.android.launcher3.Utilities.IS_RUNNING_IN_TEST_HARNESS
            if (r0 == 0) goto L14
            java.lang.StringBuilder r0 = new java.lang.StringBuilder
            r0.<init>()
            java.lang.String r1 = "Launcher.onNewIntent: "
            r0.append(r1)
            r0.append(r11)
            r0.toString()
        L14:
            com.android.launcher3.util.TraceHelper r0 = com.android.launcher3.util.TraceHelper.INSTANCE
            java.lang.String r0 = "NEW_INTENT"
            com.android.launcher3.util.TraceHelper.beginSection(r0)
            super.onMAMNewIntent(r11)
            boolean r1 = r10.hasWindowFocus()
            r2 = 1
            r3 = 0
            if (r1 == 0) goto L31
            int r1 = r11.getFlags()
            r4 = 4194304(0x400000, float:5.877472E-39)
            r1 = r1 & r4
            if (r1 == r4) goto L31
            r1 = 1
            goto L32
        L31:
            r1 = 0
        L32:
            com.android.launcher3.allapps.AppDrawerBehavior r4 = r10.mAppDrawerBehavior
            r4.isTouchOnOtherScreen = r3
            com.android.launcher3.bingsearch.BingSearchBehavior r4 = r10.mBingSearchBehavior
            r4.isTouchOnOtherScreen = r3
            com.android.launcher3.tasklayout.TaskLayoutHelper r4 = r10.getTaskLayoutHelper()
            r4.updateOccupiedStatus(r3, r3)
            r4 = 131071(0x1ffff, float:1.8367E-40)
            if (r1 == 0) goto L5c
            com.android.launcher3.LauncherState r5 = com.android.launcher3.LauncherState.NORMAL
            boolean r5 = r10.isInState(r5)
            if (r5 == 0) goto L5c
            boolean r5 = r10.workspaceOnDefaultHomePage()
            if (r5 != 0) goto L5c
            com.android.launcher3.AbstractFloatingView r5 = com.android.launcher3.AbstractFloatingView.getOpenView(r10, r4)
            if (r5 != 0) goto L5c
            r5 = 1
            goto L5d
        L5c:
            r5 = 0
        L5d:
            java.lang.String r6 = r11.getAction()
            java.lang.String r7 = "android.intent.action.MAIN"
            boolean r6 = r7.equals(r6)
            com.android.launcher3.util.ActivityTracker<com.android.launcher3.Launcher> r7 = com.android.launcher3.Launcher.ACTIVITY_TRACKER
            java.util.Objects.requireNonNull(r7)
            boolean r8 = r10.isStarted()
            boolean r7 = r7.handleIntent(r10, r11, r8)
            if (r6 == 0) goto L188
            if (r7 != 0) goto L140
            com.android.launcher3.logging.UserEventDispatcher r6 = r10.getUserEventDispatcher()
            com.android.launcher3.AbstractFloatingView r4 = com.android.launcher3.AbstractFloatingView.getOpenView(r10, r4)
            if (r4 == 0) goto L86
            r4.logActionCommand(r3)
            goto Lc3
        L86:
            if (r1 == 0) goto Lc3
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r4 = r10.mStateManager
            STATE_TYPE extends com.android.launcher3.statemanager.BaseState<STATE_TYPE> r4 = r4.mState
            com.android.launcher3.LauncherState r4 = (com.android.launcher3.LauncherState) r4
            int r4 = r4.containerType
            int r4 = com.android.launcher3.logging.LoggerUtils.a
            com.android.launcher3.userevent.nano.LauncherLogProto$Target r4 = new com.android.launcher3.userevent.nano.LauncherLogProto$Target
            r4.<init>()
            com.android.launcher3.Workspace r7 = r10.mWorkspace
            r7.getCurrentPage()
            com.android.launcher3.userevent.nano.LauncherLogProto$Target r7 = new com.android.launcher3.userevent.nano.LauncherLogProto$Target
            r7.<init>()
            r6.logActionCommand(r3, r4, r7)
            com.android.launcher3.LauncherState r4 = com.android.launcher3.LauncherState.NORMAL
            boolean r4 = r10.isInState(r4)
            if (r4 == 0) goto Lc3
            boolean r4 = r10.workspaceOnDefaultHomePage()
            if (r4 == 0) goto Lc3
            com.android.launcher3.dragndrop.DragLayer r4 = r10.mDragLayer
            if (r4 == 0) goto Lc3
            b.a.m.u2.g r4 = r4.getGestureActionHandler()
            if (r4 == 0) goto Lc3
            b.c.b.c0 r4 = new b.c.b.c0
            r4.<init>(r10)
            r10.mPostOnResumeRunnable = r4
        Lc3:
            boolean r4 = r10.isStarted()
            com.android.launcher3.AbstractFloatingView.closeAllOpenViews(r10, r4)
            com.android.launcher3.DeviceProfile r4 = r10.mDeviceProfile
            com.android.launcher3.InvariantDeviceProfile r4 = r4.inv
            com.android.launcher3.DeviceBehavior r4 = r4.mBehavior
            boolean r4 = r4.isSplitScreenMode
            com.android.launcher3.tasklayout.TaskLayoutHelper r6 = r10.mTaskLayoutHelper
            boolean r6 = r6.isActivityOpenOnDisplay(r2)
            if (r6 != 0) goto Le6
            com.android.launcher3.tasklayout.TaskLayoutHelper r6 = r10.mTaskLayoutHelper
            r7 = 2
            boolean r6 = r6.isActivityOpenOnDisplay(r7)
            if (r6 == 0) goto Le4
            goto Le6
        Le4:
            r6 = 0
            goto Le7
        Le6:
            r6 = 1
        Le7:
            if (r4 == 0) goto Lfe
            if (r6 == 0) goto Lfe
            com.android.launcher3.LauncherState r4 = com.android.launcher3.LauncherState.OVERVIEW
            boolean r4 = r10.isInState(r4)
            if (r4 != 0) goto Lfc
            com.android.launcher3.LauncherState r4 = com.android.launcher3.LauncherState.SEARCH_RESULT
            boolean r4 = r10.isInState(r4)
            if (r4 != 0) goto Lfc
            goto Lfe
        Lfc:
            r4 = 0
            goto Lff
        Lfe:
            r4 = 1
        Lff:
            com.android.launcher3.LauncherState r6 = com.android.launcher3.LauncherState.NORMAL
            boolean r7 = r10.isInState(r6)
            if (r7 != 0) goto L11c
            com.android.launcher3.allapps.AllAppsContainerView r7 = r10.mAppsView
            if (r7 == 0) goto L11c
            if (r4 == 0) goto L11c
            r7.dismissPopupMenu()
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r4 = r10.mStateManager
            r7 = 0
            com.android.launcher3.Launcher$9 r9 = new com.android.launcher3.Launcher$9
            r9.<init>(r10)
            r4.goToState(r6, r7, r9)
        L11c:
            if (r1 != 0) goto L129
            com.android.launcher3.allapps.AllAppsContainerView r1 = r10.mAppsView
            if (r1 == 0) goto L129
            boolean r4 = r10.isStarted()
            r1.reset(r4)
        L129:
            if (r5 == 0) goto L140
            com.android.launcher3.Workspace r1 = r10.mWorkspace
            boolean r1 = r1.isHandlingTouch()
            if (r1 != 0) goto L140
            com.android.launcher3.Workspace r1 = r10.mWorkspace
            java.util.Objects.requireNonNull(r1)
            b.c.b.e2 r4 = new b.c.b.e2
            r4.<init>(r1)
            r1.post(r4)
        L140:
            com.android.launcher3.logging.UserEventDispatcher r1 = r10.getUserEventDispatcher()
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r4 = r10.mStateManager
            STATE_TYPE extends com.android.launcher3.statemanager.BaseState<STATE_TYPE> r4 = r4.mState
            com.android.launcher3.LauncherState r4 = (com.android.launcher3.LauncherState) r4
            int r4 = r4.containerType
            int r4 = com.android.launcher3.logging.LoggerUtils.a
            com.android.launcher3.userevent.nano.LauncherLogProto$Target r4 = new com.android.launcher3.userevent.nano.LauncherLogProto$Target
            r4.<init>()
            com.android.launcher3.Workspace r5 = r10.mWorkspace
            r5.getCurrentPage()
            com.android.launcher3.userevent.nano.LauncherLogProto$Target r5 = new com.android.launcher3.userevent.nano.LauncherLogProto$Target
            r5.<init>()
            r1.logActionCommand(r3, r4, r5)
            android.view.Window r1 = r10.getWindow()
            android.view.View r1 = r1.peekDecorView()
            if (r1 == 0) goto L177
            android.os.IBinder r4 = r1.getWindowToken()
            if (r4 == 0) goto L177
            android.os.IBinder r1 = r1.getWindowToken()
            androidx.transition.CanvasUtils.hideKeyboardAsync(r10, r1)
        L177:
            com.android.systemui.plugins.shared.LauncherOverlayManager r1 = r10.mOverlayManager
            boolean r4 = r10.isStarted()
            if (r4 == 0) goto L180
            goto L181
        L180:
            r2 = 0
        L181:
            r1.hideOverlay(r2)
            r10.handleGestureContract(r11)
            goto L19b
        L188:
            java.lang.String r11 = r11.getAction()
            java.lang.String r2 = "android.intent.action.ALL_APPS"
            boolean r11 = r2.equals(r11)
            if (r11 == 0) goto L19b
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r11 = r10.mStateManager
            com.android.launcher3.LauncherState r2 = com.android.launcher3.LauncherState.ALL_APPS
            r11.goToState(r2, r1)
        L19b:
            java.lang.String r11 = "End"
            com.android.launcher3.util.TraceHelper.endSection(r0, r11)
            return
    }

    @Override // com.android.launcher3.BaseActivity, com.microsoft.intune.mam.client.app.MAMActivity, com.microsoft.intune.mam.client.app.HookedActivity
    public void onMAMPause() {
            r3 = this;
            r0 = 1
            com.android.launcher3.InstallShortcutReceiver.enableInstallQueue(r0)
            super.onMAMPause()
            com.android.launcher3.compat.AppWidgetManagerCompat r0 = com.android.launcher3.compat.AppWidgetManagerCompat.getInstance(r3)
            boolean r0 = r0.isDraggingWidgetItemOnDuo()
            if (r0 != 0) goto L16
            com.android.launcher3.dragndrop.DragController r0 = r3.mDragController
            r0.cancelDrag()
        L16:
            r0 = -1
            r3.mLastTouchUpTime = r0
            com.android.launcher3.DropTargetBar r0 = r3.mDropTargetBar
            r1 = 0
            r0.animateToVisibility(r1)
            com.android.launcher3.Workspace r0 = r3.mWorkspace
            int r1 = r3.getCurrentWorkspaceScreen()
            int r0 = r0.getScreenIdForPageIndex(r1)
            long r0 = (long) r0
            b.a.m.r2.c r2 = r3.mFeaturePageHost
            r2.o(r0)
            boolean r0 = r3.mDeferOverlayCallbacks
            if (r0 != 0) goto L39
            com.android.systemui.plugins.shared.LauncherOverlayManager r0 = r3.mOverlayManager
            r0.onActivityPaused(r3)
        L39:
            return
    }

    @Override // com.android.launcher3.statemanager.StatefulActivity, com.android.launcher3.BaseActivity, com.microsoft.intune.mam.client.app.MAMActivity, com.microsoft.intune.mam.client.app.HookedActivity
    public void onMAMResume() {
            r6 = this;
            com.android.launcher3.util.TraceHelper r0 = com.android.launcher3.util.TraceHelper.INSTANCE
            java.lang.String r0 = "ON_RESUME"
            android.os.Trace.beginSection(r0)
            super.onMAMResume()
            java.lang.String r1 = "superCall"
            com.android.launcher3.util.TraceHelper.partitionSection(r0, r1)
            android.os.Handler r1 = r6.mHandler
            java.lang.Runnable r2 = r6.mHandleDeferredResume
            r1.removeCallbacks(r2)
            android.os.Handler r1 = r6.mHandler
            java.lang.Runnable r2 = r6.mHandleDeferredResume
            com.android.launcher3.Utilities.postAsyncCallback(r1, r2)
            java.lang.Runnable r1 = r6.mPostOnResumeRunnable
            r2 = 0
            if (r1 == 0) goto L27
            r1.run()
            r6.mPostOnResumeRunnable = r2
        L27:
            b.a.m.w2.k r1 = b.a.m.w2.l.a
            boolean r1 = r1.k(r6)
            r3 = 1
            r4 = 0
            if (r1 == 0) goto L69
            int r1 = com.android.launcher3.InstallShortcutReceiver.sInstallQueueDisabledFlags
            android.content.SharedPreferences r1 = com.android.launcher3.Utilities.getPrefs(r6)
            java.lang.String r5 = "apps_to_install"
            if (r1 == 0) goto L4f
            java.util.Set r1 = r1.getStringSet(r5, r2)
            if (r1 == 0) goto L4a
            boolean r1 = r1.isEmpty()
            if (r1 == 0) goto L48
            goto L4a
        L48:
            r1 = 0
            goto L4b
        L4a:
            r1 = 1
        L4b:
            if (r1 != 0) goto L4f
            r1 = 1
            goto L50
        L4f:
            r1 = 0
        L50:
            if (r1 == 0) goto L6c
            b.a.m.w2.k r1 = b.a.m.w2.l.a
            r1.f(r6)
            android.content.SharedPreferences r1 = com.android.launcher3.Utilities.getPrefs(r6)
            if (r1 == 0) goto L6c
            android.content.SharedPreferences$Editor r1 = r1.edit()
            android.content.SharedPreferences$Editor r1 = r1.remove(r5)
            r1.apply()
            goto L6c
        L69:
            com.android.launcher3.InstallShortcutReceiver.disableAndFlushInstallQueue(r3, r6)
        L6c:
            java.util.ArrayList<com.android.launcher3.Launcher$OnResumeCallback> r1 = r6.mOnResumeCallbacks
            boolean r1 = r1.isEmpty()
            if (r1 != 0) goto L96
            java.util.ArrayList r1 = new java.util.ArrayList
            java.util.ArrayList<com.android.launcher3.Launcher$OnResumeCallback> r2 = r6.mOnResumeCallbacks
            r1.<init>(r2)
            java.util.ArrayList<com.android.launcher3.Launcher$OnResumeCallback> r2 = r6.mOnResumeCallbacks
            r2.clear()
            int r2 = r1.size()
            int r2 = r2 - r3
        L85:
            if (r2 < 0) goto L93
            java.lang.Object r3 = r1.get(r2)
            com.android.launcher3.Launcher$OnResumeCallback r3 = (com.android.launcher3.Launcher.OnResumeCallback) r3
            r3.onLauncherResume()
            int r2 = r2 + (-1)
            goto L85
        L93:
            r1.clear()
        L96:
            java.util.List<com.android.launcher3.BubbleTextView> r1 = r6.mCurrentAnimatedIcons
            java.util.Iterator r1 = r1.iterator()
        L9c:
            boolean r2 = r1.hasNext()
            if (r2 == 0) goto Lac
            java.lang.Object r2 = r1.next()
            com.android.launcher3.BubbleTextView r2 = (com.android.launcher3.BubbleTextView) r2
            r2.iconAnim(r4)
            goto L9c
        Lac:
            java.util.List<com.android.launcher3.BubbleTextView> r1 = r6.mCurrentAnimatedIcons
            r1.clear()
            boolean r1 = r6.mDeferOverlayCallbacks
            if (r1 == 0) goto Lc4
            android.os.Handler r1 = r6.mHandler
            java.lang.Runnable r2 = r6.mDeferredOverlayCallbacks
            r1.removeCallbacks(r2)
            android.os.Handler r1 = r6.mHandler
            java.lang.Runnable r2 = r6.mDeferredOverlayCallbacks
            com.android.launcher3.Utilities.postAsyncCallback(r1, r2)
            goto Lc9
        Lc4:
            com.android.systemui.plugins.shared.LauncherOverlayManager r1 = r6.mOverlayManager
            r1.onActivityResumed(r6)
        Lc9:
            b.a.m.n2.u.a(r6)
            com.android.launcher3.Workspace r1 = r6.mWorkspace
            int r2 = r6.getCurrentWorkspaceScreen()
            int r1 = r1.getScreenIdForPageIndex(r2)
            long r1 = (long) r1
            b.a.m.r2.c r3 = r6.mFeaturePageHost
            if (r3 == 0) goto Lde
            r3.m(r1)
        Lde:
            java.lang.String r1 = "End"
            com.android.launcher3.util.TraceHelper.endSection(r0, r1)
            return
    }

    @Override // com.android.launcher3.BaseDraggingActivity, com.microsoft.intune.mam.client.app.MAMActivity, com.microsoft.intune.mam.client.app.HookedActivity
    public void onMAMSaveInstanceState(android.os.Bundle r4) {
            r3 = this;
            com.android.launcher3.Workspace r0 = r3.mWorkspace
            int r0 = r0.getChildCount()
            if (r0 <= 0) goto L1c
            com.android.launcher3.Workspace r0 = r3.mWorkspace
            int r0 = r0.getNextPage()
            java.lang.String r1 = "launcher.current_screen"
            r4.putInt(r1, r0)
            boolean r0 = r3.isOverlayOpen()
            java.lang.String r1 = "launcher.overlay"
            r4.putInt(r1, r0)
        L1c:
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r0 = r3.mStateManager
            STATE_TYPE extends com.android.launcher3.statemanager.BaseState<STATE_TYPE> r0 = r0.mState
            com.android.launcher3.LauncherState r0 = (com.android.launcher3.LauncherState) r0
            int r0 = r0.ordinal
            java.lang.String r1 = "launcher.state"
            r4.putInt(r1, r0)
            r0 = 16
            com.android.launcher3.AbstractFloatingView r0 = com.android.launcher3.AbstractFloatingView.getOpenView(r3, r0)
            java.lang.String r1 = "launcher.widget_panel"
            if (r0 == 0) goto L3f
            android.util.SparseArray r2 = new android.util.SparseArray
            r2.<init>()
            r0.saveHierarchyState(r2)
            r4.putSparseParcelableArray(r1, r2)
            goto L42
        L3f:
            r4.remove(r1)
        L42:
            r0 = 0
            com.android.launcher3.dragndrop.DragLayer r1 = r3.mDragLayer
            if (r1 != 0) goto L48
            goto L4e
        L48:
            r2 = 114687(0x1bfff, float:1.60711E-40)
            com.android.launcher3.AbstractFloatingView.closeAllOpenViews(r1, r0, r2)
        L4e:
            r3.finishAutoCancelActionMode()
            r3.finishAutoCancelActionMode()
            com.android.launcher3.util.PendingRequestArgs r0 = r3.mPendingRequestArgs
            if (r0 == 0) goto L5d
            java.lang.String r1 = "launcher.request_args"
            r4.putParcelable(r1, r0)
        L5d:
            int r0 = r3.mPendingActivityRequestCode
            java.lang.String r1 = "launcher.request_code"
            r4.putInt(r1, r0)
            com.android.launcher3.util.ActivityResultInfo r0 = r3.mPendingActivityResult
            if (r0 == 0) goto L6d
            java.lang.String r1 = "launcher.activity_result"
            r4.putParcelable(r1, r0)
        L6d:
            super.onMAMSaveInstanceState(r4)
            com.android.systemui.plugins.shared.LauncherOverlayManager r0 = r3.mOverlayManager
            r0.onActivitySaveInstanceState(r3, r4)
            return
    }

    @Override // com.android.launcher3.BaseActivity, com.microsoft.intune.mam.client.app.MAMActivity, com.microsoft.intune.mam.client.app.HookedActivity
    public void onMAMUserLeaveHint() {
            r0 = this;
            super.onMAMUserLeaveHint()
            b.a.m.n2.u.a(r0)
            return
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void onPageBoundSynchronously(int r2) {
            r1 = this;
            r1.mSynchronouslyBoundPage = r2
            com.android.launcher3.Workspace r0 = r1.mWorkspace
            r0.setCurrentPage(r2)
            r2 = -1
            r1.mPageToBindSynchronously = r2
            return
    }

    public void onPluginConnected(com.android.systemui.plugins.OverlayPlugin r2) {
            r1 = this;
            b.c.b.e0 r0 = new b.c.b.e0
            r0.<init>(r1, r2)
            r1.switchOverlay(r0)
            return
    }

    @Override // com.android.systemui.plugins.PluginListener
    public /* bridge */ /* synthetic */ void onPluginConnected(com.android.systemui.plugins.Plugin r1, android.content.Context r2) {
            r0 = this;
            com.android.systemui.plugins.OverlayPlugin r1 = (com.android.systemui.plugins.OverlayPlugin) r1
            r0.onPluginConnected(r1)
            return
    }

    public void onPluginDisconnected() {
            r1 = this;
            b.c.b.d2 r0 = new b.c.b.d2
            r0.<init>(r1)
            r1.switchOverlay(r0)
            return
    }

    @Override // com.android.systemui.plugins.PluginListener
    public /* bridge */ /* synthetic */ void onPluginDisconnected(com.android.systemui.plugins.Plugin r1) {
            r0 = this;
            com.android.systemui.plugins.OverlayPlugin r1 = (com.android.systemui.plugins.OverlayPlugin) r1
            r0.onPluginDisconnected()
            return
    }

    @Override // android.app.Activity, android.view.Window.Callback
    @android.annotation.TargetApi(24)
    public void onProvideKeyboardShortcuts(java.util.List<android.view.KeyboardShortcutGroup> r8, android.view.Menu r9, int r10) {
            r7 = this;
            java.util.ArrayList r0 = new java.util.ArrayList
            r0.<init>()
            com.android.launcher3.LauncherState r1 = com.android.launcher3.LauncherState.NORMAL
            boolean r1 = r7.isInState(r1)
            r2 = 4096(0x1000, float:5.74E-42)
            if (r1 == 0) goto L31
            android.view.KeyboardShortcutInfo r1 = new android.view.KeyboardShortcutInfo
            r3 = 2131821096(0x7f110228, float:1.9274926E38)
            java.lang.String r3 = r7.getString(r3)
            r4 = 29
            r1.<init>(r3, r4, r2)
            r0.add(r1)
            android.view.KeyboardShortcutInfo r1 = new android.view.KeyboardShortcutInfo
            r3 = 2131823771(0x7f110c9b, float:1.9280351E38)
            java.lang.String r3 = r7.getString(r3)
            r4 = 51
            r1.<init>(r3, r4, r2)
            r0.add(r1)
        L31:
            android.view.View r1 = r7.getCurrentFocus()
            if (r1 == 0) goto La7
            int r3 = com.android.launcher3.popup.PopupContainerWithArrow.f7540j
            r3 = 2
            com.android.launcher3.AbstractFloatingView r3 = com.android.launcher3.AbstractFloatingView.getOpenView(r7, r3)
            com.android.launcher3.popup.PopupContainerWithArrow r3 = (com.android.launcher3.popup.PopupContainerWithArrow) r3
            if (r3 == 0) goto L47
            com.android.launcher3.accessibility.LauncherAccessibilityDelegate r3 = r3.getAccessibilityDelegateCompat()
            goto L49
        L47:
            com.android.launcher3.accessibility.LauncherAccessibilityDelegate r3 = r7.mAccessibilityDelegate
        L49:
            java.lang.Object r4 = r1.getTag()
            boolean r4 = r4 instanceof com.android.launcher3.model.data.ItemInfo
            r5 = 1
            if (r4 != 0) goto L55
            java.util.List r3 = java.util.Collections.EMPTY_LIST
            goto L6a
        L55:
            m.i.p.y.b r4 = m.i.p.y.b.s()
            r3.addSupportedActions(r1, r4, r5)
            java.util.ArrayList r3 = new java.util.ArrayList
            java.util.List r6 = r4.c()
            r3.<init>(r6)
            android.view.accessibility.AccessibilityNodeInfo r4 = r4.f14318b
            r4.recycle()
        L6a:
            boolean r3 = r3.isEmpty()
            r3 = r3 ^ r5
            if (r3 == 0) goto L82
            android.view.KeyboardShortcutInfo r3 = new android.view.KeyboardShortcutInfo
            r4 = 2131821632(0x7f110440, float:1.9276013E38)
            java.lang.String r4 = r7.getString(r4)
            r5 = 43
            r3.<init>(r4, r5, r2)
            r0.add(r3)
        L82:
            java.lang.Object r3 = r1.getTag()
            boolean r3 = r3 instanceof com.android.launcher3.model.data.ItemInfo
            if (r3 == 0) goto La7
            java.lang.Object r1 = r1.getTag()
            com.android.launcher3.model.data.ItemInfo r1 = (com.android.launcher3.model.data.ItemInfo) r1
            boolean r1 = androidx.transition.CanvasUtils.supportsShortcuts(r1)
            if (r1 == 0) goto La7
            android.view.KeyboardShortcutInfo r1 = new android.view.KeyboardShortcutInfo
            r3 = 2131823198(0x7f110a5e, float:1.9279189E38)
            java.lang.String r3 = r7.getString(r3)
            r4 = 47
            r1.<init>(r3, r4, r2)
            r0.add(r1)
        La7:
            boolean r1 = r0.isEmpty()
            if (r1 != 0) goto Lbc
            android.view.KeyboardShortcutGroup r1 = new android.view.KeyboardShortcutGroup
            r2 = 2131821916(0x7f11055c, float:1.9276589E38)
            java.lang.String r2 = r7.getString(r2)
            r1.<init>(r2, r0)
            r8.add(r1)
        Lbc:
            super.onProvideKeyboardShortcuts(r8, r9, r10)
            return
    }

    @Override // android.app.Activity
    public void onRequestPermissionsResult(int r6, java.lang.String[] r7, int[] r8) {
            r5 = this;
            com.android.launcher3.util.PendingRequestArgs r7 = r5.mPendingRequestArgs
            r0 = 14
            if (r6 != r0) goto L53
            if (r7 == 0) goto L53
            int r6 = r7.mObjectType
            r1 = 1
            r2 = 0
            if (r6 != r1) goto L11
            int r6 = r7.mArg1
            goto L12
        L11:
            r6 = 0
        L12:
            if (r6 != r0) goto L53
            r6 = 0
            r5.mPendingRequestArgs = r6
            int r0 = r7.container
            int r3 = r7.screenId
            com.android.launcher3.CellLayout r0 = r5.getCellLayout(r0, r3)
            if (r0 == 0) goto L2a
            int r3 = r7.cellX
            int r4 = r7.cellY
            android.view.View r0 = r0.getChildAt(r3, r4)
            goto L2b
        L2a:
            r0 = r6
        L2b:
            android.content.Intent r7 = r7.getPendingIntent()
            int r3 = r8.length
            if (r3 <= 0) goto L3a
            r8 = r8[r2]
            if (r8 != 0) goto L3a
            r5.startActivitySafely(r0, r7, r6)
            goto L53
        L3a:
            r6 = 2131822324(0x7f1106f4, float:1.9277416E38)
            java.lang.Object[] r7 = new java.lang.Object[r1]
            r8 = 2131821670(0x7f110466, float:1.927609E38)
            java.lang.String r8 = r5.getString(r8)
            r7[r2] = r8
            java.lang.String r6 = r5.getString(r6, r7)
            android.widget.Toast r6 = android.widget.Toast.makeText(r5, r6, r2)
            r6.show()
        L53:
            return
    }

    @Override // android.app.Activity
    public void onRestoreInstanceState(android.os.Bundle r2) {
            r1 = this;
            super.onRestoreInstanceState(r2)
            com.android.launcher3.Workspace r2 = r1.mWorkspace
            int r0 = r1.mSynchronouslyBoundPage
            r2.restoreInstanceStateForChild(r0)
            return
    }

    @Override // com.android.launcher3.BaseDraggingActivity, com.android.launcher3.BaseActivity, android.app.Activity
    public void onStart() {
            r2 = this;
            com.android.launcher3.util.TraceHelper r0 = com.android.launcher3.util.TraceHelper.INSTANCE
            java.lang.String r0 = "Launcher.onStart"
            android.os.Trace.beginSection(r0)
            super.onStart()
            boolean r0 = r2.mDeferOverlayCallbacks
            if (r0 != 0) goto L13
            com.android.systemui.plugins.shared.LauncherOverlayManager r0 = r2.mOverlayManager
            r0.onActivityStarted(r2)
        L13:
            com.android.launcher3.LauncherAppWidgetHost r0 = r2.mAppWidgetHost
            r1 = 1
            r0.setListenIfResumed(r1)
            com.android.launcher3.util.TraceHelper r0 = com.android.launcher3.util.TraceHelper.INSTANCE
            android.os.Trace.endSection()
            return
    }

    @Override // com.android.launcher3.statemanager.StatefulActivity
    public void onStateSetEnd(com.android.launcher3.statemanager.BaseState r8) {
            r7 = this;
            com.android.launcher3.LauncherState r8 = (com.android.launcher3.LauncherState) r8
            boolean r0 = r7.mDeferredResumePending
            if (r0 == 0) goto L9
            r7.handleDeferredResume()
        L9:
            com.android.launcher3.LauncherAppWidgetHost r0 = r7.mAppWidgetHost
            com.android.launcher3.LauncherState r1 = com.android.launcher3.LauncherState.NORMAL
            r2 = 1
            r3 = 0
            if (r8 != r1) goto L13
            r4 = 1
            goto L14
        L13:
            r4 = 0
        L14:
            int r5 = r0.mFlags
            r6 = r5 & 2
            if (r6 == 0) goto L1c
            r6 = 1
            goto L1d
        L1c:
            r6 = 0
        L1d:
            if (r4 != r6) goto L20
            goto L35
        L20:
            if (r4 == 0) goto L31
            r4 = r5 | 2
            r0.mFlags = r4
            r5 = r4 & 4
            if (r5 == 0) goto L35
            r4 = r4 & r2
            if (r4 != 0) goto L35
            b.a.m.u4.k.a(r0)
            goto L35
        L31:
            r4 = r5 & (-3)
            r0.mFlags = r4
        L35:
            com.android.launcher3.Workspace r0 = r7.mWorkspace
            int r4 = com.android.launcher3.LauncherState.FLAG_MULTI_PAGE
            boolean r4 = r8.hasFlag(r4)
            r2 = r2 ^ r4
            r0.setClipChildren(r2)
            r7.finishAutoCancelActionMode()
            r0 = 64
            r7.removeActivityFlags(r0)
            android.view.Window r0 = r7.getWindow()
            android.view.View r0 = r0.getDecorView()
            r2 = 32
            r0.sendAccessibilityEvent(r2)
            int r0 = r8.ordinal
            com.android.launcher3.compat.AccessibilityManagerCompat.sendStateEventToTest(r7, r0)
            if (r8 != r1) goto L66
            r8 = 4
            com.android.launcher3.InstallShortcutReceiver.disableAndFlushInstallQueue(r8, r7)
            com.android.launcher3.states.RotationHelper r8 = r7.mRotationHelper
            r8.setCurrentStateRequest(r3)
        L66:
            return
    }

    public void onStateSetStart(com.android.launcher3.LauncherState r4) {
            r3 = this;
            boolean r0 = r3.mDeferredResumePending
            if (r0 == 0) goto L7
            r3.handleDeferredResume()
        L7:
            boolean r0 = r3.mDeferOverlayCallbacks
            if (r0 == 0) goto L19
            android.os.Handler r0 = r3.mHandler
            java.lang.Runnable r1 = r3.mDeferredOverlayCallbacks
            r0.removeCallbacks(r1)
            android.os.Handler r0 = r3.mHandler
            java.lang.Runnable r1 = r3.mDeferredOverlayCallbacks
            com.android.launcher3.Utilities.postAsyncCallback(r0, r1)
        L19:
            r0 = 64
            r3.addActivityFlags(r0)
            int r0 = com.android.launcher3.LauncherState.FLAG_CLOSE_POPUPS
            boolean r0 = r4.hasFlag(r0)
            r1 = 1
            if (r0 == 0) goto L2f
            boolean r0 = r4.hasFlag(r1)
            r0 = r0 ^ r1
            com.android.launcher3.AbstractFloatingView.closeAllOpenViews(r3, r0)
        L2f:
            com.android.launcher3.LauncherState r0 = com.android.launcher3.LauncherState.SPRING_LOADED
            if (r4 != r0) goto L48
            r0 = 4
            com.android.launcher3.InstallShortcutReceiver.enableInstallQueue(r0)
            com.android.launcher3.states.RotationHelper r0 = r3.mRotationHelper
            r2 = 2
            r0.setCurrentStateRequest(r2)
            com.android.launcher3.Workspace r0 = r3.mWorkspace
            r0.showPageIndicatorAtCurrentScroll()
            com.android.launcher3.Workspace r0 = r3.mWorkspace
            r2 = 0
            r0.setClipChildren(r2)
        L48:
            com.android.launcher3.Workspace r0 = r3.mWorkspace
            android.view.View r0 = r0.getPageIndicator()
            com.android.launcher3.pageindicators.AbstractPageIndicator r0 = (com.android.launcher3.pageindicators.AbstractPageIndicator) r0
            int r2 = com.android.launcher3.LauncherState.FLAG_MULTI_PAGE
            boolean r4 = r4.hasFlag(r2)
            r4 = r4 ^ r1
            r0.setShouldAutoHide(r4)
            return
    }

    @Override // com.android.launcher3.statemanager.StatefulActivity
    public /* bridge */ /* synthetic */ void onStateSetStart(com.android.launcher3.statemanager.BaseState r1) {
            r0 = this;
            com.android.launcher3.LauncherState r1 = (com.android.launcher3.LauncherState) r1
            r0.onStateSetStart(r1)
            return
    }

    @Override // com.android.launcher3.statemanager.StatefulActivity, com.android.launcher3.BaseActivity, android.app.Activity
    public void onStop() {
            r2 = this;
            super.onStop()
            boolean r0 = r2.mDeferOverlayCallbacks
            if (r0 == 0) goto Lb
            r2.checkIfOverlayStillDeferred()
            goto L10
        Lb:
            com.android.systemui.plugins.shared.LauncherOverlayManager r0 = r2.mOverlayManager
            r0.onActivityStopped(r2)
        L10:
            com.android.launcher3.LauncherAppWidgetHost r0 = r2.mAppWidgetHost
            r1 = 0
            r0.setListenIfResumed(r1)
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r0 = r2.mStateManager
            r0.moveToRestState()
            b.a.m.n2.u.a(r2)
            r0 = 20
            r2.onTrimMemory(r0)
            return
    }

    @Override // android.app.Activity, android.content.ComponentCallbacks2
    public void onTrimMemory(int r2) {
            r1 = this;
            super.onTrimMemory(r2)
            r0 = 20
            if (r2 < r0) goto L13
            com.android.launcher3.Launcher$ReleaseDbRunnable r2 = new com.android.launcher3.Launcher$ReleaseDbRunnable
            r2.<init>()
            java.lang.String r0 = com.microsoft.launcher.util.threadpool.ThreadPool.a
            com.microsoft.launcher.util.threadpool.ThreadPool$ThreadPriority r0 = com.microsoft.launcher.util.threadpool.ThreadPool.ThreadPriority.Normal
            com.microsoft.launcher.util.threadpool.ThreadPool.b(r2, r0)
        L13:
            return
    }

    @Override // com.android.launcher3.BaseActivity, android.app.Activity, android.view.Window.Callback
    public void onWindowFocusChanged(boolean r1) {
            r0 = this;
            super.onWindowFocusChanged(r1)
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r1 = r0.mStateManager
            com.android.launcher3.Launcher r1 = r1.mLauncher
            b.a.m.n2.u.a(r1)
            return
    }

    public void openOverlay() {
            r2 = this;
            com.android.launcher3.Workspace r0 = r2.mWorkspace
            if (r0 == 0) goto L11
            boolean r0 = r2.isOverlayOpen()
            if (r0 != 0) goto L11
            com.android.launcher3.Workspace r0 = r2.mWorkspace
            r1 = 1065353216(0x3f800000, float:1.0)
            r0.onOverlayScrollChanged(r1)
        L11:
            return
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void preAddApps() {
            r2 = this;
            com.android.launcher3.model.ModelWriter r0 = r2.mModelWriter
            r0.commitDelete()
            r0 = 128(0x80, float:1.8E-43)
            com.android.launcher3.AbstractFloatingView r0 = com.android.launcher3.AbstractFloatingView.getOpenView(r2, r0)
            if (r0 == 0) goto L15
            b.c.b.k0 r1 = new b.c.b.k0
            r1.<init>(r0)
            r0.post(r1)
        L15:
            return
    }

    public void processCoboFolderContents(java.util.List<com.android.launcher3.model.data.WorkspaceItemInfo> r1, android.view.View r2) {
            r0 = this;
            return
    }

    public final void reCreateAppDrawerBehavior() {
            r5 = this;
            com.android.launcher3.allapps.AppDrawerBehavior r0 = r5.mAppDrawerBehavior
            com.android.launcher3.DeviceProfile r1 = r5.mDeviceProfile
            com.android.launcher3.InvariantDeviceProfile r2 = r1.inv
            com.android.launcher3.DeviceBehavior r2 = r2.mBehavior
            if (r2 == 0) goto L4f
            com.android.launcher3.allapps.AllAppsContainerView r3 = r5.mAppsView
            r4 = 1
            if (r3 == 0) goto L4d
            com.android.launcher3.allapps.AppDrawerBehavior r1 = r2.getAppDrawerBehavior(r1)
            r5.mAppDrawerBehavior = r1
            java.util.Objects.requireNonNull(r1)
            if (r0 != 0) goto L1b
            goto L27
        L1b:
            boolean r2 = r0.isTouchOnOtherScreen
            r1.isTouchOnOtherScreen = r2
            boolean r2 = r0.isTouchOnLeftScreen
            r1.isTouchOnLeftScreen = r2
            boolean r2 = r0.isOpenOnLeftScreen
            r1.isOpenOnLeftScreen = r2
        L27:
            com.android.launcher3.tasklayout.TaskLayoutHelper r1 = r5.getTaskLayoutHelper()
            com.android.launcher3.LauncherState r2 = com.android.launcher3.LauncherState.ALL_APPS
            boolean r2 = r5.isInState(r2)
            r3 = 0
            if (r2 != 0) goto L36
            r4 = 0
            goto L3c
        L36:
            boolean r0 = r0.isOpenOnLeftScreen
            if (r0 == 0) goto L3b
            goto L3c
        L3b:
            r4 = 2
        L3c:
            r1.updateOccupiedStatus(r3, r4)
            com.android.launcher3.allapps.AppDrawerBehavior r0 = r5.mAppDrawerBehavior
            r0.setupViews(r5)
            r5.needRecreateAppDrawerBehavior = r3
            com.android.launcher3.allapps.AllAppsTransitionController r0 = r5.mAllAppsController
            r1 = 0
            r0.setScrollRangeDelta(r1)
            goto L4f
        L4d:
            r5.needRecreateAppDrawerBehavior = r4
        L4f:
            return
    }

    public final void reCreateBingSearchBehavior() {
            r5 = this;
            com.android.launcher3.bingsearch.BingSearchBehavior r0 = r5.mBingSearchBehavior
            com.android.launcher3.DeviceProfile r1 = r5.mDeviceProfile
            com.android.launcher3.InvariantDeviceProfile r2 = r1.inv
            com.android.launcher3.DeviceBehavior r2 = r2.mBehavior
            if (r2 == 0) goto L56
            android.view.View r3 = r5.mBingSearchContentContainer
            r4 = 1
            if (r3 == 0) goto L54
            com.android.launcher3.bingsearch.BingSearchBehavior r1 = r2.getBingSearchBehavior(r1)
            r5.mBingSearchBehavior = r1
            boolean r1 = r1.isDualScreenLandscapeBehaviour()
            r2 = 0
            if (r1 == 0) goto L2e
            com.android.launcher3.bingsearch.BingSearchBehavior r0 = r5.mBingSearchBehavior
            r0.isOpenOnLeftScreen = r4
            com.android.launcher3.tasklayout.TaskLayoutHelper r0 = r5.getTaskLayoutHelper()
            com.android.launcher3.LauncherState r1 = com.android.launcher3.LauncherState.SEARCH_RESULT
            boolean r1 = r5.isInState(r1)
            r0.updateOccupiedStatus(r4, r1)
            goto L4c
        L2e:
            com.android.launcher3.bingsearch.BingSearchBehavior r1 = r5.mBingSearchBehavior
            boolean r3 = r0.isOpenOnLeftScreen
            r1.isOpenOnLeftScreen = r3
            com.android.launcher3.tasklayout.TaskLayoutHelper r1 = r5.getTaskLayoutHelper()
            com.android.launcher3.LauncherState r3 = com.android.launcher3.LauncherState.SEARCH_RESULT
            boolean r3 = r5.isInState(r3)
            if (r3 != 0) goto L42
            r0 = 0
            goto L49
        L42:
            boolean r0 = r0.isOpenOnLeftScreen
            if (r0 == 0) goto L48
            r0 = 1
            goto L49
        L48:
            r0 = 2
        L49:
            r1.updateOccupiedStatus(r4, r0)
        L4c:
            com.android.launcher3.bingsearch.BingSearchBehavior r0 = r5.mBingSearchBehavior
            r0.setupViews(r5)
            r5.needRecreateSearchBehavior = r2
            goto L56
        L54:
            r5.needRecreateSearchBehavior = r4
        L56:
            return
    }

    @Override // com.android.launcher3.statemanager.StatefulActivity, com.android.launcher3.BaseDraggingActivity
    public void reapplyUi() {
            r2 = this;
            com.android.launcher3.LauncherRootView r0 = r2.getRootView()
            r0.dispatchInsets()
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r0 = r2.mStateManager
            r1 = 1
            r0.reapplyState(r1)
            return
    }

    @Override // com.android.launcher3.statemanager.StatefulActivity
    public void reapplyUi(boolean r2) {
            r1 = this;
            com.android.launcher3.LauncherRootView r0 = r1.getRootView()
            r0.dispatchInsets()
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r0 = r1.mStateManager
            r0.reapplyState(r2)
            return
    }

    public void rebindModel() {
            r2 = this;
            int r0 = r2.getNextPageForFlip()
            com.android.launcher3.LauncherModel r1 = r2.mModel
            boolean r1 = r1.startLoader(r0)
            if (r1 == 0) goto L14
            com.android.launcher3.Workspace r1 = r2.mWorkspace
            r1.setCurrentPage(r0)
            r0 = 1
            r2.mWorkspaceLoading = r0
        L14:
            return
    }

    public void refreshAndBindWidgetsForPackageUser(com.android.launcher3.util.PackageUserKey r3) {
            r2 = this;
            com.android.launcher3.LauncherModel r0 = r2.mModel
            com.android.launcher3.LauncherModel$7 r1 = new com.android.launcher3.LauncherModel$7
            r1.<init>(r0, r3)
            r0.enqueueModelUpdateTask(r1)
            return
    }

    public void refreshOverviewPanel() {
            r0 = this;
            return
    }

    public boolean removeItem(android.view.View r12, com.android.launcher3.model.data.ItemInfo r13, boolean r14) {
            r11 = this;
            boolean r0 = r13 instanceof com.android.launcher3.model.data.WorkspaceItemInfo
            r1 = 0
            r2 = 1
            if (r0 == 0) goto L90
            com.android.launcher3.Workspace r0 = r11.mWorkspace
            int r3 = r13.container
            android.view.View r0 = r0.getHomescreenIconByItemId(r3)
            boolean r3 = r0 instanceof com.android.launcher3.folder.FolderIcon
            if (r3 == 0) goto L1f
            java.lang.Object r12 = r0.getTag()
            com.android.launcher3.model.data.FolderInfo r12 = (com.android.launcher3.model.data.FolderInfo) r12
            r0 = r13
            com.android.launcher3.model.data.WorkspaceItemInfo r0 = (com.android.launcher3.model.data.WorkspaceItemInfo) r0
            r12.remove(r0, r2)
            goto L24
        L1f:
            com.android.launcher3.Workspace r0 = r11.mWorkspace
            r0.removeWorkspaceItem(r12)
        L24:
            if (r14 == 0) goto L103
            int r12 = r13.itemType
            r14 = 100
            if (r12 != r14) goto L89
            com.android.launcher3.model.ModelWriter r12 = r11.mModelWriter
            java.util.Objects.requireNonNull(r12)
            int r0 = r13.itemType
            if (r0 != r14) goto L81
            boolean r14 = r13.isAvailable()
            if (r14 == 0) goto L75
            com.android.launcher3.AppSetInfo r14 = new com.android.launcher3.AppSetInfo     // Catch: com.android.launcher3.AppSetInfo.AppsetIllegalStateException -> L75
            r0 = r13
            com.android.launcher3.model.data.WorkspaceItemInfo r0 = (com.android.launcher3.model.data.WorkspaceItemInfo) r0     // Catch: com.android.launcher3.AppSetInfo.AppsetIllegalStateException -> L75
            r14.<init>(r0)     // Catch: com.android.launcher3.AppSetInfo.AppsetIllegalStateException -> L75
            b.a.m.g4.j r3 = com.microsoft.launcher.telemetry.TelemetryManager.a     // Catch: com.android.launcher3.AppSetInfo.AppsetIllegalStateException -> L75
            java.lang.String r4 = "AppGroupIcon"
            java.lang.String r5 = "AppGroupPage"
            java.lang.String r6 = ""
            java.lang.String r7 = "Delete"
            java.lang.String r8 = ""
            java.lang.String r9 = "1"
            r0 = 4
            java.lang.String[] r0 = new java.lang.String[r0]     // Catch: com.android.launcher3.AppSetInfo.AppsetIllegalStateException -> L75
            java.lang.String r10 = "pkg1"
            r0[r1] = r10     // Catch: com.android.launcher3.AppSetInfo.AppsetIllegalStateException -> L75
            com.android.launcher3.model.data.WorkspaceItemInfo r1 = r14.mPrimaryShortcut     // Catch: com.android.launcher3.AppSetInfo.AppsetIllegalStateException -> L75
            java.lang.String r1 = r1.getPackageName()     // Catch: com.android.launcher3.AppSetInfo.AppsetIllegalStateException -> L75
            r0[r2] = r1     // Catch: com.android.launcher3.AppSetInfo.AppsetIllegalStateException -> L75
            r1 = 2
            java.lang.String r10 = "pkg2"
            r0[r1] = r10     // Catch: com.android.launcher3.AppSetInfo.AppsetIllegalStateException -> L75
            r1 = 3
            com.android.launcher3.model.data.WorkspaceItemInfo r14 = r14.mSecondaryShortcut     // Catch: com.android.launcher3.AppSetInfo.AppsetIllegalStateException -> L75
            java.lang.String r14 = r14.getPackageName()     // Catch: com.android.launcher3.AppSetInfo.AppsetIllegalStateException -> L75
            r0[r1] = r14     // Catch: com.android.launcher3.AppSetInfo.AppsetIllegalStateException -> L75
            java.lang.String r10 = b.a.m.c4.v8.u(r0)     // Catch: com.android.launcher3.AppSetInfo.AppsetIllegalStateException -> L75
            r3.g(r4, r5, r6, r7, r8, r9, r10)     // Catch: com.android.launcher3.AppSetInfo.AppsetIllegalStateException -> L75
        L75:
            com.android.launcher3.util.LooperExecutor r14 = com.android.launcher3.util.Executors.MODEL_EXECUTOR
            b.c.b.w2.n0 r0 = new b.c.b.w2.n0
            r0.<init>(r12, r13)
            r14.execute(r0)
            goto L103
        L81:
            java.lang.IllegalStateException r12 = new java.lang.IllegalStateException
            java.lang.String r13 = "Item type is not correct"
            r12.<init>(r13)
            throw r12
        L89:
            com.android.launcher3.model.ModelWriter r12 = r11.mModelWriter
            r12.deleteItemFromDatabase(r13)
            goto L103
        L90:
            boolean r0 = r13 instanceof com.android.launcher3.model.data.FolderInfo
            if (r0 == 0) goto Lad
            com.android.launcher3.model.data.FolderInfo r13 = (com.android.launcher3.model.data.FolderInfo) r13
            boolean r0 = r12 instanceof com.android.launcher3.folder.FolderIcon
            if (r0 == 0) goto La0
            r0 = r12
            com.android.launcher3.folder.FolderIcon r0 = (com.android.launcher3.folder.FolderIcon) r0
            r0.removeListeners()
        La0:
            com.android.launcher3.Workspace r0 = r11.mWorkspace
            r0.removeWorkspaceItem(r12)
            if (r14 == 0) goto L103
            com.android.launcher3.model.ModelWriter r12 = r11.mModelWriter
            r12.deleteFolderAndContentsFromDatabase(r13)
            goto L103
        Lad:
            boolean r0 = r13 instanceof com.android.launcher3.model.data.AppInfo
            if (r0 == 0) goto Ld1
            com.android.launcher3.model.data.AppInfo r13 = (com.android.launcher3.model.data.AppInfo) r13
            java.lang.CharSequence r12 = r13.title
            if (r12 == 0) goto Ld0
            android.content.ComponentName r12 = r13.componentName
            if (r12 == 0) goto Ld0
            com.android.launcher3.model.ModelWriter r14 = r11.mModelWriter
            android.os.UserHandle r0 = r13.user
            r1 = -100
            r14.removeEditInfo(r12, r0, r1)
            com.android.launcher3.model.ModelWriter r12 = r11.mModelWriter
            android.content.ComponentName r14 = r13.componentName
            android.os.UserHandle r13 = r13.user
            r0 = -102(0xffffffffffffff9a, float:NaN)
            r12.removeEditInfo(r14, r13, r0)
            goto L103
        Ld0:
            return r1
        Ld1:
            boolean r0 = r13 instanceof com.android.launcher3.model.data.LauncherAppWidgetInfo
            if (r0 == 0) goto Le6
            com.android.launcher3.model.data.LauncherAppWidgetInfo r13 = (com.android.launcher3.model.data.LauncherAppWidgetInfo) r13
            com.android.launcher3.Workspace r0 = r11.mWorkspace
            r0.removeWorkspaceItem(r12)
            if (r14 == 0) goto L103
            com.android.launcher3.model.ModelWriter r12 = r11.mModelWriter
            com.android.launcher3.LauncherAppWidgetHost r14 = r11.mAppWidgetHost
            r12.deleteWidgetInfo(r13, r14)
            goto L103
        Le6:
            boolean r0 = r13 instanceof com.microsoft.launcher.featurepage.FeaturePageInfo
            if (r0 == 0) goto L104
            com.microsoft.launcher.featurepage.FeaturePageInfo r13 = (com.microsoft.launcher.featurepage.FeaturePageInfo) r13
            java.util.Set<java.lang.Integer> r0 = com.microsoft.launcher.featurepage.FeaturePageStateManager.a
            com.microsoft.launcher.featurepage.FeaturePageStateManager r0 = com.microsoft.launcher.featurepage.FeaturePageStateManager.b.a
            int r1 = r13.featurePageId
            r0.e(r1)
            com.android.launcher3.Workspace r0 = r11.mWorkspace
            r0.removeWorkspaceItem(r12)
            if (r14 == 0) goto L103
            b.a.m.r2.c r12 = r11.mFeaturePageHost
            if (r12 == 0) goto L103
            r12.k(r13)
        L103:
            return r2
        L104:
            return r1
    }

    public void removePinnedFeaturePage(int r8) {
            r7 = this;
            b.a.m.r2.c r0 = r7.mFeaturePageHost
            android.util.SparseArray<com.microsoft.launcher.featurepage.FeaturePageHostView> r0 = r0.f4114b
            java.lang.Object r0 = r0.get(r8)
            com.microsoft.launcher.featurepage.FeaturePageHostView r0 = (com.microsoft.launcher.featurepage.FeaturePageHostView) r0
            if (r0 == 0) goto L4a
            java.lang.Object r1 = r0.getTag()
            com.microsoft.launcher.featurepage.FeaturePageInfo r1 = (com.microsoft.launcher.featurepage.FeaturePageInfo) r1
            int r2 = r1.screenId
            com.android.launcher3.Workspace r3 = r7.mWorkspace
            int r3 = r3.getDefaultScreenId()
            r4 = 1
            if (r2 != r3) goto L30
            android.content.res.Resources r8 = r7.getResources()
            r0 = 2131822658(0x7f110842, float:1.9278094E38)
            java.lang.String r8 = r8.getString(r0)
            android.widget.Toast r8 = android.widget.Toast.makeText(r7, r8, r4)
            r8.show()
            return
        L30:
            b.a.m.r2.c r3 = r7.mFeaturePageHost
            long r5 = (long) r2
            r3.o(r5)
            r7.removeItem(r0, r1, r4)
            b.a.m.r2.c r0 = r7.mFeaturePageHost
            android.util.SparseArray<com.microsoft.launcher.featurepage.FeaturePageHostView> r0 = r0.f4114b
            r0.remove(r8)
            com.android.launcher3.Workspace r8 = r7.mWorkspace
            b.c.b.i0 r0 = new b.c.b.i0
            r0.<init>(r7)
            r8.removeScreenWithAnim(r2, r0)
        L4a:
            return
    }

    public void removeTempScreen(boolean r3) {
            r2 = this;
            boolean r0 = r2.alreadyAddedEmptyPage
            if (r0 != 0) goto L5
            return
        L5:
            com.android.launcher3.Workspace r0 = r2.mWorkspace
            r1 = -1000(0xfffffffffffffc18, float:NaN)
            if (r3 == 0) goto L14
            com.android.launcher3.Launcher$6 r3 = new com.android.launcher3.Launcher$6
            r3.<init>(r2)
            r0.removeScreenWithAnim(r1, r3)
            goto L1a
        L14:
            r0.removeScreenWithoutAnim(r1)
            r3 = 0
            r2.alreadyAddedEmptyPage = r3
        L1a:
            return
    }

    public void resetSlideBarPos() {
            r2 = this;
            com.android.launcher3.dragndrop.DragLayer r0 = r2.mDragLayer
            r0.requestLayout()
            r0 = 0
            r2.checkSlideBarDuringDrag(r0, r0)
            com.android.launcher3.dragndrop.DragController r1 = r2.mDragController
            boolean r1 = r1.isDragging()
            if (r1 == 0) goto L15
            r1 = 1
            r2.checkSlideBarDuringDrag(r1, r0)
        L15:
            return
    }

    @Override // com.android.systemui.plugins.shared.LauncherExterns
    public void runOnOverlayHidden(java.lang.Runnable r4) {
            r3 = this;
            com.android.launcher3.Workspace r0 = r3.mWorkspace
            java.lang.Runnable r1 = r0.mOnOverlayHiddenCallback
            if (r1 != 0) goto L9
            r0.mOnOverlayHiddenCallback = r4
            goto L10
        L9:
            b.c.b.z1 r2 = new b.c.b.z1
            r2.<init>(r1, r4)
            r0.mOnOverlayHiddenCallback = r2
        L10:
            boolean r4 = r0.tryRunOverlayCallback()
            if (r4 != 0) goto L2a
            android.view.ViewTreeObserver r4 = r0.getViewTreeObserver()
            if (r4 == 0) goto L2a
            boolean r1 = r4.isAlive()
            if (r1 == 0) goto L2a
            com.android.launcher3.Workspace$8 r1 = new com.android.launcher3.Workspace$8
            r1.<init>(r0, r4)
            r4.addOnWindowFocusChangeListener(r1)
        L2a:
            return
    }

    @Override // com.android.systemui.plugins.shared.LauncherExterns
    public void setLauncherOverlay(com.android.launcher3.Launcher.LauncherOverlay r4) {
            r3 = this;
            if (r4 == 0) goto L14
            com.android.launcher3.Launcher$LauncherOverlayCallbacksImpl r0 = new com.android.launcher3.Launcher$LauncherOverlayCallbacksImpl
            r0.<init>(r3)
            r1 = r4
            b.a.m.p3.o r1 = (b.a.m.p3.o) r1
            com.microsoft.launcher.navigation.NavigationOverlay r1 = r1.a
            b.a.m.p3.b r2 = new b.a.m.p3.b
            r2.<init>(r0)
            r1.setOverlayCallbacks(r2)
        L14:
            com.android.launcher3.Workspace r0 = r3.mWorkspace
            r0.setLauncherOverlay(r4)
            return
    }

    public boolean shouldShowHome() {
            r1 = this;
            r0 = 1
            return r0
    }

    public void showSlideBarFromTempHide() {
            r2 = this;
            boolean r0 = r2.isSlideBarTempHide
            if (r0 != 0) goto L5
            return
        L5:
            r0 = 0
            r2.isSlideBarTempHide = r0
            com.microsoft.launcher.slidebar.SlideBarDropTarget r1 = r2.mTopSlideBar
            if (r1 == 0) goto L43
            com.microsoft.launcher.slidebar.SlideBarDropTarget r1 = r2.mBottomSlideBar
            if (r1 == 0) goto L43
            com.microsoft.launcher.slidebar.SlideBarDropTarget r1 = r2.mLeftSlideBar
            if (r1 == 0) goto L43
            com.microsoft.launcher.slidebar.SlideBarDropTarget r1 = r2.mRightSlideBar
            if (r1 != 0) goto L19
            goto L43
        L19:
            com.android.launcher3.Workspace r1 = r2.mWorkspace
            boolean r1 = r1.shouldScrollVertically()
            if (r1 == 0) goto L31
            com.microsoft.launcher.slidebar.SlideBarDropTarget r1 = r2.mTopSlideBar
            boolean r1 = r2.checkSlidebarShow(r1)
            if (r1 == 0) goto L2e
            com.microsoft.launcher.slidebar.SlideBarDropTarget r1 = r2.mTopSlideBar
            r1.setVisibility(r0)
        L2e:
            com.microsoft.launcher.slidebar.SlideBarDropTarget r1 = r2.mBottomSlideBar
            goto L40
        L31:
            com.microsoft.launcher.slidebar.SlideBarDropTarget r1 = r2.mTopSlideBar
            boolean r1 = r2.checkSlidebarShow(r1)
            if (r1 == 0) goto L3e
            com.microsoft.launcher.slidebar.SlideBarDropTarget r1 = r2.mLeftSlideBar
            r1.setVisibility(r0)
        L3e:
            com.microsoft.launcher.slidebar.SlideBarDropTarget r1 = r2.mRightSlideBar
        L40:
            r1.setVisibility(r0)
        L43:
            return
    }

    @Override // com.microsoft.intune.mam.client.app.MAMActivity, android.app.Activity
    public void startActivityForResult(android.content.Intent r2, int r3, android.os.Bundle r4) {
            r1 = this;
            r0 = -1
            if (r3 == r0) goto L5
            r1.mPendingActivityRequestCode = r3
        L5:
            super.startActivityForResult(r2, r3, r4)
            return
    }

    @Override // com.android.launcher3.model.BgDataModel.Callbacks
    public void startBinding() {
            r4 = this;
            com.android.launcher3.util.TraceHelper r0 = com.android.launcher3.util.TraceHelper.INSTANCE
            java.lang.String r0 = "startBinding"
            com.android.launcher3.util.TraceHelper.beginSection(r0)
            int r1 = com.android.launcher3.AbstractFloatingView.a
            com.android.launcher3.views.BaseDragLayer r1 = r4.getDragLayer()
            r2 = 1
            if (r1 != 0) goto L11
            goto L16
        L11:
            r3 = 3466(0xd8a, float:4.857E-42)
            com.android.launcher3.AbstractFloatingView.closeAllOpenViews(r1, r2, r3)
        L16:
            r4.mWorkspaceLoading = r2
            com.android.launcher3.dragndrop.DragController r1 = r4.mDragController
            r1.cancelDrag()
            com.android.launcher3.Workspace r1 = r4.mWorkspace
            com.android.launcher3.Workspace$18 r2 = new com.android.launcher3.Workspace$18
            r2.<init>(r1)
            r1.mapOverItems(r2)
            com.android.launcher3.Workspace r1 = r4.mWorkspace
            r2 = 0
            r1.setLayoutTransition(r2)
            r2 = 2131298262(0x7f0907d6, float:1.8214492E38)
            android.view.View r2 = r1.findViewById(r2)
            if (r2 == 0) goto L3f
            android.view.ViewParent r3 = r2.getParent()
            android.view.ViewGroup r3 = (android.view.ViewGroup) r3
            r3.removeView(r2)
        L3f:
            com.android.launcher3.Workspace$15 r2 = new com.android.launcher3.Workspace$15
            r2.<init>(r1)
            r1.mapOverItems(r2)
            r1.removeAllViews()
            com.android.launcher3.util.IntArrayCompat r2 = r1.mScreenOrder
            r3 = 0
            r2.mSize = r3
            com.android.launcher3.util.IntSparseArrayMap<com.android.launcher3.CellLayout> r2 = r1.mWorkspaceScreens
            r2.clear()
            com.android.launcher3.Launcher r2 = r1.mLauncher
            android.os.Handler r2 = r2.mHandler
            java.lang.Class<com.android.launcher3.Workspace$DeferredWidgetRefresh> r3 = com.android.launcher3.Workspace.DeferredWidgetRefresh.class
            r2.removeCallbacksAndMessages(r3)
            r1.bindAndInitFirstWorkspaceScreen()
            android.animation.LayoutTransition r2 = r1.mLayoutTransition
            r1.setLayoutTransition(r2)
            com.android.launcher3.LauncherAppWidgetHost r1 = r4.mAppWidgetHost
            r1.clearViews()
            com.android.launcher3.Hotseat r1 = r4.mHotseat
            if (r1 == 0) goto L77
            com.android.launcher3.DeviceProfile r2 = r4.mDeviceProfile
            boolean r2 = r2.isVerticalBarLayout()
            r1.resetLayout(r2)
        L77:
            java.lang.String r1 = "End"
            com.android.launcher3.util.TraceHelper.endSection(r0, r1)
            return
    }

    @Override // android.app.Activity
    public void startIntentSenderForResult(android.content.IntentSender r2, int r3, android.content.Intent r4, int r5, int r6, int r7, android.os.Bundle r8) {
            r1 = this;
            r0 = -1
            if (r3 == r0) goto L5
            r1.mPendingActivityRequestCode = r3
        L5:
            super.startIntentSenderForResult(r2, r3, r4, r5, r6, r7, r8)     // Catch: android.content.IntentSender.SendIntentException -> L9
            return
        L9:
            android.content.ActivityNotFoundException r2 = new android.content.ActivityNotFoundException
            r2.<init>()
            throw r2
    }

    @Override // android.app.Activity
    public void startSearch(java.lang.String r2, boolean r3, android.os.Bundle r4, boolean r5) {
            r1 = this;
            if (r4 != 0) goto Le
            android.os.Bundle r4 = new android.os.Bundle
            r4.<init>()
            java.lang.String r5 = "source"
            java.lang.String r0 = "launcher-search"
            r4.putString(r5, r0)
        Le:
            r5 = 1
            super.startSearch(r2, r3, r4, r5)
            com.android.launcher3.statemanager.StateManager<com.android.launcher3.LauncherState> r2 = r1.mStateManager
            com.android.launcher3.LauncherState r3 = com.android.launcher3.LauncherState.NORMAL
            r2.goToState(r3)
            return
    }

    public final void switchOverlay(com.android.launcher3.function.Supplier<com.android.systemui.plugins.shared.LauncherOverlayManager> r2) {
            r1 = this;
            com.android.systemui.plugins.shared.LauncherOverlayManager r0 = r1.mOverlayManager
            if (r0 == 0) goto L7
            r0.onActivityDestroyed(r1)
        L7:
            java.lang.Object r2 = r2.get()
            com.android.systemui.plugins.shared.LauncherOverlayManager r2 = (com.android.systemui.plugins.shared.LauncherOverlayManager) r2
            r1.mOverlayManager = r2
            com.android.launcher3.LauncherRootView r2 = r1.getRootView()
            boolean r2 = r2.isAttachedToWindow()
            if (r2 == 0) goto L1e
            com.android.systemui.plugins.shared.LauncherOverlayManager r2 = r1.mOverlayManager
            r2.onAttachedToWindow()
        L1e:
            r2 = 1
            r1.mDeferOverlayCallbacks = r2
            r1.checkIfOverlayStillDeferred()
            return
    }

    public void tempHideSlideBar() {
            r2 = this;
            boolean r0 = r2.isSlideBarTempHide
            if (r0 == 0) goto L5
            return
        L5:
            r0 = 1
            r2.isSlideBarTempHide = r0
            com.microsoft.launcher.slidebar.SlideBarDropTarget r0 = r2.mTopSlideBar
            if (r0 == 0) goto L58
            com.microsoft.launcher.slidebar.SlideBarDropTarget r0 = r2.mBottomSlideBar
            if (r0 == 0) goto L58
            com.microsoft.launcher.slidebar.SlideBarDropTarget r0 = r2.mLeftSlideBar
            if (r0 == 0) goto L58
            com.microsoft.launcher.slidebar.SlideBarDropTarget r0 = r2.mRightSlideBar
            if (r0 != 0) goto L19
            goto L58
        L19:
            com.android.launcher3.Workspace r0 = r2.mWorkspace
            boolean r0 = r0.shouldScrollVertically()
            r1 = 8
            if (r0 == 0) goto L40
            com.microsoft.launcher.slidebar.SlideBarDropTarget r0 = r2.mTopSlideBar
            r0.setVisibility(r1)
            com.microsoft.launcher.slidebar.SlideBarDropTarget r0 = r2.mBottomSlideBar
            r0.setVisibility(r1)
            com.android.launcher3.dragndrop.DragController r0 = r2.mDragController
            com.microsoft.launcher.slidebar.SlideBarDropTarget r1 = r2.mTopSlideBar
            java.util.ArrayList<com.android.launcher3.DropTarget> r0 = r0.mDropTargets
            r0.remove(r1)
            com.android.launcher3.dragndrop.DragController r0 = r2.mDragController
            com.microsoft.launcher.slidebar.SlideBarDropTarget r1 = r2.mBottomSlideBar
        L3a:
            java.util.ArrayList<com.android.launcher3.DropTarget> r0 = r0.mDropTargets
            r0.remove(r1)
            goto L58
        L40:
            com.microsoft.launcher.slidebar.SlideBarDropTarget r0 = r2.mLeftSlideBar
            r0.setVisibility(r1)
            com.microsoft.launcher.slidebar.SlideBarDropTarget r0 = r2.mRightSlideBar
            r0.setVisibility(r1)
            com.android.launcher3.dragndrop.DragController r0 = r2.mDragController
            com.microsoft.launcher.slidebar.SlideBarDropTarget r1 = r2.mLeftSlideBar
            java.util.ArrayList<com.android.launcher3.DropTarget> r0 = r0.mDropTargets
            r0.remove(r1)
            com.android.launcher3.dragndrop.DragController r0 = r2.mDragController
            com.microsoft.launcher.slidebar.SlideBarDropTarget r1 = r2.mRightSlideBar
            goto L3a
        L58:
            return
    }

    public void updateBlur(boolean r1) {
            r0 = this;
            return
    }

    public void updateBlur(boolean r1, int r2) {
            r0 = this;
            return
    }

    public void updateFeedShortcutInOverview() {
            r0 = this;
            return
    }

    public void updateFolderMode(boolean r1, boolean r2) {
            r0 = this;
            return
    }

    public void updateNotificationDots(com.android.launcher3.function.Predicate<com.android.launcher3.util.PackageUserKey> r2) {
            r1 = this;
            com.android.launcher3.Workspace r0 = r1.mWorkspace
            r0.updateNotificationDots(r2)
            com.android.launcher3.allapps.AllAppsContainerView r0 = r1.mAppsView
            com.android.launcher3.allapps.AllAppsStore r0 = r0.getAppsStore()
            r0.updateNotificationDots(r2)
            return
    }

    public void useFadeOutAnimationForLauncherStart() {
            r0 = this;
            return
    }

    public boolean workspaceOnDefaultHomePage() {
            r3 = this;
            com.android.launcher3.Workspace r0 = r3.mWorkspace
            int r0 = r0.getCurrentPage()
            com.android.launcher3.Workspace r1 = r3.mWorkspace
            int r2 = r1.getDefaultScreenId()
            int r1 = r1.getPageIndexForScreenId(r2)
            if (r0 != r1) goto L14
            r0 = 1
            goto L15
        L14:
            r0 = 0
        L15:
            return r0
    }
}
