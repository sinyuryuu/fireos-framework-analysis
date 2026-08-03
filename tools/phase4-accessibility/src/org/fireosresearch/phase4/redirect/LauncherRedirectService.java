package org.fireosresearch.phase4.redirect;

import android.accessibilityservice.AccessibilityService;
import android.app.PendingIntent;
import android.content.ComponentName;
import android.content.Intent;
import android.os.SystemClock;
import android.util.Log;
import android.view.accessibility.AccessibilityEvent;

public final class LauncherRedirectService extends AccessibilityService {
    private static final String TAG = "Phase4Redirect";
    private static final String FIRE_PACKAGE = "com.amazon.firelauncher";
    private static final String TARGET_PACKAGE = "org.fireosresearch.phase4.alias";
    private static final String TARGET_CLASS =
            "org.fireosresearch.phase4.alias.HomeActivity";
    private static final long COOLDOWN_MS = 1500L;
    private static final int REDIRECT_REQUEST_CODE = 0;
    private long lastLaunch;

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        android.accessibilityservice.AccessibilityServiceInfo info = getServiceInfo();
        if (info != null) {
            info.eventTypes = AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED;
            info.feedbackType = android.accessibilityservice.AccessibilityServiceInfo.FEEDBACK_GENERIC;
            info.notificationTimeout = 250;
            info.flags = android.accessibilityservice.AccessibilityServiceInfo.DEFAULT;
            setServiceInfo(info);
        }
        Log.i(TAG, "service connected; manual toggle still required");
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (event == null || event.getEventType() != AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) {
            return;
        }
        CharSequence packageName = event.getPackageName();
        if (packageName == null || !FIRE_PACKAGE.contentEquals(packageName)) {
            return;
        }
        if (!getSharedPreferences(ControlActivity.PREFS, MODE_PRIVATE)
                .getBoolean(ControlActivity.ENABLED, false)) {
            return;
        }
        long now = SystemClock.uptimeMillis();
        if (now - lastLaunch < COOLDOWN_MS) {
            return;
        }
        lastLaunch = now;
        Intent intent = new Intent(Intent.ACTION_MAIN);
        intent.addCategory(Intent.CATEGORY_LAUNCHER);
        intent.setComponent(new ComponentName(TARGET_PACKAGE, TARGET_CLASS));
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK
                | Intent.FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS
                | Intent.FLAG_ACTIVITY_CLEAR_TOP
                | Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
        try {
            // Android 9-compatible public API. The PendingIntent is explicit and
            // targets only the research activity; it does not change HOME state.
            PendingIntent pendingIntent = PendingIntent.getActivity(
                    this, REDIRECT_REQUEST_CODE, intent, 0);
            pendingIntent.send();
            Log.i(TAG, "pending-intent redirect dispatched after Fire foreground event");
        } catch (PendingIntent.CanceledException error) {
            Log.w(TAG, "redirect PendingIntent was canceled", error);
        } catch (RuntimeException error) {
            Log.w(TAG, "redirect target unavailable", error);
        }
    }

    @Override
    public void onInterrupt() {
        Log.i(TAG, "service interrupted");
    }
}
