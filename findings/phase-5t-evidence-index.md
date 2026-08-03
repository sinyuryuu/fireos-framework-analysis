# Phase 5T evidence index

| Evidence ID | File | Observation | Interpretation | Confidence |
|---|---|---|---|---|
| `P5T-BASE-001` | `adb/phase5/PHASE5T-OTA-METADATA-20260804-01/identity.stdout.txt` | Build fingerprint, security patch, kernel and ADB identity preserved | Current target identification | 已證實 |
| `P5T-BUILD-001` | `all_getprop.stdout.txt` | `trona_fireos_ship_7330`, PS7330/4104, MediaTek branch/release, PL/LK descriptors | Stronger build/boot metadata chain | 已證實，property-scoped |
| `P5T-OTA-001` | `readable_ota_paths.stdout.txt` | `/cache`, `/data/ota`, `/data/ota_package` denied; `/data/local/tmp` contains no OTA image | No shell-visible cached OTA payload | 已證實，visibility-scoped |
| `P5T-OTA-002` | `ota_package_paths.stdout.txt` | OTA/provisioning package paths are present | Package presence does not expose payload URL or boot image | 已證實 |
| `P5T-HOME-001` | `home_result.stdout.txt` | HOME remains `com.amazon.firelauncher/.Launcher`, priority 50 | No HOME state mutation occurred | 已證實 |
| `P5T-SAFETY-001` | `result.md`, `metadata.tsv`, `sha256sums.txt` | Collector marked read-only; all outputs hashed | Reproducible, non-mutating evidence | 已證實 |
