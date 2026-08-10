# Phase 6X evidence index

All rows are reproduced in `output/tables/phase6x-control-surface.csv` and
`output/tables/phase6x-test-reconciliation.csv`. The input manifest records
the exact hashes used to generate them.

## Verdict rules

- **已證實 / Confirmed:** direct saved observation or exact static method.
- **高可信推論:** multiple evidence classes agree, but a caller/effect edge is
  still bounded.
- **待驗證 / UNKNOWN:** missing provenance, publication, identity, user scope,
  or runtime edge; not evidence of a bypass.
- **已排除 / Disproved:** the stated route was tested or statically bounded
  and did not produce the claimed effect.
- **因風險拒絕測試:** execution would require unknown transaction codes,
  driver/OTA/recovery writes, exploit payloads, or irrecoverable device state.

## Counts

- Control rows: `78`
- Reconciled route rows: `15`
- Status counts: `{'UNKNOWN': 33, 'INTEGRATED': 10, 'CONFIRMED_NO_ENTRY': 3, 'CONFIRMED_NOT_HOME_WRITER': 1, 'UNKNOWN_LAYOUT_MISMATCH': 1, 'NEW_DIFFERENCE_STATIC_ONLY': 3, 'excluded_adjacent_version': 1, 'excluded_host_derived': 1, 'duplicate_no_new_gap': 1, 'duplicate_unknown_boundary': 1, 'NEW_SOURCE_EVIDENCE': 2, 'PRECISE_NEGATIVE_PLUS_SOURCE': 1, 'PRECISE_NEGATIVE': 2, 'NEW_STATIC_LOW_PROTECTION_NO_SINK': 3, 'NEW_STATIC_DEFINITION_NO_SINK': 1, 'STATIC_CONFIRMED_NUMERIC_USER_UNKNOWN': 1, 'STATIC_SINK_CONFIRMED_EXACT_USER_UNKNOWN': 1, 'STATIC_EXPORTED_POLICY_SINK_CALLER_UNKNOWN': 1, 'STATIC_PROTECTED_ACTION_POLICY_SINK_CALLER_UNKNOWN': 1, 'STATIC_PERMISSION_HOLDER_UNKNOWN': 2, 'STATIC_REGISTRATION_ONLY_CALLER_AND_SINK_UNKNOWN': 1, 'CONFIRMED_EXISTING_BOUNDARY_DEDUPED': 1, 'OBSERVED_READ_ONLY': 6}`
- Confidence counts: `{'static direct': 18, 'UNKNOWN': 28, 'static manifest': 1, 'static file sink': 1, 'High static': 3, 'high': 8, 'high source, low caller': 2, 'high source, medium classification': 1, 'high for archive path negative': 1, 'medium': 5, 'high declaration; low reachability': 3, 'medium declaration; low reachability': 1, 'Confirmed observation': 6}`
