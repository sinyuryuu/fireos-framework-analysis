# Phase 6A — benign PI-futex lock reachability smoke test

本測試只驗證 shell domain 能否進入一次 uncontended
FUTEX_LOCK_PI_PRIVATE／FUTEX_UNLOCK_PI_PRIVATE。它不是 GhostLock
requeue-PI reproducer，也不是 exploit。

## Safety boundary

- 不使用 FUTEX_WAIT_REQUEUE_PI 或 FUTEX_CMP_REQUEUE_PI；
- 不建立多執行緒 race；
- 不安排 deadlock 或 error cleanup；
- 不讀寫 kernel memory；
- 不改變 uid/gid/credential；
- 不修改 boot、system、userdata 或 partition；
- 測試 binary 只暫存於 /data/local/tmp，測試後刪除。

Exit code：

- 0：lock 與 unlock 都回傳 0；
- 11：lock 回傳非零；
- 12：unlock 回傳非零。

Exit code 11/12 只代表 smoke test 失敗，不代表 GhostLock 不可達。

## Build and execution record

Source：

tools/test-phase6a/pi_lock_smoke.c

Build script：

tools/scripts/build_phase6a_pi_lock_smoke.sh

Build command：

    tools/scripts/build_phase6a_pi_lock_smoke.sh \
      --output artifacts/phase6a/phase6a-pi-lock-smoke-T01/pi_lock_smoke

實機執行必須保存：

- device serial；
- build fingerprint；
- binary SHA-256；
- push path；
- stdout/stderr；
- exit code；
- before/after logcat snapshot；
- cleanup result；
- binary removal result。

本測試不會提供 requeue-PI、identity mismatch、cleanup residue 或 root
證據；它最多只能把「普通 PI futex syscall 可達」提升為 runtime evidence。
