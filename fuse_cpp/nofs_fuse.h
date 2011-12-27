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


#include <vector>
#include <string>

#define THREAD_LOCAL __thread
#define BUFFER_LENGTH 4096

extern bool recv_exact(int sock, uint8_t *buf, size_t size);

#include "mem_stream.h"
#include "paths.h"
#include "packet.h"

#endif
