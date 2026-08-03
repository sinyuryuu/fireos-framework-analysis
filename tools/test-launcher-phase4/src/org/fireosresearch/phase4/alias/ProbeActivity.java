package org.fireosresearch.phase4.alias;

import android.app.Activity;
import android.view.Gravity;
import android.widget.TextView;

final class ProbeActivity {
    private ProbeActivity() {}

    static void show(Activity activity, String label) {
        TextView view = new TextView(activity);
        view.setGravity(Gravity.CENTER);
        view.setTextSize(18.0f);
        view.setText("Phase 4 alias/filter probe\n"
                + "label=" + label + "\n"
                + "package=" + activity.getPackageName() + "\n"
                + "component=" + activity.getComponentName().flattenToShortString());
        activity.setContentView(view);
    }
}
