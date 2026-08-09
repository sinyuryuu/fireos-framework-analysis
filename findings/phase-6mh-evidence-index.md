# Phase 6MH evidence index

| Evidence ID | Source / file | SHA-256 | Observation | Confidence |
|---|---|---|---|---|
| 6MH-SCAN-001 | `artifacts/phase6mh-package-state-writers-20260810-01/summary.json` | `c8bcd0cda741aa21534a5aebc7995c7daa007f669a14b1ec7b913b6bbf055cc4` | 21 setter callsites: 11 component and 10 application calls; host-only, no Binder transaction or device mutation. | **Confirmed** |
| 6MH-CALLS-001 | `output/tables/phase6mh-package-state-writers.csv` | `39ce24194ecead7109894d6bae3cfcf631118c9181ec446dc70a6dd3354f231a` | Every indexed callsite includes source line, class, method, scope observation, nearby literals, and instruction callsite. | **Confirmed** |
| 6MH-KFT-001 | `fosservices/disassembly.log:54310-54324` | VDEX `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` | KFT state writer includes Fire literal but takes supplied `UserInfo.id`; prior evidence classifies it as child/profile scoped. | **Confirmed** |
| 6MH-POLICY-001 | `fosservices/disassembly.log:293712-293738`; `findings/phase-6ce-product-policy-firelauncher-boundary.md` | VDEX `ecbe62...5151c`; Phase 6CE artifacts hash the policy files | Product Policy action is trusted and policy-file/user-list driven; exact PS7331 policy inputs contain no Fire Launcher entry. | **Confirmed** |
| 6MH-ESPRESSO-001 | `fosservices/disassembly.log:191881,192065` | VDEX `ecbe62...5151c` | Espresso toggles a gated boot-complete receiver map; no HOME/Fire target was established. | **Strong evidence** |
| 6MH-SHELL-001 | `services/disassembly.log:500744-500765` | `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53` | Standard shell setter path reaches the known PMS gate; the disproved Fire component test was not repeated. | **Confirmed** |
| 6MH-FOSINIT-001 | `findings/phase-6jd-fosinit-registration-audit-closure.md` | registration-manifest hash recorded there | Full 123 PS7331 `*_fosinit.xml` registration corpus produced no new User-0 HOME/preferred/Fire state writer. | **Strong evidence** |
| 6MH-GRAPH-001 | `output/call-graphs/phase6mh-package-state-writers.mmd` | `1a704d1b44f2c8d05b8fadf1ec7fad1a9e4873a3064cbe6282b1b6a717049f2d` | Graph separates KFT child scope, Product Policy, Espresso, standard shell/PMS, and HOME objective. | **Confirmed** |
