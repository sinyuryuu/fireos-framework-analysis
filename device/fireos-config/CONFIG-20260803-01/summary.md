# Fire OS configuration/runtime mapping collection

- Run ID: `CONFIG-20260803-01`
- Serial: `G001LT0511550CFT`
- Collected at (UTC): `2026-08-03T01:03:39Z`
- Hard command failures: `0`
- All observations remain raw until manually correlated with bytecode.

## Intended configuration roots

The Fire OS bytecode calls `Environment.getFireOsDirectory()` and appends `/etc/permissions` and `/etc/init`; this run records candidate resolved paths without assuming the result.
