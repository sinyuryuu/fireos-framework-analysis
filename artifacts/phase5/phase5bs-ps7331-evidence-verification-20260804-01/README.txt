Phase 5BS — PS7331 GhostLock evidence verification

This directory verifies preserved PS7331 source and sanitized Image-analysis
results. It reads hashes, JSON summaries, and semantic marker CSV data only.
It never executes an ELF or kernel Image, contacts ADB, calculates runtime
addresses, produces offsets, or creates a reproducer/payload.

Verdict
-------
The official PS7331 boot image hash matches the preserved input, the exact
mt8183/4.4 source is classified pre-fix, and the preserved inspected Image
patterns are consistent with that pre-fix source. Runtime exploitability and
root/privilege gain remain unproven.
