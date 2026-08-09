# Phase 6ND — `amzn_drv_test` official Image marker audit

Archive: `firmware/extracted/PS7331-SOURCE-20250617/platform.tar`

Archive SHA-256: `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd`

Official boot Image: `firmware/extracted/PS7331/boot_unpacked/Image`

Official boot Image SHA-256: `10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d`

## Scope

The source member was read from the tar stream and the already extracted official kernel Image was searched as raw bytes. Nothing was executed; no device or kernel interface was contacted.

## Result

Source-defined markers: `9`.

Markers observed in official Image: `3`.

Source markers not observed in official Image: `6` (amzn_drvs, logger_loop, no this test item, sign_of_life_test, idme_test, logger_test).

**Interpretation:** absence of the unique `amzn_drv_test` proc/test strings is bounded negative evidence against this driver being built into this Image in an unoptimized, literal-preserving form. It does not close loadable modules, generated `.config`, compiler elimination, SELinux, or runtime procfs existence. The common `idme` marker is not specific to the test driver and is not used as positive proof.

See the CSV for exact counts and the input hash manifest for provenance.
