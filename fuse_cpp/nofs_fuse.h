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

#endif
