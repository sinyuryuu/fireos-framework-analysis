# PS7331 `/init` extended policy branch window

Host-only `objdump` extraction; the ELF was not executed.

## Static observations

- **已證實：** the rootable candidate call site at `0x41ae44` sets `w5=1`
  before calling the common helper candidate at `0x41be00`.
- **已證實：** the standard candidate call site at `0x41af80` sets `w5=0`
  before calling the same helper candidate.
- **已證實：** `0x41be48` branches on `w5` to `0x41c30c`; this upgrades the
  result from a string/path observation to an instruction-level split.
- **待驗證：** the branch's high-level meaning, whether it selects a
  rootable policy, and whether the stock boot reaches that path.

No boot property, policy, partition, kernel memory, or privilege state was
changed.
