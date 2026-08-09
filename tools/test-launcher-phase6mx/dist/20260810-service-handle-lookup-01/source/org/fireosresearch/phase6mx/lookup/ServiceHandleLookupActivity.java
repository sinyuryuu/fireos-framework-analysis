package org.fireosresearch.phase6mx.lookup;

import android.app.Activity;
import android.os.Bundle;
import android.os.IBinder;
import android.os.Process;
import android.util.Log;
import android.view.Gravity;
import android.widget.TextView;

import java.lang.reflect.Method;

/**
 * Read-only service-manager probe.
 *
 * This class deliberately does not import Parcel, does not call IBinder
 * transact(), and does not invoke any Amazon Binder method.  It only asks the
 * framework ServiceManager whether a named handle is returned.
 */
public final class ServiceHandleLookupActivity extends Activity {
    private static final String TAG = "Phase6MX";
    private static final String[] SERVICES = {
            "amazonpackagemanager",
            "amazonusermanagerservice",
            "amazonprofileservice"
    };

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        StringBuilder report = new StringBuilder();
        append(report, "uid=" + Process.myUid());
        try {
            Class<?> serviceManager = Class.forName("android.os.ServiceManager");
            Method getService = serviceManager.getDeclaredMethod("getService", String.class);
            getService.setAccessible(true);
            for (String service : SERVICES) {
                try {
                    Object value = getService.invoke(null, service);
                    append(report, "service=" + service + " handle=" + (value instanceof IBinder));
                } catch (Throwable error) {
                    append(report, "service=" + service + " error=" + error.getClass().getName());
                }
            }
        } catch (Throwable error) {
            append(report, "lookup_api_error=" + error.getClass().getName());
        }
        TextView view = new TextView(this);
        view.setGravity(Gravity.CENTER);
        view.setTextSize(16.0f);
        view.setText(report.toString());
        setContentView(view);
    }

    private static void append(StringBuilder report, String line) {
        report.append(line).append('\n');
        Log.i(TAG, line);
    }
}
