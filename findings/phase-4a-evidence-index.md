# Phase 4A evidence index

## P4A-MODEL-001

- Source: `tools/scripts/model_aosp9_home_resolution.py` and unit tests
- File: `tests/test_aosp9_home_resolution.py`
- Command: `python3 -m unittest tests/test_aosp9_home_resolution.py`
- Observed: Fire priority 50 is selected before p0 ordinary preferred lookup;
  tie control selects the ordinary preferred target.
- Confidence: 已證實

## P4A-METHOD-001 … P4A-METHOD-008

- Source: AOSP r1/r61 and Fire decompiled method comparison
- Files: `output/tables/phase-4a-method-diff.csv`,
  `findings/phase-4a-fireos-resolver-method-diff.md`
- Observed: central chooser/preferred branches are AOSP-shaped; Fire adds
  resolver callback/filter boundaries; one query method has a decompiler gap.
- Confidence: 已證實 for source locations; 高可信推論 for equivalence; 待驗證 for callback return values.

## P4A-DEVICE-001

- Source: Phase 3C controlled p0 experiment
- Files: `adb/phase3c/PHASE3C-PREFERRED-P0-03/` and
  `findings/phase-3c-evidence-index.md`
- Observed: mAlways=true p0 preferred record persisted but Fire remained the
  resolver and foreground through Home, explicit HOME, lock/unlock and reboot.
- Confidence: 已證實
