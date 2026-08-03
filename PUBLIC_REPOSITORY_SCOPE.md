# Public Repository Scope

This is a direct public copy of the analysis project’s readable reports, scripts, manifests, small evidence files, AOSP reference snippets, and reproducible metadata.

The local workspace is approximately 11 GB. GitHub’s normal Git transport rejects individual files over 100 MB and a normal public repository should not carry multi-gigabyte OTA/system images. The following local-only paths are therefore excluded mechanically by `.gitignore`:

- original and extracted OTA/partition images;
- raw VDEX/baksmali trees and the full JADX/apktool output trees;
- pulled APK/JAR/ODEX/VDEX/Dex/native binaries;
- generated multi-megabyte method/class indexes and redundant diff tables.

No GitHub token, private key, or local credential is part of the repository. Public files retain the research package names, device-derived observations, report paths, and evidence hashes needed to audit the analysis. Excluded artifacts remain in the local workspace and are referenced by reports where their hashes are available.

The public repository is not a replacement for the immutable local evidence archive. Raw evidence should be distributed only after reviewing device identifiers, licensing, and applicable firmware/APK redistribution terms.
