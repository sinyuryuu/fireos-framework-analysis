/*
 * Phase 5H bounded compatibility probe.
 *
 * Host-buildable AArch64 freestanding code. It intentionally performs only:
 *   openat(/dev/mtk_cmdq, O_RDONLY)
 *   one ioctl(0x40087807, { count = 0, startPA = 0 })
 *   close(fd)
 *   exit
 *
 * It does not retry, request a non-zero allocation, use a returned address,
 * read/write kernel memory, change credentials, or invoke Android APIs.
 * Do not run on a device without the exact Level 3 approval named in the
 * accompanying report.
 */

typedef unsigned long usize;
typedef unsigned int u32;

extern long raw_syscall4(long number, long arg0, long arg1, long arg2, long arg3);

static const char device_path[] = "/dev/mtk_cmdq";
static char output[160];

static usize text_len(const char *text)
{
	usize length = 0;
	while (text[length] != '\0')
		length++;
	return length;
}

static void write_text(const char *text)
{
	raw_syscall4(64, 1, (long)text, (long)text_len(text), 0); /* write */
}

static usize append_text(usize at, const char *text)
{
	usize i = 0;
	while (text[i] != '\0')
		output[at++] = text[i++];
	return at;
}

static usize append_unsigned(usize at, unsigned long value)
{
	char digits[32];
	usize count = 0;
	if (value == 0) {
		output[at++] = '0';
		return at;
	}
	while (value != 0) {
		digits[count++] = (char)('0' + (value % 10));
		value /= 10;
	}
	while (count != 0)
		output[at++] = digits[--count];
	return at;
}

static usize append_signed(usize at, long value)
{
	if (value < 0) {
		output[at++] = '-';
		return append_unsigned(at, (unsigned long)(-(value + 1)) + 1);
	}
	return append_unsigned(at, (unsigned long)value);
}

static usize append_hex(usize at, unsigned long value)
{
	static const char hex[] = "0123456789abcdef";
	char digits[sizeof(unsigned long) * 2];
	usize count = 0;
	output[at++] = '0';
	output[at++] = 'x';
	if (value == 0) {
		output[at++] = '0';
		return at;
	}
	while (value != 0) {
		digits[count++] = hex[value & 0xfUL];
		value >>= 4;
	}
	while (count != 0)
		output[at++] = digits[--count];
	return at;
}

void _start(void)
{
	/* syscall 56 = openat; AT_FDCWD = -100; O_RDONLY = 0. */
	long fd = raw_syscall4(56, -100, (long)device_path, 0, 0);
	usize at = 0;

	at = append_text(at, "open_ret=");
	at = append_signed(at, fd);
	at = append_text(at, " (");
	at = append_hex(at, (unsigned long)fd);
	at = append_text(at, ")\n");

	if (fd >= 0) {
		/* Exactly eight bytes, count=0; no non-zero allocation is requested. */
		struct {
			u32 count;
			u32 startPA;
		} request = {0, 0};
		long result = raw_syscall4(29, fd, 0x40087807L, (long)&request, 0);
		at = append_text(at, "ioctl_ret=");
		at = append_signed(at, result);
		at = append_text(at, " (");
		at = append_hex(at, (unsigned long)result);
		at = append_text(at, ")\n");
		raw_syscall4(57, fd, 0, 0, 0); /* close */
	}

	write_text(output);
	raw_syscall4(93, 0, 0, 0, 0); /* exit */
	for (;;)
		;
}
