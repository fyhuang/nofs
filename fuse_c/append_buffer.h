typedef unsigned char uint8;

/// A buffer which can be appended to
typedef struct AppendBuffer_s
{
    uint8 *buffer;
    /// Size of the buffer
    unsigned int capacity;
    /// How many bytes are currently stored in the buffer
    unsigned int size;
} AppendBuffer;

AppendBuffer *AB_New(unsigned int capacity);
void AB_Delete(AppendBuffer *ab);
void AB_Append(AppendBuffer *ab, uint8 byte);
void AB_Clear(AppendBuffer *ab);
const char *AB_String(AppendBuffer *ab);
