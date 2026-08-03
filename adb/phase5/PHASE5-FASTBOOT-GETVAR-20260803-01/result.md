# Phase 5 fastboot getvar evidence

## Confirmed observations

- `getvar product` returned `product: trona`.
- `getvar unlocked`, `getvar secure`, and `getvar all` were rejected by the
  bootloader with: `the command you input is restricted on locked hw`.
- The fastboot host command itself returned exit code 0 for each query, but the
  remote failures must not be interpreted as successful variable reads.
- The device remained enumerated as `G001LT0511550CFT` in fastboot after all
  four queries.

## Evidence-based interpretation

- **Confirmed:** the fastboot product identity is `trona`.
- **Confirmed:** the bootloader applies a locked-hardware restriction to these
  variable queries.
- **Strong evidence:** the current fastboot interface does not expose the
  requested unlock/secure/all metadata to this host while in the present locked
  state.
- **Unknown:** the literal values of `unlocked` and `secure`; no value was
  returned.
- **Not tested:** unlock, OEM commands, partition writes, erase/format, or MTK
  BROM/preloader access.

## Stop boundary

No write or unlock command was attempted after the remote restriction. The next
low-level options require a new compatibility and risk review; this evidence
does not justify trying arbitrary OEM commands or an MTK loader.
