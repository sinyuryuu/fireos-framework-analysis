# Phase 4A core hypotheses summary

| Hypothesis | Verdict | Basis |
|---|---|---|
| H1: ranking fields are considered before ordinary preferred | 已證實 | AOSP r1/r61 source, Fire corresponding method, offline model, Phase 3C device result |
| H2: selected core resolver is AOSP-shaped and no core Fire package hardcode is needed | 高可信推論 | method comparison and model replay |
| H2 global form: no Amazon callback/filter can affect HOME | 待驗證 | Fire has pre-PM resolve callback and resolver-index filter callback |
| ordinary `mAlways=true` record can cross priority 50 vs 0 | 已排除 | exact Phase 3C write + resolver and reboot result |
| direct Fire package hardcode in inspected chooser | 已排除（bounded scope） | no literal in selected PackageManagerService chooser ranges |
| unknown callback return / candidate filtering behavior | 待驗證 | implementation result not available in checked-in evidence |
