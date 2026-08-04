# Phase 6C image policy evidence index

所有證據均為 host-only。沒有 device contact、image mount/write、ELF execution、
futex trigger、kernel memory access 或 payload generation。

## E6C-IMG-01 — image identity

- Source: preserved PS7331 firmware artifacts
- Files: `firmware/extracted/PS7331/system.img`, `firmware/extracted/PS7331/vendor.img`
- SHA-256: `da8a935484de24251e890fbf4e7dd9155567ebe158fc255d43684ea14c62b1e5`; `d1db5a5349d046361710bd6966adb7ef88dc4ddc550295e8c1926cb279f213eb`
- Command: `file ...; shasum -a 256 ...`
- Observed: ext4-family filesystem images; hashes preserved in `image-sha256sums.txt`.
- Interpretation: exactness of preserved input files; not a runtime load proof.
- Confidence: **已證實**

## E6C-IMG-02 — read-only extraction boundary

- Source: `tools/scripts/extract_phase6c_image_policy_readonly.sh`
- Files: `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/metadata.txt`, `safety.txt`, `extracted-file-manifest.tsv`, `output-sha256sums.txt`
- SHA-256: metadata `269a0910e3406aee4f6f78ba0c435868e1ee28f03c758369b71cd7e6acf43878`; manifest `a7cca925a8212b304a21b23862599b94d2a094f9870a7846b5badebc0096eee1`; safety `d6a41b2f4b92f892ad108606a1eda60b782bea0427a13d1b14a18fd597acf684`
- Timestamp: 2026-08-04 host run
- Observed: 281 recovered raw files, including root `/init`; all debugfs exit code files are 0; mounted/written/device flags false.
- Interpretation: selected filesystem coverage only.
- Confidence: **已證實**

## E6C-IMG-03 — service seccomp profiles

- Source: extracted `/system/etc/seccomp_policy` and `/vendor/etc/seccomp_policy`
- Files: five profiles listed in `findings/phase-6c-image-policy-extraction.md`
- Observed: generic `futex: 1`; no named requeue-PI rule.
- Interpretation: service profile observation; does not classify app-domain operation filtering.
- Confidence: **已證實（限定於 profiles）**

## E6C-IMG-04 — zygote launch surface

- Source: extracted root init files
- File: `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/root/init.zygote64_32.rc`
- Observed: root-owned `zygote` and `zygote_secondary` services invoke app_process binaries.
- Interpretation: Android zygote startup surface exists; no requeue-PI caller inference.
- Confidence: **已證實**

## E6C-IMG-05 — native futex/seccomp surface

- Source: host `strings` and SHA-256 over extracted native files
- Files: `system/bin/app_process64`, `system/bin/linker64`, `system/lib64/libc.so`, `libandroid_runtime.so`, `libart.so`
- Observed: libc PI helper symbols; libandroid_runtime seccomp setup symbols; linker seccomp/no-new-privs diagnostics; no named requeue-PI marker.
- Interpretation: capability/setup surface only, not a runtime caller or allow/deny result.
- Confidence: **已證實（bounded static observation）**

## E6C-IMG-06 — app/zygote SELinux labels and access surface

- Source: extracted `plat_seapp_contexts`, `plat_sepolicy.cil`, `vendor_sepolicy.cil`
- Observed: target-SDK-28 apps map to `untrusted_app`; zygote/appdomain and selected vendor ioctl rules exist.
- Interpretation: label/policy surface; does not authorize a driver command or kernel exploit.
- Confidence: **已證實（static policy text）**

## E6C-IMG-07 — alternate rootable policy files and init loader surface

- Source: `tools/scripts/audit_phase6c_selinux_policy_variants.py`
- Files: `artifacts/phase6c/phase6c-selinux-variant-audit-20260804-02/selinux-policy-variant-audit.json`, `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/root/init`, `artifacts/phase6c/phase6c-init-loader-markers-20260804-01.txt`
- SHA-256: variant JSON `de0ee3c0d4182d8ca24924962c0306acf7c2a7c6731389c0e32514710e15dfbb`; init `e72ed4e90d73b88be341985ebd624725b67d67967d04157317456233e15f31fd`; marker extract `4e3076f71580492533c7d77521d42e49ae32107216178ae719a53ed2fcbcc1e1`
- Observed: standard/rootable policy files differ; the compiled init contains rootable and standard policy path strings; literal filename scan has one hit, in `/init`.
- Interpretation: compiled loader support is a static lead; active runtime selection and boot property branch remain unknown.
- Confidence: **已證實（artifact difference）／待驗證（runtime selection）**

## E6C-IMG-08 — bounded marker audit

- Source: `tools/scripts/audit_phase6c_installed_artifacts.py`
- Files: `artifacts/phase6c/phase6c-image-policy-marker-audit-20260804-04/installed-artifact-policy.json`, `artifact-inventory.csv`, `marker-hits.csv`
- SHA-256: JSON `8b1db7205b1293174f0d2e3e9baa264a2a7233c366c87ec567be6938f4c4d8e5`; inventory `6a8471fcf119566205dbb8788d37ddef0e1d1c9b39fa2096762e456db4983fef`; hits `a7e44423fd233218703c344cfb6632b83aa8fb763f24ac207ba7c7309d502366`
- Observed: 281 raw files; named requeue-PI markers 0; generic futex policy lines 5; host-only flags true.
- Interpretation: bounded negative/positive marker observation only.
- Confidence: **已證實（bounded scan）**

## E6C-IMG-09 — GhostLock boundary

- Sources: `findings/phase-6b-host-layout-model.md`, `findings/phase-6c-lab-readiness.md`, `findings/phase-6c-requeue-precondition-model.md`
- Observed: stack-resident waiter model, lab status `NOT_READY`, proxy path requires stateful paired waiter conditions.
- Interpretation: runtime mismatch, residue, memory effect and root remain unobserved.
- Confidence: **高可信推論／待驗證**

## E6C-IMG-10 — current SELinux boot-property context

- Source: prior selected-serial read-only device baseline
- File: `device/fireos-config/CONFIG-20260803-02/device_properties.txt`
- SHA-256: `dc9ac733476f037073b2046b0c281423010b4e4d7e1b3a74313119d0275d86a6`
- Observed: `ro.boot.selinux=enforcing`; `ro.boot.unlocked_kernel=false` in the same snapshot.
- Interpretation: current boot context is enforcing/locked in that snapshot; it does not prove which init policy branch was selected or establish root.
- Confidence: **已證實（snapshot-scoped）／待驗證（policy selection）**

## Safety exclusions

因風險拒絕：stock-device `FUTEX_CMP_REQUEUE_PI`／`WAIT_REQUEUE_PI` trigger、paired
waiter、race scheduling、single-shot panic、ION/pipe heap shaping、KASLR slide
calculation from live kernel, kernel memory read/write, unknown ioctl and privilege
transition payload. These are not hidden in the scripts or artifacts above.
