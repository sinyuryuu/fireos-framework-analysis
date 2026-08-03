# PS7330 artifact follow-up metadata

日期：2026-08-04（UTC）

## Device target

| Field | Value |
|---|---|
| Model | `KFTRWI` |
| Product | `trona` |
| Installed build | `PS7330.4104N/0030099376128` |
| Fire OS | `7.3.3.0` |
| Preloader descriptor | `d1a4a4b-20231011_072631` |
| LK descriptor | `79172a1-20231008_072039` |
| Device mutation | none |

## Sources checked

| Source | Observation | Scope |
|---|---|---|
| [Amazon Fire Tablet Software Updates](https://digprjsurvey.amazon.co.uk/csad/help/node/G2JXLC4L34GX73TE) | 11th-generation entry currently says FireOS 7.3.3.1 | official version/update index |
| `https://www.amazon.com/update_Fire_HD10_11th_Gen` | HTTP 301 redirects to a PS7331 package, not PS7330 | official download endpoint observation |
| [FTVDB 11th-gen firmware history](https://ftvdb.com/firetablet/firmware/com.amazon.trona.android.os/) | rendered public history lists PS7331/4463, PS7329/3851 and older entries; no PS7330 entry | independent public metadata, absence is search-bounded |
| [FTVDB raw trona database](https://raw.githubusercontent.com/FTVDB/FTVDB/main/database/firmware/com.amazon.trona.android.os.json) | 5,169-byte JSON snapshot contains PS7319, PS7321–PS7329 and PS7331 records; no `PS7330` value | reproducible public-data corroboration |
| [Technically Competent source-notice archive](https://technicallycompetent.com/pages/amazon-kindle-source-code-notices/) | lists `Fire_HD10-7.3.3.0-20240730.tar.bz2` for 11th generation; no 11th-gen 7.3.3.1 source entry in its dated snapshot | source-notice provenance |
| exact source URL | `https://fireos-tablet-src.s3.amazonaws.com/7OU0BzzYt2YlM3MKwchLwgyUHM/Fire_HD10-7.3.3.0-20240730.tar.bz2` | current-device source family |

## Official update endpoint response

The request was a host-only metadata/HTTP check. The response redirected to:

```text
https://fireos-tablet-src.s3.us-west-2.amazonaws.com/3omHNOvwW4KDYd5xDz75MnJ9npabcf/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin
```

Relevant response metadata:

```text
HTTP/2 301
location: https://fireos-tablet-src.s3.us-west-2.amazonaws.com/3omHNOvwW4KDYd5xDz75MnJ9npabcf/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin
HTTP/1.1 200 OK
Last-Modified: Wed, 11 Jun 2025 20:38:26 GMT
ETag: "840298f39063fd73c031468b1c0eb416-76"
Content-Length: 1301005356
```

The host request was allowed to time out after `39056098` bytes while checking
the redirect and headers. The partial response hash was
`ebd8e95e7b17ff40014bbc79f988b05bfa480675996631578d2ffd80ac8ca15d`; it is not
treated as a firmware artifact, was not extracted, and was not added to the
repository. The complete PS7331 OTA already preserved in the workspace remains
the only local complete OTA and is explicitly `VERSION_MISMATCH` for PS7330.

The raw FTVDB JSON retrieved for this review was 5,169 bytes with SHA-256
`7d80beaf572ee585449da48121b190b30cee7f92b1a69d3011b61d2668e6632a`. It is
metadata only; no firmware file was downloaded from FTVDB.

## Exact-target search result

Searches for the installed build, descriptors and likely package names returned
no independently verifiable PS7330 boot image, preloader, LK, DA, or recovery
set. This is a bounded public-search result, not proof that no private or
unindexed copy exists.

## Decision

No exact PS7330 low-level artifact was obtained. No device command, loader,
fastboot write, BROM/DA operation, sideload, reboot, or partition access was
performed in this follow-up.
