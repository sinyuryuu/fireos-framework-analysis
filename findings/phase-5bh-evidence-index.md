# Phase 5BH evidence index

| Evidence ID | File | SHA-256 | Observation | Confidence |
|---|---|---|---|---|
| `P5BH-OFFICIAL-001` | `artifacts/phase5/ps7331-official-update-source-20260804-01/source-map.tsv` | `0a7eb0ac06352eb33b9ac5ce8416637b6819c67c1389bc52937ff893c836f6be` | Official Amazon update page and resolved S3 URL map to local PS7331 archive | Confirmed |
| `P5BH-HEAD-001` | `artifacts/phase5/ps7331-official-update-source-20260804-01/official-update-headers.txt` | `4ca3d7e54d0a5a3ac1aded868e1affdf3343bc99eb632c7a4b59a9e61721b8ad` | Remote content length is 1,301,005,356 bytes; S3 metadata recorded | Confirmed, HTTP metadata scope |
| `P5BH-LOCAL-001` | `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` | `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5` | Local OTA hash and size match official metadata | Confirmed, local archive scope |
| `P5BH-OTA-001` | `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/updater-script.txt` | `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248` | OTA writes multiple OS, boot-chain and firmware partitions | Confirmed, metadata scope |
| `P5BH-DECISION-001` | `findings/phase-5bg-ps7331-source-binary-semantic.md` | Reported in Phase 5BG index | Official source does not change the pre-fix GhostLock semantic result | Strong evidence |

No device state was changed.
