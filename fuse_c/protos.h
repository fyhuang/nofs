#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#include "append_buffer.h"

#define BUFFER_LENGTH 4096

// Socket functions
const char *Socket_ReadJSON(int s);

// JSON functions (TODO)

// Globals
extern int g_Socket;
extern uint8 *g_Leftover;
extern AppendBuffer *g_AppendBuffer;
