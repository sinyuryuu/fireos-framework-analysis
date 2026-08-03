# Phase 5AO evidence index

| Evidence ID | Source | File / reference | Observation | Confidence |
|---|---|---|---|---|
| `P5AO-001` | PS7331 boot parser | `artifacts/phase5/ps7331-boot-image-inspection-20260804-01/boot-image-metadata.json` | Android header, kernel offset `0x800`, page size 2048, kernel address `0x40080000` | 已證實 |
| `P5AO-002` | PS7331 compressed kernel | `.../kernel.payload.sha256`; source boot hash in `.../input.sha256` | gzip payload SHA-256 `a608a5f9…`; boot SHA-256 `cf12e561…` | 已證實 |
| `P5AO-003` | Decompressed PS7331 Image | local derived `.../kernel.Image`; `file` and `strings` output | ARM64 Image, Linux `4.4.146+`, build timestamp 2025-05-03, MT8183/Amazon paths | 已證實 |
| `P5AO-004` | Public vulnerability records | [NVD CVE-2026-43499](https://nvd.nist.gov/vuln/detail/CVE-2026-43499); [Ubuntu advisory](https://ubuntu.com/security/CVE-2026-43499) | upstream affected range and `rtmutex.c` fix reference | 已證實，external scope |
| `P5AO-005` | Exact installed-device comparison | `findings/phase-5an-ghostlock-exact-target-review.md`; `findings/phase-5n-exact-source-ghostlock-review.md` | installed device is PS7330; exact boot pull is denied; source/layout evidence is not PS7331 binary evidence | 已證實 |
| `P5AO-006` | Capability boundary | `findings/phase-5ao-ps7331-boot-analysis.md` | boot image supports offline provenance and partial symbol inspection, not full runtime exploit profile | 高可信推論 |
| `P5AO-007` | Safety decision | `findings/phase-5ao-ps7331-boot-analysis.md` | no live race, root payload, partition write, or bootloader operation | 因風險拒絕測試 |
