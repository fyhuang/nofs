#ifndef H_NOFS_FUSE
#define H_NOFS_FUSE

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <stdint.h>

#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <syslog.h>


#include <string>

#ifndef __APPLE__
#define THREAD_LOCAL __thread
#else
#define THREAD_LOCAL
#endif

#define BUFFER_LENGTH 4096

#ifdef DEBUG
#define DBPRINTF(...) debug_printf(__VA_ARGS__)
#define DBERROR(errcode) DBPRINTF("%s returning %d\n", __func__, errcode); return -errcode
#else
#define DBPRINTF(...) do{}while(false)
#endif

extern bool recv_exact(int sock, uint8_t *buf, size_t size);
extern void debug_printf(const char *format, ...);

#endif
