# Phase 6RV–RX evidence index

Date: 2026-08-10
Public baseline: `47daff30d` (Phase 6RS–RU)
Device operations in this phase: none

## 6RV-LEDGER — permission holders and callers

- Files: `work/luna_worker_phase6rv_20260810.md/.csv`
- Markdown SHA-256: `77e69d9eccbe22b2a4dc3fc0a14ce5d61ea2cc50d1e4046bc7bc7cdb0cd31708`
- CSV SHA-256: `b996cba8d13abc7921f0940c68e51101f9a6f66292e989df4c29af814f66b811`
- Rows: 15
- Result: `ADD_RM_PKG_METADATA` declaration, mutators, persistence sink, and
  visible consumers are closed statically; exact holder and production caller
  remain `UNKNOWN`.
- Confidence: Confirmed static structure; Strong evidence for bounded negative
  HOME/package-state join.

## 6RW-LEDGER — SystemUI and overlay closure

- Files: `work/luna_worker_phase6rw_20260810.md/.csv`
- Markdown SHA-256: `aa1e2d13d3a846a5035393120bedec39fc0fe82d17d8bf40af8f821eef558f17`
- CSV SHA-256: `409bc4a471847452fc5f61665ca4fbea503771a69775d6257449438156179ee6`
- Rows: 20
- Result: service arrays, callbacks, Settings HOME controller, PMS ranking,
  KFT child writer, OOBE writer, and overlay scope are separated; no explicit
  Fire component launch was found in the saved callback corpus.
- Confidence: Confirmed for cited artifacts; Strong evidence within the bounded
  SystemUI/resource corpus.

## 6RX-LEDGER — OOBE/OTA/native broad sink audit

- Files: `work/luna_worker_phase6rx_20260810.md/.csv`
- Markdown SHA-256: `dbdc9e0236e7977155b92a38969dfbdf86a49b42e4918ae56fb3c9cf9c7d665f`
- CSV SHA-256: `0b00714ae3fc01c954aea9cdedcc8d39331f822abb2d790eb32eaad77fd0dc5c`
- Rows: 13
- Result: no new ordinary-app/shell-to-sensitive-sink chain; unknown caller,
  scope, and native enforcement gaps remain explicit.
- Confidence: Strong evidence for bounded closure; UNKNOWN is not a negative
  runtime result.
- Data-quality note: the preserved raw CSV has unquoted commas in rows
  `1,2,3,4,5,7,8,9,10,11,12,13`; the normalized matrix marks shifted trailing
  fields `UNKNOWN_DUE_TO_UNQUOTED_RAW_CSV`. The raw file remains unchanged.

## 6RV-RX-MATRIX — normalized table

- File: `output/tables/phase6rv-rx-privilege-surface.csv`
- Manifest: `output/tables/phase6rv-rx-privilege-surface.csv.manifest.json`
- CSV SHA-256: `1d73a3aabbc0faa82db4f01a43dd0d6bbbe12a8a3fa933555ae04dce8c747927`
- Manifest SHA-256: `e427d309b41dda0d80939e1b3a8f6a589d308799df6688b1c45bd1d4ccd2924d`
- Generator: `tools/scripts/build_phase6rv_rx_surface.py`
- Rows: 48 (15 + 20 + 13)
- Generator safety flags: no device contact, Binder/settings operation,
  mutation, or root/exploit behavior.

### Supporting output hashes

- `output/call-graphs/phase6rv-rx-control-surfaces.mmd` —
  `212d101928acb711024a2aeaec20c9bf2112616caaa5a874ded0dbed6f90e7b2`
- `output/call-graphs/phase6rv-rx-control-surfaces.md` —
  `51d5f02d606397ff9dcbe40fd61f2a8d8be170feaccf07109c11078ff3720c79`
- `tools/scripts/build_phase6rv_rx_surface.py` —
  `f89da5483006f0459926f3a527937f8cf02412c9b1812525b0e78cfa2d0e0aab`

## 6RV-RX-SAFETY — not executed

No Binder transaction, protected broadcast, service call, input injection,
driver operation, updater/recovery execution, overlay/package/settings/user
mutation, reboot, Root/exploit, remount, SELinux change, or partition write was
performed. These are **因風險拒絕測試**, not runtime negative evidence.

## Confidence vocabulary

- **已證實 / Confirmed** — direct source or saved runtime fact.
- **高可信推論 / Strong evidence** — multiple bounded artifacts agree.
- **待驗證 / Pending** — a named host-only gap remains.
- **已排除 / Disproved** — contradicted in the stated build and scope.
- **因風險拒絕測試 / Risk-rejected** — intentionally not executed.
