# Phase 6NB evidence index

| Evidence ID | Source | File/member | Observation | Confidence |
|---|---|---|---|---|
| 6NB-S01 | Amazon GPL source | `device/amazon/kernel/driver/Kconfig:65-70` | `AMZN_DRV_TEST` option exists and is tristate | Confirmed |
| 6NB-S02 | Amazon GPL source | `device/amazon/kernel/driver/Kconfig:67` | Test option depends on metrics, sign-of-life and IDME options | Confirmed |
| 6NB-S03 | Amazon GPL source | `device/amazon/kernel/driver/Makefile:28` | `CONFIG_AMZN_DRV_TEST` maps to `amzn_drv_test.o` | Confirmed |
| 6NB-S04 | Amazon GPL source | `trona_defconfig` | No `CONFIG_AMZN_DRV_TEST=y/m` line | Strong evidence |
| 6NB-S05 | Amazon GPL source | `amzn_drv_test.c:32-35` | Proc root and child labels are `amzn_drvs`, `sign_of_life`, `idme`, `logger` | Confirmed |
| 6NB-S06 | Amazon GPL source | `amzn_drv_test.c:797-841` | `proc_mkdir` and three `proc_create_data` calls are present | Confirmed |
| 6NB-S07 | Amazon GPL source | `amzn_drv_test.c:784-790` | Shared file operations include `proc_write` | Confirmed |
| 6NB-S08 | Amazon GPL source | `amzn_drv_test.c:747-781` | Write parser bounds/copies input and parses a decimal index | Confirmed |
| 6NB-S09 | Host-only boundary | source archive only | Final image inclusion, procfs presence, SELinux and runtime caller are not established | Unknown |

Archive SHA-256:
`69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd`.

Reproduction:

```sh
python3 -B tools/scripts/audit_phase6nb_amzn_drv_test_source.py \
  --archive firmware/extracted/PS7331-SOURCE-20250617/platform.tar \
  --output artifacts/phase6nb-amzn-drv-test-source-closure-YYYYMMDD-NN
(cd artifacts/phase6nb-amzn-drv-test-source-closure-YYYYMMDD-NN && \
  sha256sum -c sha256sums.txt)
```
