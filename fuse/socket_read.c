#include "protos.h"
#include <sys/socket.h>

// For keeping unused bytes for next time
static int gs_BufferCount = 0;
static int gs_BufferPos = 0;
static unsigned char gs_ReadBuffer[BUFFER_LENGTH];

const char *Socket_ReadJSON(int s)
{
    const char *found = NULL;

    int bracket_level = 0;
    bool in_json = false;
    bool in_string = false; // TODO

    AB_Clear(g_AppendBuffer);

    while (found == NULL) {
        if (gs_BufferCount == 0) {
            gs_BufferCount = recv(s, gs_ReadBuffer, BUFFER_LENGTH, 0);
            if (gs_BufferCount < 0) {
                perror("nofs: recv");
                return NULL;
            }
            gs_BufferPos = 0;
        }

        for (; gs_BufferPos < gs_BufferCount; gs_BufferPos++) {
            int i = gs_BufferPos;
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

        if (gs_BufferPos >= gs_BufferCount)
            gs_BufferCount = 0;
    }

    return found;
}
