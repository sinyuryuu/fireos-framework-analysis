package org.fireosresearch.phase4.alias;

import android.app.Activity;
import android.os.Bundle;

public final class HomeActivity extends Activity {
    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        ProbeActivity.show(this, "HomeActivity");
    }
}
