# Phase 3B HOME path observation

- Test ID: `HOME-PATH-KEYEVENT-02`
- Serial: `G001LT0511550CFT`
- Mode: `keyevent`
- Device mutations: logcat buffer clear and foreground HOME action only.
- Package/settings/policy/overlay/partition writes: none.
- Final foreground restoration: `input keyevent 3`.
- Raw stdout/stderr, exit codes, dumps, and full logcat are preserved.
