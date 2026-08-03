/* Minimal AArch64 syscall trampoline for the bounded Phase 5H probe. */
	.text
	.align 2
	.global raw_syscall4
	.type raw_syscall4, %function
raw_syscall4:
	/* C ABI: x0=number, x1..x4=args; Linux AArch64: x8=number, x0..x3=args. */
	mov x8, x0
	mov x0, x1
	mov x1, x2
	mov x2, x3
	mov x3, x4
	svc #0
	ret
	.size raw_syscall4, .-raw_syscall4
