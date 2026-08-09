# Phase 6ND evidence index

| Evidence ID | Input | Observation | Confidence |
|---|---|---|---|
| 6ND-S01 | `amzn_drv_test.c` source member | Unique marker `amzn_drvs` is present in source | Confirmed |
| 6ND-I01 | Official PS7331 `boot_unpacked/Image` | `amzn_drvs` occurs zero times | Strong evidence |
| 6ND-I02 | Official PS7331 `boot_unpacked/Image` | `logger_loop`, test function names and source error text occur zero times | Strong evidence |
| 6ND-I03 | Artifact CSV/manifest | Generic `idme`, `logger`, `sign_of_life` hits are not driver-specific and are excluded from positive proof | Confirmed interpretation |
| 6ND-L01 | Extraction scope | Generated config, loadable modules, SELinux labels and runtime procfs remain unobserved | Unknown |

Reproduction:

```sh
python3 -B tools/scripts/audit_phase6nd_amzn_drv_test_image_markers.py \
  --archive firmware/extracted/PS7331-SOURCE-20250617/platform.tar \
  --image firmware/extracted/PS7331/boot_unpacked/Image \
  --output artifacts/phase6nd-amzn-drv-test-image-marker-YYYYMMDD-NN
(cd artifacts/phase6nd-amzn-drv-test-image-marker-YYYYMMDD-NN && \
  sha256sum -c sha256sums.txt)
```

