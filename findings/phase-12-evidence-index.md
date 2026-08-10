# Phase 12 evidence index

Generated UTC: `2026-08-10T08:42:08.165371+00:00`

This index is host-only. It does not claim that a static caller, Binder
handle, update-binary sink, driver node, or source capability was reached
on the device. Every missing caller, identity, user scope, policy or sink
edge remains `UNKNOWN`.

## Worker row counts

| Input | Rows | CSV shape QA | SHA-256 manifest |
|---|---:|---|---|
| `existing-evidence` | 14 | 8 cols; malformed rows: 0 | `8babd269dd0a5857d46146c32da974529e1a3f01e05033ce59ccd39010c75174` |
| `binder-package` | 19 | 11 cols; malformed rows: 0 | `0745b0c4cb6463ce22a99b866fe13eb6356c74298cf6825829f93a49fc1cde48` |
| `ota` | 19 | 11 cols; malformed rows: 0 | `df393bb49ab8e2b96b333f9c76542d9a876a1bb923b4c0180a73ea6d527ffdec` |
| `driver` | 12 | 14 cols; malformed rows: 10 | `88764110307182b026876d08b2145f9d78f41f96a0e7b34ed306e6752ba3271b` |

## Baseline and generated inputs

- Baseline manifest: `dc8b8e551d63692885ec59990895d20d60bfe2319e886700803ff3028e1196e9`
- Baseline metadata: `8d365b4822bbb666f19b8049b4450c680ff592e973704e8607c8b427936e7773`
- Baseline report: `b1d69f2002150d8e4fdccafb84d7ae355cfb310aa947078f52052d4a95d6d479`
- Post-host guard manifest: `6ea5eca0828a747539937aea698eda91629f7bf1688a444804a0d034116ac040`
- Normalized table: `44c7418f8c6df21fad93a506fb4971b2c891c9f4def3a2eecbd7a4cbaa8776e1`

## Confidence rule

`Confirmed` is reserved for a directly observed or directly preserved
fact. `Strong evidence` still requires any explicitly listed missing edge
to be resolved before it becomes a reachability claim. `Unknown` means the
bounded corpus did not close the edge. `Disproved` applies only to the
specific tested route, not to every possible implementation.
