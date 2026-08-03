# Package disable test summary

- Serial: `G001LT0511550CFT`
- Package: `com.amazon.firelauncher`
- User: `0`
- `pm disable-user` exit status: `255`
- `pm default-state` restore exit status: `255`
- Causal finding: `Hypothesis` until the command output and state snapshots are reviewed.

## Evidence

- [Command manifest](command_manifest.tsv)
- [State focus lines](state_focus_lines.txt)
- [SHA-256 manifest](sha256sums.txt)

The final snapshot must be compared with the pre-test snapshot before reporting restoration as successful.
