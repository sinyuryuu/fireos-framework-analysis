# Phase 5X route-surface summary

- HOME resolver raw result: `priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
com.amazon.firelauncher/.Launcher`
- Runtime summary: `HOME=priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
com.amazon.firelauncher/.Launcher; kernel_aee_threads=2; userspace_aee_lines=0; aee_node_lines=5; aee_access=/dev/aed0 read=0 write=0
/dev/aed1 read=0 write=0
/dev/atf_log read=0 write=0; apex_packages=0; apex_property=EMPTY`
- AEE kernel-thread observations: 2
- AEE userspace candidate lines: 0
- AEE node metadata lines: 5
- APEX package lines: 0
- APEX property: `EMPTY`
- APEX path output: `EMPTY`
- APEX service stderr: `cmd: Can't find service: apexservice`

This is a host-only, read-only derivation. It does not prove exploitability or patch status and does not open a device node or run a payload.
