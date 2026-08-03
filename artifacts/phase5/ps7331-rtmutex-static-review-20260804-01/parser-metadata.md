# PS7331 static parser provenance

This is host-only provenance for the address-sanitized PS7331 `rtmutex` review.
The reconstructed ELF and raw disassembly are intentionally not stored in this
repository. No ELF was executed.

| Item | Value |
|---|---|
| Input decompressed Image SHA-256 | `10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d` |
| PS7331 boot image SHA-256 | `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` |
| Reconstructed ELF SHA-256 | `fd9424539a6e005a948f713965c09a3a61996be6481ca1fb7e83469b60e3dc49` |
| `vmlinux-to-elf` | `1.3.6` |
| `vmlinux-to-elf` wheel SHA-256 | `622977d506b44e3718760689e196e5ef769ffa0c864e64d083651db713221cb5` |
| Parser source | https://github.com/marin-m/vmlinux-to-elf |
| Host disassembler | Apple LLVM 21.0.0 `nm` / `objdump` |
| Device execution | none |

The reconstruction command was equivalent to:

```sh
vmlinux-to-elf PS7331-kernel.Image reconstructed-kernel.elf
python3 tools/scripts/analyze_phase5ar_ps7331_rtmutex_binary.py \
  --elf reconstructed-kernel.elf \
  --output ps7331-rtmutex-static-review
```

The analysis output deliberately omits absolute kernel addresses, raw branch
targets, gadget data and exploit offsets. It records only symbol presence and
the semantic instruction patterns needed to determine whether the old or fixed
`remove_waiter()` behavior is present.
