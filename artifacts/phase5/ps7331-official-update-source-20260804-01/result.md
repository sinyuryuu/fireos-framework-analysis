# PS7331 official update source mapping

The official Amazon Fire Tablet Software Updates page lists Fire HD 10 (11th
Generation) under Fire OS 7.3.3.1. Its download route redirects to the S3 URL
recorded in `source-map.tsv`; the remote content length matches the locally
preserved OTA byte-for-byte in size. The local archive hash is preserved from
the earlier metadata inspection.

This check used HTTP metadata only. It did not install, sideload, execute, or
write the OTA, and it did not change the device.
