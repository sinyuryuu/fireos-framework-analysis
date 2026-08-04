# Phase 5BT source-archive validation

The local PS7331 source archive has the same byte length as the official HTTP
`Content-Length`, and its MD5 equals the single-part S3 ETag preserved in the
HTTP header record. Its SHA-256 is recorded in `metadata.tsv`.

The archive and boot image were treated as read-only evidence. No source,
build script, kernel image, exploit, payload, ADB command, fastboot command,
OTA operation, or partition operation was executed by this validation.
