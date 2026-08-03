# Phase 3C preferred activity analysis

Before mutation, preferred XML selected com.amazon.firelauncher/.Launcher. After set-home-activity
targeted p0, XML selected org.fireosresearch.home.p0/org.fireosresearch.home.HomeActivity; the preferred dump reported mAlways=true
with MAIN, HOME, and DEFAULT. Resolver still returned priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true | com.amazon.firelauncher/.Launcher.

After one reboot, p0 record org.fireosresearch.home.p0/org.fireosresearch.home.HomeActivity remained stored, but resolver and
foreground remained Fire. Rollback wrote com.amazon.firelauncher/.Launcher back and p0 uninstall
returned exit 0.

Decision tree:

    set-home-activity(p0)
      -> record written: exact filter, mAlways=true
      -> p0 enabled/queryable: effective priority 0
      -> no separate active persistent HOME record observed
      -> chooseBestActivity compares Fire priority 50 first
      -> ordinary priority-0 preferred record is not selected
      -> resolver and Home key remain Fire
      -> reboot preserves record, not effectiveness

已證實: writable ordinary preferred state is not sufficient.
高可信推論: the observed failure point is candidate ranking before the
ordinary preferred tie branch.
待驗證: a concrete non-null Amazon resolve callback for this exact intent.
