package com.google.android.finsky.setup;

/* JADX INFO: compiled from: PG */
/* JADX INFO: loaded from: classes4.dex */
@defpackage.bvzq
public class LauncherConfigurationReceiver extends defpackage.nwx {
    public defpackage.aoba a;
    public defpackage.ahmo b;
    public defpackage.aofc c;
    public defpackage.agyy d;
    public defpackage.azdc e;

    public LauncherConfigurationReceiver() {
            r0 = this;
            r0.<init>()
            return
    }

    private static defpackage.bhwd c(android.content.Intent r1, java.lang.String r2) {
            java.util.ArrayList r1 = r1.getStringArrayListExtra(r2)
            j$.util.Optional r1 = j$.util.Optional.ofNullable(r1)
            anzr r2 = new anzr
            r0 = 2
            r2.<init>(r0)
            j$.util.Optional r1 = r1.map(r2)
            biak r2 = defpackage.biak.a
            java.lang.Object r1 = r1.orElse(r2)
            bhwd r1 = (defpackage.bhwd) r1
            return r1
    }

    @Override // defpackage.nxe
    protected final defpackage.bhvb a() {
            r2 = this;
            r0 = 2548(0x9f4, float:3.57E-42)
            r1 = 2549(0x9f5, float:3.572E-42)
            nxd r0 = defpackage.nxd.a(r0, r1)
            java.lang.String r1 = "com.android.launcher3.action.FIRST_SCREEN_ACTIVE_INSTALLS"
            bhvb r0 = defpackage.bhvb.l(r1, r0)
            return r0
    }

