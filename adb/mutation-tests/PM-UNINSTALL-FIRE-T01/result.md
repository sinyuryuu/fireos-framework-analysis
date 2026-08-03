# PM-UNINSTALL-FIRE-T01

- Test ID: `PM-UNINSTALL-FIRE-T01`
- Target: `com.amazon.firelauncher`, user 0
- Command: `adb -s G001LT0511550CFT shell pm uninstall --user 0 com.amazon.firelauncher`
- Result: `Failure [DELETE_FAILED_INTERNAL_ERROR]`, exit code `1`.
- Log evidence: `PackageManager: Attempted to delete protected package: com.amazon.firelauncher`.
- State after: package remained installed, visible, unsuspended and enabled-default; HOME and foreground remained Fire Launcher.
- Rollback command: `adb -s G001LT0511550CFT shell pm install-existing --user 0 com.amazon.firelauncher`.
- Rollback probe: returned `Package com.amazon.firelauncher installed for user: 0`; it was already present because uninstall was rejected.
- Confidence: Confirmed for this build and shell caller.
