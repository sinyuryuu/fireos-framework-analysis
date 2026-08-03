# mtkclient command safety review

## Classification

- Host-only `mtk.py devices` source/help inspection: read-only.
- BROM/preloader connection: Level 3 boundary; not executed.
- `printgpt`, `r`, `dumppreloader`, and `dumpbrom`: not automatically safe;
  initialization may require a preloader handshake, crash, payload, DA, auth,
  or register operation.
- `seccfg`, `w`, `wl`, `wf`, `wo`, `e`, `ess`, `da poke`, and similar paths:
  explicit write/erase or lock-state mutation; rejected without a separate
  exact operation report and approval.

## Result for this device

The public MT8183-family configuration is now a meaningful lead, but the
available source does not expose a guaranteed passive BROM identity command
that avoids the preloader/payload boundary. The exact Amazon `trona` PS7330
preloader, DA/auth policy, and recovery path are still unknown.

No mtkclient package was installed or executed. No device-side operation was
performed.
