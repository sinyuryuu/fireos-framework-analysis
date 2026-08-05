# Reproduction boundary

"
        "The raw capture is retained locally under the source directory passed to
"
        "`build_phase5cq_public_summary.py`. The public artifact is generated
"
        "without contacting the device.

"
        "```sh
"
        "python3 tools/scripts/build_phase5cq_public_summary.py --dry-run \
"
        "  --source adb/phase5/PHASE5CQ-ACCESSIBILITY-PENDINGINTENT-PS7331-T01 \
"
        "  --output artifacts/phase5cq/public-summary-20260805-01
"
        "```

"
        "The Accessibility service was manually enabled for the measurement.
"
        "Before package rollback, the device owner must manually disable that
"
        "service and its visible redirect toggle in Android Settings.
