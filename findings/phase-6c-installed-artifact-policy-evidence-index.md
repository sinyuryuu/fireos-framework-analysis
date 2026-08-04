# Phase 6C installed-artifact policy evidence index

## E6C-IA-001

- **Source:** PS7331 7.3.3.1 OTA metadata
- **File:** `firmware/extracted/PS7331/ota.prop`
- **SHA-256:** `f91b4c792339c605d81a2d6d5e819fee5d522a7514111daa1468717e07319ded`
- **Test ID:** `PHASE6C-INSTALLED-ARTIFACT-POLICY-20260804-03`
- **Timestamp:** 2026-08-04 UTC run; generated artifact timestamp is in JSON
- **Command:** `sed -n '1,140p' firmware/extracted/PS7331/ota.prop`
- **Observed result:** `Fire OS 7.3.3.1`, `PS7331.4463N`, `trona`, release build metadata.
- **Interpretation:** Input provenance matches the PS7331 artifact set used by this audit.
- **Confidence:** Confirmed
- **Related hypothesis:** H6C-ARTIFACT-PROVENANCE

## E6C-IA-002

- **Source:** Host-only artifact scanner
- **File:** `artifacts/phase6c/phase6c-installed-artifact-policy-20260804-04/installed-artifact-policy.json`
- **SHA-256:** `8dc5b673da4a12ae3223dd298e1f95ff60b3e87abdaf3a6b9596b45cb24ecc93`
- **Test ID:** `PHASE6C-INSTALLED-ARTIFACT-POLICY-20260804-03`
- **Timestamp:** 2026-08-04T13:27:14Z generated_at_utc
- **Command:** `python3 tools/scripts/audit_phase6c_installed_artifacts.py ...`
- **Observed result:** 53 files and 14,075 archive members scanned; named `FUTEX_CMP_REQUEUE_PI` and `FUTEX_WAIT_REQUEUE_PI` counts are both 0; no image was mounted or ELF executed.
- **Interpretation:** No direct named requeue-PI marker was found in the supplied installed-artifact candidates.
- **Confidence:** Strong evidence
- **Related hypothesis:** H6C-NAMED-USERSPACE-CALLER

## E6C-IA-003

- **Source:** Host-only artifact inventory
- **File:** `artifacts/phase6c/phase6c-installed-artifact-policy-20260804-04/artifact-inventory.csv`
- **SHA-256:** `28c588e3982674e17b109cbb0f884e812909fe84503ed07058cffe6993c5cc47`
- **Test ID:** `PHASE6C-INSTALLED-ARTIFACT-POLICY-20260804-03`
- **Timestamp:** Same run as E6C-IA-002
- **Command:** scanner output; no device command
- **Observed result:** Six path candidates were policy-named: Amazon policy/key-policy init XMLs, a Serendipity allowlist, and preserved `app_process64` files. `system.img`, `vendor.img`, and `boot.img` were not included in this content scan.
- **Interpretation:** The discovered policy-named files are a bounded lead list, not proof of futex policy or a complete image inventory.
- **Confidence:** Confirmed
- **Related hypothesis:** H6C-INSTALLED-POLICY-SOURCE

## E6C-IA-004

- **Source:** Marker hit output
- **File:** `artifacts/phase6c/phase6c-installed-artifact-policy-20260804-04/marker-hits.csv`
- **SHA-256:** `923f59e2e9c48ae5d6ed3bcff21fdc452f01c3744a44100287e8b2d157c3ce89`
- **Test ID:** `PHASE6C-INSTALLED-ARTIFACT-POLICY-20260804-03`
- **Timestamp:** Same run as E6C-IA-002
- **Command:** scanner output; no device command
- **Observed result:** `linker64` contains generic `SECCOMP`/`NO_NEW_PRIVS` diagnostic markers; `app_process64` contains zygote/app_process markers; no named requeue-PI marker appears.
- **Interpretation:** These are runtime-surface clues only. They do not disclose a filter rule or prove whether any futex opcode is allowed.
- **Confidence:** Strong evidence
- **Related hypothesis:** H6C-SECCOMP-FUTEX-GATE

## E6C-IA-005

- **Source:** Amazon init/callback configuration
- **Files:** `artifacts/amazon-services/amazondevicepolicymanager_fosinit.xml`, `keypolicymanager_fosinit.xml`, `tabletkeypolicymanager_fosinit.xml`, `serendipity_allowlist.xml`
- **SHA-256:** `6fe0df7450551fb940f4169977d97b46bebb43bebef8a604ac77e0c40f91acee`, `802a9b8e22ac485a07d5198bd22fd6aae18920f56af4f34a2ba35a0083a91ffe`, `a5faec416c32013f267ed58f47b598a0f715c4e49606d99affb0367931f02118`, `a05021d432f5e5b42ea4f873ce97b6450338318781e282a72080f06be4f95895`
- **Test ID:** `PHASE6C-INSTALLED-ARTIFACT-POLICY-20260804-03`
- **Timestamp:** Same run; XMLs preserved before this audit
- **Command:** `sed -n ...` plus scanner inventory
- **Observed result:** Amazon device-policy/key-policy callbacks and a privileged permission allowlist are present; no futex opcode or seccomp rule is present in these XML files.
- **Interpretation:** These artifacts identify additional policy owners to analyze, but do not establish a GhostLock userspace path.
- **Confidence:** Confirmed
- **Related hypothesis:** H6C-AMAZON-POLICY-CALLER

## E6C-IA-006

- **Source:** Preserved native `linker64` and `app_process64`
- **Files:** `artifacts/phase5/phase5cq-fire-native-20260804-01/files/linker64`, `.../app_process64`
- **SHA-256:** `124745b0cac2fa1511cd903a3982108109d8c8f38e77c63df3e97b026e6ee21b`, `c075e6bbef31b2ae03ef6336b8d605c6f430e49bf25444c44aea0563647ec01e`
- **Test ID:** `PHASE6C-INSTALLED-ARTIFACT-POLICY-20260804-03`
- **Timestamp:** Same run; preserved native artifacts
- **Command:** host `strings -a` context check and scanner
- **Observed result:** `linker64` has generic seccomp diagnostic strings; `app_process64` has zygote startup strings.
- **Interpretation:** No direct policy rule or requeue-PI caller can be inferred from these strings.
- **Confidence:** Probable
- **Related hypothesis:** H6C-SECcomp-INTERPRETATION

## Evidence boundary

No evidence in this index authorizes a device-side requeue-PI trigger. The
remaining runtime identity mismatch, cleanup residue, memory effect and
privilege-transition questions are **待驗證** and remain outside the current
stock-device safety boundary.