    @Override // defpackage.nwx
    public final defpackage.btxk b(android.content.Context r18, android.content.Intent r19) {
            r17 = this;
            r1 = r17
            r0 = r19
            r2 = 0
            java.lang.String r3 = "Handling launcher configuration broadcast %s"
            r4 = 1
            java.lang.Object[] r5 = new java.lang.Object[r4]     // Catch: java.lang.Exception -> L2c7
            r5[r2] = r0     // Catch: java.lang.Exception -> L2c7
            com.google.android.finsky.utils.FinskyLog.f(r3, r5)     // Catch: java.lang.Exception -> L2c7
            java.lang.String r3 = "verificationToken"
            android.os.Parcelable r3 = r0.getParcelableExtra(r3)     // Catch: java.lang.Exception -> L2c7
            android.app.PendingIntent r3 = (android.app.PendingIntent) r3     // Catch: java.lang.Exception -> L2c7
            if (r3 != 0) goto L27
            java.lang.String r0 = "Receiver launcher configuration broadcast without verification token"
            java.lang.Object[] r3 = new java.lang.Object[r2]     // Catch: java.lang.Exception -> L23
            com.google.android.finsky.utils.FinskyLog.d(r0, r3)     // Catch: java.lang.Exception -> L23
            btxk r0 = defpackage.btxk.h     // Catch: java.lang.Exception -> L23
            return r0
        L23:
            r0 = move-exception
            r5 = r2
            goto L2c9
        L27:
            java.lang.String r5 = r3.getCreatorPackage()     // Catch: java.lang.Exception -> L2c7
            agyy r6 = r1.d     // Catch: java.lang.Exception -> L2c7
            java.lang.String r6 = r6.d()     // Catch: java.lang.Exception -> L2c7
            r7 = 2
            if (r6 == 0) goto L3b
            boolean r8 = r6.equals(r5)     // Catch: java.lang.Exception -> L23
            if (r8 == 0) goto L3b
            goto L64
        L3b:
            java.lang.String r8 = "Launcher configuration sender %s does not match current launcher %s"
            java.lang.Object[] r9 = new java.lang.Object[r7]     // Catch: java.lang.Exception -> L2c7
            r9[r2] = r5     // Catch: java.lang.Exception -> L2c7
            r9[r4] = r6     // Catch: java.lang.Exception -> L2c7
            com.google.android.finsky.utils.FinskyLog.f(r8, r9)     // Catch: java.lang.Exception -> L2c7
            ahmo r6 = r1.b     // Catch: java.lang.Exception -> L2c7
            java.lang.String r8 = "Setup"
            java.lang.String r9 = defpackage.aidy.B     // Catch: java.lang.Exception -> L2c7
            boolean r6 = r6.u(r8, r9)     // Catch: java.lang.Exception -> L2c7
            if (r6 == 0) goto L54
            goto L2b5
        L54:
            agyy r6 = r1.d     // Catch: java.lang.Exception -> L2c7
            android.content.pm.ApplicationInfo r6 = r6.b(r5, r4)     // Catch: java.lang.Exception -> L2c7
            agyy r8 = r1.d     // Catch: java.lang.Exception -> L2c7
            boolean r5 = r8.g(r5)     // Catch: java.lang.Exception -> L2c7
            if (r6 == 0) goto L2b5
            if (r5 == 0) goto L2b5
        L64:
            java.lang.String r3 = "hotseatItem"
            bhwd r3 = c(r0, r3)     // Catch: java.lang.Exception -> L2c7
            java.lang.String r5 = "widgetItem"
            bhwd r5 = c(r0, r5)     // Catch: java.lang.Exception -> L2c7
            java.lang.String r6 = "workspaceItem"
            bhwd r6 = c(r0, r6)     // Catch: java.lang.Exception -> L2c7
            java.lang.String r8 = "folderItem"
            bhwd r8 = c(r0, r8)     // Catch: java.lang.Exception -> L2c7
            java.lang.String r9 = "hotseatInstalledItems"
            bhwd r9 = c(r0, r9)     // Catch: java.lang.Exception -> L2c7
            java.lang.String r10 = "widgetInstalledItems"
            bhwd r10 = c(r0, r10)     // Catch: java.lang.Exception -> L2c7
            java.lang.String r11 = "workspaceInstalledItems"
            bhwd r11 = c(r0, r11)     // Catch: java.lang.Exception -> L2c7
            java.lang.String r12 = "folderInstalledItems"
            bhwd r0 = c(r0, r12)     // Catch: java.lang.Exception -> L2c7
            java.util.HashSet r12 = new java.util.HashSet     // Catch: java.lang.Exception -> L2c7
            r12.<init>(r3)     // Catch: java.lang.Exception -> L2c7
            r12.addAll(r5)     // Catch: java.lang.Exception -> L2c7
            r12.addAll(r6)     // Catch: java.lang.Exception -> L2c7
            r12.addAll(r8)     // Catch: java.lang.Exception -> L2c7
            r12.addAll(r9)     // Catch: java.lang.Exception -> L2c7
            r12.addAll(r10)     // Catch: java.lang.Exception -> L2c7
            r12.addAll(r11)     // Catch: java.lang.Exception -> L2c7
            r12.addAll(r0)     // Catch: java.lang.Exception -> L2c7
            java.lang.String r13 = "Received launcher configuration broadcast items:"
            java.lang.Object[] r14 = new java.lang.Object[r2]     // Catch: java.lang.Exception -> L2c7
            com.google.android.finsky.utils.FinskyLog.f(r13, r14)     // Catch: java.lang.Exception -> L2c7
            java.lang.String r13 = "\thotseat: %s"
            java.lang.Object[] r14 = new java.lang.Object[r4]     // Catch: java.lang.Exception -> L2c7
            r14[r2] = r3     // Catch: java.lang.Exception -> L2c7
            com.google.android.finsky.utils.FinskyLog.f(r13, r14)     // Catch: java.lang.Exception -> L2c7
            java.lang.String r13 = "\twidgets: %s"
            java.lang.Object[] r14 = new java.lang.Object[r4]     // Catch: java.lang.Exception -> L2c7
            r14[r2] = r5     // Catch: java.lang.Exception -> L2c7
            com.google.android.finsky.utils.FinskyLog.f(r13, r14)     // Catch: java.lang.Exception -> L2c7
            java.lang.String r13 = "\tshortcuts: %s"
            java.lang.Object[] r14 = new java.lang.Object[r4]     // Catch: java.lang.Exception -> L2c7
            r14[r2] = r6     // Catch: java.lang.Exception -> L2c7
            com.google.android.finsky.utils.FinskyLog.f(r13, r14)     // Catch: java.lang.Exception -> L2c7
            java.lang.String r13 = "\tfolder shortcuts: %s"
            java.lang.Object[] r14 = new java.lang.Object[r4]     // Catch: java.lang.Exception -> L2c7
            r14[r2] = r8     // Catch: java.lang.Exception -> L2c7
            com.google.android.finsky.utils.FinskyLog.f(r13, r14)     // Catch: java.lang.Exception -> L2c7
            java.lang.String r13 = "\thotseat installed: %s"
            java.lang.Object[] r14 = new java.lang.Object[r4]     // Catch: java.lang.Exception -> L2c7
            r14[r2] = r9     // Catch: java.lang.Exception -> L2c7
            com.google.android.finsky.utils.FinskyLog.f(r13, r14)     // Catch: java.lang.Exception -> L2c7
            java.lang.String r13 = "\twidgets installed: %s"
            java.lang.Object[] r14 = new java.lang.Object[r4]     // Catch: java.lang.Exception -> L2c7
            r14[r2] = r10     // Catch: java.lang.Exception -> L2c7
            com.google.android.finsky.utils.FinskyLog.f(r13, r14)     // Catch: java.lang.Exception -> L2c7
            java.lang.String r13 = "\tshortcuts installed: %s"
            java.lang.Object[] r14 = new java.lang.Object[r4]     // Catch: java.lang.Exception -> L2c7
            r14[r2] = r11     // Catch: java.lang.Exception -> L2c7
            com.google.android.finsky.utils.FinskyLog.f(r13, r14)     // Catch: java.lang.Exception -> L2c7
            java.lang.String r13 = "\tfolder shortcuts installed: %s"
            java.lang.Object[] r14 = new java.lang.Object[r4]     // Catch: java.lang.Exception -> L2c7
            r14[r2] = r0     // Catch: java.lang.Exception -> L2c7
            com.google.android.finsky.utils.FinskyLog.f(r13, r14)     // Catch: java.lang.Exception -> L2c7
            java.util.HashMap r13 = new java.util.HashMap     // Catch: java.lang.Exception -> L2c7
            r13.<init>()     // Catch: java.lang.Exception -> L2c7
            java.util.Iterator r12 = r12.iterator()     // Catch: java.lang.Exception -> L2c7
        L106:
            boolean r14 = r12.hasNext()     // Catch: java.lang.Exception -> L2c7
            if (r14 == 0) goto L1b7
            java.lang.Object r14 = r12.next()     // Catch: java.lang.Exception -> L2c7
            java.lang.String r14 = (java.lang.String) r14     // Catch: java.lang.Exception -> L2c7
            aoaf r15 = defpackage.aoaf.a     // Catch: java.lang.Exception -> L2c7
            bqma r15 = r15.aV()     // Catch: java.lang.Exception -> L2c7
            boolean r16 = r3.contains(r14)     // Catch: java.lang.Exception -> L2c7
            if (r16 != 0) goto L128
            boolean r16 = r9.contains(r14)     // Catch: java.lang.Exception -> L23
            if (r16 == 0) goto L125
            goto L128
        L125:
            r18 = r7
            goto L140
        L128:
            r18 = r7
            bqmg r7 = r15.b     // Catch: java.lang.Exception -> L2c7
            boolean r7 = r7.bm()     // Catch: java.lang.Exception -> L2c7
            if (r7 != 0) goto L135
            r15.J()     // Catch: java.lang.Exception -> L23
        L135:
            bqmg r7 = r15.b     // Catch: java.lang.Exception -> L2c7
            aoaf r7 = (defpackage.aoaf) r7     // Catch: java.lang.Exception -> L2c7
            int r2 = r7.b     // Catch: java.lang.Exception -> L2c7
            r2 = r2 | r4
            r7.b = r2     // Catch: java.lang.Exception -> L2c7
            r7.c = r4     // Catch: java.lang.Exception -> L2c7
        L140:
            boolean r2 = r5.contains(r14)     // Catch: java.lang.Exception -> L2c7
            if (r2 != 0) goto L14c
            boolean r2 = r10.contains(r14)     // Catch: java.lang.Exception -> L2c7
            if (r2 == 0) goto L163
        L14c:
            bqmg r2 = r15.b     // Catch: java.lang.Exception -> L2c7
            boolean r2 = r2.bm()     // Catch: java.lang.Exception -> L2c7
            if (r2 != 0) goto L157
            r15.J()     // Catch: java.lang.Exception -> L2c7
        L157:
            bqmg r2 = r15.b     // Catch: java.lang.Exception -> L2c7
            aoaf r2 = (defpackage.aoaf) r2     // Catch: java.lang.Exception -> L2c7
            int r7 = r2.b     // Catch: java.lang.Exception -> L2c7
            r7 = r7 | 2
            r2.b = r7     // Catch: java.lang.Exception -> L2c7
            r2.d = r4     // Catch: java.lang.Exception -> L2c7
        L163:
            boolean r2 = r6.contains(r14)     // Catch: java.lang.Exception -> L2c7
            if (r2 != 0) goto L16f
            boolean r2 = r11.contains(r14)     // Catch: java.lang.Exception -> L2c7
            if (r2 == 0) goto L186
        L16f:
            bqmg r2 = r15.b     // Catch: java.lang.Exception -> L2c7
            boolean r2 = r2.bm()     // Catch: java.lang.Exception -> L2c7
            if (r2 != 0) goto L17a
            r15.J()     // Catch: java.lang.Exception -> L2c7
        L17a:
            bqmg r2 = r15.b     // Catch: java.lang.Exception -> L2c7
            aoaf r2 = (defpackage.aoaf) r2     // Catch: java.lang.Exception -> L2c7
            int r7 = r2.b     // Catch: java.lang.Exception -> L2c7
            r7 = r7 | 4
            r2.b = r7     // Catch: java.lang.Exception -> L2c7
            r2.e = r4     // Catch: java.lang.Exception -> L2c7
        L186:
            boolean r2 = r8.contains(r14)     // Catch: java.lang.Exception -> L2c7
            if (r2 != 0) goto L192
            boolean r2 = r0.contains(r14)     // Catch: java.lang.Exception -> L2c7
            if (r2 == 0) goto L1a9
        L192:
            bqmg r2 = r15.b     // Catch: java.lang.Exception -> L2c7
            boolean r2 = r2.bm()     // Catch: java.lang.Exception -> L2c7
            if (r2 != 0) goto L19d
            r15.J()     // Catch: java.lang.Exception -> L2c7
        L19d:
            bqmg r2 = r15.b     // Catch: java.lang.Exception -> L2c7
            aoaf r2 = (defpackage.aoaf) r2     // Catch: java.lang.Exception -> L2c7
            int r7 = r2.b     // Catch: java.lang.Exception -> L2c7
            r7 = r7 | 8
            r2.b = r7     // Catch: java.lang.Exception -> L2c7
            r2.f = r4     // Catch: java.lang.Exception -> L2c7
        L1a9:
            bqmg r2 = r15.D()     // Catch: java.lang.Exception -> L2c7
            aoaf r2 = (defpackage.aoaf) r2     // Catch: java.lang.Exception -> L2c7
            r13.put(r14, r2)     // Catch: java.lang.Exception -> L2c7
            r7 = r18
            r2 = 0
            goto L106
        L1b7:
            r18 = r7
            aoba r0 = r1.a     // Catch: java.lang.Exception -> L2c7
            java.util.Set r2 = r13.entrySet()     // Catch: java.lang.Exception -> L2c7
            java.util.Iterator r2 = r2.iterator()     // Catch: java.lang.Exception -> L2c7
        L1c3:
            boolean r3 = r2.hasNext()     // Catch: java.lang.Exception -> L2c7
            if (r3 == 0) goto L1ec
            java.lang.Object r3 = r2.next()     // Catch: java.lang.Exception -> L2c7
            java.util.Map$Entry r3 = (java.util.Map.Entry) r3     // Catch: java.lang.Exception -> L2c7
            java.lang.Object r5 = r3.getKey()     // Catch: java.lang.Exception -> L2c7
            java.lang.String r5 = (java.lang.String) r5     // Catch: java.lang.Exception -> L2c7
            aoax r5 = r0.b(r5)     // Catch: java.lang.Exception -> L2c7
            if (r5 == 0) goto L1c3
            java.lang.Object r3 = r3.getValue()     // Catch: java.lang.Exception -> L2c7
            aoaf r3 = (defpackage.aoaf) r3     // Catch: java.lang.Exception -> L2c7
            r5.s(r3)     // Catch: java.lang.Exception -> L2c7
            java.lang.String r3 = r5.m()     // Catch: java.lang.Exception -> L2c7
            r0.j(r3)     // Catch: java.lang.Exception -> L2c7
            goto L1c3
        L1ec:
            azdc r0 = r1.e     // Catch: java.lang.Exception -> L2c7
            boolean r0 = r0.S()     // Catch: java.lang.Exception -> L2c7
            if (r0 == 0) goto L2b2
            azdc r0 = r1.e     // Catch: java.lang.Exception -> L2c7
            boolean r0 = r0.U()     // Catch: java.lang.Exception -> L2c7
            if (r0 != 0) goto L2b2
            aofc r0 = r1.c     // Catch: java.lang.Exception -> L2c7
            bunw r2 = r0.h     // Catch: java.lang.Exception -> L2c7
            java.lang.Object r3 = r2.a()     // Catch: java.lang.Exception -> L2c7
            aoba r3 = (defpackage.aoba) r3     // Catch: java.lang.Exception -> L2c7
            azdc r5 = r3.r     // Catch: java.lang.Exception -> L2c7
            boolean r5 = r5.S()     // Catch: java.lang.Exception -> L2c7
            if (r5 != 0) goto L213
            int r3 = defpackage.bhuq.d     // Catch: java.lang.Exception -> L2c7
            bhuq r3 = defpackage.biae.a     // Catch: java.lang.Exception -> L2c7
            goto L257
        L213:
            java.util.Map r3 = r3.d     // Catch: java.lang.Exception -> L2c7
            java.util.Collection r3 = r3.values()     // Catch: java.lang.Exception -> L2c7
            j$.util.stream.Stream r3 = j$.util.Collection.EL.stream(r3)     // Catch: java.lang.Exception -> L2c7
            anvf r5 = new anvf     // Catch: java.lang.Exception -> L2c7
            r6 = 11
            r5.<init>(r6)     // Catch: java.lang.Exception -> L2c7
            j$.util.stream.Stream r3 = r3.filter(r5)     // Catch: java.lang.Exception -> L2c7
            anvf r5 = new anvf     // Catch: java.lang.Exception -> L2c7
            r6 = 10
            r5.<init>(r6)     // Catch: java.lang.Exception -> L2c7
            j$.util.stream.Stream r3 = r3.filter(r5)     // Catch: java.lang.Exception -> L2c7
            anzr r5 = new anzr     // Catch: java.lang.Exception -> L2c7
            r5.<init>(r6)     // Catch: java.lang.Exception -> L2c7
            ajov r6 = new ajov     // Catch: java.lang.Exception -> L2c7
            r7 = 19
            r6.<init>(r7)     // Catch: java.lang.Exception -> L2c7
            java.util.Comparator r5 = j$.util.Comparator.CC.comparing(r5, r6)     // Catch: java.lang.Exception -> L2c7
            j$.util.stream.Stream r3 = r3.sorted(r5)     // Catch: java.lang.Exception -> L2c7
            r5 = 15
            j$.util.stream.Stream r3 = r3.limit(r5)     // Catch: java.lang.Exception -> L2c7
            int r5 = defpackage.bhuq.d     // Catch: java.lang.Exception -> L2c7
            j$.util.stream.Collector r5 = defpackage.bhrq.a     // Catch: java.lang.Exception -> L2c7
            java.lang.Object r3 = r3.collect(r5)     // Catch: java.lang.Exception -> L2c7
            bhuq r3 = (defpackage.bhuq) r3     // Catch: java.lang.Exception -> L2c7
        L257:
            boolean r5 = r3.isEmpty()     // Catch: java.lang.Exception -> L2c7
            if (r5 == 0) goto L25f
            r0 = 0
            goto L2a3
        L25f:
            r5 = 0
            java.lang.Object r6 = r3.get(r5)     // Catch: java.lang.Exception -> L2c7
            aoax r6 = (defpackage.aoax) r6     // Catch: java.lang.Exception -> L2c7
            java.lang.String r5 = r6.j()     // Catch: java.lang.Exception -> L2c7
            int r6 = r3.size()     // Catch: java.lang.Exception -> L2c7
            java.lang.Integer r6 = java.lang.Integer.valueOf(r6)     // Catch: java.lang.Exception -> L2c7
            java.lang.String r5 = com.google.android.finsky.utils.FinskyLog.a(r5)     // Catch: java.lang.Exception -> L2c7
            r7 = r18
            java.lang.Object[] r7 = new java.lang.Object[r7]     // Catch: java.lang.Exception -> L2c7
            r16 = 0
            r7[r16] = r6     // Catch: java.lang.Exception -> L2c7
            r7[r4] = r5     // Catch: java.lang.Exception -> L2c7
            java.lang.String r5 = "setup::RES: Start restore of %d homescreen packages for acct:%s"
            com.google.android.finsky.utils.FinskyLog.f(r5, r7)     // Catch: java.lang.Exception -> L2c7
            int r5 = r3.size()     // Catch: java.lang.Exception -> L2c7
            r6 = 0
        L28a:
            r7 = 5
            if (r6 >= r5) goto L29f
            java.lang.Object r8 = r3.get(r6)     // Catch: java.lang.Exception -> L2c7
            aoax r8 = (defpackage.aoax) r8     // Catch: java.lang.Exception -> L2c7
            java.lang.Object r9 = r2.a()     // Catch: java.lang.Exception -> L2c7
            aoba r9 = (defpackage.aoba) r9     // Catch: java.lang.Exception -> L2c7
            r9.k(r8, r7, r4)     // Catch: java.lang.Exception -> L2c7
            int r6 = r6 + 1
            goto L28a
        L29f:
            int r0 = r0.y(r3, r7)     // Catch: java.lang.Exception -> L2c7
        L2a3:
            java.lang.String r2 = "setup::RES: Restoring %d homescreen packages."
            java.lang.Integer r0 = java.lang.Integer.valueOf(r0)     // Catch: java.lang.Exception -> L2c7
            java.lang.Object[] r3 = new java.lang.Object[r4]     // Catch: java.lang.Exception -> L2c7
            r16 = 0
            r3[r16] = r0     // Catch: java.lang.Exception -> L2c7
            com.google.android.finsky.utils.FinskyLog.f(r2, r3)     // Catch: java.lang.Exception -> L2c7
        L2b2:
            btxk r0 = defpackage.btxk.b
            return r0
        L2b5:
            java.lang.String r0 = "Launcher configuration sender %s is not qualified to send this broadcast"
            java.lang.String r2 = r3.getCreatorPackage()     // Catch: java.lang.Exception -> L2c7
            java.lang.Object[] r3 = new java.lang.Object[r4]     // Catch: java.lang.Exception -> L2c7
            r16 = 0
            r3[r16] = r2     // Catch: java.lang.Exception -> L2c7
            com.google.android.finsky.utils.FinskyLog.d(r0, r3)     // Catch: java.lang.Exception -> L2c7
            btxk r0 = defpackage.btxk.f     // Catch: java.lang.Exception -> L2c7
            return r0
        L2c7:
            r0 = move-exception
            r5 = 0
        L2c9:
            java.lang.Object[] r2 = new java.lang.Object[r5]
            java.lang.String r3 = "Exception receiving launcher configuration broadcast"
            com.google.android.finsky.utils.FinskyLog.e(r0, r3, r2)
            btxk r0 = defpackage.btxk.c
            return r0
    }

    @Override // defpackage.nxe
    protected final void f() {
            r1 = this;
            java.lang.Class<aoal> r0 = defpackage.aoal.class
            java.lang.Object r0 = defpackage.akni.f(r0)
            aoal r0 = (defpackage.aoal) r0
            r0.iy(r1)
            return
    }

    @Override // defpackage.nxe
    protected final int h() {
            r1 = this;
            r0 = 20
            return r0
    }
}
