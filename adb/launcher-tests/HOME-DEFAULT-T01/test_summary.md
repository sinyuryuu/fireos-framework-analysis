# HOME activity test summary

- Test ID: `HOME-DEFAULT-T01`
- Serial: `G001LT0511550CFT`
- User: `0`
- Target: `com.microsoft.launcher/.Launcher`
- Restore target: `com.amazon.firelauncher/.Launcher`
- `set-home-activity` target exit status: `0`
- `set-home-activity` restore exit status: `0`
- Causal finding: `Hypothesis` until before/after/final resolver states are reviewed.

The final resolver state is authoritative for whether the requested restore completed; command success alone is insufficient.
