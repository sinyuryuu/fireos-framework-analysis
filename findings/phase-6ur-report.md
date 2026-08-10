# Phase 6UR — caller/sink and artifact-completeness closure

This host-only bundle follows Phase 6UM by closing four residual evidence groups: native node joins, OTA verifier/handoff, ASP/prewarm caller/sink analysis, and fosinit/classloader completeness. The acceptance rule remains caller → gate → identity/user scope → exact sink → observed effect.

Generation HEAD: `5fcc55dcebc89cafa6f5799af7d53998f26854f4`.

## Safety boundary

No Binder or service transaction, driver/node/ioctl operation, OTA/recovery/updater execution, malformed input, package/settings mutation, user provisioning, reboot, Root/exploit attempt, Fire Launcher mutation, or partition write was performed.

## Inputs

- **6UN native node join:** `work/luna_worker_phase6un_native_node_join_20260810.md` (2136d316bd27fc33ef876204ae76148a0af44bc1c867dcc3060a6a2fccf52e34); `work/luna_worker_phase6un_native_node_join_20260810.csv` (bceef4c32150d91e9b006a251d6cee85931947ad818aaee32d6c18c188d024f0); 3 row(s).
- **6UO OTA verifier/handoff:** `work/luna_worker_phase6uo_ota_verifier_handoff_20260810.md` (ab72c4a8c4afaa643d73ac2f26ee0bd60c8078e7067500a58d37e34c34d70c31); `work/luna_worker_phase6uo_ota_verifier_handoff_20260810.csv` (555957894258c019fbd30b69385818db507f4d3aae5679ef48d02f696ebcccb2); 18 row(s).
- **6UP ASP/prewarm closure:** `work/luna_worker_phase6up_asp_prewarm_closure_20260810.md` (1fc7d71c3232bd6122907394ea68665163bae3e3881ee218bcf7804c04479016); `work/luna_worker_phase6up_asp_prewarm_closure_20260810.csv` (0f33c86e23ce6c92f5e79c1adef2135736ef90de9a17cd7f4a0dab5192c39c1b); 13 row(s).
- **6UQ fosinit completeness:** `work/luna_worker_phase6uq_fosinit_completeness_20260810.md` (e024c57757729622e0f968f70338a2d453e7a96707577eaa9494947b56cb67ce); `work/luna_worker_phase6uq_fosinit_completeness_20260810.csv` (41a7dd25af6dca212867c7ccf7203d0257bacf406697a7cb8b4bc85deb7a1b04); 25 row(s).

Context hashes: `findings/phase-6um-report.md` (0f730a9543b43f15b90abc0fc81e09cd0e81eacc9f425e1f7d4fc4400c6d148f); `output/tables/phase6um-control-surface.csv` (e9cd96a4c7af4e8d09433845ae0fba366896d84e8aec7ffddc7cef395224eae0); `findings/phase-6ui-readonly-snapshot.md` (0983f132483e235d82b35a0b0f42f7dd577666249c3b347c891e8e35773b5882); `output/tables/phase6ui-readonly-state.csv` (7cfe1aa24ac4eeffca6147935ebac6ed9f71e92cde31b669eeead92e3ffcdc5b); `findings/phase-6py-service-state-exported-closure.md` (6f1a7a07e38eb92f4c65511ee3533b7809ce31c3db9bf76677c4c2d7d86d1898); `findings/phase-6nj-followup-synthesis.md` (8c57ec3d603510c57704dd72ea0a115bc7f17b1b856946ee3091a450af01589c)

## Findings

### Native node joins — **已證實 capability / 待驗證 reachability**

CMDQ, ION/MTK ION and Amazon-LD are selected or registered in the preserved source/config scope. The exact shipped object/module, DT/init instance, ueventd/file_contexts/vendor-TE policy and native client edges are not all present. Source-declared mode or an ioctl fops path is not proof that an ordinary app can reach a state-changing effect. No PackageManager, HOME or privilege-transition sink was found in this join.

### OTA verifier/handoff — **已證實 gates and recovery capability / 待驗證 handoff**

The signed PS7331 block OTA has product/build/timestamp checks, certificate/recovery-verification contracts, block verification symbols and fixed partition targets. Native recovery-to-updater caller identity, AVB/rollback implementation and canonicalization dataflow remain incomplete. The partition writer is a recovery capability, not an ADB or ordinary-app route.

### ASP/prewarm — **已證實 bounded runtime boundary / no accepted low-privilege route**

The tablet ASP branch consumes `ASP_PERMISSION` and the saved shell transaction returned `-13`; the non-tablet allow branch is cross-build static evidence only. Prewarm shows an ignored permission result before identity clear and process prewarm, but saved service lookup/dispatch evidence closes shell reachability on KFTRWI and no package/HOME/settings/root sink is present. These remain code-review anomalies, not exploit findings.

### fosinit/classloader — **高可信 bounded completeness / residual static gaps**

The preserved corpus contains 244 XML entries, 186 listed services and principal Amazon Binder contracts. Private service lookup is denied to shell in saved enforcing evidence. Several HOME-adjacent, package/settings-adjacent and OTA callback groups remain source-to-effect gaps, but no unreviewed ordinary external path to User-0 HOME/package/settings/user/OTA state is closed. Registration, listing and class presence are not method reachability.

## Final bounded conclusion

The remaining surfaces are now classified as protected lifecycle writers, high-impact static capabilities, or bounded code-review anomalies. No evidence justifies claiming a root path, confused deputy, Fire Launcher disable route, or formal User-0 HOME replacement. The next safe work is a finite host-only closure of the seven fosinit residual groups; if that produces no caller→gate→sink edge, the privileged-control branch should be archived as unclosed rather than tested by guessing Binder codes, opening drivers, or executing OTA/recovery.

## Verdict labels

- **已證實:** exact static edge or saved read-only runtime result within scope.
- **高可信推論:** bounded interpretation with named missing edge.
- **待驗證:** source/registration/caller/gate/identity/sink or runtime effect is incomplete.
- **已排除:** target effect did not occur under recorded conditions.
- **因風險拒絕測試:** operation was not performed because it crosses the safety boundary.

Integrated rows: `59`; parse warnings: `0`; source-format notes: `9`.

Warnings:
- None detected.

Source-format notes (raw provenance rows retained unchanged):
- `work/luna_worker_phase6uq_fosinit_completeness_20260810.csv:18: extra_fields=1`
- `work/luna_worker_phase6uq_fosinit_completeness_20260810.csv:19: extra_fields=1`
- `work/luna_worker_phase6uq_fosinit_completeness_20260810.csv:20: extra_fields=1`
- `work/luna_worker_phase6uq_fosinit_completeness_20260810.csv:21: extra_fields=1`
- `work/luna_worker_phase6uq_fosinit_completeness_20260810.csv:22: extra_fields=1`
- `work/luna_worker_phase6uq_fosinit_completeness_20260810.csv:23: extra_fields=1`
- `work/luna_worker_phase6uq_fosinit_completeness_20260810.csv:24: extra_fields=1`
- `work/luna_worker_phase6uq_fosinit_completeness_20260810.csv:25: extra_fields=1`
- `work/luna_worker_phase6uq_fosinit_completeness_20260810.csv:26: extra_fields=1`
