# Phase 5AS：Amazon source-notice backup review

## 結論

本頁的證據 ID 是 `P5AS-001` 與 `P5AS-002`，詳見
[`phase-5ar-evidence-index.md`](phase-5ar-evidence-index.md)。

**已證實：** the supplied backup page is a useful historical index and lists
the exact `Fire_HD10-7.3.3.0-20240730.tar.bz2` source archive for the Fire HD 10
/ Fire HD 10 Plus 11th generation.

**已證實：** the page snapshot is marked `scraped 2025-02-26` and does not list
an 11th-generation `7.3.3.1` source archive.

**高可信推論：** the 7.3.3.0 archive is the most relevant public source for the
currently installed PS7330 device and is already the source used in Phase 5N.

**待驗證：** whether Amazon published a later 7.3.3.1 source archive after the
backup snapshot. The current official software-update page lists Fire HD 10
11th Gen as Fire OS 7.3.3.1, but software availability and source-notice
availability are separate facts.

The backup page should therefore be treated as provenance, not as evidence that
the 7.3.3.1 kernel source is available there.

## Evidence

- Backup page: https://technicallycompetent.com/pages/amazon-kindle-source-code-notices/
- Page retrieval SHA-256: `fa0e0c8639549d61ab4b59a6fb34b99da5a3ce690af668c59d026fe1d97c9e0d`
- Page-stated snapshot date: `2025-02-26`
- Exact archive URL:
  https://fireos-tablet-src.s3.amazonaws.com/7OU0BzzYt2YlM3MKwchLwgyUHM/Fire_HD10-7.3.3.0-20240730.tar.bz2
- Local source review: `findings/phase-5n-exact-source-ghostlock-review.md`

No archive was modified and no firmware was flashed.
