# Alexa mode read-only probe

- Serial: `G001LT0511550CFT`
- Collected at (UTC): `2026-08-03T03:48:41Z`
- Hard command failures: `0`
- Finding status: `Hypothesis` until the raw outputs and framework code are reviewed.

## Commands and outputs

- [Command manifest](command_manifest.tsv)
- [Service list](service_list.txt)
- [dumpsys alexa_modeswitch](dumpsys_alexa_modeswitch.txt)
- [secure mss_mode](secure_mss_mode.txt)
- [Binder transaction 2 getMode probe](service_call_get_mode.txt)
- [SHA-256 manifest](sha256sums.txt)

This probe is observational only. Transaction 2 is identified as getMode() in the extracted IAlexaModeSwitchService proxy; a shell error is retained as evidence of service observability, not treated as a mode value.
