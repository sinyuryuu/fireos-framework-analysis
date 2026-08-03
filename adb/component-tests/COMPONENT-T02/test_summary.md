# Component disable test summary

- Serial: `G001LT0511550CFT`
- Component: `com.amazon.firelauncher/com.amazon.firelauncher.Launcher`
- Package: `com.amazon.firelauncher`
- User: `0`
- Disable exit status: `255`
- Home while component state changed exit status: `0`
- Restore exit status: `SKIPPED_DISABLE_REJECTED`
- Home after restore exit status: `0`
- Causal finding: `Hypothesis` until raw state and command outputs are reviewed.

## Evidence

- [Command manifest](command_manifest.tsv)
- [State focus lines](state_focus_lines.txt)
- [SHA-256 manifest](sha256sums.txt)

The final snapshot must be compared with the before snapshot before reporting restoration as successful.
