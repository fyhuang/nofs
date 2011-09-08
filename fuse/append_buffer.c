#include <stdlib.h>
#include <memory.h>
#include <assert.h>
#include "append_buffer.h"

AppendBuffer *AB_New(unsigned int capacity)
{
    AppendBuffer *ab = malloc(sizeof(AppendBuffer));
    ab->buffer = malloc(capacity);
    ab->capacity = capacity;
    ab->size = 0;
}

void AB_Delete(AppendBuffer *ab)
{
    free(ab->buffer);
    free(ab);
}

void AB_Append(AppendBuffer *ab, uint8 byte)
{
    // TODO: ability to resize buffer
    ab->buffer[ab->size] = byte;
    ab->size++;
    // We want to be able to store a NULL byte
    // at the end
    assert(ab->size < ab->capacity);
}

void AB_Clear(AppendBuffer *ab)
{
    ab->size = 0;
}

const char *AB_String(AppendBuffer *ab)
{
    ab->buffer[ab->size] = '\0';
    return ab->buffer;
}
