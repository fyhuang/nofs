#include "protos.h"
#include <sys/socket.h>

// TODO: for keeping unused bytes for next time
// TODO: static int gs_BufferCount;
// TODO: static int gs_BufferPos;
static unsigned char gs_ReadBuffer[BUFFER_LENGTH];

const char *Socket_ReadJSON(int s)
{
    const char *found = NULL;

    int bracket_level = 0;
    bool in_json = false;
    bool in_string = false; // TODO

    AB_Clear(g_AppendBuffer);

    while (found == NULL) {
        // if (gs_BufferCount == 0)
        int len = recv(s, gs_ReadBuffer, BUFFER_LENGTH, 0);
        if (len < 0) {
            perror("nofs: recv");
            return NULL;
        }

        int i;
        for (i = 0; i < len; i++) {
            if (in_json) {
                uint8 byte = gs_ReadBuffer[i];
                AB_Append(g_AppendBuffer, byte);
                if (byte == '{') {
                    bracket_level++;
                }
                else if (byte == '}') {
                    bracket_level--;
                }

                if (bracket_level == 0) {
                    in_json = false;
                    found = AB_String(g_AppendBuffer);
                    break;
                }
            }
            else {
                if (gs_ReadBuffer[i] == '{') {
                    in_json = true;
                    bracket_level++;
                    AB_Append(g_AppendBuffer, '{');
                }
            }
        }

        // TODO: rest of buffer?
    }

    return found;
}
