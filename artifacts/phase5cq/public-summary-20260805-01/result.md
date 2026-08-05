# PHASE5CQ-ACCESSIBILITY-PENDINGINTENT-PS7331-T01 measurement

- Iterations: 20
- Input: KEYCODE_HOME after each launch of the test probe.
- Fire Launcher was not stopped, disabled, hidden, suspended, uninstalled, or cleared.
- No Settings provider write and no unknown Binder call was executed.
- measure/summary.tsv records whether the alias package was observed in the foreground dump.
- This is a foreground redirect measurement, not a HOME resolver replacement measurement.

Before rollback, manually disable the redirect service in Android Settings and
turn off the visible toggle. Then run the documented rollback command.
