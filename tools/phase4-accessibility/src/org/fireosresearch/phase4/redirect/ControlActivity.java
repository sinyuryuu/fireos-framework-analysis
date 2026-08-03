package org.fireosresearch.phase4.redirect;

import android.app.Activity;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.CompoundButton;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.ToggleButton;

public final class ControlActivity extends Activity {
    static final String PREFS = "phase4_redirect";
    static final String ENABLED = "redirect_enabled";

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setGravity(Gravity.CENTER);
        TextView text = new TextView(this);
        text.setGravity(Gravity.CENTER);
        text.setText("Phase 4 redirect\n"
                + "Manual Accessibility consent required.\n"
                + "No window text or input is read.\n"
                + "Turn this off before rollback.");
        ToggleButton toggle = new ToggleButton(this);
        toggle.setTextOn("Redirect enabled");
        toggle.setTextOff("Redirect stopped");
        toggle.setChecked(getSharedPreferences(PREFS, MODE_PRIVATE).getBoolean(ENABLED, false));
        toggle.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton button, boolean checked) {
                getSharedPreferences(PREFS, MODE_PRIVATE).edit()
                        .putBoolean(ENABLED, checked).apply();
            }
        });
        layout.addView(text);
        layout.addView(toggle);
        setContentView(layout);
    }
}
