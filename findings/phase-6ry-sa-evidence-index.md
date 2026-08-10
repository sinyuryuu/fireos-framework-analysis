# Phase 6RY–SA evidence index

Date: 2026-08-10
Public baseline: `80fb5c6fe`
Device serial: `G001LT0511550CFT`

## 6RY — Amazon permission/IPC

- Markdown: `work/luna_worker_phase6ry_20260810.md`
- CSV: `work/luna_worker_phase6ry_20260810.csv`
- Markdown SHA-256: `cd921afff9a34f93a2758055c0d4eaba1edf613bcb249e5ec1595551484c6480`
- CSV SHA-256: `15ccdb6a9dbd6b2c851502bf29b85f9cefb9634ba42fc6b10887d551f96d6fbb`
- Parsed rows: 12 data rows, 11 columns
- Finding: metadata/flags Binder mutators and XML sink are static-closed;
  exact holder and production caller remain `UNKNOWN`.
- Confidence: Confirmed static path; Strong evidence for no bounded HOME/PMS
  bridge.

## 6RZ — kernel/driver inventory

- Markdown: `work/luna_worker_phase6rz_20260810.md`
- CSV: `work/luna_worker_phase6rz_20260810.csv`
- Markdown SHA-256: `63b75fce577e9176e68b8bb61c4e5bba932a5e41521ac6306ee42d57fac69b0f`
- CSV SHA-256: `f915e75e9461b1a59e26c2c939ab24e34032ca86ce38108e0649a516bfc64079`
- Parsed rows: 16 data rows, 11 columns
- Finding: custom and upstream driver capabilities are separated from final
  node/client/SELinux reachability; no privilege/package sink is closed.
- Confidence: Confirmed source/config/metadata facts; Pending runtime joins.

## 6SA — official installer/OTA

- Markdown: `work/luna_worker_phase6sa_20260810.md`
- CSV: `work/luna_worker_phase6sa_20260810.csv`
- Markdown SHA-256: `1ce1bb5597724ebc4324a155fe100c414a42732eb0e5b8f34cf600b9431f5150`
- CSV SHA-256: `38c3e0bf48a36d6331d199a2c0b8113e6ed7262ba6a3506e43d465a3aa10cda6`
- Parsed rows: 17 data rows, 9 columns
- Note: worker prose said 18 rows; actual CSV parser found 17 data rows. Raw
  output is preserved unchanged and the normalized matrix uses 17.
- Finding: signed OTA, updater, recovery, OOBE, and partition capability are
  confirmed statically; no ordinary caller route was closed.
- Confidence: Confirmed official artifacts; Strong bounded negative caller
  result; Pending outer/native/user mapping.

## 6RY-DEVICE — exact serial read-only snapshot

- Directory: `adb/phase6ry/PHASE6RY-DEVICE-READONLY-20260810-01/`
- Metadata SHA-256: `d668af5655955c4c48078200a96f5d6b6830e7cb2b70bf533d6a53ef73a503fa`
- `home_resolve.stdout.txt` SHA-256: `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6`
- `sha256sums.txt` SHA-256: `3f84e1575936b7d61b166d2b93b832a7c35a2409f6dc594ad9215773fee6fac7`
- Commands: 12, read-only
- Safety flags: no node open, driver read, Binder transaction, settings/package
  mutation, reboot, OTA/recovery, or root/exploit.
- Direct result: PS7331.4463N, SELinux Enforcing, HOME Fire priority 50,
  Microsoft candidate priority 0.

## Normalized matrix

- File: `output/tables/phase6ry-sa-control-surface.csv`
- Manifest: `output/tables/phase6ry-sa-control-surface.csv.manifest.json`
- Generator: `tools/scripts/build_phase6ry_sa_surface.py`
- Matrix rows: 45 (12 + 16 + 17)
- Generator does not contact the device or invoke Binder/settings/mutation/root.
- CSV SHA-256: `2a7cff4d64d8872c746421fedf2e12be0895c08ca5cbbdd76a36df7de993026b`
- Manifest SHA-256: `c1dbcba178a3ad5623515dbf663047131f969aeb928916dedb7c4b4eb3ce271f`

### Supporting output hashes

- `output/call-graphs/phase6ry-sa-control-surfaces.mmd` —
  `850f2ca58f29d865d267393d672c476d61bcabfd99633e54add9e06249347178`
- `output/call-graphs/phase6ry-sa-control-surfaces.md` —
  `c2c59a7502392a5320c56228b24107b1f48953bae5d869e3a7cd52379a549a50`
- `tools/scripts/build_phase6ry_sa_surface.py` —
  `4c2554604264fda3bce9c146d1a9bf32ccd70379528461ad63fa5173be97c578`

## Confidence vocabulary

- **Confirmed** — direct artifact or saved runtime fact.
- **Strong evidence** — bounded multi-source inference.
- **Pending** — named evidence gap remains.
- **Disproved** — contradicted within stated build/scope.
- **Risk-rejected** — not executed for safety/rollback reasons.
