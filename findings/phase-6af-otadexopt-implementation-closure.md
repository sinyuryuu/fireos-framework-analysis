# Phase 6AF：PS7331 `OtaDexoptService` implementation closure

## Scope

This correction closes the concrete implementation gap left in Phase 6AE. It
uses the saved PS7331 services VDEX and the already-preserved, read-only
`PHASE6AE-STATUS-20260805-01` capture. This parser did not contact the device.
No Binder transaction, OTA command, OOBE broadcast, package/settings mutation,
reboot, or partition operation was performed.

## Result

**Confirmed:** the installed PS7331 services VDEX contains
`com.android.server.pm.OtaDexoptService`, its `main()` registration under the
`otadexopt` service name, and its `onShellCommand()` bridge to
`OtaDexoptShellCommand`.

**Confirmed:** the preserved device capture reached the real service through
documented shell commands. `cmd otadexopt done` returned the service's
`IllegalStateException: done() called before prepare()` stack, including
`OtaDexoptService.java:176`, `OtaDexoptShellCommand.java:76`, and
`IOtaDexopt$Stub.onTransact`. `cmd otadexopt progress` returned `1.00`.

**Risk-rejected:** `prepare`, `next`, `cleanup`, and dexopt execution were not
run. Static code shows that `prepare` builds dexopt commands and can delete OAT
artifacts when space is low; `next` removes commands and can clear the list;
`cleanup` clears service state; `step` reaches an
`UnsupportedOperationException` in this build but was not invoked.

**Strong evidence:** this service boundary contains no HOME selection,
Fire-Launcher package comparison, privilege transition, or root path. The
absence of a method-local permission marker is only a bounded static result;
it is not an authorization bypass claim.

## Static locations

The authoritative installed VDEX is
`decompiled/baksmali/vdexExtractor/services/disassembly.log` (SHA-256 is in
`implementation.json`). The key locations are:

| Path | Location | Meaning |
|---|---:|---|
| `OtaDexoptService` | `482129` | class and source file declaration |
| `main(Context, PackageManagerService)` | `482249-482263` | constructs service, publishes `otadexopt`, moves A/B artifacts |
| `cleanup()` | `482460-482478` | clears command state and logs metrics; not invoked |
| `dexoptNextPackage()` | `482479-482489` | throws `UnsupportedOperationException`; not invoked |
| `getProgress()` | `482490-482513` | reads progress state; captured result `1.00` |
| `isDone()` | `482514-482532` | precondition/read path; captured `done()` exception |
| `nextDexoptCommand()` | `482533-482597` | removes/possibly clears command list; not invoked |
| `onShellCommand()` | `482598-482611` | delegates to `OtaDexoptShellCommand`; reached by capture |
| `prepare()` | `482613-482734` | builds dexopt command list and may delete OAT artifacts; not invoked |
| `OtaDexoptShellCommand` | `482735+` | maps `prepare`, `done`, `step`, `next`, `cleanup`, `progress` |
| `SystemServer` | `107990-108045` | starts service unless `mOnlyCore` or `config.disable_otadexopt` blocks it |

The adjacent PS7331 VDEX contains the same service-start shape and is retained
as provenance evidence; exact hashes and hit lines are in the artifact JSON.

## Security and research disposition

The service is a real shell-visible OTA dexopt control surface, but it is not a
safe launcher or privilege-escalation control surface. Future work is limited
to host-side comparison, documented read/precondition queries, or naturally
occurring OTA observation. Do not invoke `prepare`, `next`, `cleanup`, `step`,
private Binder transactions, or updater/recovery paths on the retail device.

## Reproduction

```sh
python3 tools/scripts/audit_phase6af_otadexopt_implementation.py --dry-run \
  --output /tmp/phase6af-artifact \
  --table-output /tmp/phase6af-methods.csv \
  --graph-output /tmp/phase6af-flow.mmd \
  --report-output /tmp/phase6af-report.md

python3 tools/scripts/audit_phase6af_otadexopt_implementation.py \
  --output artifacts/phase6af/otadexopt-implementation-closure-20260805-01 \
  --table-output output/tables/phase6af-otadexopt-implementation.csv \
  --graph-output output/call-graphs/phase6af-otadexopt-implementation.mmd \
  --report-output findings/phase-6af-otadexopt-implementation-closure.md
```
