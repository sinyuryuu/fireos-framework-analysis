# Phase 5BV evidence index

## P5BV-MODEL-001

- Source: Host-only synthetic semantic model
- File: `artifacts/phase5/phase5bv-ghostlock-semantic-model-20260804-01/semantic-model.json`
- SHA-256: `6cbb9e44cfd19d1b5d484d49f707b611f8028e71dae7bf67d9e273d4c740a483`
- Test ID: `P5BV-HOST-MODEL-01`
- Timestamp: `2026-08-04`
- Command: `python3 -B tools/scripts/model_phase5bv_ghostlock_semantics.py --output ...`
- Observed result: `semantic_mismatch_reproduced=true`; `fixed_cleanup_clears_waiter_task=true`.
- Interpretation: The proxy-waiter/current cleanup mismatch is reproduced in a bounded model.
- Confidence: **Confirmed** for the model; **Strong evidence** when mapped to the source markers.
- Related hypothesis: PS7331 pre-fix semantic is the relevant defect shape.

## P5BV-TEST-001

- Source: Unit test suite
- File: `tests/test_phase5bv_ghostlock_semantics.py`
- SHA-256: `cd65e1271eb5d73ded7b30c23a1e414929489511849c26213eb864a5fae77699`
- Test ID: `P5BV-HOST-UNIT-01`
- Timestamp: `2026-08-04`
- Command: `python3 -B -m unittest discover -s tests -p 'test_phase5bv_ghostlock_semantics.py'`
- Observed result: 4 tests passed.
- Interpretation: The model checks proxy mismatch, fixed cleanup, non-proxy control and bounded verdict flags.
- Confidence: **Confirmed**
- Related hypothesis: none; reproducibility control.

## P5BV-SOURCE-001

- Source: PS7331 build-selected `rtmutex.c`
- File: `artifacts/phase5/ps7331-full-source-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c`
- SHA-256: `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde`
- Test ID: `P5BV-SOURCE-MAP-01`
- Timestamp: `2026-08-04`
- Command: source line review and prior semantic checker
- Observed result: proxy API documentation, proxy error call and current-task cleanup are present at the cited lines.
- Interpretation: Model inputs are grounded in the selected PS7331 source.
- Confidence: **Confirmed**
- Related hypothesis: model maps to the PS7331 pre-fix pattern.

## P5BV-SAFETY-001

- Source: model script and result metadata
- File: `artifacts/phase5/phase5bv-ghostlock-semantic-model-20260804-01/sha256sums.txt`
- SHA-256: `f523b01a51480a0160e40370c3ce0f7ee5201d5c2351c5d12350e3e2c0cd7f99`
- Test ID: `P5BV-SAFETY-01`
- Timestamp: `2026-08-04`
- Command: Python model and unittest only
- Observed result: no device I/O, kernel execution, exploit payload or address output.
- Interpretation: Host-only semantic verification.
- Confidence: **Confirmed**
- Related hypothesis: safety boundary.
