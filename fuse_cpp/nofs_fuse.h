#ifndef H_NOFS_FUSE
#define H_NOFS_FUSE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define BUFFER_LENGTH 4096

#include "AppendBuffer.h"
#include "SocketReader.h"

// JSON functions (TODO)

// Globals
extern int g_Socket;

#endif
