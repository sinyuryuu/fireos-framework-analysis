package org.fireosresearch.home;

import android.app.Activity;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.TextView;

/** A foreground-only HOME probe with no external dependencies. */
public final class HomeActivity extends Activity {
    private static final String PRIORITY_META_DATA =
            "org.fireosresearch.home.PRIORITY";

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);

        int priority = -1;
        if (getApplicationInfo().metaData != null) {
            priority = getApplicationInfo().metaData.getInt(PRIORITY_META_DATA, -1);
        }

        TextView view = new TextView(this);
        view.setGravity(Gravity.CENTER);
        view.setTextSize(20.0f);
        view.setText("Phase 3A HOME probe\n"
                + "package=" + getPackageName() + "\n"
                + "priority=" + priority);
        setContentView(view);
    }
}
